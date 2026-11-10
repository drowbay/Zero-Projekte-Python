#!/usr/bin/env python3
"""
Emergent layered field simulation
---------------------------------
A conceptual visualization inspired by your idea of multiple fields
coexisting, overlapping, and flowing through one another.

What this script does
- Simulates several conceptual "fields" on the same 2D grid:
    * scalar support field eta
    * directional dynamics field psi
    * electromagnetic-like swirl field
    * gravity-like sink field
    * Higgs-like background field
    * noise / fluctuation field
- Combines them into a total field
- Animates the result with:
    * background intensity = scalar structure
    * streamlines = total directional flow
    * optional particles = tracers moving in the flow

Important note
This is NOT a literal simulation of real quantum fields or spin foam.
It is a conceptual, visual toy model that helps think about:
- overlap
- emergence
- flow
- symmetry breaking
- structure + dynamics

Requirements
------------
pip install numpy matplotlib
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


# -----------------------------
# Configuration
# -----------------------------

@dataclass
class SimConfig:
    grid_n: int = 140
    extent: float = 3.5
    dt: float = 0.05
    frames: int = 400
    particle_count: int = 220
    seed: int = 7

    show_particles: bool = True
    show_streamlines: bool = True

    # relative strengths
    eta_strength: float = 0.80
    psi_strength: float = 1.20
    em_strength: float = 0.75
    grav_strength: float = 0.65
    higgs_strength: float = 0.40
    noise_strength: float = 0.10

    # symmetry-breaking knob
    asymmetry: float = 0.22


CFG = SimConfig()


# -----------------------------
# Grid helpers
# -----------------------------

def make_grid(n: int, extent: float) -> Tuple[np.ndarray, np.ndarray]:
    x = np.linspace(-extent, extent, n)
    y = np.linspace(-extent, extent, n)
    return np.meshgrid(x, y)


X, Y = make_grid(CFG.grid_n, CFG.extent)
R = np.sqrt(X**2 + Y**2) + 1e-9
TH = np.arctan2(Y, X)


# -----------------------------
# Conceptual field definitions
# -----------------------------

def eta_scalar(x: np.ndarray, y: np.ndarray, t: float) -> np.ndarray:
    """
    'eta' = stabilizing background structure
    symmetric support field
    """
    r2 = x**2 + y**2
    base = np.exp(-0.33 * r2)
    ring = np.exp(-2.3 * (np.sqrt(r2) - 1.65 - 0.08 * np.sin(0.7 * t))**2)
    lattice = 0.22 * np.cos(2.0 * x) * np.cos(2.0 * y)
    return CFG.eta_strength * (0.80 * base + 0.55 * ring + lattice)


def psi_vector(x: np.ndarray, y: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    'psi' = directed dynamics
    starts near the center and radiates / twists outward,
    with a small symmetry-breaking term.
    """
    r = np.sqrt(x**2 + y**2) + 1e-9
    theta = np.arctan2(y, x)

    radial = 1.0 / (1.0 + 0.7 * r**2)
    twist = 0.4 * np.sin(4.0 * theta - 1.2 * t)
    break_term = CFG.asymmetry * np.array([np.cos(0.9 * t), np.sin(0.6 * t)])

    ux = radial * (x / r) - twist * (y / r) + break_term[0]
    uy = radial * (y / r) + twist * (x / r) + break_term[1]

    return CFG.psi_strength * ux, CFG.psi_strength * uy


