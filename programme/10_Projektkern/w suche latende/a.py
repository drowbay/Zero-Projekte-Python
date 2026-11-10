# ============================================================
# ZERO / KAUSAL-LATENTE STRUKTUR v0.03-A
# TEST A: NORMALES SIGNAL
#
# Keine pygame-Abhängigkeit
# Keine SDL-Abhängigkeit
# Keine numpy-Abhängigkeit
# Keine matplotlib-Abhängigkeit
#
# Änderung gegenüber v0.02:
#
# G = Richtung von Δj
# S = Stärke |Δj|
#
# Ereignis:
#       S >= adaptive Schwelle T
#
# Die Richtungsänderung ist KEINE Voraussetzung mehr.
# ============================================================

import math
import time


# ============================================================
# TEST A — NORMALE PARAMETER
# ============================================================

STEPS = 180
DT = 0.10

BASE = 1.0

AMPLITUDE = 0.75
OMEGA = 0.18

OMEGA_2 = 0.043
AMPLITUDE_2 = 0.25

NOISE = 0.025

THRESHOLD_MIN = 0.025
THRESHOLD_SIGMA = 2.0

WINDOW = 12


# ============================================================
# DETERMINISTISCHES RAUSCHEN
# ============================================================

def pseudo_noise(n):

    value = math.sin(n * 12.9898) * 43758.5453

    fraction = value - math.floor(value)

    return (fraction * 2.0 - 1.0) * NOISE


# ============================================================
# SIGNAL j(t)
# ============================================================

def signal(t, n):

    s1 = (
        AMPLITUDE
        * math.sin(OMEGA * t)
    )

    s2 = (
        AMPLITUDE_2
        * math.sin(
            OMEGA_2 * t + 0.7
        )
    )

    noise = pseudo_noise(n)

    return BASE + s1 + s2 + noise


# ============================================================
# Δj
# ============================================================

def delta_signal(current, previous):

    return current - previous


# ============================================================
# MITTELWERT
# ============================================================

def mean(values):

    if not values:
        return 0.0

    return sum(values) / len(values)


# ============================================================
# STANDARDABWEICHUNG
# ============================================================

def sigma(values):

    if len(values) < 2:
        return 0.0

    m = mean(values)

    variance = sum(
        (x - m) ** 2
        for x in values
    ) / len(values)

    return math.sqrt(variance)


# ============================================================
# ADAPTIVE SCHWELLE
# ============================================================

def adaptive_threshold(history):

    if len(history) < 3:
        return THRESHOLD_MIN

    values = history[-WINDOW:]

    local_sigma = sigma(values)

    threshold = (
        THRESHOLD_SIGMA
        * local_sigma
    )

    return max(
        THRESHOLD_MIN,
        threshold
    )


# ============================================================
# G — RICHTUNG
# ============================================================

def get_G(delta):

    if delta > 0:
        return 1

    if delta < 0:
        return -1

    return 0


# ============================================================
# S — STÄRKE
# ============================================================

def get_S(delta):

    return abs(delta)


# ============================================================
# w
# ============================================================

def update_w(w, G):

    return w + G


# ============================================================
# HAUPTSIMULATION
# ============================================================

def run_simulation():

    print()
    print("=" * 68)
    print(" ZERO / KAUSAL-LATENTE STRUKTUR v0.03-A")
    print(" TEST A — NORMALES SIGNAL")
    print("=" * 68)
    print()

    print("Parameter:")
    print(f"  Amplitude : {AMPLITUDE}")
    print(f"  Noise     : {NOISE}")
    print(f"  dt        : {DT}")
    print(f"  Schritte  : {STEPS}")
    print()

    previous = signal(
        0.0,
        0
    )

    delta_history = []

    w = 0

    event_times = []
    event_data = []

    for n in range(
        1,
        STEPS + 1
    ):

        t = n * DT

        current = signal(
            t,
            n
        )

        delta = delta_signal(
            current,
            previous
        )

        delta_history.append(
            delta
        )

        # --------------------------------------------
        # Neue Größen
        # --------------------------------------------

        G = get_G(delta)

        S = get_S(delta)

        # --------------------------------------------
        # Adaptive Schwelle
        # --------------------------------------------

        T = adaptive_threshold(
            delta_history
        )

        # --------------------------------------------
        # Ereignis
        #
        # NUR Stärke entscheidet.
        # Keine Richtungswechsel-Bedingung.
        # --------------------------------------------

        event = (
            S >= T
        )

        # --------------------------------------------
        # w aktualisieren
        # --------------------------------------------

        w = update_w(
            w,
            G
        )

        # --------------------------------------------
        # Ereignisdaten speichern
        # --------------------------------------------

        if event:

            if event_times:

                tau = (
                    t
                    - event_times[-1]
                )

            else:

                tau = None

            event_times.append(t)

            event_data.append({
                "t": t,
                "G": G,
                "S": S,
                "T": T,
                "w": w,
                "tau": tau
            })

        # --------------------------------------------
        # normale Ausgabe
        # --------------------------------------------

        marker = "EVENT" if event else ""

        print(
            f"{n:03d} "
            f"t={t:6.2f} "
            f"j={current:7.3f} "
            f"dj={delta:+7.4f} "
            f"G={G:+2d} "
            f"S={S:7.4f} "
            f"T={T:7.4f} "
            f"w={w:4d} "
            f"{marker}"
        )

        previous = current

    return event_data


# ============================================================
# AUSWERTUNG
# ============================================================

def show_results(event_data):

    print()
    print("=" * 68)
    print(" EREIGNIS-ANALYSE — TEST A")
    print("=" * 68)
    print()

    print(
        f"Anzahl Ereignisse: {len(event_data)}"
    )

    print()

    print(
        " Nr. |    t |  G |       S |       T |   w |    τ"
    )

    print(
        "-" * 68
    )

    pauses = []

    positive = 0
    negative = 0

    for i, event in enumerate(
        event_data,
        start=1
    ):

        tau = event["tau"]

        if tau is not None:

            pauses.append(tau)

            tau_text = f"{tau:6.2f}"

        else:

            tau_text = "   ---"

        if event["G"] > 0:
            positive += 1

        elif event["G"] < 0:
            negative += 1

        print(
            f"{i:4d} | "
            f"{event['t']:5.2f} | "
            f"{event['G']:+2d} | "
            f"{event['S']:7.4f} | "
            f"{event['T']:7.4f} | "
            f"{event['w']:4d} | "
            f"{tau_text}"
        )

    print()

    print("Richtungsverteilung:")
    print(f"  G = +1 : {positive}")
    print(f"  G = -1 : {negative}")

    if pauses:

        print()

        print(
            f"Mittlere Pause : "
            f"{mean(pauses):.4f}"
        )

        print(
            f"Kleinste Pause : "
            f"{min(pauses):.4f}"
        )

        print(
            f"Größte Pause   : "
            f"{max(pauses):.4f}"
        )

    else:

        print(
            "\nKeine Pausen messbar."
        )


# ============================================================
# START
# ============================================================

def main():

    start = time.time()

    event_data = run_simulation()

    show_results(
        event_data
    )

    elapsed = (
        time.time()
        - start
    )

    print()
    print("=" * 68)
    print(" TEST A BEENDET")
    print("=" * 68)

    print(
        f"Laufzeit: {elapsed:.3f} Sekunden"
    )

    print()
    print("Parameter dieses Tests bleiben unverändert.")
    print("Dies ist unsere Referenzmessung für B und C.")
    print()


if __name__ == "__main__":
    main()