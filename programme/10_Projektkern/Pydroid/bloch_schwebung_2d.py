import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# BLOCH-SCHWEBUNG 2D
# Didaktische Visualisierung:
# Lokale Bloch-Sphären + zeitabhängige Korrelations-Schwebung
# ============================================================

# ---------- Einstellungen ----------
C = 0.85                 # Verschränkungsstärke: 0 = keine, 1 = maximal
delta_f = 0.18           # Schwebungsfrequenz / Frequenzdifferenz
delta_phi = 0.0          # Phasenverschiebung
frames = 360             # Anzahl Frames
interval = 35            # ms pro Frame

# Bloch-Kreis-Positionen
A_center = np.array([-2.2, 0.0])
B_center = np.array([ 2.2, 0.0])
R = 1.0

# ---------- Plot vorbereiten ----------
fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor("black")
ax.set_facecolor("black")

ax.set_xlim(-4.2, 4.2)
ax.set_ylim(-1.8, 1.8)
ax.set_aspect("equal")
ax.axis("off")

# ---------- Hilfsfunktionen ----------
def draw_bloch_circle(center, label, color):
    theta = np.linspace(0, 2*np.pi, 300)

    # Außenkreis
    x = center[0] + R * np.cos(theta)
    y = center[1] + R * np.sin(theta)
    ax.plot(x, y, color=color, linewidth=2)

    # Äquator
    ax.plot(
        center[0] + R*np.cos(theta),
        center[1] + 0.28*R*np.sin(theta),
        color=color,
        linewidth=1,
        alpha=0.45,
        linestyle="--"
    )

    # Achsen
    ax.plot([center[0], center[0]], [center[1]-R, center[1]+R], color=color, alpha=0.6)
    ax.plot([center[0]-R, center[0]+R], [center[1], center[1]], color=color, alpha=0.35)

    # Labels
    ax.text(center[0], center[1]+1.18, "|0⟩", color="white", ha="center", fontsize=12)
    ax.text(center[0], center[1]-1.28, "|1⟩", color="white", ha="center", fontsize=12)
    ax.text(center[0], center[1]+1.45, label, color=color, ha="center", fontsize=14, weight="bold")


def bloch_vector(center, angle, length, color):
    x = center[0] + length * np.cos(angle)
    y = center[1] + length * np.sin(angle)

    line, = ax.plot([center[0], x], [center[1], y], color=color, linewidth=3)
    point, = ax.plot([x], [y], marker="o", color=color, markersize=7)

    return line, point


# ---------- Grundgrafik ----------
draw_bloch_circle(A_center, "Qubit A", "cyan")
draw_bloch_circle(B_center, "Qubit B", "magenta")

# Lokale Bloch-Vektoren
vecA_line, vecA_point = bloch_vector(A_center, np.pi/4, 0.8, "cyan")
vecB_line, vecB_point = bloch_vector(B_center, 3*np.pi/4, 0.8, "magenta")

# Verbindung / Schwebung
x_wave = np.linspace(A_center[0]+R, B_center[0]-R, 500)
wave_line, = ax.plot([], [], color="gold", linewidth=3)
wave_glow, = ax.plot([], [], color="orange", linewidth=8, alpha=0.18)

# Text
title = ax.text(
    0, 1.55,
    "Bloch-Schwebung: lokale Zustände + zeitabhängige Korrelation",
    color="white",
    ha="center",
    fontsize=14,
    weight="bold"
)

info_text = ax.text(
    0, -1.55,
    "",
    color="white",
    ha="center",
    fontsize=11
)

formula_text = ax.text(
    0, -1.32,
    r"$B_{vis}(t)=C\cos(\Delta\omega t+\Delta\phi)$",
    color="gold",
    ha="center",
    fontsize=13
)

# ---------- Animation ----------
def update(frame):
    t = frame / 25.0

    # Lokale Vektoren rotieren langsam
    angle_A = 0.8 + 0.55*np.sin(0.35*t)
    angle_B = 2.3 + 0.55*np.cos(0.35*t)

    len_A = 0.65 + 0.25*np.cos(0.25*t)
    len_B = 0.65 + 0.25*np.sin(0.25*t)

    Ax = A_center[0] + len_A*np.cos(angle_A)
    Ay = A_center[1] + len_A*np.sin(angle_A)

    Bx = B_center[0] + len_B*np.cos(angle_B)
    By = B_center[1] + len_B*np.sin(angle_B)

    vecA_line.set_data([A_center[0], Ax], [A_center[1], Ay])
    vecA_point.set_data([Ax], [Ay])

    vecB_line.set_data([B_center[0], Bx], [B_center[1], By])
    vecB_point.set_data([Bx], [By])

    # Schwebung: schnelle Welle mit langsamer Hüllkurve
    carrier = np.sin(12*x_wave - 4.0*t)
    envelope = np.cos(2*np.pi*delta_f*t + delta_phi)

    B_vis = C * envelope

    y_wave = 0.35 * B_vis * carrier

    wave_line.set_data(x_wave, y_wave)
    wave_glow.set_data(x_wave, y_wave)

    info_text.set_text(
        f"Verschränkungsstärke C = {C:.2f}   |   Schwebung Δf = {delta_f:.2f}   |   B_vis(t) = {B_vis:.2f}"
    )

    # Farbe/Transparenz abhängig von Stärke
    alpha = 0.25 + 0.75 * abs(B_vis)
    wave_line.set_alpha(alpha)
    wave_glow.set_alpha(0.08 + 0.25 * abs(B_vis))

    return vecA_line, vecA_point, vecB_line, vecB_point, wave_line, wave_glow, info_text


ani = FuncAnimation(fig, update, frames=frames, interval=interval, blit=False)

plt.show()