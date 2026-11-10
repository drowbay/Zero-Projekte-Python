# ============================================================
# ZERO / KAUSAL-LATENTE STRUKTUR v0.03-C
# TEST C — RAUSCHFREIES SIGNAL
#
# PYDROID-SAFE
# KEIN PYGAME
# KEIN SDL
# KEIN NUMPY
# KEINE GRAFIK
#
# Vergleich:
#
# TEST A:
#   Amplitude = 0.75
#   Noise     = 0.025
#
# TEST B:
#   Amplitude = 1.50
#   Noise     = 0.025
#
# TEST C:
#   Amplitude = 0.75
#   Noise     = 0.0
#
# Nur das Rauschen wird gegenüber A entfernt.
#
# Ereignis:
#       S >= T
#
# G = Richtung von Δj
# S = Stärke |Δj|
# w = aufsummierte Richtung
# τ = Zeit zwischen Ereignissen
# ============================================================

import math
import time


# ============================================================
# TESTPARAMETER
# ============================================================

STEPS = 180
DT = 0.10

BASE = 1.0

# ============================================================
# NORMALE AMPLITUDE — wie bei TEST A
# ============================================================

AMPLITUDE = 0.75

OMEGA = 0.18

OMEGA_2 = 0.043
AMPLITUDE_2 = 0.25

# ============================================================
# TEST C:
# KOMPLETT OHNE RAUSCHEN
# ============================================================

NOISE = 0.0

# ============================================================
# ADAPTIVE SCHWELLE
# BLEIBT UNVERÄNDERT
# ============================================================

THRESHOLD_MIN = 0.025
THRESHOLD_SIGMA = 2.0

WINDOW = 12


# ============================================================
# DETERMINISTISCHES RAUSCHEN
#
# Bei NOISE = 0.0 liefert diese Funktion immer 0.
# ============================================================

def pseudo_noise(n):

    value = math.sin(
        n * 12.9898
    ) * 43758.5453

    fraction = (
        value
        - math.floor(value)
    )

    return (
        fraction * 2.0 - 1.0
    ) * NOISE


# ============================================================
# SIGNAL j(t)
# ============================================================

def signal(t, n):

    s1 = (
        AMPLITUDE
        * math.sin(
            OMEGA * t
        )
    )

    s2 = (
        AMPLITUDE_2
        * math.sin(
            OMEGA_2 * t + 0.7
        )
    )

    noise = pseudo_noise(
        n
    )

    return (
        BASE
        + s1
        + s2
        + noise
    )


# ============================================================
# Δj
# ============================================================

def delta_signal(
    current,
    previous
):

    return (
        current
        - previous
    )


# ============================================================
# MITTELWERT
# ============================================================

def mean(values):

    if not values:
        return 0.0

    return (
        sum(values)
        / len(values)
    )


# ============================================================
# STANDARDABWEICHUNG
# ============================================================

def sigma(values):

    if len(values) < 2:
        return 0.0

    m = mean(
        values
    )

    variance = sum(
        (x - m) ** 2
        for x in values
    ) / len(values)

    return math.sqrt(
        variance
    )


# ============================================================
# ADAPTIVE SCHWELLE
# ============================================================

def adaptive_threshold(
    history
):

    if len(history) < 3:

        return THRESHOLD_MIN

    values = history[
        -WINDOW:
    ]

    local_sigma = sigma(
        values
    )

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
#
# +1 = positive Änderung
# -1 = negative Änderung
#  0 = keine Änderung
# ============================================================

def get_G(delta):

    if delta > 0:

        return 1

    if delta < 0:

        return -1

    return 0


# ============================================================
# S — STÄRKE
#
# S = |Δj|
# ============================================================

def get_S(delta):

    return abs(
        delta
    )


# ============================================================
# w — AUFSUMMIERTE RICHTUNG
# ============================================================

def update_w(
    w,
    G
):

    return w + G


# ============================================================
# HAUPTSIMULATION
# ============================================================

