import numpy as np
import matplotlib.pyplot as plt

# =====================================================
# Zero/Lumi Vergleichs-Tool:
# Feldpulsation / Messwerte gegen echte Physik-Modelle
# =====================================================
#
# Ziel:
# Du kannst später echte Messwerte eintragen.
# Das Script vergleicht dann:
# - 1/r
# - 1/r^2
# - 1/r^3
# - 1/r^4
# - exp(-k*r)
#
# und zeigt, welches Modell am ähnlichsten ist.
# =====================================================

# -----------------------------------------
# 1. Hier später echte Messwerte eintragen
# -----------------------------------------
# distance = Abstand zum Sensor
# measurement = gemessene Signalstärke
#
# Beispiel-Daten sind hier künstlich erzeugt.
# Später kannst du diese beiden Arrays ersetzen.

distance = np.array([1, 2, 3, 4, 5, 7, 10, 14, 20], dtype=float)

# Beispiel: simuliertes Signal, ungefähr wie 1/r^2 mit etwas Rauschen
np.random.seed(7)
measurement = (1 / distance**2) * (1 + 0.12 * np.random.randn(len(distance)))

# Negative Messfehler verhindern
measurement = np.abs(measurement)

# -----------------------------------------
# 2. Hilfsfunktionen
# -----------------------------------------

def normalize(y):
    """Normiert Kurven auf Maximum 1, damit Formen vergleichbar sind."""
    y = np.array(y, dtype=float)
    max_val = np.max(np.abs(y))
    if max_val == 0:
        return y
    return y / max_val

def rmse(a, b):
    """Root Mean Square Error: kleiner = ähnlicher."""
    return np.sqrt(np.mean((a - b)**2))

# -----------------------------------------
# 3. Vergleichsmodelle
# -----------------------------------------

r = distance.copy()

models = {}

models["1/r  Wellen-Fernfeld"] = 1 / r
models["1/r² Intensität"] = 1 / r**2
models["1/r³ Dipol/Nahfeld"] = 1 / r**3
models["1/r⁴ Casimir-artig"] = 1 / r**4

# Exponentielle Dämpfung: wir testen mehrere k-Werte
best_exp_error = None
best_exp_curve = None
best_k = None

measurement_norm = normalize(measurement)

for k in np.linspace(0.05, 1.5, 200):
    exp_curve = np.exp(-k * r)
    exp_norm = normalize(exp_curve)
    error = rmse(measurement_norm, exp_norm)

    if best_exp_error is None or error < best_exp_error:
        best_exp_error = error
        best_exp_curve = exp_curve
        best_k = k

models[f"exp(-k r), k={best_k:.3f}"] = best_exp_curve

# -----------------------------------------
# 4. Fehler berechnen
# -----------------------------------------

errors = {}

for name, curve in models.items():
    curve_norm = normalize(curve)
    errors[name] = rmse(measurement_norm, curve_norm)

# Nach Fehler sortieren
sorted_errors = sorted(errors.items(), key=lambda x: x[1])

print("\n=== Modellvergleich ===")
print("Kleiner Fehler = bessere Ähnlichkeit\n")

for name, error in sorted_errors:
    print(f"{name:25s}  Fehler: {error:.5f}")

best_model_name = sorted_errors[0][0]
print("\nBeste Annäherung:", best_model_name)

# -----------------------------------------
# 5. Plot 1: Kurvenvergleich
# -----------------------------------------

plt.figure(figsize=(10, 6))
plt.title("Vergleich: Messung/Simulation gegen Physik-Modelle")
plt.xlabel("Abstand r")
plt.ylabel("normierte Signalstärke")
plt.grid(True)

plt.plot(distance, measurement_norm, "o-", linewidth=3, label="Messung / Simulation")

for name, curve in models.items():
    plt.plot(distance, normalize(curve), "--", label=name)

plt.legend()
plt.tight_layout()
plt.show()

# -----------------------------------------
# 6. Plot 2: Fehlerbalken / Ranking
# -----------------------------------------

names = [x[0] for x in sorted_errors]
values = [x[1] for x in sorted_errors]

plt.figure(figsize=(10, 5))
plt.title("Fehlervergleich der Modelle")
plt.xlabel("Modell")
plt.ylabel("RMSE-Fehler")
plt.grid(True, axis="y")

plt.bar(names, values)
plt.xticks(rotation=25, ha="right")

plt.tight_layout()
plt.show()

# -----------------------------------------
# 7. Optional: Residuen des besten Modells
# -----------------------------------------

best_curve = normalize(models[best_model_name])
residual = measurement_norm - best_curve

plt.figure(figsize=(10, 5))
plt.title(f"Residuen: Messung minus bestes Modell\n{best_model_name}")
plt.xlabel("Abstand r")
plt.ylabel("Abweichung")
plt.axhline(0, linestyle="--")
plt.grid(True)

plt.plot(distance, residual, "o-", linewidth=2)

plt.tight_layout()
plt.show()