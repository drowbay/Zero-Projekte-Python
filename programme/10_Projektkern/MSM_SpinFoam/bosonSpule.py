import pygame
import random
import math

pygame.init()

W, H = 900, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("AGMMWSP - stabile Feldmulde")
clock = pygame.time.Clock()

CENTER_X, CENTER_Y = W // 2, H // 2

PARTICLE_COUNT = 70
TARGET_RADIUS = 170      # stabile Zone
SPRING_FORCE = 0.0009    # Rückstellkraft
DAMPING = 0.985          # Beruhigung
JITTER = 0.04            # Mikro-Zittern

particles = []

for _ in range(PARTICLE_COUNT):
    angle = random.uniform(0, math.tau)
    radius = random.uniform(40, 310)
    particles.append({
        "x": CENTER_X + math.cos(angle) * radius,
        "y": CENTER_Y + math.sin(angle) * radius,
        "vx": random.uniform(-1.2, 1.2),
        "vy": random.uniform(-1.2, 1.2),
        "phase": random.uniform(0, 10)
    })

def draw_snow_particle(p, t):
    x, y = p["x"], p["y"]

    pygame.draw.circle(screen, (210, 235, 255), (int(x), int(y)), 3)

    # Schneeflocken-Härchen: 6-fach, vibrierend
    for i in range(6):
        a = i * math.tau / 6
        length = 10 + math.sin(t * 0.08 + p["phase"] + i) * 3
        x2 = x + math.cos(a) * length
        y2 = y + math.sin(a) * length
        pygame.draw.line(screen, (100, 190, 255), (x, y), (x2, y2), 1)

def apply_field(p):
    dx = p["x"] - CENTER_X
    dy = p["y"] - CENTER_Y
    r = math.sqrt(dx * dx + dy * dy)

    if r == 0:
        return

    nx = dx / r
    ny = dy / r

    # Ziel: Teilchen sollen Richtung TARGET_RADIUS wandern
    error = r - TARGET_RADIUS

    # Rückstellkraft: zu weit draußen -> nach innen, zu weit innen -> nach außen
    fx = -nx * error * SPRING_FORCE
    fy = -ny * error * SPRING_FORCE

    p["vx"] += fx
    p["vy"] += fy

def interact(p1, p2):
    dx = p2["x"] - p1["x"]
    dy = p2["y"] - p1["y"]
    dist = math.sqrt(dx * dx + dy * dy)

    if dist == 0:
        return

    # Abstand halten, sonst verklumpen sie
    if dist < 35:
        force = (35 - dist) * 0.0018
        nx = dx / dist
        ny = dy / dist

        p1["vx"] -= nx * force
        p1["vy"] -= ny * force
        p2["vx"] += nx * force
        p2["vy"] += ny * force

        pygame.draw.line(
            screen,
            (255, 120, 200),
            (p1["x"], p1["y"]),
            (p2["x"], p2["y"]),
            1
        )

running = True
t = 0

while running:
    screen.fill((4, 6, 16))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Feldzonen zeichnen
    pygame.draw.circle(screen, (30, 70, 120), (CENTER_X, CENTER_Y), TARGET_RADIUS, 2)
    pygame.draw.circle(screen, (20, 40, 80), (CENTER_X, CENTER_Y), TARGET_RADIUS - 55, 1)
    pygame.draw.circle(screen, (20, 40, 80), (CENTER_X, CENTER_Y), TARGET_RADIUS + 55, 1)

    # Interaktionen
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            interact(particles[i], particles[j])

    # Update
    stable_count = 0

    for p in particles:
        apply_field(p)

        p["vx"] *= DAMPING
        p["vy"] *= DAMPING

        p["x"] += p["vx"] + random.uniform(-JITTER, JITTER)
        p["y"] += p["vy"] + random.uniform(-JITTER, JITTER)

        dx = p["x"] - CENTER_X
        dy = p["y"] - CENTER_Y
        r = math.sqrt(dx * dx + dy * dy)

        if abs(r - TARGET_RADIUS) < 18:
            stable_count += 1

        draw_snow_particle(p, t)

    # Kern
    pygame.draw.circle(screen, (10, 10, 25), (CENTER_X, CENTER_Y), 45)
    pygame.draw.circle(screen, (80, 180, 255), (CENTER_X, CENTER_Y), 45, 1)

    font = pygame.font.SysFont(None, 26)
    txt = font.render(
        f"AGMMWSP stabile Feldmulde | stabile Teilchen: {stable_count}/{PARTICLE_COUNT}",
        True,
        (220, 235, 255)
    )
    screen.blit(txt, (20, 20))

    pygame.display.flip()
    clock.tick(60)
    t += 1

pygame.quit()