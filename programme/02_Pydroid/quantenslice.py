import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# -----------------------------
# PARAMETER
# -----------------------------
size = 30
dt = 0.1

# Drift
vx, vy = 0.6, 0.2

# Diffusion
D = 0.2

# Kopplung
k = 0.5

# -----------------------------
# 3D GRID (für dein Modell)
# -----------------------------
x, y, z = np.meshgrid(
    np.arange(10),
    np.arange(10),
    np.arange(10),
    indexing='ij'
)

x = x.astype(float)
y = y.astype(float)
z = z.astype(float)

# -----------------------------
# FELDER (Heatmaps)
# -----------------------------
psi1 = np.zeros((size, size))
psi2 = np.zeros((size, size))

psi1[size//3, size//2] = 5
psi2[2*size//3, size//2] = 5

# 4 Teilchen
psiA = np.zeros((size, size))
psiB = np.zeros((size, size))
psiC = np.zeros((size, size))
psiD = np.zeros((size, size))

psiA[10, 10] = 5
psiB[20, 10] = 5
psiC[10, 20] = 5
psiD[20, 20] = 5

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
    gx = (np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1)) / 2
    gy = (np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0)) / 2
    return gx, gy

# -----------------------------
# FIGURE
# -----------------------------
fig = plt.figure(figsize=(15,5))

ax3d = fig.add_subplot(131, projection='3d')
ax2 = fig.add_subplot(132)
ax4 = fig.add_subplot(133)

im2 = ax2.imshow(psi1 + psi2, cmap='plasma')
im4 = ax4.imshow(psiA + psiB + psiC + psiD, cmap='inferno')

ax2.set_title("2 Teilchen Kommunikation")
ax4.set_title("4 Teilchen Netzwerk")

# -----------------------------
# UPDATE
# -----------------------------
def update(frame):
    global x, y, z
    global psi1, psi2, psiA, psiB, psiC, psiD

    # -------- 3D DRIFT --------
    x += vx * dt
    y += vy * dt

    x %= 10
    y %= 10

    ax3d.clear()
    ax3d.scatter(x.flatten(), y.flatten(), z.flatten(),
                 color='olive', alpha=0.6, s=8)

    ax3d.set_title("Cosmic Drift Grid")

    # -------- 2 TEILCHEN --------
    lap1 = D * laplacian(psi1)
    lap2 = D * laplacian(psi2)

    gx1, gy1 = gradient(psi1)
    gx2, gy2 = gradient(psi2)

    drift1 = -(vx * gx1 + vy * gy1)
    drift2 = -(vx * gx2 + vy * gy2)

    coupling = k * (psi2 - psi1)

    psi1 += dt * (lap1 + drift1 + coupling)
    psi2 += dt * (lap2 + drift2 - coupling)

    im2.set_array(psi1 + psi2)

    # -------- 4 TEILCHEN --------
    fields = [psiA, psiB, psiC, psiD]

    new_fields = []
    for i, f in enumerate(fields):

        lap = D * laplacian(f)
        gx, gy = gradient(f)
        drift = -(vx * gx + vy * gy)

        # Kopplung mit Nachbarn
        coupling = 0
        for j, other in enumerate(fields):
            if i != j:
                coupling += k * (other - f)

        new_f = f + dt * (lap + drift + 0.25 * coupling)
        new_fields.append(new_f)

    psiA, psiB, psiC, psiD = new_fields

    im4.set_array(psiA + psiB + psiC + psiD)

    return [im2, im4]

# -----------------------------
# START
# -----------------------------
ani = animation.FuncAnimation(fig, update, frames=200, interval=60)

plt.tight_layout()
plt.show()