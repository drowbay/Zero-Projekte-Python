# ============================================================
# PHASENHERZ-KERN v0.5 VEKTORISIERT
# ZERO ARC-1 / Kern - Zwischenraum - Schale - Worldtour
#
# Baut auf v0.4 GESTALTET auf. Raumaufteilung und Mathe-Kern
# sind unveraendert - nur die Feldberechnung wurde umgebaut.
#
# Aenderungen v0.4 -> v0.5:
# - Feldberechnung komplett mit NumPy vektorisiert.
#   Vorher: raw_energy_at() wurde pro Zelle bis zu 10x aufgerufen
#   (1x direkt + 4x fuer Gradient + 5x fuer Laplace), bei 41x21
#   Zellen also ~8.600 Funktionsaufrufe PRO FRAME.
#   Jetzt: Energiefeld (inkl. 1 Zelle Rand) wird einmal pro Frame
#   als NumPy-Array berechnet, Gradient/Laplace folgen per
#   Array-Shift (zentrale Differenzen), Symbolwahl per np.select.
# - Drift per np.random.uniform auf dem ganzen Gitter statt
#   random.uniform() pro Zelle.
# - Tote/ungenutzte Stellen markiert (H_LIFT, WORLDTOUR_RADIUS,
#   konstante Resonanz, siehe Kommentare unten).
#
# Innenraum:       Core / Phasenherz
# Zwischenraum:    Uebergang X <-> H / Resonanzbruecke
# Aussenraum:      Schale / Weltkontakt / Worldtour-Interaktion
# Friedliche Logik: bauen, reparieren, messen, craften, interagieren
#
# Hinweis:
# Modellphysik / Mathematik-Demo / keine reale Energieerzeugung.
# ============================================================

import math
import time
import os

import numpy as np

# ----------------------------
# Einstellungen
# ----------------------------

WIDTH = 41
HEIGHT = 21
STEPS = 500
DELAY = 0.08

# Phasenherz-Puls
A = 1.0
OMEGA = 0.22
OMEGA_0 = 0.22       # Eigenfrequenz des Phasenherz-Kerns
SIGMA = 0.08         # Resonanzbreite
PHI = 0.0

# Hinweis: OMEGA == OMEGA_0, daher ist resonance_factor(OMEGA, OMEGA_0, SIGMA)
# konstant 1.0 (perfekte Resonanz). R bleibt dadurch ueber den gesamten
# Lauf bei 1.0 - das ist mathematisch korrekt, aber falls "Resonanz R"
# sich im Display sichtbar veraendern soll, muesste OMEGA z.B. mit der
# Zeit leicht "atmen" (z.B. OMEGA + 0.01*sin(t*...)).

# Kopplung
K0 = 1.0
D_VECTOR = (1.0, 0.35)
A_VECTOR = (1.0, 0.0)

# Hidden Geometry / Kernel-Raum
H_LIFT = 0.68        # nur fuer Anzeige, geht nicht in die Feldformeln ein
H_GAIN = 0.30
H_RADIUS = 5.0
GAMMA = 0.58

# Gestaltung: Innen - Zwischen - Aussen
CORE_RADIUS = 2.2
INNER_RING = 4.4
BETWEEN_RING = 6.4
OUTER_SHELL = 9.2

# WORLDTOUR_RADIUS war in v0.4 definiert, aber in keiner Formel und
# keiner Anzeige verwendet (toter Wert). Die "WORLD"-Zone ist einfach
# alles mit r > OUTER_SHELL, unabhaengig von diesem Wert. Auskommentiert
# stehen lassen, bis klar ist, ob z.B. eine begrenzte Worldtour-Zone
# (OUTER_SHELL < r <= WORLDTOUR_RADIUS) gewollt ist.
# WORLDTOUR_RADIUS = 11.0

# Friedliche Worldtour-Module
UTILITY_OBJECT = {
    "item": "hammer",
    "type": "cross_game_utility_tool",
    "non_combat": True,
    "core_identity": ["repair", "build", "shape", "assemble", "interact"],
    "roles": [
        "crafting",
        "mining",
        "repair",
        "construction",
        "resource_processing",
        "engineering",
        "calibration",
        "measurement"
    ],
    "earnable_ingame": True
}

WORLD_RULE = "Alles Sinnvolle ist erspielbar: bauen, helfen, lernen, finden, reparieren."

