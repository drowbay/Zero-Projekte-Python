import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Physical base simplified
eta_air = 1.8e-5
gamma = 0.072
m_drop = 1e-7
r_drop = 3e-4
b_drag = 6*np.pi*eta_air*r_drop
F_cap = 2*np.pi*r_drop*gamma

def R_ratio(f, A):
    omega = 2*np.pi*f
    F_inert = m_drop*(omega**2)*A
    F_drag = b_drag*omega*A
    return F_inert/(F_cap+F_drag)

# TRON-grid parameters
rng = np.random.default_rng(123)
H, W = 32, 32
adhesion_factor = rng.uniform(0.9, 1.6, size=(H,W))
T = adhesion_factor * 1.0

freqs = [2200, 2600, 3200, 4000, 4800, 5600]
A = 1.0e-4

cleared = np.zeros((H,W), dtype=bool)
frames = []

for f in freqs:
    R = R_ratio(f, A)
    newly_cleared = (~cleared) & (R > T)
    cleared |= newly_cleared
    frames.append(cleared.copy())

# Create animation
fig, ax = plt.subplots(figsize=(5,5))
im = ax.imshow(frames[0], origin='lower', aspect='equal', cmap='Blues', vmin=0, vmax=1)
ax.set_title("TRON Grid Cleaning Progress")
ax.axis('off')

def update(i):
    im.set_data(frames[i])
    ax.set_title(f"TRON Grid after {freqs[i]} Hz burst")
    return [im]

ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=1200, blit=True)

# Save to mp4
ani.save("tron_grid_cleaning.mp4", writer="ffmpeg", dpi=150)
print("Animation saved as tron_grid_cleaning.mp4")
