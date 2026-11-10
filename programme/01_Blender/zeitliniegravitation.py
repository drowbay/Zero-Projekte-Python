import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Zeit
t = np.linspace(0, 20, 600)
dt = t[1] - t[0]

# Grundsignal (normal)
base = np.sin(0.8*t)

# "MS-Störung" (unruhig + zufällig)
np.random.seed(1)
noise = 0.4 * np.random.normal(size=len(t))

# sporadische Peaks (Schübe)
peaks = np.zeros_like(t)
for i in range(50, len(t), 120):
    peaks[i:i+10] += np.linspace(0, 2, 10)

# Gesamtinput
inp = base + noise + peaks

# System
gamma = 0.6
k = 1.2

Z = np.zeros_like(t)
for i in range(1, len(t)):
    Z[i] = Z[i-1] + dt * (-gamma * Z[i-1] + k * inp[i-1])

# Aktivität
dZdt = np.gradient(Z, dt)
A = dZdt**2

# Normieren
A_norm = (A - A.min()) / (A.max() - A.min())

# Plot
fig, ax = plt.subplots()
ax.set_xlim(0, 20)
ax.set_ylim(-3, 3)

line_upper, = ax.plot([], [])
line_lower, = ax.plot([], [])
line_center, = ax.plot([], [], linestyle='--')

def update(frame):
    x = t[:frame]
    
    center = 0.2*np.sin(0.3*x)
    width = 0.3 + 1.2*A_norm[:frame]   # stärkeres "Atmen"
    
    upper = center + width/2
    lower = center - width/2
    
    line_upper.set_data(x, upper)
    line_lower.set_data(x, lower)
    line_center.set_data(x, center)
    
    return line_upper, line_lower, line_center

ani = FuncAnimation(fig, update, frames=len(t), interval=20)

plt.title("Gestörtes Zeitband (MS-inspirierte Dynamik)")
plt.show()