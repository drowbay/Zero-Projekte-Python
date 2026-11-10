#!/usr/bin/env python3
import subprocess
import time
from datetime import datetime
from pathlib import Path

LOG = Path.home() / "LumiWatchtower" / "logs" / "dnslog.csv"
LOG.parent.mkdir(parents=True, exist_ok=True)

if not LOG.exists():
    LOG.write_text("timestamp;domain;ip\n")

while True:
    p = subprocess.run(
        ["getprop", "net.dns1"],
        capture_output=True,
        text=True
    )
    dns = p.stdout.strip()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if dns:
        with LOG.open("a") as f:
            f.write(f"{now};resolver;{dns}\n")

    time.sleep(10)
