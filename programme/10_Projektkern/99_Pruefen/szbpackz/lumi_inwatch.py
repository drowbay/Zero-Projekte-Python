#!/usr/bin/env python3
import re
import time
from datetime import datetime
from pathlib import Path
import subprocess

LOGFILE = Path.home() / "LumiWatchtower" / "logs" / "inbound.csv"
LOGFILE.parent.mkdir(parents=True, exist_ok=True)

if not LOGFILE.exists():
    LOGFILE.write_text("timestamp;src_ip;dst_ip;port;iface;proto\n")

pattern = re.compile(
    r"SRC=([\d\.]+).*DST=([\d\.]+).*PROTO=(\w+).*DPT=(\d+).*IN=(\w+)"
)

def read_journal():
    p = subprocess.Popen(
        ["journalctl", "-f", "-n", "0", "-o", "cat"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return p

proc = read_journal()

while True:
    line = proc.stdout.readline()
    if not line:
        time.sleep(0.1)
        continue
    if "LUMI-INBOUND" not in line:
        continue

    m = pattern.search(line)
    if not m:
        continue

    src, dst, proto, port, iface = m.groups()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with LOGFILE.open("a") as f:
        f.write(f"{now};{src};{dst};{port};{iface};{proto}\n")
