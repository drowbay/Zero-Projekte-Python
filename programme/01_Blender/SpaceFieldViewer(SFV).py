import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# -----------------------------
# PARAMETER
# -----------------------------
G = 1.0
grid_size = 180
space_size = 26.0
num_particles = 220
dt = 0.022
softening = 0.9

step_grav = 18
step_rot = 14
step_em = 18

# Schwarzes Loch / Horizont
bh_center = (0.0, 0.0)
horizon_radius = 3.2

# -----------------------------
# GALAXIENKERNE
# -----------------------------
# (x, y, Masse)
cores = [
    (0.0, 0.0, 520.0),
    (-8.0, 6.0, 120.0),
    (9.0, -7.0, 105.0),
]

# -----------------------------
# GRID
# -----------------------------
x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)

# -----------------------------
# HILFSFUNKTION
# -----------------------------
def normalize(arr):
    arr = np.array(arr, dtype=float)
    arr = arr - np.min(arr)
    return arr / (np.max(arr) + 1e-9)

# -----------------------------
# FELDER BERECHNEN
# -----------------------------
potential = np.zeros_like(X, dtype=float)
gravity_strength = np.zeros_like(X, dtype=float)
GX = np.zeros_like(X, dtype=float)
GY = np.zeros_like(X, dtype=float)

for cx, cy, mass in cores:
    dx = X - cx
    dy = Y - cy
    R = np.sqrt(dx**2 + dy**2 + softening**2)

    potential += -G * mass / R
    gravity_strength += G * mass / (R**2)

    GX += -G * mass * dx / (R**3)
    GY += -G * mass * dy / (R**3)

Gmag = np.sqrt(GX**2 + GY**2) + 1e-9

# -----------------------------
# ROTATIONSFELD
# -----------------------------
VX = np.zeros_like(X, dtype=float)
VY = np.zeros_like(X, dtype=float)

for cx, cy, mass in cores:
    dx = X - cx
    dy = Y - cy
    R = np.sqrt(dx**2 + dy**2 + softening**2)
    v_mag = np.sqrt(G * mass / R)

    VX += -dy / R * v_mag
    VY +=  dx / R * v_mag

Vmag = np.sqrt(VX**2 + VY**2)

# -----------------------------
# ENERGIE-LAYER
# -----------------------------
rot_energy = 0.5 * (Vmag**2)
grav_energy = gravity_strength
energy_field = grav_energy + rot_energy

grav_display = normalize(gravity_strength)
rot_display = normalize(Vmag)
energy_display = normalize(energy_field)

# -----------------------------
# LAYER 4: MS-VERBORGENE SCHICHT
# -----------------------------
eta_depth = normalize(np.abs(potential))

gradEx, gradEy = np.gradient(energy_field)
gradE_mag = np.sqrt(gradEx**2 + gradEy**2)
psi_activity = normalize(gradE_mag)

divGx = np.gradient(GX, axis=1)
divGy = np.gradient(GY, axis=0)
structure_flux = np.abs(divGx + divGy)
structure_flux = normalize(structure_flux)

hidden_0 = normalize(0.6 * eta_depth + 0.4 * psi_activity)
hidden_1 = normalize(0.6 * eta_depth + 0.4 * structure_flux)

ms_hidden = normalize(0.45 * eta_depth + 0.30 * psi_activity + 0.25 * structure_flux)

# -----------------------------
# LAYER 5: EM-/STRAHLUNGSLAYER
# -----------------------------
# Schlichte radiale Wellenstruktur + Modulation durch Energiegradient
R0 = np.sqrt(X**2 + Y**2) + 1e-9
em_wave = np.sin(0.55 * R0) ** 2
em_mod = normalize(0.5 * em_wave + 0.5 * psi_activity)

# Strahlungsrichtung: radial nach außen
EMX = X / R0
EMY = Y / R0

