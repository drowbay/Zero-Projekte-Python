import pygame
import math
import random

# ============================================================
# Zero-Lumi Zustandsfaser-Netz — animierte Poster-Variante
# ------------------------------------------------------------
# Stil:
# - kosmisches Zustandsnetz
# - pulsierende Knoten
# - leuchtende Verbindungsfasern
# - rechte Entwicklungsstufen
# - untere Zeitlinie
# - als Theorie-Experiment / Visualisierung
#
# Steuerung:
#   SPACE = Pause
#   UP/DOWN = Intensität hoch/runter
#   S = Screenshot speichern
#   ESC = Ende
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zero-Lumi — Zustandsfaser-Netz animiert")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("serif", 34, bold=True)
font_mid = pygame.font.SysFont("serif", 20, bold=True)
font_small = pygame.font.SysFont("serif", 15)

# ------------------------------------------------------------
# Farben
# ------------------------------------------------------------

BLACK = (4, 6, 16)
WHITE = (245, 245, 255)
SOFT = (180, 190, 230)
GOLD = (255, 210, 120)
BLUE = (90, 140, 255)
CYAN = (90, 230, 255)
VIOLET = (170, 110, 255)
PINK = (255, 120, 220)
LIME = (170, 255, 120)
DEEP = (20, 24, 50)
DIM = (60, 70, 110)

running = True
paused = False
t = 0.0
intensity = 1.0

# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------

def mix(a, b, k):
    k = max(0.0, min(1.0, k))
    return (
        int(a[0] + (b[0] - a[0]) * k),
        int(a[1] + (b[1] - a[1]) * k),
        int(a[2] + (b[2] - a[2]) * k),
    )

def draw_text(text, x, y, color=WHITE, font=font_small):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def point_lerp(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)

# ------------------------------------------------------------
# Hintergrundsterne
# ------------------------------------------------------------

stars = []
random.seed(42)
for _ in range(170):
    stars.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "r": random.choice([1, 1, 1, 2]),
        "phase": random.uniform(0, math.tau)
    })

# ------------------------------------------------------------
# Netzwerkstruktur
# ------------------------------------------------------------

network_offset_x = -90
network_offset_y = 20

nodes = [
    {"name": "U0", "x": 120, "y": 460, "size": 50, "phase": 0.2, "color": GOLD},
    {"name": "N1", "x": 220, "y": 300, "size": 26, "phase": 1.2, "color": VIOLET},
    {"name": "N2", "x": 320, "y": 220, "size": 22, "phase": 2.1, "color": CYAN},
    {"name": "N3", "x": 420, "y": 250, "size": 30, "phase": 0.4, "color": PINK},
    {"name": "N4", "x": 500, "y": 170, "size": 20, "phase": 1.7, "color": GOLD},
    {"name": "N5", "x": 560, "y": 260, "size": 22, "phase": 2.8, "color": CYAN},
    {"name": "N6", "x": 460, "y": 380, "size": 34, "phase": 0.8, "color": VIOLET},
    {"name": "N7", "x": 300, "y": 420, "size": 24, "phase": 1.0, "color": CYAN},
    {"name": "N8", "x": 580, "y": 420, "size": 26, "phase": 2.4, "color": PINK},
    {"name": "N9", "x": 670, "y": 330, "size": 28, "phase": 0.5, "color": GOLD},
    {"name": "N10", "x": 710, "y": 230, "size": 20, "phase": 2.0, "color": CYAN},
    {"name": "N11", "x": 660, "y": 510, "size": 16, "phase": 1.4, "color": VIOLET},
]

connections = [
    (0, 1), (0, 7), (1, 2), (1, 7), (2, 3), (2, 4), (3, 4), (3, 5),
    (3, 6), (4, 5), (5, 9), (6, 7), (6, 8), (7, 6), (8, 9), (8, 11),
    (9, 10), (5, 10), (6, 9), (3, 7), (2, 6), (5, 8)
]

# ------------------------------------------------------------
# Rechte Seitenstufen
# ------------------------------------------------------------

stages = [
    ("1. TIEFE\nZUSTANDSSTRUKTUR", "Ursprüngliche Ordnung\njenseits von Raum und Zeit."),
    ("2. FELDER &\nFREIHEITSGRADE", "Dynamische Felder,\nPotentiale, Wechselwirkungen."),
    ("3. HILBERT-\nRÄUME", "Mathematische Räume\naller Möglichkeiten."),
    ("4. QUANTEN-\nZUSTÄNDE", "Superposition,\nWahrscheinlichkeit, Kopplung."),
    ("5. SICHTBARE\nMATERIE", "Teilchen, Atome,\nSterne, Leben, Bewusstsein."),
]

