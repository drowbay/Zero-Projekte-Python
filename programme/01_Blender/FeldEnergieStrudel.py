import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Gitter
x = np.linspace(-6, 6, 300)
y = np.linspace(-6, 6, 300)
X, Y = np.meshgrid(x, y)

fig, ax = plt.subplots()
ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)

img = ax.imshow(np.zeros_like(X),
                extent=[-6,6,-6,6],
                origin='lower',
                cmap='plasma')

ax.set_title("Zustands-Wurmloch (Zeit als Fluss)")

def update(frame):
    t = frame / 15.0  # Zeitraffer
    
    # Polarkoordinaten
    R = np.sqrt(X**2 + Y**2)
    Theta = np.arctan2(Y, X)
    
    # Wurmloch-Struktur
    spiral = Theta + 2*np.log(R + 1)
    
    # Zustand
    Z = np.sin(3*spiral - t*2)
    
    # Zentrum verstärken (Tunnel-Effekt)
    tunnel = np.exp(-R/2)
    
    # Pulsierende Zeit
    pulse = 1 + 0.4*np.sin(t*2)
    
    Z = Z * tunnel * pulse
    
    img.set_array(Z)
    return [img]

ani = FuncAnimation(fig, update, frames=200, interval=40)

plt.colorbar(img, ax=ax)
plt.show()