import pygame
import math
import random

# ============================================================
# Zero-Lumi Leibresonanz — Seitenansicht Simulation
# ------------------------------------------------------------
# Idee:
# Gefühl ist nicht nur ein Wort, sondern eine bewegte Resonanz
# im Körper: Weite/Enge, Hoch/Runter, Welle, Kreisel, Puls,
# Spannung, Wärme/Kälte, Druck, Fluss.
#
# Steuerung:
#   1 = ruhige Resonanz
#   2 = Welle
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
pygame.display.set_caption("Zero-Lumi Leibresonanz — Seitenansicht")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 16)

# ------------------------------------------------------------
# Farben
# ------------------------------------------------------------

BLACK = (8, 10, 18)
WHITE = (235, 240, 255)
GREY = (80, 90, 110)
DARK_GREY = (35, 42, 60)

CYAN = (60, 220, 255)
BLUE = (70, 130, 255)
VIOLET = (170, 90, 255)
PINK = (255, 80, 190)
RED = (255, 80, 80)
ORANGE = (255, 150, 60)
YELLOW = (255, 220, 90)
GREEN = (90, 255, 170)

# ------------------------------------------------------------
# Körper-Seitenansicht
# ------------------------------------------------------------

body_center_x = WIDTH // 2
body_top = 100
body_bottom = 560

# Wir zeichnen keine perfekte Anatomie, sondern einen Symbolkörper
head_center = (body_center_x + 10, 90)
chest_center = (body_center_x, 220)
belly_center = (body_center_x - 10, 340)
pelvis_center = (body_center_x - 5, 455)

# Resonanzpunkte entlang der Körperachse
resonance_nodes = [
    {"name": "Kopf", "pos": (body_center_x + 8, 110), "base": 0.25},
    {"name": "Hals", "pos": (body_center_x + 5, 165), "base": 0.35},
    {"name": "Brust", "pos": (body_center_x, 235), "base": 0.75},
    {"name": "Bauch", "pos": (body_center_x - 10, 340), "base": 0.65},
    {"name": "Becken", "pos": (body_center_x - 5, 455), "base": 0.45},
]

particles = []

for i in range(160):
    y = random.randint(130, 500)
    x = body_center_x + random.randint(-50, 50)
    particles.append({
        "x": x,
        "y": y,
        "r": random.uniform(1.5, 4.0),
        "phase": random.uniform(0, math.tau),
        "speed": random.uniform(0.5, 1.6),
        "drift": random.uniform(-1.0, 1.0),
    })


mode = 1
intensity = 0.65
time_value = 0.0


def draw_text(text, x, y, color=WHITE, fnt=font):
    img = fnt.render(text, True, color)
    screen.blit(img, (x, y))


def lerp(a, b, t):
    return a + (b - a) * t


def mix_color(c1, c2, t):
    t = max(0, min(1, t))
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


def draw_body_outline():
    # Kopf
    pygame.draw.circle(screen, (28, 35, 55), head_center, 38, 2)

    # Gesichtsnase Seitenansicht
    pygame.draw.line(screen, GREY, (head_center[0] + 30, head_center[1] - 5),
                     (head_center[0] + 48, head_center[1] + 2), 2)
    pygame.draw.line(screen, GREY, (head_center[0] + 48, head_center[1] + 2),
                     (head_center[0] + 30, head_center[1] + 10), 2)

    # Hals
    pygame.draw.line(screen, GREY, (body_center_x, 125), (body_center_x - 5, 175), 3)

    # Rückenlinie
    pygame.draw.line(screen, GREY, (body_center_x - 25, 165), (body_center_x - 55, 300), 3)
    pygame.draw.line(screen, GREY, (body_center_x - 55, 300), (body_center_x - 25, 475), 3)

    # Brust/Bauch Vorderlinie
    pygame.draw.line(screen, GREY, (body_center_x + 15, 170), (body_center_x + 60, 255), 3)
    pygame.draw.line(screen, GREY, (body_center_x + 60, 255), (body_center_x + 35, 360), 3)
    pygame.draw.line(screen, GREY, (body_center_x + 35, 360), (body_center_x + 25, 475), 3)

    # Bein symbolisch
    pygame.draw.line(screen, GREY, (body_center_x - 10, 475), (body_center_x - 35, 590), 3)
    pygame.draw.line(screen, GREY, (body_center_x + 20, 475), (body_center_x + 65, 590), 3)

    # Arm symbolisch
    pygame.draw.line(screen, GREY, (body_center_x + 35, 230), (body_center_x + 90, 340), 3)
    pygame.draw.line(screen, GREY, (body_center_x + 90, 340), (body_center_x + 70, 430), 3)


