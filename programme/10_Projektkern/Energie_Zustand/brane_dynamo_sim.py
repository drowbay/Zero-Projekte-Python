import pygame
import math
import sys
import random

# ============================================================
# Zero + Lumora: 4D-Brane / Edge-Wedge / Dynamo Simulation
# Pydroid/Pygame Version
#
# Steuerung:
#   SPACE  = Pause
#   R      = Reset Zeit
#   ESC    = Beenden
#
# Idee:
#   - Links: 4D-Brane als kubische Projektion / Tesserakt-Ansicht
#   - Mitte: Querschnitt durch Brane + Felddichte
#   - Rechts: Dynamo: Rotation -> Flussänderung -> induzierter Strom
#
# Wichtig:
#   Das ist ein Denkmodell / Visualisierung, keine bestätigte Brane-Physik.
# ============================================================

pygame.init()

# Für Phone/Pydroid lieber nicht zu riesig
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4D-Brane Edge-Wedge Dynamo Simulation")

clock = pygame.time.Clock()

# Farben
BLACK = (2, 4, 8)
WHITE = (230, 240, 255)
CYAN = (0, 220, 255)
BLUE = (40, 120, 255)
GREEN = (80, 255, 120)
YELLOW = (255, 220, 70)
ORANGE = (255, 130, 30)
RED = (255, 70, 70)
MAGENTA = (255, 80, 220)
GRAY = (90, 110, 130)

font = pygame.font.SysFont("arial", 20)
small = pygame.font.SysFont("arial", 15)
tiny = pygame.font.SysFont("arial", 12)
big = pygame.font.SysFont("arial", 26, bold=True)


def clamp(x, a, b):
    return max(a, min(b, x))


def draw_text(txt, x, y, color=WHITE, fnt=font):
    img = fnt.render(txt, True, color)
    screen.blit(img, (x, y))


def glow_circle(surface, pos, radius, color, layers=4):
    x, y = int(pos[0]), int(pos[1])
    for i in range(layers, 0, -1):
        alpha_radius = radius + i * 4
        c = tuple(min(255, int(v * (0.22 + 0.13 * i))) for v in color)
        pygame.draw.circle(surface, c, (x, y), alpha_radius, 1)
    pygame.draw.circle(surface, color, (x, y), radius)


def draw_glow_line(surface, a, b, color, width=1):
    pygame.draw.line(surface, tuple(int(v * 0.35) for v in color), a, b, width + 4)
    pygame.draw.line(surface, tuple(int(v * 0.65) for v in color), a, b, width + 2)
    pygame.draw.line(surface, color, a, b, width)


def project4d(p, cx, cy, scale, t):
    """
    4D Punkt p=(x,y,z,w) wird auf 2D projiziert.
    Wir machen eine einfache Rotation in x-w und y-z.
    """
    x, y, z, w = p

    # 4D-Rotation x/w
    a = 0.55 * math.sin(t * 0.35)
    x2 = x * math.cos(a) - w * math.sin(a)
    w2 = x * math.sin(a) + w * math.cos(a)

    # 3D-Rotation y/z
    b = 0.45 + 0.25 * math.sin(t * 0.23)
    y2 = y * math.cos(b) - z * math.sin(b)
    z2 = y * math.sin(b) + z * math.cos(b)

    # Perspektive: w/z verändert Tiefe
    depth = 3.7 + z2 + 0.55 * w2
    factor = scale / depth

    sx = cx + x2 * factor
    sy = cy + y2 * factor

    return (sx, sy), depth


def make_tesseract_points():
    pts = []
    for x in [-1, 1]:
        for y in [-1, 1]:
            for z in [-1, 1]:
                for w in [-1, 1]:
                    pts.append((x, y, z, w))
    return pts


def tesseract_edges(points):
    edges = []
    for i, a in enumerate(points):
        for j, b in enumerate(points):
            if j <= i:
                continue
            diff = sum(1 for k in range(4) if a[k] != b[k])
            if diff == 1:
                edges.append((i, j))
    return edges


POINTS4D = make_tesseract_points()
EDGES4D = tesseract_edges(POINTS4D)


def draw_edge_wedge(a, b, center, phase, strength=1.0):
    """
    Keilförmige Übergangszone an einer Kante.
    Kein echtes Volumen, sondern 2D-Visualisierung:
    Linie wird zur kleinen leuchtenden Dreiecks-/Keilfläche.
    """
    ax, ay = a
    bx, by = b
    cx, cy = center

    mx = (ax + bx) * 0.5
    my = (ay + by) * 0.5

    # Richtung senkrecht zur Kante
    dx = bx - ax
    dy = by - ay
    length = math.hypot(dx, dy) + 0.001
    nx = -dy / length
    ny = dx / length

    pulse = 0.5 + 0.5 * math.sin(phase)
    wedge_size = 12 + 22 * pulse * strength

    p1 = (mx + nx * wedge_size, my + ny * wedge_size)
    p2 = (mx - nx * wedge_size * 0.45, my - ny * wedge_size * 0.45)
    p3 = (cx, cy)

    # transparente Fläche über extra Surface
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    col = (255, 180, 40, int(45 + 95 * pulse))
    pygame.draw.polygon(surf, col, [p1, p2, p3])
    pygame.draw.line(surf, (255, 230, 90, 160), p1, p2, 1)
    screen.blit(surf, (0, 0))


