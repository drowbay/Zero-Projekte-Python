import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Materialdaten: stark vereinfacht
# -----------------------------
materials = {
    "Wasser": {
        "slowdown": 0.82,
        "absorption": 0.18,
    },
    "Polyethylen": {
        "slowdown": 0.88,
        "absorption": 0.22,
    },
    "Paraffin": {
        "slowdown": 0.80,
        "absorption": 0.16,
    },
    "Beton": {
        "slowdown": 0.45,
        "absorption": 0.20,
    },
    "Borcarbid": {
        "slowdown": 0.35,
        "absorption": 0.70,
    },
    "Cadmium": {
        "slowdown": 0.20,
        "absorption": 0.82,
    },
    "Lithium-6": {
        "slowdown": 0.30,
        "absorption": 0.78,
    },
    "Mond-Regolith": {
        "slowdown": 0.38,
        "absorption": 0.14,
    },
}

NEUTRONS = 400
LAYERS = 30
START_ENERGY = 14.0  # MeV, schnelle Neutronen


def simulate_material(slowdown, absorption):
    energies = np.full(NEUTRONS, START_ENERGY)
    alive = np.ones(NEUTRONS, dtype=bool)
    survivors_per_layer = []

    for _ in range(LAYERS):
        for i in range(NEUTRONS):
            if not alive[i]:
                continue

            # Absorption
            if np.random.random() < absorption * 0.08:
                alive[i] = False
                energies[i] = 0
                continue

            # Abbremsung
            loss = slowdown * np.random.uniform(0.15, 0.45)
            energies[i] = max(0, energies[i] - loss)

            # Sehr langsame Neutronen verschwinden aus dem "Gefahrenbild"
            if energies[i] < 0.05:
                alive[i] = False

        survivors_per_layer.append(np.sum(alive))

    return survivors_per_layer


# -----------------------------
# Simulation
# -----------------------------
np.random.seed(42)

results = {}

for name, props in materials.items():
    results[name] = simulate_material(
        props["slowdown"],
        props["absorption"]
    )


# -----------------------------
# Visualisierung nebeneinander
# -----------------------------
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for ax, (name, survivors) in zip(axes, results.items()):
    ax.plot(range(1, LAYERS + 1), survivors, linewidth=2)
    ax.fill_between(range(1, LAYERS + 1), survivors, alpha=0.25)

    ax.set_title(name)
    ax.set_xlabel("Schichttiefe")
    ax.set_ylabel("aktive Neutronen")
    ax.set_ylim(0, NEUTRONS)
    ax.grid(True, alpha=0.3)

    final_percent = survivors[-1] / NEUTRONS * 100
    ax.text(
        1,
        NEUTRONS * 0.88,
        f"Durch: {final_percent:.1f}%",
        fontsize=10
    )

plt.suptitle(
    "Neutronenstrahlung: Dämmung / Abbremsung / Absorption nebeneinander",
    fontsize=16
)

plt.tight_layout()
plt.show()()