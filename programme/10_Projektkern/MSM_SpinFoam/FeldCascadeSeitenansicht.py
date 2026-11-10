import pygame
import math
import random

# ============================================================
# LUMYE MINI FIELD
# ------------------------------------------------------------
# Kleine laufende Tirxy-/Brane-Demo
# Stabil für PyDroid & PC
#
# SPACE = Farben wechseln
# R     = Reset
# ESC   = Ende
# ============================================================

pygame.init()

# ------------------------------------------------------------
# Fenster
# ------------------------------------------------------------
W, H = 900, 600

screen = pygame.display.set_mode((W, H))

pygame.display.set_caption("LUMYE MINI FIELD")

clock = pygame.time.Clock()

# ------------------------------------------------------------
# Farben
# ------------------------------------------------------------
MODES = [
    [(10, 15, 35), (120, 220, 255)],
    [(18, 10, 30), (255, 140, 220)],
    [(8, 25, 20), (120, 255, 180)],
]

MODE = 0

# ------------------------------------------------------------
# Partikel
# ------------------------------------------------------------
particles = []

class Particle:

    def __init__(self):

        self.x = random.uniform(0, W)
        self.y = random.uniform(0, H)

        self.phase = random.random() * math.tau

        self.speed = random.uniform(0.5, 1.8)

        self.size = random.randint(2, 5)

    def update(self, t):

        self.x += math.sin(
            t * 0.01 + self.phase
        ) * self.speed

        self.y += math.cos(
            t * 0.012 + self.phase
        ) * self.speed

        # Bildschirm-Wrap
        if self.x < 0:
            self.x = W

        if self.x > W:
            self.x = 0

        if self.y < 0:
            self.y = H

        if self.y > H:
            self.y = 0

    def draw(self, t):

        bg, col = MODES[MODE]

        pulse = (
            0.5 +
            0.5 * math.sin(
                t * 0.03 + self.phase
            )
        )

        r = int(col[0] * pulse)
        g = int(col[1] * pulse)
        b = int(col[2] * pulse)

        radius = int(self.size + pulse * 3)

        pygame.draw.circle(
            screen,
            (r, g, b),
            (int(self.x), int(self.y)),
            radius
        )

# ------------------------------------------------------------
# Erstellen
# ------------------------------------------------------------
def reset_particles():

    global particles

    particles = [
        Particle()
        for _ in range(180)
    ]

reset_particles()

# ------------------------------------------------------------
# Feldlinien
# ------------------------------------------------------------
def draw_field_lines(t):

    _, col = MODES[MODE]

    for y in range(0, H, 24):

        pts = []

        for x in range(0, W, 14):

            wave = math.sin(
                x * 0.015 +
                y * 0.01 +
                t * 0.025
            ) * 12

            pts.append((x, y + wave))

        for i in range(1, len(pts)):

            pygame.draw.line(
                screen,
                (
                    col[0] // 3,
                    col[1] // 3,
                    col[2] // 3
                ),
                pts[i - 1],
                pts[i],
                1
            )

# ------------------------------------------------------------
# Titel
# ------------------------------------------------------------
font_big = pygame.font.SysFont(None, 34)
font_small = pygame.font.SysFont(None, 20)

def draw_text():

    title = font_big.render(
        "LUMYE MINI FIELD",
        True,
        (255, 220, 160)
    )

    screen.blit(title, (20, 20))

    info = font_small.render(
        "SPACE = Modus | R = Reset | ESC = Ende",
        True,
        (220, 230, 255)
    )

    screen.blit(info, (20, 58))

    lore = font_small.render(
        "Raum lebt durch Bewegung.",
        True,
        (255, 210, 140)
    )

    screen.blit(lore, (20, H - 40))

# ------------------------------------------------------------
# Mainloop
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

                reset_particles()

    # --------------------------------------------------------
    # Hintergrund
    # --------------------------------------------------------
    bg, col = MODES[MODE]

    screen.fill(bg)

    # --------------------------------------------------------
    # Feldlinien
    # --------------------------------------------------------
    draw_field_lines(t)

    # --------------------------------------------------------
    # Partikel
    # --------------------------------------------------------
    for p in particles:

        p.update(t)

        p.draw(t)

    # --------------------------------------------------------
    # Verbindungslinien
    # --------------------------------------------------------
    for i in range(0, len(particles), 3):

        p1 = particles[i]

        for j in range(i + 1, min(i + 5, len(particles))):

            p2 = particles[j]

            dx = p1.x - p2.x
            dy = p1.y - p2.y

            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 90:

                strength = 1 - dist / 90

                pygame.draw.line(
                    screen,
                    (
                        int(col[0] * strength),
                        int(col[1] * strength),
                        int(col[2] * strength)
                    ),
                    (p1.x, p1.y),
                    (p2.x, p2.y),
                    1
                )

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------
    draw_text()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()