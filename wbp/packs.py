"""wbp.packs"""
import sys
import atexit
import os
import re
import zlib
import struct
import glob
import json
import shutil
import io
import hashlib
import socket
import tempfile
import zipfile
import traceback
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from wbp.common import LOGGER, print_progress
from wbp.profiles import get_profile
from wbp.detect import extract_pack_display_name
from wbp import wbconv

# -----------------------------------------------------------------------------
# CUSTOM ASSET DISCOVERY & MANIFEST GENERATOR
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# TOYBRIDGE MODPACK CLASSIFICATION & QUARANTINE ROUTINES
# -----------------------------------------------------------------------------
_OLD_CONVENTION_DATA_PATTERN = re.compile(r'^custom_data_\d+\.(futa|spouse)$', re.IGNORECASE)


_OLD_CONVENTION_PATTERN = re.compile(r'^custom_(futa|wife)_\w+_\d+\.png$', re.IGNORECASE)


KNOWN_DATA_FILES = {
    'custom_data.futa': 'futa',
    'custom_data.wife': 'wife',
    'custom_data.spouse': 'wife',
    'custom_data.bedroom': 'bedroom',
}


def classify_custom_pack(folder: Path, modern_ok: bool = False):
    """
    Classifies one character/bedroom folder as portable (simple convention - can just be
    copied into the other mod system's expected layout) or not (uses the older numbered
    convention or lacks recognized custom_data files, which causes crashes on mobile).
    Exact classification logic from ToyBridgeLauncher's GamePatcher / ToyLauncher.

    modern_ok: the target engine reads the ModRoom naming natively (ModRoom V3.3 and Deeproom: custom_futa_*_0.png,
    custom_wife_*_0.png and the _alt_N variants), so those names are not a reason to skip a pack. Wife's Bedroom v1.5
    cannot read them and keeps the old rule.
    """
    try:
        entries = list(folder.iterdir())
    except OSError as e:
        return False, f"Couldn't read folder: {e}", None

    names = [e.name for e in entries]
    lower_to_orig = {e.name.lower(): e.name for e in entries}

    # 1. Check for numbered-alt data file (custom_data_1.futa style)
    for name in names:
        if _OLD_CONVENTION_DATA_PATTERN.match(name):
            return False, "Uses a numbered-alt data file (custom_data_1.futa style) - not portable.", None

    # 2. Check for recognized data file
    data_file = None
    kind = None
    for df, k in KNOWN_DATA_FILES.items():
        if df in lower_to_orig:
            data_file = lower_to_orig[df]
            kind = k
            break

    if not data_file:
        return False, "No recognized custom_data.futa/.wife/.spouse/.bedroom file found.", None

    # 3. Check for old numbered sprite convention (custom_futa_mating_press_0.png, etc.)
    old_style_files = [n for n in names if _OLD_CONVENTION_PATTERN.match(n)]
    if old_style_files and not modern_ok:
        return False, f"Uses the older numbered sprite convention ({old_style_files[0]}, etc.) - not portable.", kind

    # 4. ModRoom naming is fine, but only when the sprites match the folder the pack sits in
    if modern_ok and old_style_files:
        low = [n.lower() for n in names]
        has_wife = any(n.startswith("custom_wife_") and n.endswith(".png") for n in low)
        has_futa = any(n.startswith("custom_futa_") and n.endswith(".png") for n in low)
        cat = folder.parent.name.lower()
        if "futa" in cat and has_wife and not has_futa:
            return False, "Holds partner sprites (custom_wife_*) but sits in a lover folder (custom_futas) - move it to custom_wives.", kind
        if ("wive" in cat or "wife" in cat) and has_futa and not has_wife:
            return False, "Holds lover sprites (custom_futa_*) but sits in a partner folder (custom_wives) - move it to custom_futas.", kind

    return True, "Simple convention - portable as-is.", kind


# -----------------------------------------------------------------------------
# 3-TIER DUPLICATE DETECTION & QUARANTINE ENGINE
# -----------------------------------------------------------------------------
def compute_file_sha256(path: Path) -> str:
    """Computes SHA-256 hash of a file for exact asset fingerprinting."""
    try:
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


