import pygame
import math
import random

# ============================================================
# QCD Toy Model — PyDroid Version
# ------------------------------------------------------------
# Didaktisches Modell, KEINE echte QCD-Simulation.
#
# Zeigt:
# - Quarks mit Farbladung: rot, gruen, blau
# - Antiquarks als helle Gegenfarben
# - Meson: Quark + Antiquark
# - Baryon: drei Quarks
# - Flux-Tubes / Gluonfeldlinien
# - Confinement-artige Rueckstellkraft:
#   je weiter Quarks auseinander, desto staerker zieht es sie zusammen
#
# Steuerung:
# SPACE = System wechseln
# R     = Reset
# ESC   = Ende
# ============================================================

pygame.init()

W, H = 900, 620
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("QCD Toy Model - Quarks, Gluons, Confinement")

clock = pygame.time.Clock()

# ------------------------------------------------------------
# Farben
# ------------------------------------------------------------
BG = (5, 6, 16)
TEXT = (235, 245, 255)
SUBTEXT = (160, 210, 255)

RED = (255, 80, 80)
GREEN = (80, 255, 150)
BLUE = (90, 150, 255)

ANTI_RED = (255, 185, 185)
ANTI_GREEN = (185, 255, 215)
ANTI_BLUE = (190, 215, 255)

WHITE = (250, 245, 220)
YELLOW = (255, 210, 110)
PURPLE = (180, 100, 255)
CYAN = (100, 225, 255)

# ------------------------------------------------------------
# Modi
# ------------------------------------------------------------
MODE = 0
MODES = [
    "Meson: Quark + Antiquark",
    "Baryon: 3 Quarks, farbneutral",
    "Quark-Pair Creation: Flux-Tube wird zu lang",
    "QCD-Bag: Quarks bleiben im Hadron eingeschlossen",
]

# ------------------------------------------------------------
# Physik-Spielparameter
# ------------------------------------------------------------
DT = 0.55
DAMPING = 0.992

# Confinement-artige Kraft:
# Rueckstellkraft steigt grob mit Abstand
STRING_TENSION = 0.00085

# Kurzreichweitige leichte Coulomb-artige Wechselwirkung
COULOMB = 45.0
SOFTENING = 45.0

# Bag / Hadronradius
BAG_RADIUS = 170

particles = []
flux_tubes = []
created_pairs = []


# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------
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


