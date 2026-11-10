import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
from matplotlib.widgets import Cursor

"""
=====================================================================
SPACE FIELD VIEWER — SPLIT-SCREEN VERGLEICHSMODELL v4 + NEBULA LAYER
=====================================================================

Basis: Weiterentwicklung des vom User hochgeladenen v3-Scripts.
Neu:
- Nibulum-/Nebula-SpaceLayer (hier als Nebula interpretiert)
- reale, daten-inspirierte Kosmos-Spezifikationen als Konstanten
- zusätzlicher Overlay-Modus über beiden Panels
- Info-Box mit CMB / Magnetfeld / Nebeltypen

STEUERUNG ZUSÄTZLICH
--------------------
N -> Nebula Overlay an/aus
B -> Nebula Alpha hoch
V -> Nebula Alpha runter
J -> Nebula Modus zyklisch wechseln

NEBULA MODI
-----------
1 = Emissionsnebel
2 = Reflexionsnebel
3 = Dunkelnebel / Absorption
4 = Magnetische Inseln / Schichtfilamente
"""

np.random.seed(7)

# ============================================================
# 1) REAL-DATA-INSPIRED COSMIC SPECS
#    (Konstanten, nicht Live-Datendownload)
# ============================================================
CMB_TEMP_K = 2.725          # NASA/COBE FIRAS blackbody temperature
CMB_ANISO_LEVEL = 1e-5      # ESA Planck / COBE anisotropy order of magnitude
B_ISM_UG = 4.0              # typische interstellare Größenordnung ~3-4 microgauss
B_GALAXY_TOTAL_UG = 10.0    # typische spirale Galaxie equipartition field strength
B_DENSE_NEBULA_UG = 80.0    # obere Größenordnung dichter Nebel/Flame-Nebula Studie

# ============================================================
# 2) GRUNDPARAMETER
# ============================================================
G = 1.0
grid_size = 180
space_size = 26.0
num_particles = 240
dt = 0.022
softening = 0.9
step_arrow = 18

cores = [
    (0.0, 0.0, 520.0),
    (-8.0, 6.0, 120.0),
    (9.0, -7.0, 105.0),
]

# ============================================================
# 3) HILFSFUNKTIONEN
# ============================================================
def normalize(arr: np.ndarray) -> np.ndarray:
    arr = np.array(arr, dtype=float)
    arr = arr - np.min(arr)
    return arr / (np.max(arr) + 1e-9)


def unit_vectors(FX: np.ndarray, FY: np.ndarray):
    n = np.sqrt(FX**2 + FY**2) + 1e-9
    return FX / n, FY / n


def short_model_text(model_id: int) -> str:
    return {
        1: "A = Feld lebt im Raum",
        2: "B = Raum besteht aus Feld",
        3: "C = Feld ist Ursprung",
        4: "D = Feld ist Realität",
    }[model_id]


def short_process_text(process_key: str) -> str:
    return {
        "expansion": "Expansion / Entfaltung",
        "phase": "Phase / Schichtung / Wirbel",
        "implosion": "Implosion / Verdichtung",
        "feedback": "Rückkopplung / Rückwirkung",
    }[process_key]


def model_weights_text(model_id: int) -> str:
    return {
        1: "A priorisiert Dynamik im Raum.",
        2: "B priorisiert Feldhaftigkeit des Raums.",
        3: "C priorisiert Ursprung / Tiefe η.",
        4: "D priorisiert gleichmäßige Ganzheit.",
    }[model_id]


def nebula_mode_name(mode: int) -> str:
    return {
        1: "Emissionsnebel",
        2: "Reflexionsnebel",
        3: "Dunkelnebel",
        4: "Magnetische Inseln",
    }[mode]


# ============================================================
# 4) GITTER / RAUM
# ============================================================
x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)
R0 = np.sqrt(X**2 + Y**2) + 1e-9
RX, RY = X / R0, Y / R0

# ============================================================
# 5) BASISFELDER
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
    VY += dx / R * v_mag

