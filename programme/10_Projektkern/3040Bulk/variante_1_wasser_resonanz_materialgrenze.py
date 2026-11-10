
# ============================================================
# Zero-Lumÿè Variante 1:
# 2D Wasserströmung + Resonanzquelle + Materialgrenze
# ------------------------------------------------------------
# Idee aus deiner Skizze:
#
# Wasser-/Feldbewegung
#     ↓
# Schwingungsquelle
#     ↓
# Druck-/Wellenfeld
#     ↓
# trifft auf gestufte/raue Materialgrenze
#     ↓
# Reflexion, Resonanzzonen, Wirbel-Andeutung
#
# Physikalische Basis:
# - 2D-Wellengleichung als vereinfachtes Wasser-/Druckfeld
# - Dämpfung
# - Materialmaske als Hindernis/Grenzfläche
# - Resonanzkarte aus lokaler Schwingungsenergie
#
# Wichtig:
# Das ist ein anschauliches Modell, kein vollständiger
# Navier-Stokes-Fluid-Solver.
# Es zeigt den Übergang:
# sichtbare Strömungs-/Wellenbewegung → Grenzfläche → Resonanz.
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# ============================================================
# 1. Einstellungen
# ============================================================

np.random.seed(4)

NX = 220
NY = 130

frames = 1200
dt = 0.16

# Wellenausbreitung
c_water = 1.00          # Geschwindigkeit im Wasser/Freiraum
c_material = 0.38       # langsamere Kopplung im Materialbereich
damping_water = 0.006
damping_material = 0.035

# Quelle
source_x = 35
source_y = NY // 2 + 10
source_frequency = 0.105
source_strength = 0.95

# Numerische Stabilität
laplace_strength = 0.22

# Felder
u = np.zeros((NY, NX), dtype=float)       # aktuelles Wellen-/Druckfeld
u_prev = np.zeros_like(u)                 # vorheriger Zustand
resonance = np.zeros_like(u)              # geglättete Energie-/Resonanzkarte


# ============================================================
# 2. Materialgrenze aus deiner Skizzen-Idee
# ============================================================

# material[y, x] = True bedeutet: Material/Hindernis/Grenzfläche
material = np.zeros((NY, NX), dtype=bool)

