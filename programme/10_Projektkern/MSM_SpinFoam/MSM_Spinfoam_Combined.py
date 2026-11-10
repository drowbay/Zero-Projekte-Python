import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, CheckButtons
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ============================================================
# MSM + 3D SPINFOAM COMBINED VIEWER
# Left: 2D MS field viewer
# Right: 3D Sinnform / Spinfoam-inspired animation
# ============================================================

np.random.seed(7)
rng = np.random.default_rng(7)

# ============================================================
# 1) GLOBAL SETTINGS
# ============================================================
G = 1.0
grid_size = 150
space_size = 24.0
num_particles = 180
dt = 0.022
softening = 0.9
step_arrow = 15
trail_length = 12
frames = 1200

cores = [
    (0.0, 0.0, 520.0),
    (-8.0, 6.0, 120.0),
    (9.0, -7.0, 105.0),
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


def short_model_text(model_id):
    return {
        1: "A = Feld lebt im Raum",
        2: "B = Raum besteht aus Feld",
        3: "C = Feld ist Ursprung",
        4: "D = Feld ist Realität",
        5: "Ψ = Emotionales Feld",
    }[model_id]


def short_process_text(process_key):
    return {
        "expansion": "Expansion / Entfaltung",
        "phase": "Phase / Schichtung / Wirbel",
        "implosion": "Implosion / Verdichtung",
        "feedback": "Rückkopplung / Rückwirkung",
        "emotion": "Ψ / Kontakt / Resonanz",
    }[process_key]


def rot_z(a):
    return np.array([
        [np.cos(a), -np.sin(a), 0],
        [np.sin(a), np.cos(a), 0],
        [0, 0, 1],
    ])


def rot_y(a):
    return np.array([
        [np.cos(a), 0, np.sin(a)],
        [0, 1, 0],
        [-np.sin(a), 0, np.cos(a)],
    ])


def make_triangle(center, size=0.4, yaw=0.0, tilt=0.0):
    base = np.array([
        [0.0, 1.0, 0.0],
        [-0.85, -0.75, 0.0],
        [0.85, -0.75, 0.0],
    ]) * size
    R = rot_z(yaw) @ rot_y(tilt)
    pts = base @ R.T
    pts += np.array(center)
    return pts


def make_wire_triangle(center, size=0.7, yaw=0.0, tilt=0.0):
    pts = make_triangle(center, size=size, yaw=yaw, tilt=tilt)
    return np.vstack([pts, pts[0]])


def cloud_points(n, xlim, ylim, zlim):
    xs = rng.uniform(xlim[0], xlim[1], n)
    ys = rng.uniform(ylim[0], ylim[1], n)
    zs = rng.uniform(zlim[0], zlim[1], n)
    return np.column_stack([xs, ys, zs])

# ============================================================
# 3) 2D GRID / MS FIELDS
# ============================================================
x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)
R0 = np.sqrt(X**2 + Y**2 + 1e-9)
RX, RY = X / R0, Y / R0

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
    VY += dx / R * v_mag

Vmag = np.sqrt(VX**2 + VY**2) + 1e-9
rot_energy = 0.5 * (Vmag**2)
energy_field = gravity_strength + rot_energy

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

radial_energy = gradEx * RX + gradEy * RY
expansion_driver = normalize(np.clip(radial_energy, 0, None) + 0.35 * rot_energy)

radial_gravity_inward = -(GX * RX + GY * RY)
implosion_driver = normalize(np.clip(radial_gravity_inward, 0, None) + 0.30 * eta_depth)

phase_feedback = normalize(0.45 * phase_field + 0.30 * structure_flux + 0.25 * eta_depth)
distance_factor = normalize(1 / (np.sqrt(X**2 + Y**2 + softening**2)))
energy_norm = normalize(energy_field)
contact_noise = normalize(np.random.uniform(0.8, 1.2, energy_field.shape))
psi_emotional = normalize(0.50 * distance_factor + 0.30 * energy_norm + 0.20 * contact_noise)
psi_spark = np.where(psi_emotional > 0.65, psi_emotional, 0.0)

