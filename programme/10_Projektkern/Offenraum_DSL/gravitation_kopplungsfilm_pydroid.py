import pygame
import math
import random

# ============================================================
# Zero-Lumi Gravitation Kopplungsfilm
# PyDroid-Version
# ------------------------------------------------------------
# Idee:
# Gravitation ist hier NICHT als Stofffilm gemeint,
# sondern als geometrische Kopplung:
#
# Masse/Energie krümmt mögliche Wege.
# Teilchen folgen nicht "geraden Linien",
# sondern werden durch das Feld geführt.
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
pygame.display.set_caption("Zero-Lumi Gravitation Kopplungsfilm")

clock = pygame.time.Clock()

# ------------------------------------------------------------
# Farben
# ------------------------------------------------------------
BG = (3, 5, 14)
GRID = (28, 55, 95)
GRID_BRIGHT = (70, 140, 220)
MASS_COLOR = (255, 210, 120)
MASS_CORE = (255, 245, 210)
PARTICLE = (140, 220, 255)
PARTICLE_HOT = (255, 180, 90)
TEXT = (235, 245, 255)
SUBTEXT = (165, 210, 255)
PATH = (90, 190, 255)

# ------------------------------------------------------------
# Simulation
# ------------------------------------------------------------
G = 0.75
SOFTENING = 35.0
PARTICLE_COUNT = 120
MODE = 0

