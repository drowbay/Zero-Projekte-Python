import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, CheckButtons

# ============================================================
# MS VIEWER v5.5 — COSMIC MODE
# Gravitation + Rotation + Dark Energy + Cosmic Rays + CMB + Trace Layer
# ============================================================

np.random.seed(7)

G = 1.0
grid_size = 180
space_size = 24.0
num_particles = 220
num_tracers = 520
dt = 0.022
softening = 0.9
frames = 1200
trail_length = 14
step_arrow = 18

dark_energy_strength = 0.010
cmb_alpha_default = 0.075
ray_rate = 7
ray_lifetime = 18

cores = [(0.0, 0.0, 520.0), (-8.0, 6.0, 120.0), (9.0, -7.0, 105.0)]

def normalize(arr):
    arr = np.array(arr, dtype=float)
    arr = arr - np.min(arr)
    return arr / (np.max(arr) + 1e-9)

def unit_vectors(FX, FY):
    n = np.sqrt(FX**2 + FY**2) + 1e-9
    return FX / n, FY / n

x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)
R0 = np.sqrt(X**2 + Y**2 + softening**2)
RX, RY = X / R0, Y / R0

potential = np.zeros_like(X)
gravity_strength = np.zeros_like(X)
GX = np.zeros_like(X)
GY = np.zeros_like(X)
VX = np.zeros_like(X)
VY = np.zeros_like(X)

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
rot_energy = 0.5 * Vmag**2
energy_field = gravity_strength + rot_energy

eta_depth = normalize(np.abs(potential))
gradEx, gradEy = np.gradient(energy_field)
gradE_mag = np.sqrt(gradEx**2 + gradEy**2)
psi_activity = normalize(gradE_mag)

DE_X = RX * dark_energy_strength * R0
DE_Y = RY * dark_energy_strength * R0
DE_mag = normalize(np.sqrt(DE_X**2 + DE_Y**2))

cmb_noise = normalize(np.random.normal(0, 1, (grid_size, grid_size)))
hidden_layer = normalize(0.45 * eta_depth + 0.35 * psi_activity + 0.20 * cmb_noise)
cosmic_field = normalize(0.38 * eta_depth + 0.25 * normalize(energy_field) + 0.22 * DE_mag + 0.15 * cmb_noise)

FLOW_X = normalize(VX) + 0.45 * normalize(GX) + 0.55 * normalize(DE_X)
FLOW_Y = normalize(VY) + 0.45 * normalize(GY) + 0.55 * normalize(DE_Y)
FLOW_X, FLOW_Y = unit_vectors(FLOW_X, FLOW_Y)

Xs = X[::step_arrow, ::step_arrow]
Ys = Y[::step_arrow, ::step_arrow]
FXs = FLOW_X[::step_arrow, ::step_arrow]
FYs = FLOW_Y[::step_arrow, ::step_arrow]

angles = np.random.uniform(0, 2*np.pi, num_particles)
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

tx = np.random.uniform(-space_size, space_size, num_tracers)
ty = np.random.uniform(-space_size, space_size, num_tracers)
tvx = np.zeros(num_tracers)
tvy = np.zeros(num_tracers)
rays = []

def spawn_rays():
    new = []
    for _ in range(ray_rate):
        x0 = np.random.uniform(-space_size, space_size)
        y0 = np.random.uniform(-space_size, space_size)
        ang = np.random.uniform(0, 2*np.pi)
        length = np.random.uniform(1.2, 4.5)
        new.append({"x0": x0, "y0": y0, "x1": x0 + np.cos(ang)*length, "y1": y0 + np.sin(ang)*length, "life": ray_lifetime})
    return new

fig = plt.figure(figsize=(14.5, 9), facecolor="black")
ax = fig.add_axes([0.04, 0.12, 0.70, 0.82], facecolor="black")
ax.axis("off")
ax_ui = fig.add_axes([0.78, 0.08, 0.20, 0.86], facecolor="black")
ax_ui.axis("off")

ax_de = fig.add_axes([0.80, 0.79, 0.16, 0.03], facecolor="dimgray")
ax_cmb = fig.add_axes([0.80, 0.73, 0.16, 0.03], facecolor="dimgray")
ax_trace = fig.add_axes([0.80, 0.67, 0.16, 0.03], facecolor="dimgray")
ax_rays = fig.add_axes([0.80, 0.61, 0.16, 0.03], facecolor="dimgray")
ax_pause = fig.add_axes([0.80, 0.52, 0.07, 0.045])
ax_reset = fig.add_axes([0.89, 0.52, 0.07, 0.045])
ax_checks = fig.add_axes([0.80, 0.31, 0.16, 0.17], facecolor="black")

