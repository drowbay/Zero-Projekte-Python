import numpy as np
import matplotlib.pyplot as plt

def bloch_coords(theta, phi):
    """Berechnet die (x,y,z) Koordinaten des Qubit-Zustands auf der Bloch-Sphere."""
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return x, y, z

def plot_bloch(theta, phi, title="Bloch Sphere"):
    # Bloch Sphere erzeugen
    u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
    xs = np.cos(u)*np.sin(v)
    ys = np.sin(u)*np.sin(v)
    zs = np.cos(v)

    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111, projection="3d")

    # Gitter-Kugel zeichnen
    ax.plot_wireframe(xs, ys, zs, color="orange", alpha=0.3)

    # Achsen |0>, |1>
    ax.quiver(0,0,0, 0,0,1, color="black", linewidth=2)
    ax.text(0,0,1.05, "|0⟩", fontsize=12)
    ax.quiver(0,0,0, 0,0,-1, color="black", linewidth=2)
    ax.text(0,0,-1.1, "|1⟩", fontsize=12)

    # Zustand berechnen
    x, y, z = bloch_coords(theta, phi)

    # Vektor zeichnen
    ax.quiver(0,0,0, x,y,z, color="red", linewidth=3)
    ax.text(x*1.1, y*1.1, z*1.1, "Qubit-Zustand", fontsize=10)

    # Achsenbeschriftung
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(title)

    # Skalen fix
    ax.set_xlim([-1,1])
    ax.set_ylim([-1,1])
    ax.set_zlim([-1,1])

    plt.show()

if __name__ == "__main__":
    # Beispiel: Superposition (|0> + |1>)/√2 → θ=π/2, φ=0
    theta = np.pi/2
    phi = 0
    plot_bloch(theta, phi, title="Bloch Sphere: (|0>+|1>)/√2")
