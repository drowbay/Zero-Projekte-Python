#!/usr/bin/env python3
"""
qos_cli.py — einfacher CLI-Adapter für Q-OS × 737
Usage:
  python qos_cli.py --mirror --scale 737 --csv out.csv --png out.png
"""
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from qos.lc_core.lumi_compile import compile_quos_737

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmin", type=float, default=-10.0)
    ap.add_argument("--cmax", type=float, default=10.0)
    ap.add_argument("--steps", type=int, default=161)
    ap.add_argument("--mirror", action="store_true")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--csv", type=str, default=None)
    ap.add_argument("--png", type=str, default=None)
    args = ap.parse_args()

    c = np.linspace(args.cmin, args.cmax, args.steps)
    df = compile_quos_737(c, mirror=args.mirror, scale=args.scale)

    if args.csv:
        df.to_csv(args.csv, index=False)
        print(f"✔ CSV geschrieben: {args.csv}")

    if args.png:
        plt.figure(figsize=(16,9))
        plt.plot(df["c"], df["value"], label="value")
        plt.xlabel("c")
        plt.ylabel("value")
        plt.title("Q-OS × 737 — value vs c")
        plt.legend()
        plt.savefig(args.png, dpi=180, bbox_inches="tight")
        plt.close()
        print(f"✔ PNG gespeichert: {args.png}")

    if not (args.csv or args.png):
        print(df.head())

if __name__ == "__main__":
    main()
