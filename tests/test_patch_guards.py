"""Every text patch on game code reports a miss when its anchor is absent (no silent str.replace).   Run: python -m unittest discover -s tests"""
import ast
import unittest
from pathlib import Path

WBP = Path(__file__).resolve().parent.parent / "wbp"


def silent_replaces(path):
    """`x = x.replace(anchor, ...)` lines that record nothing in PATCH_MISSES when the anchor is missing."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    parents = {c: n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
    found = []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "replace"
                and isinstance(n.value.func.value, ast.Name) and n.value.func.value.id == n.targets[0].id):
            continue
        p = parents.get(n)
        if isinstance(p, ast.If) and "PATCH_MISSES" in ast.get_source_segment(src, p):
            continue
        found.append(n.lineno)
    return found


class PatchGuardTests(unittest.TestCase):
    def test_gml_patches_has_no_silent_replace(self):
        self.assertEqual(silent_replaces(WBP / "gml_patches.py"), [],
                         "use guarded_replace() (count=-1 for replace-all) or an if/else that appends to PATCH_MISSES")


if __name__ == "__main__":
    unittest.main()
