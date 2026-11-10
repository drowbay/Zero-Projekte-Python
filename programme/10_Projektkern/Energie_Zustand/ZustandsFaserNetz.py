import pygame
import math
import random

# ============================================================
# Zero-Lumi Zustandsfaser-Netz
# PyDroid-Version
# ------------------------------------------------------------
# Idee:
# - tiefe Zustandsfaser / Adernetz
# - Energiefluss läuft durch Fasern
# - Universumsblasen sitzen in Knoten
# - Felder, Hilbert-Räume, Quanten und Materie entstehen
#   als sichtbare Zustandsprojektionen
#
# Steuerung:
# SPACE = Modus wechseln
# R     = Reset
# ESC   = Ende
# ============================================================

pygame.init()

# ------------------------------------------------------------
# Bildschirm
# ------------------------------------------------------------
W, H = 900, 620
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Zero-Lumi Zustandsfaser-Netz")

clock = pygame.time.Clock()

# ------------------------------------------------------------
# Farben
# ------------------------------------------------------------
BG = (3, 5, 18)
FIBER_DARK = (35, 55, 100)
FIBER_BLUE = (70, 170, 255)
FIBER_PURPLE = (170, 80, 255)
ENERGY = (255, 190, 90)
ENERGY_WHITE = (255, 245, 210)
TEXT = (230, 240, 255)
SUBTEXT = (160, 210, 255)

MODE = 0
MODES = [
    "Diffus: Energie verteilt sich weich",
    "Fokus: Energie sammelt sich in Universums-Knoten",
    "Wirbel: Zustandsfluss rotiert",
    "Helix: Rotation + Vorwärtsfluss",
]

# ------------------------------------------------------------
# Mathe-Helfer
# ------------------------------------------------------------
def lerp(a, b, t):
    return a * (1 - t) + b * t


def dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def draw_alpha_circle(target, color, pos, radius):
    if radius <= 0:
        return
    surf = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (radius + 2, radius + 2), radius)
    target.blit(surf, (pos[0] - radius - 2, pos[1] - radius - 2))


def draw_alpha_line(target, color, p1, p2, width=1):
    minx = min(p1[0], p2[0])
    miny = min(p1[1], p2[1])
    maxx = max(p1[0], p2[0])
    maxy = max(p1[1], p2[1])

    pad = width + 8
    surf_w = int(maxx - minx + pad * 2 + 2)
    surf_h = int(maxy - miny + pad * 2 + 2)

    surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)

    q1 = (p1[0] - minx + pad, p1[1] - miny + pad)
    q2 = (p2[0] - minx + pad, p2[1] - miny + pad)

    pygame.draw.line(surf, color, q1, q2, width)
    target.blit(surf, (minx - pad, miny - pad))


# ------------------------------------------------------------
# Netzwerk-Knoten
# ------------------------------------------------------------
class Node:
    def __init__(self, x, y, kind="normal"):
        self.x = x
        self.y = y
        self.kind = kind
        self.phase = random.random() * math.tau
        self.energy = random.uniform(0.4, 1.0)

    def pos(self):
        return (self.x, self.y)

    def update(self, t):
        # minimale lebendige Bewegung
        self.x += math.sin(t * 0.005 + self.phase) * 0.03
        self.y += math.cos(t * 0.004 + self.phase) * 0.03

        # Energie-Puls
        self.energy = 0.55 + 0.45 * math.sin(t * 0.025 + self.phase)

    def draw(self, target, t):
        if self.kind == "universe":
            r = 34 + int(4 * math.sin(t * 0.04 + self.phase))

            draw_alpha_circle(target, (80, 180, 255, 42), (int(self.x), int(self.y)), r + 18)
            draw_alpha_circle(target, (155, 80, 255, 32), (int(self.x), int(self.y)), r + 8)

            # Universumsblase
            pygame.draw.circle(target, (60, 120, 210), (int(self.x), int(self.y)), r, 1)
            pygame.draw.circle(target, (120, 210, 255), (int(self.x), int(self.y)), r - 7, 1)

            # Galaxie/Innenstruktur
            for i in range(18):
                a = i * 0.65 + t * 0.018 + self.phase
                rr = (i / 18) * (r - 8)
                px = self.x + math.cos(a) * rr
                py = self.y + math.sin(a) * rr * 0.55
                pygame.draw.circle(target, ENERGY_WHITE, (int(px), int(py)), 2)

            # Zentrum
            draw_alpha_circle(target, (255, 210, 120, 180), (int(self.x), int(self.y)), 5)

        else:
            pulse = 5 + int(4 * self.energy)
            draw_alpha_circle(target, (80, 180, 255, 70), (int(self.x), int(self.y)), pulse)
            pygame.draw.circle(target, (120, 220, 255), (int(self.x), int(self.y)), 2)