Gmag = np.sqrt(GX**2 + GY**2) + 1e-9
Vmag = np.sqrt(VX**2 + VY**2) + 1e-9
rot_energy = 0.5 * (Vmag**2)
energy_field = gravity_strength + rot_energy

# ============================================================
# 6) ABGELEITETE FELDER
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

radial_energy = gradEx * RX + gradEy * RY
expansion_driver = normalize(np.clip(radial_energy, 0, None) + 0.35 * rot_energy)

radial_gravity_inward = -(GX * RX + GY * RY)
implosion_driver = normalize(np.clip(radial_gravity_inward, 0, None) + 0.30 * eta_depth)

phase_feedback = normalize(0.45 * phase_field + 0.30 * structure_flux + 0.25 * eta_depth)

# ============================================================
# 7) PROZESS-RICHTUNGEN
# ============================================================
EXPX, EXPY = RX * (0.3 + expansion_driver), RY * (0.3 + expansion_driver)
IMPX, IMPY = -RX * (0.3 + implosion_driver), -RY * (0.3 + implosion_driver)
PHX, PHY = -RY * (0.3 + phase_field), RX * (0.3 + phase_field)
FBX = normalize(gradEx) - normalize(GX)
FBY = normalize(gradEy) - normalize(GY)
FBX, FBY = unit_vectors(FBX, FBY)

PROCESS_ARROWS = {
    "expansion": (EXPX, EXPY, "gold"),
    "phase": (PHX, PHY, "cyan"),
    "implosion": (IMPX, IMPY, "deepskyblue"),
    "feedback": (FBX, FBY, "violet"),
}

# ============================================================
# 8) NEBULA SPACE LAYER (DATA-INSPIRED)
# ============================================================
# NASA nebulae: emission / reflection / dark. Magnetic filaments inspired by Webb.
# Scale magnetic influence into a 0..1 control factor from typical ISM to dense nebula.
B_factor = np.clip((B_GALAXY_TOTAL_UG - B_ISM_UG) / max(B_DENSE_NEBULA_UG - B_ISM_UG, 1e-9), 0, 1)

# Dust-like medium
nebula_dust = normalize(0.50 * eta_depth + 0.30 * structure_flux + 0.20 * (1 - normalize(Vmag)))

# Emission nebula -> ionized gas & energetic regions
nebula_emission = normalize(0.50 * phase_field + 0.30 * psi_activity + 0.20 * expansion_driver)

# Reflection nebula -> illuminated dust / reflected starlight
star_glow = np.zeros_like(X, dtype=float)
for cx, cy, mass in cores:
    d = np.sqrt((X - cx)**2 + (Y - cy)**2 + 1.4)
    star_glow += (mass / np.max([c[2] for c in cores])) / d
star_glow = normalize(star_glow)
nebula_reflection = normalize(0.60 * nebula_dust + 0.40 * star_glow)

# Dark nebula -> absorption dominates emission/reflection
nebula_dark = normalize(0.70 * nebula_dust + 0.30 * (1 - star_glow))

# Magnetic islands / layered filaments inspired by Webb / interstellar magnetic structure
magnetic_filaments = normalize(np.abs(np.gradient(GX, axis=0)) + np.abs(np.gradient(GY, axis=1)))
magnetic_islands = normalize((1 - B_factor) * phase_field + B_factor * (0.55 * magnetic_filaments + 0.45 * structure_flux))

NEBULA_FIELDS = {
    1: (nebula_emission, "turbo"),
    2: (nebula_reflection, "Blues_r"),
    3: (nebula_dark, "Greys"),
    4: (magnetic_islands, "cubehelix"),
}

# ============================================================
# 9) VERGLEICHSMODELLE
# ============================================================
model_A = {
    "expansion": normalize(0.55 * expansion_driver + 0.30 * rot_energy + 0.15 * psi_activity),
    "phase": normalize(0.50 * phase_field + 0.35 * psi_activity + 0.15 * structure_flux),
    "implosion": normalize(0.60 * implosion_driver + 0.25 * gravity_strength + 0.15 * eta_depth),
    "feedback": normalize(0.45 * phase_feedback + 0.35 * structure_flux + 0.20 * psi_activity),
}

