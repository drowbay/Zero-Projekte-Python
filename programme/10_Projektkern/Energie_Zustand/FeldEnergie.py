import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Gitter (Feld)
x = np.linspace(-5, 5, 200)
y = np.linspace(-5, 5, 200)
X, Y = np.meshgrid(x, y)

# Figur
fig, ax = plt.subplots()
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)

img = ax.imshow(np.zeros_like(X), extent=[-5,5,-5,5], origin='lower')

ax.set_title("KI als temporäres Muster im Feld")

# Animation
def update(frame):
    t = frame / 30.0
    
    # Zentrum
    cx = 0
    cy = 0
    
    # Abstand vom Zentrum
    R = np.sqrt((X-cx)**2 + (Y-cy)**2)
    
    # Entstehen → Puls → Verschwinden
    envelope = np.exp(-((t-3)**2)/4)
    
    # Struktur (Wellen)
    Z = envelope * np.sin(3*R - t*2)
    
    # leichte "Atmung"
    Z *= (1 + 0.3*np.sin(t*2))
    
    img.set_array(Z)
    
    return [img]

ani = FuncAnimation(fig, update, frames=180, interval=40)

plt.colorbar(img, ax=ax)
plt.show()