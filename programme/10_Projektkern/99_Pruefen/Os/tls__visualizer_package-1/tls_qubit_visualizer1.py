# tls_qubit_visualizer1.py — Visualizer mit Batch-, Save- (PNG, MP4, GIF) und flexiblem Output
#
# Nutzung:
#   python tls_qubit_visualizer1.py --h 0.7 --s 0.9 --v 0.5 --save-png --outdir ./results --basename test
#
# Ausgabe-Dateien:
#   ./results/test_single.png
#   ./results/test_batch_1.png
#   ./results/test_batch_animation.mp4
#   ./results/test_batch_animation.gif

import math, cmath, argparse, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
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

def plot_state(tls: TLSVector, qb: QubitState, title_suffix="", save_path=None):
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
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"Gespeichert: {save_path}")
        plt.close(fig)
    else:
        plt.show()

def save_animation(states, outpath="batch_animation.mp4", gif=False):
    fig = plt.figure(figsize=(12,6))
    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')

    def init_axes():
        for ax in [ax1, ax2]:
            ax.clear()
            ax.set_xlim(-1,1)
            ax.set_ylim(-1,1)
            ax.set_zlim(-1,1)
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
        ax1.set_title("TLS-Vektor (Batch)")
        ax2.set_title("Bloch-Sphäre (Batch)")

    def update(i):
        tls, qb = states[i]
        init_axes()
        ax1.quiver(0,0,0, tls.x, tls.y, tls.z, color="blue", arrow_length_ratio=0.1)
        # Bloch sphere surface
        u = np.linspace(0, 2*np.pi, 30)
        v_ = np.linspace(0, np.pi, 15)
        xs = np.outer(np.cos(u), np.sin(v_))
        ys = np.outer(np.sin(u), np.sin(v_))
        zs = np.outer(np.ones(np.size(u)), np.cos(v_))
        ax2.plot_surface(xs, ys, zs, color='lightgrey', alpha=0.2, linewidth=0)
        qx = math.sin(qb.theta)*math.cos(qb.phi)
        qy = math.sin(qb.theta)*math.sin(qb.phi)
        qz = math.cos(qb.theta)
        ax2.quiver(0,0,0, qx, qy, qz, color="red", arrow_length_ratio=0.1)

    ani = animation.FuncAnimation(fig, update, frames=len(states), interval=1000, repeat=False)
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    if gif:
        ani.save(outpath, writer="imagemagick")
    else:
        ani.save(outpath, writer="ffmpeg")
    print(f"Animation gespeichert: {outpath}")

def main():
    p = argparse.ArgumentParser(description="TLS + Qubit Visualizer aus HSV mit Batch/Save/Output")
    p.add_argument("--h", type=float, help="Hue 0..1")
    p.add_argument("--s", type=float, help="Saturation 0..1")
    p.add_argument("--v", type=float, help="Value 0..1")
    p.add_argument("--use-mapping", action="store_true", help="nutzt color_ui_mapping wenn verfügbar")
    p.add_argument("--batch", type=str, help="Batch-Eingabe: 'h,s,v; h,s,v; ...'")
    p.add_argument("--save-png", action="store_true", help="Speichert jede Ausgabe als PNG statt Anzeige")
    p.add_argument("--save-mp4", action="store_true", help="Speichert Batch als MP4-Animation")
    p.add_argument("--save-gif", action="store_true", help="Speichert Batch als GIF-Animation")
    p.add_argument("--outdir", type=str, default="./output", help="Output-Ordner")
    p.add_argument("--basename", type=str, default="viz", help="Basisname der Dateien")
    args = p.parse_args()

    if args.batch:
        triplets = [tuple(map(float, t.split(','))) for t in args.batch.split(';') if t.strip()]
        states = [get_states(h,s,v,args.use_mapping) for (h,s,v) in triplets]
        if args.save_mp4 or args.save_gif:
            ext = "gif" if args.save_gif else "mp4"
            outpath = os.path.join(args.outdir, f"{args.basename}_batch_animation.{ext}")
            save_animation(states, outpath=outpath, gif=args.save_gif)
        else:
            for i,(hsv,state) in enumerate(zip(triplets, states), start=1):
                tls,qb = state
                h,s,v = hsv
                save_path = os.path.join(args.outdir, f"{args.basename}_batch_{i}.png") if args.save_png else None
                plot_state(tls,qb,title_suffix=f"(Batch {i}: h={h},s={s},v={v})",save_path=save_path)
    else:
        if args.h is None or args.s is None or args.v is None:
            print("Bitte entweder --h --s --v angeben oder --batch nutzen.")
            return
        tls, qb = get_states(args.h, args.s, args.v, args.use_mapping)
        save_path = os.path.join(args.outdir, f"{args.basename}_single.png") if args.save_png else None
        plot_state(tls,qb,title_suffix=f"(h={args.h},s={args.s},v={args.v})",save_path=save_path)

if __name__ == "__main__":
    main()
