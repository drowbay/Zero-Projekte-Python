import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Grid
size = 200
x = np.linspace(-10, 10, size)
y = np.linspace(-10, 10, size)
X, Y = np.meshgrid(x, y)

# Quellen
source1 = (-3, 0)
source2 = (3, 0)

def wave(x0, y0, t):
    r = np.sqrt((X - x0)**2 + (Y - y0)**2)
    return np.sin(2 * np.pi * (r - t)) / (r + 0.5)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,5))

def update(frame):
    t = frame * 0.1

    Z1 = wave(*source1, t)
    Z2 = wave(*source2, t)
    Z = Z1 + Z2

    # leichte Dämpfung für "Auflösung"
    damping = np.exp(-0.05 * (X**2))
    Z_damped = Z * damping

    # --- LEFT: SIDE VIEW (klassisch) ---
    ax1.clear()
    mid_line = Z[size//2]  # Schnitt durch Mitte
    ax1.plot(x, mid_line, color='cyan')
    ax1.set_title("Seitenansicht (klassisch)")
    ax1.set_ylim(-2, 2)

    # --- RIGHT: TOP VIEW (dein Modell) ---
    ax2.clear()
    ax2.imshow(Z_damped, extent=(-10,10,-10,10),
               cmap='plasma', vmin=-2, vmax=2)
    ax2.set_title("Draufsicht (Interferenz + Auflösung)")

ani = animation.FuncAnimation(fig, update, frames=200, interval=50)
plt.tight_layout()
plt.show()