def mode_name():
    names = {
        1: "ruhige Resonanz",
        2: "Welle / Auf und Ab",
        3: "Enge / Druck",
        4: "Weite / Öffnung",
        5: "Kreisel / Wirbel",
    }
    return names.get(mode, "unbekannt")


def node_activity(node, t):
    base = node["base"]

    if mode == 1:
        # ruhiges Atmen
        return base * (0.6 + 0.25 * math.sin(t * 1.2))

    if mode == 2:
        # Welle wandert durch Körper
        y = node["pos"][1]
        wave = math.sin(t * 3.0 - y * 0.035)
        return base * (0.55 + 0.45 * wave)

    if mode == 3:
        # Enge in Brust/Hals
        y = node["pos"][1]
        center_y = 235
        pressure = math.exp(-((y - center_y) ** 2) / 9000)
        pulse = 0.75 + 0.25 * math.sin(t * 5.0)
        return pressure * pulse

    if mode == 4:
        # Weite vom Brustraum nach außen
        y = node["pos"][1]
        center_y = 260
        openness = math.exp(-((y - center_y) ** 2) / 16000)
        pulse = 0.6 + 0.4 * math.sin(t * 1.8)
        return openness * pulse

    if mode == 5:
        # Wirbel, stärker in Bauch/Brust
        y = node["pos"][1]
        center_y = 320
        swirl = math.exp(-((y - center_y) ** 2) / 18000)
        pulse = 0.65 + 0.35 * math.sin(t * 4.0)
        return swirl * pulse

    return base


def draw_resonance_field(t):
    # weicher Glow um Körperachse
    for node in resonance_nodes:
        x, y = node["pos"]
        a = node_activity(node, t) * intensity
        radius = int(25 + 80 * abs(a))

        if mode == 3:
            color_inner = mix_color(VIOLET, RED, abs(a))
            color_outer = mix_color(BLUE, VIOLET, 0.6)
        elif mode == 4:
            color_inner = mix_color(CYAN, GREEN, abs(a))
            color_outer = mix_color(BLUE, CYAN, 0.6)
        elif mode == 5:
            color_inner = mix_color(PINK, ORANGE, abs(a))
            color_outer = mix_color(VIOLET, PINK, 0.6)
        else:
            color_inner = mix_color(BLUE, CYAN, abs(a))
            color_outer = mix_color(DARK_GREY, BLUE, 0.5)

        # Glow-Kreise transparent simuliert durch dunklere größere Kreise
        for k in range(5, 0, -1):
            rr = int(radius * k / 5)
            col = mix_color(color_outer, color_inner, 1 - k / 6)
            pygame.draw.circle(screen, col, (int(x), int(y)), rr, 1)

        pygame.draw.circle(screen, color_inner, (int(x), int(y)), max(4, int(8 + 14 * abs(a))))


def draw_particles(t):
    for p in particles:
        phase = p["phase"]

        if mode == 1:
            dx = math.sin(t * p["speed"] + phase) * 12 * intensity
            dy = math.cos(t * p["speed"] * 0.8 + phase) * 5 * intensity

        elif mode == 2:
            dx = math.sin(t * 3.0 - p["y"] * 0.04 + phase) * 35 * intensity
            dy = math.sin(t * 2.0 + phase) * 8 * intensity

        elif mode == 3:
            # nach innen ziehen, Richtung Körperachse
            pull = (body_center_x - p["x"]) * 0.35 * intensity
            dx = pull + math.sin(t * 5.0 + phase) * 5
            dy = math.cos(t * 4.0 + phase) * 4

        elif mode == 4:
            # nach außen weiten
            push = (p["x"] - body_center_x) * 0.45 * intensity
            dx = push + math.sin(t * 2.0 + phase) * 12
            dy = math.sin(t * 1.5 + phase) * 6

        elif mode == 5:
            # Wirbel um Brust/Bauch
            cx, cy = body_center_x, 320
            angle = math.atan2(p["y"] - cy, p["x"] - cx)
            dist = math.hypot(p["x"] - cx, p["y"] - cy)
            swirl_angle = angle + t * 1.8 * intensity
            dx = math.cos(swirl_angle) * min(55, dist * 0.28)
            dy = math.sin(swirl_angle) * min(55, dist * 0.28)
        else:
            dx, dy = 0, 0

        x = int(p["x"] + dx)
        y = int(p["y"] + dy)

        # Nur grob im Körperbereich anzeigen
        if body_center_x - 120 < x < body_center_x + 150 and 90 < y < 570:
            val = (math.sin(t * 2 + phase) + 1) / 2

            if mode == 3:
                color = mix_color(VIOLET, RED, val)
            elif mode == 4:
                color = mix_color(CYAN, GREEN, val)
            elif mode == 5:
                color = mix_color(PINK, ORANGE, val)
            else:
                color = mix_color(BLUE, CYAN, val)

            pygame.draw.circle(screen, color, (x, y), int(p["r"]))


