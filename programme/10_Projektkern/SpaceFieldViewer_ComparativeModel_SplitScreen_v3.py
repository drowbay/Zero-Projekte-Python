import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

"""
=====================================================================
SPACE FIELD VIEWER — SPLIT-SCREEN VERGLEICHSMODELL v3
=====================================================================

Dieses Script ist ein visuelles Denk- und Vergleichsmodell.
Es zeigt zwei gleichzeitig sichtbare Lesarten desselben Feldraums
und ergänzt sie um einen Delta-/Differenzlayer.

LAYOUT
------
- Oben links:   Feldansicht links
- Oben rechts:  Feldansicht rechts
- Unten links:  mathematische Legende
- Unten quer:   Theorieblock
- Mitte unten:  Delta-/Differenzinfo zwischen links und rechts

ZUSATZMODI
----------
- Sync-Modus: Modell- oder Prozesswechsel können gekoppelt werden.
- Delta-Modus: Zeigt |links - rechts| als eigenes Vergleichsmaß.

MODELLE
-------
1 = A = Konservativ: Feld lebt im Raum
2 = B = Raum besteht aus Feld
3 = C = Feld ist Ursprung
4 = D = Feld ist Realität

PROZESSE
--------
Q = Expansion
W = Phasenstruktur
E = Implosion
R = Phasenrückkopplung

STEUERUNG
---------
Linke Ansicht:
  1 2 3 4  -> Modell wechseln
  Q W E R  -> Prozess wechseln

Rechte Ansicht:
  7 8 9 0  -> Modell wechseln
  U I O P  -> Prozess wechseln

Global:
  Y        -> Sync alles an/aus
  X        -> Sync nur Prozesse an/aus
  C        -> Sync nur Modelle an/aus
  D        -> Delta-Overlay an/aus
  F        -> Fokus: rechter Prozess = linker Prozess
  G        -> Fokus: rechtes Modell = linkes Modell
  T        -> Theorieblock an/aus
  M        -> Mathe-Legende an/aus
  H        -> Legende in Konsole ausgeben
"""

np.random.seed(7)

# ============================================================
# 1) GRUNDPARAMETER
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
# 2) HILFSFUNKTIONEN
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


# ============================================================
# 3) GITTER / RAUM
# ============================================================
x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)
R0 = np.sqrt(X**2 + Y**2) + 1e-9
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
    VY += dx / R * v_mag

Gmag = np.sqrt(GX**2 + GY**2) + 1e-9
Vmag = np.sqrt(VX**2 + VY**2) + 1e-9
rot_energy = 0.5 * (Vmag**2)
energy_field = gravity_strength + rot_energy


# ============================================================
# 5) ABGELEITETE FELDER
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
# 6) PROZESS-RICHTUNGEN
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
# 7) VERGLEICHSMODELLE
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
# 8) PFEILFELD-CACHE
# ============================================================
Xs = X[::step_arrow, ::step_arrow]
Ys = Y[::step_arrow, ::step_arrow]

ARROW_CACHE = {}
for key, (FX, FY, _) in PROCESS_ARROWS.items():
    FXs = FX[::step_arrow, ::step_arrow]
    FYs = FY[::step_arrow, ::step_arrow]
    ARROW_CACHE[key] = unit_vectors(FXs, FYs)


# ============================================================
# 9) TESTTEILCHEN
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
# 10) LAYOUT / FIGUR
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
}


# ============================================================
# 11) PANEL-HILFSFUNKTIONEN
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
        fontsize=8.6,
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
        "title_prefix": title_prefix,
    }


left_panel = setup_panel(ax_left, state["left_model"], state["left_process"], "LINKS")
right_panel = setup_panel(ax_right, state["right_model"], state["right_process"], "RECHTS")

fig.suptitle(
    "SFV Split-Screen Vergleichsmodell v3 | Sync + Delta",
    color="white",
    fontsize=17,
    y=0.975,
)


# ============================================================
# 12) BOTTOM-DISPLAY
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
    "Δ(x,y)   := |L(x,y) - R(x,y)|\n\n"
    "Bedeutung:\n"
    "Φ  = Potential / Feldtiefe\n"
    "E  = Energiefeld\n"
    "G  = Einzugsfeld\n"
    "V  = Rotationsfeld\n"
    "r̂ = radiale Einheitsrichtung\n"
    "L/R = linkes / rechtes Panel\n"
    "norm(.) → Normierung auf [0,1]"
)