def extract_pack_info_name(pack_path: Path) -> str:
    """Reads internal [info] name= if present from .futa, .spouse, .wife, .bedroom, or .ini."""
    for pat in ["custom_data.futa", "custom_data.spouse", "custom_data.wife", "custom_data.bedroom", "*.ini"]:
        for f in pack_path.glob(pat):
            if f.is_file():
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    m = re.search(r"^\s*name\s*=\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)
                    if m:
                        clean = m.group(1).strip().strip('"').strip("'")
                        clean = re.sub(r'[\/:*?"<>|]', "", clean).strip()
                        if clean and len(clean) >= 2:
                            return clean
                except Exception:
                    pass
    return ""


def normalize_pack_slug(name: str) -> str:
    """Normalizes a folder or character name into a clean comparison slug (Tier 1)."""
    s = re.sub(r"\((COMM|3\.5|1\.4|V1|BS|WIP|Nude|Clothed|Rework)\)", "", name, flags=re.I)
    s = re.sub(r"(\s*-\s*copy(\s*\(\d+\))?|\s*\(\d+\)|_copy|_old|_backup)$", "", s, flags=re.I)
    s = re.sub(r'[\/:*?"<>|!#~_.\-]+', " ", s).strip().lower()
    return re.sub(r"\s+", "_", s)


def detect_intrinsic_category(pack_path: Path) -> str:
    """Inspects internal files to determine the true intrinsic category of a pack."""
    try:
        files = {f.name.lower() for f in pack_path.iterdir() if f.is_file()}
        if any(w in files for w in ["custom_data.spouse", "custom_data.wife", "custom_wife.ini"]):
            return "custom_wives"
        if any(w in files for w in ["custom_data.futa", "custom_futa.ini"]):
            return "custom_futas"
        if any(w in files for w in ["custom_data.bedroom", "background.png", "custom_background.png"]):
            return "custom_bedrooms"

        if any("wife" in f for f in files) or any("spouse" in f for f in files) or "custom_cowgirl.png" in files:
            return "custom_wives"
        if any("futa" in f for f in files) or "custom_futa_portrait_0.png" in files:
            return "custom_futas"
        if any("bedroom" in f for f in files) or any("room" in f for f in files):
            return "custom_bedrooms"

        for f in files:
            if f.endswith(".futa"):
                return "custom_futas"
            if f.endswith(".spouse") or f.endswith(".wife"):
                return "custom_wives"
            if f.endswith(".bedroom"):
                return "custom_bedrooms"
    except Exception:
        pass
    return "unknown"


def score_pack_canonical(pack_path: Path, cat: str = "", target_is_v15: bool = False, target_arch: str = "deeproom") -> float:
    """Calculates canonical score for duplicate tie-breaking (Tier 3). Higher is preferred."""
    score = 0.0
    valid_exts = {".png", ".ogg", ".wav", ".mp3", ".json", ".futa", ".spouse", ".wife", ".bedroom", ".ini", ".txt"}
    files = [f for f in pack_path.rglob("*") if f.is_file() and f.suffix.lower() in valid_exts]
    score += len(files) * 10.0
    audio_files = [f for f in files if f.suffix.lower() in [".ogg", ".wav", ".mp3"]]
    score += len(audio_files) * 25.0
    file_names = {f.name.lower() for f in files}
    if any("cowgirl" in n for n in file_names):
        score += 30.0
    if any("xray" in n for n in file_names):
        score += 20.0
    name = pack_path.name
    if re.search(r"(\s*-\s*copy|\s+copy(\s*\d+)?$|\s*\(\d+\)|_copy|\s+old$|_old|_backup)", name, re.I):
        score -= 50.0
    if name.isdigit() and len(name) >= 7:
        score -= 30.0

    # Category Affinity Bonus & Conflicting Folder Penalty (Ensures wives in custom_wives win over wives in custom_futas)
    intrinsic = detect_intrinsic_category(pack_path)
    if intrinsic != "unknown":
        if cat == intrinsic:
            score += 100.0  # Perfect folder match!
        elif cat == "custom":
            score += 20.0   # Unified format acceptable
        else:
            score -= 100.0  # Severe penalty for misplaced conflicting duplicate!

    # Target Architecture Alignment Bonus
    is_inside_custom_stuff = "custom_stuff" in [part.lower() for part in pack_path.parts]
    if target_is_v15 or target_arch == "v15":
        if cat == "custom":
            score += 50.0
    elif target_arch == "modroom33":
        if not is_inside_custom_stuff and cat in ["custom_futas", "custom_wives", "custom_bedrooms"]:
            score += 50.0  # ModRoom v3.3 strictly requires root-level category folders
        elif is_inside_custom_stuff:
            score -= 50.0  # ModRoom v3.3 does not read custom_stuff/
    elif target_arch == "deeproom":
        if is_inside_custom_stuff and cat in ["custom_futas", "custom_wives", "custom_bedrooms"]:
            score += 50.0  # Deeproom 4.0.3 strictly requires custom_stuff/ container
        elif not is_inside_custom_stuff:
            score -= 20.0

    try:
        mtime = max(f.stat().st_mtime for f in files) if files else pack_path.stat().st_mtime
        score += mtime / 1000000000.0
    except Exception:
        pass
    return score


def get_pack_fingerprints(pack_path: Path, cat: str = "") -> dict:
    """Extracts SHA-256 asset fingerprints across characters, bedrooms, SFX/audio, and dialogues (Tier 2)."""
    fps = {}
    try:
        audio_hashes = []
        for f in sorted(pack_path.iterdir()):
            if not f.is_file():
                continue
            fn = f.name.lower()
            ext = f.suffix.lower()
            if fn in ["custom_portrait.png", "custom_futa_portrait_0.png", "custom_wife_portrait_0.png"]:
                fps["portrait"] = compute_file_sha256(f)
            elif fn in ["custom_mating_press.png", "custom_futa_mating_press_0.png", "custom_wife_mating_press_0.png"]:
                fps["mating"] = compute_file_sha256(f)
            elif fn in ["background.png", "custom_background.png"]:
                fps["bg"] = compute_file_sha256(f)
            elif ext in [".ogg", ".wav", ".mp3"] and len(audio_hashes) < 3:
                audio_hashes.append(compute_file_sha256(f))
            elif ext == ".json" and "dialogue" in cat:
                fps["dialogue"] = compute_file_sha256(f)
        if audio_hashes:
            fps["audio_primary"] = audio_hashes[0]
    except Exception:
        pass
    return fps


def is_compatible_category(cat1: str, cat2: str) -> bool:
    """Determines whether two categories can contain duplicate variants (e.g. custom/ vs custom_wives/).
    CRITICAL: custom_futas (Lovers/Tops) and custom_wives (Partners/Bottoms) are distinct gameplay roles
    and must NEVER cluster as duplicates of each other."""
    if cat1 == cat2:
        return True
    if (cat1 == "custom" and cat2 in ["custom_futas", "custom_wives"]) or (cat2 == "custom" and cat1 in ["custom_futas", "custom_wives"]):
        return True
    if (cat1 == "custom" and cat2 == "custom_bedrooms") or (cat2 == "custom" and cat1 == "custom_bedrooms"):
        return True
    if cat1 in {"custom_sounds", "custom_music"} and cat2 in {"custom_sounds", "custom_music"}:
        return True
    if cat1 in {"dialogue", "dialogue_packs", "custom_dialogues"} and cat2 in {"dialogue", "dialogue_packs", "custom_dialogues"}:
        return True
    return False


def _in_skipped(path, skip_dirs):
    """True when path is one of skip_dirs or lies inside one of them."""
    if not skip_dirs:
        return False
    p = Path(path).resolve()
    return any(p == s or s in p.parents for s in skip_dirs)


def plan_duplicate_skips(mods_dir, target_is_v15=False, target_arch="deeproom", exclude=()):
    """
    3-Tier Cross-Folder & Cross-Category Duplicate Detection (decides only; never moves or deletes files).
    - Tier 1: slug and descriptor [info] name collisions.
    - Tier 2: SHA-256 asset fingerprints (portraits, mating sheets, backgrounds, audio, dialogues).
    - Tier 3: canonical scoring keeps the best pack of each duplicate group.
    Packs under `exclude` (e.g. already skipped as incompatible) are ignored, so a skipped pack is never "kept".
    Returns (unique_count, skips); each skip is a dict with path, cat, kind, reason, kept_path, kept_cat.
    """
    mods_dir = Path(mods_dir)
    exclude = {Path(e).resolve() for e in exclude}

    target_cats = ["custom_futas", "custom_wives", "custom_bedrooms", "custom", "custom_sounds", "custom_music", "dialogue_packs", "texture_packs"]
    ignored_dup_names = {"templates", "template", "texture_packs", "ball clench stuff", "custom sperm", "quarantine", "!duplicates", "__pycache__"}
    all_pack_data = []

    container_roots = [mods_dir]
    if (mods_dir / "custom_stuff").is_dir():
        container_roots.append(mods_dir / "custom_stuff")

    for root_base in container_roots:
        for cat in target_cats:
            cat_path = root_base / cat
            if not cat_path.is_dir():
                continue

            packs = [p for p in sorted(cat_path.iterdir()) if p.is_dir() and not p.name.startswith(".") and p.name.lower() not in ignored_dup_names and not _in_skipped(p, exclude)]
            for n_done, p in enumerate(packs, 1):
                print_progress(n_done, len(packs), prefix=f"Duplicate scan {cat:<15}")
                f_slug = normalize_pack_slug(p.name)
                i_name = extract_pack_info_name(p)
                i_slug = normalize_pack_slug(i_name) if i_name else ""
                fps = get_pack_fingerprints(p, cat=cat)
                score = score_pack_canonical(p, cat=cat, target_is_v15=target_is_v15, target_arch=target_arch)
                # Give engine-appropriate category bonus
                if target_is_v15 and cat == "custom":
                    score += 15.0
                elif (not target_is_v15) and cat in ["custom_futas", "custom_wives", "custom_bedrooms"]:
                    score += 15.0
    
                all_pack_data.append({
                    "idx": len(all_pack_data),
                    "path": p,
                    "cat": cat,
                    "folder_slug": f_slug,
                    "info_slug": i_slug,
                    "fps": fps,
                    "score": score
                })

    n = len(all_pack_data)
    if n <= 1:
        return n, []

    parent = list(range(n))
    def find(i):
        if parent[i] == i: return i
        parent[i] = find(parent[i])
        return parent[i]
    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    pair_reasons = {}
    for i in range(n):
        for j in range(i + 1, n):
            pi = all_pack_data[i]
            pj = all_pack_data[j]
            if not is_compatible_category(pi["cat"], pj["cat"]):
                continue

            is_dup = False
            reason = ""

            # Tier 2: Asset Hash match
            for k in ["portrait", "mating", "bg", "audio_primary", "dialogue"]:
                if k in pi["fps"] and k in pj["fps"] and pi["fps"][k] and pi["fps"][k] == pj["fps"][k]:
                    is_dup = True
                    reason = f"Tier 2 Asset Match (Identical {k} SHA-256)"
                    break

            # Tier 1: Slug or Metadata match
            GENERIC_SLUGS = {"example", "custom", "custom_character", "character", "wife", "partner", "futa", "lover", "not_found", "unknown", "unnamed", "none", "new_pack", "template"}
            if not is_dup:
                if pi["folder_slug"] and pi["folder_slug"] == pj["folder_slug"]:
                    is_dup = True
                    reason = f"Tier 1 Name Match (Normalized slug '{pi['folder_slug']}')"
                elif pi["info_slug"] and pi["info_slug"] not in GENERIC_SLUGS and (pi["info_slug"] == pj["folder_slug"] or pi["info_slug"] == pj["info_slug"]):
                    is_dup = True
                    reason = f"Tier 1 Metadata Match (Descriptor [info] name '{pi['info_slug']}')"
                elif pj["info_slug"] and pj["info_slug"] not in GENERIC_SLUGS and pj["info_slug"] == pi["folder_slug"]:
                    is_dup = True
                    reason = f"Tier 1 Metadata Match (Descriptor [info] name '{pj['info_slug']}')"

            if is_dup:
                union(i, j)
                pair_reasons[(min(i, j), max(i, j))] = reason

    clusters = {}
    for i in range(n):
        r = find(i)
        clusters.setdefault(r, []).append(all_pack_data[i])

    unique, skips = 0, []
    for r, group in clusters.items():
        unique += 1
        if len(group) == 1:
            continue
        group.sort(key=lambda x: x["score"], reverse=True)
        winner = group[0]
        for dup in group[1:]:
            why = pair_reasons.get((min(dup["idx"], winner["idx"]), max(dup["idx"], winner["idx"]))) or "linked to the kept pack through another duplicate in the same group"
            skips.append({
                "path": str(dup["path"]), "cat": dup["cat"], "kind": "duplicate",
                "reason": f"{why}; score {dup['score']:.1f} vs kept {winner['score']:.1f}",
                "kept_path": str(winner["path"]), "kept_cat": winner["cat"],
            })
    return unique, skips


def missing_sprites(folder, kind, profile):
    """Sprites `profile` requires for this kind of pack that the build will not contain (empty list = admitted).

    Judged on the pack's own files plus the copies plan_name_bridge() will add, so the verdict matches the APK."""
    needs = profile.needs.get(kind) if profile.needs else None
    if not needs:
        return []
    try:
        names = {e.name.lower() for e in Path(folder).iterdir()}
    except OSError:
        return []
    pack_kind = _pack_kind(Path(folder).parent.name, names)
    names |= {dst for _, dst in plan_name_bridge(names, profile.arch, pack_kind, is_modern_pack_names(names))}
    return [label for label, accepted in needs if not any(n in names for n in accepted)]


def deeproom_strip_problems(folder, kind):
    """Strips the Deeproom mobile bundle would cut wrongly, as a list of reasons (empty = loads cleanly).

    Mirrors core/bundle_src (func_futa_pack_is_legacy, func_load_custom_futa, func_load_custom_spouse,
    func_load_custom_wife, func_portrait_frames): which loader the pack gets, which files that loader reads,
    and the frame COUNT it passes to sprite_add(). GameMaker cuts a strip into that many equal frames, so a
    width that does not divide evenly gives off-centre, smeared frames. Strips whose count the bundle
    derives from the width itself (lover mating press, lover cowgirl, partner modern X-ray) are not checked.
    Judged on the pack's files plus the copies plan_name_bridge() adds, like missing_sprites()."""
    folder = Path(folder)
    try:
        files = {e.name.lower(): e for e in folder.iterdir() if e.is_file()}
    except OSError:
        return []
    names = set(files)
    for src, dst in plan_name_bridge(names, "deeproom", _pack_kind(folder.parent.name, names), is_modern_pack_names(names)):
        if dst not in files and src in files:
            files[dst] = files[src]
    has = files.__contains__
    problems = []

    def width(name):
        size = wbconv.png_size(files[name])
        return size[0] if size else None

    def check(name, frames):
        if not has(name):
            return
        w = width(name)
        if not w:  # unreadable or placeholder files are not this check's job (frame counts)
            return
        if w % frames:
            problems.append(f"{name} is {w} px wide; the game cuts it into {frames} frames ({w / frames:.1f} px each)")

    def check_portrait(candidates, label):
        name = next((n for n in candidates if has(n)), None)
        if name is None:
            problems.append(f"no {label} portrait ({' or '.join(candidates)})")
            return
        default = 17 if name.endswith("_0.png") else 10
        w = width(name)
        if not w:  # unreadable or placeholder files are not this check's job (frame counts)
            return
        if w % default and w % (27 - default):  # 27 - 10 = 17, 27 - 17 = 10
            problems.append(f"{name} is {w} px wide; a portrait must divide into 10 or 17 frames")

    if kind == "futa":
        if has("custom_mating_press.png") or not has("custom_futa_mating_press_0.png"):
            check_portrait(["custom_portrait.png", "custom_futa_portrait_0.png"], "lover")
            check("custom_xray.png", 3)
            check("custom_deepthroat.png", 9)
            # custom_condom.png (2 frames) is not checked: many packs are 1-3 px off (317 px), which shifts the
            # overlay by a pixel or two - not worth dropping the character.
        else:
            check_portrait(["custom_futa_portrait_0.png", "custom_portrait.png"], "lover")
            check("custom_futa_mating_press_0.png", 24)
            check("custom_futa_cowgirls_0.png", 19)
            check("custom_futa_xray_0.png", 18)
            check("custom_futa_deepthroat_0.png", 24)
            check("custom_deepthroat.png", 9)
    elif kind == "wife":
        if has("custom_data.spouse") or has("custom_mating_press.png") or not has("custom_wife_mating_press_0.png"):
            check_portrait(["custom_portrait.png", "custom_wife_portrait_0.png"], "partner")
            check("custom_mating_press.png", 4)
            check("custom_reverse_cowgirl.png", 5)
            check("custom_deepthroat.png", 5)
            check("custom_xray.png", 4)
        else:
            check_portrait(["custom_wife_portrait_0.png", "custom_portrait.png"], "partner")
            check("custom_wife_mating_press_0.png", 5)
            check("custom_wife_cowgirl_0.png", 11)
            check("custom_wife_reverse_cowgirl_0.png", 10)
            check("custom_wife_deepthroat_0.png", 5)
    return problems


def plan_incompatible_skips(mods_dir, target_arch="deeproom"):
    profile = get_profile(target_arch)
    """Classifies each character/bedroom pack with classify_custom_pack(); never moves files.
    Returns (portable_count, skips) with kind='incompatible'."""
    mods_dir = Path(mods_dir)
    portable, skips = 0, []
    target_cats = ["custom_futas", "custom_wives", "custom_bedrooms", "custom"]
    ignored_pack_names = {"templates", "template", "texture_packs", "ball clench stuff", "custom sperm", "quarantine", "!duplicates", "__pycache__", "custom_music", "custom_sounds", "dialogue", "dialogue_packs"}
    container_roots = [mods_dir]
    if (mods_dir / "custom_stuff").is_dir():
        container_roots.append(mods_dir / "custom_stuff")
    todo = []
    for root_base in container_roots:
        for cat in target_cats:
            cat_path = root_base / cat
            if not cat_path.is_dir():
                continue
            for pack in sorted(cat_path.iterdir()):
                if pack.is_dir() and not pack.name.startswith(".") and pack.name.lower() not in ignored_pack_names:
                    todo.append((cat, pack))
    for done, (cat, pack) in enumerate(todo, 1):
                    print_progress(done, len(todo), prefix="Checking packs")
                    is_p, reason, kind = classify_custom_pack(pack, modern_ok=profile.modern_names_ok)
                    if is_p and profile.needs:
                        missing = missing_sprites(pack, kind, profile)
                        if missing:
                            is_p = False
                            reason = (profile.label + " only lists a " + ("lover" if kind == "futa" else "partner") + " pack that has its "
                                      + ", ".join(m for m, _ in profile.needs[kind]) + " sprites; this one lacks: " + ", ".join(missing)
                                      + ". Listing it would crash the game when the missing sprite is drawn.")
                    if is_p and profile.arch == "deeproom" and kind in ("futa", "wife"):
                        problems = deeproom_strip_problems(pack, kind)
                        if problems:
                            is_p = False
                            reason = ("Deeproom cannot show this pack correctly (sprite_add cuts each strip into a fixed number "
                                      "of frames): " + "; ".join(problems))
                    if is_p:
                        portable += 1
                    else:
                        skips.append({"path": str(pack), "cat": cat, "kind": "incompatible", "reason": reason, "kept_path": "", "kept_cat": ""})
    return portable, skips


def write_skip_report(skips, report_base, source_folder, mode="build"):
    """Writes <report_base>.md (for people) and <report_base>.json (for tools) listing every skipped pack,
    why it was skipped, and how to include it. Returns the .md path, or None when nothing was skipped."""
    if not skips:
        return None
    report_base = Path(report_base)
    report_base.parent.mkdir(parents=True, exist_ok=True)
    src = Path(source_folder)
    def rel(p):
        if not p:
            return ""
        try:
            return Path(p).relative_to(src).as_posix()
        except ValueError:
            return str(p)
    dups = [x for x in skips if x["kind"] == "duplicate"]
    incs = [x for x in skips if x["kind"] == "incompatible"]
    when = datetime.now().strftime("%Y-%m-%d %H:%M")
    what = "were left out of this APK" if mode == "build" else "would be left out of a build"
    md = [f"# Skipped mod packs: {report_base.name}", "",
          f"Generated {when}. Source folder: `{src}`.", "",
          f"**{len(skips)} pack(s) {what}** ({len(dups)} duplicate, {len(incs)} incompatible). "
          "Your mod folder was not changed: nothing was moved or deleted.", ""]
    if dups:
        md += ["## Duplicates", "", "| Skipped pack | Category | Kept instead | Why |", "|---|---|---|---|"]
        md += [f"| `{rel(x['path'])}` | {x['cat']} | `{rel(x['kept_path'])}` | {x['reason']} |" for x in dups]
        md.append("")
    if incs:
        md += ["## Incompatible", "", "| Skipped pack | Category | Why |", "|---|---|---|"]
        md += [f"| `{rel(x['path'])}` | {x['cat']} | {x['reason']} |" for x in incs]
        md.append("")
    md += ["## How to include a skipped pack", "",
           "- **Duplicate:** rebuild with `--no-quarantine-duplicates` to keep every copy, or remove or rename the kept copy so the one you want wins.",
           "- **Incompatible:** fix the problem listed under *Why* (usually a missing or misnamed file) and rebuild.",
           "- To move skipped packs out of your mod folder instead, rebuild with `--move-skipped`: they go to a new `output/quarantine/<date-time>/` folder and nothing is overwritten or deleted.", ""]
    md_path = report_base.with_name(report_base.name + ".md")
    md_path.write_text("\n".join(md), encoding="utf-8")
    report_base.with_name(report_base.name + ".json").write_text(json.dumps({"generated": when, "mode": mode, "source": str(src), "skipped": skips}, indent=2), encoding="utf-8")
    return md_path


def move_skipped_packs(skips, quarantine_root):
    """Opt-in (--move-skipped): moves each skipped pack into a NEW timestamped folder. Never overwrites or deletes."""
    dest_root = Path(quarantine_root) / datetime.now().strftime("%Y%m%d-%H%M%S")
    moved = 0
    for x in skips:
        src = Path(x["path"])
        if not src.is_dir():
            continue
        dest = dest_root / x["kind"] / x["cat"] / src.name
        k = 2
        while dest.exists():
            dest = dest.with_name(f"{src.name}_{k}")
            k += 1
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(src), str(dest))
            moved += 1
        except Exception as m_err:
            LOGGER.log(f"Notice: could not move skipped pack '{src.name}': {m_err}", prefix="[!]")
    if moved:
        LOGGER.log(f"Moved {moved} skipped pack(s) to '{dest_root}' (--move-skipped).", prefix="[+]")
    return dest_root


