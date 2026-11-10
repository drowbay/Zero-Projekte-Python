import pygame, random, math

pygame.init()
W, H = 900, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("AGMMWSP Shield v1")
clock = pygame.time.Clock()

CX, CY = W // 2, H // 2

PARTICLES = 90
TARGET_RADIUS = 190
FIELD_STRENGTH = 0.0012
DAMPING = 0.985
WALL_THICKNESS = 24

particles = []

for _ in range(PARTICLES):
    angle = random.uniform(0, math.tau)
    radius = random.uniform(40, 330)
    particles.append({
        "x": CX + math.cos(angle) * radius,
        "y": CY + math.sin(angle) * radius,
        "vx": random.uniform(-1.3, 1.3),
        "vy": random.uniform(-1.3, 1.3),
        "phase": random.uniform(0, 10),
        "energy": random.uniform(0.4, 1.0)
    })

def field_force(p):
    dx = p["x"] - CX
    dy = p["y"] - CY
    r = math.sqrt(dx*dx + dy*dy)
    if r == 0:
        return

    nx, ny = dx / r, dy / r
    error = r - TARGET_RADIUS

    # zieht Teilchen in die Shield-Wand
    force = -error * FIELD_STRENGTH

    p["vx"] += nx * force
    p["vy"] += ny * force

def repel_particles(p1, p2):
    dx = p2["x"] - p1["x"]
    dy = p2["y"] - p1["y"]
    d = math.sqrt(dx*dx + dy*dy)

    if d == 0:
        return

    if d < 22:
        nx, ny = dx / d, dy / d
        force = (22 - d) * 0.0025

        p1["vx"] -= nx * force
        p1["vy"] -= ny * force
        p2["vx"] += nx * force
        p2["vy"] += ny * force

def draw_particle(p, t):
    x, y = p["x"], p["y"]

    pygame.draw.circle(screen, (200, 235, 255), (int(x), int(y)), 3)

    # Schneeflocken-Härchen
    for i in range(6):
        a = i * math.tau / 6
        length = 8 + math.sin(t * 0.08 + p["phase"] + i) * 3
        x2 = x + math.cos(a) * length
        y2 = y + math.sin(a) * length
        pygame.draw.line(screen, (90, 190, 255), (x, y), (x2, y2), 1)

def draw_shield(stability):
    # äußere Barriere
    pygame.draw.circle(screen, (40, 90, 150), (CX, CY), TARGET_RADIUS + WALL_THICKNESS, 1)
    pygame.draw.circle(screen, (60, 170, 255), (CX, CY), TARGET_RADIUS, 2)
    pygame.draw.circle(screen, (40, 90, 150), (CX, CY), TARGET_RADIUS - WALL_THICKNESS, 1)

    # Glow je nach Stabilität
    if stability > 0.65:
        color = (90, 220, 255)
        width = 4
    elif stability > 0.35:
        color = (180, 130, 255)
        width = 3
    else:
        color = (255, 80, 120)
        width = 2

    pygame.draw.circle(screen, color, (CX, CY), TARGET_RADIUS, width)

running = True
t = 0
field_strength = FIELD_STRENGTH

while running:
    screen.fill((4, 6, 16))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                field_strength += 0.0002
            if event.key == pygame.K_DOWN:
                field_strength = max(0.0001, field_strength - 0.0002)

    stable = 0

    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            repel_particles(particles[i], particles[j])

    for p in particles:
        dx = p["x"] - CX
        dy = p["y"] - CY
        r = math.sqrt(dx*dx + dy*dy)

        if r != 0:
            nx, ny = dx / r, dy / r
            error = r - TARGET_RADIUS
            force = -error * field_strength
            p["vx"] += nx * force
            p["vy"] += ny * force

        p["vx"] *= DAMPING
        p["vy"] *= DAMPING

        p["x"] += p["vx"] + random.uniform(-0.04, 0.04)
        p["y"] += p["vy"] + random.uniform(-0.04, 0.04)

        dx = p["x"] - CX
        dy = p["y"] - CY
        r = math.sqrt(dx*dx + dy*dy)

        if abs(r - TARGET_RADIUS) < WALL_THICKNESS:
            stable += 1

        draw_particle(p, t)

    stability = stable / PARTICLES
    draw_shield(stability)

    # Kern
    pygame.draw.circle(screen, (10, 10, 28), (CX, CY), 48)
    pygame.draw.circle(screen, (90, 190, 255), (CX, CY), 48, 1)

    font = pygame.font.SysFont(None, 26)
    text = font.render(
        f"AGMMWSP Shield | Stabilitaet: {int(stability*100)}% | Feld: {field_strength:.4f}",
        True,
        (230, 240, 255)
    )
    screen.blit(text, (20, 20))

    text2 = font.render("UP/DOWN = Feldstaerke regeln", True, (170, 190, 220))
    screen.blit(text2, (20, 50))

    pygame.display.flip()
    clock.tick(60)
    t += 1

pygame.quit()