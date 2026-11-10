#!/usr/bin/env python3
import re
import math

from modules.pi_tools import pi_value, parse_value, square
from modules.qubit import Qubit, shots

def help_text() -> str:
    return (
        "🌙 Lumÿè-OS v0.2 — π + Qubit + Offline-KI\n"
        "Commands:\n"
        "  help                      Hilfe\n"
        "  pi                        π anzeigen\n"
        "  square <x|pi|π>           Quadrat\n"
        "  calc <expr>               sichere Rechnung (pi/π ok)\n"
        "  qubit                     Qubit Status anzeigen\n"
        "  qubit set <theta> <phi>   Winkel setzen (rad)\n"
        "  measure <shots>           Messung simulieren\n"
        "  exit                      Beenden\n"
        "\n"
        "Beispiele:\n"
        "  calc (pi*2) / 3\n"
        "  qubit set 1.570796 0\n"
        "  measure 200\n"
    )

def safe_calc(expr: str) -> str:
    expr = expr.strip().lower().replace(",", ".")
    expr = expr.replace("π", "pi")
    expr = re.sub(r"\bpi\b", str(pi_value()), expr)

    # Only allow numbers, operators, spaces, parentheses, dots
    if not re.fullmatch(r"[0-9\.\+\-\*\/\(\) ]+", expr):
        return "❌ Nur Zahlen und + - * / ( ) erlaubt."

    try:
        val = eval(expr, {"__builtins__": {}}, {})
        return f"= {val}"
    except Exception as e:
        return f"❌ Fehler: {e}"

def banner():
    print("\n🌙 Lumÿè-OS / Zero Edition — v0.2")
    print("================================")
    print("Tippe 'help' für Befehle.\n")

def main():
    qb = Qubit(theta=0.0, phi=0.0)

    banner()
    while True:
        try:
            user = input("Du> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye 👋")
            break

        if not user:
            continue

        low = user.lower()

        if low in ("help", "h", "?"):
            print(help_text()); continue

        if low in ("exit", "quit", "q"):
            print("Bye 👋"); break

        if low in ("pi", "π"):
            print(f"π = {pi_value()}"); continue

        if low.startswith("square "):
            arg = user.split(" ", 1)[1]
            try:
                x = parse_value(arg)
                print(f"{x}² = {square(x)}")
            except Exception:
                print("❌ Usage: square <zahl|pi|π>")
            continue

        if low.startswith("calc "):
            expr = user.split(" ", 1)[1]
            print(safe_calc(expr))
            continue

        if low == "qubit":
            print(qb.summary()); continue

        if low.startswith("qubit set "):
            parts = user.split()
            if len(parts) != 4:
                print("❌ Usage: qubit set <theta> <phi>   (rad)")
                continue
            try:
                theta = float(parts[2].replace(",", "."))
                phi = float(parts[3].replace(",", "."))
                qb.set_angles(theta, phi)
                print("✅ gesetzt.")
                print(qb.summary())
            except Exception as e:
                print(f"❌ Fehler: {e}")
            continue

        if low.startswith("measure "):
            try:
                n = int(user.split(" ", 1)[1])
                print(shots(qb, n))
            except Exception:
                print("❌ Usage: measure <shots>")
            continue

        # Friendly offline-KI fallback
        if "müde" in low or "kaputt" in low or "stress" in low:
            print("💙 Okay, ganz ruhig. 1 Sache: Wasser. 1 Sache: 5 Atemzüge. Dann nächster Step.")
            continue

        print("🤖 Unbekannt. Tipp: help")

if __name__ == "__main__":
    main()