def plan_pack_skips(source_folder, check_duplicates=True, target_is_v15=False, target_arch="deeproom"):
    """Runs both planners. Duplicates are judged only among packs that are not already incompatible."""
    portable, inc = plan_incompatible_skips(source_folder, target_arch=target_arch)
    dup = []
    if check_duplicates:
        _, dup = plan_duplicate_skips(source_folder, target_is_v15=target_is_v15, target_arch=target_arch, exclude=[x["path"] for x in inc])
    if inc:
        LOGGER.log(f"Pre-flight Pack Validation: {len(inc)} incompatible pack(s) will be skipped; {portable} portable pack(s) kept.", prefix="[!]")
    else:
        LOGGER.log(f"Pre-flight Pack Validation: All {portable} pack(s) are portable.", prefix="[+]")
    if dup:
        LOGGER.log(f"Duplicate Check: {len(dup)} duplicate pack(s) will be skipped (best copy of each kept).", prefix="[!]")
    return inc + dup


def sanitize_apk_part(name: str) -> str:
    """Sanitizes directory/file component for Android APK AssetManager compatibility (lowercase, underscores, no spaces, no illegal punctuation)."""
    clean = name.strip().lower().replace(" ", "_").replace("#", "").replace(":", "_").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace('"', '').replace("'", "")
    clean = re.sub(r"_+", "_", clean).strip("_")
    return clean or "unnamed"


