import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# Zero-Lumi Zustands-Feld-Ordnungsmodell
# Pydroid-Version: langsam, sichtbar, stabiler
# ------------------------------------------------------------
# Kernidee:
#
# Gleiche Energieverteilung rho_E(x,y)
# + anderes Ordnungsfeld A(x,y)
# = anderer Energiefluss J_E
#
# Die Energie wird nicht neu erzeugt.
# Sie wird durch das Ordnungsfeld gelenkt und geformt.
#
# Modi:
# 1 = Diffus / kaum Ordnung
# 2 = Fluss nach rechts
# 3 = Wirbel / Rotation
# 4 = Fokus / Bündelung
# 5 = Helix-/Schrauben-Analog
# ============================================================

np.random.seed(11)

# ------------------------------------------------------------
# PYDROID-FREUNDLICHE EINSTELLUNGEN
# ------------------------------------------------------------
N = 60                  # Gittergröße, kleiner = schneller auf Handy
FRAMES = 1000           # Länge der Animation
START_DELAY = 150       # Anfang wird gehalten, damit man ihn sehen kann

DT = 0.008              # Zeitschritt, kleiner = langsamer
DIFFUSION = 0.004       # natürliche Verteilung
FLOW_STRENGTH = 0.18    # Stärke des Ordnungsfelds

MODE = 4
# 1 = diffus
# 2 = rechtsfluss
# 3 = wirbel
# 4 = fokus
# 5 = helix/schrauben-analog

SAVE_GIF = False
GIF_NAME = "state_field_energy_flow_pydroid.gif"

# ------------------------------------------------------------
# Raumgitter
# ------------------------------------------------------------
x = np.linspace(-1.0, 1.0, N)
y = np.linspace(-1.0, 1.0, N)
X, Y = np.meshgrid(x, y)

dx = x[1] - x[0]
dy = y[1] - y[0]


# ------------------------------------------------------------
# Anfangsenergie
# ------------------------------------------------------------
def gaussian(x0, y0, sx, sy, amp=1.0):
    return amp * np.exp(
        -(
            ((X - x0) ** 2) / (2 * sx ** 2)
            + ((Y - y0) ** 2) / (2 * sy ** 2)
        )
    )


rho = (
    gaussian(-0.45, 0.20, 0.18, 0.15, 1.0)
    + gaussian(0.25, -0.30, 0.16, 0.20, 0.85)
    + gaussian(0.10, 0.45, 0.12, 0.12, 0.70)
)

# leichte Grundenergie
rho += 0.03 * np.random.rand(N, N)

# Gesamtenergie auf 1 normieren
rho = rho / np.sum(rho)

rho_initial = rho.copy()


# ------------------------------------------------------------
# Mathematik-Helfer
# ------------------------------------------------------------
def normalize_field(Ax, Ay):
    mag = np.sqrt(Ax ** 2 + Ay ** 2) + 1e-9
    return Ax / mag, Ay / mag


def laplacian(Z):
    return (
        np.roll(Z, 1, axis=0)
        + np.roll(Z, -1, axis=0)
        + np.roll(Z, 1, axis=1)
        + np.roll(Z, -1, axis=1)
        - 4 * Z
    )


def divergence(Jx, Jy):
    dJx_dx = (np.roll(Jx, -1, axis=1) - np.roll(Jx, 1, axis=1)) / (2 * dx)
    dJy_dy = (np.roll(Jy, -1, axis=0) - np.roll(Jy, 1, axis=0)) / (2 * dy)
    return dJx_dx + dJy_dy


def clamp_edges(Z):
    # Rand beruhigen, damit auf Handy keine wilden Kanten entstehen
    Z[0, :] = Z[1, :]
    Z[-1, :] = Z[-2, :]
    Z[:, 0] = Z[:, 1]
    Z[:, -1] = Z[:, -2]
    return Z


# ------------------------------------------------------------
# Ordnungsfeld A(x,y,t)
# ------------------------------------------------------------
def order_field(mode, t):
    """
    A ist das Ordnungs-/Lenkfeld.
    Es erzeugt keine Energie.
    Es bestimmt nur, wie Energie fließt.
    """

    if mode == 1:
        # Diffus: fast keine klare Ordnung
        Ax = 0.08 * np.sin(5 * Y + 0.03 * t)
        Ay = 0.08 * np.cos(5 * X + 0.03 * t)

    elif mode == 2:
        # Energiefluss nach rechts
        Ax = np.ones_like(X)
        Ay = 0.18 * np.sin(4 * X + 0.04 * t)

    elif mode == 3:
        # Wirbel um Zentrum
        Ax = -Y
        Ay = X
        Ax, Ay = normalize_field(Ax, Ay)

    elif mode == 4:
        # Fokus zum Zentrum
        Ax = -X
        Ay = -Y
        Ax, Ay = normalize_field(Ax, Ay)

    elif mode == 5:
        # Helix-/Schrauben-Analog:
        # Rotation plus leichter Vorwärtsfluss
        rot_x = -Y
        rot_y = X
        rot_x, rot_y = normalize_field(rot_x, rot_y)

        axial_x = np.ones_like(X) * 0.65
        axial_y = 0.20 * np.sin(8 * X + 0.05 * t)

        Ax = 0.65 * rot_x + 0.55 * axial_x
        Ay = 0.65 * rot_y + 0.55 * axial_y
        Ax, Ay = normalize_field(Ax, Ay)

    else:
        Ax = np.zeros_like(X)
        Ay = np.zeros_like(Y)

    return Ax, Ay


