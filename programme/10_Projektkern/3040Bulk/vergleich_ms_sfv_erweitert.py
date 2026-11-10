
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def add_box(ax, x, y, w, h, text, fontsize=9.5):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        linewidth=1.3,
        facecolor="white",
        edgecolor="black"
    )
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fontsize)
    return box

def add_arrow(ax, x1, y1, x2, y2, text=None, text_offset=(0, 0), fontsize=8.5):
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='->',
        mutation_scale=13,
        linewidth=1.2,
        color='black'
    )
    ax.add_patch(arrow)
    if text:
        mx = (x1 + x2) / 2 + text_offset[0]
        my = (y1 + y2) / 2 + text_offset[1]
        ax.text(mx, my, text, ha="center", va="center", fontsize=fontsize)
    return arrow

def build_extended_comparison(save_path="vergleich_ms_sfv_erweitert.png"):
    fig, ax = plt.subplots(figsize=(18, 11))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5, 0.97,
        "Vergleichsprogramm erweitert: MS Viewer v6 vs. Space Field Viewer (SFV)",
        ha="center", va="center", fontsize=18, fontweight="bold"
    )

    # Column headers
    ax.text(0.20, 0.93, "MS Viewer v6", ha="center", va="center", fontsize=14, fontweight="bold")
    ax.text(0.50, 0.93, "Vergleichsebene", ha="center", va="center", fontsize=14, fontweight="bold")
    ax.text(0.80, 0.93, "Space Field Viewer (SFV)", ha="center", va="center", fontsize=14, fontweight="bold")

    y_positions = [0.84, 0.72, 0.60, 0.48, 0.36, 0.24, 0.12]

    left_texts = [
        "Mehrschichtiges Multi-Feld-System\nη, ψ, E, MS, Ψ",
        "5 Prozessarten\nExpansion / Phase / Implosion /\nFeedback / Emotion",
        "Split-Screen + Delta + Coherence\nzwei Modelle direkt vergleichbar",
        "UI-Features:\nSlider, Pause, Reset, Checks,\nTooltip, Screenshot, Speed",
        "Nebula-Layer + Ψ-Spark + Puls\nstarker Resonanz-/Emergenzfokus",
        "Konzept: Labor / Vergleich / Mapping\nmodular und experimentell",
        "Zielbild:\nDynamik, Resonanz, Differenz,\ninterpretierbare Feldbeziehungen"
    ]

    mid_texts = [
        "Gemeinsam:\nGitter, Kerne, Potential, Energie,\nPartikel und Feldvisualisierung",
        "Strukturfrage:\nMS ist prozesszentriert,\nSFV ist layerzentriert",
        "Vergleich:\nMS erweitert Beobachtung um\nDifferenz- und Sync-Logik",
        "Bedienung:\nMS ist interaktiver und dichter,\nSFV ist direkter und schlanker",
        "Physiknähe:\nSFV klarer astrophysisch,\nMS stärker modell- und resonanzbetont",
        "Lesart:\nSFV = Feld-Atlas\nMS = Multi-Feld-Labor",
        "Sauber gesagt:\nBeide zeigen sichtbare Dynamik,\nnicht „Zeit als Objekt“"
    ]

    right_texts = [
        "Kompakter Feld-Viewer\nPotential, Gravitation,\nRotation, EM, Hawking",
        "7 Layer\nGrav / Rot / Energie /\nMS / EM / Hawking / Alles",
        "Single-View Layerumschaltung\nper Tastatur direkt sichtbar",
        "Weniger UI, weniger Meta-Ebene\nfokussierter Überblick",
        "Horizont / Hawking / EM-Layer\nstärkere astrophysische Lesart",
        "Konzept: Atlas / Übersicht /\nklare Feldsichtbarkeit",
        "Zielbild:\nphysikalische Layer getrennt sehen\nund kombinieren"
    ]

    for y, lt, mt, rt in zip(y_positions, left_texts, mid_texts, right_texts):
        add_box(ax, 0.05, y-0.045, 0.24, 0.09, lt, 10)
        add_box(ax, 0.38, y-0.045, 0.24, 0.09, mt, 10)
        add_box(ax, 0.71, y-0.045, 0.24, 0.09, rt, 10)
        add_arrow(ax, 0.29, y, 0.38, y)
        add_arrow(ax, 0.62, y, 0.71, y)

    # Feature matrix
    ax.text(0.5, 0.045, "Feature-Matrix", ha="center", va="center", fontsize=13, fontweight="bold")

    matrix_y = 0.005
    features = [
        ("Split-Screen", "ja", "nein"),
        ("Delta / Vergleich", "ja", "nein"),
        ("Coherence-Score", "ja", "nein"),
        ("Tooltip / Klickwerte", "ja", "nein"),
        ("Nebula-Modi", "ja", "nein"),
        ("Hawking/Horizont", "indirekt / nein", "ja"),
        ("Emotion / Ψ-Layer", "ja", "nein"),
        ("Astrophysik-Fokus", "mittel", "hoch"),
        ("Experimenteller Fokus", "hoch", "mittel"),
    ]

    x0 = 0.08
    colw = [0.30, 0.12, 0.12]
    row_h = 0.027

    add_box(ax, x0, matrix_y + row_h*len(features), colw[0], row_h, "Feature", 10)
    add_box(ax, x0 + colw[0] + 0.02, matrix_y + row_h*len(features), colw[1], row_h, "MS", 10)
    add_box(ax, x0 + colw[0] + colw[1] + 0.04, matrix_y + row_h*len(features), colw[2], row_h, "SFV", 10)

    for i, (f, ms, sfv) in enumerate(features[::-1]):
        yy = matrix_y + i*row_h
        add_box(ax, x0, yy, colw[0], row_h, f, 9)
        add_box(ax, x0 + colw[0] + 0.02, yy, colw[1], row_h, ms, 9)
        add_box(ax, x0 + colw[0] + colw[1] + 0.04, yy, colw[2], row_h, sfv, 9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    build_extended_comparison("vergleich_ms_sfv_erweitert.png")
    print("Gespeichert als: vergleich_ms_sfv_erweitert.png")