model_B = {
    "expansion": normalize(0.35 * expansion_driver + 0.40 * eta_depth + 0.25 * psi_activity),
    "phase": normalize(0.30 * phase_field + 0.45 * eta_depth + 0.25 * structure_flux),
    "implosion": normalize(0.35 * implosion_driver + 0.45 * eta_depth + 0.20 * gravity_strength),
    "feedback": normalize(0.30 * phase_feedback + 0.45 * eta_depth + 0.25 * structure_flux),
}

model_C = {
    "expansion": normalize(0.25 * expansion_driver + 0.50 * eta_depth + 0.25 * phase_field),
    "phase": normalize(0.20 * phase_field + 0.55 * eta_depth + 0.25 * psi_activity),
    "implosion": normalize(0.25 * implosion_driver + 0.55 * eta_depth + 0.20 * structure_flux),
    "feedback": normalize(0.25 * phase_feedback + 0.50 * eta_depth + 0.25 * phase_field),
}

model_D = {
    "expansion": normalize(0.25 * expansion_driver + 0.25 * eta_depth + 0.25 * phase_field + 0.25 * structure_flux),
    "phase": normalize(0.25 * phase_field + 0.25 * psi_activity + 0.25 * eta_depth + 0.25 * structure_flux),
    "implosion": normalize(0.25 * implosion_driver + 0.25 * gravity_strength + 0.25 * eta_depth + 0.25 * structure_flux),
    "feedback": normalize(0.25 * phase_feedback + 0.25 * eta_depth + 0.25 * phase_field + 0.25 * structure_flux),
}

MODELS = {
    1: ("A", "Konservativ: Feld lebt im Raum", model_A),
    2: ("B", "Raum besteht aus Feld", model_B),
    3: ("C", "Feld ist Ursprung", model_C),
    4: ("D", "Feld ist Realität", model_D),
}

PROCESSES = {
    1: ("expansion", "Expansion"),
    2: ("phase", "Phasenstruktur"),
    3: ("implosion", "Implosion"),
    4: ("feedback", "Phasenrückkopplung"),
}

CMAPS = {
    "expansion": "inferno",
    "phase": "viridis",
    "implosion": "plasma",
    "feedback": "magma",
}

# ============================================================
# 10) PFEILFELD-CACHE
# ============================================================
Xs = X[::step_arrow, ::step_arrow]
Ys = Y[::step_arrow, ::step_arrow]

ARROW_CACHE = {}
for key, (FX, FY, _) in PROCESS_ARROWS.items():
    FXs = FX[::step_arrow, ::step_arrow]
    FYs = FY[::step_arrow, ::step_arrow]
    ARROW_CACHE[key] = unit_vectors(FXs, FYs)

# ============================================================
# 11) TESTTEILCHEN
# ============================================================
angles = np.random.uniform(0, 2 * np.pi, num_particles)
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
        vy_sum += dx / r * v
    pvx[i] = vx_sum
    pvy[i] = vy_sum

pvx += np.random.normal(0, 0.03, num_particles)
pvy += np.random.normal(0, 0.03, num_particles)

# ============================================================
# 12) LAYOUT / FIGUR
# ============================================================
fig = plt.figure(figsize=(15.8, 10.0), facecolor="black")
gs = fig.add_gridspec(
    2,
    2,
    height_ratios=[3.35, 1.75],
    width_ratios=[1.0, 1.0],
    left=0.035,
    right=0.985,
    top=0.94,
    bottom=0.05,
    wspace=0.08,
    hspace=0.08,
)

ax_left = fig.add_subplot(gs[0, 0])
ax_right = fig.add_subplot(gs[0, 1])
ax_bottom = fig.add_subplot(gs[1, :])

for ax in [ax_left, ax_right, ax_bottom]:
    ax.set_facecolor("black")

ax_bottom.axis("off")

state = {
    "left_model": 1,
    "left_process": 1,
    "right_model": 4,
    "right_process": 4,
    "show_theory": True,
    "show_math": True,
    "show_delta": True,
    "sync_all": False,
    "sync_models": False,
    "sync_processes": False,
    "show_nebula": True,
    "nebula_mode": 1,
    "nebula_alpha": 0.34,
}

