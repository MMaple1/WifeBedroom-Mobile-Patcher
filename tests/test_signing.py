"""wbp.signing: personal key made once with keytool, legacy key read from core/.   Run: python -m unittest discover -s tests"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wbp import signing  # noqa: E402
from wbp.env import get_jdk_tool  # noqa: E402

KEYTOOL = get_jdk_tool("keytool")
HAVE_KEYTOOL = bool(shutil.which(KEYTOOL) or Path(KEYTOOL).exists())


class SigningTests(unittest.TestCase):
    def test_legacy_key_found(self):
        key = signing.legacy_key()
        self.assertIsNotNone(key)
        self.assertEqual(key[1], signing.LEGACY_ALIAS)
        self.assertTrue(key[2])

    @unittest.skipUnless(HAVE_KEYTOOL, "keytool not installed")
    def test_personal_key_made_once_and_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            ks, alias, pw = signing.personal_key(tmp)
            self.assertTrue(ks.exists())
            self.assertEqual(alias, signing.PERSONAL_ALIAS)
            self.assertGreaterEqual(len(pw), 24)
            self.assertNotEqual(pw, signing.legacy_key()[2])
            before = ks.read_bytes()
            self.assertEqual(signing.personal_key(tmp), (ks, alias, pw))   # second call reuses the same key
            self.assertEqual(ks.read_bytes(), before)
            res = subprocess.run([KEYTOOL, "-list", "-keystore", str(ks), "-storepass:env", "P"], capture_output=True,
                                 text=True, env={**__import__("os").environ, "P": pw})
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn(alias, res.stdout.lower())

    def test_missing_legacy_key_is_an_error(self):
        real = signing.legacy_key
        signing.legacy_key = lambda: None
        try:
            with self.assertRaises(RuntimeError):
                signing.signing_key(use_legacy=True)
        finally:
            signing.legacy_key = real


if __name__ == "__main__":
    unittest.main()
