import pygame
import math
import random

# ============================================================
# Zero-Lumi Onami Akashi Leibresonanz
# ------------------------------------------------------------
# Theorie-Experiment:
# Gefühl als bewegte innere Resonanz im Körper.
#
# Anime/Fantasy-Style:
# - Aura
# - Glow
# - Wellenlinie
# - Akashi-Siegel
# - kreisende Lichtpartikel
# - innere Resonanzkerne
#
# Steuerung:
#   1 = Ruhe
#   2 = Onami-Welle
#   3 = Enge / Druck
#   4 = Weite / Öffnung
#   5 = Kreisel / Wirbel
#   SPACE = Modus wechseln
#   UP/DOWN = Intensität ändern
#   ESC = Ende
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zero-Lumi Onami Akashi Leibresonanz")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 15)

# Farben
BLACK = (5, 6, 14)
WHITE = (245, 248, 255)
SOFT = (130, 160, 220)
DARK = (15, 20, 40)

CYAN = (70, 230, 255)
BLUE = (80, 140, 255)
VIOLET = (170, 90, 255)
PINK = (255, 80, 190)
RED = (255, 70, 90)
ORANGE = (255, 150, 70)
GOLD = (255, 220, 110)
GREEN = (90, 255, 170)

body_x = WIDTH // 2
head = (body_x + 10, 90)

mode = 1
intensity = 0.75
t = 0.0

# Körperzonen
nodes = [
    ("Kopf", body_x + 8, 110, 0.25),
    ("Hals", body_x + 5, 165, 0.35),
    ("Brust", body_x, 235, 0.85),
    ("Bauch", body_x - 10, 340, 0.70),
    ("Becken", body_x - 5, 455, 0.45),
]

particles = []
for _ in range(230):
    particles.append({
        "x": body_x + random.uniform(-65, 65),
        "y": random.uniform(125, 520),
        "r": random.uniform(1.2, 3.4),
        "phase": random.uniform(0, math.tau),
        "speed": random.uniform(0.5, 2.2),
        "orbit": random.uniform(10, 80),
        "kind": random.choice(["dot", "spark", "petal"])
    })


def mix(a, b, k):
    k = max(0, min(1, k))
    return (
        int(a[0] + (b[0] - a[0]) * k),
        int(a[1] + (b[1] - a[1]) * k),
        int(a[2] + (b[2] - a[2]) * k),
    )


def draw_text(txt, x, y, color=WHITE, f=font):
    img = f.render(txt, True, color)
    screen.blit(img, (x, y))


def mode_name():
    return {
        1: "Shizuka — ruhige Resonanz",
        2: "Onami — große innere Welle",
        3: "Kurai — Enge / Druck",
        4: "Hikari — Weite / Öffnung",
        5: "Rasen — Kreisel / Wirbel",
    }.get(mode, "Unbekannt")


def palette():
    if mode == 1:
        return BLUE, CYAN
    if mode == 2:
        return CYAN, VIOLET
    if mode == 3:
        return VIOLET, RED
    if mode == 4:
        return CYAN, GREEN
    if mode == 5:
        return PINK, ORANGE
    return BLUE, CYAN


def activity(y, base):
    if mode == 1:
        return base * (0.45 + 0.25 * math.sin(t * 1.1))

    if mode == 2:
        return base * (0.55 + 0.45 * math.sin(t * 3.0 - y * 0.035))

    if mode == 3:
        center = 235
        pressure = math.exp(-((y - center) ** 2) / 8000)
        return pressure * (0.75 + 0.25 * math.sin(t * 5.5))

    if mode == 4:
        center = 270
        open_ = math.exp(-((y - center) ** 2) / 17000)
        return open_ * (0.65 + 0.35 * math.sin(t * 1.7))

    if mode == 5:
        center = 320
        swirl = math.exp(-((y - center) ** 2) / 19000)
        return swirl * (0.65 + 0.35 * math.sin(t * 4.0))

    return base


