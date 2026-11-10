import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# BLOCH-WASSERFALL / KORRELATIONS-SPEKTROGRAMM
# ------------------------------------------------------------
# Didaktische Visualisierung:
# - zwei lokale Bloch-Zustände
# - goldene Bloch-Schwebung als Korrelationsband
# - Wasserfallkarte als Frequenz-Zeit-Darstellung
#
# Keine neue Naturkraft:
# Das ist eine Visualisierung von zeitabhängigen Korrelationen.
# ============================================================

# ----------------------------
# Grundeinstellungen
# ----------------------------
np.random.seed(7)

frames = 360
interval = 40

# Bloch-Positionen
A_center = np.array([-2.2, 0.0])
B_center = np.array([2.2, 0.0])
R = 0.85

# Frequenz-Achse für Wasserfall
n_freq = 240
n_time = 150

f_min = 0.0
f_max = 1.0
freqs = np.linspace(f_min, f_max, n_freq)

# Zentrum der "Korrelationsfrequenz"
f0 = 0.52

# Frequenzbreite des Peaks
sigma_f = 0.035

# Speicher für Wasserfall
waterfall = np.zeros((n_time, n_freq))

# Welle zwischen den Bloch-Kreisen
x_wave = np.linspace(A_center[0] + R, B_center[0] - R, 500)

# ----------------------------
# Figur
# ----------------------------
fig = plt.figure(figsize=(10, 7))
fig.patch.set_facecolor("black")

gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.25], hspace=0.18)

ax_top = fig.add_subplot(gs[0])
ax_spec = fig.add_subplot(gs[1])

for ax in [ax_top, ax_spec]:
    ax.set_facecolor("black")

# ----------------------------
# Oberes Bild: Bloch-Schwebung
# ----------------------------
ax_top.set_xlim(-4, 4)
ax_top.set_ylim(-1.55, 1.55)
ax_top.set_aspect("equal")
ax_top.axis("off")

def draw_bloch(ax, center, color, label):
    theta = np.linspace(0, 2 * np.pi, 300)

    # Außenkreis
    ax.plot(
        center[0] + R * np.cos(theta),
        center[1] + R * np.sin(theta),
        color=color,
        lw=2
    )

    # Äquator
    ax.plot(
        center[0] + R * np.cos(theta),
        center[1] + 0.28 * R * np.sin(theta),
        color=color,
        lw=1,
        alpha=0.55,
        linestyle="--"
    )

    # Achsen
    ax.plot(
        [center[0], center[0]],
        [center[1] - R, center[1] + R],
        color=color,
        lw=1,
        alpha=0.45
    )
    ax.plot(
        [center[0] - R, center[0] + R],
        [center[1], center[1]],
        color=color,
        lw=1,
        alpha=0.25
    )

    ax.text(center[0], center[1] + R + 0.14, "|0⟩", color="white",
            ha="center", va="bottom", fontsize=11)
    ax.text(center[0], center[1] - R - 0.16, "|1⟩", color="white",
            ha="center", va="top", fontsize=11)

    ax.text(center[0], center[1] + 1.25, label, color=color,
            ha="center", fontsize=14, weight="bold")

draw_bloch(ax_top, A_center, "cyan", "Qubit A")
draw_bloch(ax_top, B_center, "magenta", "Qubit B")

# Bloch-Vektoren
vecA, = ax_top.plot([], [], color="cyan", lw=3)
dotA, = ax_top.plot([], [], "o", color="cyan", markersize=7)

vecB, = ax_top.plot([], [], color="magenta", lw=3)
dotB, = ax_top.plot([], [], "o", color="magenta", markersize=7)

# Schwebungsband
band, = ax_top.plot([], [], color="gold", lw=3)
band_glow, = ax_top.plot([], [], color="orange", lw=10, alpha=0.12)

# Text
ax_top.text(
    0, 1.42,
    "Bloch-Wasserfall: Zustand → Korrelation → Schwebung → Spektrum",
    color="white",
    ha="center",
    fontsize=14,
    weight="bold"
)

formula = ax_top.text(
    0, -1.38,
    r"$B_{\mathrm{vis}}(t)=C(t)\cos(\Delta\omega t+\Delta\phi)$",
    color="gold",
    ha="center",
    fontsize=13
)

info = ax_top.text(
    0, -1.15,
    "",
    color="white",
    ha="center",
    fontsize=10
)

# ----------------------------
# Unteres Bild: Wasserfall
# ----------------------------
extent = [f_min, f_max, 0, n_time]

img = ax_spec.imshow(
    waterfall,
    origin="lower",
    aspect="auto",
    extent=extent,
    cmap="turbo",
    vmin=0,
    vmax=1.2
)

