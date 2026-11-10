import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button, CheckButtons
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ============================================================
# MSM + SPINFOAM = ONE UNIFIED ANIMATION
# Peak-Wedges + Delta-Cracks Edition
# ============================================================

np.random.seed(7)

slider_eta = None
slider_psi = None
slider_delta = None
slider_speed = None

# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------
G = 1.0
grid_size = 52
space_size = 16.0
softening = 0.9
frames = 620

cores = [
    (0.0, 0.0, 360.0),
    (-6.0, 5.0, 95.0),
    (7.0, -5.0, 80.0),
]

NUM_WEDGES = 4
PEAK_MIN_DISTANCE = 7
PEAK_CANDIDATES = 100

NUM_CRACK_POINTS = 140
CRACK_THRESHOLD = 0.62

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def normalize(arr):
    arr = np.array(arr, dtype=float)
    arr = arr - np.min(arr)
    return arr / (np.max(arr) + 1e-9)

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

def find_peak_points(field, num_peaks=4, min_dist=7, max_candidates=100):
    flat_idx = np.argsort(field.ravel())[::-1]
    selected = []

    count = 0
    for idx in flat_idx:
        iy, ix = np.unravel_index(idx, field.shape)
        ok = True
        for py, px in selected:
            if (iy - py) ** 2 + (ix - px) ** 2 < min_dist ** 2:
                ok = False
                break
        if ok:
            selected.append((iy, ix))
            if len(selected) >= num_peaks:
                break
        count += 1
        if count >= max_candidates:
            break

    while len(selected) < num_peaks:
        selected.append((field.shape[0] // 2, field.shape[1] // 2))

    return selected

def grid_to_world(ix, iy, zval):
    return np.array([x[ix], y[iy], zval])

def sample_crack_points(delta_field, zfloor, threshold=0.62, max_points=140):
    """
    Nimmt starke Delta-Zonen und gibt Punktkoordinaten im 3D-Raum zurück.
    Keine perfekte Linienverfolgung, aber stabil und gut sichtbar.
    """
    gy, gx = np.gradient(delta_field)
    edge = normalize(np.sqrt(gx**2 + gy**2))

    crack_strength = normalize(0.65 * delta_field + 0.35 * edge)
    mask = crack_strength > threshold

    iy, ix = np.where(mask)
    if len(ix) == 0:
        return np.empty((0, 3))

    vals = crack_strength[iy, ix]
    order = np.argsort(vals)[::-1]

    pts = []
    taken = []

    for k in order:
        py = iy[k]
        px = ix[k]

        ok = True
        for ty, tx in taken:
            if (py - ty) ** 2 + (px - tx) ** 2 < 5:
                ok = False
                break

        if ok:
            wz = zfloor[py, px] + 0.08
            pts.append([x[px], y[py], wz])
            taken.append((py, px))

        if len(pts) >= max_points:
            break

    return np.array(pts)

# ------------------------------------------------------------
# GRID / FIELD
# ------------------------------------------------------------
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
    VY +=  dx / R * v_mag

rot_energy = 0.5 * (VX**2 + VY**2)
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

expansion_driver = normalize(np.clip(gradEx * RX + gradEy * RY, 0, None) + 0.35 * rot_energy)
implosion_driver = normalize(np.clip(-(GX * RX + GY * RY), 0, None) + 0.30 * eta_depth)
phase_feedback = normalize(0.45 * phase_field + 0.30 * structure_flux + 0.25 * eta_depth)

MODELS = {
    1: ("A", normalize(0.55 * expansion_driver + 0.30 * rot_energy + 0.15 * psi_activity), "inferno"),
    2: ("B", normalize(0.50 * phase_field + 0.35 * psi_activity + 0.15 * structure_flux), "viridis"),
    3: ("C", normalize(0.60 * implosion_driver + 0.25 * gravity_strength + 0.15 * eta_depth), "plasma"),
    4: ("D", normalize(0.45 * phase_feedback + 0.35 * structure_flux + 0.20 * psi_activity), "magma"),
    5: ("Ψ", normalize(0.45 * eta_depth + 0.30 * psi_activity + 0.25 * normalize(energy_field)), "twilight"),
}

# ------------------------------------------------------------
# SAFE SLIDER ACCESS
# ------------------------------------------------------------
def get_eta_scale():
    return slider_eta.val if slider_eta is not None else 1.0

def get_psi_scale():
    return slider_psi.val if slider_psi is not None else 1.0

def get_delta_scale():
    return slider_delta.val if slider_delta is not None else 1.0

def get_speed_scale():
    return slider_speed.val if slider_speed is not None else 1.0

def current_scaled_fields(model_id):
    eta_scale = get_eta_scale()
    psi_scale = get_psi_scale()
    delta_scale = get_delta_scale()

    eta_mix = normalize(eta_depth * eta_scale)
    psi_mix = normalize(psi_activity * psi_scale)
    delta_mix = normalize(np.abs(eta_mix - psi_mix) * delta_scale)

    model_field = MODELS[model_id][1]
    base = normalize(0.55 * model_field + 0.25 * eta_mix + 0.20 * psi_mix)
    combined = normalize(0.78 * base + 0.22 * delta_mix)

    return eta_mix, psi_mix, delta_mix, combined

# ------------------------------------------------------------
# 3D STATIC STRUCTURE
# ------------------------------------------------------------
rng = np.random.default_rng(7)

vertex = np.array([0.0, 0.0, 3.4])
g1 = np.array([0.35, 0.95, 3.95])
g2 = np.array([0.45, -0.75, 3.05])

eta_points_3d = np.column_stack([
    rng.uniform(-2.5, 8.0, 80),
    rng.uniform(-1.6, 5.2, 80),
    rng.uniform(2.2, 6.3, 80)
])

face_top = np.array([
    [1.2, 3.7, 5.1],
    [6.8, 4.4, 5.8],
    [7.7, 2.2, 4.1],
    [3.0, 1.5, 3.8],
    [0.9, 2.4, 4.3]
])

face_mid = np.array([
    [0.7, 1.0, 3.7],
    [5.8, 1.6, 4.3],
    [6.8, 0.2, 3.4],
    [3.6, -0.7, 2.7],
    [1.2, -0.1, 3.1]
])

# ------------------------------------------------------------
# STATE
# ------------------------------------------------------------
state = {
    "model": 1,
    "show_wire": True,
    "show_links": True,
    "show_labels": False,
    "show_peaks": True,
    "show_cracks": True,
    "paused": False,
}

# ------------------------------------------------------------
# FIGURE
# ------------------------------------------------------------
fig = plt.figure(figsize=(13, 9), facecolor="black")
ax = fig.add_axes([0.05, 0.26, 0.90, 0.68], projection="3d", facecolor="black")

# ------------------------------------------------------------
# CREATE SLIDERS / BUTTONS
# ------------------------------------------------------------
ax_eta = fig.add_axes([0.08, 0.17, 0.20, 0.03], facecolor="dimgray")
ax_psi = fig.add_axes([0.32, 0.17, 0.20, 0.03], facecolor="dimgray")
ax_delta = fig.add_axes([0.56, 0.17, 0.20, 0.03], facecolor="dimgray")
ax_speed = fig.add_axes([0.08, 0.12, 0.20, 0.03], facecolor="dimgray")

slider_eta = Slider(ax_eta, "η", 0.0, 2.0, valinit=1.0)
slider_psi = Slider(ax_psi, "ψ", 0.0, 2.0, valinit=1.0)
slider_delta = Slider(ax_delta, "Δ", 0.0, 2.0, valinit=1.0)
slider_speed = Slider(ax_speed, "v", 0.1, 2.5, valinit=1.0)

ax_reset = fig.add_axes([0.32, 0.11, 0.10, 0.05])
ax_pause = fig.add_axes([0.45, 0.11, 0.10, 0.05])
btn_reset = Button(ax_reset, "Reset")
btn_pause = Button(ax_pause, "Pause")

ax_checks = fig.add_axes([0.62, 0.06, 0.28, 0.13], facecolor="black")
checks = CheckButtons(ax_checks, ["Wire", "Links", "Labels", "Peaks", "Cracks"], [True, True, False, True, True])
for txt in checks.labels:
    txt.set_color("white")

# ------------------------------------------------------------
# INITIAL FIELD SURFACE
# ------------------------------------------------------------
_, _, delta0, Zfield0 = current_scaled_fields(state["model"])
Zfloor0 = 2.2 * Zfield0 - 1.2

surface = ax.plot_surface(
    X, Y, Zfloor0,
    cmap=MODELS[state["model"]][2],
    linewidth=0,
    antialiased=False,
    alpha=0.92
)

# ------------------------------------------------------------
# 3D OVERLAY OBJECTS
# ------------------------------------------------------------
poly_top = Poly3DCollection([face_top], facecolors="0.95", edgecolors="white", linewidths=1.2, alpha=0.80)
poly_mid = Poly3DCollection([face_mid], facecolors="0.75", edgecolors="white", linewidths=1.2, alpha=0.75)
ax.add_collection3d(poly_top)
ax.add_collection3d(poly_mid)

eta_scatter_3d = ax.scatter(
    eta_points_3d[:, 0], eta_points_3d[:, 1], eta_points_3d[:, 2],
    s=10, facecolors="none", edgecolors="white", linewidths=0.6, alpha=0.55
)

ax.scatter([vertex[0]], [vertex[1]], [vertex[2]], s=36, color="white")
ax.scatter([g1[0], g2[0]], [g1[1], g2[1]], [g1[2], g2[2]], s=14, color="white")

ax.plot([vertex[0], g1[0]], [vertex[1], g1[1]], [vertex[2], g1[2]], color="white", lw=1.0, alpha=0.8)
ax.plot([vertex[0], g2[0]], [vertex[1], g2[1]], [vertex[2], g2[2]], color="white", lw=1.0, alpha=0.8)

wedge_polys = []
wire_lines = []
for _ in range(NUM_WEDGES):
    poly = Poly3DCollection([np.zeros((3, 3))], facecolors="cyan", edgecolors="white", linewidths=1.0, alpha=0.95)
    ax.add_collection3d(poly)
    wedge_polys.append(poly)

    line, = ax.plot([], [], [], color="white", lw=0.9, alpha=0.6)
    wire_lines.append(line)

link_lines = []
for _ in range(3):
    line, = ax.plot([], [], [], color="magenta", lw=1.2, alpha=0.85)
    link_lines.append(line)

peak_scatter = ax.scatter([], [], [], s=26, c="gold", alpha=0.95)
crack_scatter = ax.scatter([], [], [], s=8, c="red", alpha=0.85)

label_vertex = ax.text(-0.55, 0.0, 3.35, "vertex", color="white", fontsize=10)
label_wedge = ax.text(3.7, 0.6, 3.75, "peak wedge", color="white", fontsize=10)
label_face = ax.text(7.0, 3.2, 5.4, "spin foam face", color="white", fontsize=10)
label_edge = ax.text(7.0, -0.6, 2.7, "edge", color="white", fontsize=10)

# ------------------------------------------------------------
# AXIS STYLE
# ------------------------------------------------------------
ax.set_xlim(-space_size, space_size)
ax.set_ylim(-space_size, space_size)
ax.set_zlim(-2.5, 7.0)

ax.set_xlabel("X", color="white")
ax.set_ylabel("Y", color="white")
ax.set_zlabel("Z", color="white")
ax.tick_params(colors="white")
ax.view_init(elev=28, azim=-60)

title = ax.set_title("", color="white", fontsize=14)

info_ax = fig.add_axes([0.08, 0.02, 0.84, 0.07], facecolor="black")
info_ax.axis("off")
info_text = info_ax.text(
    0.0, 0.95, "",
    transform=info_ax.transAxes,
    color="white",
    fontsize=10,
    va="top",
    ha="left",
    family="monospace",
)

# ------------------------------------------------------------
# UI HELPERS
# ------------------------------------------------------------
def refresh_text():
    model_letter = MODELS[state["model"]][0]
    title.set_text(f"Unified MSM + Spinfoam | Peak-Wedges + Δ-Risse | Modell {model_letter}")

    info_text.set_text(
        f"Modell={model_letter}   η={get_eta_scale():.2f}   ψ={get_psi_scale():.2f}   Δ={get_delta_scale():.2f}   v={get_speed_scale():.2f}\n"
        f"Wire={state['show_wire']}   Links={state['show_links']}   Labels={state['show_labels']}   Peaks={state['show_peaks']}   Cracks={state['show_cracks']}   Paused={state['paused']}\n"
        "Peak-Wedges = stärkste Feldzonen | Δ-Risse = starke Differenz-/Kantenzonen | Tasten: 1..5 Modell | Space Pause | W Wire | K Links | L Labels | P Peaks | R Cracks"
    )

def on_slider_change(val):
    refresh_text()
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
    state["show_wire"] = True
    state["show_links"] = True
    state["show_labels"] = False
    state["show_peaks"] = True
    state["show_cracks"] = True
    state["paused"] = False
    btn_pause.label.set_text("Pause")
    refresh_text()
    fig.canvas.draw_idle()

btn_reset.on_clicked(reset_all)

def toggle_pause(event):
    state["paused"] = not state["paused"]
    btn_pause.label.set_text("Resume" if state["paused"] else "Pause")
    refresh_text()
    fig.canvas.draw_idle()

btn_pause.on_clicked(toggle_pause)

def on_checks(label):
    if label == "Wire":
        state["show_wire"] = not state["show_wire"]
    elif label == "Links":
        state["show_links"] = not state["show_links"]
    elif label == "Labels":
        state["show_labels"] = not state["show_labels"]
    elif label == "Peaks":
        state["show_peaks"] = not state["show_peaks"]
    elif label == "Cracks":
        state["show_cracks"] = not state["show_cracks"]
    refresh_text()
    fig.canvas.draw_idle()

checks.on_clicked(on_checks)

def on_key(event):
    key = (event.key or "").lower()
    if key in ["1", "2", "3", "4", "5"]:
        state["model"] = int(key)
    elif key == " ":
        state["paused"] = not state["paused"]
        btn_pause.label.set_text("Resume" if state["paused"] else "Pause")
    elif key == "w":
        state["show_wire"] = not state["show_wire"]
    elif key == "k":
        state["show_links"] = not state["show_links"]
    elif key == "l":
        state["show_labels"] = not state["show_labels"]
    elif key == "p":
        state["show_peaks"] = not state["show_peaks"]
    elif key == "r":
        state["show_cracks"] = not state["show_cracks"]

    refresh_text()
    fig.canvas.draw_idle()

fig.canvas.mpl_connect("key_press_event", on_key)

# ------------------------------------------------------------
# ANIMATION
# ------------------------------------------------------------
def update(frame):
    global surface

    speed = get_speed_scale()
    t = frame * 0.05 * speed
    psi_scale = get_psi_scale()
    delta_scale = get_delta_scale()

    if state["paused"]:
        t = getattr(update, "_last_t", t)
    else:
        update._last_t = t

    # MSM floor
    _, _, delta_field, Zfield = current_scaled_fields(state["model"])

    pulse = 0.10 * np.sin(0.8 * t + 0.22 * X) + 0.08 * np.cos(0.7 * t + 0.18 * Y)
    Zfloor = 2.0 * normalize(0.86 * Zfield + 0.14 * normalize(pulse)) - 1.2

    surface.remove()
    surface = ax.plot_surface(
        X, Y, Zfloor,
        cmap=MODELS[state["model"]][2],
        linewidth=0,
        antialiased=False,
        alpha=0.92
    )

    # Peaks
    peaks_ij = find_peak_points(
        Zfield,
        num_peaks=NUM_WEDGES,
        min_dist=PEAK_MIN_DISTANCE,
        max_candidates=PEAK_CANDIDATES
    )

    peak_world_points = []
    for iy, ix in peaks_ij:
        z_here = Zfloor[iy, ix] + 3.0
        peak_world_points.append(grid_to_world(ix, iy, z_here))

    peak_world_points = np.array(peak_world_points)

    if state["show_peaks"]:
        peak_scatter._offsets3d = (
            peak_world_points[:, 0],
            peak_world_points[:, 1],
            peak_world_points[:, 2]
        )
        peak_scatter.set_alpha(0.95)
    else:
        peak_scatter._offsets3d = ([], [], [])
        peak_scatter.set_alpha(0.0)

    # Wedges on peaks
    for i in range(NUM_WEDGES):
        c = peak_world_points[i].copy()
        local_val = Zfield[peaks_ij[i][0], peaks_ij[i][1]]
        size = (0.34 + 0.45 * local_val) * psi_scale
        yaw = np.arctan2(c[1], c[0]) + 0.25 * np.sin(t + i)
        tilt = 0.30 * np.sin(0.7 * t + 0.8 * i)

        tri = make_triangle(c, size=size, yaw=yaw, tilt=tilt)
        wire = make_wire_triangle(c, size=size + 0.24, yaw=yaw, tilt=tilt)

        wedge_polys[i].set_verts([tri])
        wedge_polys[i].set_facecolor(plt.get_cmap(MODELS[state["model"]][2])(0.75))
        wedge_polys[i].set_edgecolor("white")
        wedge_polys[i].set_alpha(0.95)

        wire_lines[i].set_data(wire[:, 0], wire[:, 1])
        wire_lines[i].set_3d_properties(wire[:, 2])
        wire_lines[i].set_alpha(0.6 if state["show_wire"] else 0.0)

    # Links
    link_targets = [peak_world_points[0], peak_world_points[1], peak_world_points[2]]
    starts = [vertex, g1, g2]

    for i in range(3):
        p0 = starts[i]
        p1 = link_targets[i]
        link_lines[i].set_data([p0[0], p1[0]], [p0[1], p1[1]])
        link_lines[i].set_3d_properties([p0[2], p1[2]])
        link_lines[i].set_linewidth(1.2 + 1.0 * delta_scale)
        link_lines[i].set_alpha(0.9 if state["show_links"] else 0.0)

    # Delta cracks
    crack_points = sample_crack_points(
        delta_field,
        Zfloor,
        threshold=CRACK_THRESHOLD,
        max_points=NUM_CRACK_POINTS
    )

    if state["show_cracks"] and len(crack_points) > 0:
        crack_scatter._offsets3d = (
            crack_points[:, 0],
            crack_points[:, 1],
            crack_points[:, 2]
        )
        crack_scatter.set_alpha(0.85)
    else:
        crack_scatter._offsets3d = ([], [], [])
        crack_scatter.set_alpha(0.0)

    # Labels
    label_alpha = 1.0 if state["show_labels"] else 0.0
    label_vertex.set_alpha(label_alpha)
    label_wedge.set_alpha(label_alpha)
    label_face.set_alpha(label_alpha)
    label_edge.set_alpha(label_alpha)

    ax.view_init(elev=28 + 2*np.sin(0.25*t), azim=-60 + 7*np.sin(0.18*t))

    refresh_text()

    return [surface, peak_scatter, crack_scatter, *wedge_polys, *wire_lines, *link_lines, title, info_text]

refresh_text()

ani = FuncAnimation(fig, update, frames=frames, interval=45, blit=False)
plt.show()