EXPX, EXPY = RX * (0.3 + expansion_driver), RY * (0.3 + expansion_driver)
IMPX, IMPY = -RX * (0.3 + implosion_driver), -RY * (0.3 + implosion_driver)
PHX, PHY = -RY * (0.3 + phase_field), RX * (0.3 + phase_field)
FBX = normalize(gradEx) - normalize(GX)
FBY = normalize(gradEy) - normalize(GY)
FBX, FBY = unit_vectors(FBX, FBY)
EMOX, EMOY = unit_vectors(gradEx + RX, gradEy + RY)

PROCESS_ARROWS = {
    "expansion": (EXPX, EXPY, "gold"),
    "phase": (PHX, PHY, "cyan"),
    "implosion": (IMPX, IMPY, "deepskyblue"),
    "feedback": (FBX, FBY, "violet"),
    "emotion": (EMOX, EMOY, "magenta"),
}

model_A = {
    "expansion": normalize(0.55 * expansion_driver + 0.30 * rot_energy + 0.15 * psi_activity),
    "phase": normalize(0.50 * phase_field + 0.35 * psi_activity + 0.15 * structure_flux),
    "implosion": normalize(0.60 * implosion_driver + 0.25 * gravity_strength + 0.15 * eta_depth),
    "feedback": normalize(0.45 * phase_feedback + 0.35 * structure_flux + 0.20 * psi_activity),
    "emotion": normalize(0.70 * psi_emotional + 0.30 * psi_spark),
}
model_B = {
    "expansion": normalize(0.35 * expansion_driver + 0.40 * eta_depth + 0.25 * psi_activity),
    "phase": normalize(0.30 * phase_field + 0.45 * eta_depth + 0.25 * structure_flux),
    "implosion": normalize(0.35 * implosion_driver + 0.45 * eta_depth + 0.20 * gravity_strength),
    "feedback": normalize(0.30 * phase_feedback + 0.45 * eta_depth + 0.25 * structure_flux),
    "emotion": normalize(0.55 * psi_emotional + 0.45 * eta_depth),
}
model_C = {
    "expansion": normalize(0.25 * expansion_driver + 0.50 * eta_depth + 0.25 * phase_field),
    "phase": normalize(0.20 * phase_field + 0.55 * eta_depth + 0.25 * psi_activity),
    "implosion": normalize(0.25 * implosion_driver + 0.55 * eta_depth + 0.20 * structure_flux),
    "feedback": normalize(0.25 * phase_feedback + 0.50 * eta_depth + 0.25 * phase_field),
    "emotion": normalize(0.45 * psi_emotional + 0.25 * eta_depth + 0.30 * psi_activity),
}
model_D = {
    "expansion": normalize(0.25 * expansion_driver + 0.25 * eta_depth + 0.25 * phase_field + 0.25 * structure_flux),
    "phase": normalize(0.25 * phase_field + 0.25 * psi_activity + 0.25 * eta_depth + 0.25 * structure_flux),
    "implosion": normalize(0.25 * implosion_driver + 0.25 * gravity_strength + 0.25 * eta_depth + 0.25 * structure_flux),
    "feedback": normalize(0.25 * phase_feedback + 0.25 * eta_depth + 0.25 * phase_field + 0.25 * structure_flux),
    "emotion": normalize(0.35 * psi_emotional + 0.20 * eta_depth + 0.20 * psi_activity + 0.25 * psi_spark),
}
model_PSI = {
    "expansion": normalize(0.60 * psi_emotional + 0.20 * expansion_driver + 0.20 * psi_spark),
    "phase": normalize(0.60 * psi_emotional + 0.20 * phase_field + 0.20 * psi_spark),
    "implosion": normalize(0.60 * psi_emotional + 0.20 * implosion_driver + 0.20 * psi_spark),
    "feedback": normalize(0.60 * psi_emotional + 0.20 * phase_feedback + 0.20 * psi_spark),
    "emotion": normalize(0.75 * psi_emotional + 0.25 * psi_spark),
}

