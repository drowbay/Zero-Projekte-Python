
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def add_box(ax, x, y, w, h, text, fontsize=10):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        linewidth=1.4,
        facecolor="white",
        edgecolor="black"
    )
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fontsize)
    return box

def add_arrow(ax, x1, y1, x2, y2, text=None, text_offset=(0, 0), fontsize=9):
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='->',
        mutation_scale=14,
        linewidth=1.3,
        color='black'
    )
    ax.add_patch(arrow)
    if text:
        mx = (x1 + x2) / 2 + text_offset[0]
        my = (y1 + y2) / 2 + text_offset[1]
        ax.text(mx, my, text, ha="center", va="center", fontsize=fontsize)
    return arrow

def build_comparison(save_path="vergleich_ms_sfv.png"):
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5, 0.965,
        "Vergleichsprogramm: MS Viewer v6 vs. Space Field Viewer (SFV)",
        ha="center", va="center", fontsize=17, fontweight="bold"
    )

    # Column titles
    ax.text(0.24, 0.91, "MS Viewer v6", ha="center", va="center", fontsize=14, fontweight="bold")
    ax.text(0.76, 0.91, "Space Field Viewer (SFV)", ha="center", va="center", fontsize=14, fontweight="bold")
    ax.text(0.50, 0.91, "Vergleich", ha="center", va="center", fontsize=14, fontweight="bold")

    # Left column: MS Viewer
    add_box(ax, 0.05, 0.78, 0.26, 0.09, "Multi-Feld-System\nη, ψ, E, MS, Ψ", 11)
    add_box(ax, 0.05, 0.63, 0.26, 0.10, "5 Prozesse\nExpansion / Phase /\nImplosion / Feedback / Emotion", 11)
    add_box(ax, 0.05, 0.46, 0.26, 0.11, "Split-Screen + Delta\n2 Modelle direkt vergleichbar", 11)
    add_box(ax, 0.05, 0.28, 0.26, 0.11, "Nebula + Energy + MS + Ψ-Spark\nLayer-Mischung / UI / Slider", 11)
    add_box(ax, 0.05, 0.11, 0.26, 0.10, "Starker Fokus auf\nEmergenz + Resonanz + Mapping", 11)

    # Right column: SFV
    add_box(ax, 0.69, 0.78, 0.26, 0.09, "Kompakter Feld-Viewer\nPotential, Gravitation, Rotation, EM", 11)
    add_box(ax, 0.69, 0.63, 0.26, 0.10, "7 Layer\nGrav / Rot / Energie /\nMS / EM / Hawking / Alles", 11)
    add_box(ax, 0.69, 0.46, 0.26, 0.11, "Single-View Darstellung\nLayer per Tastatur umschaltbar", 11)
    add_box(ax, 0.69, 0.28, 0.26, 0.11, "Horizont / Hawking / Partikel\nklarere astrophysische Lesart", 11)
    add_box(ax, 0.69, 0.11, 0.26, 0.10, "Starker Fokus auf\nFeldsichtbarkeit + physikalische Layer", 11)

    # Center compare boxes
    add_box(ax, 0.37, 0.78, 0.26, 0.09, "Gemeinsam:\nGitter + Kerne + Partikel + Feldvisualisierung", 11)
    add_box(ax, 0.37, 0.63, 0.26, 0.10, "MS Viewer erweitert SFV um:\nVergleich, Resonanz, UI, Delta, Prozesslogik", 11)
    add_box(ax, 0.37, 0.46, 0.26, 0.11, "SFV ist einfacher / klarer\nMS Viewer ist tiefer / modularer", 11)
    add_box(ax, 0.37, 0.28, 0.26, 0.11, "Konzeptuell:\nSFV = Feld-Atlas\nMS = Multi-Feld-Labor", 11)
    add_box(ax, 0.37, 0.11, 0.26, 0.10, "Saubere Lesart:\nBeide zeigen Dynamik, nicht Zeit als Objekt", 11)

    # Arrows left to center
    ys = [0.825, 0.68, 0.515, 0.335, 0.16]
    for y in ys:
        add_arrow(ax, 0.31, y, 0.37, y)

    # Arrows center to right
    for y in ys:
        add_arrow(ax, 0.63, y, 0.69, y)

    # Bottom formula strip
    add_box(ax, 0.12, 0.005, 0.76, 0.065,
            "Kurzform: Input-Felder → abgeleitete Felder → Zustand Z → Aktivität A → sichtbare Struktur / Layer",
            12)

    plt.tight_layout()
    plt.savefig(save_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    build_comparison("vergleich_ms_sfv.png")
    print("Gespeichert als: vergleich_ms_sfv.png")
