import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ==========================================
# Zero/Lumi: Feldpulsation Mess-Simulation
# ==========================================
# Idee:
# Eine Quelle pulsiert.
# Das Feld breitet sich aus.
# Je weiter weg ein Sensor ist, desto schwächer wird das Signal.
#
# Physik-nahes Prinzip:
# Signal = Amplitude * sin(Welle)
# Abstand dämpft die Amplitude.
#
# Keine echte Brane/Bulk-Messung,
# sondern ein Anschauungsmodell für:
# Feldpulsation -> Kopplung -> Messsignal
# ==========================================

# Raumgitter
x = np.linspace(-12, 12, 500)

# Parameter
frequency = 1.2       # Schwingungsgeschwindigkeit
wave_number = 1.8     # Wellenstruktur im Raum
decay = 0.28          # Dämpfung mit Abstand
source_strength = 1.0 # Stärke der Quelle

# Sensorpositionen
sensor_positions = [-2, 4, 8]

# Messverlauf speichern
history = {pos: [] for pos in sensor_positions}
max_history = 250

fig, (ax_field, ax_signal) = plt.subplots(2, 1, figsize=(10, 7))
fig.suptitle("Feldpulsation: Feld -> Abstand -> Messsignal", fontsize=14)

# Oberer Plot: Feld im Raum
ax_field.set_xlim(x.min(), x.max())
ax_field.set_ylim(-1.4, 1.4)
ax_field.set_title("Pulsierendes Feld im Raum")
ax_field.set_xlabel("Raumposition")
ax_field.set_ylabel("Feldstärke")
ax_field.grid(True)

field_line, = ax_field.plot([], [], linewidth=2, label="Feldpulsation")
source_dot, = ax_field.plot([0], [0], marker="o", markersize=10, label="Quelle")

sensor_dots = []
for pos in sensor_positions:
    dot, = ax_field.plot([pos], [0], marker="s", markersize=8, label=f"Sensor x={pos}")
    sensor_dots.append(dot)

ax_field.legend(loc="upper right")

# Unterer Plot: Sensorwerte über Zeit
ax_signal.set_xlim(0, max_history)
ax_signal.set_ylim(-1.1, 1.1)
ax_signal.set_title("Gemessene Signale an verschiedenen Abständen")
ax_signal.set_xlabel("Zeit")
ax_signal.set_ylabel("Sensorsignal")
ax_signal.grid(True)

signal_lines = {}
for pos in sensor_positions:
    line, = ax_signal.plot([], [], linewidth=2, label=f"Sensor x={pos}")
    signal_lines[pos] = line

ax_signal.legend(loc="upper right")

info_text = ax_field.text(
    -11.5, 1.15,
    "",
    fontsize=10,
    bbox=dict(boxstyle="round", alpha=0.15)
)

def field_function(x_values, t):
    # Abstand von Quelle
    r = np.abs(x_values)

    # Dämpfung: weiter weg = schwächer
    amplitude = source_strength * np.exp(-decay * r)

    # Pulsierende Welle
    wave = np.sin(wave_number * r - frequency * t)

    return amplitude * wave

def update(frame):
    t = frame * 0.08

    # Feld berechnen
    y = field_function(x, t)
    field_line.set_data(x, y)

    # Sensorwerte berechnen
    for pos, dot in zip(sensor_positions, sensor_dots):
        value = field_function(np.array([pos]), t)[0]

        history[pos].append(value)
        if len(history[pos]) > max_history:
            history[pos] = history[pos][-max_history:]

        dot.set_data([pos], [value])

        signal_lines[pos].set_data(
            np.arange(len(history[pos])),
            history[pos]
        )

    info_text.set_text(
        "Feldpulsation = zeitliche Änderung eines Feldzustands\n"
        "Je weiter der Sensor weg ist, desto schwächer wird das Signal\n"
        "Messbar wird es erst, wenn Feld und Sensor koppeln"
    )

    return [field_line, source_dot, info_text] + sensor_dots + list(signal_lines.values())

ani = FuncAnimation(
    fig,
    update,
    frames=2000,
    interval=35,
    blit=True
)

plt.tight_layout()
plt.show()