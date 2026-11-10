# visualization_737_pydroid_fixed.py
# 737 Visualization Toolkit — korrigierte Pydroid-3-freundliche Version
#
# Start in Pydroid 3:
#   1) Falls nötig installieren:
#      pip install numpy matplotlib
#   2) Datei starten.
#
# Ergebnis:
#   Es wird ein Ordner "viz_737_output" erstellt.
#   Darin liegen die PNG-Bilder.
#
# Hinweis:
#   Diese Version nutzt kein Fenster/Show(), sondern speichert nur PNGs.
#   Das ist für Pydroid 3 deutlich stabiler.

from pathlib import Path
import sys

try:
    import matplotlib
    matplotlib.use("Agg")  # kein Grafikfenster, nur Dateien speichern
    import matplotlib.pyplot as plt
    import numpy as np
except Exception as exc:
    print("FEHLER: Benötigte Pakete fehlen oder konnten nicht geladen werden.")
    print("Bitte in Pydroid 3 installieren:")
    print("  pip install numpy matplotlib")
    print()
    print("Originalfehler:", exc)
    input("ENTER drücken zum Schließen ... ")
    sys.exit(1)


DPI = 110
FIGSIZE = (12.8, 7.2)  # 16:9, leichter für Android als riesige 1920x1080-Figuren
OUT_DIR = Path("viz_737_output")


def ensure_output_dir():
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def savefig(fig, name):
    ensure_output_dir()
    path = OUT_DIR / name
    try:
        fig.tight_layout()
    except Exception:
        pass
    fig.savefig(path, bbox_inches="tight", dpi=DPI)
    plt.close(fig)
    print("Gespeichert:", path)


def viz_raum_resonanz(out="viz_1_raum_resonanz.png"):
    k = np.linspace(1, 10, 90)
    c = np.linspace(1, 10, 90)
    K, C = np.meshgrid(k, c)
    delta = 2 + 0.9 * K + 0.6 * np.log(C + 1) + 0.15 * K * np.power(C, 0.25)

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(K, C, delta, linewidth=0, antialiased=True)
    ax.set_xlabel("k")
    ax.set_ylabel("c")
    ax.set_zlabel("ð")
    ax.set_title("3D Landschaft: Raum-Resonanz (ð)")
    savefig(fig, out)


def viz_737_tls(out="viz_2_737_tls.png"):
    c_vals = np.array([2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0])
    lel = 300 + 40 * (c_vals ** 2) + 5 * (c_vals ** 3) / 3.0

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot(111)
    ax.plot(c_vals, lel, marker="o")
    ax.set_xlabel("c")
    ax.set_ylabel("lel_737_TLS")
    ax.set_title("737 lel - mit [TLS] (Toy Curve)")
    ax.grid(True)
    savefig(fig, out)


def viz_bloch(out="viz_3_bloch_sphere.png"):
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 60)
    X = np.outer(np.cos(u), np.sin(v))
    Y = np.outer(np.sin(u), np.sin(v))
    Z = np.outer(np.ones_like(u), np.cos(v))

    theta = np.pi / 2
    phi = 0.0
    px = np.sin(theta) * np.cos(phi)
    py = np.sin(theta) * np.sin(phi)
    pz = np.cos(theta)

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_wireframe(X, Y, Z, rstride=4, cstride=4, linewidth=0.4, alpha=0.6)

    ax.quiver(0, 0, 0, 1, 0, 0, length=1.0, normalize=True)
    ax.quiver(0, 0, 0, 0, 1, 0, length=1.0, normalize=True)
    ax.quiver(0, 0, 0, 0, 0, 1, length=1.0, normalize=True)

    ax.text(0, 0, 1.05, "|0>")
    ax.text(0, 0, -1.1, "|1>")
    ax.quiver(0, 0, 0, px, py, pz, length=1.0, normalize=True)
    ax.text(px * 1.05, py * 1.05, pz * 1.05, "Superposition")

    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])
    ax.set_zlim([-1.1, 1.1])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Bloch Sphere: (|0> + |1>)/sqrt(2)")
    savefig(fig, out)


