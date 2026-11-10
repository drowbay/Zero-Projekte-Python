#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimoXus Vitalscript — Bluetooth Dual-Audio Companion (Monitor + optional Heal)

What it does:
- Watches Bluetooth state and connected audio devices (best-effort parsing)
- Logs events to a file
- Sends Termux notifications (optional)
- Optional: soft-restart Bluetooth via 'su -c svc bluetooth disable/enable' (root)

Notes:
- Android/Samsung Dual Audio is not a public API toggle. This script focuses on stability + automation around it.
- Parsing dumpsys output varies by Android versions. Adjust regex if needed.
"""

import os
import re
import sys
import time
import subprocess
from datetime import datetime

# =======================
# CONFIG (edit me)
# =======================

TARGET_NAMES = [
    "SRS-XB20",   # your Sony
    "Xssive",     # adjust to exact BT name you see in phone settings
]

POLL_SECONDS = 8

LOG_PATH = os.path.expanduser("~/timoxus_bt_vitals.log")

# Safety first: start in monitor-only mode.
MONITOR_ONLY = True  # set False to allow healing actions

# Healing knobs (only used if MONITOR_ONLY == False)
ALLOW_BT_TOGGLE = True     # requires root for best results
TOGGLE_COOLDOWN = 120      # seconds between bluetooth toggles

# Notifications (Termux)
USE_TERMUX_NOTIFICATION = True  # requires 'pkg install termux-api' + Termux:API app

# Quick actions / deep links
OPEN_BT_SETTINGS_CMD = ["am", "start", "-a", "android.settings.BLUETOOTH_SETTINGS"]
OPEN_SOUND_SETTINGS_CMD = ["am", "start", "-a", "android.settings.SOUND_SETTINGS"]
# Media output picker deep link is inconsistent; BT settings is the reliable one.

# =======================
# Helpers
# =======================

last_toggle_ts = 0

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def run(cmd, as_root=False, timeout=10):
    """
    Run a shell command. If as_root=True, tries 'su -c'.
    Returns (rc, stdout, stderr).
    """
    if as_root:
        cmd = ["su", "-c", " ".join(cmd)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 999, "", str(e)

def log(line):
    line2 = f"[{now()}] {line}"
    print(line2)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line2 + "\n")
    except Exception:
        pass

def notify(title, content):
    if not USE_TERMUX_NOTIFICATION:
        return
    # termux-notification is best effort; if missing, we just skip.
    rc, out, err = run(["termux-notification", "--title", title, "--content", content], as_root=False)
    if rc != 0:
        # avoid spam in logs
        return

def get_bluetooth_state():
    """
    Best-effort: checks if bluetooth is ON via settings.
    """
    # settings get global bluetooth_on -> "1" or "0"
    rc, out, err = run(["settings", "get", "global", "bluetooth_on"], as_root=False)
    if rc == 0 and out in ("0", "1"):
        return out == "1"
    # fallback: dumpsys bluetooth_manager
    rc, out, err = run(["dumpsys", "bluetooth_manager"], as_root=False, timeout=15)
    if rc == 0 and out:
        # heuristic: look for "enabled: true" or "Bluetooth: ON"
        if re.search(r"enabled:\s*true", out, re.IGNORECASE) or re.search(r"\bON\b", out):
            return True
    return None  # unknown

def get_connected_devices():
    """
    Best-effort parse of dumpsys bluetooth_manager / bluetooth output.
    Returns a dict {name_or_addr: raw_line}
    """
    devices = {}

    # Try bluetooth_manager first
    rc, out, err = run(["dumpsys", "bluetooth_manager"], as_root=False, timeout=20)
    text = out if rc == 0 else ""

    # Some builds list "Connected devices:" sections; others not.
    # We'll just collect any lines that look like device entries.
    for line in text.splitlines():
        s = line.strip()
        # Heuristics: MAC address or "Device" lines
        if re.search(r"([0-9A-F]{2}:){5}[0-9A-F]{2}", s, re.IGNORECASE):
            devices[s] = s
        if "SRS" in s or "XB20" in s or "Xssive" in s:
            devices[s] = s

    # Fallback: dumpsys bluetooth (bigger)
    if not devices:
        rc, out, err = run(["dumpsys", "bluetooth"], as_root=False, timeout=25)
        if rc == 0:
            for line in out.splitlines():
                s = line.strip()
                if any(name.lower() in s.lower() for name in TARGET_NAMES):
                    devices[s] = s

    return devices

def targets_present(devices_dict):
    """
    Check whether our target names appear anywhere in collected device lines.
    """
    found = {name: False for name in TARGET_NAMES}
    blob = "\n".join(devices_dict.keys())
    for name in TARGET_NAMES:
        if re.search(re.escape(name), blob, re.IGNORECASE):
            found[name] = True
    return found

def soft_toggle_bluetooth():
    """
    Tries to toggle BT OFF/ON. Prefer root. Rate-limited by cooldown.
    """
    global last_toggle_ts
    if not ALLOW_BT_TOGGLE:
        return False, "BT toggle disabled in config"
    if time.time() - last_toggle_ts < TOGGLE_COOLDOWN:
        return False, "Cooldown active"

    # Try root toggle
    rc1, out1, err1 = run(["svc", "bluetooth", "disable"], as_root=True, timeout=10)
    time.sleep(2)
    rc2, out2, err2 = run(["svc", "bluetooth", "enable"], as_root=True, timeout=10)

    if rc1 == 0 and rc2 == 0:
        last_toggle_ts = time.time()
        return True, "Toggled Bluetooth via root svc"
    else:
        # Try non-root (may fail)
        rc1, out1, err1 = run(["svc", "bluetooth", "disable"], as_root=False, timeout=10)
        time.sleep(2)
        rc2, out2, err2 = run(["svc", "bluetooth", "enable"], as_root=False, timeout=10)
        if rc1 == 0 and rc2 == 0:
            last_toggle_ts = time.time()
            return True, "Toggled Bluetooth via svc (non-root)"
        return False, f"Toggle failed: {err1 or out1} | {err2 or out2}"

def open_bluetooth_settings():
    run(OPEN_BT_SETTINGS_CMD, as_root=False, timeout=5)

# =======================
# Main Loop
# =======================

def main():
    log("TimoXus Vitalscript started.")
    log(f"Targets: {TARGET_NAMES}")
    log(f"Monitor only: {MONITOR_ONLY}")
    notify("TimoXus", "Vitalscript started. Monitoring Bluetooth…")

    last_state = None
    last_found = None

    while True:
        bt_on = get_bluetooth_state()
        devices = get_connected_devices()
        found = targets_present(devices)

        # State change logs
        if bt_on != last_state:
            log(f"Bluetooth state: {bt_on}")
            last_state = bt_on

        if found != last_found:
            log(f"Targets present: {found}")
            last_found = found

        # Health logic
        missing = [name for name, ok in found.items() if not ok]
        if bt_on is False:
            msg = "Bluetooth is OFF. Open settings?"
            log(msg)
            notify("TimoXus", msg)

        elif missing:
            msg = f"Missing: {', '.join(missing)}"
            log(msg)
            notify("TimoXus", msg)

            if not MONITOR_ONLY:
                # Gentle heal: one soft toggle max every cooldown
                ok, info = soft_toggle_bluetooth()
                log(f"Heal attempt: {ok} — {info}")
                if ok:
                    notify("TimoXus", f"Heal: {info}")
                else:
                    # If heal not possible, at least open settings once in a while
                    pass

        # Optional: print quick snapshot occasionally
        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Stopped by user.")
        sys.exit(0)
