"""Golden-output harness for WB_Mobile_Patcher.

Proves a refactor changed nothing. It runs the real pipeline on fixed inputs and records
hashes of everything the patcher produces:
  * every GML script handed to `UndertaleModCli replace` (that call is faked, so no game.droid
    is rebuilt and the run is fast),
  * every entry of the APK it would write (name, CRC32, size, compression) - signing is skipped,
  * the set of patch anchors that were not found (PATCH_MISSES),
  * the output of the dynamic (fallback) patchers on the vanilla PC game scripts.

Usage:
  python tests/golden_harness.py --record      # write tests/golden.json from the current code
  python tests/golden_harness.py               # compare current code against tests/golden.json
  options: --patcher <path to WB_Mobile_Patcher.py>  --io <folder with the example games/APKs>
           --only deeproom,modroom33,v15,dyn_deeproom,dyn_modroom33

Default inputs are the example folders in ../io next to the repository (see SCENARIOS). Scenarios whose inputs
are missing are skipped and reported, never silently passed.
"""
import argparse, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile, time, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

SCENARIOS = {
    "deeproom":  {"kind": "build", "apk": "wifes_bedroom1_4.apk", "folder": "Deeproom 4.0.3"},
    "modroom33": {"kind": "build", "apk": "wifes_bedroom1_4.apk", "folder": "ModRoom V3.3"},
    "v15":       {"kind": "build", "apk": "wifes_bedroom1_5.apk", "folder": "wifes_bedroom_win1_5"},
    "dyn_deeproom":  {"kind": "dynamic", "data": "Deeproom 4.0.3/data.win"},
    "dyn_modroom33": {"kind": "dynamic", "data": "ModRoom V3.3/data.win"},
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load_patcher(path):
    path = Path(path).resolve()
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("wbp_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["wbp_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


class Recorder:
    """Replaces subprocess.run: UTMT `replace` is recorded and faked, everything else runs for real."""
    def __init__(self):
        self.real = subprocess.run
        self.replaced = []

    def __call__(self, cmd, *a, **kw):
        if isinstance(cmd, (list, tuple)) and len(cmd) > 2 and Path(str(cmd[0])).name.lower().startswith("undertalemodcli") and cmd[1] == "replace":
            src = Path(cmd[2])
            out = None
            for i, c in enumerate(cmd):
                if c == "-c" and i + 1 < len(cmd):
                    name, _, path = str(cmd[i + 1]).partition("=")
                    self.replaced.append((name, sha(Path(path).read_bytes())))
                if c == "-o" and i + 1 < len(cmd):
                    out = Path(cmd[i + 1])
            if out is not None and src.exists() and out != src:
                shutil.copyfile(src, out)
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return self.real(cmd, *a, **kw)


def set_everywhere(m, name, value):
    """Set `name` in the entry module and in every wbp.* module that has it (works for a single file or a package)."""
    old = getattr(m, name)
    for mod in [m] + [v for k, v in list(sys.modules.items()) if k.startswith("wbp.") and v is not None]:
        if hasattr(mod, name):
            setattr(mod, name, value)
    return old


def run_build(m, io, sc):
    apk, folder = io / sc["apk"], io / sc["folder"]
    if not apk.exists() or not folder.exists():
        return {"skipped": f"missing input: {apk if not apk.exists() else folder}"}
    rec = Recorder()
    real_run, real_sleep = subprocess.run, time.sleep
    real_sign = set_everywhere(m, "sign_apk_file", lambda p, **kw: None)
    subprocess.run, time.sleep = rec, (lambda s: None)
    try:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "out.apk"
            opts = {"quarantine_duplicates": True, "core_manifest": True, "scaling": True, "stability": True,
                    "climax_and_panels": True, "css_and_favs": True, "phone_import": True,
                    "toy_telemetry": False, "fast_packaging": True}
            m.PATCH_MISSES.clear()
            m.patch_game_apk(Path(m.get_utmt_cli()), apk, target, source_folder=folder, opts=opts)
            with zipfile.ZipFile(target) as z:
                entries = sorted((i.filename, i.CRC, i.file_size) for i in z.infolist())
            report = {}
            for suffix in ("_skipped_packs.md", "_skipped_packs.json", "_patch_report.txt"):
                p = target.with_name(target.stem + suffix)
                if p.exists():
                    body = p.read_bytes().replace(str(folder).encode(), b"<SRC>")
                    body = re.sub(rb"\d{4}-\d\d-\d\d[ T]\d\d:\d\d(:\d\d)?", b"<TIME>", body)
                    report[suffix] = sha(body)
    finally:
        subprocess.run, time.sleep = real_run, real_sleep
        set_everywhere(m, "sign_apk_file", real_sign)
    return {
        "replaced_gml": [list(x) for x in rec.replaced],
        "apk_entry_count": len(entries),
        "apk_entries_hash": sha(json.dumps(entries).encode()),
        "reports": report,
        "patch_misses": sorted(set(m.PATCH_MISSES)),
    }


def run_dynamic(m, io, sc):
    data = io / sc["data"]
    if not data.exists():
        return {"skipped": f"missing input: {data}"}
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        shutil.copyfile(data, td / "game.droid")
        cli = m.get_utmt_cli()
        names = ["oFutaMatingPress_Create_0", "oFutaMatingPress_Draw_0", "oFutaMatingPress_Step_0",
                 "oBackground_Create_0", "oDialogueManager_Create_0"]
        args = [str(cli), "dump", str(td / "game.droid")]
        for n in names:
            args += ["-c", "gml_Object_" + n]
        subprocess.run(args + ["-o", str(td)], capture_output=True, stdin=subprocess.DEVNULL)
        ce = td / "CodeEntries"

        def rd(n):
            p = ce / f"gml_Object_{n}.gml"
            return p.read_text(encoding="utf-8", errors="replace") if p.exists() else None
        out = {}
        m.PATCH_MISSES.clear()
        for label, fn, ent in (("create", m.patch_create_code, "oFutaMatingPress_Create_0"),
                               ("step", m.patch_step_code, "oFutaMatingPress_Step_0"),
                               ("draw", m.patch_draw_code, "oFutaMatingPress_Draw_0"),
                               ("background", m.patch_background_code, "oBackground_Create_0"),
                               ("dialogue", m.patch_dialogue_code, "oDialogueManager_Create_0")):
            src = rd(ent)
            out[label] = sha(fn(src).encode("utf-8")) if src is not None else "no-source"
        out["patch_misses"] = sorted(set(m.PATCH_MISSES))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--patcher", default=str(ROOT / "WB_Mobile_Patcher.py"))
    ap.add_argument("--io", default=os.environ.get("WBP_IO", str(HERE.parent.parent / "io")))
    ap.add_argument("--golden", default=str(HERE / "golden.json"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    io = Path(a.io)
    m = load_patcher(a.patcher)
    names = [n for n in SCENARIOS if not a.only or n in a.only.split(",")]
    result = {}
    for n in names:
        sc = SCENARIOS[n]
        t0 = time.time()
        result[n] = run_build(m, io, sc) if sc["kind"] == "build" else run_dynamic(m, io, sc)
        print(f"[{n}] {'SKIPPED: ' + result[n]['skipped'] if 'skipped' in result[n] else 'ok'} ({time.time() - t0:.0f}s)", flush=True)
    result["bundle_sha256"] = sha((Path(a.patcher).parent / "core" / "mobile_engine.bundle").read_bytes())
    if a.record:
        old = json.loads(Path(a.golden).read_text()) if Path(a.golden).exists() and a.only else {}
        old.update(result)
        Path(a.golden).write_text(json.dumps(old, indent=1, sort_keys=True))
        print("recorded", a.golden)
        return 0
    gold = json.loads(Path(a.golden).read_text())
    bad = 0
    for n, r in result.items():
        if isinstance(r, dict) and "skipped" in r:
            print(f"SKIP  {n}: {r['skipped']}")
            bad += 1
            continue
        if r != gold.get(n):
            bad += 1
            print(f"DIFF  {n}")
            g = gold.get(n)
            if isinstance(r, dict) and isinstance(g, dict):
                for k in sorted(set(r) | set(g)):
                    if r.get(k) != g.get(k):
                        print(f"        field {k} differs")
        else:
            print(f"SAME  {n}")
    print("RESULT:", "IDENTICAL" if not bad else f"{bad} scenario(s) differ or skipped")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