def unique_apk_name(clean, folder, used) -> str:
    """`clean` if free, else it plus the part of the pack's folder name that is not just the display name again
    ("astolfo" + "Astolfo (naked)" gives "astolfo_naked"), and a number only as a last resort."""
    if clean not in used:
        return clean
    shown, tokens = clean.split("_"), sanitize_apk_part(folder).split("_")
    i = 0
    while i < len(shown) and i < len(tokens) and shown[i] == tokens[i]:
        i += 1
    rest = "_".join(tokens[i:])
    cand = f"{clean}_{rest}" if rest else clean
    base, n = cand, 2
    while cand in used:
        cand = f"{base}_{n}"
        n += 1
    return cand


def sanitize_apk_path(rel_path: Path) -> str:
    """Sanitizes full relative path for Android APK asset manager."""
    parts = [sanitize_apk_part(p) for p in rel_path.parts]
    return "/".join(parts)


_ROOT_CUSTOM = re.compile(r"^assets/custom_(?!stuff/)[^/]+/")


def restrict_manifests(manifests, target_arch):
    """Keep manifests only under the directory the target engine reads, so no duplicate custom_* folders are built.

    Deeproom reads assets/custom_stuff/custom_*; its code treats the root custom_* folders as a legacy fallback and
    prefers custom_stuff when that manifest exists (a root copy would create a folder holding only manifests).
    ModRoom reads the root custom_* folders; custom_stuff is only its fallback. v1.5 reads custom/ (unchanged).
    target_arch None keeps everything (callers that do not know the engine).
    """
    if target_arch == "deeproom":
        return {k: v for k, v in manifests.items() if not _ROOT_CUSTOM.match(k)}
    if target_arch == "modroom33":
        return {k: v for k, v in manifests.items() if not k.startswith("assets/custom_stuff/")}
    return manifests


