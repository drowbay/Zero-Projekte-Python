# tron_grid_visualizer_pydroid3.py
# Pydroid 3 kompatible Version
# - kein ffmpeg-Zwang
# - speichert immer PNG-Bilder
# - versucht optional ein GIF zu speichern, falls Pillow installiert ist

import math
from pathlib import Path

import numpy as np

# Backend setzen, damit Speichern auch ohne normales Desktop-Fenster stabiler läuft.
# In Pydroid 3 funktioniert plt.show() je nach Installation unterschiedlich,
# aber savefig() ist deutlich robuster.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# -----------------------------
# Vereinfachte physikalische Basis
# -----------------------------
ETA_AIR = 1.8e-5       # dynamische Viskosität Luft [Pa*s]
GAMMA = 0.072          # Oberflächenspannung Wasser grob [N/m]
M_DROP = 1e-7          # Tropfenmasse [kg]
R_DROP = 3e-4          # Tropfenradius [m]

B_DRAG = 6 * math.pi * ETA_AIR * R_DROP
F_CAP = 2 * math.pi * R_DROP * GAMMA


def r_ratio(freq_hz: float, amplitude_m: float) -> float:
    """Berechnet das vereinfachte Verhältnis aus Trägheitskraft zu Halte-/Reibkraft."""
    omega = 2 * math.pi * freq_hz
    f_inert = M_DROP * (omega ** 2) * amplitude_m
    f_drag = B_DRAG * omega * amplitude_m
    return f_inert / (F_CAP + f_drag)


def build_frames(height=32, width=32, freqs=None, amplitude_m=1.0e-4, seed=123):
    """Erzeugt TRON-Grid-Zustände für mehrere Frequenz-Bursts."""
    if freqs is None:
        freqs = [2200, 2600, 3200, 4000, 4800, 5600]

    rng = np.random.default_rng(seed)
    adhesion_factor = rng.uniform(0.9, 1.6, size=(height, width))
    threshold = adhesion_factor

    cleared = np.zeros((height, width), dtype=bool)
    frames = []
    ratios = []

    for freq in freqs:
        ratio = r_ratio(freq, amplitude_m)
        newly_cleared = (~cleared) & (ratio > threshold)
        cleared |= newly_cleared
        frames.append(cleared.copy())
        ratios.append(ratio)

    return frames, freqs, ratios


def save_frame_sheet(frames, freqs, out_path: Path):
    """Speichert alle Frames als Übersicht in einer PNG-Datei."""
    cols = 3
    rows = math.ceil(len(frames) / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))
    axes = np.array(axes).reshape(-1)

    for i, ax in enumerate(axes):
        ax.axis("off")
        if i < len(frames):
            ax.imshow(frames[i], origin="lower", aspect="equal", cmap="Blues", vmin=0, vmax=1)
            percent = frames[i].mean() * 100
            ax.set_title(f"{freqs[i]} Hz | {percent:.1f}% frei")

    fig.suptitle("TRON Grid Cleaning Progress", fontsize=14)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def save_last_frame(frames, freqs, out_path: Path):
    """Speichert den letzten Zustand als PNG."""
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(frames[-1], origin="lower", aspect="equal", cmap="Blues", vmin=0, vmax=1)
    ax.set_title(f"TRON Grid final after {freqs[-1]} Hz")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def try_save_gif(frames, freqs, out_path: Path):
    """Versucht ein GIF zu speichern. Klappt nur, wenn Pillow installiert ist."""
    fig, ax = plt.subplots(figsize=(5, 5))
    image = ax.imshow(frames[0], origin="lower", aspect="equal", cmap="Blues", vmin=0, vmax=1)
    ax.axis("off")

    def update(i):
        image.set_data(frames[i])
        percent = frames[i].mean() * 100
        ax.set_title(f"{freqs[i]} Hz burst | {percent:.1f}% frei")
        return [image]

    anim = animation.FuncAnimation(fig, update, frames=len(frames), interval=900, blit=False)

    try:
        anim.save(out_path, writer="pillow", dpi=120)
        print(f"[OK] GIF gespeichert: {out_path}")
    except Exception as exc:
        print("[WARN] GIF konnte nicht gespeichert werden.")
        print("       In Pydroid 3 ggf. Pillow installieren oder nur PNG nutzen.")
        print(f"       Grund: {exc}")
    finally:
        plt.close(fig)


def main():
    output_dir = Path("tron_output")
    output_dir.mkdir(exist_ok=True)

    freqs = [2200, 2600, 3200, 4000, 4800, 5600]
    amplitude_m = 1.0e-4

    frames, freqs, ratios = build_frames(freqs=freqs, amplitude_m=amplitude_m)

    print("TRON Grid Visualizer - Pydroid 3 Edition")
    print("----------------------------------------")
    print(f"Frames: {len(frames)}")
    print(f"Grid:   {frames[0].shape[0]} x {frames[0].shape[1]}")
    print()

    for freq, ratio, frame in zip(freqs, ratios, frames):
        print(f"{freq:5d} Hz | R={ratio:.3f} | frei={frame.mean() * 100:.1f}%")

    sheet_path = output_dir / "tron_grid_cleaning_sheet.png"
    final_path = output_dir / "tron_grid_final.png"
    gif_path = output_dir / "tron_grid_cleaning.gif"

    save_frame_sheet(frames, freqs, sheet_path)
    save_last_frame(frames, freqs, final_path)
    try_save_gif(frames, freqs, gif_path)

    print()
    print(f"[OK] Übersicht gespeichert: {sheet_path}")
    print(f"[OK] Endbild gespeichert:   {final_path}")
    print("Fertig. In Pydroid findest du die Dateien im Projektordner/tron_output.")


if __name__ == "__main__":
    main()
