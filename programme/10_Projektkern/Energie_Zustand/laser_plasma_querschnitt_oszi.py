import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# Zero-Lumi Laser-Plasma-Querschnitt + Oszilloskop/Äquivalent
# ------------------------------------------------------------
# Zeigt zwei Dinge gleichzeitig:
#
# 1. Links:
#    Laser-Plasma-Querschnitt:
#    E_Laser -> Plasma -> Wellen -> EM-Feld -> Strahlung -> Verlust
#
# 2. Rechts:
#    Messlinien / "Preisdiagramm"-Style:
#    Energieanteile als Kurven mit Ausschlägen.
#
# 3. Unten:
#    Frequenz-/Resonanz-Äquivalent:
#    f_Laser, f_Plasma und Resonanzantwort.
#
# Wichtig:
# Das ist ein didaktisches Toy-Modell.
# Keine echte PIC-, MHD- oder Maxwell-Vlasov-Simulation.
# ============================================================

import matplotlib as mpl

# -----------------------------
# 1. Raumgitter
# -----------------------------
N = 300
space = 6.0

x = np.linspace(-space, space, N)
y = np.linspace(-space, space, N)
X, Y = np.meshgrid(x, y)

R = np.sqrt(X**2 + Y**2)
TH = np.arctan2(Y, X)

# -----------------------------
# 2. Parameter
# -----------------------------
frames = 420

E_laser = 1.0

# Frequenzen normiert
f_laser = 1.00
f_plasma = 1.00

# Resonanzbreite
resonanz_breite = 0.18

# Länge der Messkurven-Historie
history_len = 220

# -----------------------------
# 3. Resonanzfunktion
# -----------------------------
def resonance_factor(f_laser, f_plasma, width):
    delta = f_laser - f_plasma
    return np.exp(-(delta**2) / (2 * width**2))


R_res = resonance_factor(f_laser, f_plasma, resonanz_breite)

