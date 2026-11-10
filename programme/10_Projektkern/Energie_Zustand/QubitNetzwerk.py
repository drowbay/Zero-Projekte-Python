import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Anzahl Qubits einstellen (z.B. 9, 12, 24, 48)
N = 12

# Positionen im Kreis
theta = np.linspace(0, 2*np.pi, N, endpoint=False)
x = np.cos(theta)
y = np.sin(theta)

# Zufällige Verbindungen (Paare)
pairs = [(i, (i+1)%N) for i in range(0, N, 2)]

fig, ax = plt.subplots(figsize=(6,6))

def update(frame):
    ax.clear()
    
    # Phase Bewegung
    phase = frame * 0.05
    
    # Farben (Phase codiert)
    colors = np.sin(theta + phase)
    
    # Qubits bewegen sich leicht (Rotation)
    x_rot = np.cos(theta + phase)
    y_rot = np.sin(theta + phase)
    
    # Verbindungen zeichnen
    for i, j in pairs:
        ax.plot([x_rot[i], x_rot[j]],
                [y_rot[i], y_rot[j]],
                color='orange', alpha=0.8)
    
    # Zusätzliche Netzwerkverbindungen
    for i in range(N):
        j = (i + 3) % N
        ax.plot([x_rot[i], x_rot[j]],
                [y_rot[i], y_rot[j]],
                color='purple', alpha=0.2)
    
    # Qubits zeichnen
    scatter = ax.scatter(x_rot, y_rot,
                         c=colors,
                         cmap='plasma',
                         s=80)
    
    ax.set_xlim(-1.5,1.5)
    ax.set_ylim(-1.5,1.5)
    ax.set_title(f"Qubit-Netzwerk (N={N})")
    ax.axis('off')

ani = animation.FuncAnimation(fig, update, frames=200, interval=50)
plt.show()