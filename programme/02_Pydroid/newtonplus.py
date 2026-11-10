import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

G = 6.674e-11

# --- Beispiel REAL DATA (vereinfacht, typische Galaxie) ---
# Radius (Meter)
r_data = np.array([
    1e19, 2e19, 3e19, 5e19, 8e19,
    1e20, 2e20, 5e20, 8e20, 1e21
])

# Geschwindigkeit (m/s) – flache Kurve simuliert reale Messung
v_data = np.array([
    1.2e5, 1.5e5, 1.7e5, 1.9e5, 2.0e5,
    2.1e5, 2.1e5, 2.2e5, 2.2e5, 2.2e5
])

# --- Dein Modell ---
def velocity_model(r, M, epsilon0, rc):
    F_newton = G * M / r**2
    epsilon_r = epsilon0 * (r / (r + rc))
    F_total = F_newton + epsilon_r / r
    return np.sqrt(r * F_total)

# --- Fit durchführen ---
initial_guess = [1e41, 1e-10, 1e20]

params, covariance = curve_fit(velocity_model, r_data, v_data, p0=initial_guess)

M_fit, epsilon_fit, rc_fit = params

print("Gefittete Parameter:")
print("M =", M_fit)
print("epsilon0 =", epsilon_fit)
print("rc =", rc_fit)

# --- Modellkurve ---
r_plot = np.logspace(19, 21.5, 500)
v_fit = velocity_model(r_plot, M_fit, epsilon_fit, rc_fit)

# --- Plot ---
plt.figure(figsize=(10,6))

plt.scatter(r_data, v_data, color='red', label="Daten")
plt.loglog(r_plot, v_fit, label="Dein Modell (Fit)")
plt.xlabel("Radius (m)")
plt.ylabel("Geschwindigkeit (m/s)")
plt.title("Real Data Fit – Galaxienrotation")
plt.legend()
plt.grid(True)

plt.show()