def viz_classic_extension(out="viz_4_classic_extension.png"):
    i = np.linspace(1, 5, 25)
    j = np.linspace(1, 5, 25)
    I, J = np.meshgrid(i, j)
    Z = (
        3.5
        + 0.8 * np.sin(1.7 * I)
        + 0.9 * np.cos(1.3 * J)
        + 0.7 * np.sin(0.9 * I * J / 4)
    )

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_trisurf(I.flatten(), J.flatten(), Z.flatten(), linewidth=0.2, antialiased=True)
    ax.set_xlabel("Klassische Formeln (1-5)")
    ax.set_ylabel("Erweiterungen (1-5)")
    ax.set_zlabel("Spiegelung / Resonanz")
    ax.set_title("3D Landschaft: Klassische Physik ↔ Deine Erweiterung")
    savefig(fig, out)


def viz_737_mandala(out="viz_5_737_mandala.png"):
    theta = np.linspace(0, 2 * np.pi, 1500)
    r = (
        1
        + 0.35 * np.sin(7 * theta)
        + 0.18 * np.sin(3 * theta + 0.6)
        + 0.12 * np.sin(7 * theta * 0.5 + 1.2)
    )

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot(111, projection="polar")
    ax.plot(theta, r)
    ax.set_title("Projekt 737 lel - Mandala (Toy)")
    savefig(fig, out)


def viz_neon_surface(out="viz_6_neon_mandala_surface.png"):
    r = np.linspace(0.05, 1.0, 140)
    t = np.linspace(0, 2 * np.pi, 140)
    R, T = np.meshgrid(r, t)
    X = R * np.cos(T) * 10
    Y = R * np.sin(T) * 10
    Z = np.exp(-3 * R) * (1 + 1.4 * np.sin(6 * T) + 0.9 * np.sin(12 * T))

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, Z, linewidth=0, antialiased=True)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("3D Mandala Surface (Toy)")
    savefig(fig, out)


def viz_injection_spirals(out="viz_7_injection_spirals.png"):
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot(111, projection="3d")

    for phase in np.linspace(0, 2 * np.pi, 8, endpoint=False):
        t = np.linspace(0, 12 * np.pi, 600)
        r = 0.15 * t
        x = r * np.cos(t + phase)
        y = r * np.sin(t + phase)
        z = 0.03 * t
        ax.plot(x, y, z, linewidth=1.2)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("3D Injection Spirals (Toy)")
    savefig(fig, out)


def viz_project_integration(out="viz_8_project_integration.png"):
    labels = ["Visualisierungen", "noqa Wissen", "Test-Anleitung"]
    coords = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot(111, projection="3d")

    ax.plot([0, 1], [0, 0], [0, 0])
    ax.plot([0, 0], [0, 1], [0, 0])
    ax.plot([0, 0], [0, 0], [0, 1])

    ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], s=80)

    for (x, y, z), label in zip(coords, labels):
        ax.text(x * 1.05, y * 1.05, z * 1.05, label, fontsize=10)

    ax.plot([1, 0], [0, 1], [0, 0], linestyle="--")
    ax.plot([1, 0], [0, 0], [0, 1], linestyle="--")
    ax.plot([0, 0], [1, 0], [0, 1], linestyle="--")

    ax.set_xlabel("X: Visuals")
    ax.set_ylabel("Y: Linter/Noqa")
    ax.set_zlabel("Z: Anleitung")
    ax.set_title("Projekt-Integration: 3D Konzeptdiagramm")
    ax.set_xlim(0, 1.2)
    ax.set_ylim(0, 1.2)
    ax.set_zlim(0, 1.2)
    savefig(fig, out)


def noqa_examples():
    """Kleine sichere noqa-Beispiele ohne SyntaxError."""
    temp_value = 42  # noqa: F841
    import math  # noqa: E402
    import sys as _sys  # noqa: F401

    return f"noqa Beispiele okay: sqrt(9)={math.sqrt(9)}, python={_sys.version_info.major}"


def run_all():
    print("Starte 737 Visualisierung ...")
    ensure_output_dir()

    tasks = [
        viz_raum_resonanz,
        viz_737_tls,
        viz_bloch,
        viz_classic_extension,
        viz_737_mandala,
        viz_neon_surface,
        viz_injection_spirals,
        viz_project_integration,
    ]

    for index, task in enumerate(tasks, start=1):
        print(f"[{index}/{len(tasks)}] {task.__name__}")
        task()

    print()
    print("Fertig. Bilder liegen im Ordner:", OUT_DIR.resolve())
    print(noqa_examples())


if __name__ == "__main__":
    try:
        run_all()
    except Exception as exc:
        print()
        print("FEHLER beim Ausführen:")
        print(exc)
    finally:
        # In Pydroid offen halten, damit man die Meldungen lesen kann.
        try:
            input("ENTER drücken zum Schließen ... ")
        except EOFError:
            pass
