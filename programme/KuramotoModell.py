# ============================================================
# Kuramoto-Modell - Original-Grundform
# ------------------------------------------------------------
# Modell:
#
# dθ_i/dt = ω_i + (K/N) * Σ_j sin(θ_j - θ_i)
#
# θ_i  = Phase des Oszillators i
# ω_i  = natürliche Eigenfrequenz
# K    = Kopplungsstärke
# N    = Anzahl der Oszillatoren
#
# Wenn K groß genug ist, synchronisieren sich die Oszillatoren.
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# -----------------------------
# Einstellungen
# -----------------------------
np.random.seed(42)

N = 80                  # Anzahl Oszillatoren
K = 2.0                 # Kopplungsstärke
dt = 0.03               # Zeitschritt
frames = 800            # Animationsframes

# Anfangsphasen zufällig zwischen 0 und 2π
theta = np.random.uniform(0, 2 * np.pi, N)

# Eigenfrequenzen: kleine Streuung um 0
omega = np.random.normal(0.0, 1.0, N)


# -----------------------------
# Kuramoto-Schritt
# -----------------------------
def kuramoto_step(theta, omega, K, dt):
    """
    Ein Integrationsschritt des Kuramoto-Modells.
    """

    N = len(theta)

    # Phasendifferenzen θ_j - θ_i
    phase_diff = theta[None, :] - theta[:, None]

    # Kopplungsterm
    coupling = (K / N) * np.sum(np.sin(phase_diff), axis=1)

    # Differentialgleichung:
    # dθ_i/dt = ω_i + Kopplung
    dtheta = omega + coupling

    # Euler-Integration
    theta_new = theta + dtheta * dt

    # Phasen im Bereich 0 bis 2π halten
    theta_new = np.mod(theta_new, 2 * np.pi)

    return theta_new


# -----------------------------
# Ordnungsparameter
# -----------------------------
def order_parameter(theta):
    """
    Misst die Synchronisation.

    r = 0 bedeutet: völlig ungeordnet
    r = 1 bedeutet: perfekt synchron
    """

    complex_mean = np.mean(np.exp(1j * theta))
    r = np.abs(complex_mean)
    psi = np.angle(complex_mean)

    return r, psi


# -----------------------------
# Plot vorbereiten
# -----------------------------
fig, ax = plt.subplots(figsize=(7, 7))

ax.set_aspect("equal")
ax.set_xlim(-1.4, 1.4)
ax.set_ylim(-1.4, 1.4)
ax.set_title("Kuramoto-Modell: gekoppelte Oszillatoren")

# Einheitskreis
circle = plt.Circle((0, 0), 1.0, fill=False, linewidth=1.5)
ax.add_patch(circle)

# Punkte auf dem Kreis
x = np.cos(theta)
y = np.sin(theta)

points = ax.scatter(x, y, s=45)

# Zeiger für mittlere Phase / Synchronisation
mean_line, = ax.plot([], [], linewidth=3)

# Textanzeige
text = ax.text(
    -1.3,
    1.25,
    "",
    fontsize=11
)


# -----------------------------
# Animation
# -----------------------------
def update(frame):
    global theta

    theta = kuramoto_step(theta, omega, K, dt)

    x = np.cos(theta)
    y = np.sin(theta)

    points.set_offsets(np.column_stack([x, y]))

    r, psi = order_parameter(theta)

    # Mittlerer Synchronisationszeiger
    mean_x = r * np.cos(psi)
    mean_y = r * np.sin(psi)

    mean_line.set_data([0, mean_x], [0, mean_y])

    text.set_text(
        f"Frame: {frame}\n"
        f"Kopplung K = {K}\n"
        f"Synchronisation r = {r:.3f}"
    )

    return points, mean_line, text


ani = FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=30,
    blit=True
)

plt.show()