def draw_wave_lines(t):
    # Haupt-Wellenlinie durch den Körper
    points = []
    for y in range(130, 510, 8):
        if mode == 2:
            amp = 38 * intensity
            x = body_center_x + math.sin(t * 3.2 - y * 0.035) * amp
        elif mode == 3:
            amp = 14 * intensity
            x = body_center_x + math.sin(t * 6.0 - y * 0.05) * amp
        elif mode == 4:
            amp = 55 * intensity
            x = body_center_x + math.sin(t * 1.7 - y * 0.025) * amp
        elif mode == 5:
            amp = 45 * intensity
            x = body_center_x + math.sin(t * 4.0 - y * 0.04) * amp
        else:
            amp = 20 * intensity
            x = body_center_x + math.sin(t * 1.4 - y * 0.025) * amp

        points.append((int(x), y))

    if len(points) > 1:
        pygame.draw.lines(screen, WHITE, False, points, 2)

    # zweite feine Gegenlinie
    points2 = []
    for y in range(130, 510, 10):
        x = body_center_x + math.cos(t * 2.0 - y * 0.032) * (22 + 25 * intensity)
        points2.append((int(x), y))

    pygame.draw.lines(screen, (130, 190, 255), False, points2, 1)


def draw_pressure_bands(t):
    # horizontale Bänder: Weite/Enge
    for i, y in enumerate(range(160, 500, 35)):
        phase = t * 2.5 + i * 0.7

        if mode == 3:
            # Enge: Bänder ziehen nach innen
            half_width = int(70 - 35 * intensity * (0.5 + 0.5 * math.sin(phase)))
            color = mix_color(VIOLET, RED, 0.7)
        elif mode == 4:
            # Weite: Bänder gehen nach außen
            half_width = int(55 + 65 * intensity * (0.5 + 0.5 * math.sin(phase)))
            color = mix_color(BLUE, CYAN, 0.8)
        else:
            half_width = int(55 + 25 * math.sin(phase) * intensity)
            color = (80, 120, 170)

        pygame.draw.line(
            screen,
            color,
            (body_center_x - half_width, y),
            (body_center_x + half_width, y),
            1
        )


def draw_labels():
    draw_text("Zero-Lumi Leibresonanz — Seitenansicht", 25, 22, WHITE)
    draw_text(f"Modus: {mode} — {mode_name()}", 25, 55, CYAN)
    draw_text(f"Intensität: {int(intensity * 100)}%", 25, 85, WHITE)

    draw_text("Steuerung:", 25, HEIGHT - 150, WHITE, small_font)
    draw_text("1 ruhig | 2 Welle | 3 Enge | 4 Weite | 5 Kreisel", 25, HEIGHT - 125, WHITE, small_font)
    draw_text("SPACE Modus wechseln | ↑/↓ Intensität | ESC Ende", 25, HEIGHT - 100, WHITE, small_font)

    # kleine Legende rechts
    x = WIDTH - 320
    y = 35
    draw_text("Modell-Legende", x, y, WHITE)
    draw_text("Wellenlinie = bewegte Leibresonanz", x, y + 30, CYAN, small_font)
    draw_text("Punkte = innere Aktivierungs-Spuren", x, y + 52, WHITE, small_font)
    draw_text("Bänder = Enge / Weite", x, y + 74, WHITE, small_font)
    draw_text("Glow = Intensität im Körperraum", x, y + 96, WHITE, small_font)


def draw_axis_labels():
    # Körperzonen links
    for node in resonance_nodes:
        x, y = node["pos"]
        draw_text(node["name"], body_center_x - 210, y - 10, GREY, small_font)
        pygame.draw.line(screen, DARK_GREY, (body_center_x - 150, y), (body_center_x - 70, y), 1)


running = True

while running:
    dt = clock.tick(60) / 1000.0
    time_value += dt

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
                intensity = min(1.5, intensity + 0.08)

            if event.key == pygame.K_DOWN:
                intensity = max(0.05, intensity - 0.08)

    screen.fill(BLACK)

    # Hintergrundraster sehr subtil
    for y in range(80, HEIGHT, 40):
        pygame.draw.line(screen, (15, 20, 32), (0, y), (WIDTH, y), 1)

    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, (12, 16, 26), (x, 0), (x, HEIGHT), 1)

    draw_axis_labels()
    draw_pressure_bands(time_value)
    draw_resonance_field(time_value)
    draw_particles(time_value)
    draw_wave_lines(time_value)
    draw_body_outline()
    draw_labels()

    pygame.display.flip()

pygame.quit()