import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Zeit
t_vals = np.linspace(0, 10, 200)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,5))

def update(frame):
    t = t_vals[frame]

    # Bloch-Kugel Parameter
    theta = np.pi/2 + 0.3*np.sin(t)   # Superposition
    phi = t                           # Phase

    # Bloch Vektor
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    # --- SIDE VIEW (θ) ---
    ax1.clear()
    ax1.plot([0, 0], [-1, 1], color='gray')  # Z-Achse
    ax1.scatter(0, z, color='cyan', s=100)
    ax1.set_xlim(-1,1)
    ax1.set_ylim(-1,1)
    ax1.set_title("Seitenansicht (Superposition θ)")
    ax1.set_aspect('equal')

    # --- TOP VIEW (φ) ---
    ax2.clear()
    ax2.add_patch(plt.Circle((0,0),1, fill=False, color='gray'))
    ax2.scatter(x, y, color='magenta', s=100)
    ax2.set_xlim(-1,1)
    ax2.set_ylim(-1,1)
    ax2.set_title("Draufsicht (Phase φ)")
    ax2.set_aspect('equal')

ani = animation.FuncAnimation(fig, update, frames=len(t_vals), interval=50)

plt.tight_layout()
plt.show()