MODELS = {
    1: ("A", "Konservativ: Feld lebt im Raum", model_A),
    2: ("B", "Raum besteht aus Feld", model_B),
    3: ("C", "Feld ist Ursprung", model_C),
    4: ("D", "Feld ist Realität", model_D),
    5: ("Ψ", "Emotionales Feld / Resonanz", model_PSI),
}
PROCESSES = {
    1: ("expansion", "Expansion"),
    2: ("phase", "Phasenstruktur"),
    3: ("implosion", "Implosion"),
    4: ("feedback", "Phasenrückkopplung"),
    5: ("emotion", "Ψ Emotional"),
}
CMAPS = {
    "expansion": "inferno",
    "phase": "viridis",
    "implosion": "plasma",
    "feedback": "magma",
    "emotion": "twilight",
}

Xs = X[::step_arrow, ::step_arrow]
Ys = Y[::step_arrow, ::step_arrow]
ARROW_CACHE = {}
for key, (FX, FY, _) in PROCESS_ARROWS.items():
    FXs = FX[::step_arrow, ::step_arrow]
    FYs = FY[::step_arrow, ::step_arrow]
    ARROW_CACHE[key] = unit_vectors(FXs, FYs)

# ============================================================
# 4) PARTICLES FOR 2D VIEW
# ============================================================
angles = np.random.uniform(0, 2 * np.pi, num_particles)
radii = np.random.uniform(4.0, 18.0, num_particles)
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
        vy_sum += dx / r * v
    pvx[i] = vx_sum
    pvy[i] = vy_sum

pvx += np.random.normal(0, 0.03, num_particles)
pvy += np.random.normal(0, 0.03, num_particles)
trail_x = [px.copy() for _ in range(trail_length)]
trail_y = [py.copy() for _ in range(trail_length)]

# ============================================================
# 5) FIGURE / AXES
# ============================================================
fig = plt.figure(figsize=(16, 10), facecolor="black")
ax_left = fig.add_axes([0.04, 0.28, 0.47, 0.66], facecolor="black")
ax_right = fig.add_axes([0.55, 0.28, 0.40, 0.66], projection="3d")
ax_bottom = fig.add_axes([0.04, 0.05, 0.91, 0.18], facecolor="black")
ax_bottom.axis("off")

# slider axes
ax_eta = fig.add_axes([0.93, 0.83, 0.015, 0.10], facecolor="dimgray")
ax_psi = fig.add_axes([0.955, 0.83, 0.015, 0.10], facecolor="dimgray")
ax_delta = fig.add_axes([0.93, 0.69, 0.015, 0.10], facecolor="dimgray")
ax_speed = fig.add_axes([0.955, 0.69, 0.015, 0.10], facecolor="dimgray")
ax_reset = fig.add_axes([0.925, 0.59, 0.045, 0.04])
ax_pause = fig.add_axes([0.925, 0.54, 0.045, 0.04])
ax_checks = fig.add_axes([0.915, 0.31, 0.08, 0.18], facecolor="black")

state = {
    "model": 5,
    "process": 5,
    "show_particles": True,
    "show_labels_3d": False,
    "show_links_3d": True,
    "show_wire_3d": True,
    "paused": False,
}

# ============================================================
# 6) 2D PANEL SETUP
# ============================================================
def current_field_data():
    model_id = state["model"]
    process_id = state["process"]
    process_key = PROCESSES[process_id][0]
    data = MODELS[model_id][2][process_key]
    return data, process_key


def current_scaled_fields():
    eta_scale = slider_eta.val
    psi_scale = slider_psi.val
    delta_scale = slider_delta.val
    eta_mix = normalize(eta_depth * eta_scale)
    psi_mix = normalize(psi_activity * psi_scale)
    delta_hint = normalize(np.abs(psi_mix - eta_mix)) * delta_scale
    return eta_mix, psi_mix, delta_hint