# -----------------------------
# LAYER 6: HAWKING-/HORIZONTLAYER
# -----------------------------
bx, by = bh_center
BH_R = np.sqrt((X - bx)**2 + (Y - by)**2) + 1e-9

# Horizont-Ring
ring = np.exp(-((BH_R - horizon_radius) ** 2) / 0.18)

# Raumkrümmungsnähe + Ringaktivität
horizon_depth = normalize((1.0 / BH_R) * 0.35 + ring * 0.65)

# Emergenz: Ring + Gradient + Potentialtiefe
hawking_layer = normalize(0.50 * ring + 0.25 * eta_depth + 0.25 * psi_activity)

# Hawking-Richtung: radial nach außen vom Horizont
HX = (X - bx) / BH_R
HY = (Y - by) / BH_R

# -----------------------------
# AUSGEDÜNNTE PFEILE
# -----------------------------
Xg = X[::step_grav, ::step_grav]
Yg = Y[::step_grav, ::step_grav]
GXg = GX[::step_grav, ::step_grav]
GYg = GY[::step_grav, ::step_grav]

# Gravitationspfeile nur Richtung sichtbar machen
Gnorm = np.sqrt(GXg**2 + GYg**2) + 1e-9
GXg_vis = 1.5 * GXg / Gnorm
GYg_vis = 1.5 * GYg / Gnorm

Xr = X[::step_rot, ::step_rot]
Yr = Y[::step_rot, ::step_rot]
VXr = VX[::step_rot, ::step_rot]
VYr = VY[::step_rot, ::step_rot]

Vnorm = np.sqrt(VXr**2 + VYr**2) + 1e-9
VXr_vis = 1.5 * VXr / Vnorm
VYr_vis = 1.5 * VYr / Vnorm

Xe = X[::step_em, ::step_em]
Ye = Y[::step_em, ::step_em]
EMXe = EMX[::step_em, ::step_em]
EMYe = EMY[::step_em, ::step_em]
HXe = HX[::step_em, ::step_em]
HYe = HY[::step_em, ::step_em]

# Winkel der Gravitationspfeile in Grad
angle_deg = (np.degrees(np.arctan2(GYg, GXg)) + 360) % 360

# -----------------------------
# TESTTEILCHEN
# -----------------------------
angles = np.random.uniform(0, 2*np.pi, num_particles)
radii = np.random.uniform(4.0, 20.0, num_particles)

px = radii * np.cos(angles)
py = 0.72 * radii * np.sin(angles)

pvx = np.zeros(num_particles)
pvy = np.zeros(num_particles)

for i in range(num_particles):
    vx_sum = 0.0
    vy_sum = 0.0
    for cx, cy, mass in cores:
        dx = px[i] - cx
        dy = py[i] - cy
        r = np.sqrt(dx**2 + dy**2 + softening**2)
        v = np.sqrt(G * mass / r)

        vx_sum += -dy / r * v
        vy_sum +=  dx / r * v

    pvx[i] = vx_sum
    pvy[i] = vy_sum

pvx += np.random.normal(0, 0.03, num_particles)
pvy += np.random.normal(0, 0.03, num_particles)

# -----------------------------
# FIGURE
# -----------------------------
fig, ax = plt.subplots(figsize=(10.5, 10.5), facecolor='black')
ax.set_facecolor('black')

current_layer = {"mode": 4}

im = ax.imshow(
    ms_hidden,
    extent=[-space_size, space_size, -space_size, space_size],
    origin='lower',
    cmap='magma',
    alpha=0.98
)

# Layer 1 Gravitation
quiv_grav = ax.quiver(
    Xg, Yg, GXg_vis, GYg_vis,
    color='deepskyblue',
    alpha=0.85,
    scale=28,
    width=0.004,
    headwidth=5,
    headlength=6,
    headaxislength=5
)

# Layer 2 Rotation
quiv_rot = ax.quiver(
    Xr, Yr, VXr_vis, VYr_vis,
    color='cyan',
    alpha=0.75,
    scale=26,
    width=0.0035,
    headwidth=4.5,
    headlength=5.5,
    headaxislength=5
)

