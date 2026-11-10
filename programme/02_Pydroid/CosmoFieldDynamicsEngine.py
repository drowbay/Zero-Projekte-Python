import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Pluto reale Parameter
# -----------------------------
PLUTO = {
    "radius_km": 1188.3,
    "mass_kg": 1.303e22,
    "gravity_surface": 0.62  # m/s^2
}

# -----------------------------
# Simulation Parameter
# -----------------------------
SIZE = 15          # Raumgröße (40x40x40)
STEPS = 50        # Zeitschritte
DIFFUSION = 0.12   # Energieausbreitung
GRAVITY_SCALE = 2  # Stärke Gravitationseinfluss

# -----------------------------
# Raum erstellen
# -----------------------------
space = np.zeros((SIZE, SIZE, SIZE))

cx = cy = cz = SIZE // 2  # Pluto Position

# Startimpuls
space[cx, cy, cz] = 5


# -----------------------------
# Gravitation von Pluto
# -----------------------------
def gravity_field(x, y, z):

    dx = x - cx
    dy = y - cy
    dz = z - cz

    r = np.sqrt(dx*dx + dy*dy + dz*dz) + 0.0001

    g = PLUTO["gravity_surface"] / (r*r)

    return g


# -----------------------------
# Simulation Schritt
# -----------------------------
def step(field):

    new = field.copy()

    for x in range(1, SIZE-1):
        for y in range(1, SIZE-1):
            for z in range(1, SIZE-1):

                # Nachbarn
                neighbors = (
                    field[x+1,y,z] +
                    field[x-1,y,z] +
                    field[x,y+1,z] +
                    field[x,y-1,z] +
                    field[x,y,z+1] +
                    field[x,y,z-1]
                ) / 6

                diffusion = neighbors - field[x,y,z]

                g = gravity_field(x,y,z)

                new[x,y,z] += DIFFUSION * diffusion
                new[x,y,z] += GRAVITY_SCALE * g

    return new


# -----------------------------
# Simulation Loop
# -----------------------------
for t in range(STEPS):

    print("Simulation Step:", t)

    space = step(space)

    if t % 10 == 0:

        plt.clf()

        # mittlere Scheibe anzeigen
        slice_ = space[:,:,SIZE//2]

        plt.imshow(slice_, cmap="inferno")
        plt.title(f"Pluto Field Simulation – step {t}")
        plt.colorbar()

        plt.pause(0.01)

plt.show()