# ============================================================
# 13) PANEL-HILFSFUNKTIONEN
# ============================================================
def get_panel_data(model_id: int, process_id: int):
    process_key = PROCESSES[process_id][0]
    return MODELS[model_id][2][process_key]


def setup_panel(ax, model_id: int, process_id: int, title_prefix: str):
    process_key = PROCESSES[process_id][0]
    data = get_panel_data(model_id, process_id)
    arrows = ARROW_CACHE[process_key]
    arrow_color = PROCESS_ARROWS[process_key][2]

    im = ax.imshow(
        data,
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap=CMAPS[process_key],
        alpha=0.98,
    )

    quiv = ax.quiver(
        Xs,
        Ys,
        arrows[0],
        arrows[1],
        color=arrow_color,
        alpha=0.82,
        scale=24,
        width=0.0031,
        headwidth=4.6,
        headlength=5.2,
        headaxislength=4.9,
    )

    # Nebula overlay
    neb_data, neb_cmap = NEBULA_FIELDS[state["nebula_mode"]]
    nebula_overlay = ax.imshow(
        neb_data,
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap=neb_cmap,
        alpha=state["nebula_alpha"] if state["show_nebula"] else 0.0,
        vmin=0.0,
        vmax=1.0,
    )

    for cx, cy, mass in cores:
        ax.scatter(cx, cy, s=80 + mass * 0.15, c="white", alpha=0.98)

    particles = ax.scatter(px, py, s=8, c="white", alpha=0.84)
    ax.set_xlim(-space_size, space_size)
    ax.set_ylim(-space_size, space_size)
    ax.tick_params(colors="white")

    title = ax.set_title(title_prefix, color="white", fontsize=12)

    mini_legend = ax.text(
        0.02,
        0.02,
        "",
        transform=ax.transAxes,
        color="white",
        fontsize=8.4,
        alpha=0.92,
        va="bottom",
        bbox=dict(facecolor="black", alpha=0.36, edgecolor="gray"),
    )

    delta_overlay = ax.imshow(
        np.zeros_like(data),
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap="coolwarm",
        alpha=0.0,
        vmin=0.0,
        vmax=1.0,
    )

    return {
        "ax": ax,
        "im": im,
        "quiv": quiv,
        "particles": particles,
        "title": title,
        "mini_legend": mini_legend,
        "delta_overlay": delta_overlay,
        "nebula_overlay": nebula_overlay,
        "title_prefix": title_prefix,
    }


left_panel = setup_panel(ax_left, state["left_model"], state["left_process"], "LINKS")
right_panel = setup_panel(ax_right, state["right_model"], state["right_process"], "RECHTS")

fig.suptitle(
    "SFV Split-Screen Vergleichsmodell v4 | Sync + Delta + Nebula Layer",
    color="white",
    fontsize=17,
    y=0.975,
)

# ============================================================
# 14) BOTTOM-DISPLAY
# ============================================================
math_legend_text = (
    "MATHEMATISCHE LEGENDE\n"
    "────────────────────────────\n"
    "η(x,y)   := norm(|Φ(x,y)|)\n"
    "ψ(x,y)   := norm(|∇E(x,y)|)\n"
    "S(x,y)   := norm(|div G(x,y)|)\n"
    "P(x,y)   := norm(|curl V(x,y)| + a·ψ)\n"
    "X_exp    := norm(max(<∇E, r̂>,0) + b·E_rot)\n"
    "X_imp    := norm(max(-<G, r̂>,0) + c·η)\n"
    "F_back   := norm(α·P + β·S + γ·η)\n"
    "Δ(x,y)   := |L(x,y) - R(x,y)|\n"
    "N_em     := norm(0.50·P + 0.30·ψ + 0.20·X_exp)\n"
    "N_ref    := norm(0.60·Dust + 0.40·Glow)\n"
    "N_dark   := norm(0.70·Dust + 0.30·(1-Glow))\n"
    "N_mag    := norm((1-Bf)·P + Bf·(0.55·Fil + 0.45·S))\n"
)

