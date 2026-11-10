import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, CheckButtons
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ============================================================
# MSM + 3D SPINFOAM COMBINED
# Mobile-freundlichere Kombi-Version
# ============================================================

np.random.seed(7)

# ============================================================
# 0) SLIDER PLACEHOLDERS (wichtig gegen NameError)
# ============================================================
slider_eta = None
slider_psi = None
slider_delta = None
slider_speed = None

# ============================================================
# 1) SETTINGS
# ============================================================
G = 1.0
grid_size = 120
space_size = 20.0
num_particles = 120
dt = 0.024
softening = 0.9
step_arrow = 16
trail_length = 10
frames = 900

cores = [
    (0.0, 0.0, 420.0),
    (-7.0, 5.0, 110.0),
    (8.0, -6.0, 95.0),
]

# ============================================================
# 2) HELPERS
# ============================================================
def normalize(arr):
    arr = np.array(arr, dtype=float)
    arr = arr - np.min(arr)
    return arr / (np.max(arr) + 1e-9)

def unit_vectors(FX, FY):
    n = np.sqrt(FX**2 + FY**2) + 1e-9
    return FX / n, FY / n

def rot_z(a):
    return np.array([
        [np.cos(a), -np.sin(a), 0],
        [np.sin(a),  np.cos(a), 0],
        [0, 0, 1]
    ])

def rot_y(a):
    return np.array([
        [ np.cos(a), 0, np.sin(a)],
        [0, 1, 0],
        [-np.sin(a), 0, np.cos(a)]
    ])

def make_triangle(center, size=0.4, yaw=0.0, tilt=0.0):
    base = np.array([
        [0.0,  1.0, 0.0],
        [-0.85, -0.75, 0.0],
        [0.85, -0.75, 0.0]
    ]) * size
    R = rot_z(yaw) @ rot_y(tilt)
    pts = base @ R.T
    pts += np.array(center)
    return pts

def make_wire_triangle(center, size=0.7, yaw=0.0, tilt=0.0):
    pts = make_triangle(center, size=size, yaw=yaw, tilt=tilt)
    return np.vstack([pts, pts[0]])

# ============================================================
# 3) GRID / 2D RAUM
# ============================================================
x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)

R0 = np.sqrt(X**2 + Y**2 + 1e-9)
RX, RY = X / R0, Y / R0

# ============================================================
# 4) BASISFELDER
# ============================================================
potential = np.zeros_like(X, dtype=float)
gravity_strength = np.zeros_like(X, dtype=float)
GX = np.zeros_like(X, dtype=float)
GY = np.zeros_like(X, dtype=float)
VX = np.zeros_like(X, dtype=float)
VY = np.zeros_like(X, dtype=float)

for cx, cy, mass in cores:
    dx = X - cx
    dy = Y - cy
    R = np.sqrt(dx**2 + dy**2 + softening**2)

    potential += -G * mass / R
    gravity_strength += G * mass / (R**2)
    GX += -G * mass * dx / (R**3)
    GY += -G * mass * dy / (R**3)

    v_mag = np.sqrt(G * mass / R)
    VX += -dy / R * v_mag
    VY +=  dx / R * v_mag

Gmag = np.sqrt(GX**2 + GY**2) + 1e-9
Vmag = np.sqrt(VX**2 + VY**2) + 1e-9
rot_energy = 0.5 * (Vmag**2)
energy_field = gravity_strength + rot_energy

# ============================================================
# 5) MS BASIS
# ============================================================
eta_depth = normalize(np.abs(potential))

gradEx, gradEy = np.gradient(energy_field)
gradE_mag = np.sqrt(gradEx**2 + gradEy**2)
psi_activity = normalize(gradE_mag)

partial_gx_x = np.gradient(GX, axis=1)
partial_gy_y = np.gradient(GY, axis=0)
grav_div = partial_gx_x + partial_gy_y
structure_flux = normalize(np.abs(grav_div))

partial_vy_x = np.gradient(VY, axis=1)
partial_vx_y = np.gradient(VX, axis=0)
vorticity = partial_vy_x - partial_vx_y
phase_field = normalize(np.abs(vorticity) + 0.65 * psi_activity)