state = {"paused": False, "show_cmb": True, "show_trace": True, "show_rays": True, "show_arrows": True}

im_base = ax.imshow(cosmic_field, extent=[-space_size, space_size, -space_size, space_size], origin="lower", cmap="magma", alpha=0.90)
im_cmb = ax.imshow(cmb_noise, extent=[-space_size, space_size, -space_size, space_size], origin="lower", cmap="gray", alpha=cmb_alpha_default)
im_hidden = ax.imshow(hidden_layer, extent=[-space_size, space_size, -space_size, space_size], origin="lower", cmap="cool", alpha=0.18)
quiv = ax.quiver(Xs, Ys, FXs, FYs, color="cyan", alpha=0.55, scale=26, width=0.0028, headwidth=4.3, headlength=5.0)

for cx, cy, mass in cores:
    ax.scatter(cx, cy, s=80 + mass * 0.12, c="white", alpha=0.95)

trail_scatters = []
for i in range(trail_length):
    alpha = (i + 1) / trail_length * 0.075
    size = 1.5 + (i / trail_length) * 4
    trail_scatters.append(ax.scatter([], [], s=size, c="white", alpha=alpha))

particles = ax.scatter(px, py, s=7, c="white", alpha=0.88)
tracers = ax.scatter(tx, ty, s=2, c="deepskyblue", alpha=0.34)
ray_lines = []
for _ in range(ray_rate * ray_lifetime):
    line, = ax.plot([], [], color="white", alpha=0.0, linewidth=1.0)
    ray_lines.append(line)

title = ax.text(0, 21.6, "MS VIEWER v5.5 — COSMIC MODE", ha="center", va="center", color="white", fontsize=16, fontweight="bold")
subtitle = ax.text(0, -21.6, "Gravity forms • Dark Energy expands • Cosmic Rays strike • CMB whispers", ha="center", va="center", color="white", fontsize=9, alpha=0.82)

s_de = Slider(ax_de, "Dark E", 0.0, 2.5, valinit=1.0)
s_cmb = Slider(ax_cmb, "CMB", 0.0, 0.25, valinit=cmb_alpha_default)
s_trace = Slider(ax_trace, "Trace", 0.0, 1.0, valinit=0.34)
s_rays = Slider(ax_rays, "Rays", 0.0, 1.0, valinit=0.75)
btn_pause = Button(ax_pause, "Pause")
btn_reset = Button(ax_reset, "Reset")
checks = CheckButtons(ax_checks, ["CMB", "Trace", "Rays", "Arrows"], [True, True, True, True])

ax_ui.text(0.02, 0.98,
    "COSMIC MODE\n────────────────────\n"
    "Orange/Magma:\n  Cosmic composite field\n\n"
    "Cyan arrows:\n  Direction D⃗\n  rotation + gravity + expansion\n\n"
    "Gray noise:\n  CMB background\n\n"
    "Blue dust:\n  Trace particles / field flow\n\n"
    "White streaks:\n  Cosmic ray events\n\n"
    "Violet/Cool overlay:\n  ~0/~1 hidden layer\n\n"
    "MS MAP\nη = gravitational structure\nψ = dynamics / gradient\n~0/~1 = hidden fluctuations\n0/1 = visible particles\nD⃗ = total direction field",
    color="white", fontsize=9.5, ha="left", va="top", family="monospace",
    bbox=dict(facecolor="black", alpha=0.45, edgecolor="gray"))

ax.set_xlim(-space_size, space_size)
ax.set_ylim(-space_size, space_size)

def refresh_ui(val=None):
    im_cmb.set_alpha(s_cmb.val if state["show_cmb"] else 0.0)
    tracers.set_alpha(s_trace.val if state["show_trace"] else 0.0)
    quiv.set_alpha(0.55 if state["show_arrows"] else 0.0)
    fig.canvas.draw_idle()

s_de.on_changed(refresh_ui)
s_cmb.on_changed(refresh_ui)
s_trace.on_changed(refresh_ui)
s_rays.on_changed(refresh_ui)

def toggle_pause(event):
    state["paused"] = not state["paused"]
    btn_pause.label.set_text("Resume" if state["paused"] else "Pause")
btn_pause.on_clicked(toggle_pause)

def reset_view(event):
    s_de.reset(); s_cmb.reset(); s_trace.reset(); s_rays.reset(); refresh_ui()
btn_reset.on_clicked(reset_view)

