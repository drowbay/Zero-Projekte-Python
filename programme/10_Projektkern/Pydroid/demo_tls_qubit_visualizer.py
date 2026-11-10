# demo_tls_qubit_visualizer.py — Demo-Script für Lumi
# Visualisiert TLS-Vektor + Qubit-State aus HSV
#
# Nutzung: python demo_tls_qubit_visualizer.py

import math, cmath
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

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

def main():
    h, s, v = 0.7, 0.9, 0.5
    tls = hsv_to_tls(h, s, v, c2_scale=False)
    qb = hsv_to_qubit(h, s, v)

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
    ax1.set_title("TLS-Vektor (aus HSV)")

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
    ax2.set_title("Bloch-Sphäre (Qubit)")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
