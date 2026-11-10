# ============================================================
# PHASENHERZ-KERN v0.3 MATH
# ZERO ARC-1 / Zustandsfeld-Simulation für Pydroid 3
#
# v0.3 bringt echte Mathematik rein:
# - Skalarprodukt:        K = K0 * |D^→ · A^→|
# - Winkel:               theta = arccos(...)
# - RBF/Gauss-Kernel:     H(r) = exp(-gamma * (r-r0)^2)
# - Resonanz:             R = 1 / (1 + ((omega-omega0)/sigma)^2)
# - Gradient-Näherung:    |grad E|
# - Laplace-Näherung:     ∇²E
# - Energiebegrenzung:    E_out <= E_in * eta_max
#
# Hinweis:
# Modellphysik / Mathematik-Demo / keine reale Energieerzeugung.
# ============================================================

import math
import time
import random
import os

# ----------------------------
# Einstellungen
# ----------------------------

WIDTH = 35
HEIGHT = 17
STEPS = 500
DELAY = 0.08

# Phasenherz-Puls
A = 1.0
OMEGA = 0.22
OMEGA_0 = 0.22       # Eigenfrequenz des Phasenherz-Kerns
SIGMA = 0.08         # Resonanzbreite
PHI = 0.0

# Kopplung
K0 = 1.0
D_VECTOR = (1.0, 0.35)
A_VECTOR = (1.0, 0.0)

# Hidden Geometry / Kernel-Raum
H_LIFT = 0.68
H_GAIN = 0.30
H_RADIUS = 5.0
GAMMA = 0.58         # Gauss-Kernel-Schärfe

# Zustands-Echo
ECHO_DECAY = 0.965
ECHO_GAIN = 0.035

# Feld
DRIFT = 0.015

# Energie
ETA_MAX = 0.92       # maximale erlaubte Rückgabequote, Schutz vor Perpetuum-Mobile-Quatsch

# ----------------------------
# Mathe-Hilfsfunktionen
# ----------------------------

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def normalize(v):
    x, y = v
    length = math.sqrt(x*x + y*y)
    if length == 0:
        return (0.0, 0.0)
    return (x / length, y / length)


def dot(a, b):
    return a[0]*b[0] + a[1]*b[1]


def angle_between(a, b):
    a = normalize(a)
    b = normalize(b)
    value = max(-1.0, min(1.0, dot(a, b)))
    return math.degrees(math.acos(value))


def coupling_strength(d_vec, a_vec):
    """
    Echte Vektormathematik:
    K = K0 * |D^→ · A^→|

    Wenn beide Richtungen gleich zeigen: K groß.
    Wenn sie quer stehen: K klein.
    """
    d = normalize(d_vec)
    a = normalize(a_vec)
    return K0 * abs(dot(d, a))


def resonance_factor(omega, omega0, sigma):
    """
    Resonanzformel:
    R = 1 / (1 + ((omega - omega0) / sigma)^2)

    Wenn omega nahe omega0 ist, geht R gegen 1.
    Wenn omega weit weg ist, wird R kleiner.
    """
    if sigma == 0:
        return 0.0
    return 1.0 / (1.0 + ((omega - omega0) / sigma) ** 2)


def phase_heart_pulse(t):
    """
    Harmonische Schwingung:
    P(t) = A * sin(omega*t + phi)
    """
    return A * math.sin(OMEGA * t + PHI)


def rbf_kernel(r, center, gamma):
    """
    Echter Gauss-/RBF-Kernel:
    H(r) = exp(-gamma * (r - center)^2)

    Das ist die mathematische Hidden-Geometry-Hebung X -> H.
    """
    return math.exp(-gamma * ((r - center) ** 2))


def hidden_geometry(r, pulse, coupling, resonance):
    """
    X -> H über Kernel-Raum.

    H kombiniert:
    - Ring-Kernel um H_RADIUS
    - Core-Kernel um Zentrum
    - Resonanzfaktor
    """
    hidden_ring = rbf_kernel(r, H_RADIUS, GAMMA)
    hidden_core = rbf_kernel(r, 0.0, 0.045)
    wave_fold = 0.5 + 0.5 * math.sin(r * 1.7)

    h_value = hidden_ring * 0.75 + hidden_core * 0.25
    h_value *= abs(pulse) * coupling * resonance
    h_value *= wave_fold

    return h_value


