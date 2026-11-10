import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Raumgitter
x = np.linspace(-6, 6, 200)
y = np.linspace(-6, 6, 200)
X, Y = np.meshgrid(x, y)

fig, ax = plt.subplots()
ax.set_xlim(-6, 6)
ax.set_ylim(-6, 6)

img = ax.imshow(np.zeros_like(X),
                extent=[-6,6,-6,6],
                origin='lower',
                cmap='plasma')

ax.set_title("Zustands-Zeitraffer (15 Sekunden Realität)")

def update(frame):
    t = frame / 10.0  # Zeit skaliert
    
    # mehrere Quellen = komplexere Realität
    R1 = np.sqrt((X+2)**2 + (Y+1)**2)
    R2 = np.sqrt((X-2)**2 + (Y-1)**2)
    
    # Zustandsfunktion
    Z = (
        np.sin(2*R1 - t*2) +
        np.cos(2*R2 + t*1.5)
    )
    
    # sanftes Ausklingen / Entstehen
    envelope = np.exp(-((t-7)**2)/20)
    Z *= envelope
    
    img.set_array(Z)
    return [img]

ani = FuncAnimation(fig, update, frames=150, interval=100)

plt.colorbar(img, ax=ax)
plt.show()