# ------------------------------------------------------------
# Untere Zeitlinie
# ------------------------------------------------------------

timeline = [
    "Potenzial",
    "Fluktuation",
    "Interferenz",
    "Musterbildung",
    "Struktur",
    "Komplexität",
    "Bewusstes\nErleben"
]

# ------------------------------------------------------------
# Zeichnen
# ------------------------------------------------------------

def draw_psi_field(time_value):
    # --------------------------------------------------------
    # ψ-Feld: Zustandswelle / Möglichkeitswelle im Faser-Netz
    # --------------------------------------------------------
    # Diese Welle ist kein Wasser und kein normales Licht,
    # sondern Symbol für:
    # ψ(t) = Zustand + Phase + Möglichkeit + Dynamik
    # --------------------------------------------------------

    psi_color = mix(VIOLET, CYAN, 0.5 + 0.5 * math.sin(time_value * 0.8))

    # Große ψ-Welle durch das Hauptnetz
    points = []
    for x in range(80, 820, 6):
        envelope = math.exp(-((x - 430) ** 2) / (2 * 260 ** 2))
        y = 330
        y += math.sin(time_value * 2.2 + x * 0.025) * 55 * envelope
        y += math.sin(time_value * 4.1 - x * 0.045) * 14 * envelope
        points.append((x, int(y)))

    # Glow-Schichten
    pygame.draw.lines(screen, mix(DEEP, psi_color, 0.55), False, points, 9)
    pygame.draw.lines(screen, mix(psi_color, WHITE, 0.25), False, points, 4)
    pygame.draw.lines(screen, WHITE, False, points, 1)

    # ψ-Partikel auf der Welle
    for i in range(9):
        u = (time_value * 0.09 + i / 9) % 1.0
        idx = int(u * (len(points) - 1))
        x, y = points[idx]
        pulse = 0.5 + 0.5 * math.sin(time_value * 5 + i)
        r = int(4 + 5 * pulse)
        pygame.draw.circle(screen, mix(psi_color, WHITE, pulse), (x, y), r, 1)
        pygame.draw.circle(screen, WHITE, (x, y), 2)

    # Formel oben im Bild
    draw_text("ψ(t) → K_L → G_R(t) → A_R", 410, 38, mix(WHITE, CYAN, 0.25), font_mid)
    draw_text("Zustandswelle → Kontaktlamelle → Grenzresonanz → Abdruck", 380, 64, SOFT, font_small)

    # ψ-Symbol links im Netz
    draw_text("ψ", 770, 145, mix(WHITE, VIOLET, 0.25), font_big)
    draw_text("Zustandswelle", 755, 185, SOFT, font_small)

    # kleine Dirac-Notation
    draw_text("|ψ⟩ = α|0⟩ + β|1⟩", 705, 210, mix(WHITE, CYAN, 0.25), font_small)

def draw_background(time_value):
    # Verlauf
    for y in range(HEIGHT):
        k = y / HEIGHT
        col = mix((4, 6, 18), (16, 10, 38), k)
        pygame.draw.line(screen, col, (0, y), (WIDTH, y))

    # Sterne
    for s in stars:
        blink = 0.5 + 0.5 * math.sin(time_value * 0.7 + s["phase"])
        color = mix((80, 90, 140), (220, 230, 255), blink)
        pygame.draw.circle(screen, color, (s["x"], s["y"]), s["r"])

def node_screen_pos(node, time_value):
    # sanftes "lebendiges" Driften
    wobble_x = math.sin(time_value * 0.5 + node["phase"]) * 6
    wobble_y = math.cos(time_value * 0.4 + node["phase"] * 1.2) * 5
    return (
        int(node["x"] + network_offset_x + wobble_x),
        int(node["y"] + network_offset_y + wobble_y)
    )

def draw_connections(time_value):
    # Fasern
    for idx, (a, b) in enumerate(connections):
        pa = node_screen_pos(nodes[a], time_value)
        pb = node_screen_pos(nodes[b], time_value)

        base_col = mix(VIOLET, CYAN, (idx % 10) / 10)
        pygame.draw.line(screen, mix(DEEP, base_col, 0.45), pa, pb, 1)

        # fließende Energiepunkte
        for j in range(2):
            u = (0.15 * j + 0.12 * idx + time_value * 0.12 * intensity) % 1.0
            x, y = point_lerp(pa, pb, u)
            glow = 0.5 + 0.5 * math.sin(time_value * 4 + idx + j)
            col = mix(base_col, WHITE, glow)
            pygame.draw.circle(screen, col, (int(x), int(y)), 2)

        # leichte Doppelstruktur
        mid = point_lerp(pa, pb, 0.5)
        offset = math.sin(time_value * 1.3 + idx) * 6
        pygame.draw.circle(screen, mix(base_col, WHITE, 0.15), (int(mid[0]), int(mid[1] + offset)), 1)