theory_text = (
    "THEORIEBLOCK\n"
    "────────────────────────────────────────────────────────────────────────────\n"
    "Dieses Modell vergleicht vier Aussagen über denselben Feldraum.\n\n"
    "A | Konservativ: Das Feld lebt im Raum.\n"
    "    Der Raum ist Bühne. Felder und Dynamiken treten in ihm auf.\n\n"
    "B | Raum besteht aus Feld.\n"
    "    Raum ist nicht nur Behälter, sondern selbst Ausdruck einer Feldstruktur.\n\n"
    "C | Feld ist Ursprung.\n"
    "    Feldtiefe und Grundzustand werden als primäre Quelle von Struktur, Bewegung\n"
    "    und emergenter Ordnung gelesen.\n\n"
    "D | Feld ist Realität.\n"
    "    Nicht Objekt plus Raum, sondern ein einheitlicher Feldzusammenhang, dessen\n"
    "    Zustände wir als Realität wahrnehmen.\n\n"
    "Vier Prozesse werden verglichen:\n"
    "• Expansion           = nach außen gerichtete Entfaltung\n"
    "• Phasenstruktur      = Wirbel, Schichtung, Muster, lokale Zustandsordnung\n"
    "• Implosion           = nach innen gerichtete Verdichtung\n"
    "• Phasenrückkopplung  = Rückwirkung zwischen Tiefe, Struktur und Aktivität\n\n"
    "Delta-Lesart:\n"
    "Das Delta misst nicht Wahrheit, sondern Differenz der Gewichtung.\n"
    "Hohe Δ-Werte markieren Orte, an denen zwei Modelle oder Prozesse den gleichen\n"
    "Raum besonders unterschiedlich lesen."
)

math_box = ax_bottom.text(
    0.015,
    0.95,
    math_legend_text,
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=10.0,
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
    fontsize=10.15,
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
    fontsize=9.6,
    va="bottom",
    ha="center",
    bbox=dict(facecolor="black", alpha=0.40, edgecolor="gray", boxstyle="round,pad=0.45"),
)

controls_box = ax_bottom.text(
    0.985,
    0.05,
    "STEUERUNG\n"
    "Links: 1 2 3 4 + Q W E R\n"
    "Rechts: 7 8 9 0 + U I O P\n"
    "Y = Sync alle | X = Sync Prozesse | C = Sync Modelle\n"
    "D = Delta | F = rechts Prozess = links | G = rechts Modell = links\n"
    "H = Konsole | T = Theorie | M = Mathe",
    transform=ax_bottom.transAxes,
    color="white",
    fontsize=9.15,
    va="bottom",
    ha="right",
    bbox=dict(facecolor="black", alpha=0.36, edgecolor="gray", boxstyle="round,pad=0.45"),
)


# ============================================================
# 13) KONSOLE / UPDATE-FUNKTIONEN
# ============================================================
def console_legend():
    print("\n" + "=" * 74)
    print("SFV SPLIT-SCREEN VERGLEICHSMODELL v3 — LEGENDE")
    print("=" * 74)
    print("MODELLE")
    print("A  Raum ist Bühne, Feld wirkt darin.")
    print("B  Raum wird selbst als Feldstruktur gelesen.")
    print("C  Feldtiefe / Feldgrund ist Ursprung der Struktur.")
    print("D  Alles wird als Feldzustand interpretiert.")
    print("-" * 74)
    print("PROZESSE")
    print("Q  Expansion = nach außen gerichtete Entfaltung")
    print("W  Phase     = Wirbel / lokale Zustandsstruktur")
    print("E  Implosion = nach innen gerichtete Verdichtung")
    print("R  Feedback  = Rückwirkung zwischen Tiefe, Struktur, Aktivität")
    print("-" * 74)
    print("VERGLEICH")
    print("Δ(x,y) = |L(x,y) - R(x,y)|")
    print("Hohe Delta-Werte = starke Differenz der Lesart an derselben Stelle.")
    print("Sync-Modi koppeln Modell- und/oder Prozesswechsel beider Panels.")
    print("=" * 74 + "\n")


def update_panel(panel, model_id: int, process_id: int):
    model_letter, model_name, model_dict = MODELS[model_id]
    process_key, process_name = PROCESSES[process_id]

    panel["im"].set_array(model_dict[process_key])
    panel["im"].set_cmap(CMAPS[process_key])

    U, V = ARROW_CACHE[process_key]
    panel["quiv"].set_UVC(U, V)
    panel["quiv"].set_color(PROCESS_ARROWS[process_key][2])

    panel["title"].set_text(
        f"{panel['title_prefix']} | Modell {model_letter}: {model_name}\n"
        f"Prozess: {process_name}"
    )

    panel["mini_legend"].set_text(
        f"{short_model_text(model_id)}\n"
        f"{short_process_text(process_key)}\n"
        f"{model_weights_text(model_id)}"
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
    refresh_text_boxes()
    fig.canvas.draw_idle()


# ============================================================
# 14) TASTENSTEUERUNG
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


fig.canvas.mpl_connect("key_press_event", on_key)


# ============================================================
# 15) ANIMATION
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
        left_panel["quiv"],
        right_panel["quiv"],
        left_panel["title"],
        right_panel["title"],
        left_panel["mini_legend"],
        right_panel["mini_legend"],
        math_box,
        theory_box,
        controls_box,
        delta_box,
    ]


# ============================================================
# 16) START
# ============================================================
console_legend()
refresh_all()
ani = animation.FuncAnimation(fig, update, frames=800, interval=30, blit=False)
plt.show()