def mode_name(mode):
    if mode == 1:
        return "Modus 1 — Diffus: Energie bleibt weich verteilt"
    if mode == 2:
        return "Modus 2 — Rechtsfluss: Ordnung lenkt Energie"
    if mode == 3:
        return "Modus 3 — Wirbel: Energie rotiert"
    if mode == 4:
        return "Modus 4 — Fokus: Energie bündelt sich"
    if mode == 5:
        return "Modus 5 — Helix-Analog: Rotation + Fluss"
    return "Unbekannter Modus"


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 7))
fig.patch.set_facecolor("black")
ax.set_facecolor("#02040a")

im = ax.imshow(
    rho,
    extent=[-1, 1, -1, 1],
    origin="lower",
    cmap="inferno",
    interpolation="bilinear",
    vmin=0,
    vmax=np.max(rho_initial) * 1.4,
)

# weniger Pfeile = besser für Pydroid
skip = 8
Ax0, Ay0 = order_field(MODE, 0)

quiv = ax.quiver(
    X[::skip, ::skip],
    Y[::skip, ::skip],
    Ax0[::skip, ::skip],
    Ay0[::skip, ::skip],
    color="cyan",
    alpha=0.65,
    scale=22,
    width=0.004,
)

title = ax.text(
    0,
    1.12,
    "",
    color="white",
    fontsize=13,
    ha="center",
    va="center",
    fontweight="bold",
)

subtitle = ax.text(
    0,
    1.04,
    "",
    color="#bfefff",
    fontsize=9,
    ha="center",
    va="center",
)

energy_text = ax.text(
    -0.98,
    -1.12,
    "",
    color="#e8f7ff",
    fontsize=8,
    ha="left",
    va="center",
)

formula_text = ax.text(
    0.98,
    -1.12,
    "J_E = rho_E · A   |   Energie bleibt erhalten",
    color="#e8f7ff",
    fontsize=8,
    ha="right",
    va="center",
)

legend_text = ax.text(
    -0.98,
    0.96,
    "rho_E = Energiedichte\nA = Ordnungsfeld\nJ_E = Energiefluss",
    color="white",
    fontsize=8,
    ha="left",
    va="top",
    bbox=dict(
        boxstyle="round,pad=0.35",
        facecolor=(0.02, 0.04, 0.08, 0.72),
        edgecolor="#4db6ff",
    ),
)

ax.set_xlim(-1, 1)
ax.set_ylim(-1.18, 1.18)
ax.set_xticks([])
ax.set_yticks([])


# ------------------------------------------------------------
# Update-Funktion
# ------------------------------------------------------------
def update(frame):
    global rho

    # --------------------------------------------------------
    # STARTPAUSE:
    # Erst Anfangszustand zeigen.
    # --------------------------------------------------------
    if frame < START_DELAY:
        Ax, Ay = order_field(MODE, 0)

        im.set_data(rho_initial)
        im.set_clim(0, np.max(rho_initial) * 1.4)

        if frame % 5 == 0:
            quiv.set_UVC(Ax[::skip, ::skip], Ay[::skip, ::skip])

        title.set_text("Zero-Lumi Zustands-Feld-Ordnungsmodell")
        subtitle.set_text("Startzustand — gleiche Energieverteilung wird gehalten")

        total_energy = np.sum(rho_initial)
        max_energy = np.max(rho_initial)
        center_energy = rho_initial[
            N // 2 - 5:N // 2 + 5,
            N // 2 - 5:N // 2 + 5
        ].sum()

        energy_text.set_text(
            f"STARTPAUSE | Gesamt={total_energy:.4f} | Max={max_energy:.6f} | Zentrum={center_energy:.4f}"
        )

        return im, quiv, title, subtitle, energy_text, formula_text, legend_text

    # --------------------------------------------------------
    # echte Simulationszeit nach Startpause
    # --------------------------------------------------------
    t = frame - START_DELAY

    Ax, Ay = order_field(MODE, t)

    # Energiefluss:
    # vorhandene Energie wird durch A gelenkt
    Jx = FLOW_STRENGTH * rho * Ax
    Jy = FLOW_STRENGTH * rho * Ay

    # Kontinuitätsgleichung:
    # rho(t+dt) = rho - div(J)*dt + Diffusion
    divJ = divergence(Jx, Jy)

    rho_new = rho - DT * divJ + DIFFUSION * laplacian(rho)

    rho_new = clamp_edges(rho_new)
    rho_new = np.clip(rho_new, 0, None)

    # Gesamtenergie stabil halten
    total_before = np.sum(rho)
    total_after = np.sum(rho_new)

    if total_after > 0:
        rho_new *= total_before / total_after

    rho = rho_new

    # Anzeige aktualisieren
    im.set_data(rho)
    im.set_clim(0, max(np.max(rho) * 1.15, 1e-6))

    if frame % 5 == 0:
        quiv.set_UVC(Ax[::skip, ::skip], Ay[::skip, ::skip])

    total_energy = np.sum(rho)
    max_energy = np.max(rho)
    center_energy = rho[
        N // 2 - 5:N // 2 + 5,
        N // 2 - 5:N // 2 + 5
    ].sum()

    title.set_text("Zero-Lumi Zustands-Feld-Ordnungsmodell")
    subtitle.set_text(mode_name(MODE))

    energy_text.set_text(
        f"Gesamt={total_energy:.4f} | Max={max_energy:.6f} | Zentrum={center_energy:.4f}"
    )

    return im, quiv, title, subtitle, energy_text, formula_text, legend_text


# ------------------------------------------------------------
# Animation
# ------------------------------------------------------------
ani = FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=70,   # größer = langsamer
    blit=False
)

plt.tight_layout()

if SAVE_GIF:
    ani.save(GIF_NAME, writer="pillow", fps=20)
    print("GIF gespeichert als:", GIF_NAME)

plt.show()