def generate_manifest_data(folder, is_v15=False, skip_dirs=(), target_arch=None):
    """
    Generates in-memory _manifest.txt files for every directory GameMaker scans
    on Android (custom_futas, custom_wives, custom_bedrooms, custom_music,
    custom_sounds, dialogue, dialogue_packs, texture_packs).
    
    Alphabetical Sorting Mandate:
    All entries across all categories (including converted v1.5 packs) are strictly
    merged and sorted alphabetically to ensure natural in-game selector ordering.
    Zero prepending to front.
    
    Deeproom APK Mandate:
    For Deeproom APKs, all custom assets belong under assets/custom_stuff/.
    Never place or mirror custom/ into both root and custom_stuff/.
    """
    manifests = {}
    folder = Path(folder).resolve()
    valid_exts = {".png", ".ogg", ".wav", ".mp3", ".json", ".futa", ".spouse", ".wife", ".bedroom", ".ini", ".jpg", ".jpeg", ".gif", ".webp"}
    ignored_containers = {"templates", "template", "ball clench stuff", "custom sperm", "quarantine", "!duplicates", "__pycache__", ".git"}
    ignored_project_exts = {".aseprite", ".ase", ".clip", ".pdn", ".kra", ".psd", ".xcf", ".blend", ".zip", ".rar", ".7z", ".tar", ".gz", ".bak", ".tmp", ".pdf", ".docx", ".doc"}

    is_dr = (folder / "custom_stuff").is_dir()

    target_dirs = [
        "custom_futas", "custom_wives", "custom_bedrooms",
        "custom_music", "custom_sounds", "dialogue", "dialogue_packs", "texture_packs"
    ]

    all_category_entries = {cat: set() for cat in target_dirs}
    if is_v15:
        all_category_entries["custom"] = set()

    c_base = (folder / "custom_stuff") if is_dr else folder

    for td_name in target_dirs:
        candidate_top_dirs = []
        if (c_base / td_name).is_dir():
            candidate_top_dirs.append(c_base / td_name)
        # Texture packs and loose categories: also check root game folder if different from c_base
        if (folder / td_name).is_dir() and (folder / td_name) != (c_base / td_name):
            candidate_top_dirs.append(folder / td_name)

        if not candidate_top_dirs:
            continue

        for top_dir in candidate_top_dirs:
            for item in top_dir.iterdir():
                if item.is_dir() and not item.name.startswith(".") and item.name.lower() not in ignored_containers and not _in_skipped(item, skip_dirs):
                    clean_name = sanitize_apk_part(item.name)
                    all_category_entries[td_name].add(clean_name)

                    # Write individual pack manifest
                    pack_entries = []
                    for root, dirs, files in os.walk(item):
                        clean_dirs = sorted([sanitize_apk_part(d) for d in dirs if not d.startswith(".") and d != "__pycache__"])
                        clean_files = sorted([sanitize_apk_part(Path(f).stem) + Path(f).suffix.lower() for f in files if Path(f).suffix.lower() in valid_exts and f != "_manifest.txt" and not f.startswith(".") and not f.endswith("~")])
                        pack_entries.extend(clean_dirs + clean_files)
                    if pack_entries:
                        # Write standard mobile asset manifest and dual custom_stuff manifest
                        m_bytes = ("\n".join(sorted(set(pack_entries))) + "\n").encode("utf-8")
                        manifests[f"assets/{td_name}/{clean_name}/_manifest.txt"] = m_bytes
                        manifests[f"assets/custom_stuff/{td_name}/{clean_name}/_manifest.txt"] = m_bytes
                elif item.is_file() and item.suffix.lower() in valid_exts and item.name != "_manifest.txt":
                    all_category_entries[td_name].add(sanitize_apk_part(item.name))

    # Process custom/ packs (if present in root or custom_stuff)
    custom_sources = []
    if (folder / "custom").is_dir():
        custom_sources.append(folder / "custom")
    if (folder / "custom_stuff" / "custom").is_dir():
        custom_sources.append(folder / "custom_stuff" / "custom")

    used_loose_names = {}
    for c_dir in custom_sources:
        for pack in sorted(c_dir.iterdir()):
            if pack.is_dir() and not pack.name.startswith(".") and pack.name.lower() not in ignored_containers and not _in_skipped(pack, skip_dirs):
                cat = None
                p_files = {f.name.lower() for f in pack.iterdir() if f.is_file()}
                if (pack / "custom_data.futa").exists() or (pack / "custom_futa_portrait_0.png").exists() or any(f.endswith(".futa") for f in p_files):
                    cat = "custom_futas"
                elif (pack / "custom_data.spouse").exists() or (pack / "custom_data.wife").exists() or (pack / "custom_wife.ini").exists() or (pack / "custom_wife_portrait_0.png").exists() or (pack / "custom_forward_cowgirl.png").exists() or (pack / "custom_egg.png").exists() or any(f.endswith(".spouse") or f.endswith(".wife") for f in p_files) or any(w in pack.name.lower() for w in ["wife", "wives", "spouse", "partner", "bottom"]):
                    cat = "custom_wives"
                elif (pack / "custom_data.bedroom").exists() or (pack / "custom_background.png").exists() or (pack / "background.png").exists() or any(f.endswith(".bedroom") for f in p_files) or any(w in pack.name.lower() for w in ["bedroom", "bedrooms", "room", "background"]):
                    cat = "custom_bedrooms"
                elif (pack / "custom_portrait.png").exists() or (pack / "custom_mating_press.png").exists():
                    cat = "custom_futas"

                clean_pname = sanitize_apk_part(extract_pack_display_name(pack))
                if cat and c_dir == folder / "custom" and not is_dr:
                    # same collision rule as gather_custom_assets, so the index lists the folder name the asset gets
                    clean_pname = unique_apk_name(clean_pname, pack.name, used_loose_names.setdefault(cat, set()))
                    used_loose_names[cat].add(clean_pname)
                if cat:
                    all_category_entries[cat].add(clean_pname)
                if is_v15:
                    all_category_entries["custom"].add(clean_pname)

                # Individual pack manifest
                pack_entries = []
                for root, dirs, files in os.walk(pack):
                    clean_dirs = sorted([sanitize_apk_part(d) for d in dirs if not d.startswith(".") and d != "__pycache__"])
                    clean_files = sorted([sanitize_apk_part(Path(f).stem) + Path(f).suffix.lower() for f in files if Path(f).suffix.lower() in valid_exts and f != "_manifest.txt" and not f.startswith(".") and not f.endswith("~")])
                    pack_entries.extend(clean_dirs + clean_files)
                if pack_entries:
                    if is_dr and cat:
                        m_path = f"assets/custom_stuff/{cat}/{clean_pname}/_manifest.txt"
                    elif is_v15:
                        m_path = f"assets/custom/{clean_pname}/_manifest.txt"
                    elif cat:
                        m_path = f"assets/{cat}/{clean_pname}/_manifest.txt"
                    else:
                        m_path = None
                    if m_path:
                        manifests[m_path] = ("\n".join(sorted(set(pack_entries))) + "\n").encode("utf-8")

    # Write top-level manifests sorted alphabetically (strictly mixed in alphabetically, no front-prepending)
    for cat_name, entries in all_category_entries.items():
        if not entries:
            continue
        if is_v15 and cat_name != "custom":
            continue
        if not is_v15 and cat_name == "custom":
            continue

        sorted_entries = sorted(entries, key=lambda s: s.lower())
        top_bytes = ("\n".join(sorted_entries) + "\n").encode("utf-8")
        manifests[f"assets/{cat_name}/_manifest.txt"] = top_bytes
        if is_dr:
            manifests[f"assets/custom_stuff/{cat_name}/_manifest.txt"] = top_bytes

    return restrict_manifests(manifests, target_arch)


