"""wbp.common"""
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

# Folder that contains WB_Mobile_Patcher.py, core/, input/ and output/
ROOT_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# PROGRESS BAR FEEDBACK
# -----------------------------------------------------------------------------
_last_progress = {}


def print_progress(current, total, prefix="Packaging APK", bar_length=30):
    """One-line progress bar. Redraws only when the whole percentage changes (thousands of small steps
    would otherwise slow the console down) and always at the start and the end."""
    percent = float(current) / max(1, total)
    shown = int(percent * 100)
    if current < total and current > 1 and _last_progress.get(prefix) == shown:
        return
    _last_progress[prefix] = shown
    arrow = "=" * max(0, int(round(percent * bar_length)) - 1) + ">" if percent > 0 else ""
    spaces = " " * (bar_length - len(arrow))
    sys.stdout.write(f"\r[*] {prefix}: [{arrow}{spaces}] {int(percent * 100)}% ({current}/{total})")
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")


class Spinner:
    """Animated "working" line for steps whose progress cannot be measured (external tools):

        with Spinner("Compiling mobile engine"):
            subprocess.run(...)

    Shows a moving bar and the elapsed seconds; prints one final line with the duration."""
    FRAMES = "|/-\\"

    def __init__(self, label, width=24):
        self.label, self.width = label, width
        self._stop = None
        self._thread = None
        self._start = 0.0

    def __enter__(self):
        import threading, time
        self._start = time.time()
        self._stop = threading.Event()
        interactive = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

        def run():
            i = 0
            while not self._stop.wait(0.15):
                if not interactive:
                    continue
                pos = i % (2 * self.width - 2)
                pos = pos if pos < self.width else 2 * self.width - 2 - pos
                bar = " " * pos + "###" + " " * max(0, self.width - pos - 1)
                sys.stdout.write(f"\r[{self.FRAMES[i % 4]}] {self.label}: [{bar[:self.width + 2]}] {time.time() - self._start:5.0f}s ")
                sys.stdout.flush()
                i += 1

        if not interactive:
            print(f"[*] {self.label} ...")
        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        import time
        self._stop.set()
        self._thread.join(timeout=1)
        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            sys.stdout.write("\r" + " " * (len(self.label) + self.width + 24) + "\r")
        status = "failed" if exc_type else "done"
        print(f"[*] {self.label}: {status} in {time.time() - self._start:.0f}s")
        return False


# -----------------------------------------------------------------------------
# LOGGING & ERROR REPORTING SYSTEM
# -----------------------------------------------------------------------------
class ExecutionLogger:
    def __init__(self):
        self.logs = []
        self.log_dir = ROOT_DIR

    def log(self, msg, prefix="[*]"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"{prefix} [{timestamp}] {msg}"
        print(formatted)
        self.logs.append(formatted)

    def error(self, msg):
        self.log(msg, prefix="[ERROR]")

    def progress(self, prefix, current, total):
        print_progress(current, total, prefix=prefix)

    def write_error_report(self, exc, stage="Unknown"):
        err_file = self.log_dir / "patch_overlay_latest_error.log"
        with open(err_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("           WB_Mobile_Patcher Failure Diagnosis\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Failed Stage: {stage}\n")
            f.write(f"Exception Type: {type(exc).__name__}\n")
            f.write(f"Exception Message: {str(exc)}\n")
            if isinstance(exc, PermissionError):
                f.write("Hint: Windows refused to open a file for writing. Another program has it open: the previous APK in output/\n"
                        "      (phone sync, MEGA upload, Explorer preview pane, antivirus scan, an installer) or the folder is read-only.\n"
                        "      Close or pause that program and run again. Builds normally pick a new file name when the old APK is locked.\n")
            f.write("\n")
            f.write("-" * 60 + "\n")
            f.write("Python Traceback:\n")
            f.write("-" * 60 + "\n")
            f.write(traceback.format_exc() + "\n\n")
            f.write("-" * 60 + "\n")
            f.write("Execution Log Trail:\n")
            f.write("-" * 60 + "\n")
            for line in self.logs:
                f.write(line + "\n")
        print(f"\n[!] A detailed diagnosis report was saved to: {err_file.name}")


LOGGER = ExecutionLogger()


# GML code that the patchers insert or look for lives in core/gml_patches/<function>/<name>.gml
# (one file per string, read byte-exact). gml("<function>/<name>") returns the text.
_GML_PATCH_DIR = ROOT_DIR / "core" / "gml_patches"


def gml(key):
    with open(_GML_PATCH_DIR / (key + ".gml"), "r", encoding="utf-8", newline="") as f:
        return f.read()


# Anchors a patch looked for and did not find in the current game build. Patches that
# match nothing used to be skipped silently; guarded_replace() records each miss so the
# build can report it (see PATCH_MISSES summary in patch_game_apk).
PATCH_MISSES = []


def guarded_replace(code, old, new, label, count=1, optional=False):
    """Replace `old` with `new` in `code` (first `count` hits, -1 = all). If `old` is not
    found the code is returned unchanged and `label` is recorded in PATCH_MISSES, unless
    `optional` is set (used where an earlier patch in the same run normally rewrites the anchor)."""
    if old in code:
        return code.replace(old, new, count)
    if not optional:
        PATCH_MISSES.append(label)
    return code


def unlink_with_retry(path, tries=4, delay=1.0):
    """Delete `path`, retrying briefly. Windows refuses to delete a file another program has open, and sync tools
    (MEGA), Explorer previews and virus scanners hold a freshly written APK for a few seconds.
    Returns True when the file is gone, False when it is still locked."""
    import time
    path = Path(path)
    for attempt in range(max(1, tries)):
        try:
            path.unlink()
            return True
        except FileNotFoundError:
            return True
        except OSError:
            if attempt + 1 < tries:
                time.sleep(delay)
    return not path.exists()