print("============================================")
print("Zero-Lumi Laser-Plasma-Querschnitt + Oszi")
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
    Symbolische Energieverteilung.
    Summe wird auf 1.0 normiert.

    E_Laser =
        E_thermisch
      + E_kinetisch
      + E_EM
      + E_Wellen
      + E_Strahlung
      + E_Verlust
    """

    # Plasmawellen reagieren stark auf Resonanz
    E_wellen = 0.16 + 0.30 * R_res * (0.5 + 0.5 * np.sin(1.00 * t))

    # EM-Feld-Anteil, etwas langsamer
    E_em = 0.14 + 0.22 * R_res * (0.5 + 0.5 * np.cos(0.72 * t + 0.4))

    # Kinetische Energie / Wakefield-Beschleunigung
    E_kinetisch = 0.11 + 0.20 * R_res * (0.5 + 0.5 * np.sin(1.37 * t + 1.1))

    # Thermische Energie: mehr bei schwacher Resonanz, weil Energie eher "verkocht"
    E_thermisch = 0.17 + 0.12 * (1.0 - R_res) + 0.035 * np.sin(0.45 * t + 0.8)

    # Strahlung: pulsiert mit schnellen Ausschlägen
    E_strahlung = 0.07 + 0.12 * R_res * (0.5 + 0.5 * np.sin(1.82 * t + 0.2))

    # Verlustanteil als Rest
    used = E_wellen + E_em + E_kinetisch + E_thermisch + E_strahlung
    E_verlust = max(0.02, E_laser - used)

    # Normalisieren
    total = E_wellen + E_em + E_kinetisch + E_thermisch + E_strahlung + E_verlust

    return {
        "thermisch": E_thermisch / total,
        "kinetisch": E_kinetisch / total,
        "EM": E_em / total,
        "wellen": E_wellen / total,
        "strahlung": E_strahlung / total,
        "verlust": E_verlust / total,
    }


# -----------------------------
# 5. Feldmodell
# -----------------------------
def make_field(frame):
    t = frame * 0.065
    E = energy_budget(t, R_res)

    # Plasma-Ring
    ring_radius = 2.2 + 0.10 * np.sin(0.85 * t)
    ring_width = 0.46

    ring = np.exp(-((R - ring_radius) ** 2) / (2 * ring_width ** 2))

    mode_1 = np.sin(8 * TH + 2.5 * t)
    mode_2 = np.cos(13 * TH - 1.7 * t)
    mode_3 = np.sin(5 * R - 2.0 * t)

    plasma_modes = 1.0 + 0.26 * R_res * mode_1 + 0.17 * mode_2 + 0.12 * mode_3
    plasma_ring = ring * plasma_modes

    # Dicker Laser-/Energie-Strahl
    beam_width = 1.05 + 0.20 * R_res
    beam_core = np.exp(-(X ** 2) / (2 * beam_width ** 2))

    # Von unten nach oben, aber im Ringbereich gekoppelt
    beam_shape = 1 / (1 + np.exp(2.1 * (Y - 1.45)))
    beam = beam_core * beam_shape

    # Wellenstruktur im Strahl
    wave_phase = np.sin(8.5 * Y - 4.0 * t + 1.7 * np.sin(TH))
    helical = np.sin(5 * TH + 7.5 * Y - 3.5 * t)

    laser_wave = beam * (1.0 + 0.24 * wave_phase + 0.16 * helical)

    # Plasmawellen / Wakefield-Zone
    wake = np.exp(-(X ** 2) / (2 * 1.35 ** 2)) * np.exp(-((Y - 0.15) ** 2) / (2 * 2.25 ** 2))
    wake *= np.sin(7.3 * Y - 5.1 * t) ** 2
    wake *= R_res

    # EM-Feld außen
    em_field = np.sin(3.4 * R - 2.0 * t + 2.0 * np.sin(TH)) ** 2
    em_field *= np.exp(-R / 5.6)
    em_field *= 0.65 + 0.35 * R_res

    # Plasmafilamentierung
    filaments = (
        np.sin(12.0 * X + 4.0 * np.sin(Y) + 2.5 * t)
        * np.cos(10.0 * Y - 3.0 * np.sin(X) - 1.8 * t)
    )
    filaments = np.abs(filaments)
    filaments *= np.exp(-R / 4.9)
    filaments *= R_res

    # Strahlungshülle
    radiation_shell = np.exp(-((R - 3.65) ** 2) / (2 * 0.82 ** 2))
    radiation_shell *= 0.65 + 0.35 * np.sin(7 * TH + t) ** 2

    # Verlustnebel
    loss_cloud = np.exp(-R / 4.0) * (0.8 + 0.2 * np.sin(2.0 * R - t))

    # Gesamtfeld
    field = (
        E["EM"]        * 1.25 * em_field +
        E["wellen"]    * 1.75 * wake +
        E["kinetisch"] * 1.65 * laser_wave +
        E["thermisch"] * 1.10 * plasma_ring +
        E["strahlung"] * 1.00 * radiation_shell +
        E["verlust"]   * 0.35 * loss_cloud +
        0.18 * filaments
    )

    # Kopplungspunkt: Laser trifft Plasma
    coupling = np.exp(-(X ** 2 + (Y - 0.95) ** 2) / (2 * 0.58 ** 2))
    field += 1.55 * R_res * coupling

    # Normieren
    field -= field.min()
    field /= field.max() + 1e-9

    return field, E


# -----------------------------
# 6. Messsignal / Äquivalent
# -----------------------------
def equivalent_signal(t, E):
    """
    Erzeugt ein einzelnes Messsignal wie Oszilloskop/Preislinie:
    Mischung aus Energieanteilen, Resonanz und Plasmawelle.
    """

    signal = (
        0.85 * E["wellen"]    * np.sin(2.8 * t)
        + 0.70 * E["EM"]      * np.sin(4.1 * t + 0.6)
        + 0.65 * E["kinetisch"] * np.sin(6.3 * t + 1.1)
        + 0.35 * E["strahlung"] * np.sin(9.0 * t)
        - 0.25 * E["verlust"] * np.cos(2.0 * t)
    )

    # Resonanzspitze
    spike = R_res * np.exp(-((np.sin(0.45 * t)) ** 2) / 0.035) * 0.25

    return signal + spike


# -----------------------------
# 7. Plot Layout
# -----------------------------
fig = plt.figure(figsize=(14, 8))

gs = fig.add_gridspec(
    2, 2,
    width_ratios=[1.35, 1.0],
    height_ratios=[1.0, 0.42],
    wspace=0.22,
    hspace=0.28
)

ax_field = fig.add_subplot(gs[:, 0])
ax_energy = fig.add_subplot(gs[0, 1])
ax_signal = fig.add_subplot(gs[1, 1])

initial_field, initial_E = make_field(0)

img = ax_field.imshow(
    initial_field,
    extent=[-space, space, -space, space],
    origin="lower",
    cmap="magma",
    interpolation="bilinear",
    vmin=0,
    vmax=1
)

ax_field.set_title("Querschnitt: Laser → Plasma → Welle → Feld → Strahlung")
ax_field.set_xlabel("x / Querschnitt")
ax_field.set_ylabel("y / Laserachse")

# Ring und Achse markieren
theta = np.linspace(0, 2 * np.pi, 500)
ax_field.plot(2.2 * np.cos(theta), 2.2 * np.sin(theta), linewidth=1.0, alpha=0.55)
ax_field.plot([0, 0], [-space, space], linestyle="--", linewidth=0.9, alpha=0.45)

energy_text = ax_field.text(
    -5.75, 5.55,
    "",
    fontsize=8.5,
    va="top",
    bbox=dict(boxstyle="round", alpha=0.28)
)

# Rechte Energie-Kurven vorbereiten
names = ["thermisch", "kinetisch", "EM", "wellen", "strahlung", "verlust"]
history = {name: [] for name in names}
signal_history = []
time_history = []

energy_lines = {}
for name in names:
    line, = ax_energy.plot([], [], linewidth=1.4, label=f"E_{name}")
    energy_lines[name] = line

sum_line, = ax_energy.plot([], [], linewidth=2.2, linestyle="--", label="Summe ≈ E_Laser")

ax_energy.set_title("Energie-Äquivalent: Linien/Wellen/Ausschläge")
ax_energy.set_xlim(0, history_len)
ax_energy.set_ylim(0, 1.1)
ax_energy.set_xlabel("Zeitfenster")
ax_energy.set_ylabel("normierte Energie")
ax_energy.grid(True, alpha=0.25)
ax_energy.legend(loc="upper right", fontsize=8)

# Unteres Oszi-Signal
signal_line, = ax_signal.plot([], [], linewidth=1.8, label="Messsignal Ψ(t)")
res_line, = ax_signal.plot([], [], linewidth=1.2, linestyle="--", label="Resonanzniveau")

ax_signal.set_title("Oszilloskop-Äquivalent: Plasmaantwort / Resonanzsignal")
ax_signal.set_xlim(0, history_len)
ax_signal.set_ylim(-0.65, 0.95)
ax_signal.set_xlabel("Zeitfenster")
ax_signal.set_ylabel("Ausschlag")
ax_signal.grid(True, alpha=0.25)
ax_signal.legend(loc="upper right", fontsize=8)

plt.colorbar(img, ax=ax_field, label="normierte Feld-/Energieintensität")


# -----------------------------
# 8. Animation
# -----------------------------
def update(frame):
    t = frame * 0.065

    field, E = make_field(frame)
    img.set_data(field)

    # Historie auffüllen
    time_history.append(frame)
    for name in names:
        history[name].append(E[name])

    sig = equivalent_signal(t, E)
    signal_history.append(sig)

    # Länge begrenzen
    if len(time_history) > history_len:
        time_history.pop(0)
        signal_history.pop(0)
        for name in names:
            history[name].pop(0)

    xs = np.arange(len(time_history))

    # Energie-Linien aktualisieren
    for name in names:
        energy_lines[name].set_data(xs, history[name])

    # Summe sollte nahe 1 bleiben
    sums = np.zeros(len(xs))
    for name in names:
        sums += np.array(history[name])

    sum_line.set_data(xs, sums)

    ax_energy.set_xlim(0, history_len)

    # Signal aktualisieren
    signal_line.set_data(xs, signal_history)
    res_line.set_data(xs, np.ones(len(xs)) * R_res * 0.45)

    ax_signal.set_xlim(0, history_len)

    total = sum(E.values())

    energy_text.set_text(
        f"f_Laser = {f_laser:.2f}\n"
        f"f_Plasma = {f_plasma:.2f}\n"
        f"Resonanz = {R_res:.2f}\n\n"
        f"E_Laser ≈ {total:.2f}\n"
        f"E_thermisch = {E['thermisch']:.2f}\n"
        f"E_kinetisch = {E['kinetisch']:.2f}\n"
        f"E_EM        = {E['EM']:.2f}\n"
        f"E_Wellen    = {E['wellen']:.2f}\n"
        f"E_Strahlung = {E['strahlung']:.2f}\n"
        f"E_Verlust   = {E['verlust']:.2f}\n\n"
        "Bilanz:\n"
        "E_Laser = Σ E_Anteile"
    )

    return (
        [img, energy_text, sum_line, signal_line, res_line]
        + list(energy_lines.values())
    )


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
# Optional speichern
# -----------------------------
# Für GIF:
# pip install pillow
# ani.save("laser_plasma_oszi.gif", writer="pillow", fps=24)
#
# Für MP4 brauchst du ffmpeg:
# ani.save("laser_plasma_oszi.mp4", writer="ffmpeg", fps=30)