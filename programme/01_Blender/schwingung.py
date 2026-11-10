import numpy as np
import matplotlib.pyplot as plt

# ===============================
# NASA / ESA INSPIRED SETTINGS
# ===============================

GRID_SIZE = 60
SPACE_SIZE = 10.0

SMOOTH_TO_GRAIN = 0.6   # 0 = smooth | 1 = körnig
THRESHOLD = 0.2
LEVELS = 6
EDGE_MIX = 0.3

# Kosmische Zusammensetzung (NASA / ESA inspiriert)
BARYON_MIX = 0.05       # normale Materie ~5%
DARK_MATTER_MIX = 0.27  # dunkle Materie ~27%
DARK_ENERGY_MIX = 0.68  # dunkle Energie ~68%

# Optionaler Welch/Earendel-Vibe
EARRENDEL_REDSHIFT = 6.2

TIME = 2.0              # statischer Zeitpunkt

# ===============================
# GRID
# ===============================

x = np.linspace(-SPACE_SIZE, SPACE_SIZE, GRID_SIZE)
y = np.linspace(-SPACE_SIZE, SPACE_SIZE, GRID_SIZE)
z = np.linspace(-SPACE_SIZE, SPACE_SIZE, GRID_SIZE)

X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

# ===============================
# HELPERS
# ===============================

def normalize(a):
    a = a - np.min(a)
    m = np.max(a)
    if m < 1e-12:
        return np.zeros_like(a)
    return a / m

def gaussian3d(xv, yv, zv, x0, y0, z0, sigma, amp=1.0):
    return amp * np.exp(-((xv-x0)**2 + (yv-y0)**2 + (zv-z0)**2)/(2*sigma**2))

def stylize(img):
    base = normalize(img)

    grain = np.floor(base * LEVELS) / LEVELS
    grain = np.where(grain > THRESHOLD, grain, 0)

    out = (1 - SMOOTH_TO_GRAIN) * base + SMOOTH_TO_GRAIN * grain

    gy, gx = np.gradient(out)
    edge = normalize(np.sqrt(gx**2 + gy**2))
    out = (1 - EDGE_MIX) * out + EDGE_MIX * edge

    return normalize(out)

# ===============================
# FIELD COMPONENTS
# ===============================

def make_baryonic_field(t):
    """
    Normale / sichtbare Materie:
    kompaktere, stärker lokalisierte Strukturen
    """
    f = np.zeros_like(X)

    sources = [
        (-4.5 + np.sin(t), 3.0, 2.0*np.cos(t), 1.2),
        (4.0, -3.0 + np.cos(t), -2.0, 1.0),
        (2.0*np.cos(t), 5.0, 3.0*np.sin(t), 0.9),
        (-5.0, -4.0, 2.0, 1.1),
    ]

    for sx, sy, sz, amp in sources:
        f += gaussian3d(X, Y, Z, sx, sy, sz, 1.5, amp)

    R = np.sqrt(X**2 + Y**2 + Z**2 + 0.5)
    f += 0.15 * np.sin(0.4*X + 0.3*Y - 0.3*Z - t)
    f += 0.10 * np.cos(0.5*R - t)

    return normalize(f)

def make_dark_matter_field(t):
    """
    Dunkle Materie:
    diffuser, großräumiger, halo-artiger
    """
    d = np.zeros_like(X)

    d += gaussian3d(
        X, Y, Z,
        2.0*np.cos(t),
        2.0*np.sin(t),
        3.0*np.cos(t*0.5),
        3.0, 0.8
    )

    d += gaussian3d(
        X, Y, Z,
        -3.5 + 0.5*np.sin(0.7*t),
        4.0*np.cos(0.4*t),
        -2.5,
        3.8, 0.6
    )

    d += 0.08 * np.cos(0.15*X - 0.12*Y + 0.09*Z - 0.5*t)

    return normalize(d)

def apply_dark_energy_expansion(field, factor):
    """
    Dunkle Energie nicht als Klumpen,
    sondern als sanfte globale Expansion / Glättung.
    """
    R = np.sqrt(X**2 + Y**2 + Z**2)
    expansion = normalize(1.0 - np.exp(-(R**2) / (2 * (SPACE_SIZE * 0.9)**2)))

    mixed = (1.0 - factor) * field + factor * expansion
    return normalize(mixed)

# ===============================
# BUILD FIELD
# ===============================

baryon = make_baryonic_field(TIME)
dark_matter = make_dark_matter_field(TIME)

# Baryonen + Dunkle Materie mischen
F = normalize(BARYON_MIX * baryon + DARK_MATTER_MIX * dark_matter)

# Dunkle Energie als globaler Expansionsanteil anwenden
F = apply_dark_energy_expansion(F, DARK_ENERGY_MIX * 0.35)

# ===============================
# SLICES
# ===============================

mid = GRID_SIZE // 2

xy = F[:, :, mid]
xz = F[:, mid, :]
yz = F[mid, :, :]

xy = stylize(xy)
xz = stylize(xz)
yz = stylize(yz)

# ===============================
# PLOT
# ===============================

fig, axes = plt.subplots(1, 3, figsize=(15, 5.8))
fig.patch.set_facecolor("black")

titles = [
    f"XY-Schnitt  |  z = {z[mid]:.2f}",
    f"XZ-Schnitt  |  y = {y[mid]:.2f}",
    f"YZ-Schnitt  |  x = {x[mid]:.2f}"
]
data = [xy, xz, yz]
cmaps = ["inferno", "viridis", "cool"]

axis_labels = [
    ("X", "Y"),
    ("X", "Z"),
    ("Y", "Z"),
]

for ax, d, title, cmap, (xlabel, ylabel) in zip(axes, data, titles, cmaps, axis_labels):
    im = ax.imshow(
        d.T,
        origin="lower",
        cmap=cmap,
        extent=[-SPACE_SIZE, SPACE_SIZE, -SPACE_SIZE, SPACE_SIZE],
        vmin=0.0,
        vmax=1.0,
        aspect="auto"
    )

    ax.set_title(title, color="white")
    ax.set_xlabel(xlabel, color="white")
    ax.set_ylabel(ylabel, color="white")
    ax.tick_params(colors="white")
    ax.set_facecolor("black")

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.get_yticklabels(), color="white")
    cbar.set_label("Normierte Intensität", color="white")

fig.suptitle(
    f"ABES – NASA/ESA inspired cosmic mix | baryon={BARYON_MIX:.2f}, dark matter={DARK_MATTER_MIX:.2f}, dark energy={DARK_ENERGY_MIX:.2f} | Earendel vibe z≈{EARRENDEL_REDSHIFT}",
    color="white",
    fontsize=11
)

plt.tight_layout()
plt.show()