def em_like_vector(x: np.ndarray, y: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Electromagnetic-like swirl around two moving centers.
    """
    c1x, c1y = 0.95 * np.cos(0.8 * t), 0.95 * np.sin(0.9 * t)
    c2x, c2y = -0.95 * np.cos(0.7 * t), -0.95 * np.sin(0.8 * t)

    def swirl(cx: float, cy: float, sign: float) -> Tuple[np.ndarray, np.ndarray]:
        dx = x - cx
        dy = y - cy
        rr = dx**2 + dy**2 + 0.08
        return sign * (-dy / rr), sign * (dx / rr)

    u1x, u1y = swirl(c1x, c1y, +1.0)
    u2x, u2y = swirl(c2x, c2y, -1.0)

    return CFG.em_strength * (u1x + u2x), CFG.em_strength * (u1y + u2y)


def grav_like_vector(x: np.ndarray, y: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Gravity-like sink field pulling toward a drifting center.
    """
    cx = 0.35 * np.cos(0.35 * t)
    cy = 0.35 * np.sin(0.28 * t)
    dx = x - cx
    dy = y - cy
    rr = np.sqrt(dx**2 + dy**2) + 0.12

    ux = -dx / (rr**1.55)
    uy = -dy / (rr**1.55)
    return CFG.grav_strength * ux, CFG.grav_strength * uy


def higgs_scalar(x: np.ndarray, y: np.ndarray, t: float) -> np.ndarray:
    """
    Higgs-like background: mostly uniform, gently modulated.
    """
    mod = 0.12 * np.sin(0.55 * t + 0.7 * x) * np.cos(0.45 * t + 0.7 * y)
    return CFG.higgs_strength * (1.0 + mod)


def fluctuation_scalar(x: np.ndarray, y: np.ndarray, t: float) -> np.ndarray:
    """
    Small structured fluctuations.
    """
    return CFG.noise_strength * (
        0.6 * np.sin(2.3 * x - 1.1 * t)
        + 0.6 * np.cos(2.0 * y + 0.9 * t)
        + 0.35 * np.sin(1.7 * (x + y) + 1.7 * t)
    )


def total_scalar(x: np.ndarray, y: np.ndarray, t: float) -> np.ndarray:
    return (
        eta_scalar(x, y, t)
        + higgs_scalar(x, y, t)
        + fluctuation_scalar(x, y, t)
    )


def total_vector(x: np.ndarray, y: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
    psi_x, psi_y = psi_vector(x, y, t)
    em_x, em_y = em_like_vector(x, y, t)
    g_x, g_y = grav_like_vector(x, y, t)

    # Add a weak drift derived from the gradient of eta
    eta = eta_scalar(x, y, t)
    gy, gx = np.gradient(eta)
    gx = gx / max(np.max(np.abs(gx)), 1e-6)
    gy = gy / max(np.max(np.abs(gy)), 1e-6)

    ux = psi_x + em_x + g_x + 0.22 * gx
    uy = psi_y + em_y + g_y + 0.22 * gy
    return ux, uy


# -----------------------------
# Particle tracing
# -----------------------------

def init_particles(count: int, extent: float, rng: np.random.Generator) -> np.ndarray:
    pts = rng.uniform(-extent * 0.85, extent * 0.85, size=(count, 2))
    return pts


def sample_field(xp: np.ndarray, yp: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray]:
    ux, uy = total_vector(xp, yp, t)
    return ux, uy


def advect_particles(particles: np.ndarray, t: float, dt: float, extent: float) -> np.ndarray:
    # simple RK2 step
    x1 = particles[:, 0]
    y1 = particles[:, 1]
    u1x, u1y = sample_field(x1, y1, t)

    xm = x1 + 0.5 * dt * u1x
    ym = y1 + 0.5 * dt * u1y
    u2x, u2y = sample_field(xm, ym, t + 0.5 * dt)

    particles[:, 0] = x1 + dt * u2x
    particles[:, 1] = y1 + dt * u2y

    # wrap to keep particles in view
    particles[:, 0] = np.where(particles[:, 0] > extent, -extent, particles[:, 0])
    particles[:, 0] = np.where(particles[:, 0] < -extent, extent, particles[:, 0])
    particles[:, 1] = np.where(particles[:, 1] > extent, -extent, particles[:, 1])
    particles[:, 1] = np.where(particles[:, 1] < -extent, extent, particles[:, 1])

    return particles


# -----------------------------
# Plot / animation
# -----------------------------

def make_animation() -> None:
    rng = np.random.default_rng(CFG.seed)
    particles = init_particles(CFG.particle_count, CFG.extent, rng)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-CFG.extent, CFG.extent)
    ax.set_ylim(-CFG.extent, CFG.extent)
    ax.set_aspect("equal")
    ax.set_title("Emergent Layered Fields (conceptual)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    scalar0 = total_scalar(X, Y, 0.0)
    im = ax.imshow(
        scalar0,
        origin="lower",
        extent=(-CFG.extent, CFG.extent, -CFG.extent, CFG.extent),
        alpha=0.85,
        interpolation="bilinear",
    )

    # initial streamlines
    stream_container = {"artists": None}
    if CFG.show_streamlines:
        u0, v0 = total_vector(X, Y, 0.0)
        speed0 = np.sqrt(u0**2 + v0**2)
        stream = ax.streamplot(
            np.linspace(-CFG.extent, CFG.extent, CFG.grid_n),
            np.linspace(-CFG.extent, CFG.extent, CFG.grid_n),
            u0,
            v0,
            density=1.35,
            linewidth=0.4 + 1.2 * speed0 / (speed0.max() + 1e-9),
            arrowsize=0.8,
        )
        stream_container["artists"] = stream

    scat = None
    if CFG.show_particles:
        scat = ax.scatter(
            particles[:, 0],
            particles[:, 1],
            s=8,
            alpha=0.85,
        )

    # annotate a conceptual legend directly on the axes
    text = ax.text(
        0.02,
        0.98,
        "η: support structure\nψ: directed dynamics\nEM-like swirl\nGravity-like sink\nHiggs-like background",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox=dict(boxstyle="round", alpha=0.15),
    )

    def update(frame: int):
        t = frame * CFG.dt

        scalar = total_scalar(X, Y, t)
        im.set_data(scalar)
        im.set_clim(vmin=np.percentile(scalar, 5), vmax=np.percentile(scalar, 95))

        if CFG.show_streamlines:
            # remove old streamlines
            old = stream_container["artists"]
            if old is not None:
                try:
                    old.lines.remove()
                except Exception:
                    pass
                try:
                    for p in old.arrows.patches:
                        p.remove()
                except Exception:
                    pass

            u, v = total_vector(X, Y, t)
            speed = np.sqrt(u**2 + v**2)
            stream = ax.streamplot(
                np.linspace(-CFG.extent, CFG.extent, CFG.grid_n),
                np.linspace(-CFG.extent, CFG.extent, CFG.grid_n),
                u,
                v,
                density=1.35,
                linewidth=0.4 + 1.2 * speed / (speed.max() + 1e-9),
                arrowsize=0.8,
            )
            stream_container["artists"] = stream

        if CFG.show_particles and scat is not None:
            advect_particles(particles, t, CFG.dt, CFG.extent)
            scat.set_offsets(particles)

        ax.set_title(f"Emergent Layered Fields (conceptual)   t = {t:5.2f}")

        artists = [im, text]
        if scat is not None:
            artists.append(scat)
        return artists

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=CFG.frames,
        interval=40,
        blit=False,
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    make_animation()