# (existing name, name to copy it to). Each pair belongs to one kind of pack (see _pair_kind).
BRIDGE_PAIRS = [
    # ModRoom v3.3 -> Deeproom / v1.5 Standard
    ("custom_futa_portrait_0.png", "custom_portrait.png"),
    ("custom_futa_mating_press_0.png", "custom_mating_press.png"),
    ("custom_futa_cowgirls_0.png", "custom_reverse_cowgirl.png"),
    ("custom_futa_cowgirls_0.png", "custom_cowgirl.png"),
    ("custom_futa_xray_0.png", "custom_xray.png"),
    ("custom_futa_deepthroat_0.png", "custom_deepthroat.png"),
    ("custom_futa_bc.png", "custom_ballclench.png"),
    ("custom_futa_bccrest.png", "custom_ballclenchcrest.png"),
    ("custom_wife_portrait_0.png", "custom_portrait.png"),
    ("custom_wife_mating_press_0.png", "custom_mating_press.png"),
    ("custom_wife_reverse_cowgirl_0.png", "custom_reverse_cowgirl.png"),
    ("custom_wife_cowgirl_0.png", "custom_cowgirl.png"),
    ("custom_wife_cowgirl_0.png", "custom_forward_cowgirl.png"),
    ("custom_wife_xray_0.png", "custom_xray.png"),
    ("custom_data.wife", "custom_data.spouse"),
    ("custom_data.spouse", "custom_data.wife"),
    # Deeproom / v1.5 Standard -> ModRoom v3.3 Legacy (_0.png)
    ("custom_portrait.png", "custom_futa_portrait_0.png"),
    ("custom_mating_press.png", "custom_futa_mating_press_0.png"),
    ("custom_reverse_cowgirl.png", "custom_futa_cowgirls_0.png"),
    ("custom_cowgirl.png", "custom_futa_cowgirls_0.png"),
    ("custom_xray.png", "custom_futa_xray_0.png"),
    ("custom_deepthroat.png", "custom_futa_deepthroat_0.png"),
    ("custom_ballclench.png", "custom_futa_bc.png"),
    ("custom_ballclenchcrest.png", "custom_futa_bccrest.png"),
    ("custom_portrait.png", "custom_wife_portrait_0.png"),
    ("custom_mating_press.png", "custom_wife_mating_press_0.png"),
    ("custom_reverse_cowgirl.png", "custom_wife_reverse_cowgirl_0.png"),
    ("custom_reverse_cowgirl.png", "custom_wife_cowgirl_0.png"),
    ("custom_cowgirl.png", "custom_wife_cowgirl_0.png"),
    ("custom_forward_cowgirl.png", "custom_wife_cowgirl_0.png"),
    ("custom_xray.png", "custom_wife_xray_0.png"),
    ("background.png", "custom_background.png"),
    ("custom_background.png", "background.png")
]


def plan_name_bridge(names, arch, pack_kind, is_modern_pack):
    """The (source, destination) copies the packer makes for one pack, in order.

    One planner for the packer and for the validator, so the pre-flight check judges exactly the files the
    build will contain. `names` is the set of lower-case file names in the pack folder.
    """
    out = []
    for src, dst in BRIDGE_PAIRS:
        pair_kind = _pair_kind(src, dst)
        if pack_kind and pair_kind and pair_kind != pack_kind:
            continue  # never create futa-named files in a wife pack (or the reverse): no loader reads them
        if arch == "deeproom":
            if dst.endswith("_0.png"):
                continue  # Deeproom: only normalise _0.png to standard names, never create _0.png copies
            if is_modern_pack and src.endswith("_0.png"):
                continue  # keep modern packs as authored
            if src == "custom_data.spouse" and dst == "custom_data.wife":
                continue  # Deeproom packs are natively .spouse; a .wife clone adds nothing
            if src == "custom_data.wife" and dst == "custom_data.spouse" and is_modern_pack:
                continue  # a .spouse file would send a modern wife pack to the legacy spouse loader
        elif arch == "modroom33":
            if is_modern_pack and src.endswith("_0.png"):
                continue  # native ModRoom pack: standard-named copies would switch it to the legacy loader
        else:
            continue
        if src in names and dst not in names:
            out.append((src, dst))
    return out


def is_modern_pack_names(names):
    """A pack authored in the modern/ModRoom format: it has a custom_*_mating_press_0.png strip."""
    return any(k.endswith("_0.png") and "mating_press" in k for k in names)


# Wife/spouse sprite formats slice frames differently: the legacy spouse loader reads a 4-frame mating
# press, 10-frame portrait, 5-frame reverse cowgirl and 4-frame X-ray; the ModRoom / modern wife (_0.png)
# loader reads 5, 17, 10 and 3. Renaming a strip between the two sets keeps its pixels but not its frame
# count, so those renames are recorded here and reported after the build.
BRIDGED_WIFE_PACKS = []
MODERN_PACKS_IN_V15 = []  # ModRoom-format packs (_0.png strips only) in a v1.5 build: v1.5 reads standard names only
_WIFE_FRAME_SENSITIVE = ("portrait", "mating_press", "reverse_cowgirl", "xray")


BRIDGE_SKIPPED = []  # (pack label, note): lossy conversions not done because approximate frames were not requested
BRIDGE_CONVERTED = []  # (pack label, note): strips whose frame count was converted while bridging names
_BRIDGE_TMP = []


def _bridge_tmpdir():
    if not _BRIDGE_TMP:
        d = tempfile.mkdtemp(prefix="wbp_bridge_")
        _BRIDGE_TMP.append(d)
        atexit.register(shutil.rmtree, d, True)
    return Path(_BRIDGE_TMP[0])


def _strip_role(kind, name):
    """(format, strip) a file name plays for `kind` ('futa'/'wife'), or None."""
    for fmt in ("modern", "standard"):
        for strip, n in wbconv.NAMES[(kind, fmt)].items():
            if n == name:
                return fmt, strip
        for (k, f, strip), aliases in wbconv.ALIASES.items():
            if k == kind and f == fmt and name in aliases:
                return fmt, strip
    return None


