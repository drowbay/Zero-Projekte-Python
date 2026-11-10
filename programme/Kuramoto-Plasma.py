# ============================================================
# Zero-Lumÿè Kuramoto Plasma Visualizer
# ------------------------------------------------------------
# Kuramoto-Modell + Plasma-artige Darstellung
#
# Grundgleichung:
# dθ_i/dt = ω_i + (K/N) * Σ_j sin(θ_j - θ_i)
#
# θ_i  = Phase eines Plasma-Partikels / Oszillators
# ω_i  = Eigenfrequenz
# K    = Kopplungsstärke
# N    = Anzahl der Oszillatoren
#
# Visualisierung:
# - Partikel bewegen sich in einem "Plasmafeld"
# - Kuramoto-Phasen steuern Radius, Leuchten und Bewegung
# - Ordnungsparameter r zeigt Synchronisation:
#       r ≈ 0  -> ungeordnet
#       r ≈ 1  -> synchronisiert
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# -----------------------------
# Einstellungen
# -----------------------------
np.random.seed(7)

N = 260                 # Anzahl Plasma-Partikel
K = 1.8                 # Kopplungsstärke
dt = 0.035              # Zeitschritt
frames = 900            # Animationslänge

space_size = 8.0        # Darstellungsbereich
trail_alpha = 0.10      # Nachleuchten / Schweif-Effekt

# Anfangsphasen und Eigenfrequenzen
theta = np.random.uniform(0, 2 * np.pi, N)
omega = np.random.normal(0.0, 0.8, N)

# Grundpositionen im Raum
base_radius = np.random.uniform(1.0, space_size, N)
base_angle = np.random.uniform(0, 2 * np.pi, N)

# individuelle Bewegungsparameter
swirl_speed = np.random.normal(0.15, 0.05, N)
radial_amp = np.random.uniform(0.2, 1.4, N)
phase_offset = np.random.uniform(0, 2 * np.pi, N)


# -----------------------------
# Kuramoto-Schritt
# -----------------------------
def kuramoto_step(theta, omega, K, dt):
    N = len(theta)

    # Matrix aller Phasendifferenzen θ_j - θ_i
    phase_diff = theta[None, :] - theta[:, None]

    # Kopplung
    coupling = (K / N) * np.sum(np.sin(phase_diff), axis=1)

    # Ableitung
    dtheta = omega + coupling

    # Euler-Integration
    theta_new = theta + dtheta * dt
    theta_new = np.mod(theta_new, 2 * np.pi)

    return theta_new


# -----------------------------
# Ordnungsparameter
# -----------------------------
def order_parameter(theta):
    z = np.mean(np.exp(1j * theta))
    r = np.abs(z)
    psi = np.angle(z)
    return r, psi


# -----------------------------
# Positionen aus Phase erzeugen
# -----------------------------
def plasma_positions(theta, t, r_sync, psi):
    """
    Kuramoto-Phase wird in Plasma-Bewegung übersetzt.
    Je höher r_sync, desto stärker bündelt sich das System.
    """

    # rotierender Grundwinkel
    angle = base_angle + swirl_speed * t + 0.45 * np.sin(theta)

    # Plasma-Radius pulsiert mit Phase
    radius = base_radius + radial_amp * np.sin(theta + phase_offset)

    # Wenn Synchronisation steigt, zieht es die Partikel sanfter in gemeinsame Struktur
    sync_pull = 1.0 - 0.45 * r_sync
    radius = radius * sync_pull

    # zusätzliche Wellenstruktur
    wave = 0.35 * np.sin(3 * angle + theta + t * 0.04)

    x = (radius + wave) * np.cos(angle)
    y = (radius + wave) * np.sin(angle)

    # gemeinsame Synchronisationsrichtung als leichte Drift
    x += r_sync * 1.5 * np.cos(psi)
    y += r_sync * 1.5 * np.sin(psi)

    return x, y


# -----------------------------
# Plot vorbereiten
# -----------------------------
fig, ax = plt.subplots(figsize=(8, 8))

ax.set_facecolor("black")
fig.patch.set_facecolor("black")

ax.set_xlim(-space_size, space_size)
ax.set_ylim(-space_size, space_size)
ax.set_aspect("equal")
ax.axis("off")

title = ax.text(
    -7.7, 7.35,
    "Kuramoto-Plasma-Modell",
    color="white",
    fontsize=14,
    weight="bold"
)

info = ax.text(
    -7.7, 6.85,
    "",
    color="white",
    fontsize=10
)

# Hintergrund-Nachleuchten als transparente Scatter-Layer
x0, y0 = plasma_positions(theta, 0, 0, 0)

scatter = ax.scatter(
    x0, y0,
    s=22,
    c=theta,
    cmap="plasma",
    alpha=0.9
)

# Synchronisationsvektor
sync_line, = ax.plot([], [], color="white", linewidth=2, alpha=0.9)

# Zentrum
center = ax.scatter([0], [0], s=40, color="white", alpha=0.8)


# -----------------------------
# Animation
# -----------------------------
def update(frame):
    global theta

    theta = kuramoto_step(theta, omega, K, dt)

    r_sync, psi = order_parameter(theta)
    x, y = plasma_positions(theta, frame, r_sync, psi)

    # Partikel aktualisieren
    scatter.set_offsets(np.column_stack([x, y]))
    scatter.set_array(theta)

    # Größe pulsiert mit Phase und Synchronisation
    sizes = 12 + 34 * (0.5 + 0.5 * np.sin(theta)) * (0.6 + r_sync)
    scatter.set_sizes(sizes)

    # Synchronisationszeiger
    line_len = 2.6 * r_sync
    sync_line.set_data(
        [0, line_len * np.cos(psi)],
        [0, line_len * np.sin(psi)]
    )

    info.set_text(
        f"Kopplung K = {K:.2f}   |   Synchronisation r = {r_sync:.3f}\n"
        f"r ≈ 0: ungeordnet    r ≈ 1: synchron"
    )

    return scatter, sync_line, info


ani = FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=30,
    blit=True
)

plt.show()