# Layer 5 EM
quiv_em = ax.quiver(
    Xe, Ye, EMXe, EMYe,
    color='gold',
    alpha=0.75,
    scale=24,
    width=0.003,
    headwidth=4.5,
    headlength=5.2,
    headaxislength=4.8
)

# Layer 6 Hawking
quiv_hawk = ax.quiver(
    Xe, Ye, HXe, HYe,
    color='orange',
    alpha=0.0,
    scale=28,
    width=0.003,
    headwidth=4.5,
    headlength=5.2,
    headaxislength=4.8
)

# Gradtexte für Gravitation
angle_texts = []
for xi, yi, ang in zip(Xg.flatten(), Yg.flatten(), angle_deg.flatten()):
    txt = ax.text(
        xi, yi,
        f"{ang:.0f}°",
        color='lightskyblue',
        fontsize=7,
        fontweight='bold',
        ha='center',
        va='center',
        alpha=0.0
    )
    angle_texts.append(txt)

# MS-Texte
ms_texts = []
sample_step = 22
Xs = X[::sample_step, ::sample_step]
Ys = Y[::sample_step, ::sample_step]
H0s = hidden_0[::sample_step, ::sample_step]
H1s = hidden_1[::sample_step, ::sample_step]

for xi, yi, h0, h1 in zip(Xs.flatten(), Ys.flatten(), H0s.flatten(), H1s.flatten()):
    label = "~0" if h0 >= h1 else "~1"
    txt = ax.text(
        xi, yi,
        label,
        color='violet',
        fontsize=8,
        fontweight='bold',
        ha='center',
        va='center',
        alpha=0.0
    )
    ms_texts.append(txt)

# Kerne
for cx, cy, mass in cores:
    ax.scatter(cx, cy, s=80 + mass * 0.15, c='white', alpha=0.98)

# Ereignishorizont
horizon_circle = plt.Circle(
    bh_center, horizon_radius,
    edgecolor='orange',
    facecolor='none',
    linewidth=1.8,
    alpha=0.0
)
ax.add_patch(horizon_circle)

# Teilchen
particles = ax.scatter(px, py, s=8, c='white', alpha=0.9)

ax.set_xlim(-space_size, space_size)
ax.set_ylim(-space_size, space_size)
ax.tick_params(colors='white')
title = ax.set_title("", color='white', fontsize=14)

