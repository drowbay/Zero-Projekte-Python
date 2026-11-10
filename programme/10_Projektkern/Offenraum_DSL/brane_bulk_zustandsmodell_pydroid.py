import pygame
import math
import random

# ============================================================
# Zero-Lumi Brane-Bulk-Zustandsmodell
# PyDroid-Version
# ------------------------------------------------------------
# Idee:
# - Bulk = höherdimensionaler Hintergrund / Tiefenraum
# - Brane = Trägerfläche unserer sichtbaren Welt
# - Strings/Fasern = Grundlinien / Zustandsfasern
# - Felder = Wellen/Dynamik auf der Brane
# - Materie = stabile Kopplungsknoten
# - Gravitation = geometrische Kopplung, die in den Bulk hineinreichen kann
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
pygame.display.set_caption("Zero-Lumi Brane / Bulk / Zustandsmodell")

clock = pygame.time.Clock()

# ------------------------------------------------------------
# Farben
# ------------------------------------------------------------
BG = (3, 4, 15)
BULK_BLUE = (25, 55, 110)
BULK_PURPLE = (80, 35, 130)

BRANE_EDGE = (110, 210, 255)
BRANE_FILL = (20, 70, 120)
BRANE_GLOW = (70, 170, 255)

STRING = (255, 190, 90)
STRING_HOT = (255, 240, 180)

FIELD = (110, 220, 255)
MATTER = (255, 220, 130)
GRAVITY = (180, 110, 255)

TEXT = (235, 245, 255)
SUBTEXT = (170, 215, 255)

# ------------------------------------------------------------
# Modi
# ------------------------------------------------------------
MODE = 0
MODES = [
    "1 Brane: Felder und Materie bleiben auf der Trägerfläche",
    "Bulk-Kopplung: Gravitation reicht tiefer in den Bulk",
    "Zwei Branen: mögliche Nachbarwelt im höheren Raum",
    "Innen-Außen-Zyklus: Mikro und Makro koppeln über D5",
]

# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------
def lerp(a, b, t):
    return a * (1 - t) + b * t


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
    sw = int(maxx - minx + pad * 2 + 2)
    sh = int(maxy - miny + pad * 2 + 2)

    if sw <= 0 or sh <= 0:
        return

    surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
    q1 = (p1[0] - minx + pad, p1[1] - miny + pad)
    q2 = (p2[0] - minx + pad, p2[1] - miny + pad)
    pygame.draw.line(surf, color, q1, q2, width)
    target.blit(surf, (minx - pad, miny - pad))


def clamp(v, a, b):
    return max(a, min(b, v))


# ------------------------------------------------------------
# Brane-Geometrie
# ------------------------------------------------------------
def brane_y(x, t, offset=0):
    """
    Leicht gekrümmte Brane.
    Das ist keine echte M-Theorie-Simulation,
    sondern ein visuelles Modell.
    """
    base = H * 0.48 + offset
    wave1 = math.sin(x * 0.012 + t * 0.020) * 35
    wave2 = math.sin(x * 0.027 - t * 0.014) * 12
    return base + wave1 + wave2


def brane_normal(x, t, offset=0):
    """
    Näherung der Normalenrichtung an der Brane.
    """
    y1 = brane_y(x - 2, t, offset)
    y2 = brane_y(x + 2, t, offset)
    dy = y2 - y1
    dx = 4.0

    # Tangente = (dx, dy)
    # Normale = (-dy, dx)
    nx = -dy
    ny = dx
    mag = math.sqrt(nx * nx + ny * ny) + 1e-9
    return nx / mag, ny / mag


