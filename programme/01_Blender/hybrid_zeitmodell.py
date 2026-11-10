
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 12, 900)

activity = 0.55 + 0.20*np.sin(1.3*x) + 0.10*np.sin(3.4*x + 0.7)
center = 0.18*np.sin(0.8*x) + 0.05*np.sin(2.6*x)

upper = center + activity/2
lower = center - activity/2

state = 0.9*np.sin(0.55*x) + 0.2*np.cos(1.8*x)

theta = np.linspace(0, 2*np.pi, 400)
R = 1.0
ox, oy = 9.3, -2.2
cx = ox + R*np.cos(theta)
cy = oy + R*np.sin(theta)

t = np.linspace(0, 10, 400)
traj_x = 7.2 + 0.9*np.cos(0.8*t) + 0.18*t/10
traj_y = 2.0 + 0.55*np.sin(1.7*t) * np.exp(-0.08*t)

fig = plt.figure(figsize=(12, 8))
ax = plt.gca()

ax.plot(x, upper, linewidth=1.6)
ax.plot(x, lower, linewidth=1.6)
ax.plot(x, center, linewidth=1.2, linestyle='--')
ax.fill_between(x, lower, upper, alpha=0.15)

ax.plot(x, state + 2.4, linewidth=1.5)

ax.plot(cx, cy, linewidth=1.2)
ax.plot([ox], [oy], marker='o')
ax.plot([ox + R], [oy], marker='o')

ax.plot(traj_x, traj_y, linewidth=1.4)
ax.plot([traj_x[0]], [traj_y[0]], marker='o')
ax.plot([traj_x[-1]], [traj_y[-1]], marker='s')

ax.axhline(0, linewidth=1.0)
ax.axvline(0, linewidth=1.0)

ax.text(0.3, 1.35, "A: atmendes Zeitband", fontsize=12)
ax.text(0.4, 0.05, "Mittellinie f(x)", fontsize=10)
ax.text(0.5, -0.95, "Bandbreite d(x) ~ Aktivitaet / Veraenderung", fontsize=10)

ax.text(0.3, 4.2, "B: Zustandskurve  Z(t)", fontsize=12)
ax.text(6.8, 2.85, "C: Pfad im Zustandsraum", fontsize=12)
ax.text(8.0, -0.8, "D: zyklisches Subsystem", fontsize=12)

ax.annotate("obere Begrenzung", xy=(2.7, upper[200]), xytext=(1.4, 1.9),
            arrowprops=dict(arrowstyle="->"), fontsize=10)
ax.annotate("untere Begrenzung", xy=(2.7, lower[200]), xytext=(1.1, -1.75),
            arrowprops=dict(arrowstyle="->"), fontsize=10)
ax.annotate("Start", xy=(traj_x[0], traj_y[0]), xytext=(6.0, 1.3),
            arrowprops=dict(arrowstyle="->"), fontsize=10)
ax.annotate("Ende", xy=(traj_x[-1], traj_y[-1]), xytext=(8.6, 3.0),
            arrowprops=dict(arrowstyle="->"), fontsize=10)
ax.annotate("Rotation / Zyklus", xy=(ox+0.7, oy+0.2), xytext=(10.2, -3.3),
            arrowprops=dict(arrowstyle="->"), fontsize=10)

ax.set_title("Hybrid-Modell: Zeit als sichtbare Projektion von Zustandsaenderung")
ax.set_xlabel("x / Prozessachse")
ax.set_ylabel("Struktur / Zustand")
ax.grid(True, alpha=0.35)
ax.set_xlim(0, 12)
ax.set_ylim(-3.8, 5.1)

plt.tight_layout()
plt.show()