# -----------------------------
# LAYER ANZEIGE
# -----------------------------
def apply_layer():
    mode = current_layer["mode"]

    # Alles erst ausblenden/neutralisieren
    for txt in angle_texts:
        txt.set_alpha(0.0)
    for txt in ms_texts:
        txt.set_alpha(0.0)

    quiv_grav.set_alpha(0.0)
    quiv_rot.set_alpha(0.0)
    quiv_em.set_alpha(0.0)
    quiv_hawk.set_alpha(0.0)
    horizon_circle.set_alpha(0.0)

    if mode == 1:
        im.set_array(grav_display)
        im.set_cmap('plasma')
        im.set_alpha(0.97)

        quiv_grav.set_alpha(0.98)
        for txt in angle_texts:
            txt.set_alpha(0.96)

        title.set_text("MS Space Field Viewer v6\nLayer 1: Gravitation + D⃗ + Richtungsgrade")

    elif mode == 2:
        im.set_array(rot_display)
        im.set_cmap('viridis')
        im.set_alpha(0.97)

        quiv_rot.set_alpha(0.96)

        title.set_text("MS Space Field Viewer v6\nLayer 2: Rotation")

    elif mode == 3:
        im.set_array(energy_display)
        im.set_cmap('inferno')
        im.set_alpha(0.99)

        title.set_text("MS Space Field Viewer v6\nLayer 3: Gesamtenergie")

    elif mode == 4:
        im.set_array(ms_hidden)
        im.set_cmap('magma')
        im.set_alpha(0.99)

        quiv_grav.set_alpha(0.22)
        for txt in ms_texts:
            txt.set_alpha(0.72)

        title.set_text("MS Space Field Viewer v6\nLayer 4: Verborgene Struktur (~0 / ~1)")

    elif mode == 5:
        im.set_array(em_mod)
        im.set_cmap('cividis')
        im.set_alpha(0.98)

        quiv_em.set_alpha(0.95)

        title.set_text("MS Space Field Viewer v6\nLayer 5: EM-/Strahlungslayer")

    elif mode == 6:
        im.set_array(hawking_layer)
        im.set_cmap('afmhot')
        im.set_alpha(0.99)

        quiv_hawk.set_alpha(0.95)
        horizon_circle.set_alpha(0.95)

        title.set_text("MS Space Field Viewer v6\nLayer 6: Hawking-/Horizontlayer")

    elif mode == 7:
        im.set_array(ms_hidden)
        im.set_cmap('magma')
        im.set_alpha(0.90)

        quiv_grav.set_alpha(0.55)
        quiv_rot.set_alpha(0.58)
        quiv_em.set_alpha(0.45)
        quiv_hawk.set_alpha(0.35)
        horizon_circle.set_alpha(0.45)

        for txt in angle_texts:
            txt.set_alpha(0.35)
        for txt in ms_texts:
            txt.set_alpha(0.28)

        title.set_text("MS Space Field Viewer v6\nLayer 7: Alles zusammen")

# -----------------------------
# TASTEN
# -----------------------------
def on_key(event):
    if event.key in ['1', '2', '3', '4', '5', '6', '7']:
        current_layer["mode"] = int(event.key)
        apply_layer()
        fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', on_key)

# -----------------------------
# UPDATE
# -----------------------------
def update(frame):
    global px, py, pvx, pvy

    ax_total = np.zeros(num_particles)
    ay_total = np.zeros(num_particles)

    for cx, cy, mass in cores:
        dx = px - cx
        dy = py - cy
        r = np.sqrt(dx**2 + dy**2 + softening**2)

        ax_total += -G * mass * dx / (r**3)
        ay_total += -G * mass * dy / (r**3)

    pvx += ax_total * dt
    pvy += ay_total * dt

    px += pvx * dt
    py += pvy * dt

    r_out = np.sqrt(px**2 + py**2)
    too_far = r_out > 24.0
    too_close = r_out < 1.1
    reset = too_far | too_close

    if np.any(reset):
        new_angles = np.random.uniform(0, 2*np.pi, np.sum(reset))
        new_radii = np.random.uniform(8.0, 20.0, np.sum(reset))

        px[reset] = new_radii * np.cos(new_angles)
        py[reset] = 0.72 * new_radii * np.sin(new_angles)

        idxs = np.where(reset)[0]
        pvx_reset = np.zeros(len(idxs))
        pvy_reset = np.zeros(len(idxs))

        for j, i in enumerate(idxs):
            vx_sum = 0.0
            vy_sum = 0.0
            for cx, cy, mass in cores:
                dx = px[i] - cx
                dy = py[i] - cy
                r = np.sqrt(dx**2 + dy**2 + softening**2)
                v = np.sqrt(G * mass / r)

                vx_sum += -dy / r * v
                vy_sum +=  dx / r * v

            pvx_reset[j] = vx_sum
            pvy_reset[j] = vy_sum

        pvx[reset] = pvx_reset
        pvy[reset] = pvy_reset

    particles.set_offsets(np.column_stack([px, py]))
    return [particles, im, quiv_grav, quiv_rot, quiv_em, quiv_hawk, horizon_circle, *angle_texts, *ms_texts]

# -----------------------------
# START
# -----------------------------
apply_layer()

ani = animation.FuncAnimation(
    fig, update, frames=800, interval=30, blit=False
)

plt.tight_layout()
plt.show()