def draw_background():
    # Anime-Night-Gradient als Streifen
    for y in range(HEIGHT):
        k = y / HEIGHT
        col = mix((5, 6, 18), (18, 8, 35), k)
        pygame.draw.line(screen, col, (0, y), (WIDTH, y))

    # dezente Sterne / Akashi-Partikel
    random.seed(3)
    for _ in range(90):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        blink = 0.5 + 0.5 * math.sin(t * 1.2 + x * 0.02)
        c = mix((40, 50, 90), (120, 170, 255), blink)
        pygame.draw.circle(screen, c, (x, y), 1)


def draw_body():
    # Körperumriss als Anime-Silhouette
    outline = (90, 110, 150)

    pygame.draw.circle(screen, outline, head, 38, 2)

    # Nase
    pygame.draw.line(screen, outline, (head[0] + 29, head[1] - 5), (head[0] + 48, head[1] + 2), 2)
    pygame.draw.line(screen, outline, (head[0] + 48, head[1] + 2), (head[0] + 30, head[1] + 10), 2)

    # Hals
    pygame.draw.line(screen, outline, (body_x, 125), (body_x - 5, 175), 3)

    # Rücken
    pygame.draw.line(screen, outline, (body_x - 25, 165), (body_x - 58, 300), 3)
    pygame.draw.line(screen, outline, (body_x - 58, 300), (body_x - 25, 475), 3)

    # Vorderseite
    pygame.draw.line(screen, outline, (body_x + 15, 170), (body_x + 62, 255), 3)
    pygame.draw.line(screen, outline, (body_x + 62, 255), (body_x + 35, 360), 3)
    pygame.draw.line(screen, outline, (body_x + 35, 360), (body_x + 25, 475), 3)

    # Arm
    pygame.draw.line(screen, outline, (body_x + 35, 230), (body_x + 92, 340), 3)
    pygame.draw.line(screen, outline, (body_x + 92, 340), (body_x + 70, 430), 3)

    # Beine
    pygame.draw.line(screen, outline, (body_x - 10, 475), (body_x - 35, 590), 3)
    pygame.draw.line(screen, outline, (body_x + 20, 475), (body_x + 65, 590), 3)


def draw_aura():
    c1, c2 = palette()

    # große Aura um Körper
    for i in range(12, 0, -1):
        w = int(75 + i * 16 + 45 * intensity * math.sin(t * 1.3 + i))
        h = int(230 + i * 18)
        col = mix((12, 14, 30), c1, 0.08 + i * 0.018)
        rect = pygame.Rect(body_x - w // 2, 95 - i, w, h * 2)
        pygame.draw.ellipse(screen, col, rect, 1)

    # äußere pulsierende Aura
    pulse = 0.5 + 0.5 * math.sin(t * 1.8)
    rect = pygame.Rect(
        body_x - int(115 + 35 * pulse * intensity),
        85 - int(10 * pulse),
        int(230 + 70 * pulse * intensity),
        500 + int(30 * pulse),
    )
    pygame.draw.ellipse(screen, mix(c1, c2, pulse), rect, 2)


def draw_akashi_seal():
    c1, c2 = palette()
    cx, cy = body_x, 235
    pulse = 0.5 + 0.5 * math.sin(t * 2.2)

    radius = int(42 + 12 * pulse * intensity)

    # Siegelringe
    pygame.draw.circle(screen, mix(c1, WHITE, 0.2), (cx, cy), radius, 2)
    pygame.draw.circle(screen, mix(c2, WHITE, 0.15), (cx, cy), radius + 18, 1)
    pygame.draw.circle(screen, mix(c1, c2, pulse), (cx, cy), radius - 18, 1)

    # rotierende Zeichen-Strahlen
    for i in range(12):
        ang = t * 1.4 + i * math.tau / 12
        r1 = radius - 8
        r2 = radius + 22
        x1 = cx + math.cos(ang) * r1
        y1 = cy + math.sin(ang) * r1
        x2 = cx + math.cos(ang) * r2
        y2 = cy + math.sin(ang) * r2
        pygame.draw.line(screen, mix(c1, c2, i / 12), (x1, y1), (x2, y2), 1)

    # Kern
    pygame.draw.circle(screen, WHITE, (cx, cy), int(4 + 5 * pulse))
    pygame.draw.circle(screen, c2, (cx, cy), int(12 + 6 * pulse), 1)


def draw_resonance_cores():
    c1, c2 = palette()

    for name, x, y, base in nodes:
        a = abs(activity(y, base)) * intensity
        radius = int(10 + 55 * a)

        # Glow-Ringe
        for k in range(5, 0, -1):
            rr = int(radius * k / 3.5)
            col = mix(DARK, mix(c1, c2, a), 0.18 + 0.08 * k)
            pygame.draw.circle(screen, col, (int(x), int(y)), rr, 1)

        pygame.draw.circle(screen, mix(c1, c2, a), (int(x), int(y)), int(5 + 12 * a))
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), max(2, int(2 + 4 * a)))


