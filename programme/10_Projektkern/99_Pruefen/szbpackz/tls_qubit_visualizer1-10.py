# tls_qubit_visualizer1.py — Kombinierter Visualizer mit Batch-Modus
# Visualisiert TLS-Vektor + Qubit-State aus HSV
# 
# Nutzung:
#   python tls_qubit_visualizer1.py --h 0.7 --s 0.9 --v 0.5
#   python tls_qubit_visualizer1.py --h 0.7 --s 0.9 --v 0.5 --use-mapping
#   python tls_qubit_visualizer1.py --batch "0.1,0.8,0.5; 0.5,0.6,0.7; 0.9,0.4,0.3"
#
# Batch-Mode akzeptiert eine Zeichenkette mit HSV-Tuples getrennt durch ';'.
# Beispiel: "0.2,0.5,0.7; 0.6,0.8,0.4"

import math, cmath, argparse
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

try:
    import color_ui_mapping
    HAS_MAPPING = True
except ImportError:
    HAS_MAPPING = False

C = 299_792_458.0
C2 = C*C

@dataclass
class TLSVector:
    x: float
    y: float
    z: float
    scale: float

@dataclass
class QubitState:
    theta: float
    phi: float
    alpha: complex
    beta: complex
    visibility: float

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def hsv_to_tls(h: float, s: float, v: float, c2_scale: bool = True) -> TLSVector:
    h = h % 1.0
    s = clamp01(s)
    v = clamp01(v)
    phi = 2.0 * math.pi * h
    x = s * math.cos(phi)
    y = s * math.sin(phi)
    z = v
    k = C2 if c2_scale else 1.0
    return TLSVector(x*k, y*k, z*k, k)

def hsv_to_qubit(h: float, s: float, v: float) -> QubitState:
    h = h % 1.0
    s = clamp01(s)
    v = clamp01(v)
    phi = 2.0 * math.pi * h
    theta = math.pi * (1.0 - v)
    alpha = math.cos(theta/2.0) + 0j
    beta = cmath.exp(1j*phi) * math.sin(theta/2.0)
    return QubitState(theta, phi, alpha, beta, s)

def visualize(tls: TLSVector, qb: QubitState, title_suffix=""):
    fig = plt.figure(figsize=(12,6))

    # TLS Vektor
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.quiver(0,0,0, tls.x, tls.y, tls.z, color="blue", arrow_length_ratio=0.1)
    ax1.set_xlim(-1,1)
    ax1.set_ylim(-1,1)
    ax1.set_zlim(0,1)
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.set_zlabel("Z")
    ax1.set_title(f"TLS-Vektor {title_suffix}")

    # Bloch-Sphäre
    ax2 = fig.add_subplot(122, projection='3d')
    u = np.linspace(0, 2*np.pi, 50)
    v_ = np.linspace(0, np.pi, 25)
    xs = np.outer(np.cos(u), np.sin(v_))
    ys = np.outer(np.sin(u), np.sin(v_))
    zs = np.outer(np.ones(np.size(u)), np.cos(v_))
    ax2.plot_surface(xs, ys, zs, color='lightgrey', alpha=0.2, linewidth=0)

    qx = math.sin(qb.theta)*math.cos(qb.phi)
    qy = math.sin(qb.theta)*math.sin(qb.phi)
    qz = math.cos(qb.theta)
    ax2.quiver(0,0,0, qx, qy, qz, color="red", arrow_length_ratio=0.1)

    ax2.set_xlim(-1,1)
    ax2.set_ylim(-1,1)
    ax2.set_zlim(-1,1)
    ax2.set_xlabel("X")
    ax2.set_ylabel("Y")
    ax2.set_zlabel("Z")
    ax2.set_title(f"Bloch-Sphäre {title_suffix}")

    plt.tight_layout()
    plt.show()

def get_states(h, s, v, use_mapping):
    if use_mapping and HAS_MAPPING:
        payload = color_ui_mapping.pack_payload(h, s, v, c2_scale=False)
        tls_data = payload["tls"]
        tls = TLSVector(**tls_data)
        qb_data = payload["qubit"]
        qb = QubitState(
            theta=qb_data["theta"],
            phi=qb_data["phi"],
            alpha=complex(*qb_data["alpha"]),
            beta=complex(*qb_data["beta"]),
            visibility=qb_data["visibility"]
        )
    else:
        tls = hsv_to_tls(h, s, v, c2_scale=False)
        qb = hsv_to_qubit(h, s, v)
    return tls, qb

def main():
    p = argparse.ArgumentParser(description="TLS + Qubit Visualizer aus HSV")
    p.add_argument("--h", type=float, help="Hue 0..1")
    p.add_argument("--s", type=float, help="Saturation 0..1")
    p.add_argument("--v", type=float, help="Value 0..1")
    p.add_argument("--use-mapping", action="store_true", help="nutzt color_ui_mapping wenn verfügbar")
    p.add_argument("--batch", type=str, help="Batch-Eingabe: 'h,s,v; h,s,v; ...'")
    args = p.parse_args()

    if args.batch:
        triplets = [tuple(map(float, t.split(','))) for t in args.batch.split(';') if t.strip()]
        for i,(h,s,v) in enumerate(triplets, start=1):
            tls, qb = get_states(h, s, v, args.use_mapping)
            visualize(tls, qb, title_suffix=f"(Batch {i}: h={h},s={s},v={v})")
    else:
        if args.h is None or args.s is None or args.v is None:
            print("Bitte entweder --h --s --v angeben oder --batch nutzen.")
            return
        tls, qb = get_states(args.h, args.s, args.v, args.use_mapping)
        visualize(tls, qb, title_suffix=f"(h={args.h},s={args.s},v={args.v})")

if __name__ == "__main__":
    main()