MODES = [
    "Orbit: Anfangsbewegung + Gravitation erzeugt Umlauf",
    "Fall: Teilchen fallen in gekruemmte Wege",
    "Wirbel: Rotation + Gravitation",
    "Doppelmasse: zwei Quellen verformen den Raumfilm",
]

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

    pad = width + 5
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
# Massequelle
# ------------------------------------------------------------
class MassSource:
    def __init__(self, x, y, mass=6500, radius=26):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
        self.phase = random.random() * math.tau

    def pos(self):
        return (self.x, self.y)

    def draw(self, target, t):
        pulse = 0.5 + 0.5 * math.sin(t * 0.04 + self.phase)

        # Gravitationsglow
        draw_alpha_circle(
            target,
            (255, 170, 70, int(28 + 28 * pulse)),
            (int(self.x), int(self.y)),
            self.radius + 42
        )

        draw_alpha_circle(
            target,
            (255, 220, 140, int(42 + 25 * pulse)),
            (int(self.x), int(self.y)),
            self.radius + 18
        )

        pygame.draw.circle(
            target,
            MASS_COLOR,
            (int(self.x), int(self.y)),
            self.radius
        )
        pygame.draw.circle(
            target,
            MASS_CORE,
            (int(self.x), int(self.y)),
            max(4, self.radius // 3)
        )


# ------------------------------------------------------------
# Teilchen
# ------------------------------------------------------------
class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        if MODE == 0:
            # Orbit: Start ringförmig um Zentrum
            angle = random.random() * math.tau
            r = random.uniform(120, 270)
            cx, cy = W * 0.52, H * 0.47
            self.x = cx + math.cos(angle) * r
            self.y = cy + math.sin(angle) * r

            # Tangentiale Anfangsgeschwindigkeit
            speed = random.uniform(1.15, 2.05)
            self.vx = -math.sin(angle) * speed
            self.vy = math.cos(angle) * speed

        elif MODE == 1:
            # Fall: zufällig oben/außen, fast keine Geschwindigkeit
            self.x = random.uniform(80, W - 80)
            self.y = random.uniform(90, H - 130)
            self.vx = random.uniform(-0.4, 0.4)
            self.vy = random.uniform(-0.4, 0.4)

        elif MODE == 2:
            # Wirbel: stärker rotierende Anfangsbewegung
            angle = random.random() * math.tau
            r = random.uniform(150, 310)
            cx, cy = W * 0.50, H * 0.44
            self.x = cx + math.cos(angle) * r
            self.y = cy + math.sin(angle) * r
            speed = random.uniform(1.7, 2.8)
            self.vx = -math.sin(angle) * speed
            self.vy = math.cos(angle) * speed

        else:
            # Doppelmasse: Teilchen von links/rechts
            side = random.choice([-1, 1])
            self.x = W // 2 + side * random.uniform(260, 390)
            self.y = random.uniform(110, H - 160)
            self.vx = -side * random.uniform(0.8, 1.6)
            self.vy = random.uniform(-0.5, 0.5)

        self.life = random.randint(400, 900)
        self.trail = []
        self.size = random.choice([2, 2, 3])

    def update(self, sources):
        ax = 0.0
        ay = 0.0

        # Gravitation von allen Quellen
        for s in sources:
            dx = s.x - self.x
            dy = s.y - self.y
            r2 = dx * dx + dy * dy + SOFTENING * SOFTENING
            r = math.sqrt(r2)

            force = G * s.mass / r2

            ax += force * dx / r
            ay += force * dy / r

        # leichte Dämpfung, damit PyDroid stabil bleibt
        damping = 0.998
        self.vx = (self.vx + ax) * damping
        self.vy = (self.vy + ay) * damping

        self.x += self.vx
        self.y += self.vy

        self.trail.append((self.x, self.y))
        if len(self.trail) > 28:
            self.trail.pop(0)

        self.life -= 1

        # Reset bei Rand oder wenn zu nah am Zentrum
        if (
            self.x < -80 or self.x > W + 80
            or self.y < -80 or self.y > H + 80
            or self.life <= 0
        ):
            self.reset()

        for s in sources:
            if math.hypot(self.x - s.x, self.y - s.y) < s.radius + 4:
                self.reset()

    def draw(self, target):
        # Spur
        for i in range(1, len(self.trail)):
            p1 = self.trail[i - 1]
            p2 = self.trail[i]
            a = int(10 + i * 5)

            draw_alpha_line(
                target,
                (80, 190, 255, a),
                p1,
                p2,
                1
            )

        # Teilchenfarbe nach Geschwindigkeit
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        hot = clamp(speed / 4.0, 0, 1)

        col = (
            int(PARTICLE[0] * (1 - hot) + PARTICLE_HOT[0] * hot),
            int(PARTICLE[1] * (1 - hot) + PARTICLE_HOT[1] * hot),
            int(PARTICLE[2] * (1 - hot) + PARTICLE_HOT[2] * hot),
        )

        pygame.draw.circle(target, col, (int(self.x), int(self.y)), self.size)


# ------------------------------------------------------------
# Szenenaufbau
# ------------------------------------------------------------
sources = []
particles = []


def reset_sim():
    global sources, particles

    if MODE == 3:
        sources = [
            MassSource(W * 0.40, H * 0.43, 5200, 23),
            MassSource(W * 0.62, H * 0.45, 5200, 23),
        ]
    else:
        sources = [
            MassSource(W * 0.52, H * 0.45, 7200, 28),
        ]

    particles = [Particle() for _ in range(PARTICLE_COUNT)]


reset_sim()

# ------------------------------------------------------------
# Feld / Raumfilm zeichnen
# ------------------------------------------------------------
def gravity_accel_at(x, y, sources):
    ax = 0.0
    ay = 0.0

    for s in sources:
        dx = s.x - x
        dy = s.y - y
        r2 = dx * dx + dy * dy + SOFTENING * SOFTENING
        r = math.sqrt(r2)
        force = G * s.mass / r2
        ax += force * dx / r
        ay += force * dy / r

    return ax, ay


def draw_background(t):
    screen.fill(BG)

    # Sterne
    random.seed(3)
    for i in range(110):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        tw = 0.4 + 0.6 * math.sin(t * 0.02 + i)
        c = int(80 + 80 * tw)
        screen.set_at((x, y), (c // 2, c // 2, c))

    # Verzerrtes Grid als "Kopplungsfilm"
    spacing = 45

    # horizontale Linien
    for yy in range(80, H - 90, spacing):
        pts = []
        for xx in range(40, W - 40, 18):
            ax, ay = gravity_accel_at(xx, yy, sources)
            strength = math.sqrt(ax * ax + ay * ay)

            # Verzerrung zeigt: Wege werden geformt
            wx = xx + ax * 1400
            wy = yy + ay * 1400 + math.sin(t * 0.01 + xx * 0.02) * 2

            pts.append((wx, wy))

        for i in range(1, len(pts)):
            draw_alpha_line(screen, (55, 105, 180, 55), pts[i - 1], pts[i], 1)

    # vertikale Linien
    for xx in range(60, W - 60, spacing):
        pts = []
        for yy in range(70, H - 100, 18):
            ax, ay = gravity_accel_at(xx, yy, sources)

            wx = xx + ax * 1400 + math.cos(t * 0.01 + yy * 0.02) * 2
            wy = yy + ay * 1400

            pts.append((wx, wy))

        for i in range(1, len(pts)):
            draw_alpha_line(screen, (55, 105, 180, 48), pts[i - 1], pts[i], 1)


def draw_field_arrows(t):
    # Pfeile zeigen lokale Feldrichtung
    for yy in range(115, H - 135, 70):
        for xx in range(90, W - 90, 70):
            ax, ay = gravity_accel_at(xx, yy, sources)
            mag = math.sqrt(ax * ax + ay * ay) + 1e-9

            nx = ax / mag
            ny = ay / mag

            length = clamp(mag * 6500, 8, 28)

            p1 = (xx, yy)
            p2 = (xx + nx * length, yy + ny * length)

            draw_alpha_line(screen, (90, 210, 255, 85), p1, p2, 1)

            # kleine Pfeilspitze
            angle = math.atan2(ny, nx)
            left = (
                p2[0] - math.cos(angle - 0.45) * 6,
                p2[1] - math.sin(angle - 0.45) * 6,
            )
            right = (
                p2[0] - math.cos(angle + 0.45) * 6,
                p2[1] - math.sin(angle + 0.45) * 6,
            )

            pygame.draw.polygon(screen, (90, 210, 255), [p2, left, right])


# ------------------------------------------------------------
# Text
# ------------------------------------------------------------
font_title = pygame.font.SysFont(None, 34)
font_mid = pygame.font.SysFont(None, 22)
font_small = pygame.font.SysFont(None, 18)


def draw_text():
    title = font_title.render("GRAVITATION ALS GEOMETRISCHER KOPPLUNGSFILM", True, (255, 225, 165))
    screen.blit(title, (22, 20))

    sub = font_mid.render("Nicht Stofffilm: Raumzeit-Geometrie formt moegliche Wege", True, TEXT)
    screen.blit(sub, (24, 54))

    mode = font_small.render("Modus: " + MODES[MODE], True, SUBTEXT)
    help_text = font_small.render("SPACE = Modus   |   R = Reset   |   ESC = Ende", True, (210, 220, 235))

    screen.blit(mode, (24, 84))
    screen.blit(help_text, (24, 106))

    # Formelbox
    box = pygame.Surface((330, 150), pygame.SRCALPHA)
    pygame.draw.rect(box, (7, 12, 28, 190), (0, 0, 330, 150), border_radius=14)
    pygame.draw.rect(box, (80, 150, 230, 120), (0, 0, 330, 150), 2, border_radius=14)

    lines = [
        "Modell-Lesart:",
        "Masse/Energie -> Wegkruemmung",
        "Wegkruemmung -> Bewegung",
        "Anfangsimpuls + Gravitation -> Rotation",
        "",
        "Fachlich:",
        "Gravitation koppelt an Energie-Impuls.",
    ]

    y = 12
    for i, line in enumerate(lines):
        col = (255, 225, 165) if i in [0, 5] else (190, 225, 255)
        img = font_small.render(line, True, col)
        box.blit(img, (12, y))
        y += 19

    screen.blit(box, (W - 355, 20))


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
    for p in particles:
        p.update(sources)

    # Draw
    draw_background(t)
    draw_field_arrows(t)

    # Massequellen
    for s in sources:
        s.draw(screen, t)

    # Teilchen
    for p in particles:
        p.draw(screen)

    # Unterer Merksatz
    pygame.draw.line(screen, (180, 135, 75), (60, H - 58), (W - 60, H - 58), 1)
    cap = font_mid.render("Gravitation ist nicht der Film im Raum — sie ist die Formung der Wege.", True, (245, 220, 150))
    screen.blit(cap, (W // 2 - cap.get_width() // 2, H - 46))

    draw_text()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()