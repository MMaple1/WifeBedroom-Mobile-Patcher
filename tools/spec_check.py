"""Check that every code excerpt in the technical specification is shipped code.

  python tools/spec_check.py [spec.md] [--strict] [--list]

A fenced code block passes when each of its significant lines (not blank, not a comment, not only braces or
punctuation, at least 6 characters) appears word for word, ignoring indentation, in the shipped sources:
core/bundle_src/*.gml, core/gml_patches/**/*.gml, wbp/*.py, WB_Mobile_Patcher.py and, when the sibling
converter repositories are present, their .py files. Blocks tagged `text` or `json` are examples, not excerpts,
and are skipped. --strict exits 1 when a block has lines that are not in the sources or when the text still holds
audit wording. --list prints every block with its match.
"""
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN = re.compile(r"\baudit(ed|s)?\b|not verified|unverified|TODO|TBD|FIXME|open item|remaining work", re.I)
SKIP_LANGS = {"", "text", "json", "txt", "console", "bash", "sh", "powershell", "ini", "diff", "yaml", "xml"}


def norm(line):
    return re.sub(r"\s+", " ", line.strip())


def significant(line):
    n = norm(line)
    return len(n) >= 6 and not n.startswith(("//", "#", "*", "/*")) and re.search(r"[A-Za-z0-9_]", n)


def corpus_files():
    files = list((ROOT / "core" / "bundle_src").glob("*.gml")) + list((ROOT / "core" / "gml_patches").rglob("*.gml"))
    files += list((ROOT / "wbp").glob("*.py")) + [ROOT / "WB_Mobile_Patcher.py"]
    for sib in ("Modded_to_WB_1.5", "WB_1.5_to_Modded"):
        d = ROOT.parent / "WB_Converters" / sib
        if d.is_dir():
            files += list(d.glob("*.py")) + list((d / "core").glob("*.py"))
    return [f for f in files if f.is_file()]


def load_corpus():
    lines = set()
    for f in corpus_files():
        for raw in f.read_text(encoding="utf-8", errors="replace").split("\n"):
            lines.add(norm(raw))
    return lines


def blocks(text):
    """(heading, lang, first_line_no, [lines]) for each fenced block."""
    out, heading, fence, buf, start = [], "", None, [], 0
    for i, line in enumerate(text.split("\n"), 1):
        if fence is None:
            if line.startswith("#"):
                heading = line.lstrip("# ").strip()
            elif line.startswith("```"):
                fence, buf, start = line[3:].strip().lower(), [], i + 1
        elif line.startswith("```"):
            out.append((heading, fence, start, buf))
            fence = None
        else:
            buf.append(line)
    return out


def check(spec, list_all=False):
    text = Path(spec).read_text(encoding="utf-8")
    corpus = load_corpus()
    bad = 0
    for heading, lang, start, lines in blocks(text):
        if lang in SKIP_LANGS:
            continue
        sig = [l for l in lines if significant(l)]
        miss = [l for l in sig if norm(l) not in corpus]
        if miss:
            bad += 1
        if miss or list_all:
            print(f"line {start}: [{heading[:60]}] {len(sig) - len(miss)}/{len(sig)} lines in the shipped code")
            for l in miss[:6]:
                print("    missing: " + norm(l)[:110])
    words = [(i, l.strip()[:100]) for i, l in enumerate(text.split("\n"), 1) if FORBIDDEN.search(l)]
    for i, l in words[:20]:
        print(f"line {i}: audit/open wording: {l}")
    print(f"{bad} block(s) with lines not in the shipped code; {len(words)} line(s) with audit/open wording")
    return bad, len(words)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    spec = args[0] if args else str(ROOT / "core" / "TECHNICAL_SPECIFICATION.md")
    b, w = check(spec, "--list" in sys.argv)
    sys.exit(1 if "--strict" in sys.argv and (b or w) else 0)
