import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon, Circle

# ============================================================
# Künstliche Gravitation vs. echte Gravitation
# Version 2: deutlich weg von "Bloch-Sphäre"
#
# LINKS:
#   Ein rechteckiger Raum rotiert.
#   Die Außenwand wird zum gefühlten Boden.
#   a_rot = omega^2 * r
#
# RECHTS:
#   Newtonsche Gravitation.
#   Ein Raumgitter wird zum Massenzentrum hin verzerrt,
#   Falllinien zeigen die Richtung der Beschleunigung.
#   g = G*M/r^2
#
# Benötigt:
#   pip install numpy matplotlib
# ============================================================

G = 6.67430e-11
M_EARTH = 5.972e24
R_EARTH = 6.371e6

OMEGA = 0.65         # rad/s
ROOM_CENTER_R = 8.0  # Abstand Zimmerzentrum von Drehachse [m]
ROOM_W = 6.0
ROOM_H = 3.4
DT = 0.04

def artificial_gravity(omega, r):
    return omega**2 * r

def real_gravity(M, r):
    return G * M / r**2

def rotation_matrix(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s], [s, c]])

# ------------------------------------------------------------
# Figur
# ------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
fig.suptitle("Künstliche Gravitation vs. echte Gravitation", fontsize=15)

# ============================================================
# LINKS: ROTIERENDES RECHTECKIGES ZIMMER
# ============================================================
ax1.set_aspect("equal")
ax1.set_xlim(-13, 13)
ax1.set_ylim(-13, 13)
ax1.set_title("1) Drehraum: Wand wird zum Boden")
ax1.set_xlabel("x [m]")
ax1.set_ylabel("y [m]")
ax1.grid(True, alpha=0.18)

# Drehachse
ax1.plot(0, 0, "o")
ax1.text(0.35, 0.4, "Drehachse")

# gestrichelte Kreisbahn des Zimmerzentrums
phi = np.linspace(0, 2*np.pi, 400)
ax1.plot(
    ROOM_CENTER_R*np.cos(phi),
    ROOM_CENTER_R*np.sin(phi),
    linestyle="--",
    linewidth=1.0,
    alpha=0.35
)

# Zimmerpolygon
room_patch = Polygon(np.zeros((4, 2)), closed=True, fill=False, linewidth=2.5)
ax1.add_patch(room_patch)

# "Boden"-Kante
floor_line, = ax1.plot([], [], linewidth=5)

# Person
person_body, = ax1.plot([], [], linewidth=2.5)
person_head, = ax1.plot([], [], marker="o", markersize=7)

# Richtung künstliche Gravitation
fake_g_line, = ax1.plot([], [], linewidth=3)

# Tangentiale Bewegungsrichtung
tangent_line, = ax1.plot([], [], linestyle="--", linewidth=2)

# Verbindung Drehachse -> Raum
radius_line, = ax1.plot([], [], linewidth=1.2, alpha=0.6)

text1 = ax1.text(-12.5, -12.0, "", fontsize=10)

# ============================================================
# RECHTS: ECHTE GRAVITATION MIT VERZERRTEM GITTER
# ============================================================
ax2.set_aspect("equal")
ax2.set_xlim(-4.2, 4.2)
ax2.set_ylim(-4.2, 4.2)
ax2.set_title("2) Echte Gravitation: Feld zum Zentrum")
ax2.set_xlabel("x [Erdradien]")
ax2.set_ylabel("y [Erdradien]")
ax2.grid(False)

# Zentralmasse
earth = Circle((0, 0), 0.75, fill=False, linewidth=3)
ax2.add_patch(earth)
ax2.text(-0.11, 0.05, "M", fontsize=14)

# Verformtes Raumgitter
grid_lines = []

def bend_grid_vertical(x0, ys):
    # reine Visualisierung:
    # nahe am Zentrum wird die Linie stärker zum Zentrum gezogen
    xs = []
    out_y = []
    for y in ys:
        r = np.sqrt(x0*x0 + y*y)
        influence = 0.0 if r < 0.85 else 0.45 / (r*r + 0.35)
        xs.append(x0 * (1 - influence))
        out_y.append(y * (1 - influence))
    return np.array(xs), np.array(out_y)

def bend_grid_horizontal(y0, xs):
    out_x = []
    ys = []
    for x in xs:
        r = np.sqrt(x*x + y0*y0)
        influence = 0.0 if r < 0.85 else 0.45 / (r*r + 0.35)
        out_x.append(x * (1 - influence))
        ys.append(y0 * (1 - influence))
    return np.array(out_x), np.array(ys)

grid_vals = np.arange(-4, 4.01, 0.5)
curve = np.linspace(-4, 4, 250)

for x0 in grid_vals:
    xg, yg = bend_grid_vertical(x0, curve)
    line, = ax2.plot(xg, yg, linewidth=0.55, alpha=0.28)
    grid_lines.append(line)

for y0 in grid_vals:
    xg, yg = bend_grid_horizontal(y0, curve)
    line, = ax2.plot(xg, yg, linewidth=0.55, alpha=0.28)
    grid_lines.append(line)