def convert_bridged_strip(src_path, src_name, dst_name, pack_kind, label, approximate=False, has_wife_desc=False):
    """Path to use as the source of a name bridge: the file itself, or a frame-converted copy.

    The ModRoom (_0.png) and standard formats slice a strip into different frame counts, so a pure rename leaves
    the engine cutting the strip at the wrong places. When the strip's real width matches the source format,
    it is padded or safely cropped with the converters' rules (wbconv) into a temp file. Lossy conversions (dropped
    frames) happen only when `approximate` is set, as in the converters' --approximate. Anything that does
    not match the tables (unknown strip, odd width, unreadable PNG) is bridged unchanged, as before."""
    kinds = [pack_kind] if pack_kind in ("futa", "wife") else [k for k in ("futa", "wife") if k == _pair_kind(src_name, dst_name)]
    for kind in kinds:
        s_role, d_role = _strip_role(kind, src_name), _strip_role(kind, dst_name)
        if kind == "wife" and s_role == ("standard", "reverse_cowgirl") and d_role == ("modern", "forward_cowgirl"):
            # a partner with no forward cowgirl: the reverse strip stands in for it, padded to ModRoom's 11 frames (as the converters do)
            src_n, dst_n, fw = wbconv.FRAMES[("wife", "standard")]["reverse_cowgirl"], wbconv.FRAMES[("wife", "modern")]["forward_cowgirl"], wbconv.FRAME_W
            size = wbconv.png_size(src_path)
            if not size or size[0] != src_n * fw:
                return src_path
            try:
                tmp = _bridge_tmpdir() / f"{len(BRIDGE_CONVERTED):05d}_{dst_name}"
                wbconv.write_png(tmp, wbconv.pad_width(wbconv.read_png(src_path), dst_n * fw))
            except (wbconv.PngError, OSError, zlib.error):
                return src_path
            BRIDGE_CONVERTED.append((label, f"forward cowgirl taken from the reverse cowgirl, {src_n} to {dst_n} frames (padded)"))
            return tmp
        if not s_role or not d_role or s_role[1] != d_role[1] or s_role[0] == d_role[0]:
            continue
        (src_fmt, strip), dst_fmt = s_role, d_role[0]
        src_n, dst_n = wbconv.FRAMES[(kind, src_fmt)].get(strip), wbconv.FRAMES[(kind, dst_fmt)].get(strip)
        fw = wbconv._frame_w(strip)
        size = wbconv.png_size(src_path)
        if not src_n or not dst_n or src_n == dst_n or not size or size[0] != src_n * fw:
            return src_path
        if (kind, strip, src_fmt, dst_fmt, src_n, dst_n) == ("wife", "portrait", "standard", "modern", 10, 17):
            # ModRoom draws partner portraits with the 17-frame modern layout only: lay the 10 standard frames out that way
            try:
                tmp = _bridge_tmpdir() / f"{len(BRIDGE_CONVERTED):05d}_{dst_name}"
                wbconv.write_png(tmp, wbconv.wife_portrait_std_to_modern(wbconv.read_png(src_path), fw))
            except (wbconv.PngError, OSError, zlib.error):
                return src_path
            BRIDGE_CONVERTED.append((label, f"portrait {src_n} to {dst_n} frames (laid out as the modern portrait)"))
            return tmp
        policy = wbconv._policy(kind, strip, src_n, dst_n)
        if kind == "wife" and strip == "xray" and dst_n < src_n and not has_wife_desc:
            return src_path  # the X-ray crop is only done for packs with a custom_data.wife (as in the converters)
        if policy == "approximate" and not approximate:
            BRIDGE_SKIPPED.append((label, f"{strip} {src_n} to {dst_n} frames (renamed only; use --approximate to convert)"))
            return src_path
        try:
            img = wbconv.read_png(src_path)
            picked = wbconv.FRAME_MAPS.get((kind, strip)) if (src_fmt == "modern" and dst_fmt == "standard") else None
            if picked and len(picked) == dst_n and max(picked) < src_n and policy == "approximate":
                out, how = wbconv.select_frames(img, fw, picked), "frames " + ",".join(map(str, picked)) + " kept"
            elif dst_n > src_n:
                out, how = wbconv.pad_width(img, dst_n * fw), "padded"
            else:
                out, how = wbconv.crop_width(img, dst_n * fw), "first frames kept"
            tmp = _bridge_tmpdir() / f"{len(BRIDGE_CONVERTED):05d}_{dst_name}"
            wbconv.write_png(tmp, out)
        except (wbconv.PngError, OSError, zlib.error):
            return src_path
        BRIDGE_CONVERTED.append((label, f"{strip} {src_n} to {dst_n} frames ({how}{'' if policy in ('pad', 'copy', 'crop_safe') else ', approximate'})"))
        return tmp
    return src_path


def _pack_kind(cat_dir_name, f_map):
    """'futa', 'wife', 'bed' or None (unknown). The descriptor file wins over the category folder."""
    has_futa = "custom_data.futa" in f_map
    has_wife = "custom_data.spouse" in f_map or "custom_data.wife" in f_map
    if has_futa and has_wife:
        return None  # hybrid pack: keep every bridge, as before
    if has_futa:
        return "futa"
    if has_wife:
        return "wife"
    if "custom_data.bedroom" in f_map:
        return "bed"
    c = str(cat_dir_name).lower()
    if "futa" in c:
        return "futa"
    if "wive" in c or "wife" in c or "spouse" in c:
        return "wife"
    if "bedroom" in c:
        return "bed"
    return None


def _pair_kind(src, dst):
    """Which kind of pack a filename pair belongs to; None when it applies to any pack."""
    both = (src + " " + dst).lower()
    if "futa" in both or "ballclench" in both:
        return "futa"
    if "wife" in both or "spouse" in both:
        return "wife"
    if "background" in both:
        return "bed"
    return None


def _note_wife_bridge(pack_kind, src, dst, pack_label):
    """Record a wife pack that had a frame-sensitive sprite renamed between the _0.png and standard names."""
    if pack_kind != "wife" or pack_label in BRIDGED_WIFE_PACKS:
        return
    if src.endswith("_0.png") == dst.endswith("_0.png"):
        return
    if any(k in src or k in dst for k in _WIFE_FRAME_SENSITIVE):
        BRIDGED_WIFE_PACKS.append(pack_label)


