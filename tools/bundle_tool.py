"""Unpack / pack core/mobile_engine.bundle (zlib-compressed JSON: code-entry file name -> GML source).

  python tools/bundle_tool.py unpack     # core/mobile_engine.bundle -> core/bundle_src/*.gml
  python tools/bundle_tool.py pack       # core/bundle_src/*.gml     -> core/mobile_engine.bundle
  python tools/bundle_tool.py check      # verify the bundle matches core/bundle_src

core/bundle_src is the editable source. Edit those files, run `pack`, then run
`python tests/golden_harness.py` (and --record when the change is intended).
Files are read and written without newline translation.
"""
import json, sys, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "core" / "mobile_engine.bundle"
SRC = ROOT / "core" / "bundle_src"


def read_src():
    out = {}
    for p in sorted(SRC.glob("*.gml")):
        with open(p, "r", encoding="utf-8", newline="") as f:
            out[p.name] = f.read()
    return out


def pack_bytes(scripts):
    return zlib.compress(json.dumps(scripts, ensure_ascii=False).encode("utf-8"), 9)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "unpack":
        scripts = json.loads(zlib.decompress(BUNDLE.read_bytes()))
        SRC.mkdir(exist_ok=True)
        for name, text in scripts.items():
            with open(SRC / name, "w", encoding="utf-8", newline="") as f:
                f.write(text)
        print(f"unpacked {len(scripts)} scripts to {SRC}")
    elif cmd == "pack":
        scripts = read_src()
        BUNDLE.write_bytes(pack_bytes(scripts))
        print(f"packed {len(scripts)} scripts into {BUNDLE} ({BUNDLE.stat().st_size} bytes)")
    elif cmd == "check":
        same = json.loads(zlib.decompress(BUNDLE.read_bytes())) == read_src()
        print("bundle matches core/bundle_src" if same else "MISMATCH: bundle differs from core/bundle_src")
        return 0 if same else 1
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