def on_checks(label):
    if label == "CMB": state["show_cmb"] = not state["show_cmb"]
    elif label == "Trace": state["show_trace"] = not state["show_trace"]
    elif label == "Rays": state["show_rays"] = not state["show_rays"]
    elif label == "Arrows": state["show_arrows"] = not state["show_arrows"]
    refresh_ui()
checks.on_clicked(on_checks)

def update(frame):
    global px, py, pvx, pvy, trail_x, trail_y, tx, ty, tvx, tvy, rays
    if not state["paused"]:
        de_scale = s_de.val
        ax_total = np.zeros(num_particles)
        ay_total = np.zeros(num_particles)
        for cx, cy, mass in cores:
            dx = px - cx; dy = py - cy
            r = np.sqrt(dx**2 + dy**2 + softening**2)
            ax_total += -G * mass * dx / (r**3)
            ay_total += -G * mass * dy / (r**3)
        r_main = np.sqrt(px**2 + py**2 + softening**2)
        ax_total += de_scale * dark_energy_strength * px / r_main
        ay_total += de_scale * dark_energy_strength * py / r_main
        pvx += ax_total * dt; pvy += ay_total * dt
        px += pvx * dt; py += pvy * dt

        r_out = np.sqrt(px**2 + py**2)
        reset = (r_out > 22.5) | (r_out < 1.10)
        if np.any(reset):
            new_angles = np.random.uniform(0, 2*np.pi, np.sum(reset))
            new_radii = np.random.uniform(8.0, 18.0, np.sum(reset))
            px[reset] = new_radii * np.cos(new_angles)
            py[reset] = 0.72 * new_radii * np.sin(new_angles)
            pr = np.sqrt(px[reset]**2 + py[reset]**2 + softening**2)
            v = np.sqrt(G * 520.0 / pr)
            pvx[reset] = -py[reset] / pr * v
            pvy[reset] = px[reset] / pr * v

        trail_x.pop(0); trail_y.pop(0)
        trail_x.append(px.copy()); trail_y.append(py.copy())
        for i, sc in enumerate(trail_scatters):
            sc.set_offsets(np.column_stack([trail_x[i], trail_y[i]]))
        particles.set_offsets(np.column_stack([px, py]))

        tr = np.sqrt(tx**2 + ty**2 + softening**2)
        rot_vx = -ty / tr * np.sqrt(G * 520.0 / tr)
        rot_vy = tx / tr * np.sqrt(G * 520.0 / tr)
        grav_vx = -tx / (tr**2)
        grav_vy = -ty / (tr**2)
        de_vx = de_scale * 0.020 * tx / tr
        de_vy = de_scale * 0.020 * ty / tr
        tvx = 0.85 * tvx + 0.15 * (0.65 * rot_vx + 2.2 * grav_vx + de_vx)
        tvy = 0.85 * tvy + 0.15 * (0.65 * rot_vy + 2.2 * grav_vy + de_vy)
        tx += tvx * dt; ty += tvy * dt
        tr_out = np.sqrt(tx**2 + ty**2)
        treset = tr_out > space_size
        if np.any(treset):
            tx[treset] = np.random.uniform(-space_size, space_size, np.sum(treset))
            ty[treset] = np.random.uniform(-space_size, space_size, np.sum(treset))
            tvx[treset] = 0; tvy[treset] = 0
        tracers.set_offsets(np.column_stack([tx, ty]))

        if state["show_rays"] and np.random.rand() < s_rays.val:
            rays.extend(spawn_rays())
        for ray in rays:
            ray["life"] -= 1
        rays = [r for r in rays if r["life"] > 0]
        for idx, line in enumerate(ray_lines):
            if idx < len(rays) and state["show_rays"]:
                ray = rays[idx]
                alpha = max(0.0, ray["life"] / ray_lifetime) * 0.9
                line.set_data([ray["x0"], ray["x1"]], [ray["y0"], ray["y1"]])
                line.set_alpha(alpha)
            else:
                line.set_data([], [])
                line.set_alpha(0.0)

        scale = 1.0 + 0.008 * np.sin(frame * 0.045)
        ax.set_xlim(-space_size * scale, space_size * scale)
        ax.set_ylim(-space_size * scale, space_size * scale)
        im_hidden.set_alpha(0.14 + 0.06 * np.sin(frame * 0.055))

    return [im_base, im_cmb, im_hidden, quiv, particles, tracers, title, subtitle, *trail_scatters, *ray_lines]

ani = animation.FuncAnimation(fig, update, frames=frames, interval=30, blit=False)
refresh_ui()
plt.show()