eta_mix0, psi_mix0, delta0 = current_scaled_fields()
data0, process_key0 = current_field_data()
base0 = normalize(0.62 * data0 + 0.20 * eta_mix0 + 0.18 * psi_mix0)

im2d = ax_left.imshow(
    base0,
    extent=[-space_size, space_size, -space_size, space_size],
    origin="lower",
    cmap=CMAPS[process_key0],
    alpha=0.98,
)

delta_overlay = ax_left.imshow(
    delta0,
    extent=[-space_size, space_size, -space_size, space_size],
    origin="lower",
    cmap="coolwarm",
    alpha=0.24,
    vmin=0.0,
    vmax=1.0,
)

U0, V0 = ARROW_CACHE[process_key0]
quiv2d = ax_left.quiver(
    Xs, Ys, U0, V0,
    color=PROCESS_ARROWS[process_key0][2],
    alpha=0.82, scale=24, width=0.0031,
    headwidth=4.6, headlength=5.2, headaxislength=4.9,
)

ring_angles = np.linspace(0, 2*np.pi, 300)
ring1, = ax_left.plot(2.2*np.cos(ring_angles), 2.2*np.sin(ring_angles), linewidth=1.0, alpha=0.10, color="white")
ring2, = ax_left.plot(4.0*np.cos(ring_angles), 4.0*np.sin(ring_angles), linewidth=0.8, alpha=0.08, color="white")

trail_scatters = []
for i in range(trail_length):
    alpha = (i + 1) / trail_length * 0.08
    size = 1.5 + (i / trail_length) * 4
    sc = ax_left.scatter([], [], s=size, c="white", alpha=alpha)
    trail_scatters.append(sc)
particles2d = ax_left.scatter(px, py, s=8, c="white", alpha=0.84)

ax_left.set_xlim(-space_size, space_size)
ax_left.set_ylim(-space_size, space_size)
ax_left.tick_params(colors="white")
left_title = ax_left.set_title("", color="white", fontsize=13)
left_legend = ax_left.text(
    0.02, 0.02, "",
    transform=ax_left.transAxes,
    color="white", fontsize=8.5, va="bottom",
    bbox=dict(facecolor="black", alpha=0.36, edgecolor="gray"),
)

# ============================================================
# 7) 3D SINNFORM SETUP
# ============================================================
vertex = np.array([0.0, 0.0, 0.0])
g1 = np.array([0.35, 0.95, 0.55])
g2 = np.array([0.45, -0.75, -0.35])
eta_points = cloud_points(180, (-2.5, 8.0), (-1.6, 5.2), (-1.8, 3.8))

face_top = np.array([
    [1.2, 3.7, 2.2], [6.8, 4.4, 2.9], [7.7, 2.2, 1.2], [3.0, 1.5, 0.9], [0.9, 2.4, 1.4]
])
face_mid = np.array([
    [0.7, 1.0, 0.4], [5.8, 1.6, 1.0], [6.8, 0.2, 0.1], [3.6, -0.7, -0.6], [1.2, -0.1, -0.2]
])

ax_right.set_facecolor("white")
poly_top = Poly3DCollection([face_top], facecolors="0.95", edgecolors="black", linewidths=1.5, alpha=1.0)
poly_mid = Poly3DCollection([face_mid], facecolors="0.88", edgecolors="black", linewidths=1.5, alpha=1.0)
ax_right.add_collection3d(poly_top)
ax_right.add_collection3d(poly_mid)

eta_scatter = ax_right.scatter(
    eta_points[:, 0], eta_points[:, 1], eta_points[:, 2],
    s=14, facecolors="none", edgecolors="0.4", linewidths=0.7, alpha=0.75
)
ax_right.scatter([vertex[0]], [vertex[1]], [vertex[2]], s=40, color="black")
ax_right.scatter([g1[0], g2[0]], [g1[1], g2[1]], [g1[2], g2[2]], s=18, color="black")
ax_right.plot([vertex[0], g1[0]], [vertex[1], g1[1]], [vertex[2], g1[2]], color="black", lw=1.3)
ax_right.plot([vertex[0], g2[0]], [vertex[1], g2[1]], [vertex[2], g2[2]], color="black", lw=1.3)

