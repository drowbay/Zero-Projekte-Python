import random
import matplotlib.pyplot as plt

# =============================
# REALISTISCHERE LIFE-SUPPORT-SIM
# Mondbasis / Schiff - Core Modell
# =============================

DAYS = 180
CREW = 4

# Startreserven
water_l = 800.0          # Liter
oxygen_kg = 120.0        # kg
co2_kg = 0.0             # kg
energy_kwh = 500.0       # kWh
solid_waste_kg = 0.0     # Kot, Verpackung, Biomüll
bio_risk = 0.0           # Keim-/Schimmelrisiko 0-100
health = 100.0

# Technikparameter
water_recovery_eff = 0.88      # realistisch: 80-95%
urine_recovery_eff = 0.75
co2_scrubber_eff = 0.92
oxygen_recycling_eff = 0.55    # z.B. Elektrolyse/Regeneration vereinfacht
solar_generation_kwh = 42.0    # pro Tag
base_energy_use_kwh = 28.0
life_support_energy_kwh = 9.0

# Tagesverbrauch pro Person
water_need_l = 3.2
oxygen_need_kg = 0.84
co2_produced_kg = 1.0
urine_l = 1.6
greywater_l = 2.0
feces_kg = 0.13

history = {
    "water": [],
    "oxygen": [],
    "co2": [],
    "energy": [],
    "waste": [],
    "bio_risk": [],
    "health": []
}

for day in range(DAYS):
    # -------------------------
    # 1. Menschliche Outputs
    # -------------------------
    daily_water_need = CREW * water_need_l
    daily_o2_need = CREW * oxygen_need_kg
    daily_co2 = CREW * co2_produced_kg
    daily_urine = CREW * urine_l
    daily_greywater = CREW * greywater_l
    daily_feces = CREW * feces_kg

    water_l -= daily_water_need
    oxygen_kg -= daily_o2_need
    co2_kg += daily_co2
    solid_waste_kg += daily_feces

    # -------------------------
    # 2. Energieproduktion
    # kleine Schwankungen: Staub, Tag/Nacht, Defekte
    # -------------------------
    solar_today = solar_generation_kwh * random.uniform(0.75, 1.1)
    energy_kwh += solar_today

    # Energieverbrauch
    energy_kwh -= base_energy_use_kwh
    energy_kwh -= life_support_energy_kwh

    # -------------------------
    # 3. Wasserrecycling
    # -------------------------
    if energy_kwh > 80:
        recovered_urine = daily_urine * urine_recovery_eff
        recovered_grey = daily_greywater * water_recovery_eff
        water_l += recovered_urine + recovered_grey
        energy_kwh -= 5.0
    else:
        # zu wenig Energie = schlechteres Recycling
        recovered_urine = daily_urine * 0.35
        recovered_grey = daily_greywater * 0.45
        water_l += recovered_urine + recovered_grey
        energy_kwh -= 2.0
        bio_risk += 1.5

    # -------------------------
    # 4. CO2-Entfernung + O2-Rückgewinnung
    # -------------------------
    if energy_kwh > 60:
        removed_co2 = co2_kg * co2_scrubber_eff
        co2_kg -= removed_co2

        regenerated_o2 = removed_co2 * oxygen_recycling_eff
        oxygen_kg += regenerated_o2

        energy_kwh -= 7.0
    else:
        # Scrubber läuft schlecht
        removed_co2 = co2_kg * 0.35
        co2_kg -= removed_co2
        oxygen_kg += removed_co2 * 0.2
        energy_kwh -= 3.0

    # -------------------------
    # 5. Festabfall / Hygiene
    # -------------------------
    if energy_kwh > 50:
        # Trocknen/Sterilisieren/Komprimieren
        processed = solid_waste_kg * 0.35
        solid_waste_kg -= processed
        bio_risk -= 1.0
        energy_kwh -= 3.5
    else:
        # Abfall bleibt liegen = Risiko steigt
        bio_risk += 2.5

    # -------------------------
    # 6. Risiko- und Gesundheitslogik
    # -------------------------
    if water_l < 120:
        health -= 1.2

    if oxygen_kg < 30:
        health -= 1.5

    if co2_kg > 12:
        health -= 1.0

    if energy_kwh < 50:
        health -= 0.8

    if solid_waste_kg > 25:
        bio_risk += 1.0

    if bio_risk > 40:
        health -= 1.3

    # zufälliger kleiner Defekt
    if random.random() < 0.03:
        energy_kwh -= random.uniform(10, 35)
        bio_risk += random.uniform(2, 6)

    # Grenzen
    water_l = max(water_l, 0)
    oxygen_kg = max(oxygen_kg, 0)
    co2_kg = max(co2_kg, 0)
    energy_kwh = max(energy_kwh, 0)
    solid_waste_kg = max(solid_waste_kg, 0)
    bio_risk = min(max(bio_risk, 0), 100)
    health = min(max(health, 0), 100)

    # Speichern
    history["water"].append(water_l)
    history["oxygen"].append(oxygen_kg)
    history["co2"].append(co2_kg)
    history["energy"].append(energy_kwh)
    history["waste"].append(solid_waste_kg)
    history["bio_risk"].append(bio_risk)
    history["health"].append(health)

# =============================
# VISUALISIERUNG
# =============================

plt.figure(figsize=(12, 7))
plt.plot(history["water"], label="Wasser (L)")
plt.plot(history["oxygen"], label="Sauerstoff (kg)")
plt.plot(history["co2"], label="CO2 (kg)")
plt.plot(history["energy"], label="Energie (kWh)")
plt.plot(history["waste"], label="Festabfall (kg)")
plt.plot(history["bio_risk"], label="Bio-Risiko")
plt.plot(history["health"], label="Crew-Gesundheit")

plt.title("Realistischere Lebenserhaltung: Wasser, Luft, Energie, Abfall, Krankheiten")
plt.xlabel("Tage")
plt.ylabel("Systemwert")
plt.legend()
plt.grid(True)
plt.show()

print("=== ENDSTATUS ===")
print(f"Wasser: {water_l:.1f} L")
print(f"Sauerstoff: {oxygen_kg:.1f} kg")
print(f"CO2: {co2_kg:.1f} kg")
print(f"Energie: {energy_kwh:.1f} kWh")
print(f"Festabfall: {solid_waste_kg:.1f} kg")
print(f"Bio-Risiko: {bio_risk:.1f}/100")
print(f"Gesundheit: {health:.1f}/100")