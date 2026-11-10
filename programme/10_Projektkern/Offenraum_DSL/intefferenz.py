import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Grid
size = 200
x = np.linspace(-10, 10, size)
y = np.linspace(-10, 10, size)
X, Y = np.meshgrid(x, y)

# zwei Quellen
source1 = (-3, 0)
source2 = (3, 0)

def wave(x0, y0, t):
    r = np.sqrt((X - x0)**2 + (Y - y0)**2)
    return np.sin(2 * np.pi * (r - t)) / (r + 0.5)

fig, ax = plt.subplots()

def update(frame):
    t = frame * 0.1

    Z1 = wave(*source1, t)
    Z2 = wave(*source2, t)

    # Überlagerung
    Z = Z1 + Z2

    # "Auflösung" simulieren (Dämpfung an Seiten)
    damping = np.exp(-0.05 * (X**2))
    Z *= damping

    ax.clear()
    ax.imshow(Z, extent=(-10,10,-10,10), cmap='plasma', vmin=-2, vmax=2)
    ax.set_title("Interferenz + Seitenauflösung")

ani = animation.FuncAnimation(fig, update, frames=200, interval=50)
plt.show()