def draw_brane_panel(t, paused):
    px, py, pw, ph = 20, 60, 390, 590
    pygame.draw.rect(screen, (0, 60, 70), (px, py, pw, ph), 1, border_radius=10)
    draw_text("4D-Brane / Hyperwürfel", px + 80, py - 38, CYAN, big)

    cx, cy = px + pw * 0.52, py + ph * 0.47
    scale = 410

    projected = []
    depths = []
    for p in POINTS4D:
        pos, d = project4d(p, cx, cy, scale, t)
        projected.append(pos)
        depths.append(d)

    # Stern-Partikel im Bulk
    random.seed(4)
    for _ in range(140):
        sx = px + random.random() * pw
        sy = py + random.random() * ph
        c = (0, 80 + random.randint(0, 90), 120 + random.randint(0, 100))
        screen.set_at((int(sx), int(sy)), c)

    # Kanten
    for i, j in EDGES4D:
        a = projected[i]
        b = projected[j]
        depth_avg = (depths[i] + depths[j]) * 0.5

        if abs(POINTS4D[i][3] - POINTS4D[j][3]) > 0:
            color = YELLOW
            width = 2
        else:
            color = CYAN
            width = 1

        if depth_avg < 3.4:
            color = ORANGE

        draw_glow_line(screen, a, b, color, width)

    # Edge-Wedges an ausgewählten Kanten
    selected = [0, 5, 11, 18, 24, 29]
    for n, edge_index in enumerate(selected):
        if edge_index < len(EDGES4D):
            i, j = EDGES4D[edge_index]
            draw_edge_wedge(
                projected[i],
                projected[j],
                (cx, cy),
                t * 2.0 + n,
                strength=0.75 + 0.25 * math.sin(t + n)
            )

    # Knoten
    for idx, pos in enumerate(projected):
        w = POINTS4D[idx][3]
        col = YELLOW if w > 0 else CYAN
        r = 5 if w > 0 else 4
        glow_circle(screen, pos, r, col, 3)

    # Zentrum
    glow_circle(screen, (cx, cy), 7, WHITE, 5)

    # Achsen
    draw_glow_line(screen, (cx, cy), (cx + 135, cy), RED, 2)
    draw_glow_line(screen, (cx, cy), (cx, cy - 135), GREEN, 2)
    draw_glow_line(screen, (cx, cy), (cx - 100, cy + 90), BLUE, 2)
    draw_glow_line(screen, (cx, cy), (cx + 105, cy + 100), YELLOW, 2)

    draw_text("x", cx + 145, cy - 10, RED, font)
    draw_text("y", cx + 10, cy - 150, GREEN, font)
    draw_text("z", cx - 120, cy + 95, BLUE, font)
    draw_text("w", cx + 112, cy + 105, YELLOW, font)

    draw_text("Edge-Wedge", px + 25, py + ph - 80, YELLOW, font)
    draw_text("Bulk", px + pw - 75, py + ph - 70, BLUE, font)

    # Legende
    lx, ly = px + 20, py + ph - 35
    glow_circle(screen, (lx, ly), 4, CYAN, 2)
    draw_text("Knoten", lx + 15, ly - 9, WHITE, tiny)
    draw_glow_line(screen, (lx + 85, ly), (lx + 125, ly), CYAN, 1)
    draw_text("Kante", lx + 132, ly - 9, WHITE, tiny)
    draw_glow_line(screen, (lx + 200, ly), (lx + 245, ly), YELLOW, 2)
    draw_text("Wedge", lx + 252, ly - 9, WHITE, tiny)


