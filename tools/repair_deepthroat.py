#!/usr/bin/env python3
"""Fix Deeproom partners whose deepthroat sprite sits too high (packs converted before 2026-11-17).

Older converters added a [deepthroat] block (origin_y 150, or a v1.5 value copied unchanged) to the
custom_data.spouse of every partner converted for Deeproom, which draws the sprite 66-70 px high in the game
and in APKs built from it. Run this on the game's custom_wives folder before building. Hand-made blocks are
left alone. Dry run unless --apply; with --apply the originals go to a backup zip next to the folder.

  python tools/repair_deepthroat.py "<Deeproom>/custom_stuff/custom_wives" [--apply]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wbp import wbconv  # noqa: E402

if __name__ == "__main__":
    sys.exit(wbconv.repair_deepthroat_main())
