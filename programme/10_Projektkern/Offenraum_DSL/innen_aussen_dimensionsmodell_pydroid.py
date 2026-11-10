import pygame
import math
import random

# ============================================================
# Zero-Lumi Innen-Außen-Dimensionsmodell
# PyDroid-Version
# ------------------------------------------------------------
# Modell:
#
# D0 = Grundrelation / Urmuster
# D1 = Zustandsfaser / String-Analog
# D2 = Brane / Adernetz / Trägerfläche
# D3 = sichtbarer Raum
# D4 = Dynamik / Zeitspur
# D5 = Zustands-/Skalendimension sigma
# D6 = Innen-Außen-Rückkopplung
#
# Kerngedanke:
# Das Kleinste und das Größte sind nicht zwei getrennte Enden,
# sondern Grenzprojektionen derselben tieferen Zustandsstruktur.
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
pygame.display.set_caption("Zero-Lumi Innen-Aussen-Dimensionsmodell")

clock = pygame.time.Clock()

# ------------------------------------------------------------
# Farben
# ------------------------------------------------------------
BG = (3, 4, 14)
TEXT = (235, 245, 255)
SUBTEXT = (160, 210, 255)

GOLD = (255, 210, 120)
WHITE_GOLD = (255, 245, 205)
BLUE = (90, 190, 255)
CYAN = (120, 230, 255)
PURPLE = (170, 90, 255)
GREEN = (120, 255, 190)
RED = (255, 110, 95)

MODE = 0
MODES = [
    "D0-D6 Kette: Grundmuster bis Rueckkopplung",
    "Mikro-Makro Projektion: Innen und Aussen aus S",
    "Sigma-Achse D5: Mikro und Makro werden Nachbarn",
    "Innen-Aussen-Zyklus D6: Aussen beginnt im Innen",
]

# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------
def lerp(a, b, t):
    return a * (1 - t) + b * t


def clamp(v, a, b):
    return max(a, min(b, v))


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


def draw_arrow(target, p1, p2, color, width=2):
    draw_alpha_line(target, color, p1, p2, width)

    angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    size = 9

    left = (
        p2[0] - math.cos(angle - 0.45) * size,
        p2[1] - math.sin(angle - 0.45) * size,
    )
    right = (
        p2[0] - math.cos(angle + 0.45) * size,
        p2[1] - math.sin(angle + 0.45) * size,
    )

    pygame.draw.polygon(target, color[:3], [p2, left, right])


def rotate_point(cx, cy, r, a):
    return cx + math.cos(a) * r, cy + math.sin(a) * r


