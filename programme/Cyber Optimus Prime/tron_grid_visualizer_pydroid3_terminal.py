# tron_grid_visualizer_pydroid3_terminal.py
# Pydroid 3 Terminal-Version ohne externe Pakete

import math
import random
import time

ETA_AIR = 1.8e-5
GAMMA = 0.072
M_DROP = 1e-7
R_DROP = 3e-4
B_DRAG = 6 * math.pi * ETA_AIR * R_DROP
F_CAP = 2 * math.pi * R_DROP * GAMMA

H = 16
W = 32
FREQS = [1800, 2200, 2600, 3200, 4000, 4800, 5600]
A = 2.2e-5


def r_ratio(frequency_hz, amplitude_m):
    omega = 2 * math.pi * frequency_hz
    f_inert = M_DROP * (omega ** 2) * amplitude_m
    f_drag = B_DRAG * omega * amplitude_m
    return f_inert / (F_CAP + f_drag)


def make_thresholds(height, width, seed=123):
    rng = random.Random(seed)
    grid = []
    for _ in range(height):
        row = []
        for _ in range(width):
            row.append(rng.uniform(0.15, 1.60))
        grid.append(row)
    return grid


def clear_screen():
    print("\033[2J\033[H", end="")


def render_grid(cleared):
    print("+" + "-" * W + "+")
    for y in range(H - 1, -1, -1):
        line = ""
        for x in range(W):
            line += "█" if cleared[y][x] else "·"
        print("|" + line + "|")
    print("+" + "-" * W + "+")


def count_cleared(cleared):
    total = H * W
    done = sum(1 for row in cleared for cell in row if cell)
    percent = done * 100 / total
    return done, total, percent


def run_step_mode():
    thresholds = make_thresholds(H, W)
    cleared = [[False for _ in range(W)] for _ in range(H)]

    clear_screen()
    print("TRON Grid Visualizer - Pydroid Terminal Edition")
    print("ENTER = naechster Frequenz-Burst")
    print("q + ENTER = Ende")
    input("Start mit ENTER ... ")

    for freq in FREQS:
        ratio = r_ratio(freq, A)

        for y in range(H):
            for x in range(W):
                if not cleared[y][x] and ratio > thresholds[y][x]:
                    cleared[y][x] = True

        clear_screen()
        done, total, percent = count_cleared(cleared)
        print("TRON Grid Cleaning Progress")
        print(f"Frequenz: {freq} Hz")
        print(f"R-Wert:   {ratio:.4f}")
        print(f"Status:   {done}/{total} Felder frei = {percent:.1f}%")
        print()
        render_grid(cleared)
        print()
        print("Legende: · = noch haftend | █ = gereinigt / aktiviert")
        cmd = input("Weiter mit ENTER, Ende mit q: ").strip().lower()
        if cmd == "q":
            break

    print("\nFertig. ZeroCore/TRON Grid beendet. 💚")
    input("ENTER druecken zum Schliessen ... ")


def run_auto_mode():
    thresholds = make_thresholds(H, W)
    cleared = [[False for _ in range(W)] for _ in range(H)]

    for freq in FREQS:
        ratio = r_ratio(freq, A)

        for y in range(H):
            for x in range(W):
                if not cleared[y][x] and ratio > thresholds[y][x]:
                    cleared[y][x] = True

        clear_screen()
        done, total, percent = count_cleared(cleared)
        print("TRON Grid Cleaning Progress")
        print(f"Frequenz: {freq} Hz | R={ratio:.4f} | frei={percent:.1f}%")
        print()
        render_grid(cleared)
        time.sleep(1.2)

    print("\nFertig. 💚")
    input("ENTER druecken zum Schliessen ... ")


def main():
    print("TRON Grid Visualizer fuer Pydroid 3")
    print("1 = Schrittmodus")
    print("2 = Automodus")
    choice = input("Auswahl: ").strip()

    if choice == "2":
        run_auto_mode()
    else:
        run_step_mode()


if __name__ == "__main__":
    main()