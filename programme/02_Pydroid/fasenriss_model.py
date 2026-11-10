# fasenriss_model.py
# Eigenständiges Script für das Projekt "Fasenriss"
# - Plottet S(c) und die Fasenriss-Punkte (n=c^2)
# - Plottet eine 3D-Oberfläche S_eff(c, s) mit s=Subgruppen
# - Exportiert die 3D-Oberfläche als .obj-Mesh

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

def S_of_c(c: float) -> float:
    return 1.0 / (c*c - 1.0)

def S_eff(c: float, s: float) -> float:
    n_eff = (c*c) / max(s, 1e-9)
    if n_eff <= 1.0:
        return np.nan
    return 1.0 / (n_eff - 1.0)

def plot_fasenriss_points(c_min=2, c_max=10):
    cs = np.arange(c_min, c_max+1)
    Ss = 1.0 / (cs**2 - 1.0)
    plt.figure()
    plt.plot(cs, 1.0/(cs**2 - 1.0), linestyle="--")
    plt.scatter(cs, Ss, marker="x")
    plt.title("Fasenriss – S(c) bei Quadratzahlen (n=c^2)")
    plt.xlabel("c")
    plt.ylabel("S(c)")
    plt.grid(True)
    plt.show()

def plot_surface(c_lo=1.1, c_hi=10.0, s_lo=1.0, s_hi=10.0, n_c=120, n_s=100):
    C = np.linspace(c_lo, c_hi, n_c)
    Sg = np.linspace(s_lo, s_hi, n_s)
    CC, SS = np.meshgrid(C, Sg)
    ZZ = 1.0 / ((CC**2 / SS) - 1.0)
    ZZ[(CC**2 / SS) <= 1.0] = np.nan
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(CC, SS, ZZ, linewidth=0, antialiased=True)
    ax.set_title("Fasenriss-Oberfläche: S_eff(c, s)")
    ax.set_xlabel("c")
    ax.set_ylabel("s (Subgruppen)")
    ax.set_zlabel("S_eff")
    plt.show()
    return CC, SS, ZZ

def save_obj_surface(xgrid, ygrid, zgrid, path: str):
    H, W = xgrid.shape
    verts = []
    faces = []
    for i in range(H):
        for j in range(W):
            z = zgrid[i, j]
            if np.isnan(z):
                verts.append(None)
            else:
                verts.append((xgrid[i, j], ygrid[i, j], z))
    def vid(i, j):
        return i*W + j
    for i in range(H-1):
        for j in range(W-1):
            idx = [vid(i,j), vid(i+1,j), vid(i+1,j+1), vid(i,j+1)]
            if any(verts[k] is None for k in idx):
                continue
            v1, v2, v3, v4 = [k+1 for k in idx]
            faces.append((v1, v2, v3))
            faces.append((v1, v3, v4))
    with open(path, "w", encoding="utf-8") as f:
        f.write("# OBJ file: Fasenriss-Oberfläche S_eff(c,s)\n")
        for v in verts:
            if v is None:
                f.write("v 0 0 0\n")
            else:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for (a,b,c) in faces:
            f.write(f"f {a} {b} {c}\n")

if __name__ == "__main__":
    plot_fasenriss_points()
    CC, SS, ZZ = plot_surface()
    save_obj_surface(CC, SS, ZZ, "fasenriss_surface.obj")
    print("Saved: fasenriss_surface.obj")