theory_text = (
    "THEORIEBLOCK\n"
    "────────────────────────────────────────────────────────────────────────────\n"
    "Dieses Modell vergleicht vier Aussagen über denselben Feldraum und ergänzt sie\n"
    "um einen daten-inspirierten Nebula-SpaceLayer.\n\n"
    "A | Konservativ: Das Feld lebt im Raum.\n"
    "B | Raum besteht aus Feld.\n"
    "C | Feld ist Ursprung.\n"
    "D | Feld ist Realität.\n\n"
    "Nebula-Lesart:\n"
    "• Emissionsnebel  = ionisierte Gasregionen / energetische Anregung\n"
    "• Reflexionsnebel = beleuchteter Staub / reflektiertes Sternenlicht\n"
    "• Dunkelnebel     = Absorption / staubdominierte Abschattung\n"
    "• Magnetische Inseln = filamentartige, magnetisch strukturierte Schichten\n\n"
    "Der Nebula-Layer ist real-daten-inspiriert, aber KEIN direkter Survey-Import:\n"
    "er benutzt typische astrophysikalische Größenordnungen und modelliert daraus\n"
    "ein vergleichbares Strukturbild für den Viewer."
)

math_box = ax_bottom.text(
    0.015,
    0.95,
    math_legend_text,
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=9.7,
    va="top",
    ha="left",
    family="monospace",
    bbox=dict(facecolor="black", alpha=0.42, edgecolor="gray", boxstyle="round,pad=0.55"),
)

theory_box = ax_bottom.text(
    0.34,
    0.95,
    theory_text,
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=9.95,
    va="top",
    ha="left",
    bbox=dict(facecolor="black", alpha=0.34, edgecolor="gray", boxstyle="round,pad=0.60"),
)

delta_box = ax_bottom.text(
    0.50,
    0.07,
    "",
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=9.4,
    va="bottom",
    ha="center",
    bbox=dict(facecolor="black", alpha=0.40, edgecolor="gray", boxstyle="round,pad=0.45"),
)

spec_box = ax_bottom.text(
    0.985,
    0.57,
    "",
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=9.0,
    va="top",
    ha="right",
    bbox=dict(facecolor="black", alpha=0.36, edgecolor="gray", boxstyle="round,pad=0.45"),
)

controls_box = ax_bottom.text(
    0.985,
    0.05,
    "STEUERUNG\n"
    "Links: 1 2 3 4 + Q W E R\n"
    "Rechts: 7 8 9 0 + U I O P\n"
    "Y = Sync alle | X = Sync Prozesse | C = Sync Modelle\n"
    "D = Delta | F = rechts Prozess = links | G = rechts Modell = links\n"
    "N = Nebula an/aus | J = Nebula Modus | B/V = Alpha +/-\n"
    "H = Konsole | T = Theorie | M = Mathe\n"
    "Maus = Live-Koordinaten | Klick = Analyse + CSV Export",
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=9.05,
    va="bottom",
    ha="right",
    bbox=dict(facecolor="black", alpha=0.36, edgecolor="gray", boxstyle="round,pad=0.45"),
)

coord_text = ax_bottom.text(
    0.02,
    0.05,
    "",
    transform=ax_bottom.transAxes,
    color="cyan",
    fontsize=10,
    ha="left",
    va="bottom",
    bbox=dict(facecolor="black", alpha=0.50, edgecolor="gray", boxstyle="round,pad=0.35"),
)

analysis_text = ax_right.text(
    0.02,
    0.05,
    "",
    transform=ax_right.transAxes,
    color="white",
    fontsize=9.5,
    va="bottom",
    ha="left",
    bbox=dict(facecolor="black", alpha=0.60, edgecolor="gray", boxstyle="round,pad=0.35"),
)

scan_marker_left = ax_left.scatter([], [], s=90, c="red", alpha=0.95, marker="x")
scan_marker_right = ax_right.scatter([], [], s=90, c="red", alpha=0.95, marker="x")

cursor_left = Cursor(ax_left, useblit=True, color="white", linewidth=1)
cursor_right = Cursor(ax_right, useblit=True, color="white", linewidth=1)

