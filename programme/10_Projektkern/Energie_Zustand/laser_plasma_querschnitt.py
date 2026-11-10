import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# Zero-Lumi Laser-Plasma-Querschnitt
# ------------------------------------------------------------
# Modellidee:
#
#   E_Laser =
#       E_thermisch
#     + E_kinetisch
#     + E_EM
#     + E_Wellen
#     + E_Strahlung
#     + E_Verlust
#
# Sichtbar gemacht als Querschnitt:
# - oben: ring-/trichterartiges Plasma
# - Laser/Wellenstrahl koppelt axial hinein
# - Plasmafrequenz erzeugt Resonanzfaktor
# - EM-Feld + Plasmawellen modulieren den Nebel
# - Strahlung/Verlust werden als Rand-/Außenanteile gezeigt
#
# Achtung:
# Das ist eine didaktische Toy-Simulation, keine echte PIC/MHD-Simulation.
# Für echte Plasma-Physik bräuchte man z.B. Particle-in-Cell,
# Magnetohydrodynamik oder Maxwell-Vlasov-Solver.
# ============================================================


# -----------------------------
# 1. Raumgitter
# -----------------------------
N = 360
space = 6.0

x = np.linspace(-space, space, N)
y = np.linspace(-space, space, N)
X, Y = np.meshgrid(x, y)

R = np.sqrt(X**2 + Y**2)
TH = np.arctan2(Y, X)

# -----------------------------
# 2. Laser / Plasma Parameter
# -----------------------------
frames = 360

# Laserfrequenz, frei normiert
f_laser = 1.00

# Plasmafrequenz, frei normiert
# Stelle auf 1.00 für starke Resonanz.
# Stelle z.B. auf 0.70 oder 1.40 für schwächere Kopplung.
f_plasma = 1.00

# Resonanzbreite: kleinere Werte = schärfere Resonanz
resonanz_breite = 0.18

# Dämpfung / Verlustfaktor
verlust_rate = 0.18

# Laserleistung, normiert
E_laser = 1.0

# -----------------------------
# 3. Resonanzfunktion
# -----------------------------
def resonance_factor(f_laser, f_plasma, width):
    """
    Gibt einen Resonanzfaktor zwischen 0 und 1 zurück.
    Maximum bei f_laser == f_plasma.
    """
    delta = f_laser - f_plasma
    return np.exp(-(delta**2) / (2 * width**2))


R_res = resonance_factor(f_laser, f_plasma, resonanz_breite)

print("============================================")
print("Zero-Lumi Laser-Plasma-Modell")
print("============================================")
print(f"f_Laser       = {f_laser:.3f}")
print(f"f_Plasma      = {f_plasma:.3f}")
print(f"Resonanz      = {R_res:.3f}")
print("============================================")


# -----------------------------
# 4. Energie-Bilanz
# -----------------------------
def energy_budget(t, R_res):
    """
    Symbolische Energieaufteilung.
    Alle Werte sind normiert.
    Die Summe bleibt etwa E_laser.
    """

    # Plasmawellen wachsen bei Resonanz
    E_wellen = 0.18 + 0.28 * R_res * (0.5 + 0.5 * np.sin(t))

    # EM-Feld-Anteil schwankt mit Plasmaantwort
    E_em = 0.16 + 0.20 * R_res * (0.5 + 0.5 * np.cos(0.7 * t))

    # Kinetische Teilchenenergie durch Wakefield/Beschleunigung
    E_kinetisch = 0.12 + 0.18 * R_res * (0.5 + 0.5 * np.sin(1.3 * t + 1.0))

    # Thermischer Anteil
    E_thermisch = 0.18 + 0.10 * (1.0 - R_res) + 0.04 * np.sin(0.5 * t)

    # Strahlung
    E_strahlung = 0.08 + 0.10 * R_res * (0.5 + 0.5 * np.sin(1.7 * t))

    # Verlust: Restenergie, damit Bilanz nicht über 1 geht
    used = E_wellen + E_em + E_kinetisch + E_thermisch + E_strahlung
    E_verlust = max(0.0, E_laser - used)

    # Falls durch Überlagerungen > 1, normalisieren wir sanft
    total = E_wellen + E_em + E_kinetisch + E_thermisch + E_strahlung + E_verlust

    E_wellen /= total
    E_em /= total
    E_kinetisch /= total
    E_thermisch /= total
    E_strahlung /= total
    E_verlust /= total

    return {
        "thermisch": E_thermisch,
        "kinetisch": E_kinetisch,
        "EM": E_em,
        "wellen": E_wellen,
        "strahlung": E_strahlung,
        "verlust": E_verlust,
    }