wedge_polys = []
wire_lines = []
link_lines = []
for _ in range(4):
    poly = Poly3DCollection([np.zeros((3, 3))], facecolors="0.2", edgecolors="black", linewidths=1.0, alpha=1.0)
    ax_right.add_collection3d(poly)
    wedge_polys.append(poly)
    line, = ax_right.plot([], [], [], color="0.5", lw=1.0, alpha=0.7)
    wire_lines.append(line)
for _ in range(3):
    line, = ax_right.plot([], [], [], color="0.25", lw=1.2)
    link_lines.append(line)

label_artists = [
    ax_right.text(7.0, 3.2, 2.5, "spin foam face", fontsize=12, visible=False),
    ax_right.text(3.7, 0.6, 0.4, "wedge", fontsize=12, visible=False),
    ax_right.text(-0.55, 0.0, 0.0, "vertex", fontsize=12, visible=False),
    ax_right.text(7.0, -0.6, -0.5, "edge", fontsize=12, visible=False),
]

ax_right.set_xlim(-1.2, 8.4)
ax_right.set_ylim(-2.2, 5.3)
ax_right.set_zlim(-2.2, 4.0)
ax_right.set_xlabel("X")
ax_right.set_ylabel("Y")
ax_right.set_zlabel("Z")
ax_right.view_init(elev=24, azim=-64)
right_title = ax_right.set_title("MSM 3D Sinnform", fontsize=13)

# ============================================================
# 8) UI WIDGETS
# ============================================================
slider_eta = Slider(ax_eta, "η", 0.0, 2.0, valinit=1.0, orientation="vertical")
slider_psi = Slider(ax_psi, "ψ", 0.0, 2.0, valinit=1.0, orientation="vertical")
slider_delta = Slider(ax_delta, "Δ", 0.0, 2.0, valinit=1.0, orientation="vertical")
slider_speed = Slider(ax_speed, "v", 0.2, 2.5, valinit=1.0, orientation="vertical")
btn_reset = Button(ax_reset, "Reset")
btn_pause = Button(ax_pause, "Pause")
checks = CheckButtons(ax_checks, ["Particles", "3D Links", "3D Wire", "3D Labels"], [True, True, True, False])
for txt in checks.labels:
    txt.set_color("white")
for line in checks.lines:
    for artist in line:
        artist.set_color("white")

# ============================================================
# 9) TEXT BOXES
# ============================================================
info_box = ax_bottom.text(
    0.01, 0.95,
    "",
    transform=ax_bottom.transAxes,
    color="white", fontsize=10, va="top",
    family="monospace",
    bbox=dict(facecolor="black", alpha=0.40, edgecolor="gray", boxstyle="round,pad=0.55"),
)

controls_box = ax_bottom.text(
    0.99, 0.05,
    "Tasten:\n1..5 = Modell | Q..T = Prozess\nLeertaste = Pause | L = 3D Labels\nP = Partikel | K = 3D Links | W = 3D Wire",
    transform=ax_bottom.transAxes,
    color="white", fontsize=9, va="bottom", ha="right",
    bbox=dict(facecolor="black", alpha=0.40, edgecolor="gray", boxstyle="round,pad=0.55"),
)

