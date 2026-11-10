import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Anzahl Qubits (hochdrehen!)
N = 120  

# Startpositionen zufällig
positions = np.random.uniform(-1,1,(N,2))

# Geschwindigkeit (für Drift)
velocity = np.random.uniform(-0.01,0.01,(N,2))

fig, ax = plt.subplots(figsize=(7,7))

def update(frame):
    global positions, velocity
    
    # 🌀 Drift + leichte Rückführung (damit es nicht wegfliegt)
    center = np.mean(positions, axis=0)
    velocity += (center - positions) * 0.0005
    
    # 🎲 Noise → Leben
    velocity += np.random.uniform(-0.002,0.002,(N,2))
    
    positions += velocity
    
    ax.clear()
    
    # 🌈 Phase (dein Schwingen)
    phase = np.sin(frame*0.05 + np.arange(N))
    
    # 🔗 Verbindungen (lokale Nähe)
    for i in range(N):
        for j in range(i+1, N):
            dist = np.linalg.norm(positions[i] - positions[j])
            
            # nur nahe verbinden → organisch
            if dist < 0.3:
                ax.plot([positions[i,0], positions[j,0]],
                        [positions[i,1], positions[j,1]],
                        color='orange', alpha=0.05)
    
    # ✨ Qubits
    scatter = ax.scatter(
        positions[:,0], positions[:,1],
        c=phase,
        cmap='plasma',
        s=20
    )
    
    ax.set_xlim(-2,2)
    ax.set_ylim(-2,2)
    ax.set_title(f"Driftendes Qubit-Netzwerk (N={N})")
    ax.axis('off')

ani = animation.FuncAnimation(fig, update, frames=300, interval=40)
plt.show()