# ------------------------------------------------------------
# Teilchen / Materieknoten auf der Brane
# ------------------------------------------------------------
class MatterNode:
    def __init__(self, x):
        self.x = x
        self.phase = random.random() * math.tau
        self.energy = random.uniform(0.6, 1.0)
        self.radius = random.randint(5, 9)

    def update(self, t):
        self.x += math.sin(t * 0.01 + self.phase) * 0.25

        if self.x < 70:
            self.x = W - 70
        if self.x > W - 70:
            self.x = 70

        self.energy = 0.55 + 0.45 * math.sin(t * 0.04 + self.phase)

    def pos(self, t, offset=0):
        y = brane_y(self.x, t, offset)
        return self.x, y

    def draw(self, target, t, offset=0):
        x, y = self.pos(t, offset)

        pulse = 0.5 + 0.5 * math.sin(t * 0.05 + self.phase)
        glow_r = int(18 + 10 * pulse)

        draw_alpha_circle(
            target,
            (255, 210, 120, int(45 + 45 * pulse)),
            (int(x), int(y)),
            glow_r
        )

        pygame.draw.circle(
            target,
            MATTER,
            (int(x), int(y)),
            self.radius
        )

        pygame.draw.circle(
            target,
            STRING_HOT,
            (int(x), int(y)),
            max(2, self.radius // 2)
        )


# ------------------------------------------------------------
# Strings / Zustandsfasern auf der Brane
# ------------------------------------------------------------
class StringFiber:
    def __init__(self, x1, x2, offset=0):
        self.x1 = x1
        self.x2 = x2
        self.offset = offset
        self.phase = random.random() * math.tau

    def point_at(self, u, t):
        x = lerp(self.x1, self.x2, u)
        y = brane_y(x, t, self.offset)

        # kleine Schwingung senkrecht zur Brane
        nx, ny = brane_normal(x, t, self.offset)
        amp = math.sin(u * math.pi * 2 + t * 0.04 + self.phase) * 9
        return x + nx * amp, y + ny * amp

    def draw(self, target, t):
        pts = []
        steps = 25

        for i in range(steps + 1):
            u = i / steps
            pts.append(self.point_at(u, t))

        # dunkle Grundlinie
        for i in range(1, len(pts)):
            draw_alpha_line(
                target,
                (140, 80, 255, 70),
                pts[i - 1],
                pts[i],
                4
            )

        # helle String-Faser
        for i in range(1, len(pts)):
            phase_mix = 0.5 + 0.5 * math.sin(t * 0.035 + i + self.phase)
            col = (
                int(lerp(255, 120, phase_mix)),
                int(lerp(195, 220, phase_mix)),
                int(lerp(95, 255, phase_mix)),
                150
            )
            draw_alpha_line(
                target,
                col,
                pts[i - 1],
                pts[i],
                2
            )

    def draw_packets(self, target, t):
        for k in range(3):
            u = (t * 0.006 + k / 3 + self.phase * 0.08) % 1.0
            x, y = self.point_at(u, t)

            draw_alpha_circle(
                target,
                (255, 180, 80, 110),
                (int(x), int(y)),
                8
            )
            pygame.draw.circle(
                target,
                STRING_HOT,
                (int(x), int(y)),
                3
            )


# ------------------------------------------------------------
# Bulk-Partikel / Hintergrundzustände
# ------------------------------------------------------------
class BulkParticle:
    def __init__(self):
        self.x = random.uniform(0, W)
        self.y = random.uniform(0, H)
        self.phase = random.random() * math.tau
        self.speed = random.uniform(0.15, 0.55)
        self.size = random.choice([1, 1, 2])

    def update(self, t):
        self.x += math.sin(t * 0.006 + self.phase) * self.speed
        self.y += math.cos(t * 0.005 + self.phase * 1.3) * self.speed

        if self.x < 0:
            self.x = W
        if self.x > W:
            self.x = 0
        if self.y < 0:
            self.y = H
        if self.y > H:
            self.y = 0

    def draw(self, target, t):
        pulse = 0.4 + 0.6 * math.sin(t * 0.03 + self.phase)
        col = (
            int(50 + 60 * pulse),
            int(80 + 60 * pulse),
            int(150 + 90 * pulse),
        )
        pygame.draw.circle(target, col, (int(self.x), int(self.y)), self.size)


# ------------------------------------------------------------
# Simulation erstellen
# ------------------------------------------------------------
matter_nodes = []
strings = []
bulk_particles = []


def reset_sim():
    global matter_nodes, strings, bulk_particles

    matter_nodes = [
        MatterNode(random.uniform(110, W - 110))
        for _ in range(13)
    ]

    strings = []

    # Strings/Fasern auf Hauptbrane
    for _ in range(16):
        x1 = random.uniform(50, W * 0.55)
        x2 = random.uniform(W * 0.45, W - 50)
        if x1 > x2:
            x1, x2 = x2, x1
        strings.append(StringFiber(x1, x2, offset=0))

    # Zweite Brane, wenn Modus 2/3 sichtbar wird
    if MODE in [2, 3]:
        for _ in range(9):
            x1 = random.uniform(60, W * 0.55)
            x2 = random.uniform(W * 0.45, W - 60)
            if x1 > x2:
                x1, x2 = x2, x1
            strings.append(StringFiber(x1, x2, offset=-155))

    bulk_particles = [BulkParticle() for _ in range(120)]


reset_sim()

# ------------------------------------------------------------
# Hintergrund / Bulk
# ------------------------------------------------------------
def draw_bulk(t):
    screen.fill(BG)

    # weicher Bulk-Glow
    for i in range(4):
        cx = int(W * (0.2 + 0.2 * i) + math.sin(t * 0.01 + i) * 20)
        cy = int(H * (0.28 + 0.13 * i) + math.cos(t * 0.012 + i) * 25)
        r = 180 + i * 35
        col = (
            40 + i * 12,
            35 + i * 10,
            95 + i * 25,
            18
        )
        draw_alpha_circle(screen, col, (cx, cy), r)

    # Hintergrundteilchen
    for p in bulk_particles:
        p.update(t)
        p.draw(screen, t)

    # höherdimensionales Netz
    for x in range(-100, W + 120, 70):
        draw_alpha_line(
            screen,
            (45, 80, 150, 30),
            (x, 0),
            (x + 180, H),
            1
        )

    for y in range(0, H, 70):
        draw_alpha_line(
            screen,
            (60, 40, 130, 25),
            (0, y),
            (W, y + 90),
            1
        )


# ------------------------------------------------------------
# Brane zeichnen
# ------------------------------------------------------------
def draw_brane(t, offset=0, label="3-Brane / sichtbare Welt"):
    pts = []
    for x in range(35, W - 35, 10):
        y = brane_y(x, t, offset)
        pts.append((x, y))

    # Glow unter/über der Brane
    for i in range(1, len(pts)):
        draw_alpha_line(
            screen,
            (70, 170, 255, 55),
            pts[i - 1],
            pts[i],
            8
        )

    for i in range(1, len(pts)):
        draw_alpha_line(
            screen,
            (120, 225, 255, 170),
            pts[i - 1],
            pts[i],
            2
        )

    # leicht transparente Fläche darunter
    poly = pts + [(W - 35, H + 50), (35, H + 50)]
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (20, 80, 130, 35), poly)
    screen.blit(surf, (0, 0))

    # Label
    font_small = pygame.font.SysFont(None, 18)
    img = font_small.render(label, True, SUBTEXT)
    screen.blit(img, (45, int(brane_y(55, t, offset)) - 28))