ax_spec.set_title(
    "Korrelations-Spektrogramm / Bloch-Wasserfall",
    color="white",
    fontsize=13,
    pad=10
)

ax_spec.set_xlabel("Frequenz / Modenachse  f", color="white")
ax_spec.set_ylabel("Zeitverlauf", color="white")

ax_spec.tick_params(colors="white")

for spine in ax_spec.spines.values():
    spine.set_color("white")
    spine.set_alpha(0.25)

# Aktuelle Frequenzlinie
freq_marker = ax_spec.axvline(f0, color="white", lw=1.2, alpha=0.75)

# ----------------------------
# Hilfsfunktionen
# ----------------------------
def gaussian(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)

def normalize(x):
    x = x - np.min(x)
    return x / (np.max(x) + 1e-9)

# ----------------------------
# Animation
# ----------------------------
def update(frame):
    global waterfall

    t = frame / 25.0

    # --------------------------------
    # Simulierte "Verschränkungsstärke"
    # --------------------------------
    # C(t) zwischen ungefähr 0 und 1
    C = 0.55 + 0.35 * np.sin(0.37 * t)
    C = np.clip(C, 0.0, 1.0)

    # Schwebungsparameter
    delta_omega = 2.0 * np.pi * (0.18 + 0.03 * np.sin(0.11 * t))
    delta_phi = 0.6 * np.sin(0.09 * t)

    B_vis = C * np.cos(delta_omega * t + delta_phi)

    # --------------------------------
    # Bloch-Vektoren bewegen
    # --------------------------------
    angle_A = 0.7 + 0.8 * np.sin(0.23 * t)
    angle_B = 2.3 + 0.8 * np.cos(0.21 * t)

    len_A = 0.45 + 0.35 * (0.5 + 0.5 * np.cos(0.31 * t))
    len_B = 0.45 + 0.35 * (0.5 + 0.5 * np.sin(0.29 * t))

    Ax = A_center[0] + len_A * np.cos(angle_A)
    Ay = A_center[1] + len_A * np.sin(angle_A)

    Bx = B_center[0] + len_B * np.cos(angle_B)
    By = B_center[1] + len_B * np.sin(angle_B)

    vecA.set_data([A_center[0], Ax], [A_center[1], Ay])
    dotA.set_data([Ax], [Ay])

    vecB.set_data([B_center[0], Bx], [B_center[1], By])
    dotB.set_data([Bx], [By])

    # --------------------------------
    # Goldene Schwebungswelle
    # --------------------------------
    carrier = np.sin(13.0 * x_wave - 4.5 * t)
    envelope = np.cos(delta_omega * t + delta_phi)

    y_wave = 0.32 * C * envelope * carrier

    band.set_data(x_wave, y_wave)
    band_glow.set_data(x_wave, y_wave)

    strength = abs(B_vis)
    band.set_alpha(0.25 + 0.75 * strength)
    band_glow.set_alpha(0.06 + 0.24 * strength)

    info.set_text(
        f"C(t) = {C:.2f}   |   B_vis(t) = {B_vis:.2f}   |   Δω = {delta_omega:.2f}"
    )

    # --------------------------------
    # Wasserfall-Spektrum bauen
    # --------------------------------
    # Bewegliches Zentrum wie Drift im Spektrum
    center = f0 + 0.035 * np.sin(0.08 * t)

    # Hauptpeak
    peak_main = gaussian(freqs, center, sigma_f)

    # Seitenbänder durch Schwebung
    side_dist = 0.075 + 0.015 * np.sin(0.19 * t)
    peak_left = 0.45 * gaussian(freqs, center - side_dist, sigma_f * 1.25)
    peak_right = 0.45 * gaussian(freqs, center + side_dist, sigma_f * 1.25)

    # Feine Modulationslinien
    ripple = 0.12 * (np.sin(80 * freqs + 1.8 * t) ** 2)

    # Rauschen / Hintergrund
    noise = 0.035 * np.random.rand(n_freq)

    # Intensität: stark gekoppelt = gelber/heller
    row = (
        (0.25 + 0.95 * strength) * peak_main
        + (0.15 + 0.55 * C) * (peak_left + peak_right)
        + ripple * strength
        + noise
    )

    row = normalize(row)

    # Alte Zeilen nach unten schieben, neue oben einfügen
    waterfall = np.roll(waterfall, -1, axis=0)
    waterfall[-1, :] = row

    img.set_data(waterfall)

    # Frequenzmarker aktualisieren
    freq_marker.set_xdata([center, center])

    return (
        vecA, dotA, vecB, dotB,
        band, band_glow,
        img, freq_marker, info
    )

ani = FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=interval,
    blit=False
)

plt.show()