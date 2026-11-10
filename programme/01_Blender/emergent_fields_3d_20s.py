from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path

FPS = 12
DURATION = 20
FRAMES = FPS * DURATION
SEED = 7
N_PARTICLES = 260
EXTENT = 3.0
OUT = Path('/mnt/data/emergent_fields_3d_20s.mp4')


def total_vector(x, y, z, t):
    r = np.sqrt(x*x + y*y + z*z) + 1e-9
    shell = np.sin(1.5 * r - 0.7 * t)
    eta_x = -0.10 * x * shell / (1 + 0.35 * r*r)
    eta_y = -0.10 * y * shell / (1 + 0.35 * r*r)
    eta_z = -0.10 * z * shell / (1 + 0.35 * r*r)

    psi_rad = 0.45 / (1 + 0.45 * r*r)
    rho = np.sqrt(x*x + y*y) + 1e-9
    psi_twist = 0.28 * np.sin(2.6 * np.arctan2(y, x) - 1.0 * t)
    psi_x = psi_rad * x / r - psi_twist * y / rho
    psi_y = psi_rad * y / r + psi_twist * x / rho
    psi_z = 0.15 * np.sin(1.7 * z + 0.75 * t)

    c1 = np.array([0.85*np.cos(0.65*t), 0.85*np.sin(0.7*t), 0.4*np.sin(0.45*t)])
    c2 = -c1
    def swirl(cx, cy, cz, sign=1.0):
        dx = x - cx
        dy = y - cy
        dz = z - cz
        rr = dx*dx + dy*dy + dz*dz + 0.14
        return sign * (-dy / rr), sign * (dx / rr), sign * (0.28 * dz / rr)
    e1x, e1y, e1z = swirl(*c1, sign=1.0)
    e2x, e2y, e2z = swirl(*c2, sign=-1.0)

    gx0 = 0.3*np.cos(0.23*t)
    gy0 = 0.3*np.sin(0.19*t)
    gz0 = 0.22*np.cos(0.27*t)
    dx = x - gx0
    dy = y - gy0
    dz = z - gz0
    rr = np.sqrt(dx*dx + dy*dy + dz*dz) + 0.25
    grav_x = -0.22 * dx / (rr**1.35)
    grav_y = -0.22 * dy / (rr**1.35)
    grav_z = -0.22 * dz / (rr**1.35)

    asym_x = 0.05 * np.cos(0.5 * t)
    asym_y = 0.03 * np.sin(0.41 * t)
    asym_z = 0.04 * np.cos(0.33 * t + 0.4)

    ux = eta_x + psi_x + 0.18*(e1x + e2x) + grav_x + asym_x
    uy = eta_y + psi_y + 0.18*(e1y + e2y) + grav_y + asym_y
    uz = eta_z + psi_z + 0.18*(e1z + e2z) + grav_z + asym_z
    return ux, uy, uz


def init_particles(n, extent, rng):
    return rng.uniform(-extent * 0.78, extent * 0.78, size=(n, 3))


def advect(particles, t, dt):
    x1, y1, z1 = particles[:, 0], particles[:, 1], particles[:, 2]
    u1x, u1y, u1z = total_vector(x1, y1, z1, t)
    xm = x1 + 0.5 * dt * u1x
    ym = y1 + 0.5 * dt * u1y
    zm = z1 + 0.5 * dt * u1z
    u2x, u2y, u2z = total_vector(xm, ym, zm, t + 0.5 * dt)
    particles[:, 0] = x1 + dt * u2x
    particles[:, 1] = y1 + dt * u2y
    particles[:, 2] = z1 + dt * u2z
    for i in range(3):
        particles[:, i] = np.where(particles[:, i] > EXTENT, -EXTENT, particles[:, i])
        particles[:, i] = np.where(particles[:, i] < -EXTENT, EXTENT, particles[:, i])
    return particles


def shell_xyz(radius, wobble, t):
    u = np.linspace(0, 2*np.pi, 28)
    v = np.linspace(0, np.pi, 16)
    uu, vv = np.meshgrid(u, v)
    rr = radius + wobble * np.sin(3*uu + 2*vv - 0.8*t)
    xs = rr * np.cos(uu) * np.sin(vv)
    ys = rr * np.sin(uu) * np.sin(vv)
    zs = rr * np.cos(vv)
    return xs, ys, zs


def main():
    rng = np.random.default_rng(SEED)
    particles = init_particles(N_PARTICLES, EXTENT, rng)

    fig = plt.figure(figsize=(5.5, 5.5), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(-EXTENT, EXTENT); ax.set_ylim(-EXTENT, EXTENT); ax.set_zlim(-EXTENT, EXTENT)
    ax.set_box_aspect((1,1,1))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])

    xs1, ys1, zs1 = shell_xyz(1.15, 0.09, 0.0)
    xs2, ys2, zs2 = shell_xyz(1.9, 0.11, 0.5)
    surf1 = [ax.plot_surface(xs1, ys1, zs1, alpha=0.10, linewidth=0, antialiased=False)]
    surf2 = [ax.plot_surface(xs2, ys2, zs2, alpha=0.07, linewidth=0, antialiased=False)]

    qx, qy, qz = np.meshgrid(
        np.linspace(-2.0, 2.0, 4),
        np.linspace(-2.0, 2.0, 4),
        np.linspace(-2.0, 2.0, 3),
    )
    ux, uy, uz = total_vector(qx, qy, qz, 0.0)
    quiver = {'artist': ax.quiver(qx, qy, qz, ux, uy, uz, length=0.14, normalize=True, linewidth=0.35)}

    scat = ax.scatter(particles[:,0], particles[:,1], particles[:,2], s=3, alpha=0.8)
    ax.text2D(0.02, 0.98, '3D emergent layered fields\nη support shells | ψ directed flow', transform=ax.transAxes,
              va='top', fontsize=8, bbox=dict(boxstyle='round', alpha=0.12))
    dt = 0.07

    def update(frame):
        t = frame / FPS
        advect(particles, t, dt)
        scat._offsets3d = (particles[:,0], particles[:,1], particles[:,2])
        surf1[0].remove(); surf2[0].remove()
        x1, y1, z1 = shell_xyz(1.15, 0.09, t)
        x2, y2, z2 = shell_xyz(1.9, 0.11, t+0.5)
        surf1[0] = ax.plot_surface(x1, y1, z1, alpha=0.10, linewidth=0, antialiased=False)
        surf2[0] = ax.plot_surface(x2, y2, z2, alpha=0.07, linewidth=0, antialiased=False)
        quiver['artist'].remove()
        ux, uy, uz = total_vector(qx, qy, qz, t)
        quiver['artist'] = ax.quiver(qx, qy, qz, ux, uy, uz, length=0.14, normalize=True, linewidth=0.35)
        ax.view_init(elev=22 + 4*np.sin(0.24*t), azim=frame*1.3)
        ax.set_title(f'Emergent Layered Fields — 3D   t={t:4.1f}s')
        return scat,

    ani = FuncAnimation(fig, update, frames=FRAMES, interval=1000/FPS, blit=False)
    try:
        ani.save(OUT, writer='ffmpeg', fps=FPS, bitrate=1400)
        print(f'Saved {OUT}')
    except Exception as e:
        print('ffmpeg failed:', e)
        gif = OUT.with_suffix('.gif')
        ani.save(gif, writer='pillow', fps=FPS)
        print(f'Saved {gif}')
    plt.close(fig)

if __name__ == '__main__':
    main()
