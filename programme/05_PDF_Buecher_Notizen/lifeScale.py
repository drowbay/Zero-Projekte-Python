import matplotlib.pyplot as plt
import random

# -----------------------------
# Systemwerte
# -----------------------------
water = 100
energy = 100
waste = 0
health = 100

history_water = []
history_energy = []
history_waste = []
history_health = []

steps = 120

# -----------------------------
# Simulation
# -----------------------------
for t in range(steps):

    # Mensch produziert Abfall
    waste += random.uniform(1, 3)

    # Wasserverbrauch
    water -= random.uniform(0.5, 1.5)

    # Energieverbrauch
    energy -= random.uniform(0.5, 1.2)

    # Recycling (wenn genug Energie)
    if energy > 20:
        recycled = waste * 0.4
        water += recycled * 0.6
        waste -= recycled
        energy -= 2

    # Krankheitseffekt
    if waste > 50:
        health -= 0.5

    # Wassermangel
    if water < 30:
        health -= 0.7

    # Energie kritisch
    if energy < 20:
        health -= 0.4

    # Grenzen
    water = max(0, water)
    energy = max(0, energy)
    waste = max(0, waste)
    health = max(0, health)

    # Speichern
    history_water.append(water)
    history_energy.append(energy)
    history_waste.append(waste)
    history_health.append(health)

# -----------------------------
# Plot
# -----------------------------
plt.figure(figsize=(10, 6))

plt.plot(history_water, label="Wasser")
plt.plot(history_energy, label="Energie")
plt.plot(history_waste, label="Abfall")
plt.plot(history_health, label="Gesundheit")

plt.legend()
plt.title("Lebenssystem Simulation (Kreislauf)")
plt.xlabel("Zeit")
plt.ylabel("Systemwerte")

plt.grid()
plt.show()