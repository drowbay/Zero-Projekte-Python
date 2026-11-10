
# visualization_737.py — 737 Visualization Toolkit
# Run: python visualization_737.py
# Creates PNGs (16:9) for multiple visualizations.
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

dpi = 120
figsize = (1920/dpi, 1080/dpi)

def savefig(fig, name):
    fig.tight_layout()
    fig.savefig(name, bbox_inches='tight', dpi=dpi)
    plt.close(fig)

def viz_raum_resonanz(out="viz_1_raum_resonanz.png"):
    k = np.linspace(1, 10, 120)
    c = np.linspace(1, 10, 120)
    K, C = np.meshgrid(k, c)
    delta = 2 + 0.9*K + 0.6*np.log(C+1) + 0.15*K*np.power(C, 0.25)
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(K, C, delta, linewidth=0, antialiased=True, rstride=1, cstride=1)
    ax.set_xlabel("k"); ax.set_ylabel("c"); ax.set_zlabel("ð")
    ax.set_title("3D Landschaft: Raum‑Resonanz (ð)")
    savefig(fig, out)

def viz_737_tls(out="viz_2_737_tls.png"):
    c_vals = np.array([2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0])
    lel = 300 + 40*(c_vals**2) + 5*(c_vals**3)/3.0
    fig = plt.figure(figsize=figsize, dpi=dpi); ax = fig.add_subplot(111)
    ax.plot(c_vals, lel, marker='o')
    ax.set_xlabel("c"); ax.set_ylabel("lel_737_TLS")
    ax.set_title("737 lel – mit [TLS] (Toy Curve)")
    ax.grid(True, which="both", axis="both", linestyle='-')
    savefig(fig, out)

def viz_bloch(out="viz_3_bloch_sphere.png"):
    u = np.linspace(0, 2*np.pi, 80); v = np.linspace(0, np.pi, 80)
    X = np.outer(np.cos(u), np.sin(v))
    Y = np.outer(np.sin(u), np.sin(v))
    Z = np.outer(np.ones_like(u), np.cos(v))
    theta = np.pi/2; phi = 0.0
    px = np.sin(theta)*np.cos(phi); py = np.sin(theta)*np.sin(phi); pz = np.cos(theta)
    fig = plt.figure(figsize=figsize, dpi=dpi); ax = fig.add_subplot(111, projection='3d')
    ax.plot_wireframe(X, Y, Z, rstride=4, cstride=4, linewidth=0.4, alpha=0.6)
    ax.quiver(0,0,0, 1,0,0, length=1.0, normalize=True)
    ax.quiver(0,0,0, 0,1,0, length=1.0, normalize=True)
    ax.quiver(0,0,0, 0,0,1, length=1.0, normalize=True)
    ax.text(0,0,1.05,"|0>"); ax.text(0,0,-1.1,"|1>")
    ax.quiver(0,0,0, px,py,pz, length=1.0, normalize=True)
    ax.text(px*1.05, py*1.05, pz*1.05, "Superposition")
    ax.set_xlim([-1.1,1.1]); ax.set_ylim([-1.1,1.1]); ax.set_zlim([-1.1,1.1])
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.set_title("Bloch Sphere: (|0> + |1>)/√2")
    savefig(fig, out)

def viz_classic_extension(out="viz_4_classic_extension.png"):
    i = np.linspace(1,5,25); j = np.linspace(1,5,25)
    I, J = np.meshgrid(i, j)
    Z = 3.5 + 0.8*np.sin(1.7*I) + 0.9*np.cos(1.3*J) + 0.7*np.sin(0.9*I*J/4)
    fig = plt.figure(figsize=figsize, dpi=dpi); ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(I.flatten(), J.flatten(), Z.flatten(), linewidth=0.2, antialiased=True)
    ax.set_xlabel("Klassische Formeln (1–5)"); ax.set_ylabel("Erweiterungen (1–5)"); ax.set_zlabel("Spiegelung / Resonanz")
    ax.set_title("3D Landschaft: Klassische Physik ↔ Deine Erweiterung")
    savefig(fig, out)

def viz_737_mandala(out="viz_5_737_mandala.png"):
    theta = np.linspace(0, 2*np.pi, 2000)
    r = 1 + 0.35*np.sin(7*theta) + 0.18*np.sin(3*theta + 0.6) + 0.12*np.sin(7*theta*0.5 + 1.2)
    fig = plt.figure(figsize=figsize, dpi=dpi); ax = fig.add_subplot(111, projection='polar')
    ax.plot(theta, r)
    ax.set_title("Projekt 737 lel – Mandala (Toy)")
    savefig(fig, out)

def viz_neon_surface(out="viz_6_neon_mandala_surface.png"):
    r = np.linspace(0.05,1.0,200); t = np.linspace(0,2*np.pi,200)
    R, T = np.meshgrid(r, t)
    X = R*np.cos(T)*10; Y = R*np.sin(T)*10
    Z = np.exp(-3*R) * (1 + 1.4*np.sin(6*T) + 0.9*np.sin(12*T))
    fig = plt.figure(figsize=figsize, dpi=dpi); ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, linewidth=0, antialiased=True)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z"); ax.set_title("3D Mandala Surface (Toy)")
    savefig(fig, out)

def viz_injection_spirals(out="viz_7_injection_spirals.png"):
    fig = plt.figure(figsize=figsize, dpi=dpi); ax = fig.add_subplot(111, projection='3d')
    for phase in np.linspace(0, 2*np.pi, 8, endpoint=False):
        t = np.linspace(0, 12*np.pi, 800); r = 0.15*t
        x = r*np.cos(t + phase); y = r*np.sin(t + phase); z = 0.03*t
        ax.plot(x, y, z, linewidth=1.2)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z"); ax.set_title("3D Injection Spirals (Toy)")
    savefig(fig, out)

def run_all():
    viz_raum_resonanz()
    viz_737_tls()
    viz_bloch()
    viz_classic_extension()
    viz_737_mandala()
    viz_neon_surface()
    viz_injection_spirals()

if __name__ == "__main__":
    run_all()


# ------------------------------------------------------------------------------
# noqa Cheat-Sheet (für Lumi 🤓⚡)
#
# 🔹 Häufige Codes:
# - F401 → module imported but unused
# - F403 → 'from module import *' used; unable to detect undefined names
# - F405 → name may be undefined, or defined from star imports
# - F841 → local variable is assigned to but never used
#
# 🔹 Style-Warnungen (E-Serie):
# - E402 → import not at top of file
# - E501 → line too long (> 79 chars)
#
# 🔹 Weitere:
# - W291 → trailing whitespace
# - W503 → line break before binary operator
#
# 👉 Nutzung:
# - '# noqa'  → alle Fehler/Warnungen in dieser Zeile ignorieren
# - '# noqa: F401' → nur F401 ignorieren
# - '# noqa: F401, E501' → mehrere Codes ignorieren
#
# Merksatz: noqa = "No Quality Assurance" → Schutzschild gegen Linter-Nörgler 😎
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Mini-Beispiele für noqa (direkt testbar)
# ------------------------------------------------------------------------------

def noqa_examples():
    # F841 → Variable wird nie benutzt
    temp_value = 42  # noqa: F841

    # E402 → Import nicht ganz oben im File
    import math  # noqa: E402

    # F401 → Modul importiert, aber nicht genutzt
    import sys  # noqa: F401

    # F403/F405 → Wildcard-Import (nicht empfohlen, aber manchmal nötig)
    from math import *  # noqa: F403,F405

    return "noqa Beispiele laufen durch ohne Linter-Fehler 😎"