# ------------------------------------------------------------
# Felder auf der Brane
# ------------------------------------------------------------
def draw_field_waves(t, offset=0):
    """
    Feldwellen auf der Brane.
    Normale EM/Felder bleiben im Modell auf der Brane.
    """
    for wave_id in range(4):
        pts = []
        phase = wave_id * 1.6

        for x in range(50, W - 50, 12):
            y = brane_y(x, t, offset)

            nx, ny = brane_normal(x, t, offset)
            amp = math.sin(x * 0.025 + t * 0.05 + phase) * (14 + 3 * wave_id)

            pts.append((x + nx * amp, y + ny * amp))

        for i in range(1, len(pts)):
            alpha = 55 + wave_id * 18
            draw_alpha_line(
                screen,
                (90, 220, 255, alpha),
                pts[i - 1],
                pts[i],
                1
            )


# ------------------------------------------------------------
# Gravitation / Bulk-Kopplung zeichnen
# ------------------------------------------------------------
def draw_gravity_bulk_coupling(t):
    """
    Gravitation wird als Kopplung gezeigt,
    die nicht nur auf der Brane bleibt,
    sondern in den Bulk hineinreichen kann.
    """
    if MODE not in [1, 2, 3]:
        return

    for node in matter_nodes:
        x, y = node.pos(t, offset=0)

        # Linien in den Bulk
        for k in range(4):
            angle = -math.pi / 2 + (k - 1.5) * 0.45
            length = 70 + 25 * math.sin(t * 0.03 + node.phase + k)
            x2 = x + math.cos(angle) * length
            y2 = y + math.sin(angle) * length

            draw_alpha_line(
                screen,
                (180, 110, 255, 65),
                (x, y),
                (x2, y2),
                1
            )

        draw_alpha_circle(
            screen,
            (160, 80, 255, 30),
            (int(x), int(y - 35)),
            42
        )


