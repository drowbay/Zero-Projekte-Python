import pygame
import math
import random

# ============================================================
# TIRXY FIELD CASCADE
# ------------------------------------------------------------
# Zero + Lumi Zustandsfeld-Demo
#
# Idee:
# - Raum = aktives Zustandsfeld
# - Energie verteilt sich dynamisch
# - Nachbarfelder koppeln sich
# - Stabile Muster entstehen emergent
# - Materie = lokale Verdichtung
#
# Steuerung:
# SPACE = Modus wechseln
# R     = Reset
# ESC   = Ende
# ============================================================

pygame.init()

# ------------------------------------------------------------
# Fenster
# ------------------------------------------------------------
W, H = 1000, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("TIRXY FIELD CASCADE")

clock = pygame.time.Clock()

# ------------------------------------------------------------
# Farben
# ------------------------------------------------------------
BG = (4, 5, 16)

TEXT = (220, 235, 255)

# ------------------------------------------------------------
# Grid
# ------------------------------------------------------------
GRID = 14

GW = W // GRID
GH = H // GRID

# ------------------------------------------------------------
# Modi
# ------------------------------------------------------------
MODE = 0

MODES = [
    "Relaxation",
    "Wave Cascade",
    "Emergent Matter",
    "Quantum Noise"
]

# ------------------------------------------------------------
# Hilfsfunktion
# ------------------------------------------------------------
def clamp(v, a, b):
    return max(a, min(b, v))

# ------------------------------------------------------------
# Feldzellen
# ------------------------------------------------------------
cells = []

def reset_cells():

    global cells

    cells = []

    for x in range(GW):

        row = []

        for y in range(GH):

            row.append({
                "energy": random.random(),
                "phase": random.random() * math.tau,
                "velocity": random.uniform(-0.02, 0.02),
            })

        cells.append(row)

reset_cells()

# ------------------------------------------------------------
# Nachbarenergie
# ------------------------------------------------------------
def neighbor_energy(gx, gy):

    total = 0
    count = 0

    for ox in [-1, 0, 1]:
        for oy in [-1, 0, 1]:

            nx = (gx + ox) % GW
            ny = (gy + oy) % GH

            total += cells[nx][ny]["energy"]
            count += 1

    return total / count

# ------------------------------------------------------------
# Update
# ------------------------------------------------------------
def update_cells(t):

    new_energy = []

    for gx in range(GW):

        row = []

        for gy in range(GH):

            c = cells[gx][gy]

            e = c["energy"]

            n = neighbor_energy(gx, gy)

            # ------------------------------------------------
            # MODE 0 = Relaxation
            # ------------------------------------------------
            if MODE == 0:

                e += (n - e) * 0.03
                e += math.sin(t * 0.01 + c["phase"]) * 0.003

            # ------------------------------------------------
            # MODE 1 = Wellenkaskade
            # ------------------------------------------------
            elif MODE == 1:

                wave = math.sin(
                    gx * 0.12 +
                    gy * 0.09 +
                    t * 0.03 +
                    c["phase"]
                )

                e += wave * 0.01
                e += (n - e) * 0.05

            # ------------------------------------------------
            # MODE 2 = Materiecluster
            # ------------------------------------------------
            elif MODE == 2:

                density = n * n

                e += (density - e) * 0.04

                if density > 0.72:
                    e += 0.02

            # ------------------------------------------------
            # MODE 3 = Quantenrauschen
            # ------------------------------------------------
            elif MODE == 3:

                noise = random.uniform(-0.03, 0.03)

                e += noise
                e += (n - e) * 0.02

                wave = math.sin(
                    t * 0.06 +
                    gx * 0.15 +
                    gy * 0.11
                )

                e += wave * 0.006

            e = clamp(e, 0.0, 1.0)

            row.append(e)

        new_energy.append(row)

    # übernehmen
    for gx in range(GW):
        for gy in range(GH):

            cells[gx][gy]["energy"] = new_energy[gx][gy]