# Zustands-Echo
ECHO_DECAY = 0.965
ECHO_GAIN = 0.035

# Feld
DRIFT = 0.015

# Energie
ETA_MAX = 0.92       # Schutzdeckel gegen Perpetuum-Mobile-Quatsch

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
    d = normalize(d_vec)
    a = normalize(a_vec)
    return K0 * abs(dot(d, a))


def resonance_factor(omega, omega0, sigma):
    if sigma == 0:
        return 0.0
    return 1.0 / (1.0 + ((omega - omega0) / sigma) ** 2)


def phase_heart_pulse(t):
    return A * math.sin(OMEGA * t + PHI)


def rbf_kernel(r, center, gamma):
    # np.exp statt math.exp, damit r sowohl ein float als auch ein
    # NumPy-Array sein darf (wird unten fuer das ganze Gitter genutzt).
    return np.exp(-gamma * ((r - center) ** 2))


def bar(value, width=20):
    value = max(0.0, min(1.0, value))
    filled = int(value * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"

# ----------------------------
# Gitter-Vorberechnung (frame-unabhaengig)
# ----------------------------
# Alles, was nur von der Geometrie (x, y) abhaengt und sich ueber die
# gesamte Laufzeit nicht aendert, wird hier EINMAL fuer das ganze
# Gitter berechnet - inklusive 1 Zelle Rand rundherum, damit Gradient
# und Laplace per zentraler Differenz ohne Sonderfaelle funktionieren.

_CX = WIDTH // 2
_CY = HEIGHT // 2

_DX, _DY = np.meshgrid(
    np.arange(-1, WIDTH + 1) - _CX,
    np.arange(-1, HEIGHT + 1) - _CY,
)
_R = np.sqrt(_DX * _DX + _DY * _DY)
_R_SAFE = np.where(_R == 0, 1.0, _R)

_D_NORM = normalize(D_VECTOR)
_DIRECTION_BIAS = np.where(
    _R == 0,
    0.0,
    np.abs((_DX / _R_SAFE) * _D_NORM[0] + (_DY / _R_SAFE) * _D_NORM[1]),
)

# Zonen-Masken (gleiche Grenzen wie die alte zone_name()-Funktion)
_CORE_MASK = _R <= CORE_RADIUS
_INNER_MASK = (_R > CORE_RADIUS) & (_R <= INNER_RING)
_BETWEEN_MASK = (_R > INNER_RING) & (_R <= BETWEEN_RING)
_SHELL_MASK = (_R > BETWEEN_RING) & (_R <= OUTER_SHELL)
_WORLD_MASK = _R > OUTER_SHELL

_BRIDGE_MASK = (_R > INNER_RING) & (_R < BETWEEN_RING)
_SHELL_BAND_MASK = (_R > OUTER_SHELL - 0.7) & (_R < OUTER_SHELL + 0.7)

# Hidden-Geometry-Basis haengt nur von r ab -> einmal vorberechnen
_HIDDEN_RING = rbf_kernel(_R, H_RADIUS, GAMMA)
_HIDDEN_CORE = rbf_kernel(_R, 0.0, 0.045)
_BETWEEN_BRIDGE = rbf_kernel(_R, BETWEEN_RING, 0.22)
_SHELL_SKIN = rbf_kernel(_R, OUTER_SHELL, 0.16)
_WAVE_FOLD = 0.5 + 0.5 * np.sin(_R * 1.7)

_HIDDEN_BASE = (
    _HIDDEN_RING * 0.58 + _HIDDEN_CORE * 0.18
    + _BETWEEN_BRIDGE * 0.16 + _SHELL_SKIN * 0.08
) * _WAVE_FOLD

# Inner-Masken (ohne Rand) - werden fuer Zonen-Mittelwerte und Symbole
# gebraucht, deshalb einmal zugeschnitten bereithalten.
_ZONE_MASKS_INNER = {
    "CORE": _CORE_MASK[1:-1, 1:-1],
    "INNER": _INNER_MASK[1:-1, 1:-1],
    "BETWEEN": _BETWEEN_MASK[1:-1, 1:-1],
    "SHELL": _SHELL_MASK[1:-1, 1:-1],
    "WORLD": _WORLD_MASK[1:-1, 1:-1],
}

_NOT_CENTER = np.ones((HEIGHT, WIDTH), dtype=bool)
_NOT_CENTER[_CY, _CX] = False

# ----------------------------
# Gestaltung: Strukturmetrik & Worldtour
# ----------------------------

def poetic_structure_metric(avg_core, avg_between, avg_shell):
    """
    Kleine Design-Metrik:
    Nicht nur viel Energie ist wichtig, sondern eine lesbare Ordnung.
    """
    balance = 1.0 - min(1.0, abs(avg_core - avg_shell))
    bridge = avg_between
    return max(0.0, min(1.0, 0.55 * bridge + 0.45 * balance))


def worldtour_unlock(avg_between, avg_shell, structure):
    """
    Friedlicher Fortschritt: keine Waffenlogik, sondern Werkzeug-/Lern-Freischaltungen.
    """
    if structure > 0.74 and avg_shell > 0.30:
        return "Worldtour: Engineering-Modul freigeschaltet durch Verstehen + Reparatur."
    if avg_between > 0.36:
        return "Worldtour: Zwischenraum stabil - neue Interaktion mit Werkbank/Station moeglich."
    if avg_shell > 0.28:
        return "Worldtour: Aussenraum antwortet - Sammeln, Messen, Craften verbessert."
    return "Worldtour: Grundweg aktiv - alles bleibt erspielbar, nichts wird erzwungen."

# ----------------------------
# Vektorisierte Feldberechnung
# ----------------------------

def compute_field(t, pulse, coupling, echo, resonance):
    """
    Berechnet Energie, Hidden-Feld H, sichtbares Feld 'visible',
    Gradient und Laplace fuer das GESAMTE Gitter in einem Schritt.

    Mathematisch identisch zur alten Zelle-fuer-Zelle-Variante
    (raw_energy_at + gradient_magnitude + laplacian), aber als
    NumPy-Arrays statt Python-Funktionsaufrufen pro Zelle.

    Rueckgabe (alle Arrays in Form HEIGHT x WIDTH, ohne Rand):
        energy   - geklammertes Energiefeld E in [0, 1]
        h        - geklammertes Hidden-Feld H in [0, 1]
        visible  - sichtbarer Feldanteil X (ungeklammert)
        grad     - |grad E| (zentrale Differenz)
        lap      - Laplace E (zentrale Differenz, VORZEICHEN behalten)
    """
    p = abs(pulse)

    wave = np.sin(_R * 0.9 - t * 0.35)
    visible = p * coupling * resonance
    visible = visible * (0.55 + 0.45 * wave) * (0.45 + 0.55 * _DIRECTION_BIAS)

    h = _HIDDEN_BASE * p * coupling * resonance

    shaped = np.zeros_like(_R)
    shaped[_CORE_MASK] = 0.26 + p * 0.34 + echo * 0.18
    shaped[_INNER_MASK] = 0.14 + p * 0.18
    shaped[_BETWEEN_MASK] = 0.22 + resonance * 0.20 + echo * 0.12
    shaped[_SHELL_MASK] = 0.12 + resonance * 0.12
    shaped[_WORLD_MASK] = 0.05 + echo * 0.05

    # Zwischenring: Bruecke zwischen sichtbarem Feld X und Hidden-Feld H
    if p > 0.22:
        visible = visible + np.where(_BRIDGE_MASK, 0.16, 0.0)
        h = h + np.where(_BRIDGE_MASK, 0.20, 0.0)

    # Aussen-Schale: Worldtour-Kontakt, nicht Kampf, sondern Interaktion
    if echo > 0.18:
        visible = visible + np.where(_SHELL_BAND_MASK, 0.10, 0.0)
        h = h + np.where(_SHELL_BAND_MASK, 0.08, 0.0)

    energy = visible + h * H_GAIN + echo * 0.35 + shaped
    energy = np.clip(energy, 0.0, 1.0)
    h = np.clip(h, 0.0, 1.0)

    # Gradient & Laplace per zentraler Differenz auf dem Rand-Array.
    # Das entspricht genau gradient_magnitude()/laplacian() aus v0.4,
    # nur fuer alle Zellen gleichzeitig.
    e0 = energy[1:-1, 1:-1]
    e_px = energy[1:-1, 2:]
    e_mx = energy[1:-1, :-2]
    e_py = energy[2:, 1:-1]
    e_my = energy[:-2, 1:-1]

    d_dx = (e_px - e_mx) / 2.0
    d_dy = (e_py - e_my) / 2.0
    grad = np.sqrt(d_dx * d_dx + d_dy * d_dy)
    lap = e_px + e_mx + e_py + e_my - 4.0 * e0

    return e0, h[1:-1, 1:-1], visible[1:-1, 1:-1], grad, lap


def symbol_grid(energy, h, lap_abs):
    """
    Vektorisierte Variante von symbol_from_values() fuer das gesamte
    Gitter. Reihenfolge der Bedingungen ist identisch zu v0.4 -
    np.select prueft von links nach rechts und nimmt die erste
    zutreffende.
    """
    default = np.full(energy.shape, " ", dtype="<U1")
    default[_ZONE_MASKS_INNER["CORE"]] = "o"
    default[_ZONE_MASKS_INNER["BETWEEN"]] = "~"
    default[_ZONE_MASKS_INNER["SHELL"]] = "="
    default[_ZONE_MASKS_INNER["WORLD"]] = "'"
    # INNER bleibt " " (wie im Original)

    return np.select(
        [
            lap_abs > 0.35,
            (h > 0.70) & (energy > 0.55),
            energy > 0.90,
            energy > 0.70,
            energy > 0.50,
            energy > 0.34,
            energy > 0.18,
        ],
        ["C", "H", "@", "#", "*", "+", "."],
        default=default,
    )


def build_field(t, pulse, coupling, echo, resonance):
    energy, h, visible, grad, lap = compute_field(t, pulse, coupling, echo, resonance)
    lap_abs = np.abs(lap)

    drift = np.random.uniform(-DRIFT, DRIFT, size=energy.shape)
    energy_drift = np.clip(energy + drift, 0.0, 1.0)

    symbols = symbol_grid(energy_drift, h, lap_abs)
    symbols[_CY, _CX] = "◆"
    lines = ["".join(row) for row in symbols]

    total_visible = visible[_NOT_CENTER].sum()
    total_hidden = h[_NOT_CENTER].sum()
    total_gradient = grad[_NOT_CENTER].sum()
    total_curvature = lap_abs[_NOT_CENTER].sum()
    samples = int(_NOT_CENTER.sum())

    avg_visible = total_visible / samples
    avg_hidden = total_hidden / samples
    avg_gradient = total_gradient / samples
    avg_curvature = total_curvature / samples
    zwischenraum = abs(avg_hidden - avg_visible)

    zone_avg = {}
    for key, mask in _ZONE_MASKS_INNER.items():
        m = mask & _NOT_CENTER
        count = int(m.sum())
        zone_avg[key] = float(energy_drift[m].sum() / max(1, count))

    structure = poetic_structure_metric(zone_avg["CORE"], zone_avg["BETWEEN"], zone_avg["SHELL"])

    return (
        lines,
        float(avg_visible),
        float(avg_hidden),
        float(zwischenraum),
        float(avg_gradient),
        float(avg_curvature),
        zone_avg,
        structure,
    )


def state_name(pulse, echo, hidden_level, curvature, structure):
    if structure > 0.78:
        return "O*  Objekt-Seele / Worldtour-Bruecke aktiv"
    if hidden_level > 0.55 and echo > 0.45:
        return "H*  Hidden Geometry aktiv"
    if curvature > 0.22:
        return "C*  Feldkruemmung / Laplace-Zone"
    if pulse > 0.65:
        return "S*  angeregter Zustand"
    if pulse > 0.15:
        return "S+  posdir / Aufbau"
    if pulse < -0.65:
        return "S-  negdir / Ausgleich"
    if pulse < -0.15:
        return "S~  Rueckphase / Entladung"
    return "S0  Grundzustand"


def energy_values(pulse, coupling, echo, hidden_avg, resonance, curvature, structure):
    e_in = abs(pulse) * 100.0

    storage_factor = 0.54
    storage_factor += hidden_avg * 0.18
    storage_factor += echo * 0.08
    storage_factor += resonance * 0.12
    storage_factor += structure * 0.06
    storage_factor -= curvature * 0.10
    storage_factor = max(0.0, min(0.95, storage_factor))

    e_stored = e_in * coupling * storage_factor

    out_factor = 0.68 + echo * 0.06 + resonance * 0.08 + structure * 0.03
    out_factor = max(0.0, min(0.95, out_factor))
    e_out = e_stored * out_factor

    if e_out > e_in * ETA_MAX:
        e_out = e_in * ETA_MAX

    loss = e_in - e_out
    return e_in, e_stored, e_out, loss, storage_factor, out_factor


def lyrik_line(pulse, echo, zwischenraum, grad, curvature, structure):
    if structure > 0.76:
        return "Der Kern hat eine Schale gefunden; zwischen ihnen beginnt die Welt zu antworten."
    if curvature > 0.18:
        return "Die Flaeche kruemmt sich: nicht wild, sondern nach Zahl und Richtung."
    if grad > 0.20:
        return "Das Feld hat Kanten bekommen; der Gradient zeigt, wo der Zustand kippt."
    if zwischenraum > 0.35 and echo > 0.45:
        return "Der sichtbare Raum schweigt, doch H faltet leise sein Licht."
    if echo > 0.60:
        return "Was einmal stark koppelte, klingt noch im Feld nach."
    if pulse > 0.65:
        return "Das Phasenherz hebt den Zustand wie eine Sonne im Kern."
    if pulse < -0.65:
        return "Die Gegenphase atmet aus und glaettet den alten Impuls."
    if zwischenraum > 0.22:
        return "Zwischen X und H liegt ein Raum, den nur Resonanz betritt."
    return "Der Kern ruht, doch unter der Flaeche wartet der naechste Takt."

# ----------------------------
# Hauptprogramm
# ----------------------------

def main():
    print("PHASENHERZ-KERN v0.5 VEKTORISIERT startet...")
    print("ZERO ARC-1 / Kern - Zwischenraum - Schale - Worldtour")
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

        (
            field,
            avg_x,
            avg_h,
            zwischenraum,
            avg_grad,
            avg_curv,
            zone_avg,
            structure,
        ) = build_field(t, pulse, coupling, zustands_echo, resonance)

        state = state_name(pulse, zustands_echo, avg_h, avg_curv, structure)

        e_in, e_stored, e_out, loss, storage_factor, out_factor = energy_values(
            pulse, coupling, zustands_echo, avg_h, resonance, avg_curv, structure
        )

        unlock_text = worldtour_unlock(zone_avg["BETWEEN"], zone_avg["SHELL"], structure)

        clear()
        print("============================================================")
        print("        PHASENHERZ-KERN v0.5 VEKTORISIERT / ZERO ARC-1")
        print("============================================================")
        print()
        print("Raumaufbau:")
        print("Innenraum     = Core / Phasenherz")
        print("Zwischenraum  = X <-> H / Resonanzbruecke")
        print("Aussenraum    = Schale / Worldtour-Kontakt")
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
        print("Zonen:")
        print("Core avg:          ", round(zone_avg["CORE"], 3), bar(zone_avg["CORE"]))
        print("Inner avg:         ", round(zone_avg["INNER"], 3), bar(zone_avg["INNER"]))
        print("Zwischen avg:      ", round(zone_avg["BETWEEN"], 3), bar(zone_avg["BETWEEN"]))
        print("Schale avg:        ", round(zone_avg["SHELL"], 3), bar(zone_avg["SHELL"]))
        print("World avg:         ", round(zone_avg["WORLD"], 3), bar(zone_avg["WORLD"]))
        print("Strukturordnung:   ", round(structure, 3), bar(structure))
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
        print("Worldtour-Regel:")
        print(WORLD_RULE)
        print(unlock_text)
        print("Utility-Objekt:    ", UTILITY_OBJECT["item"], "/", UTILITY_OBJECT["type"])
        print("Non-Combat:        ", UTILITY_OBJECT["non_combat"])
        print()
        print("Lyrik:")
        print(lyrik_line(pulse, zustands_echo, zwischenraum, avg_grad, avg_curv, structure))
        print()
        print("Legende:")
        print("◆ = Phasenherz-Kern")
        print("o = Innenraum/Core, ~ = Zwischenraum, = = Schale, ' = Welt")
        print("H = Hidden Geometry / Kernel-Raum")
        print("C = Feldkruemmung / Laplace-Zone")
        print("@ # * + . = Feldstaerke / Resonanz")
        print()
        print("Gestaltetes SpinFoam-Feld:")
        print()
        for line in field:
            print(line)
        print()
        print("Hinweis:")
        print("Mathematische Modell-Simulation, keine reale Energieerzeugung.")
        print("Abbruch mit STRG+C")
        print("============================================================")

        time.sleep(DELAY)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        print("Simulation beendet.")
        print("Phasenherz-Kern v0.5 VEKTORISIERT wurde sauber heruntergefahren. 💚")
