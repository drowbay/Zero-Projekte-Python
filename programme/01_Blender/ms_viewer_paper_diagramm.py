
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def add_box(ax, x, y, w, h, text, fontsize=11):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.6,
        facecolor="white",
        edgecolor="black"
    )
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fontsize)
    return box

def add_arrow(ax, x1, y1, x2, y2, text=None, text_offset=(0, 0), fontsize=10):
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='->',
        mutation_scale=14,
        linewidth=1.4,
        color='black'
    )
    ax.add_patch(arrow)
    if text:
        mx = (x1 + x2) / 2 + text_offset[0]
        my = (y1 + y2) / 2 + text_offset[1]
        ax.text(mx, my, text, ha="center", va="center", fontsize=fontsize)
    return arrow

def build_diagram(save_path):
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5, 0.96,
        "Paper-Diagramm: MS-Viewer als Multi-Feld-System mit Emergenz",
        ha="center", va="center", fontsize=16, fontweight="bold"
    )

    add_box(ax, 0.06, 0.78, 0.18, 0.10, "Φ(x,y)\nPotential / Struktur", 12)
    add_box(ax, 0.29, 0.78, 0.18, 0.10, "E(x,y)\nEnergie", 12)
    add_box(ax, 0.52, 0.78, 0.18, 0.10, "Noise / Kontakt\nStörung / Resonanz", 12)
    add_box(ax, 0.75, 0.78, 0.18, 0.10, "Richtungen\nExpansion / Phase /\nImplosion / Feedback", 11)

    add_box(ax, 0.06, 0.56, 0.18, 0.10, "η(x,y)\n= norm(|Φ|)", 12)
    add_box(ax, 0.29, 0.56, 0.18, 0.10, "ψ(x,y)\n= norm(|∇E|)", 12)
    add_box(ax, 0.52, 0.56, 0.18, 0.10, "Ψ(x,y)\n= Resonanzfeld", 12)
    add_box(ax, 0.75, 0.56, 0.18, 0.10, "Vektorfelder\nF_exp, F_phase,\nF_imp, F_fb", 11)

    add_box(ax, 0.21, 0.34, 0.24, 0.12, "Z(x,y)\n= f(η, ψ, E, Ψ)", 13)
    add_box(ax, 0.55, 0.34, 0.24, 0.12, "MS(x,y)\n= Misch- / Vergleichslayer", 13)

    add_box(ax, 0.21, 0.13, 0.24, 0.12, "A(x,y)\n~ |∇Z|  oder  |∂Z/∂t|²", 13)
    add_box(ax, 0.55, 0.13, 0.24, 0.12, "sichtbares Band / Diagramm\nBreite d ~ A", 13)

    add_box(ax, 0.80, 0.13, 0.15, 0.12, "Interpretation\nZeit nicht als Ding,\nsondern als\nsichtbare Dynamik", 11)

    add_arrow(ax, 0.15, 0.78, 0.15, 0.66)
    add_arrow(ax, 0.38, 0.78, 0.38, 0.66)
    add_arrow(ax, 0.61, 0.78, 0.61, 0.66)
    add_arrow(ax, 0.84, 0.78, 0.84, 0.66)

    add_arrow(ax, 0.15, 0.56, 0.31, 0.46)
    add_arrow(ax, 0.38, 0.56, 0.33, 0.46)
    add_arrow(ax, 0.61, 0.56, 0.40, 0.46)
    add_arrow(ax, 0.84, 0.56, 0.67, 0.46)

    add_arrow(ax, 0.45, 0.40, 0.55, 0.40, "Vergleich / Mapping", text_offset=(0, 0.03), fontsize=10)

    add_arrow(ax, 0.33, 0.34, 0.33, 0.25)
    add_arrow(ax, 0.67, 0.34, 0.67, 0.25)

    add_arrow(ax, 0.79, 0.19, 0.80, 0.19)

    ax.text(0.06, 0.05, "Kernidee:", fontsize=12, fontweight="bold")
    ax.text(
        0.15, 0.05,
        "Input-Felder → abgeleitete Felder → Systemzustand Z → Aktivität A → sichtbare Struktur",
        fontsize=12
    )
    ax.text(
        0.06, 0.01,
        "Physikalisch sauber gelesen: Das Bild zeigt Aktivität / Änderungsdichte, nicht „Zeit als Objekt“.",
        fontsize=11
    )

    plt.tight_layout()
    plt.savefig(save_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    build_diagram("ms_viewer_paper_diagramm.png")
    print("Gespeichert als: ms_viewer_paper_diagramm.png")