expansion_driver = normalize(np.clip(gradEx * RX + gradEy * RY, 0, None) + 0.35 * rot_energy)
implosion_driver = normalize(np.clip(-(GX * RX + GY * RY), 0, None) + 0.30 * eta_depth)
phase_feedback = normalize(0.45 * phase_field + 0.30 * structure_flux + 0.25 * eta_depth)

MODELS = {
    1: ("A", normalize(0.55 * expansion_driver + 0.30 * rot_energy + 0.15 * psi_activity)),
    2: ("B", normalize(0.50 * phase_field + 0.35 * psi_activity + 0.15 * structure_flux)),
    3: ("C", normalize(0.60 * implosion_driver + 0.25 * gravity_strength + 0.15 * eta_depth)),
    4: ("D", normalize(0.45 * phase_feedback + 0.35 * structure_flux + 0.20 * psi_activity)),
    5: ("Ψ", normalize(0.45 * eta_depth + 0.30 * psi_activity + 0.25 * normalize(energy_field))),
}

PROCESS_ARROWS = {
    1: unit_vectors(RX * (0.3 + expansion_driver), RY * (0.3 + expansion_driver)),
    2: unit_vectors(-RY * (0.3 + phase_field), RX * (0.3 + phase_field)),
    3: unit_vectors(-RX * (0.3 + implosion_driver), -RY * (0.3 + implosion_driver)),
    4: unit_vectors(normalize(gradEx) - normalize(GX), normalize(gradEy) - normalize(GY)),
    5: unit_vectors(gradEx + RX, gradEy + RY),
}

CMAPS = {
    1: "inferno",
    2: "viridis",
    3: "plasma",
    4: "magma",
    5: "twilight",
}

Xs = X[::step_arrow, ::step_arrow]
Ys = Y[::step_arrow, ::step_arrow]

# ============================================================
# 6) PARTICLES 2D
# ============================================================
angles = np.random.uniform(0, 2 * np.pi, num_particles)
radii = np.random.uniform(4.0, 15.0, num_particles)

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

trail_x = [px.copy() for _ in range(trail_length)]
trail_y = [py.copy() for _ in range(trail_length)]

# ============================================================
# 7) 3D STATIC STRUCTURE
# ============================================================
rng = np.random.default_rng(7)

vertex = np.array([0.0, 0.0, 0.0])
g1 = np.array([0.35, 0.95, 0.55])
g2 = np.array([0.45, -0.75, -0.35])

eta_points_3d = np.column_stack([
    rng.uniform(-2.5, 8.0, 120),
    rng.uniform(-1.6, 5.2, 120),
    rng.uniform(-1.8, 3.8, 120)
])

face_top = np.array([
    [1.2, 3.7, 2.2],
    [6.8, 4.4, 2.9],
    [7.7, 2.2, 1.2],
    [3.0, 1.5, 0.9],
    [0.9, 2.4, 1.4]
])

face_mid = np.array([
    [0.7, 1.0, 0.4],
    [5.8, 1.6, 1.0],
    [6.8, 0.2, 0.1],
    [3.6, -0.7, -0.6],
    [1.2, -0.1, -0.2]
])

# ============================================================
# 8) STATE
# ============================================================
state = {
    "model": 1,
    "show_particles": True,
    "show_3d_links": True,
    "show_3d_wire": True,
    "show_3d_labels": False,
    "paused": False,
}

# ============================================================
# 9) SAFE SCALE ACCESS
# ============================================================
def get_eta_scale():
    return slider_eta.val if slider_eta is not None else 1.0

def get_psi_scale():
    return slider_psi.val if slider_psi is not None else 1.0

def get_delta_scale():
    return slider_delta.val if slider_delta is not None else 1.0

def get_speed_scale():
    return slider_speed.val if slider_speed is not None else 1.0

def current_scaled_fields():
    eta_scale = get_eta_scale()
    psi_scale = get_psi_scale()
    delta_scale = get_delta_scale()

    eta_mix = normalize(eta_depth * eta_scale)
    psi_mix = normalize(psi_activity * psi_scale)
    delta_mix = normalize(np.abs(eta_mix - psi_mix) * delta_scale)

    return eta_mix, psi_mix, delta_mix

