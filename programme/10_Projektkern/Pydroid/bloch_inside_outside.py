import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def bloch_coords(theta, phi):
    """Berechne (x,y,z) auf der Bloch-Sphere für gegebenes (theta,phi)."""
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return np.array([x, y, z])

def rotation_matrix_from_vectors(u, v):
    """Erzeuge Rotationsmatrix, die Vektor u auf v abbildet."""
    u = u / np.linalg.norm(u)
    v = v / np.linalg.norm(v)
    cross = np.cross(u, v)
    dot = np.dot(u, v)
    if np.isclose(dot, -1.0):
        # 180° Drehung um senkrechte Achse
        perp = np.array([1,0,0]) if abs(u[0]) < 0.9 else np.array([0,1,0])
        axis = np.cross(u, perp)
        axis = axis / np.linalg.norm(axis)
        return -np.eye(3) + 2*np.outer(axis,axis)
    elif np.isclose(dot, 1.0):
        return np.eye(3)
    else:
        s = np.linalg.norm(cross)
        kmat = np.array([[0, -cross[2], cross[1]],
                         [cross[2], 0, -cross[0]],
                         [-cross[1], cross[0], 0]])
        return np.eye(3) + kmat + kmat @ kmat * ((1 - dot) / (s**2))

def plot_bloch_dual(theta, phi, save_as="bloch_inside_outside.mp4"):
    state_vec = bloch_coords(theta, phi)

    # Sphere mesh
    u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
    xs = np.cos(u) * np.sin(v)
    ys = np.sin(u) * np.sin(v)
    zs = np.cos(v)
    sphere_points = np.stack([xs,ys,zs], axis=-1)

    # Rotation for inside view
    R = rotation_matrix_from_vectors(state_vec, np.array([0,0,1]))
    sphere_points_rot = sphere_points @ R.T

    fig = plt.figure(figsize=(10,5))
    ax1 = fig.add_subplot(121, projection="3d")
    ax2 = fig.add_subplot(122, projection="3d")

    def init_axes(ax, title):
        ax.set_xlim([-1,1]); ax.set_ylim([-1,1]); ax.set_zlim([-1,1])
        ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
        ax.set_title(title)

    init_axes(ax1, "Außen-Sicht")
    init_axes(ax2, "Innen-Sicht")

    ax1.plot_wireframe(xs, ys, zs, color="orange", alpha=0.3)
    ax2.plot_wireframe(sphere_points_rot[...,0],
                       sphere_points_rot[...,1],
                       sphere_points_rot[...,2],
                       color="orange", alpha=0.3)

    # Vectors
    ax1.quiver(0,0,0,state_vec[0],state_vec[1],state_vec[2],color="red",linewidth=3)
    ax2.quiver(0,0,0,0,0,1,color="red",linewidth=3)

    def update(angle):
        ax1.view_init(30, angle)
        ax2.view_init(30, angle)
        return []

    ani = animation.FuncAnimation(fig, update, frames=np.arange(0,360,3), interval=120)
    ani.save(save_as, writer="ffmpeg", dpi=150)
    print(f"Animation saved as {save_as}")

if __name__ == "__main__":
    # Beispiel: θ=π/3, φ=π/4
    theta, phi = np.pi/3, np.pi/4
    plot_bloch_dual(theta, phi)
