import pygame
import random
import math
import sys

# ============================================================
# TIRXY EMERGENCE GRID
# ------------------------------------------------------------
# Inspiriert von Zeros Skizze:
#
# - Raster / Spielideen / Emergenz
# - Knoten mit Zuständen
# - Pfeile / Flussrichtungen
# - Zustandszahlen 1,2,3...
# - Kreis-/Wellenimpuls links gedacht als Energiequelle
#
# Steuerung:
#   Linksklick  = Energie setzen
#   Rechtsklick = Knoten blockieren / Defekt setzen
#   Leertaste   = Pause
#   R           = Reset
#   W           = Wellenimpuls vom Zentrum
#   ESC         = Beenden
#
# Zustände:
#   0 = leer / ruhig
#   1 = stabil
#   2 = aktiv
#   3 = überladen
#  -1 = Defekt / Blockade
#
# ============================================================


# -----------------------------
# Pygame Setup
# -----------------------------
pygame.init()

WIDTH, HEIGHT = 1100, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tirxy Emergence Grid - Zero/Lumi Prototype")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 18)
BIG_FONT = pygame.font.SysFont("consolas", 32)


# -----------------------------
# Farben
# -----------------------------
BG = (10, 10, 18)
GRID_LINE = (45, 45, 60)

WHITE = (230, 230, 240)
DIM = (90, 90, 110)

STATE_COLORS = {
    -1: (95, 30, 55),       # Defekt
    0: (35, 35, 50),        # ruhig
    1: (80, 180, 255),      # stabil
    2: (255, 120, 220),     # aktiv
    3: (255, 220, 90),      # überladen
}

ENERGY_COLOR = (180, 90, 255)
ARROW_COLOR = (160, 160, 190)


# -----------------------------
# Raster
# -----------------------------
COLS = 18
ROWS = 12
CELL = 46

GRID_X = 230
GRID_Y = 90

CENTER_X = GRID_X + COLS * CELL // 2
CENTER_Y = GRID_Y + ROWS * CELL // 2


# -----------------------------
# Simulation
# -----------------------------
paused = False
frame = 0

states = [[0 for _ in range(COLS)] for _ in range(ROWS)]
energy = [[0.0 for _ in range(COLS)] for _ in range(ROWS)]

# zufällige Startknoten
for y in range(ROWS):
    for x in range(COLS):
        if random.random() < 0.12:
            states[y][x] = 1
            energy[y][x] = random.uniform(0.2, 0.7)


# -----------------------------
# Hilfsfunktionen
# -----------------------------
def clamp(v, a, b):
    return max(a, min(b, v))


def cell_center(x, y):
    return GRID_X + x * CELL + CELL // 2, GRID_Y + y * CELL + CELL // 2


def neighbors(x, y):
    result = []
    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx = x + dx
        ny = y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            result.append((nx, ny))
    return result


def set_energy_at_mouse(mx, my, amount=1.0):
    gx = (mx - GRID_X) // CELL
    gy = (my - GRID_Y) // CELL

    if 0 <= gx < COLS and 0 <= gy < ROWS:
        if states[gy][gx] != -1:
            energy[gy][gx] += amount
            states[gy][gx] = 2


def toggle_defect_at_mouse(mx, my):
    gx = (mx - GRID_X) // CELL
    gy = (my - GRID_Y) // CELL

    if 0 <= gx < COLS and 0 <= gy < ROWS:
        if states[gy][gx] == -1:
            states[gy][gx] = 0
            energy[gy][gx] = 0
        else:
            states[gy][gx] = -1
            energy[gy][gx] = 0


def reset():
    global states, energy, frame

    frame = 0
    states = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    energy = [[0.0 for _ in range(COLS)] for _ in range(ROWS)]

    for y in range(ROWS):
        for x in range(COLS):
            if random.random() < 0.10:
                states[y][x] = 1
                energy[y][x] = random.uniform(0.2, 0.6)


def wave_pulse():
    """Energieimpuls vom Mittelpunkt nach außen."""
    cx = COLS / 2
    cy = ROWS / 2

    for y in range(ROWS):
        for x in range(COLS):
            if states[y][x] == -1:
                continue

            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            pulse = max(0.0, 1.4 - d * 0.18)
            energy[y][x] += pulse

            if pulse > 0.45:
                states[y][x] = 2