# ============================================================
# 10) FIGURE
# ============================================================
fig = plt.figure(figsize=(15, 9), facecolor="black")

ax2d = fig.add_axes([0.05, 0.33, 0.40, 0.58], facecolor="black")
ax3d = fig.add_axes([0.52, 0.33, 0.42, 0.58], projection="3d", facecolor="white")
ax_info = fig.add_axes([0.05, 0.05, 0.89, 0.18], facecolor="black")
ax_info.axis("off")

# sliders / buttons
ax_eta = fig.add_axes([0.08, 0.25, 0.22, 0.03], facecolor="dimgray")
ax_psi = fig.add_axes([0.36, 0.25, 0.22, 0.03], facecolor="dimgray")
ax_delta = fig.add_axes([0.64, 0.25, 0.22, 0.03], facecolor="dimgray")
ax_speed = fig.add_axes([0.08, 0.20, 0.22, 0.03], facecolor="dimgray")

ax_reset = fig.add_axes([0.36, 0.19, 0.10, 0.05])
ax_pause = fig.add_axes([0.49, 0.19, 0.10, 0.05])
ax_checks = fig.add_axes([0.64, 0.16, 0.22, 0.08], facecolor="black")

# ============================================================
# 11) CREATE SLIDERS NOW (vor Benutzung!)
# ============================================================
slider_eta = Slider(ax_eta, "η", 0.0, 2.0, valinit=1.0)
slider_psi = Slider(ax_psi, "ψ", 0.0, 2.0, valinit=1.0)
slider_delta = Slider(ax_delta, "Δ", 0.0, 2.0, valinit=1.0)
slider_speed = Slider(ax_speed, "v", 0.1, 2.5, valinit=1.0)

btn_reset = Button(ax_reset, "Reset")
btn_pause = Button(ax_pause, "Pause")

checks = CheckButtons(
    ax_checks,
    ["Particles", "3D Links", "3D Wire", "3D Labels"],
    [True, True, True, False]
)

for txt in checks.labels:
    txt.set_color("white")

# ============================================================
# 12) INITIAL 2D VIEW
# ============================================================
eta_mix0, psi_mix0, delta0 = current_scaled_fields()
base0 = normalize(0.55 * MODELS[state["model"]][1] + 0.25 * eta_mix0 + 0.20 * psi_mix0)

im2d = ax2d.imshow(
    base0,
    extent=[-space_size, space_size, -space_size, space_size],
    origin="lower",
    cmap=CMAPS[state["model"]],
    alpha=0.98,
)

delta_overlay = ax2d.imshow(
    delta0,
    extent=[-space_size, space_size, -space_size, space_size],
    origin="lower",
    cmap="coolwarm",
    alpha=0.24,
    vmin=0.0,
    vmax=1.0,
)

U0, V0 = PROCESS_ARROWS[state["model"]]
quiver2d = ax2d.quiver(
    Xs, Ys, U0[::step_arrow, ::step_arrow], V0[::step_arrow, ::step_arrow],
    color="white", alpha=0.75, scale=24, width=0.003
)

particles2d = ax2d.scatter(px, py, s=8, c="white", alpha=0.85)

trail_scatters = []
for i in range(trail_length):
    alpha = (i + 1) / trail_length * 0.08
    size = 1.5 + (i / trail_length) * 4
    sc = ax2d.scatter([], [], s=size, c="white", alpha=alpha)
    trail_scatters.append(sc)

ax2d.set_xlim(-space_size, space_size)
ax2d.set_ylim(-space_size, space_size)
ax2d.tick_params(colors="white")
title2d = ax2d.set_title("MSM Feldansicht", color="white", fontsize=13)

# ============================================================
# 13) INITIAL 3D VIEW
# ============================================================
poly_top = Poly3DCollection([face_top], facecolors="0.95", edgecolors="black", linewidths=1.5, alpha=1.0)
poly_mid = Poly3DCollection([face_mid], facecolors="0.88", edgecolors="black", linewidths=1.5, alpha=1.0)
ax3d.add_collection3d(poly_top)
ax3d.add_collection3d(poly_mid)