# ------------------------------------------------------------
# Faser / Ader
# ------------------------------------------------------------
class Fiber:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.phase = random.random() * math.tau
        self.thickness = random.choice([2, 2, 3, 4])

    def point_at(self, u, t):
        # Kurvige Verbindung zwischen Knoten
        ax, ay = self.a.pos()
        bx, by = self.b.pos()

        x = lerp(ax, bx, u)
        y = lerp(ay, by, u)

        # Normale für organische Ader-Krümmung
        dx = bx - ax
        dy = by - ay
        length = math.sqrt(dx * dx + dy * dy) + 1e-6

        nx = -dy / length
        ny = dx / length

        curve = math.sin(u * math.pi) * 32
        wave = math.sin(u * math.pi * 3 + t * 0.02 + self.phase) * 8

        x += nx * (curve + wave)
        y += ny * (curve * 0.4 + wave * 0.6)

        return (x, y)

    def draw(self, target, t):
        points = []
        steps = 22

        for i in range(steps + 1):
            u = i / steps
            points.append(self.point_at(u, t))

        # dunkler breiter Untergrund
        for i in range(1, len(points)):
            draw_alpha_line(
                target,
                (45, 75, 140, 90),
                points[i - 1],
                points[i],
                self.thickness + 4,
            )

        # leuchtende Faser
        for i in range(1, len(points)):
            mix = 0.5 + 0.5 * math.sin(t * 0.02 + i + self.phase)
            col = (
                int(lerp(FIBER_BLUE[0], FIBER_PURPLE[0], mix)),
                int(lerp(FIBER_BLUE[1], FIBER_PURPLE[1], mix)),
                int(lerp(FIBER_BLUE[2], FIBER_PURPLE[2], mix)),
                140,
            )

            draw_alpha_line(
                target,
                col,
                points[i - 1],
                points[i],
                self.thickness,
            )

    def draw_energy_packets(self, target, t, mode):
        # kleine Lichtpunkte, die auf der Faser wandern
        packet_count = 4

        for k in range(packet_count):
            base = (t * 0.006 + k / packet_count + self.phase * 0.05) % 1.0

            if mode == 1:
                # Fokus: mehr Richtung zum b-Knoten
                u = base ** 0.75
            elif mode == 2:
                # Wirbel: Puls pendelt
                u = 0.5 + 0.5 * math.sin(t * 0.035 + k + self.phase)
            elif mode == 3:
                # Helix: schneller und welliger
                u = (t * 0.010 + k / packet_count + self.phase * 0.1) % 1.0
            else:
                # Diffus
                u = base

            x, y = self.point_at(u, t)
            r = 3 + int(2 * math.sin(t * 0.06 + k))

            draw_alpha_circle(target, (255, 180, 80, 150), (int(x), int(y)), r + 5)
            pygame.draw.circle(target, ENERGY_WHITE, (int(x), int(y)), r)


