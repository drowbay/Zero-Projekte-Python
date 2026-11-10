
# ============================================================
# Zero-Lumÿè Feld-zu-Materie Übergang
# ------------------------------------------------------------
# Idee aus dem Chat:
#
# Unsichtbare Feldschwingung / Feldenergie
#        ↓ Kopplung
# Elektronen / Dipole reagieren
#        ↓ Relaxation / Energieübertragung
# Atomgitter schwingt stärker
#        ↓
# sichtbare Materialbewegung / Wärme / Schall / Vibration
#
# Physikalische Basis:
# - Feldschwingung: z.B. elektromagnetisches Feld
# - Kopplung: Feld wirkt auf geladene Teilchen oder Dipole
# - Materie-Reaktion: Elektronen-/Dipol-Anregung
# - Phononen: kollektive Gitterschwingung im Material
#
# Wichtig:
# Dies ist ein anschauliches Lehr-/Ideenmodell.
# Kein vollständiger Quantenfeld- oder Festkörper-Solver.
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# ============================================================
# 1. Einstellungen
# ============================================================

np.random.seed(11)

# Raumgitter
N = 220
x = np.linspace(0, 1, N)

# Animation
frames = 900
dt = 0.035

# Feldparameter
field_frequency = 8.0       # Frequenz der unsichtbaren Feldschwingung
field_speed = 0.55          # Ausbreitungsgeschwindigkeit der Feldwelle
field_strength = 1.0        # Feldamplitude

# Materie/Kopplung
coupling_g = 0.075          # Kopplungsstärke Feld -> Materie
damping = 0.035             # Dämpfung der Materialschwingung
spring_k = 0.22             # Nachbarschaftskopplung im Materialgitter
mass = 1.0

# Thermalisierung / Wärme
heat_gain = 0.020           # wie stark Materialbewegung Wärme erzeugt
heat_decay = 0.003          # kleine Abkühlung / Verlust


# ============================================================
# 2. Materialzustände
# ============================================================

# Elektronen-/Dipol-Reaktion:
# "polarization" ist hier die Antwort der Materie auf das Feld.
polarization = np.zeros(N)
polarization_velocity = np.zeros(N)

# Gitterauslenkung:
# phonon_u ist die sichtbare/kollektive Materialschwingung.
phonon_u = np.zeros(N)
phonon_v = np.zeros(N)

# Wärme/Unordnung:
# heat misst grob, wie viel Energie in ungeordnete Bewegung überging.
heat = np.zeros(N)


# ============================================================
# 3. Hilfsfunktionen
# ============================================================

def incoming_field(x, t):
    """
    Unsichtbare Feldschwingung.
    Man kann sie sich als elektromagnetische Welle vorstellen.

    Hier als laufende Sinuswelle mit Hüllkurve.
    """
    wave = np.sin(2 * np.pi * field_frequency * (x - field_speed * t))

    # Hüllkurve, damit es wie ein Feldpaket aussieht
    center = (0.15 + field_speed * t) % 1.2
    envelope = np.exp(-((x - center) ** 2) / (2 * 0.055 ** 2))

    return field_strength * wave * envelope


def laplacian(arr):
    """
    Diskrete zweite Ableitung.
    Beschreibt Nachbarschaftskopplung im Material.
    """
    out = np.zeros_like(arr)
    out[1:-1] = arr[2:] - 2 * arr[1:-1] + arr[:-2]
    return out


def total_energy(field, pol, pol_v, u, v, heat):
    """
    Nur eine grobe Energieanzeige für das Lehrmodell.
    Keine exakte konservative Hamilton-Funktion.
    """
    e_field = np.mean(field ** 2)
    e_pol = np.mean(pol ** 2 + pol_v ** 2)
    e_phonon = np.mean(u ** 2 + v ** 2)
    e_heat = np.mean(heat)
    return e_field, e_pol, e_phonon, e_heat


# ============================================================
# 4. Plot vorbereiten
# ============================================================

fig, axes = plt.subplots(4, 1, figsize=(10, 9), sharex=True)
fig.suptitle("Feldschwingung → Materie-Reaktion → Phononen → Wärme", fontsize=14)

ax_field, ax_pol, ax_phonon, ax_heat = axes