eta_scatter_3d = ax3d.scatter(
    eta_points_3d[:, 0], eta_points_3d[:, 1], eta_points_3d[:, 2],
    s=14, facecolors="none", edgecolors="0.4", linewidths=0.7, alpha=0.75
)

ax3d.scatter([vertex[0]], [vertex[1]], [vertex[2]], s=40, color="black")
ax3d.scatter([g1[0], g2[0]], [g1[1], g2[1]], [g1[2], g2[2]], s=18, color="black")

ax3d.plot([vertex[0], g1[0]], [vertex[1], g1[1]], [vertex[2], g1[2]], color="black", lw=1.3)
ax3d.plot([vertex[0], g2[0]], [vertex[1], g2[1]], [vertex[2], g2[2]], color="black", lw=1.3)

wedge_polys = []
wire_lines = []
for _ in range(4):
    poly = Poly3DCollection([np.zeros((3, 3))], facecolors="0.2", edgecolors="black", linewidths=1.0, alpha=1.0)
    ax3d.add_collection3d(poly)
    wedge_polys.append(poly)

    line, = ax3d.plot([], [], [], color="0.5", lw=1.0, alpha=0.7)
    wire_lines.append(line)

link_lines = []
for _ in range(3):
    line, = ax3d.plot([], [], [], color="0.25", lw=1.2)
    link_lines.append(line)

label_vertex = ax3d.text(-0.55, 0.0, 0.0, "vertex", fontsize=10)
label_wedge = ax3d.text(3.7, 0.6, 0.4, "wedge", fontsize=10)
label_face = ax3d.text(7.0, 3.2, 2.5, "spin foam face", fontsize=10)
label_edge = ax3d.text(7.0, -0.6, -0.5, "edge", fontsize=10)

ax3d.set_xlim(-1.2, 8.4)
ax3d.set_ylim(-2.2, 5.3)
ax3d.set_zlim(-2.2, 4.0)
ax3d.set_xlabel("X")
ax3d.set_ylabel("Y")
ax3d.set_zlabel("Z")
ax3d.view_init(elev=24, azim=-64)
title3d = ax3d.set_title("3D Sinnform / Spinfoam", fontsize=13)

# ============================================================
# 14) INFO TEXT
# ============================================================
info_text = ax_info.text(
    0.01, 0.95,
    "",
    transform=ax_info.transAxes,
    color="white",
    fontsize=10,
    va="top",
    ha="left",
    family="monospace",
    bbox=dict(facecolor="black", alpha=0.35, edgecolor="gray", boxstyle="round,pad=0.5"),
)

# ============================================================
# 15) UPDATE HELPERS
# ============================================================
def refresh_titles():
    model_letter = MODELS[state["model"]][0]
    title2d.set_text(f"MSM Feldansicht | Modell {model_letter}")
    title3d.set_text(f"3D Sinnform / Spinfoam | Modell {model_letter}")

    info_text.set_text(
        "MSM + 3D SPINFOAM COMBINED\n"
        f"Modell: {model_letter}\n"
        f"η = {get_eta_scale():.2f}\n"
        f"ψ = {get_psi_scale():.2f}\n"
        f"Δ = {get_delta_scale():.2f}\n"
        f"v = {get_speed_scale():.2f}\n"
        f"Particles = {state['show_particles']}\n"
        f"3D Links = {state['show_3d_links']}\n"
        f"3D Wire = {state['show_3d_wire']}\n"
        f"3D Labels = {state['show_3d_labels']}\n"
        f"Paused = {state['paused']}\n\n"
        "Tasten:\n"
        "1..5 = Modell\n"
        "Leertaste = Pause\n"
        "P = Partikel\n"
        "L = Labels\n"
        "K = Links\n"
        "W = Wire"
    )

def on_slider_change(val):
    refresh_titles()
    fig.canvas.draw_idle()

slider_eta.on_changed(on_slider_change)
slider_psi.on_changed(on_slider_change)
slider_delta.on_changed(on_slider_change)
slider_speed.on_changed(on_slider_change)