# ============================================================
# 15) UPDATE-FUNKTIONEN
# ============================================================
def console_legend():
    print("\n" + "=" * 78)
    print("SFV SPLIT-SCREEN VERGLEICHSMODELL v4 — NEBULA LAYER")
    print("=" * 78)
    print("Real-data-inspired constants:")
    print(f"CMB temperature      : {CMB_TEMP_K:.3f} K")
    print(f"CMB anisotropy level : {CMB_ANISO_LEVEL:.1e}")
    print(f"ISM magnetic field   : {B_ISM_UG:.1f} microgauss")
    print(f"Galaxy total B field : {B_GALAXY_TOTAL_UG:.1f} microgauss")
    print(f"Dense nebula upper B : {B_DENSE_NEBULA_UG:.1f} microgauss")
    print("Nebula modes: 1 Emission | 2 Reflection | 3 Dark | 4 Magnetic islands")
    print("=" * 78 + "\n")


def update_panel(panel, model_id: int, process_id: int):
    model_letter, model_name, model_dict = MODELS[model_id]
    process_key, process_name = PROCESSES[process_id]

    panel["im"].set_array(model_dict[process_key])
    panel["im"].set_cmap(CMAPS[process_key])

    U, V = ARROW_CACHE[process_key]
    panel["quiv"].set_UVC(U, V)
    panel["quiv"].set_color(PROCESS_ARROWS[process_key][2])

    neb_data, neb_cmap = NEBULA_FIELDS[state["nebula_mode"]]
    panel["nebula_overlay"].set_array(neb_data)
    panel["nebula_overlay"].set_cmap(neb_cmap)
    panel["nebula_overlay"].set_alpha(state["nebula_alpha"] if state["show_nebula"] else 0.0)

    panel["title"].set_text(
        f"{panel['title_prefix']} | Modell {model_letter}: {model_name}\n"
        f"Prozess: {process_name} | Nebula: {nebula_mode_name(state['nebula_mode'])}"
    )

    panel["mini_legend"].set_text(
        f"{short_model_text(model_id)}\n"
        f"{short_process_text(process_key)}\n"
        f"{model_weights_text(model_id)}\n"
        f"Nebula={nebula_mode_name(state['nebula_mode'])} α={state['nebula_alpha']:.2f}"
    )


def compute_delta():
    left = get_panel_data(state["left_model"], state["left_process"])
    right = get_panel_data(state["right_model"], state["right_process"])
    delta = np.abs(left - right)
    return normalize(delta), left, right


def update_delta_overlay():
    delta, left, right = compute_delta()
    alpha = 0.34 if state["show_delta"] else 0.0
    left_panel["delta_overlay"].set_array(delta)
    right_panel["delta_overlay"].set_array(delta)
    left_panel["delta_overlay"].set_alpha(alpha)
    right_panel["delta_overlay"].set_alpha(alpha)

    mean_delta = float(np.mean(np.abs(left - right)))
    max_delta = float(np.max(np.abs(left - right)))
    hot_ratio = float(np.mean(delta > 0.60))

    sync_info = (
        f"sync_all={state['sync_all']} | "
        f"sync_models={state['sync_models']} | "
        f"sync_processes={state['sync_processes']}"
    )

    delta_box.set_text(
        "DELTA / DIFFERENZLAYER\n"
        f"Δ_mean = {mean_delta:.3f} | Δ_max = {max_delta:.3f} | Hot-Zone(Δ>0.60) = {100*hot_ratio:.1f}%\n"
        f"{sync_info}"
    )
    delta_box.set_visible(state["show_delta"])


def update_specs_box():
    spec_box.set_text(
        "COSMIC SPECS (daten-inspiriert)\n"
        f"CMB: {CMB_TEMP_K:.3f} K\n"
        f"CMB-ΔT/T: ~{CMB_ANISO_LEVEL:.0e}\n"
        f"ISM-B: {B_ISM_UG:.1f} μG\n"
        f"Galaxie-B: {B_GALAXY_TOTAL_UG:.1f} μG\n"
        f"Dichter Nebel B: bis ~{B_DENSE_NEBULA_UG:.0f} μG\n"
        f"Nebula-Modus: {nebula_mode_name(state['nebula_mode'])}\n"
        f"Overlay α: {state['nebula_alpha']:.2f}"
    )