# ------------------------------------------------------------
# Zeichnen
# ------------------------------------------------------------
def draw_cells(t):

    for gx in range(GW):
        for gy in range(GH):

            e = cells[gx][gy]["energy"]

            # ------------------------------------------------
            # Farben
            # ------------------------------------------------
            r = int(20 + e * 180)
            g = int(40 + e * 120)
            b = int(90 + e * 255)

            # zusätzliche Plasma-Pulse
            pulse = 0.5 + 0.5 * math.sin(
                t * 0.03 +
                gx * 0.2 +
                gy * 0.15
            )

            r += int(pulse * 20)
            b += int(pulse * 40)

            r = clamp(r, 0, 255)
            g = clamp(g, 0, 255)
            b = clamp(b, 0, 255)

            color = (r, g, b)

            # ------------------------------------------------
            # Größe
            # ------------------------------------------------
            size = int(2 + e * GRID * 1.1)

            px = gx * GRID + GRID // 2
            py = gy * GRID + GRID // 2

            # ------------------------------------------------
            # Glow
            # ------------------------------------------------
            glow = pygame.Surface((GRID * 3, GRID * 3), pygame.SRCALPHA)

            pygame.draw.circle(
                glow,
                (r, g, b, 40),
                (GRID + GRID // 2, GRID + GRID // 2),
                size + 4
            )

            screen.blit(
                glow,
                (px - GRID - GRID // 2, py - GRID - GRID // 2)
            )

            # ------------------------------------------------
            # Kern
            # ------------------------------------------------
            pygame.draw.circle(
                screen,
                color,
                (px, py),
                size
            )

# ------------------------------------------------------------
# Verbindungslinien
# ------------------------------------------------------------
def draw_connections():

    threshold = 0.72

    for gx in range(GW - 1):
        for gy in range(GH - 1):

            e = cells[gx][gy]["energy"]

            if e > threshold:

                px = gx * GRID + GRID // 2
                py = gy * GRID + GRID // 2

                # rechts
                er = cells[gx + 1][gy]["energy"]

                if er > threshold:

                    px2 = (gx + 1) * GRID + GRID // 2
                    py2 = py

                    pygame.draw.line(
                        screen,
                        (255, 210, 120),
                        (px, py),
                        (px2, py2),
                        1
                    )

                # unten
                eb = cells[gx][gy + 1]["energy"]

                if eb > threshold:

                    px2 = px
                    py2 = (gy + 1) * GRID + GRID // 2

                    pygame.draw.line(
                        screen,
                        (255, 210, 120),
                        (px, py),
                        (px2, py2),
                        1
                    )

# ------------------------------------------------------------
# Hintergrund
# ------------------------------------------------------------
def draw_background(t):

    screen.fill(BG)

    for i in range(6):

        x = int(W * (0.15 + i * 0.12) + math.sin(t * 0.01 + i) * 40)
        y = int(H * (0.2 + i * 0.1) + math.cos(t * 0.012 + i) * 35)

        radius = 120 + i * 25

        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        pygame.draw.circle(
            surf,
            (60, 40, 120, 18),
            (radius, radius),
            radius
        )

        screen.blit(surf, (x - radius, y - radius))

# ------------------------------------------------------------
# HUD
# ------------------------------------------------------------
font_big = pygame.font.SysFont(None, 34)
font_mid = pygame.font.SysFont(None, 22)
font_small = pygame.font.SysFont(None, 18)

def draw_text():

    title = font_big.render(
        "TIRXY FIELD CASCADE",
        True,
        (255, 220, 150)
    )

    screen.blit(title, (20, 18))

    sub = font_mid.render(
        "Emergente Zustandsfelder / Relaxation / Feldkopplung",
        True,
        TEXT
    )

    screen.blit(sub, (22, 50))

    mode = font_small.render(
        f"Modus: {MODES[MODE]}",
        True,
        (180, 220, 255)
    )

    screen.blit(mode, (24, 82))

    helptext = font_small.render(
        "SPACE = Modus | R = Reset | ESC = Ende",
        True,
        (180, 180, 210)
    )

    screen.blit(helptext, (24, 104))

    lore = [
        "Raum ist kein leerer Container.",
        "Raum ist ein dynamischer Zustand.",
        "Muster entstehen durch Kopplung.",
        "Materie ist stabile Resonanz."
    ]

    y = H - 110

    for line in lore:

        img = font_small.render(
            line,
            True,
            (255, 210, 140)
        )

        screen.blit(img, (22, y))

        y += 20

# ------------------------------------------------------------
# Hauptloop
# ------------------------------------------------------------
running = True
t = 0

while running:

    t += 1

    # --------------------------------------------------------
    # Events
    # --------------------------------------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE:

                MODE = (MODE + 1) % len(MODES)

            elif event.key == pygame.K_r:

                reset_cells()

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------
    update_cells(t)

    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------
    draw_background(t)

    draw_cells(t)

    if MODE in [2, 3]:
        draw_connections()

    draw_text()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()