# ------------------------------------------------------------
# Innen-Außen-Zyklus anzeigen
# ------------------------------------------------------------
def draw_micro_macro_cycle(t):
    if MODE != 3:
        return

    cx, cy = W - 155, H - 175
    r = 58

    # Kreis
    pygame.draw.circle(screen, (120, 190, 255), (cx, cy), r, 1)

    # rotierender Punkt
    a = t * 0.035
    px = cx + math.cos(a) * r
    py = cy + math.sin(a) * r
    draw_alpha_circle(screen, (255, 190, 90, 130), (int(px), int(py)), 9)
    pygame.draw.circle(screen, STRING_HOT, (int(px), int(py)), 3)

    font = pygame.font.SysFont(None, 18)
    lines = [
        "Innen-Aussen-Zyklus",
        "Mikro -> Makro",
        "Grenze -> Tiefe"
    ]

    y = cy + 72
    for line in lines:
        img = font.render(line, True, (230, 240, 255))
        screen.blit(img, (cx - img.get_width() // 2, y))
        y += 18

    # Verbindungspfeile
    pygame.draw.arc(screen, (255, 190, 90), (cx - r, cy - r, r * 2, r * 2), 0.2, 5.6, 1)


# ------------------------------------------------------------
# Textboxen
# ------------------------------------------------------------
font_title = pygame.font.SysFont(None, 36)
font_mid = pygame.font.SysFont(None, 22)
font_small = pygame.font.SysFont(None, 18)


def draw_text(t):
    title = font_title.render("BRANE / BULK / ZUSTANDSFASER-MODELL", True, (255, 225, 165))
    screen.blit(title, (22, 18))

    sub = font_mid.render("Brane = Trägerplatte | Bulk = höherer Hintergrund | Felder = Dynamik darauf", True, TEXT)
    screen.blit(sub, (24, 52))

    mode_img = font_small.render("Modus: " + MODES[MODE], True, SUBTEXT)
    help_img = font_small.render("SPACE = Modus   |   R = Reset   |   ESC = Ende", True, (210, 220, 235))

    screen.blit(mode_img, (24, 82))
    screen.blit(help_img, (24, 104))

    # Legende rechts
    box = pygame.Surface((315, 230), pygame.SRCALPHA)
    pygame.draw.rect(box, (7, 12, 30, 195), (0, 0, 315, 230), border_radius=14)
    pygame.draw.rect(box, (90, 150, 230, 130), (0, 0, 315, 230), 2, border_radius=14)

    lines = [
        "Modell-Lesart:",
        "String = Faser / Linie",
        "Brane = Traegerflaeche",
        "Bulk = hoeherer Hintergrund",
        "Feld = Welle auf der Brane",
        "Materie = stabiler Knoten",
        "Gravitation = Geometrie-Kopplung",
        "",
        "Zeit = sichtbare Dynamik",
        "Aussen beginnt im tiefsten Innen"
    ]

    y = 12
    for i, line in enumerate(lines):
        col = (255, 225, 165) if i in [0, 8, 9] else (190, 225, 255)
        img = font_small.render(line, True, col)
        box.blit(img, (12, y))
        y += 20

    screen.blit(box, (W - 340, 22))


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

            elif event.key == pygame.K_SPACE:
                MODE = (MODE + 1) % len(MODES)
                reset_sim()

            elif event.key == pygame.K_r:
                reset_sim()

    # Update
    for m in matter_nodes:
        m.update(t)

    # Draw
    draw_bulk(t)

    # zweite Brane zuerst hinten
    if MODE in [2, 3]:
        draw_brane(t, offset=-155, label="Nachbar-Brane / andere Trägerschicht")
        draw_field_waves(t, offset=-155)

    # Hauptbrane
    draw_brane(t, offset=0, label="3-Brane / sichtbare Welt")
    draw_field_waves(t, offset=0)

    # Strings/Fasern
    for s in strings:
        s.draw(screen, t)

    for s in strings:
        s.draw_packets(screen, t)

    # Materieknoten
    for m in matter_nodes:
        m.draw(screen, t, offset=0)

    # Gravitation in Bulk
    draw_gravity_bulk_coupling(t)

    # Innen-Außen-Zyklus
    draw_micro_macro_cycle(t)

    # Unterer Merksatz
    pygame.draw.line(screen, (180, 135, 75), (55, H - 52), (W - 55, H - 52), 1)
    cap = font_mid.render("Strings sind Fasern. Branen sind Traegerplatten. Felder sind Bewegungen darauf.", True, (245, 220, 150))
    screen.blit(cap, (W // 2 - cap.get_width() // 2, H - 40))

    draw_text(t)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()