def refresh_text_boxes():
    math_box.set_visible(state["show_math"])
    theory_box.set_visible(state["show_theory"])


def apply_sync_from_left(change_model=False, change_process=False):
    if state["sync_all"] or (state["sync_models"] and change_model):
        state["right_model"] = state["left_model"]
    if state["sync_all"] or (state["sync_processes"] and change_process):
        state["right_process"] = state["left_process"]


def refresh_all():
    update_panel(left_panel, state["left_model"], state["left_process"])
    update_panel(right_panel, state["right_model"], state["right_process"])
    update_delta_overlay()
    update_specs_box()
    refresh_text_boxes()
    fig.canvas.draw_idle()


def analyze_point(x, y):
    ix = int(np.abs(X[0] - x).argmin())
    iy = int(np.abs(Y[:, 0] - y).argmin())

    g_val = float(gravity_strength[iy, ix])
    e_val = float(energy_field[iy, ix])
    v_val = float(Vmag[iy, ix])
    pot_val = float(potential[iy, ix])
    eta_val = float(eta_depth[iy, ix])
    psi_val = float(psi_activity[iy, ix])
    struct_val = float(structure_flux[iy, ix])
    neb_data, _ = NEBULA_FIELDS[state["nebula_mode"]]
    nebula_val = float(neb_data[iy, ix])
    delta_map, _, _ = compute_delta()
    delta_val = float(delta_map[iy, ix])

    return {
        "x": float(x),
        "y": float(y),
        "r": float(np.sqrt(x**2 + y**2)),
        "gravity": g_val,
        "energy": e_val,
        "rotation": v_val,
        "potential": pot_val,
        "eta": eta_val,
        "psi": psi_val,
        "structure": struct_val,
        "nebula": nebula_val,
        "delta": delta_val,
        "left_model": MODELS[state["left_model"]][0],
        "left_process": PROCESSES[state["left_process"]][0],
        "right_model": MODELS[state["right_model"]][0],
        "right_process": PROCESSES[state["right_process"]][0],
        "nebula_mode": nebula_mode_name(state["nebula_mode"]),
    }