# Eine gestufte Schräge rechts unten, inspiriert durch deine Zeichnung.
# Alles unterhalb dieser Linie ist "Material".
for x in range(NX):
    if x < 80:
        boundary = NY + 10
    elif x < 135:
        # schräge Übergangszone
        boundary = int(92 - 0.25 * (x - 80))
    elif x < 175:
        # Treppenbereich
        step = ((x - 135) // 7)
        boundary = 78 + step * 4
    else:
        # flacher Block rechts
        boundary = 92

    if 0 <= boundary < NY:
        material[boundary:, x] = True

# Kleine Kantenstruktur / Vorsprung als Resonanz-Störer
material[78:86, 132:145] = True
material[86:94, 145:158] = True
material[94:102, 158:171] = True

# Freiraum-Kavität / Einschnitt rechts, ähnlich wie ein rechteckiger Ausschnitt
material[74:110, 188:213] = False
material[105:, 213:] = True


# ============================================================
# 3. Hilfsfunktionen
# ============================================================

def laplacian(a):
    """
    2D-Laplace-Operator mit einfachen festen Rändern.
    """
    out = np.zeros_like(a)
    out[1:-1, 1:-1] = (
        a[1:-1, 2:] +
        a[1:-1, :-2] +
        a[2:, 1:-1] +
        a[:-2, 1:-1] -
        4.0 * a[1:-1, 1:-1]
    )
    return out


def add_source(field, frame):
    """
    Lokale sinusförmige Schwingungsquelle.
    """
    pulse = source_strength * np.sin(2.0 * np.pi * source_frequency * frame)

    # kleine Gaußquelle statt einzelner Pixel
    yy, xx = np.ogrid[:NY, :NX]
    r2 = (xx - source_x) ** 2 + (yy - source_y) ** 2
    source_shape = np.exp(-r2 / (2.0 * 5.0 ** 2))

    field += pulse * source_shape
    return field


def compute_vorticity_like(field):
    """
    Keine echte Fluid-Vorticity, sondern eine Wirbel-Andeutung:
    lokale Kreuzgradienten/Gradientstärke.
    Das zeigt, wo das Feld stark gebrochen/verzogen wird.
    """
    gy, gx = np.gradient(field)
    gyy, gyx = np.gradient(gy)
    gxy, gxx = np.gradient(gx)
    curl_like = gyx - gxy
    return curl_like


# ============================================================
# 4. Plot vorbereiten
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle(
    "Variante 1: Wasser-/Druckwelle trifft Materialgrenze → Resonanzzonen",
    fontsize=14
)

ax_wave, ax_res, ax_vort = axes

# Anzeige: Wellenfeld
wave_img = ax_wave.imshow(
    u,
    cmap="RdBu_r",
    vmin=-1.0,
    vmax=1.0,
    origin="lower",
    interpolation="bilinear"
)
ax_wave.set_title("Wellen-/Druckfeld")
ax_wave.axis("off")

# Materialkontur überlagern
ax_wave.contour(material, levels=[0.5], colors="black", linewidths=1.2)

# Anzeige: Resonanz
res_img = ax_res.imshow(
    resonance,
    cmap="inferno",
    vmin=0.0,
    vmax=0.12,
    origin="lower",
    interpolation="bilinear"
)
ax_res.set_title("Resonanz / lokale Energie")
ax_res.axis("off")
ax_res.contour(material, levels=[0.5], colors="white", linewidths=1.0)

# Anzeige: Wirbel-Andeutung / Feldbruch
vort_img = ax_vort.imshow(
    np.zeros_like(u),
    cmap="PuOr",
    vmin=-0.25,
    vmax=0.25,
    origin="lower",
    interpolation="bilinear"
)
ax_vort.set_title("Wirbel-/Streuungs-Andeutung")
ax_vort.axis("off")
ax_vort.contour(material, levels=[0.5], colors="black", linewidths=1.0)

# Quelle markieren
for ax in axes:
    ax.plot(source_x, source_y, "wo", markersize=5, markeredgecolor="black")
    ax.text(source_x + 4, source_y + 4, "Quelle", color="white", fontsize=8)

info = fig.text(
    0.02,
    0.02,
    "",
    fontsize=10,
    family="monospace"
)


# ============================================================
# 5. Animationsschritt
# ============================================================

def update(frame):
    global u, u_prev, resonance

    # Lokale Ausbreitungsgeschwindigkeit:
    # Im Material langsamer und stärker gedämpft.
    c_map = np.where(material, c_material, c_water)
    damping_map = np.where(material, damping_material, damping_water)

    # Wellengleichung diskret:
    # u_next = 2u - u_prev + c² * Laplace(u)
    lap = laplacian(u)
    u_next = (
        2.0 * u
        - u_prev
        + laplace_strength * (c_map ** 2) * lap
    )

    # Dämpfung
    u_next *= (1.0 - damping_map)

    # Quelle einspeisen
    u_next = add_source(u_next, frame)

    # In starkem Material nicht hart blocken, sondern gedämpft weiterlaufen lassen.
    # Das simuliert: ein Teil koppelt ein, ein Teil wird geschluckt/gedämpft.
    u_prev = u
    u = u_next

    # Resonanzkarte:
    # lokale Schwingungsenergie über Zeit geglättet
    local_energy = (u - u_prev) ** 2 + 0.35 * (laplacian(u) ** 2)
    resonance = 0.985 * resonance + 0.015 * local_energy

    # Wirbel-/Streuungs-Andeutung
    vort = compute_vorticity_like(u)

    # Anzeigen aktualisieren
    wave_img.set_data(u)
    res_img.set_data(resonance)
    vort_img.set_data(vort)

    # Auto-Skalierung etwas robust halten
    wave_img.set_clim(-1.0, 1.0)
    res_img.set_clim(0.0, max(0.04, np.percentile(resonance, 99.5)))
    vort_limit = max(0.05, np.percentile(np.abs(vort), 99.0))
    vort_img.set_clim(-vort_limit, vort_limit)

    # Diagnosewerte
    total_wave = np.mean(u ** 2)
    total_res = np.mean(resonance)
    mat_res = np.mean(resonance[material]) if np.any(material) else 0.0
    water_res = np.mean(resonance[~material]) if np.any(~material) else 0.0

    info.set_text(
        f"Frame={frame:04d} | Quelle f={source_frequency:.3f} | "
        f"Wellenenergie={total_wave:.4f} | Resonanz={total_res:.4f} | "
        f"Wasser={water_res:.4f} | Material={mat_res:.4f}\n"
        f"Physik-Idee: Welle trifft Grenzfläche → Reflexion/Streuung → lokale Resonanz → gedämpfte Materialkopplung"
    )

    return wave_img, res_img, vort_img, info


# ============================================================
# 6. Start
# ============================================================

ani = FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=30,
    blit=False
)

plt.tight_layout()
plt.show()