# -----------------------------
# Emergenz-Regeln
# -----------------------------
def update_simulation():
    global states, energy

    new_energy = [[energy[y][x] for x in range(COLS)] for y in range(ROWS)]
    new_states = [[states[y][x] for x in range(COLS)] for y in range(ROWS)]

    for y in range(ROWS):
        for x in range(COLS):
            if states[y][x] == -1:
                continue

            e = energy[y][x]

            # Energie verliert langsam Kraft
            e *= 0.965

            # Energiefluss zu Nachbarn
            for nx, ny in neighbors(x, y):
                if states[ny][nx] == -1:
                    continue

                diff = energy[y][x] - energy[ny][nx]

                if diff > 0.12:
                    flow = diff * 0.055
                    new_energy[y][x] -= flow
                    new_energy[ny][nx] += flow

            # Nachbaranalyse
            active_neighbors = 0
            stable_neighbors = 0

            for nx, ny in neighbors(x, y):
                if states[ny][nx] == 2:
                    active_neighbors += 1
                if states[ny][nx] == 1:
                    stable_neighbors += 1

            # Regel 1:
            # Mehrere stabile Nachbarn erzeugen Ordnung
            if stable_neighbors >= 2 and e < 1.2:
                new_states[y][x] = 1
                e += 0.015

            # Regel 2:
            # Aktive Nachbarn erzeugen Welle / Aktivierung
            if active_neighbors >= 2:
                e += 0.05
                new_states[y][x] = 2

            # Regel 3:
            # Zu viel Energie = Überladung
            if e > 1.65:
                new_states[y][x] = 3

            # Regel 4:
            # Überladung entlädt sich und erzeugt Defektchance
            if states[y][x] == 3:
                e *= 0.72

                if random.random() < 0.006:
                    new_states[y][x] = -1
                    e = 0
                else:
                    new_states[y][x] = 2

            # Regel 5:
            # Ruhe bei wenig Energie
            if e < 0.08 and states[y][x] != -1:
                new_states[y][x] = 0

            # Regel 6:
            # mittlere Energie stabilisiert
            if 0.22 < e < 0.75 and states[y][x] != -1:
                if random.random() < 0.025:
                    new_states[y][x] = 1

            new_energy[y][x] = clamp(e, 0.0, 2.5)

    states = new_states
    energy = new_energy


# -----------------------------
# Zeichnen
# -----------------------------
def draw_text(text, x, y, color=WHITE, font=FONT):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_arrow(start, end, color=ARROW_COLOR):
    sx, sy = start
    ex, ey = end

    pygame.draw.line(screen, color, start, end, 2)

    angle = math.atan2(ey - sy, ex - sx)
    length = 10

    p1 = (
        ex - length * math.cos(angle - 0.45),
        ey - length * math.sin(angle - 0.45),
    )
    p2 = (
        ex - length * math.cos(angle + 0.45),
        ey - length * math.sin(angle + 0.45),
    )

    pygame.draw.polygon(screen, color, [end, p1, p2])


def draw_energy_source():
    """Linke runde Skizzen-Idee: Kreisquelle / radialer Generator."""
    cx, cy = 110, 330
    radius = 70

    # Außenwelle
    wave_r = radius + 10 + math.sin(frame * 0.08) * 8
    pygame.draw.circle(screen, (130, 60, 160), (cx, cy), int(wave_r), 2)

    # Kreis
    pygame.draw.circle(screen, (100, 160, 255), (cx, cy), radius, 2)
    pygame.draw.circle(screen, ENERGY_COLOR, (cx, cy), 6)

    # Speichen
    spokes = 18
    for i in range(spokes):
        a = (math.tau / spokes) * i + frame * 0.01
        x2 = cx + math.cos(a) * radius
        y2 = cy + math.sin(a) * radius
        pygame.draw.line(screen, (110, 130, 180), (cx, cy), (x2, y2), 1)

    # kleine Pfeile nach außen
    for i in range(12):
        a = (math.tau / 12) * i
        x1 = cx + math.cos(a) * (radius + 18)
        y1 = cy + math.sin(a) * (radius + 18)
        x2 = cx + math.cos(a) * (radius + 38)
        y2 = cy + math.sin(a) * (radius + 38)
        draw_arrow((x1, y1), (x2, y2), (160, 80, 190))

    draw_text("Energiequelle", 42, 225)
    draw_text("radialer Impuls", 35, 245, DIM)


def draw_grid():
    # Linien
    for y in range(ROWS + 1):
        yy = GRID_Y + y * CELL
        pygame.draw.line(screen, GRID_LINE, (GRID_X, yy), (GRID_X + COLS * CELL, yy), 1)

    for x in range(COLS + 1):
        xx = GRID_X + x * CELL
        pygame.draw.line(screen, GRID_LINE, (xx, GRID_Y), (xx, GRID_Y + ROWS * CELL), 1)

    # Verbindungen und Pfeile
    for y in range(ROWS):
        for x in range(COLS):
            if states[y][x] == -1:
                continue

            cx, cy = cell_center(x, y)

            # Pfeile nach rechts/unten, wenn Energiefluss sichtbar ist
            for nx, ny in neighbors(x, y):
                if nx < x or ny < y:
                    continue
                if states[ny][nx] == -1:
                    continue

                ncx, ncy = cell_center(nx, ny)
                avg_e = (energy[y][x] + energy[ny][nx]) / 2

                if avg_e > 0.18:
                    col = (
                        int(80 + avg_e * 60),
                        int(80 + avg_e * 45),
                        int(120 + avg_e * 60),
                    )
                    pygame.draw.line(screen, col, (cx, cy), (ncx, ncy), 2)

    # Knoten
    for y in range(ROWS):
        for x in range(COLS):
            cx, cy = cell_center(x, y)
            s = states[y][x]
            e = energy[y][x]

            color = STATE_COLORS.get(s, WHITE)

            # Radius wächst mit