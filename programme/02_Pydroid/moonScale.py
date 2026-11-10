import random
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# =============================
# Pydroid3 Mondbasis Simulation
# =============================

crew = 4
water = 800.0
oxygen = 120.0
co2 = 0.0
energy = 500.0
waste = 0.0
bio_risk = 5.0
health = 100.0
day = 0

history_health = []
history_bio = []
history_water = []
history_energy = []

plt.ion()
fig, ax = plt.subplots(figsize=(9, 6))

def clamp(v, a, b):
    return max(a, min(b, v))

def step():
    global water, oxygen, co2, energy, waste, bio_risk, health, day

    day += 1

    # Verbrauch / Produktion
    water -= crew * 3.2
    oxygen -= crew * 0.84
    co2 += crew * 1.0
    waste += crew * 0.13

    # Solarenergie
    energy += 42 * random.uniform(0.72, 1.1)

    # Grundverbrauch
    energy -= 28
    energy -= 9

    # Wasserrecycling
    if energy > 80:
        water += crew * (1.6 * 0.75 + 2.0 * 0.88)
        energy -= 5
        bio_risk -= 0.4
    else:
        water += crew * 1.2
        energy -= 2
        bio_risk += 1.6

    # CO2 → O2 teilweise zurück
    if energy > 60:
        removed = co2 * 0.92
        co2 -= removed
        oxygen += removed * 0.55
        energy -= 7
    else:
        removed = co2 * 0.35
        co2 -= removed
        oxygen += removed * 0.2
        energy -= 3
        bio_risk += 0.8

    # Abfallverarbeitung
    if energy > 50:
        waste -= waste * 0.35
        bio_risk -= 1.0
        energy -= 3.5
    else:
        bio_risk += 2.5

    # Zufallsdefekt
    if random.random() < 0.03:
        energy -= random.uniform(10, 35)
        bio_risk += random.uniform(2, 6)

    # Gesundheit
    if water < 120:
        health -= 1.2
    if oxygen < 30:
        health -= 1.5
    if co2 > 12:
        health -= 1.0
    if energy < 50:
        health -= 0.8
    if bio_risk > 40:
        health -= 1.3

    if water > 250 and oxygen > 60 and energy > 120 and bio_risk < 20:
        health += 0.25

    water = max(water, 0)
    oxygen = max(oxygen, 0)
    co2 = max(co2, 0)
    energy = max(energy, 0)
    waste = max(waste, 0)
    bio_risk = clamp(bio_risk, 0, 100)
    health = clamp(health, 0, 100)

    history_health.append(health)
    history_bio.append(bio_risk)
    history_water.append(water)
    history_energy.append(energy)

    if len(history_health) > 80:
        history_health.pop(0)
        history_bio.pop(0)
        history_water.pop(0)
        history_energy.pop(0)

def draw_bar(x, y, label, value, max_value):
    level = clamp(value / max_value, 0, 1)

    ax.add_patch(Rectangle((x, y), 1.2, 4, fill=False, linewidth=2))
    ax.add_patch(Rectangle((x, y), 1.2, 4 * level, alpha=0.4))

    ax.text(x + 0.6, y + 4.25, label, ha="center", fontsize=9)
    ax.text(x + 0.6, y - 0.35, f"{value:.1f}", ha="center", fontsize=8)

def draw():
    ax.clear()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.set_title("Mondbasis Life Support - Pydroid3 Version")
    ax.axis("off")

    draw_bar(0.5, 1, "Wasser", water, 800)
    draw_bar(2.0, 1, "O2", oxygen, 140)
    draw_bar(3.5, 1, "CO2", co2, 20)
    draw_bar(5.0, 1, "Energie", energy, 650)
    draw_bar(6.5, 1, "Abfall", waste, 35)
    draw_bar(8.0, 1, "Bio", bio_risk, 100)

    if health > 70 and bio_risk < 30:
        status = "STABIL"
    elif health > 35:
        status = "WARNUNG"
    else:
        status = "KRITISCH"

    ax.text(5, 6.4, f"Tag {day} | Crew: {crew} | Gesundheit: {health:.1f}% | {status}",
            ha="center", fontsize=11)

    ax.text(5, 5.8,
            "Kreislauf: Mensch → Urin/Kot/CO2 → Recycling → Wasser/O2 zurück",
            ha="center", fontsize=9)

    # kleine Verlaufskurve
    if len(history_health) > 2:
        ax.plot([0.5 + i * 0.08 for i in range(len(history_health))],
                [0.25 + h * 0.02 for h in history_health],
                linewidth=2)

        ax.plot([0.5 + i * 0.08 for i in range(len(history_bio))],
                [0.25 + b * 0.02 for b in history_bio],
                linestyle="--")

        ax.text(0.5, 0.1, "Kurve: Gesundheit / gestrichelt: Bio-Risiko", fontsize=8)

    plt.pause(0.08)

# Hauptloop
for _ in range(500):
    step()
    draw()

plt.ioff()
plt.show()