# ============================================================
# 10) UPDATE HELPERS
# ============================================================
def update_texts():
    model_letter, model_name, _ = MODELS[state["model"]]
    process_key, process_name = PROCESSES[state["process"]]
    left_title.set_text(f"2D MS Viewer | Modell {model_letter}: {model_name} | Prozess: {process_name}")
    left_legend.set_text(
        f"{short_model_text(state['model'])}\n"
        f"{short_process_text(process_key)}\n"
        f"η={slider_eta.val:.2f} | ψ={slider_psi.val:.2f} | Δ={slider_delta.val:.2f} | v={slider_speed.val:.2f}"
    )
    right_title.set_text(f"3D Sinnform | {model_letter} / {process_name}")
    info_box.set_text(
        "MSM + 3D Spinfoam Combined\n"
        "────────────────────────────\n"
        f"Modell: {model_letter} = {model_name}\n"
        f"Prozess: {process_name}\n"
        f"η steuert Grundstruktur / Punktwolke\n"
        f"ψ steuert Wedge-Größe / Dynamik\n"
        f"Δ steuert Links / Differenzstärke\n"
        "Links = 2D Feldsicht, rechts = 3D Sinnform"
    )


def refresh_static_views():
    eta_mix, psi_mix, delta_hint = current_scaled_fields()
    data, process_key = current_field_data()
    base = normalize(0.62 * data + 0.20 * eta_mix + 0.18 * psi_mix)
    im2d.set_array(base)
    im2d.set_cmap(CMAPS[process_key])
    delta_overlay.set_array(delta_hint)
    delta_overlay.set_alpha(0.24 + 0.10 * min(1.0, slider_delta.val / 2.0))
    U, V = ARROW_CACHE[process_key]
    quiv2d.set_UVC(U, V)
    quiv2d.set_color(PROCESS_ARROWS[process_key][2])
    particles2d.set_alpha(0.84 if state["show_particles"] else 0.0)
    eta_scatter.set_alpha(0.25 + 0.55 * min(1.0, slider_eta.val / 2.0))
    for text in label_artists:
        text.set_visible(state["show_labels_3d"])
    update_texts()
    fig.canvas.draw_idle()

# ============================================================
# 11) CALLBACKS
# ============================================================
def on_slider_change(val):
    refresh_static_views()

for s in [slider_eta, slider_psi, slider_delta, slider_speed]:
    s.on_changed(on_slider_change)


def reset_all(event):
    slider_eta.reset()
    slider_psi.reset()
    slider_delta.reset()
    slider_speed.reset()
    state["show_particles"] = True
    state["show_labels_3d"] = False
    state["show_links_3d"] = True
    state["show_wire_3d"] = True
    state["paused"] = False
    btn_pause.label.set_text("Pause")
    refresh_static_views()

btn_reset.on_clicked(reset_all)


def toggle_pause(event):
    state["paused"] = not state["paused"]
    btn_pause.label.set_text("Resume" if state["paused"] else "Pause")

btn_pause.on_clicked(toggle_pause)


def on_checks(label):
    if label == "Particles":
        state["show_particles"] = not state["show_particles"]
    elif label == "3D Links":
        state["show_links_3d"] = not state["show_links_3d"]
    elif label == "3D Wire":
        state["show_wire_3d"] = not state["show_wire_3d"]
    elif label == "3D Labels":
        state["show_labels_3d"] = not state["show_labels_3d"]
    refresh_static_views()

checks.on_clicked(on_checks)


def on_key(event):
    key = (event.key or "").lower()
    if key in {"1", "2", "3", "4", "5"}:
        state["model"] = int(key)
        refresh_static_views()
    elif key in {"q", "w", "e", "r", "t"}:
        proc_map = {"q": 1, "w": 2, "e": 3, "r": 4, "t": 5}
        state["process"] = proc_map[key]
        refresh_static_views()
    elif key == " ":
        state["paused"] = not state["paused"]
        btn_pause.label.set_text("Resume" if state["paused"] else "Pause")
    elif key == "l":
        state["show_labels_3d"] = not state["show_labels_3d"]
        refresh_static_views()
    elif key == "p":
        state["show_particles"] = not state["show_particles"]
        refresh_static_views()
    elif key == "k":
        state["show_links_3d"] = not state["show_links_3d"]
        refresh_static_views()
    elif key == "w":
        state["show_wire_3d"] = not state["show_wire_3d"]
        refresh_static_views()

