"""wbp.env"""
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
from wbp.common import LOGGER, ROOT_DIR

# -----------------------------------------------------------------------------
# TOOL & ENVIRONMENT RESOLUTION
# -----------------------------------------------------------------------------
def get_utmt_cli():
    env_cli = os.environ.get("UTMT_CLI")
    if env_cli and Path(env_cli).exists():
        return str(Path(env_cli).resolve())

    patcher_dir = ROOT_DIR
    core_dir = patcher_dir / "core"

    which_utmt = shutil.which("UndertaleModCli") or shutil.which("UndertaleModCli.exe")
    if which_utmt:
        return which_utmt

    candidates = [
        core_dir / "UndertaleModCli.exe",
        core_dir / "UndertaleModCli" / "UndertaleModCli.exe",
        core_dir / "UTMT_CLI" / "UndertaleModCli.exe",
        patcher_dir / "UndertaleModCli.exe",
        patcher_dir / "tools" / "UndertaleModCli.exe"
    ]
    for c in candidates:
        if c.exists():
            return str(c.resolve())

    which_utmt = shutil.which("UndertaleModCli")
    if which_utmt:
        return which_utmt

    raise FileNotFoundError("UndertaleModCli.exe not found. Please set UTMT_CLI environment variable.")


def verify_environment():
    """Pre-flight check verifying required Python and Java runtimes before any processing."""
    if sys.version_info < (3, 8):
        LOGGER.error(f"Python 3.8 or higher is required. Current version: {sys.version.split()[0]}")
        raise RuntimeError("Outdated Python version.")

    java_bin = get_jdk_tool("java")
    java_ok = False
    if java_bin:
        try:
            res = subprocess.run([java_bin, "-version"], capture_output=True, stdin=subprocess.DEVNULL)
            if res.returncode == 0:
                java_ok = True
        except Exception:
            pass

    if not java_ok:
        print("\n" + "=" * 70)
        print(" [ERROR] Java Runtime (JRE / JDK) is required to sign Android APKs!")
        print("=" * 70)
        print("Java was not found on your system PATH. Android devices will refuse")
        print("to install unsigned APK packages.\n")
        print("Quick Solution (Choose one, free and takes 1 minute):")
        print("  1. Recommended (OpenJDK): https://adoptium.net/ (Temurin 17 or 21)")
        print("  2. Standard Java JRE     : https://www.java.com/")
        print("\nNote: During installation, ensure the 'Add to PATH' option is checked.")
        print("=" * 70 + "\n")
        raise RuntimeError("Java Runtime Environment (java) missing from system PATH.")


def get_jdk_tool(tool_name):
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    jdk_dirs = [
        Path(pf) / "Microsoft" / "jdk-11.0.16.101-hotspot" / "bin",
        Path(pf) / "Java" / "jdk-17" / "bin",
        Path(pf) / "Java" / "jdk-11" / "bin",
        Path(pf) / "Android" / "Android Studio" / "jbr" / "bin"
    ]
    for jd in jdk_dirs:
        p = jd / f"{tool_name}.exe"
        if p.exists():
            return str(p)
    found = shutil.which(tool_name)
    return found if found else tool_name


def find_uber_apk_signer():
    patcher_dir = ROOT_DIR
    core_dir = patcher_dir / "core"
    candidates = [
        core_dir / "uber-apk-signer.jar",
        patcher_dir / "uber-apk-signer.jar",
        patcher_dir / "tools" / "uber-apk-signer.jar"
    ]
    for c in candidates:
        if c.exists():
            return str(c.resolve())
    return None