def draw_nodes(time_value):
    for i, node in enumerate(nodes):
        x, y = node_screen_pos(node, time_value)
        pulse = 0.5 + 0.5 * math.sin(time_value * 2.2 + node["phase"])
        r = int(node["size"] * (0.78 + 0.18 * pulse * intensity))
        core_color = mix(node["color"], WHITE, 0.35 + 0.4 * pulse)

        # Glow-Ringe
        for k in range(5, 0, -1):
            rr = r + k * 8
            col = mix(DEEP, node["color"], 0.08 * k)
            pygame.draw.circle(screen, col, (x, y), rr, 1)

        # Kern
        pygame.draw.circle(screen, core_color, (x, y), max(3, r // 3), 0)
        pygame.draw.circle(screen, mix(core_color, WHITE, 0.5), (x, y), max(2, r // 6), 0)

        # Orbit-Partikel
        for p in range(5):
            ang = time_value * (0.6 + 0.08 * p) + node["phase"] + p * 1.2
            orbit_r = r + 8 + p * 3
            ox = x + math.cos(ang) * orbit_r
            oy = y + math.sin(ang) * orbit_r
            pygame.draw.circle(screen, mix(node["color"], WHITE, 0.4), (int(ox), int(oy)), 1)

        # bei großem Start-Knoten kleine "Galaxie"
        if i == 0:
            for p in range(12):
                ang = time_value * 0.5 + p * 0.52
                orbit_r = 10 + p * 3
                ox = x + math.cos(ang) * orbit_r
                oy = y + math.sin(ang) * orbit_r * 0.7
                pygame.draw.circle(screen, mix(GOLD, WHITE, 0.5), (int(ox), int(oy)), 1)

def draw_right_panel(time_value):
    x0 = 980
    y0 = 92

    active_stage = int((time_value * 0.5) % len(stages))

    # vertikale Verbindung
    pygame.draw.line(screen, mix(DIM, CYAN, 0.35), (1060, 115), (1060, 490), 1)

    for i, (title, desc) in enumerate(stages):
        y = y0 + i * 87
        active = (i == active_stage)
        pulse = 0.5 + 0.5 * math.sin(time_value * 3 + i)

        circle_col = mix(VIOLET, CYAN, i / max(1, len(stages)-1))
        if active:
            circle_col = mix(circle_col, WHITE, 0.45 + 0.25 * pulse)

        # Symbol
        pygame.draw.circle(screen, mix(DEEP, circle_col, 0.35), (930, y + 25), 26, 1)
        pygame.draw.circle(screen, circle_col, (930, y + 25), 8, 1)

        # Mini-Icon innen
        if i == 0:
            draw_text("∞", 922, y + 12, circle_col, font_mid)
        elif i == 1:
            pygame.draw.line(screen, circle_col, (915, y + 25), (945, y + 25), 1)
            pygame.draw.line(screen, circle_col, (930, y + 10), (930, y + 40), 1)
        elif i == 2:
            pygame.draw.circle(screen, circle_col, (930, y + 25), 14, 1)
            pygame.draw.line(screen, circle_col, (916, y + 25), (944, y + 25), 1)
        elif i == 3:
            for a in range(3):
                ang = time_value + a * 2.1
                ox = 930 + math.cos(ang) * 12
                oy = y + 25 + math.sin(ang) * 12
                pygame.draw.circle(screen, circle_col, (int(ox), int(oy)), 2)
        else:
            pygame.draw.circle(screen, circle_col, (930, y + 25), 3, 0)
            pygame.draw.circle(screen, circle_col, (918, y + 18), 2, 0)
            pygame.draw.circle(screen, circle_col, (942, y + 18), 2, 0)

        # Text
        title_lines = title.split("\n")
        desc_lines = desc.split("\n")

        for li, line in enumerate(title_lines):
            draw_text(line, x0, y + li * 18, mix(WHITE, circle_col, 0.25 if not active else 0.45), font_small)

        for li, line in enumerate(desc_lines):
            draw_text(line, x0, y + 38 + li * 16, SOFT if not active else mix(WHITE, circle_col, 0.15), font_small)

def draw_timeline(time_value):
    base_y = 635
    start_x = 180
    spacing = 118

    progress = (time_value * 0.35) % len(timeline)
    active_idx = int(progress)

    draw_text("ZEIT WIRD DURCH DYNAMIK SICHTBAR", 330, 570, mix(GOLD, WHITE, 0.18), font_mid)
    draw_text("Veränderung von Zuständen erzeugt Ordnung in Sequenz — das Erleben von Zeit.", 265, 595, SOFT, font_small)

    pygame.draw.line(screen, mix(DIM, GOLD, 0.4), (start_x, base_y), (start_x + spacing * (len(timeline)-1), base_y), 1)

    for i, label in enumerate(timeline):
        x = start_x + i * spacing
        pulse = 0.5 + 0.5 * math.sin(time_value * 3 + i)
        active = (i == active_idx)

        col = mix(CYAN, GOLD, i / max(1, len(timeline)-1))
        if active:
            col = mix(col, WHITE, 0.45 + 0.25 * pulse)

        # Kreis / Stadium
        pygame.draw.circle(screen, mix(DEEP, col, 0.3), (x, base_y), 28, 1)
        pygame.draw.circle(screen, col, (x, base_y), 8, 1)

        # Innenmini-Symbol
        inner_r = 3 + int(3 * pulse) if active else 3
        pygame.draw.circle(screen, col, (x, base_y), inner_r, 0)

        # kleiner Energielauf
        if i < len(timeline)-1:
            step_u = (progress - i)
            if 0 <= step_u < 1:
                px = x + step_u * spacing
                pygame.draw.circle(screen, mix(col, WHITE, 0.5), (int(px), base_y), 3)

        # Label
        parts = label.split("\n")
        for li, part in enumerate(parts):
            draw_text(part, x - 36, base_y + 36 + li * 14, SOFT if not active else mix(WHITE, col, 0.18), font_small)

    draw_text("ZEIT", 602, 690, GOLD, font_small)

def draw_title_block():
    draw_text("ZUSTANDSFASER-NETZ", 45, 36, WHITE, font_big)
    draw_text("Alles Existierende ist ein Ausdruck tiefer Zustände.", 45, 74, SOFT, font_small)
    draw_text("Universum in einer Ader.", 45, 94, SOFT, font_small)

    draw_text("ENERGIEFLUSS", 35, 165, mix(GOLD, WHITE, 0.2), font_small)
    draw_text("Information trägt,", 35, 183, SOFT, font_small)
    draw_text("Ordnung entsteht.", 35, 199, SOFT, font_small)

    draw_text("UNIVERSUM\nIN EINER ADER", 36, 498, mix(WHITE, CYAN, 0.16), font_small)
    draw_text("Lokale Raumzeiten\nschwingen eingebettet\nim Zustandsfaser-Netz.", 36, 535, SOFT, font_small)

    draw_text("FELDRESONANZ", 335, 498, mix(WHITE, CYAN, 0.18), font_small)
    draw_text("Felder koppeln.\nInformation interferiert.\nMuster entstehen.", 335, 535, SOFT, font_small)

    draw_text("ZUSTANDSFASER", 705, 72, mix(WHITE, CYAN, 0.2), font_small)
    draw_text("Träger tiefer Zustände\nund Möglichkeiten.", 705, 90, SOFT, font_small)

    quote = "“Nicht die Dinge selbst\nsind die Grundlage,\nsondern die Zustände,\naus denen sie hervortreten.”"
    q_lines = quote.split("\n")
    for i, line in enumerate(q_lines):
        draw_text(line, 1015, 560 + i * 16, mix(WHITE, PINK, 0.15), font_small)

def save_screenshot():
    filename = "zustandsfaser_animiert_screenshot.png"
    pygame.image.save(screen, filename)
    print(f"Screenshot gespeichert als {filename}")

# ------------------------------------------------------------
# Hauptschleife
# ------------------------------------------------------------

while running:
    dt = clock.tick(60) / 1000.0
    if not paused:
        t += dt * intensity

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_UP:
                intensity = min(2.0, intensity + 0.1)
            elif event.key == pygame.K_DOWN:
                intensity = max(0.2, intensity - 0.1)
            elif event.key == pygame.K_s:
                save_screenshot()

    draw_background(t)
    draw_connections(t)
    draw_nodes(t)
    draw_title_block()
    draw_right_panel(t)
    draw_timeline(t)

    draw_text("SPACE Pause | UP/DOWN Intensität | S Screenshot | ESC Ende", 20, 700, mix(WHITE, CYAN, 0.2), font_small)

    pygame.display.flip()

pygame.quit()