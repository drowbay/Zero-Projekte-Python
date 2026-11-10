import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# -----------------------------
# PARAMETER (dein Universum)
# -----------------------------
size = 50          # Gittergröße
D = 0.2            # Diffusion (Nachbarn-Austausch)
vx, vy = 0.5, 0.0  # Drift-Richtung (dein Fluss!)
dt = 0.1           # Zeitschritt

# -----------------------------
# INITIALZUSTAND (ψ Feld)
# -----------------------------
psi = np.zeros((size, size))

# Start: kleine "Quelle"
psi[size//2, size//2] = 10

# -----------------------------
# HILFSFUNKTIONEN
# -----------------------------
def laplacian(field):
    return (
        np.roll(field, 1, axis=0) +
        np.roll(field, -1, axis=0) +
        np.roll(field, 1, axis=1) +
        np.roll(field, -1, axis=1) -
        4 * field
    )

def gradient(field):
    grad_x = (np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1)) / 2
    grad_y = (np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0)) / 2
    return grad_x, grad_y

# -----------------------------
# UPDATE REGEL (DEIN MODELL)
# -----------------------------
def update(frame):
    global psi

    # Diffusion (Nachbarn)
    diff = D * laplacian(psi)

    # Drift (dein "Fluss")
    grad_x, grad_y = gradient(psi)
    drift = -(vx * grad_x + vy * grad_y)

    # Update Gleichung
    psi += dt * (diff + drift)

    # Visualisierung
    im.set_array(psi)
    return [im]

# -----------------------------
# VISUALISIERUNG
# -----------------------------
fig, ax = plt.subplots()
im = ax.imshow(psi, cmap='plasma', interpolation='bilinear')
ax.set_title("Cosmic Drift Model (ψ Feld)")

ani = animation.FuncAnimation(fig, update, frames=200, interval=50)

plt.colorbar(im)
plt.show()