def reset_all(event):
    slider_eta.reset()
    slider_psi.reset()
    slider_delta.reset()
    slider_speed.reset()
    state["show_particles"] = True
    state["show_3d_links"] = True
    state["show_3d_wire"] = True
    state["show_3d_labels"] = False
    state["paused"] = False
    btn_pause.label.set_text("Pause")
    refresh_titles()
    fig.canvas.draw_idle()

btn_reset.on_clicked(reset_all)

def toggle_pause(event):
    state["paused"] = not state["paused"]
    btn_pause.label.set_text("Resume" if state["paused"] else "Pause")
    refresh_titles()
    fig.canvas.draw_idle()

btn_pause.on_clicked(toggle_pause)

def on_checks(label):
    if label == "Particles":
        state["show_particles"] = not state["show_particles"]
    elif label == "3D Links":
        state["show_3d_links"] = not state["show_3d_links"]
    elif label == "3D Wire":
        state["show_3d_wire"] = not state["show_3d_wire"]
    elif label == "3D Labels":
        state["show_3d_labels"] = not state["show_3d_labels"]
    refresh_titles()
    fig.canvas.draw_idle()

checks.on_clicked(on_checks)

def on_key(event):
    key = (event.key or "").lower()

    if key in ["1", "2", "3", "4", "5"]:
        state["model"] = int(key)
        refresh_titles()
        fig.canvas.draw_idle()
    elif key == " ":
        state["paused"] = not state["paused"]
        btn_pause.label.set_text("Resume" if state["paused"] else "Pause")
        refresh_titles()
        fig.canvas.draw_idle()
    elif key == "p":
        state["show_particles"] = not state["show_particles"]
        refresh_titles()
        fig.canvas.draw_idle()
    elif key == "l":
        state["show_3d_labels"] = not state["show_3d_labels"]
        refresh_titles()
        fig.canvas.draw_idle()
    elif key == "k":
        state["show_3d_links"] = not state["show_3d_links"]
        refresh_titles()
        fig.canvas.draw_idle()
    elif key == "w":
        state["show_3d_wire"] = not state["show_3d_wire"]
        refresh_titles()
        fig.canvas.draw_idle()

fig.canvas.mpl_connect("key_press_event", on_key)

