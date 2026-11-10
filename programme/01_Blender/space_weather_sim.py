
"""
Space Weather Toy Viz (2D magnetosphere-like) — by ChatGPT for Lumi
Requires: numpy, matplotlib

Usage (local):
  python space_weather_sim.py

Outputs:
  - space_weather_heatmap.png
  - space_weather_surface.png
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

def dipole_field(x, y, m=1.0):
    r2 = x**2 + y**2
    r3 = np.power(r2 + 1e-12, 1.5)
    Psi = m * y / r3
    Bx = np.gradient(Psi, axis=1)
    By = -np.gradient(Psi, axis=0)
    return Bx, By

def solar_wind_field(x, y, Bsw=-0.22):
    Bx = Bsw * np.ones_like(x)
    By = np.zeros_like(y)
    return Bx, By

def compress_dayside(x, scale_day=0.6, scale_night=1.8):
    return np.where(x >= 0, scale_day, scale_night)

def main():
    nx, ny = 600, 300
    x = np.linspace(-12, 8, nx)
    y = np.linspace(-6, 6, ny)
    X, Y = np.meshgrid(x, y)

    Bx_d, By_d = dipole_field(X, Y, m=1.0)
    Bx_sw, By_sw = solar_wind_field(X, Y, Bsw=-0.22)
    k = compress_dayside(X, scale_day=0.6, scale_night=1.8)

    Bx = k * (Bx_d + Bx_sw)
    By = k * (By_d + By_sw)
    Bmag = np.sqrt(Bx**2 + By**2)

    mask = (X**2 + Y**2) < 1.0**2
    Bmag_m = np.ma.array(Bmag, mask=mask)
    Bx_m = np.ma.array(Bx, mask=mask)
    By_m = np.ma.array(By, mask=mask)

    # 2D heatmap + streamlines
    dpi = 120
    fig1 = plt.figure(figsize=(1920/dpi,1080/dpi), dpi=dpi)
    ax = plt.gca()
    ax.imshow(Bmag_m, origin='lower', extent=[x.min(), x.max(), y.min(), y.max()])
    step = 3
    xs = X[::step, ::step]; ys = Y[::step, ::step]
    u = Bx_m[::step, ::step]; v = By_m[::step, ::step]
    ax.streamplot(xs, ys, u, v, density=1.2, linewidth=0.6)
    ax.add_patch(Circle((0,0), 1.0, fill=False, linewidth=1.2))
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('x (≈ Re)'); ax.set_ylabel('y (≈ Re)')
    ax.set_title('Spielzeug‑Magnetosphäre: Heatmap(|B|) + Feldlinien')
    plt.tight_layout()
    plt.savefig('space_weather_heatmap.png', bbox_inches='tight', dpi=dpi)
    plt.close(fig1)

    # 3D surface
    fig2 = plt.figure(figsize=(1920/dpi,1080/dpi), dpi=dpi)
    ax3 = fig2.add_subplot(111, projection='3d')
    step3d = 4
    Xc = X[::step3d, ::step3d]; Yc = Y[::step3d, ::step3d]; Zc = Bmag[::step3d, ::step3d]
    ax3.plot_surface(Xc, Yc, Zc, linewidth=0, antialiased=True, rstride=1, cstride=1)
    ax3.set_xlabel('x (≈ Re)'); ax3.set_ylabel('y (≈ Re)'); ax3.set_zlabel('|B| (arb.)')
    ax3.set_title('Spielzeug‑Magnetosphäre: 3D‑Surface von |B|')
    plt.tight_layout()
    plt.savefig('space_weather_surface.png', bbox_inches='tight', dpi=dpi)
    plt.close(fig2)

if __name__ == '__main__':
    main()