def dist(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def clamp(v, a, b):
    return max(a, min(b, v))


def color_for_charge(charge, anti=False):
    if charge == "r":
        return ANTI_RED if anti else RED
    if charge == "g":
        return ANTI_GREEN if anti else GREEN
    if charge == "b":
        return ANTI_BLUE if anti else BLUE
    return WHITE


# ------------------------------------------------------------
# Quark / Antiquark
# ------------------------------------------------------------
class Quark:
    def __init__(self, x, y, charge="r", anti=False):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.7, 0.7)
        self.vy = random.uniform(-0.7, 0.7)
        self.fx = 0.0
        self.fy = 0.0

        self.charge = charge
        self.anti = anti
        self.radius = 13 if not anti else 12
        self.phase = random.random() * math.tau
        self.trail = []

    def reset_force(self):
        self.fx = 0.0
        self.fy = 0.0

    def apply_force(self, fx, fy):
        self.fx += fx
        self.fy += fy

    def update(self):
        self.vx = (self.vx + self.fx * DT) * DAMPING
        self.vy = (self.vy + self.fy * DT) * DAMPING

        self.x += self.vx * DT
        self.y += self.vy * DT

        self.trail.append((self.x, self.y))
        if len(self.trail) > 18:
            self.trail.pop(0)

        # Bildschirm weich begrenzen
        if self.x < 40:
            self.x = 40
            self.vx *= -0.5
        if self.x > W - 40:
            self.x = W - 40
            self.vx *= -0.5
        if self.y < 80:
            self.y = 80
            self.vy *= -0.5
        if self.y > H - 80:
            self.y = H - 80
            self.vy *= -0.5

    def draw(self, target, t):
        col = color_for_charge(self.charge, self.anti)

        # Spur
        for i in range(1, len(self.trail)):
            a = int(8 + i * 6)
            draw_alpha_line(target, (*col, a), self.trail[i - 1], self.trail[i], 1)

        pulse = 0.5 + 0.5 * math.sin(t * 0.08 + self.phase)

        draw_alpha_circle(target, (*col, int(45 + 50 * pulse)), (int(self.x), int(self.y)), self.radius + 14)
        pygame.draw.circle(target, col, (int(self.x), int(self.y)), self.radius)

        if self.anti:
            pygame.draw.circle(target, BG, (int(self.x), int(self.y)), self.radius - 5)
            pygame.draw.circle(target, col, (int(self.x), int(self.y)), self.radius, 2)
        else:
            pygame.draw.circle(target, WHITE, (int(self.x), int(self.y)), max(3, self.radius // 3))

        font = pygame.font.SysFont(None, 18)
        label = ("anti-" if self.anti else "") + self.charge
        img = font.render(label, True, WHITE)
        target.blit(img, (self.x - img.get_width() // 2, self.y + 18))


# ------------------------------------------------------------
# Flux Tube / Gluonfeld-Linie
# ------------------------------------------------------------
class FluxTube:
    def __init__(self, a, b, color=(255, 190, 90)):
        self.a = a
        self.b = b
        self.color = color
        self.phase = random.random() * math.tau

    def length(self):
        return dist(self.a, self.b)

    def draw(self, target, t):
        ax, ay = self.a.x, self.a.y
        bx, by = self.b.x, self.b.y

        dx = bx - ax
        dy = by - ay
        L = math.sqrt(dx * dx + dy * dy) + 1e-6
        nx = -dy / L
        ny = dx / L

        pts = []
        steps = 26

        for i in range(steps + 1):
            u = i / steps
            x = ax * (1 - u) + bx * u
            y = ay * (1 - u) + by * u

            wave = math.sin(u * math.pi * 4 + t * 0.08 + self.phase) * 8
            envelope = math.sin(u * math.pi)

            x += nx * wave * envelope
            y += ny * wave * envelope

            pts.append((x, y))

        # Energie steigt mit Laenge, optisch als Dicke/Glow
        energy = clamp(L / 260, 0.3, 2.2)
        width = int(2 + energy * 2)

        for i in range(1, len(pts)):
            draw_alpha_line(target, (255, 170, 80, 55), pts[i - 1], pts[i], width + 6)
            draw_alpha_line(target, (255, 220, 130, 130), pts[i - 1], pts[i], width)

        # Gluon-Pakete laufen auf der Tube
        for k in range(3):
            u = (t * 0.012 + k / 3 + self.phase * 0.1) % 1.0
            idx = int(u * (len(pts) - 1))
            x, y = pts[idx]
            draw_alpha_circle(target, (255, 220, 120, 120), (int(x), int(y)), 7)
            pygame.draw.circle(target, WHITE, (int(x), int(y)), 2)


# ------------------------------------------------------------
# QCD-artige Kräfte
# ------------------------------------------------------------
def apply_pair_force(a, b):
    """
    Didaktische Kraft:
    - Kurze Distanz: leichte Coulomb-artige Wechselwirkung
    - Lange Distanz: Confinement-artige Stringspannung
    """
    dx = b.x - a.x
    dy = b.y - a.y
    r2 = dx * dx + dy * dy + SOFTENING * SOFTENING
    r = math.sqrt(r2)

    ux = dx / r
    uy = dy / r

    # Confinement: Rueckstellkraft waechst mit Abstand
    f_conf = STRING_TENSION * r

    # leichte kurze Wechselwirkung
    f_coul = COULOMB / r2

    # Insgesamt anziehend im Toy-Modell
    f = f_conf + f_coul

    a.apply_force(f * ux, f * uy)
    b.apply_force(-f * ux, -f * uy)


def apply_bag_force(q, cx, cy):
    """
    Bag-Modell: Quarks bleiben im Hadronbereich.
    Wenn sie zu weit rausgehen, drueckt eine Rueckstellkraft sie zurueck.
    """
    dx = q.x - cx
    dy = q.y - cy
    r = math.sqrt(dx * dx + dy * dy) + 1e-6

    if r > BAG_RADIUS:
        excess = r - BAG_RADIUS
        f = -0.018 * excess
        q.apply_force(f * dx / r, f * dy / r)


# ------------------------------------------------------------
# Szenen
# ------------------------------------------------------------
def reset_sim():
    global particles, flux_tubes, created_pairs

    particles = []
    flux_tubes = []
    created_pairs = []

    cx, cy = W // 2, H // 2 + 15

    if MODE == 0:
        # Meson: q + anti-q
        q = Quark(cx - 120, cy, "r", anti=False)
        aq = Quark(cx + 120, cy, "r", anti=True)
        q.vy = -1.1
        aq.vy = 1.1
        particles = [q, aq]
        flux_tubes = [FluxTube(q, aq)]

    elif MODE == 1:
        # Baryon: rot + gruen + blau
        q1 = Quark(cx, cy - 110, "r")
        q2 = Quark(cx - 105, cy + 70, "g")
        q3 = Quark(cx + 105, cy + 70, "b")
        q1.vx = 1.0
        q2.vy = -0.8
        q3.vx = -1.0
        particles = [q1, q2, q3]
        flux_tubes = [FluxTube(q1, q2), FluxTube(q2, q3), FluxTube(q3, q1)]

    elif MODE == 2:
        # Quark-Pair Creation: q anti-q werden auseinandergezogen
        q = Quark(cx - 90, cy, "r")
        aq = Quark(cx + 90, cy, "r", anti=True)
        q.vx = -2.4
        aq.vx = 2.4
        particles = [q, aq]
        flux_tubes = [FluxTube(q, aq)]

    elif MODE == 3:
        # QCD Bag: drei Quarks im "Hadron-Bag"
        for charge in ["r", "g", "b"]:
            angle = random.random() * math.tau
            r = random.uniform(30, 120)
            q = Quark(cx + math.cos(angle) * r, cy + math.sin(angle) * r, charge)
            q.vx = random.uniform(-1.5, 1.5)
            q.vy = random.uniform(-1.5, 1.5)
            particles.append(q)

        flux_tubes = [
            FluxTube(particles[0], particles[1]),
            FluxTube(particles[1], particles[2]),
            FluxTube(particles[2], particles[0]),
        ]


reset_sim()


# ------------------------------------------------------------
# Pair Creation fuer Mode 2
# ------------------------------------------------------------
def check_pair_creation():
    """
    Spielidee:
    Wenn Flux-Tube zu lang wird, entsteht ein neues q/anti-q Paar.
    In echter QCD: statt isolierte Quarks zu bekommen,
    bildet sich ein neues Hadronpaar.
    """
    global particles, flux_tubes, created_pairs

    if MODE != 2:
        return

    if len(created_pairs) > 0:
        return

    if not flux_tubes:
        return

    tube = flux_tubes[0]
    L = tube.length()

    if L > 330:
        mx = (tube.a.x + tube.b.x) / 2
        my = (tube.a.y + tube.b.y) / 2

        new_q = Quark(mx - 18, my, "g", anti=False)
        new_aq = Quark(mx + 18, my, "g", anti=True)

        new_q.vx = -0.7
        new_aq.vx = 0.7

        particles.append(new_q)
        particles.append(new_aq)
        created_pairs.append((new_q, new_aq))

        # alte Tube ersetzen durch zwei Meson-artige Tubes
        left = tube.a
        right = tube.b

        flux_tubes = [
            FluxTube(left, new_aq),
            FluxTube(new_q, right),
        ]


# ------------------------------------------------------------
# Zeichnen
# ------------------------------------------------------------
def draw_background(t):
    screen.fill(BG)

    # Stern-/Vakuumfluktuationen
    random.seed(4)
    for i in range(115):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        pulse = 0.4 + 0.6 * math.sin(t * 0.02 + i)
        c = int(70 + 90 * pulse)
        screen.set_at((x, y), (c // 3, c // 2, c))

    # Gitter
    for x in range(0, W, 60):
        draw_alpha_line(screen, (40, 70, 130, 24), (x, 70), (x + 70, H - 70), 1)

    for y in range(80, H - 70, 60):
        draw_alpha_line(screen, (50, 45, 110, 20), (40, y), (W - 40, y + 40), 1)


def draw_bag(t):
    if MODE != 3:
        return

    cx, cy = W // 2, H // 2 + 15
    pulse = 0.5 + 0.5 * math.sin(t * 0.035)

    draw_alpha_circle(screen, (90, 170, 255, 35), (cx, cy), BAG_RADIUS + 25)
    pygame.draw.circle(screen, (110, 210, 255), (cx, cy), BAG_RADIUS, 2)

    font = pygame.font.SysFont(None, 20)
    img = font.render("QCD-Bag / Hadronbereich", True, SUBTEXT)
    screen.blit(img, (cx - img.get_width() // 2, cy + BAG_RADIUS + 12))


def draw_color_neutrality_box():
    font = pygame.font.SysFont(None, 18)

    box = pygame.Surface((290, 145), pygame.SRCALPHA)
    pygame.draw.rect(box, (7, 12, 30, 195), (0, 0, 290, 145), border_radius=14)
    pygame.draw.rect(box, (90, 150, 230, 120), (0, 0, 290, 145), 2, border_radius=14)

    lines = [
        "QCD-Kernideen:",
        "Quarks tragen Farbladung",
        "rot + gruen + blau = farbneutral",
        "Quark + Antiquark = Meson",
        "isolierte Quarks sieht man nicht",
        "lange Flux-Tube -> Paarbildung",
    ]

    y = 12
    for i, line in enumerate(lines):
        col = YELLOW if i == 0 else TEXT
        img = font.render(line, True, col)
        box.blit(img, (12, y))
        y += 21

    screen.blit(box, (W - 315, 22))


def draw_text(t):
    font_title = pygame.font.SysFont(None, 34)
    font_mid = pygame.font.SysFont(None, 22)
    font_small = pygame.font.SysFont(None, 18)

    title = font_title.render("QCD TOY MODEL", True, YELLOW)
    screen.blit(title, (24, 20))

    sub = font_mid.render("Quarks, Gluonen-Flux-Tubes und Confinement — didaktisch, nicht echte Gitter-QCD", True, TEXT)
    screen.blit(sub, (26, 54))

    mode = font_small.render("Modus: " + MODES[MODE], True, SUBTEXT)
    help_text = font_small.render("SPACE = Modus   |   R = Reset   |   ESC = Ende", True, (210, 220, 235))

    screen.blit(mode, (26, 84))
    screen.blit(help_text, (26, 106))

    # Formel unten
    pygame.draw.line(screen, (180, 135, 75), (60, H - 52), (W - 60, H - 52), 1)

    if MODE == 0:
        cap = "Meson: Quark + Antiquark, verbunden durch eine Flux-Tube"
    elif MODE == 1:
        cap = "Baryon: drei Quarks bilden zusammen einen farbneutralen Zustand"
    elif MODE == 2:
        cap = "Confinement-Idee: Trennung erzeugt keine freien Quarks, sondern neue Paare"
    else:
        cap = "QCD-Bag-Idee: Quarks bleiben im Hadronbereich eingeschlossen"

    cap_img = font_mid.render(cap, True, (245, 220, 150))
    screen.blit(cap_img, (W // 2 - cap_img.get_width() // 2, H - 40))


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

    # Kraefte nullen
    for p in particles:
        p.reset_force()

    # Pair forces an Flux-Tubes
    for tube in flux_tubes:
        apply_pair_force(tube.a, tube.b)

    # Bag force
    if MODE == 3:
        cx, cy = W // 2, H // 2 + 15
        for p in particles:
            apply_bag_force(p, cx, cy)

    # Update
    for p in particles:
        p.update()

    check_pair_creation()

    # Draw
    draw_background(t)
    draw_bag(t)

    for tube in flux_tubes:
        tube.draw(screen, t)

    for p in particles:
        p.draw(screen, t)

    draw_color_neutrality_box()
    draw_text(t)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()