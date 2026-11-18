"""wbp.signing: which key signs the built APK.

Default: a personal key made once on this computer (random password), kept outside the repository in
~/.wb_mobile_patcher (%USERPROFILE%\\.wb_mobile_patcher on Windows). Android installs an update only over an APK
signed with the same key, so with a personal key nobody else can push an "update" over your build.

--legacy-key: the shared key in core/ that builds before 2026-11-18 were signed with. It is public (it has been in
the repository), so use it only to keep updating an install made with an older build; switching an existing
install to the personal key needs an uninstall first (back up the save area if you want to keep it).
"""
import os
import secrets
import subprocess
from pathlib import Path

from wbp.common import LOGGER, ROOT_DIR
from wbp.env import get_jdk_tool

PERSONAL_ALIAS = "wbpatcher"
LEGACY_ALIAS = "apkpatcherkey"


def key_dir() -> Path:
    # Not %APPDATA%: the Microsoft Store Python redirects its own writes there to a private folder that keytool
    # and the signer (both Java) cannot see.
    return Path.home() / ".wb_mobile_patcher"


def legacy_key():
    """(keystore, alias, password) of the shared key, or None when its files are missing."""
    for d in (ROOT_DIR / "core", ROOT_DIR):
        ks, pw = d / "apkpatcher.keystore", d / "apkpatcher.keystore.pass"
        if ks.exists() and pw.exists():
            return ks, LEGACY_ALIAS, pw.read_text(encoding="utf-8").strip()
    return None


def personal_key(directory=None, keytool=None):
    """(keystore, alias, password) of this computer's key; made on first use. Raises RuntimeError when keytool fails."""
    d = Path(directory) if directory else key_dir()
    ks, pw = d / "signing.keystore", d / "signing.keystore.pass"
    if ks.exists() and pw.exists():
        return ks, PERSONAL_ALIAS, pw.read_text(encoding="utf-8").strip()
    d.mkdir(parents=True, exist_ok=True)
    password = secrets.token_urlsafe(24)
    tmp = ks.with_suffix(".tmp")
    if tmp.exists():
        tmp.unlink()
    cmd = [keytool or get_jdk_tool("keytool"), "-genkeypair", "-keystore", str(tmp), "-storetype", "PKCS12",
           "-alias", PERSONAL_ALIAS, "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
           "-dname", "CN=WB Mobile Patcher user", "-storepass:env", "WBP_KS_PASS", "-keypass:env", "WBP_KS_PASS"]
    env = dict(os.environ, WBP_KS_PASS=password)
    res = subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace", env=env)
    if res.returncode != 0 or not tmp.exists():
        if tmp.exists():
            tmp.unlink()
        raise RuntimeError("keytool could not create the signing key: " + (res.stderr or res.stdout).strip()[:300])
    pw.write_text(password, encoding="utf-8")
    tmp.replace(ks)
    LOGGER.log(f"Created your personal signing key in {d} (keep this folder; back it up to keep updating your installs).", prefix="[+]")
    LOGGER.log("APKs signed with it do not install over ones built before 2026-11-18 (shared key): uninstall first, "
               "or build with --legacy-key to keep updating an older install.", prefix="[!]")
    return ks, PERSONAL_ALIAS, password


def signing_key(use_legacy=False):
    """The key to sign with: the shared legacy key when asked for, else the personal one."""
    if use_legacy:
        key = legacy_key()
        if key is None:
            raise RuntimeError("--legacy-key: core/apkpatcher.keystore or its .pass file is missing.")
        LOGGER.log("Signing with the shared legacy key (--legacy-key): it is public, use it only to update an older install.", prefix="[!]")
        return key
    return personal_key()