def state_name(pulse, echo, hidden_level, curvature):
    if hidden_level > 0.55 and echo > 0.45:
        return "H*  Hidden Geometry aktiv"
    elif curvature > 0.22:
        return "C*  Feldkruemmung / Laplace-Zone"
    elif pulse > 0.65:
        return "S*  angeregter Zustand"
    elif pulse > 0.15:
        return "S+  posdir / Aufbau"
    elif pulse < -0.65:
        return "S-  negdir / Ausgleich"
    elif pulse < -0.15:
        return "S~  Rueckphase / Entladung"
    else:
        return "S0  Grundzustand"


def symbol_from_values(e, h, curvature):
    if curvature > 0.35:
        return "C"
    elif h > 0.70 and e > 0.55:
        return "H"
    elif e > 0.90:
        return "@"
    elif e > 0.70:
        return "#"
    elif e > 0.50:
        return "*"
    elif e > 0.30:
        return "+"
    elif e > 0.13:
        return "."
    else:
        return " "


def bar(value, width=20):
    value = max(0.0, min(1.0, value))
    filled = int(value * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


# ----------------------------
# Feldberechnung
# ----------------------------

def raw_energy_at(x, y, t, pulse, coupling, echo, resonance):
    """
    Berechnet Feldenergie an einem Punkt.
    Daraus können wir später Gradient und Laplace ableiten.
    """
    cx = WIDTH // 2
    cy = HEIGHT // 2

    dx = x - cx
    dy = y - cy
    r = math.sqrt(dx*dx + dy*dy)

    wave = math.sin(r * 0.9 - t * 0.35)

    direction_bias = 0.0
    if r != 0:
        nx = dx / r
        ny = dy / r
        direction_bias = abs(dot((nx, ny), normalize(D_VECTOR)))

    # sichtbares Feld X
    visible = abs(pulse) * coupling * resonance
    visible *= (0.55 + 0.45 * wave)
    visible *= (0.45 + 0.55 * direction_bias)

    # Hidden-Feld H
    h = hidden_geometry(r, pulse, coupling, resonance)

    # Epot-Ring
    if 4.3 < r < 5.4 and abs(pulse) > 0.35:
        visible += 0.30
        h += 0.18

    energy = visible + h * H_GAIN + echo * 0.35
    return max(0.0, min(1.0, energy)), max(0.0, min(1.0, h)), visible


def gradient_magnitude(x, y, t, pulse, coupling, echo, resonance):
    """
    Numerische Gradient-Näherung:
    |grad E| ≈ sqrt((dE/dx)^2 + (dE/dy)^2)

    Zeigt, wie stark sich das Feld räumlich ändert.
    """
    e_plus_x, _, _ = raw_energy_at(x + 1, y, t, pulse, coupling, echo, resonance)
    e_minus_x, _, _ = raw_energy_at(x - 1, y, t, pulse, coupling, echo, resonance)
    e_plus_y, _, _ = raw_energy_at(x, y + 1, t, pulse, coupling, echo, resonance)
    e_minus_y, _, _ = raw_energy_at(x, y - 1, t, pulse, coupling, echo, resonance)

    d_dx = (e_plus_x - e_minus_x) / 2.0
    d_dy = (e_plus_y - e_minus_y) / 2.0

    return math.sqrt(d_dx*d_dx + d_dy*d_dy)


def laplacian(x, y, t, pulse, coupling, echo, resonance):
    """
    Numerische Laplace-Näherung:
    ∇²E ≈ E(x+1,y)+E(x-1,y)+E(x,y+1)+E(x,y-1)-4E(x,y)

    Das ist echte Feldmathematik.
    Hoher Betrag = starke lokale Krümmung / Strukturänderung.
    """
    e0, _, _ = raw_energy_at(x, y, t, pulse, coupling, echo, resonance)
    epx, _, _ = raw_energy_at(x + 1, y, t, pulse, coupling, echo, resonance)
    emx, _, _ = raw_energy_at(x - 1, y, t, pulse, coupling, echo, resonance)
    epy, _, _ = raw_energy_at(x, y + 1, t, pulse, coupling, echo, resonance)
    emy, _, _ = raw_energy_at(x, y - 1, t, pulse, coupling, echo, resonance)

    return epx + emx + epy + emy - 4.0 * e0


def build_field(t, pulse, coupling, echo, resonance):
    cx = WIDTH // 2
    cy = HEIGHT // 2

    lines = []

    total_visible = 0.0
    total_hidden = 0.0
    total_gradient = 0.0
    total_curvature = 0.0
    samples = 0

    for y in range(HEIGHT):
        row = ""
        for x in range(WIDTH):
            if x == cx and y == cy:
                row += "◆"
                continue

            energy, h, visible = raw_energy_at(x, y, t, pulse, coupling, echo, resonance)

            grad = gradient_magnitude(x, y, t, pulse, coupling, echo, resonance)
            lap = abs(laplacian(x, y, t, pulse, coupling, echo, resonance))

            # leichte Drift, aber klein, damit Mathe sichtbar bleibt
            energy += random.uniform(-DRIFT, DRIFT)
            energy = max(0.0, min(1.0, energy))

            total_visible += visible
            total_hidden += h
            total_gradient += grad
            total_curvature += lap
            samples += 1

            row += symbol_from_values(energy, h, lap)

        lines.append(row)

    avg_visible = total_visible / max(1, samples)
    avg_hidden = total_hidden / max(1, samples)
    avg_gradient = total_gradient / max(1, samples)
    avg_curvature = total_curvature / max(1, samples)

    zwischenraum = abs(avg_hidden - avg_visible)

    return lines, avg_visible, avg_hidden, zwischenraum, avg_gradient, avg_curvature


def energy_values(pulse, coupling, echo, hidden_avg, resonance, curvature):
    """
    Modellenergie mit mathematischer Begrenzung.

    E_in kommt vom Puls.
    Speicherfaktor hängt von Kopplung, Hidden Geometry, Echo, Resonanz ab.
    Krümmung kostet Energie.
    """
    e_in = abs(pulse) * 100.0

    storage_factor = 0.54
    storage_factor += hidden_avg * 0.18
    storage_factor += echo * 0.08
    storage_factor += resonance * 0.12
    storage_factor -= curvature * 0.10

    storage_factor = max(0.0, min(0.95, storage_factor))

    e_stored = e_in * coupling * storage_factor

    out_factor = 0.68 + echo * 0.06 + resonance * 0.08
    out_factor = max(0.0, min(0.95, out_factor))

    e_out = e_stored * out_factor

    # harter Energieerhaltungsdeckel
    if e_out > e_in * ETA_MAX:
        e_out = e_in * ETA_MAX

    loss = e_in - e_out

    return e_in, e_stored, e_out, loss, storage_factor, out_factor


def lyrik_line(pulse, echo, zwischenraum, grad, curvature):
    if curvature > 0.18:
        return "Die Flaeche kruemmt sich: nicht wild, sondern nach Zahl und Richtung."
    elif grad > 0.20:
        return "Das Feld hat Kanten bekommen; der Gradient zeigt, wo der Zustand kippt."
    elif zwischenraum > 0.35 and echo > 0.45:
        return "Der sichtbare Raum schweigt, doch H faltet leise sein Licht."
    elif echo > 0.60:
        return "Was einmal stark koppelte, klingt noch im Feld nach."
    elif pulse > 0.65:
        return "Das Phasenherz hebt den Zustand wie eine Sonne im Kern."
    elif pulse < -0.65:
        return "Die Gegenphase atmet aus und glättet den alten Impuls."
    elif zwischenraum > 0.22:
        return "Zwischen X und H liegt ein Raum, den nur Resonanz betritt."
    else:
        return "Der Kern ruht, doch unter der Flaeche wartet der nächste Takt."


# ----------------------------
# Hauptprogramm
# ----------------------------

def main():
    print("PHASENHERZ-KERN v0.3 MATH startet...")
    print("ZERO ARC-1 / X -> H / echte Mathe-Naeherungen")
    time.sleep(1.5)

    coupling = coupling_strength(D_VECTOR, A_VECTOR)
    theta = angle_between(D_VECTOR, A_VECTOR)
    resonance = resonance_factor(OMEGA, OMEGA_0, SIGMA)

    zustands_echo = 0.0

    for t in range(STEPS):
        pulse = phase_heart_pulse(t)

        new_resonance = coupling * abs(pulse) * resonance
        zustands_echo = zustands_echo * ECHO_DECAY + new_resonance * ECHO_GAIN
        zustands_echo = max(0.0, min(1.0, zustands_echo))

        field, avg_x, avg_h, zwischenraum, avg_grad, avg_curv = build_field(
            t, pulse, coupling, zustands_echo, resonance
        )

        state = state_name(pulse, zustands_echo, avg_h, avg_curv)

        e_in, e_stored, e_out, loss, storage_factor, out_factor = energy_values(
            pulse, coupling, zustands_echo, avg_h, resonance, avg_curv
        )

        clear()

        print("========================================================")
        print("        PHASENHERZ-KERN v0.3 MATH / ZERO ARC-1")
        print("========================================================")
        print()
        print("Zustandsraum:")
        print("Z = (x, y, z, w, t, D^→)")
        print()
        print("Mathe-Kern:")
        print("K       = K0 * |D^→ · A^→|")
        print("theta   = arccos((D^→·A^→)/(|D^→||A^→|))")
        print("H(r)    = exp(-gamma * (r-r0)^2)")
        print("R       = 1 / (1 + ((omega-omega0)/sigma)^2)")
        print("grad E  = sqrt((dE/dx)^2 + (dE/dy)^2)")
        print("lap E   = E_x+ + E_x- + E_y+ + E_y- - 4E")
        print()
        print("Aktueller Zustand:", state)
        print("Phasenpuls P(t):   ", round(pulse, 3), bar(abs(pulse)))
        print("Kopplung K:        ", round(coupling, 3), bar(coupling))
        print("Theta Winkel:      ", round(theta, 2), "Grad")
        print("Resonanz R:        ", round(resonance, 3), bar(resonance))
        print("D^→ Richtung:      ", D_VECTOR)
        print("A^→ Achse:         ", A_VECTOR)
        print()
        print("H_LIFT:            ", H_LIFT)
        print("GAMMA Kernel:      ", GAMMA)
        print("Zustands-Echo:     ", round(zustands_echo, 3), bar(zustands_echo))
        print("X sichtbar avg:    ", round(avg_x, 3), bar(avg_x))
        print("H hidden avg:      ", round(avg_h, 3), bar(avg_h))
        print("Zwischenraum ΔXH:  ", round(zwischenraum, 3), bar(zwischenraum))
        print("Gradient |∇E| avg: ", round(avg_grad, 3), bar(avg_grad))
        print("Laplace |∇²E| avg: ", round(avg_curv, 3), bar(avg_curv))
        print()
        print("E_in:              ", round(e_in, 2))
        print("E_stored:          ", round(e_stored, 2))
        print("E_out:             ", round(e_out, 2))
        print("Verlust:           ", round(loss, 2))
        print("Speicherfaktor:    ", round(storage_factor, 3))
        print("Outputfaktor:      ", round(out_factor, 3))
        print("Eta-Max Deckel:    ", ETA_MAX)
        print()
        print("Lyrik:")
        print(lyrik_line(pulse, zustands_echo, zwischenraum, avg_grad, avg_curv))
        print()
        print("Legende:")
        print("◆ = Phasenherz-Kern")
        print("H = Hidden Geometry / Kernel-Raum")
        print("C = Feldkruemmung / Laplace-Zone")
        print("@ # * + . = Feldstaerke / Resonanz")
        print()
        print("SpinFoam-Feld:")
        print()

        for line in field:
            print(line)

        print()
        print("Hinweis:")
        print("Mathematische Modell-Simulation, keine reale Energieerzeugung.")
        print("Abbruch mit STRG+C")
        print("========================================================")

        time.sleep(DELAY)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        print("Simulation beendet.")
        print("Phasenherz-Kern v0.3 MATH wurde sauber heruntergefahren. 💚")