# ============================================================
# 16) ANIMATION
# ============================================================
def update(frame):
    global px, py, pvx, pvy, trail_x, trail_y

    speed = get_speed_scale()
    t = frame * 0.045 * speed

    eta_mix, psi_mix, delta_mix = current_scaled_fields()

    # 2D update
    base = normalize(0.55 * MODELS[state["model"]][1] + 0.25 * eta_mix + 0.20 * psi_mix)
    im2d.set_array(base)
    im2d.set_cmap(CMAPS[state["model"]])

    delta_overlay.set_array(delta_mix)
    delta_overlay.set_alpha(0.26)

    U, V = PROCESS_ARROWS[state["model"]]
    quiver2d.set_UVC(U[::step_arrow, ::step_arrow], V[::step_arrow, ::step_arrow])

    if not state["paused"]:
        ax_total = np.zeros(num_particles)
        ay_total = np.zeros(num_particles)

        for cx, cy, mass in cores:
            dx = px - cx
            dy = py - cy
            r = np.sqrt(dx**2 + dy**2 + softening**2)
            ax_total += -G * mass * dx / (r**3)
            ay_total += -G * mass * dy / (r**3)

        pvx += ax_total * dt * speed
        pvy += ay_total * dt * speed
        px += pvx * dt * speed
        py += pvy * dt * speed

        r_out = np.sqrt(px**2 + py**2)
        reset = (r_out > 19.0) | (r_out < 1.2)

        if np.any(reset):
            new_angles = np.random.uniform(0, 2*np.pi, np.sum(reset))
            new_radii = np.random.uniform(8.0, 15.0, np.sum(reset))
            px[reset] = new_radii * np.cos(new_angles)
            py[reset] = 0.72 * new_radii * np.sin(new_angles)
            pvx[reset] = 0.0
            pvy[reset] = 0.0

        trail_x.pop(0)
        trail_y.pop(0)
        trail_x.append(px.copy())
        trail_y.append(py.copy())

    offsets = np.column_stack([px, py])
    particles2d.set_offsets(offsets)
    particles2d.set_alpha(0.85 if state["show_particles"] else 0.0)

    for i, sc in enumerate(trail_scatters):
        sc.set_offsets(np.column_stack([trail_x[i], trail_y[i]]))
        sc.set_alpha((((i + 1) / trail_length) * 0.08) if state["show_particles"] else 0.0)

    # 3D update
    drift = np.array([0.010 * frame * speed, 0.0, 0.0])

    psi_scale = get_psi_scale()
    delta_scale = get_delta_scale()

    centers = [
        np.array([2.2 + 0.35*np.sin(1.2*t),  2.2 + 0.15*np.cos(t),     1.3 + 0.25*np.sin(0.8*t)]),
        np.array([2.8 + 0.30*np.cos(0.9*t),  0.2 + 0.22*np.sin(1.1*t), 0.2 + 0.18*np.cos(1.3*t)]),
        np.array([6.6 + 0.18*np.sin(1.0*t), -1.1 + 0.18*np.cos(0.7*t), -0.8 + 0.20*np.sin(0.9*t)]),
        np.array([6.5 + 0.25*np.cos(0.8*t),  3.7 + 0.20*np.sin(0.9*t),  2.7 + 0.15*np.cos(1.0*t)]),
    ]

    yaws = [
        -0.55 + 0.30*np.sin(t),
        -0.35 + 0.25*np.cos(1.2*t),
         0.95 + 0.25*np.sin(0.9*t),
         0.75 + 0.22*np.cos(1.1*t),
    ]

    tilts = [
        0.35*np.sin(0.7*t),
        0.25*np.cos(0.9*t),
        0.40*np.sin(0.8*t),
        0.28*np.cos(0.85*t),
    ]

    sizes = [
        0.42 + 0.05*np.sin(t),
        0.48 + 0.05*np.cos(1.1*t),
        0.54 + 0.04*np.sin(0.8*t),
        0.52 + 0.04*np.cos(0.9*t),
    ]

    for i in range(4):
        c = centers[i] + drift * 0.02
        tri = make_triangle(c, size=sizes[i] * psi_scale, yaw=yaws[i], tilt=tilts[i])
        wire = make_wire_triangle(c, size=(sizes[i] + 0.28), yaw=yaws[i], tilt=tilts[i])

        wedge_polys[i].set_verts([tri])
        wedge_polys[i].set_alpha(1.0)

        wire_lines[i].set_data(wire[:, 0], wire[:, 1])
        wire_lines[i].set_3d_properties(wire[:, 2])
        wire_lines[i].set_alpha(0.7 if state["show_3d_wire"] else 0.0)

    link_targets = [
        centers[1] + np.array([-0.35, 0.1, 0.0]),
        centers[0] + np.array([-0.25, -0.1, 0.0]),
        centers[2] + np.array([-0.45, 0.0, 0.1]),
    ]

    starts = [vertex, g1, g2]

    for i in range(3):
        p0 = starts[i]
        p1 = link_targets[i] + drift * 0.02
        xs = [p0[0], p1[0]]
        ys = [p0[1], p1[1]]
        zs = [p0[2], p1[2]]

        link_lines[i].set_data(xs, ys)
        link_lines[i].set_3d_properties(zs)
        link_lines[i].set_linewidth(1.1 + 0.9 * delta_scale)
        link_lines[i].set_alpha(1.0 if state["show_3d_links"] else 0.0)

    label_alpha = 1.0 if state["show_3d_labels"] else 0.0
    label_vertex.set_alpha(label_alpha)
    label_wedge.set_alpha(label_alpha)
    label_face.set_alpha(label_alpha)
    label_edge.set_alpha(label_alpha)

    ax3d.view_init(elev=24 + 2*np.sin(0.3*t), azim=-64 + 8*np.sin(0.18*t))

    refresh_titles()

    artists = [
        im2d, delta_overlay, quiver2d, particles2d,
        *trail_scatters,
        *wedge_polys, *wire_lines, *link_lines,
        title2d, title3d, info_text,
        label_vertex, label_wedge, label_face, label_edge
    ]
    return artists

# ============================================================
# 17) START
# ============================================================
refresh_titles()

ani = animation.FuncAnimation(
    fig, update, frames=frames, interval=40, blit=False
)

plt.show()