def draw_cross_section(t):
    px, py, pw, ph = 435, 60, 390, 590
    pygame.draw.rect(screen, (0, 60, 70), (px, py, pw, ph), 1, border_radius=10)
    draw_text("Querschnitt / Schnitt", px + 85, py - 38, CYAN, big)

    cx, cy = px + pw * 0.5, py + ph * 0.38

    # Schnittlinie
    pygame.draw.line(screen, GRAY, (cx, py + 20), (cx, py + ph - 160), 1)
    draw_text("✂", cx - 10, py + 3, WHITE, font)

    # Brane-Netz im Schnitt
    rings = 9
    segments = 34

    for r in range(1, rings + 1):
        rr = r / rings
        pts = []
        for s in range(segments):
            ang = 2 * math.pi * s / segments

            wave = math.sin(ang * 4 + t * 2.0) * 0.18
            pulse = math.sin(t * 1.6) * 0.20
            deform = 1 + wave + pulse * math.cos(ang)

            x = math.cos(ang) * rr * 155 * deform
            y = math.sin(ang) * rr * 125 * (1 - 0.12 * math.sin(t)) * deform

            # leichte 4D-Projektions-Krümmung
            y += 28 * math.sin(t + rr * 2.5) * (1 - rr)

            pts.append((cx + x, cy + y))

        for i in range(len(pts)):
            a = pts[i]
            b = pts[(i + 1) % len(pts)]
            color = GREEN if r < rings * 0.6 else YELLOW
            draw_glow_line(screen, a, b, color, 1)

    # Radiallinien
    for s in range(0, segments, 3):
        ang = 2 * math.pi * s / segments
        x = math.cos(ang) * 160
        y = math.sin(ang) * 130
        draw_glow_line(screen, (cx, cy), (cx + x, cy + y), (80, 170, 120), 1)

    # Zentraler Dichtepunkt
    density = 0.5 + 0.5 * math.sin(t * 2.0)
    glow_circle(screen, (cx, cy), 7 + int(5 * density), ORANGE, 5)

    # Edge-Wedge-Keile im Schnitt
    for ang in [0.6, 2.4, 3.8, 5.4]:
        mx = cx + math.cos(ang) * 150
        my = cy + math.sin(ang) * 120
        p1 = (mx, my)
        p2 = (mx + math.cos(ang + 0.4) * 35, my + math.sin(ang + 0.4) * 35)
        p3 = (cx + math.cos(ang) * 55, cy + math.sin(ang) * 45)
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = int(50 + 80 * (0.5 + 0.5 * math.sin(t * 2 + ang)))
        pygame.draw.polygon(surf, (255, 180, 30, alpha), [p1, p2, p3])
        screen.blit(surf, (0, 0))

    draw_text("Edge-Wedge", px + pw - 120, py + 115, YELLOW, small)
    draw_text("Bulk", px + pw - 80, py + 235, BLUE, font)
    draw_text("Felddichte", px + 25, py + 235, ORANGE, small)

    # Projektion unten
    base_cx, base_cy = cx, py + ph - 120
    for rr in range(20, 155, 18):
        col = (70, 150 + rr // 3, 30)
        pygame.draw.ellipse(screen, col, (base_cx - rr, base_cy - rr * 0.28, rr * 2, rr * 0.56), 1)
    for a in range(0, 360, 20):
        rad = math.radians(a)
        draw_glow_line(
            screen,
            (base_cx, base_cy),
            (base_cx + math.cos(rad) * 150, base_cy + math.sin(rad) * 42),
            (60, 120, 40),
            1
        )

    glow_circle(screen, (base_cx, base_cy), 5, RED, 4)
    draw_text("Projektion", base_cx - 40, base_cy + 55, WHITE, small)


def draw_dynamo(t):
    px, py, pw, ph = 850, 60, 410, 590
    pygame.draw.rect(screen, (0, 60, 70), (px, py, pw, ph), 1, border_radius=10)
    draw_text("Magnetische Dynamo-Übersetzung", px + 35, py - 38, CYAN, big)

    cx, cy = px + pw * 0.52, py + 185

    # Magnetblöcke
    pygame.draw.rect(screen, (10, 60, 120), (px + 35, py + 90, 90, 120), 2)
    pygame.draw.rect(screen, (120, 20, 20), (px + pw - 125, py + 90, 90, 120), 2)
    draw_text("N", px + 70, py + 135, BLUE, big)
    draw_text("S", px + pw - 90, py + 135, RED, big)

    # Magnetfeldlinien
    for k in range(-4, 5):
        yy = cy + k * 22
        start = (px + 125, yy)
        end = (px + pw - 125, yy)
        mid_y = yy + math.sin(t * 1.2 + k) * 12
        pygame.draw.arc(
            screen,
            CYAN,
            (px + 110, mid_y - 80, pw - 220, 160),
            math.radians(180),
            math.radians(360),
            1
        )
        draw_glow_line(screen, start, end, (0, 90, 120), 1)

    # Dynamo-Rotation
    angle = t * 1.6
    coil_w = 95 * abs(math.cos(angle)) + 18
    coil_h = 145
    tilt = math.sin(angle) * 45

    # Achse
    draw_glow_line(screen, (cx, cy - 115), (cx, cy + 130), WHITE, 2)
    pygame.draw.circle(screen, ORANGE, (int(cx), int(cy + 100)), 38, 2)

    # Spule als rotierende Rechteckform
    p_top_l = (cx - coil_w / 2 + tilt * 0.25, cy - coil_h / 2)
    p_top_r = (cx + coil_w / 2 + tilt * 0.25, cy - coil_h / 2)
    p_bot_r = (cx + coil_w / 2 - tilt * 0.25, cy + coil_h / 2)
    p_bot_l = (cx - coil_w / 2 - tilt * 0.25, cy + coil_h / 2)

    coil_pts = [p_top_l, p_top_r, p_bot_r, p_bot_l]
    for i in range(4):
        draw_glow_line(screen, coil_pts[i], coil_pts[(i + 1) % 4], ORANGE, 3)

    # Rotationspfeil
    pygame.draw.arc(screen, YELLOW, (cx - 35, cy - 150, 70, 36), 0, math.pi * 1.7, 3)
    draw_text("ω", cx - 8, cy - 178, WHITE, font)

    # Stromrichtung
    current = math.sin(angle)
    current_color = YELLOW if current >= 0 else RED
    draw_text("I", cx + 85, cy - 10, current_color, big)
    arrow_dir = 1 if current >= 0 else -1
    draw_glow_line(screen, (cx + 75, cy - 35 * arrow_dir), (cx + 75, cy + 35 * arrow_dir), current_color, 2)

    # Schaltkreis + Lampe
    bulb_x, bulb_y = px + pw - 65, py + 375
    draw_glow_line(screen, (cx, cy + 138), (cx, bulb_y), YELLOW, 2)
    draw_glow_line(screen, (cx, bulb_y), (bulb_x - 25, bulb_y), YELLOW, 2)
    pygame.draw.circle(screen, YELLOW, (int(bulb_x), int(bulb_y)), 18, 2)
    glow_circle(screen, (bulb_x, bulb_y), 10, YELLOW, 4)
    draw_text("Induktion", cx - 45, cy + 155, YELLOW, font)

    # Graph
    gx, gy, gw, gh = px + 40, py + 430, 320, 100
    pygame.draw.rect(screen, (0, 90, 100), (gx, gy, gw, gh), 1, border_radius=6)
    draw_text("Induzierter Strom I(t)", gx + 70, gy - 28, YELLOW, small)

    # Achsen
    pygame.draw.line(screen, WHITE, (gx + 25, gy + gh // 2), (gx + gw - 15, gy + gh // 2), 1)
    pygame.draw.line(screen, WHITE, (gx + 25, gy + 15), (gx + 25, gy + gh - 15), 1)

    # Kurve
    pts = []
    for i in range(gw - 50):
        x = gx + 30 + i
        tt = (i / 50.0) - t * 1.6
        y = gy + gh // 2 - math.sin(tt) * 34
        pts.append((x, y))
    if len(pts) > 2:
        pygame.draw.lines(screen, YELLOW, False, pts, 2)

    # Status
    dphi = math.cos(angle)
    if abs(dphi) < 0.15:
        status = "dΦ/dt ≈ 0  →  I ≈ 0"
        scol = CYAN
    elif dphi > 0:
        status = "dΦ/dt > 0  →  I > 0"
        scol = YELLOW
    else:
        status = "dΦ/dt < 0  →  I < 0"
        scol = RED

    pygame.draw.rect(screen, (0, 50, 60), (gx, gy + gh + 18, gw, 38), 1, border_radius=6)
    draw_text(status, gx + 20, gy + gh + 25, scol, small)


def draw_background(t):
    screen.fill(BLACK)

    # subtile Sternpunkte
    random.seed(1)
    for _ in range(220):
        x = random.randrange(0, WIDTH)
        y = random.randrange(0, HEIGHT)
        flick = 80 + int(60 * math.sin(t + x * 0.01))
        screen.set_at((x, y), (0, flick // 2, flick))


def draw_footer(t, paused):
    pygame.draw.rect(screen, (0, 40, 50), (20, HEIGHT - 45, WIDTH - 40, 28), 1, border_radius=8)

    draw_text("SPACE Pause | R Reset | ESC Ende", 35, HEIGHT - 40, WHITE, tiny)

    mode = "PAUSE" if paused else "LIVE"
    col = ORANGE if paused else GREEN
    draw_text(mode, WIDTH - 120, HEIGHT - 40, col, small)

    draw_text("Denkmodell: Edge-Wedge Ω(t) → magnetischer Fluss Φ(t) → Induktion U_ind", 350, HEIGHT - 40, CYAN, tiny)


def main():
    t = 0.0
    paused = False

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:
                    paused = not paused

                if event.key == pygame.K_r:
                    t = 0.0

        if not paused:
            t += dt

        draw_background(t)

        draw_brane_panel(t, paused)
        draw_cross_section(t)
        draw_dynamo(t)

        draw_footer(t, paused)

        pygame.display.flip()


if __name__ == "__main__":
    main()