fig.canvas.mpl_connect("key_press_event", on_key)

# ============================================================
# 12) ANIMATION UPDATE
# ============================================================
def update(frame):
    global px, py, pvx, pvy, trail_x, trail_y

    speed = slider_speed.val
    t = frame * 0.055 * speed
    eta_scale = slider_eta.val
    psi_scale = slider_psi.val
    delta_scale = slider_delta.val

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
        reset = (r_out > 22.0) | (r_out < 1.15)
        if np.any(reset):
            new_angles = np.random.uniform(0, 2*np.pi, np.sum(reset))
            new_radii = np.random.uniform(8.0, 18.0, np.sum(reset))
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
    for i, sc in enumerate(trail_scatters):
        sc.set_offsets(np.column_stack([trail_x[i], trail_y[i]]))
        sc.set_alpha((((i + 1) / trail_length) * 0.08) if state["show_particles"] else 0.0)

    ring1.set_alpha(0.08 + 0.05 * np.sin(frame * 0.12 * speed))
    ring2.set_alpha(0.06 + 0.04 * np.sin(frame * 0.08 * speed + 0.6))

    # 3D Sinnform dynamic part, driven by same process/model sliders
    process_key = PROCESSES[state["process"]][0]
    process_weight = {
        "expansion": 1.00,
        "phase": 0.92,
        "implosion": 1.08,
        "feedback": 0.98,
        "emotion": 0.88,
    }[process_key]
    drift = np.array([0.020 * frame * speed, 0.0, 0.0])

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
        (0.42 + 0.05*np.sin(t)) * psi_scale * process_weight,
        (0.48 + 0.05*np.cos(1.1*t)) * psi_scale * process_weight,
        (0.54 + 0.04*np.sin(0.8*t)) * psi_scale * process_weight,
        (0.52 + 0.04*np.cos(0.9*t)) * psi_scale * process_weight,
    ]

    for i in range(4):
        c = centers[i] + drift * 0.02
        tri = make_triangle(c, size=max(0.12, sizes[i]), yaw=yaws[i], tilt=tilts[i])
        wire = make_wire_triangle(c, size=max(0.18, sizes[i] + 0.28), yaw=yaws[i], tilt=tilts[i])
        wedge_polys[i].set_verts([tri])
        wedge_polys[i].set_alpha(0.55 + 0.35 * min(1.0, psi_scale / 2.0))
        wire_lines[i].set_data(wire[:, 0], wire[:, 1])
        wire_lines[i].set_3d_properties(wire[:, 2])
        wire_lines[i].set_alpha(0.7 if state["show_wire_3d"] else 0.0)

    link_targets = [
        centers[1] + np.array([-0.35, 0.1, 0.0]),
        centers[0] + np.array([-0.25, -0.1, 0.0]),
        centers[2] + np.array([-0.45, 0.0, 0.1]),
    ]
    starts = [vertex, g1, g2]
    for i in range(3):
        p0 = starts[i]
        p1 = link_targets[i] + drift * 0.02
        link_lines[i].set_data([p0[0], p1[0]], [p0[1], p1[1]])
        link_lines[i].set_3d_properties([p0[2], p1[2]])
        link_lines[i].set_linewidth(0.8 + 1.6 * delta_scale)
        link_lines[i].set_alpha(0.9 if state["show_links_3d"] else 0.0)

    ax_right.view_init(elev=24 + 2*np.sin(0.3*t), azim=-64 + 8*np.sin(0.18*t))

    return [
        im2d, delta_overlay, quiv2d, particles2d, ring1, ring2,
        *trail_scatters, *wedge_polys, *wire_lines, *link_lines,
        left_title, right_title, left_legend, info_box,
    ]

# ============================================================
# 13) START
# ============================================================
refresh_static_views()
ani = animation.FuncAnimation(fig, update, frames=frames, interval=30, blit=False)
plt.show()