def run_simulation():

    print()
    print("=" * 68)
    print(
        " ZERO / KAUSAL-LATENTE STRUKTUR v0.03-C"
    )
    print(
        " TEST C — RAUSCHFREIES SIGNAL"
    )
    print("=" * 68)
    print()

    print("Parameter:")
    print(
        f"  Amplitude : {AMPLITUDE}"
    )
    print(
        f"  Noise     : {NOISE}"
    )
    print(
        f"  dt        : {DT}"
    )
    print(
        f"  Schritte  : {STEPS}"
    )
    print(
        f"  Omega     : {OMEGA}"
    )
    print(
        f"  Schwelle  : "
        f"{THRESHOLD_SIGMA} × sigma"
    )

    print()

    print(
        "Kontrolle:"
    )

    print(
        "  Signalrauschen ist deaktiviert."
    )

    print(
        "  Das Signal besteht nur aus"
    )

    print(
        "  den beiden definierten"
    )

    print(
        "  Sinuskomponenten."
    )

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

        # ----------------------------------------
        # RICHTUNG G
        # ----------------------------------------

        G = get_G(
            delta
        )

        # ----------------------------------------
        # STÄRKE S
        # ----------------------------------------

        S = get_S(
            delta
        )

        # ----------------------------------------
        # ADAPTIVE SCHWELLE
        # ----------------------------------------

        T = adaptive_threshold(
            delta_history
        )

        # ----------------------------------------
        # EREIGNIS
        #
        # Nur die Stärke entscheidet.
        # ----------------------------------------

        event = (
            S >= T
        )

        # ----------------------------------------
        # w
        # ----------------------------------------

        w = update_w(
            w,
            G
        )

        # ----------------------------------------
        # EREIGNIS SPEICHERN
        # ----------------------------------------

        if event:

            if event_times:

                tau = (
                    t
                    - event_times[-1]
                )

            else:

                tau = None

            event_times.append(
                t
            )

            event_data.append({

                "t": t,

                "G": G,

                "S": S,

                "T": T,

                "w": w,

                "tau": tau
            })

        # ----------------------------------------
        # AUSGABE
        # ----------------------------------------

        if event:

            marker = "EVENT"

        else:

            marker = ""

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

def show_results(
    event_data
):

    print()
    print("=" * 68)
    print(
        " EREIGNIS-ANALYSE — TEST C"
    )
    print("=" * 68)
    print()

    print(
        f"Anzahl Ereignisse: "
        f"{len(event_data)}"
    )

    print()

    print(
        " Nr. |    t |  G |       S |       T |"
        "   w |    tau"
    )

    print(
        "-" * 68
    )

    pauses = []

    positive = 0
    negative = 0
    neutral = 0

    strengths = []

    for i, event in enumerate(
        event_data,
        start=1
    ):

        tau = event[
            "tau"
        ]

        if tau is not None:

            pauses.append(
                tau
            )

            tau_text = (
                f"{tau:6.2f}"
            )

        else:

            tau_text = (
                "   ---"
            )

        S = event[
            "S"
        ]

        strengths.append(
            S
        )

        G = event[
            "G"
        ]

        if G > 0:

            positive += 1

        elif G < 0:

            negative += 1

        else:

            neutral += 1

        print(
            f"{i:4d} | "
            f"{event['t']:5.2f} | "
            f"{G:+2d} | "
            f"{S:7.4f} | "
            f"{event['T']:7.4f} | "
            f"{event['w']:4d} | "
            f"{tau_text}"
        )

    # ========================================================
    # PAUSEN
    # ========================================================

    print()

    print(
        "PAUSEN"
    )

    print(
        "-" * 40
    )

    if pauses:

        for i, pause in enumerate(
            pauses,
            start=1
        ):

            print(
                f"{i:03d}: "
                f"{pause:.4f}"
            )

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
            "Keine Pausen messbar."
        )

    # ========================================================
    # SIGNALSTÄRKE
    # ========================================================

    print()

    print(
        "SIGNALSTÄRKE S = |Δj|"
    )

    print(
        "-" * 40
    )

    if strengths:

        print(
            f"Mittleres S : "
            f"{mean(strengths):.6f}"
        )

        print(
            f"Kleinstes S : "
            f"{min(strengths):.6f}"
        )

        print(
            f"Größtes S   : "
            f"{max(strengths):.6f}"
        )

    else:

        print(
            "Keine Ereignisse."
        )

    # ========================================================
    # RICHTUNGSVERTEILUNG
    # ========================================================

    print()

    print(
        "RICHTUNGSVERTEILUNG"
    )

    print(
        "-" * 40
    )

    print(
        f"G = +1 : {positive}"
    )

    print(
        f"G = -1 : {negative}"
    )

    print(
        f"G =  0 : {neutral}"
    )


# ============================================================
# START
# ============================================================

def main():

    start = time.time()

    event_data = (
        run_simulation()
    )

    show_results(
        event_data
    )

    elapsed = (
        time.time()
        - start
    )

    print()
    print("=" * 68)
    print(
        " TEST C BEENDET"
    )
    print("=" * 68)

    print(
        f"Laufzeit: "
        f"{elapsed:.3f} Sekunden"
    )

    print()

    print(
        "Pydroid-Sicherheitscheck:"
    )

    print(
        "  pygame : NICHT verwendet"
    )

    print(
        "  SDL    : NICHT verwendet"
    )

    print(
        "  numpy  : NICHT verwendet"
    )

    print(
        "  grafik : NICHT verwendet"
    )

    print()

    print(
        "Test C — rauschfreies Signal"
    )

    print(
        "erfolgreich abgeschlossen."
    )

    print()


# ============================================================
# PROGRAMMSTART
# ============================================================

if __name__ == "__main__":

    main()