def draw_onami_wave():
    c1, c2 = palette()

    # Hauptwelle
    pts = []
    for y in range(125, 525, 6):
        if mode == 2:
            amp = 55 * intensity
            x = body_x + math.sin(t * 3.2 - y * 0.032) * amp
        elif mode == 3:
            amp = 20 * intensity
            x = body_x + math.sin(t * 6.0 - y * 0.055) * amp
        elif mode == 4:
            amp = 75 * intensity
            x = body_x + math.sin(t * 1.8 - y * 0.022) * amp
        elif mode == 5:
            amp = 60 * intensity
            x = body_x + math.sin(t * 4.5 - y * 0.045) * amp
        else:
            amp = 30 * intensity
            x = body_x + math.sin(t * 1.4 - y * 0.025) * amp

        pts.append((int(x), y))

    # Glow-Linie mehrfach
    for width, col in [
        (7, mix(c1, c2, 0.2)),
        (4, mix(c1, c2, 0.6)),
        (2, WHITE),
    ]:
        if len(pts) > 1:
            pygame.draw.lines(screen, col, False, pts, width)

    # zweite feine Gegenphase
    pts2 = []
    for y in range(130, 515, 8):
        x = body_x + math.cos(t * 2.4 - y * 0.031) * (28 + 32 * intensity)
        pts2.append((int(x), y))

    pygame.draw.lines(screen, mix(c2, WHITE, 0.15), False, pts2, 2)


def draw_pressure_bands():
    c1, c2 = palette()

    for i, y in enumerate(range(155, 505, 35)):
        ph = t * 2.6 + i * 0.7

        if mode == 3:
            half = int(75 - 42 * intensity * (0.5 + 0.5 * math.sin(ph)))
        elif mode == 4:
            half = int(50 + 85 * intensity * (0.5 + 0.5 * math.sin(ph)))
        else:
            half = int(55 + 28 * math.sin(ph) * intensity)

        col = mix(c1, c2, (math.sin(ph) + 1) / 2)
        pygame.draw.line(screen, col, (body_x - half, y), (body_x + half, y), 1)

        # kleine Endpunkte wie Energieperlen
        pygame.draw.circle(screen, col, (body_x - half, y), 3)
        pygame.draw.circle(screen, col, (body_x + half, y), 3)