def export_point(data, filename="ms_field_data.csv"):
    file_exists = False
    try:
        with open(filename, "r", encoding="utf-8"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def on_mouse_move(event):
    if event.inaxes not in [ax_left, ax_right]:
        return
    x = event.xdata
    y = event.ydata
    if x is None or y is None:
        return

    data = analyze_point(x, y)
    coord_text.set_text(
        f"x={data['x']:.2f}, y={data['y']:.2f}\n"
        f"r={data['r']:.2f}\n"
        f"grav={data['gravity']:.4f}\n"
        f"energy={data['energy']:.4f}\n"
        f"rotation={data['rotation']:.4f}\n"
        f"nebula={data['nebula']:.4f}"
    )
    fig.canvas.draw_idle()


def on_click(event):
    if event.inaxes not in [ax_left, ax_right]:
        return
    x = event.xdata
    y = event.ydata
    if x is None or y is None:
        return

    data = analyze_point(x, y)
    scan_marker_left.set_offsets([[x, y]])
    scan_marker_right.set_offsets([[x, y]])

    analysis_text.set_text(
        "SCAN\n"
        f"x={data['x']:.2f}, y={data['y']:.2f}\n"
        f"r={data['r']:.2f}\n"
        f"grav={data['gravity']:.4f}\n"
        f"energy={data['energy']:.4f}\n"
        f"rot={data['rotation']:.4f}\n"
        f"pot={data['potential']:.4f}\n"
        f"η={data['eta']:.4f} | ψ={data['psi']:.4f}\n"
        f"S={data['structure']:.4f} | Δ={data['delta']:.4f}\n"
        f"N={data['nebula']:.4f} | {data['nebula_mode']}"
    )

    export_point(data)
    print("✔ Exported:", data)
    fig.canvas.draw_idle()

# ============================================================
# 16) TASTENSTEUERUNG
# ============================================================
def on_key(event):
    key = (event.key or "").lower()

    left_model_map = {"1": 1, "2": 2, "3": 3, "4": 4}
    right_model_map = {"7": 1, "8": 2, "9": 3, "0": 4}
    left_process_map = {"q": 1, "w": 2, "e": 3, "r": 4}
    right_process_map = {"u": 1, "i": 2, "o": 3, "p": 4}

    if key in left_model_map:
        state["left_model"] = left_model_map[key]
        apply_sync_from_left(change_model=True)
        refresh_all()
    elif key in right_model_map:
        state["right_model"] = right_model_map[key]
        refresh_all()
    elif key in left_process_map:
        state["left_process"] = left_process_map[key]
        apply_sync_from_left(change_process=True)
        refresh_all()
    elif key in right_process_map:
        state["right_process"] = right_process_map[key]
        refresh_all()
    elif key == "h":
        console_legend()
    elif key == "t":
        state["show_theory"] = not state["show_theory"]
        refresh_all()
    elif key == "m":
        state["show_math"] = not state["show_math"]
        refresh_all()
    elif key == "d":
        state["show_delta"] = not state["show_delta"]
        refresh_all()
    elif key == "y":
        state["sync_all"] = not state["sync_all"]
        if state["sync_all"]:
            state["sync_models"] = False
            state["sync_processes"] = False
        refresh_all()
    elif key == "x":
        state["sync_processes"] = not state["sync_processes"]
        if state["sync_processes"]:
            state["sync_all"] = False
        refresh_all()
    elif key == "c":
        state["sync_models"] = not state["sync_models"]
        if state["sync_models"]:
            state["sync_all"] = False
        refresh_all()
    elif key == "f":
        state["right_process"] = state["left_process"]
        refresh_all()
    elif key == "g":
        state["right_model"] = state["left_model"]
        refresh_all()
    elif key == "n":
        state["show_nebula"] = not state["show_nebula"]
        refresh_all()
    elif key == "j":
        state["nebula_mode"] += 1
        if state["nebula_mode"] > 4:
            state["nebula_mode"] = 1
        refresh_all()
    elif key == "b":
        state["nebula_alpha"] = min(0.85, state["nebula_alpha"] + 0.05)
        refresh_all()
    elif key == "v":
        state["nebula_alpha"] = max(0.0, state["nebula_alpha"] - 0.05)
        refresh_all()


fig.canvas.mpl_connect("key_press_event", on_key)
fig.canvas.mpl_connect("motion_notify_event", on_mouse_move)
fig.canvas.mpl_connect("button_press_event", on_click)

# ============================================================
# 17) ANIMATION
# ============================================================
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
        new_angles = np.random.uniform(0, 2 * np.pi, np.sum(reset))
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
                vy_sum += dx / r * v
            pvx_reset[j] = vx_sum
            pvy_reset[j] = vy_sum

        pvx[reset] = pvx_reset
        pvy[reset] = pvy_reset

    offsets = np.column_stack([px, py])
    left_panel["particles"].set_offsets(offsets)
    right_panel["particles"].set_offsets(offsets)

    return [
        left_panel["particles"],
        right_panel["particles"],
        left_panel["im"],
        right_panel["im"],
        left_panel["delta_overlay"],
        right_panel["delta_overlay"],
        left_panel["nebula_overlay"],
        right_panel["nebula_overlay"],
        left_panel["quiv"],
        right_panel["quiv"],
        left_panel["title"],
        right_panel["title"],
        left_panel["mini_legend"],
        right_panel["mini_legend"],
        math_box,
        theory_box,
        controls_box,
        spec_box,
        delta_box,
        coord_text,
        analysis_text,
        scan_marker_left,
        scan_marker_right,
    ]

# ============================================================
# 18) START
# ============================================================
console_legend()
refresh_all()
ani = animation.FuncAnimation(fig, update, frames=800, interval=30, blit=False)
plt.show()
