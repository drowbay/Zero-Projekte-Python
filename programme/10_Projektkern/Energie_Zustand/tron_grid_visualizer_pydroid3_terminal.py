# tron_grid_visualizer_pydroid3_terminal.py
# Pydroid-3 sichere Terminal-Version: keine externen Bibliotheken, kein Grafikfenster.
# Zeigt den TRON-Grid-Fortschritt direkt in der Pydroid-Konsole.

import math
import random
import os
import time

ETA_AIR = 1.8e-5
GAMMA = 0.072
M_DROP = 1e-7
R_DROP = 3e-4
B_DRAG = 6 * math.pi * ETA_AIR * R_DROP
F_CAP = 2 * math.pi * R_DROP * GAMMA

HEIGHT = 16       # 16x32 passt besser aufs Handy-Display
WIDTH = 32
FREQS = [1600, 1900, 2200, 2600, 3200, 4000, 4800, 5600]
AMPLITUDE_M = 4.5e-6
SEED = 123


def clear_screen():
    # In Pydroid funktioniert clear nicht immer; der Fallback schiebt einfach nach unten.
    try:
        os.system("clear")
    except Exception:
        pass
    print("\n" * 3)


def r_ratio(freq_hz, amplitude_m):
    omega = 2 * math.pi * freq_hz
    f_inert = M_DROP * (omega ** 2) * amplitude_m
    f_drag = B_DRAG * omega * amplitude_m
    return f_inert / (F_CAP + f_drag)


def build_thresholds():
    random.seed(SEED)
    grid = []
    for _y in range(HEIGHT):
        row = []
        for _x in range(WIDTH):
            # etwas breiterer Bereich, damit Fortschritt sichtbar bleibt
            row.append(random.uniform(0.45, 2.2))
        grid.append(row)
    return grid


def percent(cleared):
    total = HEIGHT * WIDTH
    count = 0
    for row in cleared:
        for cell in row:
            if cell:
                count += 1
    return 100.0 * count / total


def draw_grid(cleared):
    # Unicode-Blöcke sehen in Pydroid meist gut aus.
    # Falls Kästchen kaputt aussehen, unten "ON" auf "#" ändern.
    ON = "█"
    OFF = "·"
    border = "+" + "-" * WIDTH + "+"
    print(border)
    for y in range(HEIGHT - 1, -1, -1):
        line = "|"
        for x in range(WIDTH):
            line += ON if cleared[y][x] else OFF
        line += "|"
        print(line)
    print(border)


def run_step_mode():
    thresholds = build_thresholds()
    cleared = [[False for _x in range(WIDTH)] for _y in range(HEIGHT)]

    print("TRON Grid Visualizer - Pydroid Terminal Edition")
    print("Keine Zusatzpakete. Kein weißes Grafikfenster. Nur Konsole. 💚")
    print()
    input("Drücke ENTER zum Starten...")

    for freq in FREQS:
        ratio = r_ratio(freq, AMPLITUDE_M)

        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (not cleared[y][x]) and ratio > thresholds[y][x]:
                    cleared[y][x] = True

        clear_screen()
        print("TRON GRID CLEANING")
        print(f"Frequenz: {freq} Hz")
        print(f"R-Wert:    {ratio:.3f}")
        print(f"Frei:      {percent(cleared):.1f}%")
        print()
        draw_grid(cleared)
        print()
        input("ENTER = nächster Burst...")

    print("Fertig. TRON Grid komplett durchlaufen. 🚀")
    input("ENTER = beenden...")


def run_auto_mode():
    thresholds = build_thresholds()
    cleared = [[False for _x in range(WIDTH)] for _y in range(HEIGHT)]

    for freq in FREQS:
        ratio = r_ratio(freq, AMPLITUDE_M)

        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (not cleared[y][x]) and ratio > thresholds[y][x]:
                    cleared[y][x] = True

        clear_screen()
        print("TRON GRID CLEANING - AUTO")
        print(f"Frequenz: {freq} Hz | R={ratio:.3f} | frei={percent(cleared):.1f}%")
        print()
        draw_grid(cleared)
        time.sleep(1.1)

    input("Fertig. ENTER = beenden...")


def main():
    print("TRON Grid Visualizer für Pydroid 3")
    print("1 = Schrittmodus, sicher")
    print("2 = Automodus")
    print()
    choice = input("Auswahl [1/2]: ").strip()

    if choice == "2":
        run_auto_mode()
    else:
        run_step_mode()


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print("FEHLER:", err)
        input("ENTER = beenden...")