# -----------------------------
# 5. Feldmodell
# -----------------------------
def make_field(frame):
    """
    Erzeugt ein 2D-Querschnittsbild:
    - Plasmaring oben/zentral
    - Laser/Wellenkanal von unten nach oben
    - ringförmige und filamentartige Struktur
    """

    t = frame * 0.065

    # Energieanteile
    E = energy_budget(t, R_res)

    # --------------------------------------------------------
    # Plasma-Ring / Trichter
    # --------------------------------------------------------
    ring_radius = 2.2 + 0.12 * np.sin(0.8 * t)
    ring_width = 0.45

    ring = np.exp(-((R - ring_radius)**2) / (2 * ring_width**2))

    # Ringrotation / Wellenmoden im Plasma
    mode_1 = np.sin(8 * TH + 2.5 * t)
    mode_2 = np.cos(13 * TH - 1.7 * t)
    mode_3 = np.sin(5 * R - 2.0 * t)

    plasma_modes = 1.0 + 0.25 * R_res * mode_1 + 0.18 * mode_2 + 0.12 * mode_3
    plasma_ring = ring * plasma_modes

    # --------------------------------------------------------
    # Laserkanal / dicker Strahl
    # --------------------------------------------------------
    # Vertikaler Strahl entlang x=0
    beam_width = 0.70 + 0.15 * R_res
    beam_core = np.exp(-(X**2) / (2 * beam_width**2))

    # Strahl kommt von unten und koppelt in Ringzentrum
    beam_shape = 1 / (1 + np.exp(2.2 * (Y - 1.2)))
    beam = beam_core * beam_shape

    # Wellenstruktur im Strahl
    wave_phase = np.sin(9 * Y - 4.0 * t + 2.2 * np.sin(TH))
    helical = np.sin(5 * TH + 8 * Y - 3.5 * t)

    laser_wave = beam * (1.0 + 0.22 * wave_phase + 0.18 * helical)

    # --------------------------------------------------------
    # Plasmawellen / Wakefield
    # --------------------------------------------------------
    wake = np.exp(-(X**2) / (2 * 1.25**2)) * np.exp(-((Y - 0.1)**2) / (2 * 2.2**2))
    wake *= np.sin(7.5 * Y - 5.0 * t) ** 2
    wake *= R_res

    # --------------------------------------------------------
    # EM-Feld-Struktur außen
    # --------------------------------------------------------
    em_field = np.sin(3.5 * R - 2.0 * t + 2 * np.sin(TH)) ** 2
    em_field *= np.exp(-R / 5.5)
    em_field *= 0.65 + 0.35 * R_res

    # --------------------------------------------------------
    # Plasma-Filamentierung
    # --------------------------------------------------------
    filaments = (
        np.sin(12 * X + 4 * np.sin(Y) + 2.5 * t) *
        np.cos(10 * Y - 3 * np.sin(X) - 1.8 * t)
    )
    filaments = np.abs(filaments)
    filaments *= np.exp(-R / 4.8)
    filaments *= R_res

    # --------------------------------------------------------
    # Strahlung / Nebel
    # --------------------------------------------------------
    radiation_shell = np.exp(-((R - 3.6)**2) / (2 * 0.8**2))
    radiation_shell *= 0.6 + 0.4 * np.sin(7 * TH + t)**2

    # --------------------------------------------------------
    # Gesamtbild aus Energieanteilen
    # --------------------------------------------------------
    field = (
        E["EM"]        * 1.35 * em_field +
        E["wellen"]    * 1.60 * wake +
        E["kinetisch"] * 1.50 * laser_wave +
        E["thermisch"] * 1.10 * plasma_ring +
        E["strahlung"] * 0.95 * radiation_shell +
        E["verlust"]   * 0.30 * np.exp(-R / 4.0)
    )

    # Extra Leuchten im Kopplungspunkt: Laser trifft Plasma
    coupling = np.exp(-(X**2 + (Y - 0.9)**2) / (2 * 0.55**2))
    field += 1.7 * R_res * coupling

    # Normalisieren
    field = field - field.min()
    field = field / (field.max() + 1e-9)

    return field, E