def draw_particles():
    c1, c2 = palette()

    for p in particles:
        ph = p["phase"]

        if mode == 1:
            dx = math.sin(t * p["speed"] + ph) * 18 * intensity
            dy = math.cos(t * p["speed"] * 0.7 + ph) * 8 * intensity

        elif mode == 2:
            dx = math.sin(t * 3.4 - p["y"] * 0.038 + ph) * 48 * intensity
            dy = math.sin(t * 2.0 + ph) * 13 * intensity

        elif mode == 3:
            dx = (body_x - p["x"]) * 0.40 * intensity + math.sin(t * 5.5 + ph) * 5
            dy = math.cos(t * 4.0 + ph) * 5

        elif mode == 4:
            dx = (p["x"] - body_x) * 0.55 * intensity + math.sin(t * 2.0 + ph) * 18
            dy = math.sin(t * 1.4 + ph) * 8

        elif mode == 5:
            cx, cy = body_x, 320
            ang = math.atan2(p["y"] - cy, p["x"] - cx)
            dist = math.hypot(p["x"] - cx, p["y"] - cy)
            swirl = ang + t * 2.2 * intensity + ph * 0.15
            dx = math.cos(swirl) * min(85, dist * 0.36)
            dy = math.sin(swirl) * min(85, dist * 0.36)

        x = int(p["x"] + dx)
        y = int(p["y"] + dy)

        if body_x - 160 < x < body_x + 180 and 80 < y < 590:
            k = 0.5 + 0.5 * math.sin(t * 2.0 + ph)
            col = mix(c1, c2, k)

            if p["kind"] == "dot":
                pygame.draw.circle(screen, col, (x, y), int(p["r"]))
                pygame.draw.circle(screen, WHITE, (x, y), 1)

            elif p["kind"] == "spark":
                pygame.draw.line(screen, col, (x - 4, y), (x + 4, y), 1)
                pygame.draw.line(screen, col, (x, y - 4), (x, y + 4), 1)

            else:
                # kleine Petal-/Sakura-Form
                pygame.draw.ellipse(screen, col, (x - 3, y - 2, 7, 4), 1)


def draw_ui():
    draw_text("Zero-Lumi Onami Akashi Leibresonanz", 25, 22)
    draw_text(f"Modus {mode}: {mode_name()}", 25, 55, CYAN)
    draw_text(f"Intensität: {int(intensity * 100)}%", 25, 82, WHITE, small_font)

    draw_text("Theorie-Experiment:", 25, HEIGHT - 160, WHITE, small_font)
    draw_text("Gefühl = bewegte Leibresonanz, nicht stiller Punkt.", 25, HEIGHT - 136, SOFT, small_font)
    draw_text("Welle = innere Zustandsbewegung / Klang im Körper.", 25, HEIGHT - 114, SOFT, small_font)

    draw_text("Steuerung:", 25, HEIGHT - 78, WHITE, small_font)
    draw_text("1 Ruhe | 2 Welle | 3 Enge | 4 Weite | 5 Kreisel", 25, HEIGHT - 55, SOFT, small_font)
    draw_text("SPACE wechseln | ↑/↓ Intensität | ESC Ende", 25, HEIGHT - 33, SOFT, small_font)

    # rechte Legende
    x = WIDTH - 330
    y = 35
    draw_text("Onami-Legende", x, y)
    draw_text("Aura = Resonanzfeld", x, y + 30, SOFT, small_font)
    draw_text("Siegel = Brust-Kopplungspunkt", x, y + 52, SOFT, small_font)
    draw_text("Partikel = innere Aktivierung", x, y + 74, SOFT, small_font)
    draw_text("Bänder = Enge / Weite", x, y + 96, SOFT, small_font)
    draw_text("Welle = Gefühl in Bewegung", x, y + 118, SOFT, small_font)


running = True

while running:
    dt = clock.tick(60) / 1000
    t += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_SPACE:
                mode += 1
                if mode > 5:
                    mode = 1

            if event.key == pygame.K_1:
                mode = 1
            if event.key == pygame.K_2:
                mode = 2
            if event.key == pygame.K_3:
                mode = 3
            if event.key == pygame.K_4:
                mode = 4
            if event.key == pygame.K_5:
                mode = 5

            if event.key == pygame.K_UP:
                intensity = min(1.6, intensity + 0.08)

            if event.key == pygame.K_DOWN:
                intensity = max(0.05, intensity - 0.08)

    draw_background()

    draw_aura()
    draw_pressure_bands()
    draw_resonance_cores()
    draw_particles()
    draw_onami_wave()
    draw_akashi_seal()
    draw_body()
    draw_ui()

    pygame.display.flip()

pygame.quit()