def gather_custom_assets(folder, is_v15=False, target_arch="deeproom", skip_dirs=(), approximate=False):
    """
    Finds all valid GameMaker custom asset files in custom_* directories, dialogue*, texture_packs, etc.
    Filters out raw art project files (.aseprite, .clip, .pdn, .kra, .zip, etc.) to prevent APK bloat and Android asset table crashes.
    Sanitizes all relative APK paths to lowercase with underscores to match ToyBridge's exact Android AssetManager convention.
    
    Deeproom APK Mandate:
    For Deeproom APKs, assets belong strictly under assets/custom_stuff/.
    Never place or mirror custom/ into both root and custom_stuff/.
    Returns list of (full_file_path, relative_apk_path).
    """
    BRIDGED_WIFE_PACKS.clear()
    BRIDGE_CONVERTED.clear()
    BRIDGE_SKIPPED.clear()
    MODERN_PACKS_IN_V15.clear()
    valid_exts = {".png", ".ogg", ".wav", ".mp3", ".json", ".futa", ".spouse", ".wife", ".bedroom", ".ini", ".jpg", ".jpeg", ".gif", ".webp"}
    ignored_containers = {"templates", "template", "ball clench stuff", "custom sperm", "quarantine", "!duplicates", "__pycache__", ".git", "edit_files"}
    ignored_project_exts = {".aseprite", ".ase", ".clip", ".pdn", ".kra", ".psd", ".xcf", ".blend", ".zip", ".rar", ".7z", ".tar", ".gz", ".bak", ".tmp", ".pdf", ".docx", ".doc"}
    folder = Path(folder).resolve()
    assets = []
    seen_apk_paths = set()

    is_dr = (folder / "custom_stuff").is_dir()

    # Exclude development templates folder from target prefixes
    target_prefixes = ("custom_", "dialogue", "texture_packs", "custom_stuff")

    for root, dirs, files in os.walk(folder):
        rel_root = Path(root).relative_to(folder)
        root_parts = rel_root.parts
        if not root_parts:
            for file in files:
                if file.lower() == "options.ini":
                    fpath = Path(root) / file
                    assets.append((fpath, f"assets/{file.lower()}"))
            continue

        # Skip any bloat container directory (!duplicates, quarantine, templates, etc.) and packs skipped by the pre-flight checks
        if any(p.lower() in ignored_containers for p in root_parts) or _in_skipped(root, skip_dirs):
            dirs[:] = []
            continue

        first_dir = root_parts[0].lower()
        if is_dr and first_dir == "custom_stuff" and len(root_parts) > 1:
            first_dir = root_parts[1].lower()

        if any(first_dir.startswith(pref) for pref in target_prefixes):
            f_map = {f.lower(): (Path(root) / f) for f in files}
            for file in files:
                fpath = Path(root) / file
                ext = fpath.suffix.lower()
                fname_l = fpath.name.lower()

                # Filter out raw project files, archives, non-runtime notes, and binaries
                if ext in ignored_project_exts or (ext == ".txt" and fname_l != "_manifest.txt"):
                    continue
                if fname_l == "data.win" or fname_l.startswith(".") or fname_l.endswith("~"):
                    continue

                if ext in valid_exts or fname_l == "_manifest.txt":
                    rel_p = fpath.relative_to(folder)
                    clean_rel = sanitize_apk_path(rel_p)

                    # Architecture-Strict Path Assignment (Eliminates Cross-Architecture Bloat)
                    if target_arch == "deeproom":
                        # Deeproom 4.0.3 strictly requires assets under assets/custom_stuff/
                        if not clean_rel.startswith("custom_stuff/"):
                            apk_p = f"assets/custom_stuff/{clean_rel}"
                        else:
                            apk_p = f"assets/{clean_rel}"
                    elif target_arch == "modroom33":
                        # ModRoom v3.3 strictly requires root-level assets under assets/custom_*/
                        if clean_rel.startswith("custom_stuff/"):
                            clean_rel = "/".join(clean_rel.split("/")[1:])
                        apk_p = f"assets/{clean_rel}"
                    else:
                        apk_p = f"assets/{clean_rel}"

                    if apk_p not in seen_apk_paths:
                        seen_apk_paths.add(apk_p)
                        assets.append((fpath, apk_p))

            # Forward-Only ModRoom v3.3 (_0.png) & Loose Portrait -> Standard Normalization (Applied to custom_stuff/ AND root categories)
            is_char_pack = (len(root_parts) == 2 and not is_dr) or (len(root_parts) == 3 and is_dr and root_parts[0].lower() == "custom_stuff")
            if is_char_pack:
                cat_dir_name = sanitize_apk_part(root_parts[1] if is_dr else root_parts[0])
                char_dir_name = sanitize_apk_part(root_parts[2] if is_dr else root_parts[1])
                # Complete Bi-Directional Asset Mapping between ModRoom v3.3 Legacy (_0.png) & Deeproom/v1.5 Standard
                pack_kind = _pack_kind(cat_dir_name, f_map)
                # A pack authored in the modern/ModRoom format (custom_*_mating_press_0.png) is read natively by Deeproom.
                # Standard-named copies of its strips would switch Deeproom to the legacy loaders, which cut the same
                # strip into different frame counts (futa mating press 9 vs 24, wife 4 vs 5, portrait 10 vs 17, ...).
                is_modern_pack = is_modern_pack_names(f_map)
                if is_v15 and is_modern_pack and "custom_mating_press.png" not in f_map:
                    MODERN_PACKS_IN_V15.append(f"{cat_dir_name}/{char_dir_name}")
                for v33_src, norm_dst in plan_name_bridge(set(f_map), target_arch, pack_kind, is_modern_pack):
                    if target_arch == "deeproom":
                        apk_p = f"assets/custom_stuff/{cat_dir_name}/{char_dir_name}/{norm_dst}"
                    else:
                        apk_p = f"assets/{cat_dir_name}/{char_dir_name}/{norm_dst}"
                    if apk_p not in seen_apk_paths:
                        seen_apk_paths.add(apk_p)
                        assets.append((convert_bridged_strip(f_map[v33_src], v33_src, norm_dst, pack_kind, f"{cat_dir_name}/{char_dir_name}", approximate, "custom_data.wife" in f_map), apk_p))
                        _note_wife_bridge(pack_kind, v33_src, norm_dst, f"{cat_dir_name}/{char_dir_name}")

                # If custom_portrait.png is missing, automatically map any loose portrait PNG to custom_portrait.png
                if "custom_portrait.png" not in f_map:
                    for f in files:
                        fl = f.lower()
                        if "portrait" in fl and fl.endswith(".png") and fl != "custom_portrait.png":
                            if is_modern_pack and fl.endswith("_0.png"):
                                continue  # a native modern pack keeps its _0.png portrait; a custom_portrait.png copy would switch the loader
                            portrait_dir = "assets/custom_stuff" if target_arch == "deeproom" else "assets"  # each engine reads one place only
                            apk_p = f"{portrait_dir}/{cat_dir_name}/{char_dir_name}/custom_portrait.png"
                            if apk_p not in seen_apk_paths:
                                seen_apk_paths.add(apk_p)
                                assets.append((Path(root) / f, apk_p))
                            break

    # Automatic routing of loose root custom/ packs into categories (non-Deeproom only)
    if not is_dr:
        custom_dir = folder / "custom"
        if custom_dir.is_dir():
            used_cat_names = {"custom_futas": set(), "custom_wives": set(), "custom_bedrooms": set()}
            for pack in sorted(custom_dir.iterdir()):
                if pack.is_dir() and not pack.name.startswith(".") and not _in_skipped(pack, skip_dirs):
                    cat = None
                    p_files = {f.name.lower() for f in pack.iterdir() if f.is_file()}
                    if (pack / "custom_data.futa").exists() or (pack / "custom_futa_portrait_0.png").exists() or any(f.endswith(".futa") for f in p_files):
                        cat = "custom_futas"
                    elif (pack / "custom_data.spouse").exists() or (pack / "custom_data.wife").exists() or (pack / "custom_wife.ini").exists() or (pack / "custom_wife_portrait_0.png").exists() or (pack / "custom_forward_cowgirl.png").exists() or (pack / "custom_egg.png").exists() or any(f.endswith(".spouse") or f.endswith(".wife") for f in p_files) or any(w in pack.name.lower() for w in ["wife", "wives", "spouse", "partner", "bottom"]):
                        cat = "custom_wives"
                    elif (pack / "custom_data.bedroom").exists() or (pack / "custom_background.png").exists() or (pack / "background.png").exists() or any(f.endswith(".bedroom") for f in p_files) or any(w in pack.name.lower() for w in ["bedroom", "bedrooms", "room", "background"]):
                        cat = "custom_bedrooms"
                    elif (pack / "custom_portrait.png").exists() or (pack / "custom_mating_press.png").exists():
                        cat = "custom_futas"

                    display_name = extract_pack_display_name(pack)
                    clean_pname = sanitize_apk_part(display_name)
                    if cat:
                        clean_pname = unique_apk_name(clean_pname, pack.name, used_cat_names[cat])
                        used_cat_names[cat].add(clean_pname)
                    for root, dirs, files in os.walk(pack):
                        rel_to_pack = Path(root).relative_to(pack)
                        clean_sub = "/".join(sanitize_apk_part(p) for p in rel_to_pack.parts) if rel_to_pack.parts else ""
                        for f in files:
                            fpath = Path(root) / f
                            if fpath.suffix.lower() in valid_exts and not fpath.name.startswith(".") and not fpath.name.endswith("~"):
                                clean_f = sanitize_apk_part(fpath.stem) + fpath.suffix.lower()
                                sub_p = f"{clean_sub}/{clean_f}" if clean_sub else clean_f
                                if is_v15:
                                    apk_p = f"assets/custom/{clean_pname}/{sub_p}"
                                elif cat:
                                    apk_p = f"assets/{cat}/{clean_pname}/{sub_p}"
                                else:
                                    apk_p = None
                                if apk_p and apk_p not in seen_apk_paths:
                                    seen_apk_paths.add(apk_p)
                                    assets.append((fpath, apk_p))

    return assets
