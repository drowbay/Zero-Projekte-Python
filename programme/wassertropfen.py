import pygame
import math
import random

pygame.init()

W, H = 800, 500
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Wassertropfen Slowmotion - Teilchen & Felder")

clock = pygame.time.Clock()

# Simulation
surface_y = 330
droplet_x = W // 2
droplet_y = 80
droplet_vy = 0.8
gravity = 0.035

impact = False
impact_time = 0
waves = []
particles = []

class Wave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 5
        self.alpha = 255

    def update(self):
        self.r += 1.4
        self.alpha -= 2.2

    def draw(self):
        if self.alpha > 0:
            color = (80, 180, 255)
            pygame.draw.circle(screen, color, (self.x, self.y), int(self.r), 2)

class Particle:
    def __init__(self, x, y):
        angle = random.uniform(math.pi, 2 * math.pi)
        speed = random.uniform(1.2, 4.2)

        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 120
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.04
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, (120, 210, 255), (int(self.x), int(self.y)), self.size)

def draw_field(cx, cy, strength):
    # Feldlinien / Energieausbreitung
    for i in range(36):
        angle = i * (math.pi * 2 / 36)
        length = 40 + strength * 0.8

        x2 = cx + math.cos(angle) * length
        y2 = cy + math.sin(angle) * length

        pygame.draw.line(
            screen,
            (60, 130, 255),
            (cx, cy),
            (x2, y2),
            1
        )

def draw_water_surface(t):
    points = []

    for x in range(0, W + 10, 10):
        wave = 0

        if impact:
            distance = abs(x - droplet_x)
            wave += math.sin(distance * 0.05 - t * 0.16) * 12 * math.exp(-distance * 0.008)

        y = surface_y + wave
        points.append((x, y))

    pygame.draw.lines(screen, (80, 190, 255), False, points, 3)

running = True

while running:
    screen.fill((8, 10, 18))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Neustart mit Leertaste
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                droplet_y = 80
                droplet_vy = 0.8
                impact = False
                impact_time = 0
                waves.clear()
                particles.clear()

    # Tropfen fällt
    if not impact:
        droplet_vy += gravity
        droplet_y += droplet_vy

        pygame.draw.circle(screen, (90, 200, 255), (droplet_x, int(droplet_y)), 18)

        # kleine innere Reflexion
        pygame.draw.circle(screen, (190, 240, 255), (droplet_x - 6, int(droplet_y) - 7), 5)

        if droplet_y + 18 >= surface_y:
            impact = True
            impact_time = 0

            waves.append(Wave(droplet_x, surface_y))

            for _ in range(65):
                particles.append(Particle(droplet_x, surface_y))

    else:
        impact_time += 1

        # Einschlag-Krone
        radius = 22 + impact_time * 0.5
        if impact_time < 70:
            pygame.draw.ellipse(
                screen,
                (70, 180, 255),
                (droplet_x - radius, surface_y - 12, radius * 2, 24),
                2
            )

        # Feld/Energie sichtbar
        if impact_time < 90:
            draw_field(droplet_x, surface_y, 90 - impact_time)

        # Neue schwächere Wellen
        if impact_time in [25, 50, 80]:
            waves.append(Wave(droplet_x, surface_y))

    # Wasseroberfläche
    draw_water_surface(impact_time)

    # Wellen
    for wv in waves[:]:
        wv.update()
        wv.draw()
        if wv.alpha <= 0:
            waves.remove(wv)

    # Spritzteilchen
    for p in particles[:]:
        p.update()
        p.draw()
        if p.life <= 0:
            particles.remove(p)

    # Boden/Wasserfläche füllen
    pygame.draw.rect(screen, (10, 40, 65), (0, surface_y + 20, W, H - surface_y))

    font = pygame.font.SysFont(None, 24)
    text1 = font.render("Wassertropfen-Slowmotion: Druckfeld, Welle, Spritzer", True, (230, 240, 255))
    text2 = font.render("Leertaste = Neustart", True, (180, 200, 220))

    screen.blit(text1, (20, 20))
    screen.blit(text2, (20, 48))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()