# feste Feldlinien nach innen
angles = np.linspace(0, 2*np.pi, 14, endpoint=False)
for a in angles:
    r0 = 3.7
    r1 = 0.9
    x = [r0*np.cos(a), r1*np.cos(a)]
    y = [r0*np.sin(a), r1*np.sin(a)]
    ax2.plot(x, y, linewidth=1.0, alpha=0.45)

# animierter Testkörper
particle, = ax2.plot([], [], marker="o", markersize=8)

# Spur
trail, = ax2.plot([], [], linewidth=1.5)

# g-Linie
g_line, = ax2.plot([], [], linewidth=3)

text2 = ax2.text(-4.0, -3.9, "", fontsize=10)

# Startposition und Geschwindigkeit
p = np.array([3.2, 1.4], dtype=float)
v = np.array([-0.004, 0.012], dtype=float)
trail_x, trail_y = [], []

# ============================================================
# UPDATE
# ============================================================
def update(frame):
    global p, v, trail_x, trail_y

    t = frame * DT

    # --------------------------------------------------------
    # LINKS: Zimmer rotieren
    # --------------------------------------------------------
    angle = OMEGA * t

    # Einheitsvektoren
    er = np.array([np.cos(angle), np.sin(angle)])        # radial nach außen
    et = np.array([-np.sin(angle), np.cos(angle)])       # tangential

    center = ROOM_CENTER_R * er

    # Lokale Raumkoordinaten:
    # x_local = tangential
    # y_local = radial
    half_w = ROOM_W / 2
    half_h = ROOM_H / 2

    local_corners = np.array([
        [-half_w, -half_h],
        [ half_w, -half_h],
        [ half_w,  half_h],
        [-half_w,  half_h]
    ])

    # Basis: lokale x-Achse = et, lokale y-Achse = er
    corners = np.array([
        center + c[0]*et + c[1]*er
        for c in local_corners
    ])

    room_patch.set_xy(corners)

    # äußere Kante = gefühlter Boden
    outer_a = center - half_w*et + half_h*er
    outer_b = center + half_w*et + half_h*er
    floor_line.set_data(
        [outer_a[0], outer_b[0]],
        [outer_a[1], outer_b[1]]
    )

    # Person steht auf Außenkante
    foot = center + 0.6*et + half_h*er
    body_base = foot - 0.15*er
    body_top = foot - 1.2*er
    head = foot - 1.55*er

    person_body.set_data(
        [body_base[0], body_top[0]],
        [body_base[1], body_top[1]]
    )
    person_head.set_data([head[0]], [head[1]])

    # künstliche Gravitation: nach außen
    g_start = foot - 0.9*er
    g_end = g_start + 2.2*er
    fake_g_line.set_data(
        [g_start[0], g_end[0]],
        [g_start[1], g_end[1]]
    )

    # Tangentiale Bewegung
    tv_start = center
    tv_end = center + 2.4*et
    tangent_line.set_data(
        [tv_start[0], tv_end[0]],
        [tv_start[1], tv_end[1]]
    )

    radius_line.set_data([0, center[0]], [0, center[1]])

    a_rot = artificial_gravity(OMEGA, ROOM_CENTER_R + half_h)

    text1.set_text(
        "Im mitrotierenden Raum:\n"
        f"ω = {OMEGA:.2f} rad/s\n"
        f"r ≈ {ROOM_CENTER_R + half_h:.2f} m\n"
        f"a = ω²r = {a_rot:.2f} m/s²\n"
        "Außenwand = gefühlter Boden"
    )

    # --------------------------------------------------------
    # RECHTS: Testkörper im Gravitationsfeld
    # --------------------------------------------------------
    r = np.linalg.norm(p)

    if r > 0.82:
        # dimensionloses 1/r^2-Feld
        acc = -0.0042 * p / (r**3)
        v += acc
        p += v
    else:
        # Aufprall / Oberfläche
        p = p / np.linalg.norm(p) * 0.82
        v[:] = 0

    particle.set_data([p[0]], [p[1]])

    # Spur
    trail_x.append(p[0])
    trail_y.append(p[1])

    if len(trail_x) > 350:
        trail_x = trail_x[-350:]
        trail_y = trail_y[-350:]

    trail.set_data(trail_x, trail_y)

    # g-Richtung
    r = np.linalg.norm(p)
    inward = -p / r if r > 0 else np.array([0.0, 0.0])
    g_start = p
    g_end = p + 0.9*inward

    g_line.set_data(
        [g_start[0], g_end[0]],
        [g_start[1], g_end[1]]
    )

    physical_r = max(r * R_EARTH, R_EARTH)
    g_phys = real_gravity(M_EARTH, physical_r)

    text2.set_text(
        "Newtonsche Gravitation:\n"
        "g = GM / r²\n"
        f"r = {r:.2f} R⊕\n"
        f"g ≈ {g_phys:.2f} m/s²\n"
        "Richtung: zum Massenzentrum"
    )

    return (
        room_patch,
        floor_line,
        person_body,
        person_head,
        fake_g_line,
        tangent_line,
        radius_line,
        particle,
        trail,
        g_line,
        text1,
        text2
    )

ani = FuncAnimation(
    fig,
    update,
    frames=3000,
    interval=DT*1000,
    blit=False
)

plt.tight_layout()
plt.show()