# ------------------------------------------------------------
# Zeit-/Dynamik-Spur unten
# ------------------------------------------------------------
class TimePulse:
    def __init__(self, index):
        self.index = index
        self.phase = index * 0.8

    def draw(self, target, t):
        count = 7
        start_x = 115
        gap = 95
        y = H - 70

        x = start_x + self.index * gap
        pulse = 0.5 + 0.5 * math.sin(t * 0.04 + self.phase)
        r = 25 + int(5 * pulse)

        pygame.draw.circle(target, (95, 125, 180), (x, y), r, 1)
        draw_alpha_circle(target, (80, 170, 255, int(28 + 50 * pulse)), (x, y), r - 4)

        # Innenmuster
        for i in range(6):
            a = i * math.tau / 6 + t * 0.015 + self.phase
            px = x + math.cos(a) * (r - 9)
            py = y + math.sin(a) * (r - 9)
            pygame.draw.circle(target, (200, 235, 255), (int(px), int(py)), 2)

        font_small = pygame.font.SysFont(None, 17)
        labels = [
            "t0\nPotenzial",
            "t1\nFluktuation",
            "t2\nInterferenz",
            "t3\nMuster",
            "t4\nStruktur",
            "t5\nMaterie",
            "t6\nErleben",
        ]
        lines = labels[self.index].split("\n")
        img1 = font_small.render(lines[0], True, TEXT)
        img2 = font_small.render(lines[1], True, SUBTEXT)
        target.blit(img1, (x - img1.get_width() // 2, y + 36))
        target.blit(img2, (x - img2.get_width() // 2, y + 52))

        if self.index < count - 1:
            pygame.draw.line(target, (200, 150, 80), (x + 35, y), (x + gap - 35, y), 1)
            pygame.draw.polygon(
                target,
                (200, 150, 80),
                [
                    (x + gap - 37, y - 4),
                    (x + gap - 30, y),
                    (x + gap - 37, y + 4),
                ],
            )


# ------------------------------------------------------------
# Simulation bauen
# ------------------------------------------------------------
def create_network():
    nodes = []

    # Universums-Knoten
    universe_positions = [
        (210, 250),
        (420, 165),
        (610, 285),
        (690, 130),
        (335, 350),
    ]

    for p in universe_positions:
        nodes.append(Node(p[0], p[1], "universe"))

    # normale Knoten drumherum
    normal_positions = [
        (65, 150), (115, 345), (260, 95), (505, 70),
        (760, 215), (820, 370), (520, 410), (150, 445),
        (375, 250), (720, 445), (80, 260), (575, 185),
        (300, 455), (455, 310)
    ]

    for p in normal_positions:
        nodes.append(Node(p[0], p[1], "normal"))

    fibers = []

    # Verbindungen organisch aufbauen
    links = [
        (0, 5), (0, 10), (0, 8), (0, 13),
        (1, 2), (1, 8), (1, 11), (1, 3),
        (2, 11), (2, 6), (2, 13),
        (3, 11), (3, 9), (3, 4),
        (4, 9), (4, 14), (4, 6),
        (5, 7), (7, 10), (10, 13),
        (8, 13), (13, 6), (6, 14), (14, 9),
        (12, 7), (12, 13), (12, 6),
    ]

    for a, b in links:
        if a < len(nodes) and b < len(nodes):
            fibers.append(Fiber(nodes[a], nodes[b]))

    return nodes, fibers


nodes, fibers = create_network()
time_pulses = [TimePulse(i) for i in range(7)]

# ------------------------------------------------------------
# Text
# ------------------------------------------------------------
font_title = pygame.font.SysFont(None, 42)
font_mid = pygame.font.SysFont(None, 24)
font_small = pygame.font.SysFont(None, 19)


def draw_text(t):
    title = font_title.render("ZUSTANDSFASER-NETZ", True, (245, 225, 170))
    subtitle = font_mid.render("Universum in einer Ader — Energie wird durch Ordnung sichtbar", True, TEXT)

    screen.blit(title, (24, 22))
    screen.blit(subtitle, (28, 62))

    mode_text = font_small.render("Modus: " + MODES[MODE], True, SUBTEXT)
    help_text = font_small.render("SPACE = Modus   |   R = Reset   |   ESC = Ende", True, (210, 220, 235))

    screen.blit(mode_text, (28, 92))
    screen.blit(help_text, (28, 114))

    # rechte Legende
    box = pygame.Surface((260, 250), pygame.SRCALPHA)
    pygame.draw.rect(box, (8, 12, 28, 190), (0, 0, 260, 250), border_radius=14)
    pygame.draw.rect(box, (90, 150, 230, 120), (0, 0, 260, 250), 2, border_radius=14)

    legend_lines = [
        "1. Tiefe Zustandsstruktur",
        "2. Felder & Freiheitsgrade",
        "3. Hilbert-Raeume",
        "4. Quantenzustaende",
        "5. Sichtbare Materie",
        "",
        "Zeit = sichtbare Dynamik",
        "Energie = Menge",
        "Ordnung = Richtung",
        "Kopplung = Wirkung",
    ]

    y = 14
    for i, line in enumerate(legend_lines):
        col = (245, 225, 170) if i in [0, 6] else (190, 225, 255)
        img = font_small.render(line, True, col)
        box.blit(img, (14, y))
        y += 22

    screen.blit(box, (W - 286, 24))


def draw_background(t):
    screen.fill(BG)

    # Sternpunkte / Hintergrundnetz
    random.seed(2)
    for i in range(120):
        x = random.randint(0, W)
        y = random.randint(0, H)
        tw = 0.5 + 0.5 * math.sin(t * 0.02 + i)
        col = (80, 120, 190 + int(50 * tw))
        screen.set_at((x, y), col)

    # dezentes Gitternetz
    for x in range(0, W, 60):
        draw_alpha_line(screen, (40, 70, 120, 25), (x, 0), (x + 80, H), 1)

    for y in range(0, H, 60):
        draw_alpha_line(screen, (40, 70, 120, 22), (0, y), (W, y + 40), 1)


# ------------------------------------------------------------
# Hauptloop
# ------------------------------------------------------------
running = True
t = 0

while running:
    t += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_SPACE:
                MODE = (MODE + 1) % len(MODES)

            if event.key == pygame.K_r:
                nodes, fibers = create_network()

    # Update
    for n in nodes:
        n.update(t)

    # Draw
    draw_background(t)

    # Fasern zuerst
    for f in fibers:
        f.draw(screen, t)

    # Energiepakete
    for f in fibers:
        f.draw_energy_packets(screen, t, MODE)

    # Universumsblasen / Knoten
    for n in nodes:
        n.draw(screen, t)

    # Feldresonanz-Kreise um mittlere Knoten
    for n in nodes:
        if n.kind == "universe":
            pulse = 0.5 + 0.5 * math.sin(t * 0.03 + n.phase)
            r = int(58 + 22 * pulse)
            draw_alpha_circle(screen, (170, 80, 255, 30), (int(n.x), int(n.y)), r)
            pygame.draw.circle(screen, (120, 180, 255), (int(n.x), int(n.y)), r, 1)

    # Zeitspur unten
    pygame.draw.line(screen, (180, 135, 75), (60, H - 115), (W - 60, H - 115), 1)
    cap = font_mid.render("ZEIT WIRD DURCH DYNAMIK SICHTBAR", True, (245, 210, 130))
    screen.blit(cap, (W // 2 - cap.get_width() // 2, H - 142))

    for p in time_pulses:
        p.draw(screen, t)

    draw_text(t)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()