# ------------------------------------------------------------
# Hintergrund
# ------------------------------------------------------------
class Star:
    def __init__(self):
        self.x = random.randint(0, W - 1)
        self.y = random.randint(0, H - 1)
        self.phase = random.random() * math.tau
        self.size = random.choice([1, 1, 1, 2])

    def draw(self, target, t):
        pulse = 0.4 + 0.6 * math.sin(t * 0.025 + self.phase)
        c = int(80 + 115 * pulse)
        pygame.draw.circle(target, (c // 2, c // 2, c), (self.x, self.y), self.size)


stars = [Star() for _ in range(135)]


def draw_background(t):
    screen.fill(BG)

    # tiefer Bulk-/Zustandsraum-Glow
    for i in range(4):
        cx = int(W * (0.20 + i * 0.20) + math.sin(t * 0.008 + i) * 25)
        cy = int(H * (0.25 + i * 0.12) + math.cos(t * 0.010 + i) * 28)
        r = 160 + i * 35
        draw_alpha_circle(screen, (40 + i * 12, 45, 120 + i * 20, 16), (cx, cy), r)

    for s in stars:
        s.draw(screen, t)

    # schräges Tiefennetz
    for x in range(-140, W + 180, 80):
        draw_alpha_line(screen, (45, 80, 150, 28), (x, 0), (x + 190, H), 1)

    for y in range(0, H, 80):
        draw_alpha_line(screen, (70, 45, 145, 24), (0, y), (W, y + 85), 1)


# ------------------------------------------------------------
# D-Knoten
# ------------------------------------------------------------
class DimNode:
    def __init__(self, label, name, desc, x, y, color):
        self.label = label
        self.name = name
        self.desc = desc
        self.x = x
        self.y = y
        self.color = color
        self.phase = random.random() * math.tau

    def pos(self):
        return (self.x, self.y)

    def draw(self, target, t, active=False):
        pulse = 0.5 + 0.5 * math.sin(t * 0.04 + self.phase)
        r = 25 + int(5 * pulse)

        if active:
            draw_alpha_circle(target, (255, 220, 130, 85), (int(self.x), int(self.y)), r + 20)
            draw_alpha_circle(target, (120, 220, 255, 65), (int(self.x), int(self.y)), r + 10)
        else:
            draw_alpha_circle(target, (*self.color, 45), (int(self.x), int(self.y)), r + 10)

        pygame.draw.circle(target, self.color, (int(self.x), int(self.y)), r, 2)
        pygame.draw.circle(target, (12, 18, 36), (int(self.x), int(self.y)), r - 4)
        pygame.draw.circle(target, self.color, (int(self.x), int(self.y)), 4)

        font_big = pygame.font.SysFont(None, 28)
        font_small = pygame.font.SysFont(None, 16)

        img = font_big.render(self.label, True, WHITE_GOLD if active else TEXT)
        target.blit(img, (self.x - img.get_width() // 2, self.y - 10))

        name_img = font_small.render(self.name, True, SUBTEXT)
        target.blit(name_img, (self.x - name_img.get_width() // 2, self.y + 34))


# Positionen als Kreislauf
cx, cy = W // 2, H // 2 + 20
R = 205

labels = [
    ("D0", "Grundrelation", "Relation / Moeglichkeit / Zustandsunterschied"),
    ("D1", "Zustandsfaser", "String-Analog / Grundlinie / Schwingung"),
    ("D2", "Brane / Adernetz", "Feldtraeger / Membran / Kopplungsflaeche"),
    ("D3", "sichtbarer Raum", "x,y,z / Form / Abstand / Innen-Aussen"),
    ("D4", "Dynamik", "Zeitspur / Bewegung / Messbarkeit"),
    ("D5", "Sigma-Achse", "Skala / Zustand / Kopplung / Projektion"),
    ("D6", "Rueckkopplung", "Mikro -> Kosmos -> Grenze -> Mikro"),
]

colors = [
    GOLD,
    CYAN,
    PURPLE,
    BLUE,
    GREEN,
    (255, 145, 95),
    (255, 90, 160),
]

nodes = []
for i, (lab, name, desc) in enumerate(labels):
    a = -math.pi / 2 + i * math.tau / len(labels)
    x, y = rotate_point(cx, cy, R, a)
    nodes.append(DimNode(lab, name, desc, x, y, colors[i]))


# ------------------------------------------------------------
# bewegte Energiepunkte im Kreislauf
# ------------------------------------------------------------
class FlowPacket:
    def __init__(self, phase):
        self.phase = phase

    def draw_on_cycle(self, target, t):
        # Paket läuft entlang der D0-D6-Ringstruktur
        u = (t * 0.0035 + self.phase) % 1.0
        f = u * len(nodes)
        i = int(f) % len(nodes)
        j = (i + 1) % len(nodes)
        local = f - int(f)

        p1 = nodes[i].pos()
        p2 = nodes[j].pos()

        # leicht gebogen zum Zentrum hin
        x = lerp(p1[0], p2[0], local)
        y = lerp(p1[1], p2[1], local)

        bend = math.sin(local * math.pi) * 20
        dx = cx - x
        dy = cy - y
        mag = math.sqrt(dx * dx + dy * dy) + 1e-9
        x += dx / mag * bend
        y += dy / mag * bend

        draw_alpha_circle(target, (255, 180, 80, 120), (int(x), int(y)), 9)
        pygame.draw.circle(target, WHITE_GOLD, (int(x), int(y)), 3)


packets = [FlowPacket(i / 5) for i in range(5)]


# ------------------------------------------------------------
# Zeichnung: D0-D6 Kreislauf
# ------------------------------------------------------------
def draw_chain_model(t):
    # Verbindungen
    for i in range(len(nodes)):
        p1 = nodes[i].pos()
        p2 = nodes[(i + 1) % len(nodes)].pos()

        draw_alpha_line(screen, (80, 160, 255, 65), p1, p2, 3)
        draw_alpha_line(screen, (255, 190, 90, 55), p1, p2, 1)

    for p in packets:
        p.draw_on_cycle(screen, t)

    active = int((t * 0.025) % len(nodes))

    for i, n in enumerate(nodes):
        n.draw(screen, t, active=(i == active))

    # Zentrum: tiefe Struktur S
    pulse = 0.5 + 0.5 * math.sin(t * 0.045)
    draw_alpha_circle(screen, (120, 220, 255, int(45 + 45 * pulse)), (cx, cy), 72)
    draw_alpha_circle(screen, (170, 90, 255, int(35 + 35 * pulse)), (cx, cy), 50)

    font = pygame.font.SysFont(None, 36)
    small = pygame.font.SysFont(None, 18)

    s_img = font.render("S", True, WHITE_GOLD)
    screen.blit(s_img, (cx - s_img.get_width() // 2, cy - 18))

    txt = small.render("tiefe Struktur", True, TEXT)
    screen.blit(txt, (cx - txt.get_width() // 2, cy + 15))

    txt2 = small.render("S(x,y,z,t,sigma)", True, SUBTEXT)
    screen.blit(txt2, (cx - txt2.get_width() // 2, cy + 34))


# ------------------------------------------------------------
# Mikro-Makro Projektion
# ------------------------------------------------------------
def draw_projection_model(t):
    left = (190, H // 2 + 20)
    center = (W // 2, H // 2 + 20)
    right = (710, H // 2 + 20)

    # zentrale Quelle S
    draw_alpha_circle(screen, (120, 220, 255, 65), center, 90)
    draw_alpha_circle(screen, (170, 90, 255, 45), center, 64)
    pygame.draw.circle(screen, CYAN, center, 58, 2)

    font_big = pygame.font.SysFont(None, 36)
    font = pygame.font.SysFont(None, 22)
    small = pygame.font.SysFont(None, 18)

    s_img = font_big.render("S", True, WHITE_GOLD)
    screen.blit(s_img, (center[0] - s_img.get_width() // 2, center[1] - 23))

    s_text = small.render("S = tiefe Zustandsstruktur", True, TEXT)
    screen.blit(s_text, (center[0] - s_text.get_width() // 2, center[1] + 24))

    # Mikro-Kreis
    draw_alpha_circle(screen, (90, 190, 255, 50), left, 78)
    pygame.draw.circle(screen, BLUE, left, 62, 2)

    for i in range(18):
        a = i * math.tau / 18 + t * 0.025
        r = 12 + (i % 5) * 8
        x = left[0] + math.cos(a) * r
        y = left[1] + math.sin(a * 1.7) * r
        pygame.draw.circle(screen, CYAN, (int(x), int(y)), 2)

    m_img = font.render("R_micro", True, TEXT)
    screen.blit(m_img, (left[0] - m_img.get_width() // 2, left[1] - 98))

    m_desc = small.render("Quanten / Felder / Teilchen", True, SUBTEXT)
    screen.blit(m_desc, (left[0] - m_desc.get_width() // 2, left[1] + 78))

    # Makro-Kreis
    draw_alpha_circle(screen, (255, 170, 80, 45), right, 86)
    pygame.draw.circle(screen, GOLD, right, 66, 2)

    for i in range(28):
        a = i * 0.45 + t * 0.012
        r = (i / 28) * 58
        x = right[0] + math.cos(a) * r
        y = right[1] + math.sin(a) * r * 0.65
        pygame.draw.circle(screen, WHITE_GOLD, (int(x), int(y)), 2)

    ma_img = font.render("R_macro", True, TEXT)
    screen.blit(ma_img, (right[0] - ma_img.get_width() // 2, right[1] - 105))

    ma_desc = small.render("Kosmos / Netz / Horizont", True, SUBTEXT)
    screen.blit(ma_desc, (right[0] - ma_desc.get_width() // 2, right[1] + 86))

    # Projektionspfeile
    draw_arrow(screen, (center[0] - 70, center[1] - 15), (left[0] + 68, left[1] - 15), (90, 210, 255, 160), 2)
    draw_arrow(screen, (center[0] + 70, center[1] + 15), (right[0] - 72, right[1] + 15), (255, 190, 90, 160), 2)

    p1 = small.render("P_micro(S)", True, CYAN)
    p2 = small.render("P_macro(S)", True, GOLD)

    screen.blit(p1, (280, center[1] - 52))
    screen.blit(p2, (535, center[1] + 42))

    # unten Gleichung
    eq = font.render("R_micro = P_micro(S)       |       R_macro = P_macro(S)", True, WHITE_GOLD)
    screen.blit(eq, (W // 2 - eq.get_width() // 2, H - 92))

    eq2 = small.render("Beide Projektionen kommen aus derselben Quelle S.", True, TEXT)
    screen.blit(eq2, (W // 2 - eq2.get_width() // 2, H - 64))


# ------------------------------------------------------------
# Sigma-Achse
# ------------------------------------------------------------
def draw_sigma_axis(t):
    font = pygame.font.SysFont(None, 22)
    small = pygame.font.SysFont(None, 17)

    x0, x1 = 110, W - 110
    y = H // 2 + 60

    # Achse
    draw_alpha_line(screen, (120, 220, 255, 100), (x0, y), (x1, y), 3)

    # Kreisende als Rückkopplung oben
    arc_rect = (x0, y - 210, x1 - x0, 420)
    pygame.draw.arc(screen, (255, 190, 90), arc_rect, math.pi * 0.08, math.pi * 0.92, 2)

    left_label = font.render("sigma -> mikro", True, CYAN)
    right_label = font.render("sigma -> makro", True, GOLD)

    screen.blit(left_label, (x0 - 40, y + 28))
    screen.blit(right_label, (x1 - right_label.get_width() + 40, y + 28))

    # Mikro links
    draw_alpha_circle(screen, (90, 190, 255, 65), (x0, y), 45)
    pygame.draw.circle(screen, CYAN, (x0, y), 34, 2)

    for i in range(10):
        a = i * math.tau / 10 + t * 0.04
        px = x0 + math.cos(a) * 22
        py = y + math.sin(a) * 22
        pygame.draw.circle(screen, CYAN, (int(px), int(py)), 2)

    # Makro rechts
    draw_alpha_circle(screen, (255, 190, 90, 65), (x1, y), 50)
    pygame.draw.circle(screen, GOLD, (x1, y), 38, 2)

    for i in range(16):
        a = i * 0.55 + t * 0.015
        r = (i / 16) * 34
        px = x1 + math.cos(a) * r
        py = y + math.sin(a) * r
        pygame.draw.circle(screen, WHITE_GOLD, (int(px), int(py)), 2)

    # bewegter Punkt auf Achse
    u = 0.5 + 0.5 * math.sin(t * 0.018)
    px = lerp(x0, x1, u)
    py = y

    draw_alpha_circle(screen, (255, 180, 80, 135), (int(px), int(py)), 12)
    pygame.draw.circle(screen, WHITE_GOLD, (int(px), int(py)), 4)

    # D5-Box
    box = pygame.Surface((500, 120), pygame.SRCALPHA)
    pygame.draw.rect(box, (8, 12, 30, 195), (0, 0, 500, 120), border_radius=14)
    pygame.draw.rect(box, (90, 150, 230, 120), (0, 0, 500, 120), 2, border_radius=14)

    lines = [
        "D5 = Zustands-/Skalendimension sigma",
        "sigma beschreibt: Skala, Kopplung, Projektion, Zustandstiefe",
        "In D5 koennen Mikro und Makro Nachbarn sein.",
        "Innen und Aussen sind nicht nur Entfernung, sondern Projektion."
    ]

    yy = 12
    for i, line in enumerate(lines):
        col = WHITE_GOLD if i == 0 else TEXT
        img = small.render(line, True, col)
        box.blit(img, (14, yy))
        yy += 25

    screen.blit(box, (W // 2 - 250, 85))

    # Rückkopplungssatz
    bottom = font.render("lim(sigma -> mikro) S  ~=  lim(sigma -> makro) S", True, WHITE_GOLD)
    screen.blit(bottom, (W // 2 - bottom.get_width() // 2, H - 85))


# ------------------------------------------------------------
# D6 Innen-Außen-Zyklus
# ------------------------------------------------------------
def draw_inner_outer_cycle(t):
    center = (W // 2, H // 2 + 25)
    r_outer = 185
    r_inner = 72

    font = pygame.font.SysFont(None, 22)
    small = pygame.font.SysFont(None, 17)

    # äußerer Zyklus
    pygame.draw.circle(screen, (90, 170, 255), center, r_outer, 1)
    pygame.draw.circle(screen, (255, 190, 90), center, r_inner, 1)

    # Möbius-artige Verbindung
    pts = []
    for i in range(220):
        u = i / 219
        a = u * math.tau
        r = lerp(r_inner, r_outer, 0.5 + 0.5 * math.sin(a))
        twist = math.sin(2 * a + t * 0.012) * 28

        x = center[0] + math.cos(a) * (r + twist)
        y = center[1] + math.sin(a) * (r * 0.58)

        pts.append((x, y))

    for i in range(1, len(pts)):
        mix = i / len(pts)
        col = (
            int(lerp(90, 255, mix)),
            int(lerp(190, 180, mix)),
            int(lerp(255, 90, mix)),
            115
        )
        draw_alpha_line(screen, col, pts[i - 1], pts[i], 2)

    # Energiepunkt auf Schleife
    u = (t * 0.0035) % 1.0
    idx = int(u * (len(pts) - 1))
    px, py = pts[idx]
    draw_alpha_circle(screen, (255, 180, 80, 140), (int(px), int(py)), 12)
    pygame.draw.circle(screen, WHITE_GOLD, (int(px), int(py)), 4)

    # Labels
    labels = [
        ("MIKRO", center[0] - r_outer - 35, center[1] - 15, CYAN),
        ("MATERIE", center[0] - 55, center[1] - r_outer * 0.62 - 35, TEXT),
        ("KOSMOS", center[0] + r_outer - 35, center[1] - 15, GOLD),
        ("GRENZE", center[0] - 38, center[1] + r_outer * 0.62 + 15, PURPLE),
    ]

    for text, x, y, col in labels:
        img = font.render(text, True, col)
        screen.blit(img, (x, y))

    # Zentrum D0/D1
    draw_alpha_circle(screen, (120, 220, 255, 55), center, 52)
    pygame.draw.circle(screen, CYAN, center, 40, 2)

    img = font.render("D0/D1", True, WHITE_GOLD)
    screen.blit(img, (center[0] - img.get_width() // 2, center[1] - 12))

    img2 = small.render("Grundmuster/Faser", True, SUBTEXT)
    screen.blit(img2, (center[0] - img2.get_width() // 2, center[1] + 18))

    # Kernsatz
    box = pygame.Surface((560, 78), pygame.SRCALPHA)
    pygame.draw.rect(box, (8, 12, 30, 200), (0, 0, 560, 78), border_radius=14)
    pygame.draw.rect(box, (255, 190, 90, 130), (0, 0, 560, 78), 2, border_radius=14)

    s1 = font.render("Aussen beginnt im tiefsten Innen erneut.", True, WHITE_GOLD)
    s2 = small.render("Das Kleinste und das Groesste sind Grenzprojektionen derselben Tiefe.", True, TEXT)

    box.blit(s1, (560 // 2 - s1.get_width() // 2, 14))
    box.blit(s2, (560 // 2 - s2.get_width() // 2, 45))

    screen.blit(box, (W // 2 - 280, H - 112))


# ------------------------------------------------------------
# Textkopf + Legende
# ------------------------------------------------------------
font_title = pygame.font.SysFont(None, 34)
font_mid = pygame.font.SysFont(None, 21)
font_small = pygame.font.SysFont(None, 17)


def draw_header():
    title = font_title.render("ZERO-LUMI INNEN-AUSSEN-DIMENSIONSMODELL", True, (255, 225, 165))
    screen.blit(title, (22, 18))

    sub = font_mid.render("Mikro und Makro als Grenzprojektionen derselben Zustandsstruktur", True, TEXT)
    screen.blit(sub, (24, 52))

    mode_img = font_small.render("Modus: " + MODES[MODE], True, SUBTEXT)
    help_img = font_small.render("SPACE = Modus   |   R = Reset   |   ESC = Ende", True, (210, 220, 235))

    screen.blit(mode_img, (24, 82))
    screen.blit(help_img, (24, 104))


def draw_side_legend():
    box = pygame.Surface((300, 210), pygame.SRCALPHA)
    pygame.draw.rect(box, (8, 12, 30, 190), (0, 0, 300, 210), border_radius=14)
    pygame.draw.rect(box, (90, 150, 230, 120), (0, 0, 300, 210), 2, border_radius=14)

    lines = [
        "Kernsaetze:",
        "1. Energie = Menge",
        "2. Ordnung = Richtung",
        "3. Kopplung = Wirkung",
        "4. Dynamik macht Zeit sichtbar",
        "5. Felder tragen Zustaende",
        "6. Hilbert-Raeume beschreiben Moeglichkeiten",
        "7. Mikro/Makro = Grenzprojektionen",
        "8. Aussen beginnt im Innen"
    ]

    yy = 12
    for i, line in enumerate(lines):
        col = WHITE_GOLD if i in [0, 8] else (190, 225, 255)
        img = font_small.render(line, True, col)
        box.blit(img, (12, yy))
        yy += 21

    screen.blit(box, (W - 322, H - 238))


# ------------------------------------------------------------
# Reset
# ------------------------------------------------------------
def reset_sim():
    global packets
    packets = [FlowPacket(i / 5) for i in range(5)]


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

    draw_background(t)

    if MODE == 0:
        draw_chain_model(t)
    elif MODE == 1:
        draw_projection_model(t)
    elif MODE == 2:
        draw_sigma_axis(t)
    elif MODE == 3:
        draw_inner_outer_cycle(t)

    draw_header()

    if MODE in [0, 1]:
        draw_side_legend()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()