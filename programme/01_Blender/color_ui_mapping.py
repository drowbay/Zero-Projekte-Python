
# color_ui_mapping.py — Mappt Farbauswahl (HSV) auf TLS-Space + Qubit
# Autor: ChatGPT (für Lumi)
#
# Funktionen:
# - hsv_to_tls(h, s, v, c2_scale=True): Mappt HSV auf TLS-Vektor (x,y,z) inkl. optionalem c^2-Scaling.
# - hsv_to_qubit(h, s, v): Mappt HSV auf Bloch-Parameter (theta, phi) und State-Vector |ψ>.
# - pack_payload(h, s, v): Kombiniert TLS + Qubit in ein Dictionary.
# - UI_CATALOG: Metadaten zu gängigen Programmen/Picker-UIs.
#
# Mathematische Übertragung (Design-Entscheidung, leicht anpassbar):
# - Hue h in [0,1) -> Winkel φ = 2πh (Phase auf der XY-Ebene / Azimut im TLS).
# - Saturation s in [0,1] -> Radius in XY (wie „Reinheit“ der Farbe / Quanten-Kohärenz).
# - Value v in [0,1] -> Z-Anteil (Helligkeit, interpretiert als „Energiehöhe“).
#
# TLS-Vektor:
#   x = s * cos(2πh)
#   y = s * sin(2πh)
#   z = v
# Optional: Skaliere jeden Anteil mit c^2 (n = c^2, m = c^2, l = c^2), um das Projekt-Paradigma zu reflektieren.
#
# Qubit (Bloch-Sphäre):
#   φ = 2πh
#   θ = π * (1 - v)     # Hell = kleiner θ (näher |0>), Dunkel = größer θ (näher |1>)
#   |ψ> = cos(θ/2)|0> + e^{iφ} sin(θ/2)|1>
#   Reinheit/Skalierung über s (0 = voll gemischt / 1 = rein) – hier als „visibility“ ausgegeben.
#
# Nutzung:
#   python color_ui_mapping.py --h 0.8 --s 0.7 --v 0.5 --no-c2
#
import math
import cmath
import argparse
from dataclasses import dataclass, asdict

C = 299_792_458.0  # Lichtgeschwindigkeit [m/s]
C2 = C * C

@dataclass
class TLSVector:
    x: float
    y: float
    z: float
    scale: float  # verwendete Skala (1 oder c^2)

@dataclass
class QubitState:
    theta: float     # [rad]
    phi: float       # [rad]
    alpha: complex   # Amplitude vor |0>
    beta: complex    # Amplitude vor |1>
    visibility: float  # aus s, 0..1

UI_CATALOG = [
    {"program": "Krita", "picker": "Hue-Rad + SV-Quadrat (HSV)", "shortcut": "Shift+I (Popup)"},
    {"program": "Paint Tool SAI", "picker": "Hue-Rad + Block (HSV)", "shortcut": "Standard rechts, kein Shortcut nötig"},
    {"program": "Clip Studio Paint", "picker": "Farbkreis + Paletten", "shortcut": "Fenster > Farbkreis"},
    {"program": "Photoshop (HUD/Plugin)", "picker": "HUD-Farbwähler / Plugin-Rad", "shortcut": "Alt+Shift+Rechtsklick (HUD)"},
    {"program": "Blender", "picker": "Rad/Quadrant/Linear", "shortcut": "Klick aufs Farbfeld (je Editor)"},
]

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def hsv_to_tls(h: float, s: float, v: float, c2_scale: bool = True) -> TLSVector:
    """Mappt HSV (0..1) auf TLS-Vektor (x,y,z). Optional mit c^2-Skalierung."""
    h = h % 1.0
    s = clamp01(s)
    v = clamp01(v)
    phi = 2.0 * math.pi * h
    x = s * math.cos(phi)
    y = s * math.sin(phi)
    z = v
    k = C2 if c2_scale else 1.0
    return TLSVector(x * k, y * k, z * k, k)

def hsv_to_qubit(h: float, s: float, v: float) -> QubitState:
    """Mappt HSV auf Bloch-Parameter und |ψ> (reinheits-agnostisch, s als visibility)."""
    h = h % 1.0
    s = clamp01(s)
    v = clamp01(v)
    phi = 2.0 * math.pi * h
    theta = math.pi * (1.0 - v)
    alpha = math.cos(theta / 2.0) + 0j
    beta = cmath.exp(1j * phi) * math.sin(theta / 2.0)
    return QubitState(theta, phi, alpha, beta, s)

def pack_payload(h: float, s: float, v: float, c2_scale: bool = True) -> dict:
    tls = hsv_to_tls(h, s, v, c2_scale=c2_scale)
    qb = hsv_to_qubit(h, s, v)
    return {
        "input": {"h": h, "s": s, "v": v},
        "tls": asdict(tls),
        "qubit": {
            "theta": qb.theta,
            "phi": qb.phi,
            "alpha": [qb.alpha.real, qb.alpha.imag],
            "beta": [qb.beta.real, qb.beta.imag],
            "visibility": qb.visibility,
        },
        "ui_catalog": UI_CATALOG,
        "notes": {
            "mapping": "Hue->Phase φ, Saturation->XY-Radius, Value->Z; θ=π(1−v)",
            "project_constants": "n=m=l=c^2 optional aktiv (scale = c^2)",
        },
    }

def main():
    p = argparse.ArgumentParser(description="Mappt HSV auf TLS-Space + Qubit-State")
    p.add_argument("--h", type=float, required=True, help="Hue 0..1")
    p.add_argument("--s", type=float, required=True, help="Saturation 0..1")
    p.add_argument("--v", type=float, required=True, help="Value 0..1")
    p.add_argument("--no-c2", action="store_true", help="c^2-Skalierung deaktivieren")
    args = p.parse_args()
    payload = pack_payload(args.h, args.s, args.v, c2_scale=not args.no_c2)
    import json
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