# -----------------------------
# 6. Plot vorbereiten
# -----------------------------
fig = plt.figure(figsize=(10, 8))
ax = plt.gca()

initial_field, initial_E = make_field(0)

img = ax.imshow(
    initial_field,
    extent=[-space, space, -space, space],
    origin="lower",
    cmap="magma",
    interpolation="bilinear",
    vmin=0,
    vmax=1
)

ax.set_title(
    "Laser-Plasma-Wechselwirkung: E-Laser → E-Plasmawelle → E-Feld → E-Strahlung",
    fontsize=12
)

ax.set_xlabel("x / Querschnitt")
ax.set_ylabel("y / Achse des Laserkanals")

# Plasma-Ring visuell markieren
theta = np.linspace(0, 2 * np.pi, 400)
ring_x = 2.2 * np.cos(theta)
ring_y = 2.2 * np.sin(theta)
ax.plot(ring_x, ring_y, linewidth=1.0, alpha=0.55)

# Laserachse
ax.plot([0, 0], [-space, space], linestyle="--", linewidth=0.9, alpha=0.45)

# Textbox Energie
energy_text = ax.text(
    -5.75, 5.45,
    "",
    fontsize=9,
    va="top",
    bbox=dict(boxstyle="round", alpha=0.25)
)

# Erklärung rechts unten
model_text = ax.text(
    1.25, -5.55,
    "Modellbegriffe:\n"
    "• Plasmafrequenz\n"
    "• Resonanz\n"
    "• Plasmawellen\n"
    "• Wakefield-Beschleunigung\n"
    "• EM-Feld\n"
    "• Magnetohydrodynamik\n"
    "• Plasmafilamentierung",
    fontsize=8,
    va="bottom",
    bbox=dict(boxstyle="round", alpha=0.20)
)

plt.colorbar(img, ax=ax, label="normierte Feld-/Energieintensität")


# -----------------------------
# 7. Animation
# -----------------------------
def update(frame):
    field, E = make_field(frame)
    img.set_data(field)

    total = sum(E.values())

    energy_text.set_text(
        f"f_Laser = {f_laser:.2f}\n"
        f"f_Plasma = {f_plasma:.2f}\n"
        f"Resonanz = {R_res:.2f}\n\n"
        f"E_Laser = {total:.2f}\n"
        f"E_thermisch  = {E['thermisch']:.2f}\n"
        f"E_kinetisch  = {E['kinetisch']:.2f}\n"
        f"E_EM         = {E['EM']:.2f}\n"
        f"E_Wellen     = {E['wellen']:.2f}\n"
        f"E_Strahlung  = {E['strahlung']:.2f}\n"
        f"E_Verlust    = {E['verlust']:.2f}"
    )

    return img, energy_text


ani = FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=35,
    blit=False
)

plt.tight_layout()
plt.show()


# -----------------------------
# Optional speichern:
# -----------------------------
# Wenn du ein GIF willst, unten einkommentieren.
# Dafür brauchst du pillow:
# pip install pillow
#
# ani.save("laser_plasma_querschnitt.gif", writer="pillow", fps=24)