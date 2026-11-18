"""Keep the four copies of wbconv.py identical (two converters, the patcher, the Custom Studio).

  python tools/sync_wbconv.py          copy the canonical file over the other three
  python tools/sync_wbconv.py --check  report only; exit 1 if they differ

Canonical: ../WB_Converters/Modded_to_WB_1.5/core/wbconv.py. Copies: ../WB_Converters/WB_1.5_to_Modded/core/wbconv.py,
this repo's wbp/wbconv.py and ../Wifes_Bedroom_Custom_Studio/backend/wbconv.py. A folder that is not present is skipped.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONVERTERS = ROOT.parent / "WB_Converters"
CANON = CONVERTERS / "Modded_to_WB_1.5" / "core" / "wbconv.py"
COPIES = [CONVERTERS / "WB_1.5_to_Modded" / "core" / "wbconv.py", ROOT / "wbp" / "wbconv.py",
          ROOT.parent / "Wifes_Bedroom_Custom_Studio" / "backend" / "wbconv.py"]


def differing():
    """Copies that exist and differ from the canonical file."""
    if not CANON.is_file():
        return None
    return [c for c in COPIES if c.parent.is_dir() and (not c.is_file() or c.read_bytes() != CANON.read_bytes())]


def main():
    diff = differing()
    if diff is None:
        print(f"canonical file not found: {CANON}")
        return 1
    if not diff:
        print("wbconv.py copies are identical")
        return 0
    for c in diff:
        print(("DIFFERS: " if "--check" in sys.argv else "copied to ") + str(c))
        if "--check" not in sys.argv:
            shutil.copyfile(CANON, c)
    return 1 if "--check" in sys.argv else 0


if __name__ == "__main__":
    sys.exit(main())