line_field, = ax_field.plot(x, np.zeros(N), linewidth=2)
line_pol, = ax_pol.plot(x, polarization, linewidth=2)
line_phonon, = ax_phonon.plot(x, phonon_u, linewidth=2)
line_heat, = ax_heat.plot(x, heat, linewidth=2)

ax_field.set_ylabel("Feld F")
ax_pol.set_ylabel("Reaktion P")
ax_phonon.set_ylabel("Gitter u")
ax_heat.set_ylabel("Wärme H")
ax_heat.set_xlabel("Materialposition x")

ax_field.set_title("1. Unsichtbare Feldschwingung")
ax_pol.set_title("2. Elektronen-/Dipol-Reaktion durch Kopplung")
ax_phonon.set_title("3. Gitterschwingung / Phonon-artige Bewegung")
ax_heat.set_title("4. Thermalisierung: Energie verteilt sich als Wärme")

for ax in axes:
    ax.grid(True, alpha=0.25)
    ax.set_xlim(0, 1)

ax_field.set_ylim(-1.1, 1.1)
ax_pol.set_ylim(-1.3, 1.3)
ax_phonon.set_ylim(-1.3, 1.3)
ax_heat.set_ylim(0, 0.8)

info = ax_field.text(
    0.01,
    0.82,
    "",
    transform=ax_field.transAxes,
    fontsize=10,
    bbox=dict(facecolor="white", alpha=0.75, edgecolor="none")
)


# ============================================================
# 5. Animationsschritt
# ============================================================

def update(frame):
    global polarization, polarization_velocity
    global phonon_u, phonon_v, heat

    t = frame * dt

    # --------------------------------------------------------
    # A) Feldschwingung
    # --------------------------------------------------------
    field = incoming_field(x, t)

    # --------------------------------------------------------
    # B) Feld koppelt an Materie
    # --------------------------------------------------------
    # Vereinfachtes Modell:
    # polarization wird vom Feld getrieben, aber gedämpft.
    # Das steht für Elektronenhülle / Dipol / Ladungsträger-Antwort.
    pol_force = coupling_g * field - 0.55 * polarization - damping * polarization_velocity
    polarization_velocity += pol_force * dt
    polarization += polarization_velocity * dt

    # --------------------------------------------------------
    # C) Materie-Reaktion treibt Gitterschwingung
    # --------------------------------------------------------
    # Polarisation gibt Energie an das Materialgitter weiter.
    # Nachbarschaftskopplung erzeugt wellenartige Ausbreitung.
    phonon_force = (
        spring_k * laplacian(phonon_u)
        + 0.65 * polarization
        - damping * phonon_v
    )

    phonon_v += phonon_force * dt
    phonon_u += phonon_v * dt

    # feste Randbedingungen
    phonon_u[0] = 0
    phonon_u[-1] = 0
    phonon_v[0] = 0
    phonon_v[-1] = 0

    # --------------------------------------------------------
    # D) Geordnete Schwingung wird teilweise zu Wärme
    # --------------------------------------------------------
    # Wärme wächst dort, wo viel Bewegung/Gradient entsteht.
    local_motion = phonon_v ** 2 + 0.5 * laplacian(phonon_u) ** 2
    heat += heat_gain * local_motion * dt
    heat -= heat_decay * heat * dt
    heat = np.clip(heat, 0, None)

    # --------------------------------------------------------
    # E) Anzeige aktualisieren
    # --------------------------------------------------------
    line_field.set_ydata(field)
    line_pol.set_ydata(polarization)
    line_phonon.set_ydata(phonon_u)
    line_heat.set_ydata(heat)

    e_field, e_pol, e_phonon, e_heat = total_energy(
        field,
        polarization,
        polarization_velocity,
        phonon_u,
        phonon_v,
        heat
    )

    info.set_text(
        f"Kopplung g = {coupling_g:.3f} | Dämpfung = {damping:.3f}\n"
        f"E Feld={e_field:.3f}  P={e_pol:.3f}  Phonon={e_phonon:.3f}  Wärme={e_heat:.3f}"
    )

    return line_field, line_pol, line_phonon, line_heat, info


# ============================================================
# 6. Start
# ============================================================

ani = FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=30,
    blit=True
)

plt.tight_layout()
plt.show()
