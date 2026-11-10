import pygame
import random
import math
import time

# ==========================================================
# TIRXY WORKSPACE LIVE SIM
# Aus unseren Arbeitsbereich-Themen:
# ?-A-B, Horizont, Wasser, Mensch-Feld, KI-Schaltkreise,
# Erinnerung, App/Engine, Spinfoam/Links/Wedges
# ==========================================================

pygame.init()

WIDTH, HEIGHT = 1100, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TIRXY Workspace Live Simulation")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 18)
SMALL = pygame.font.SysFont("arial", 14)
BIG = pygame.font.SysFont("arial", 28, bold=True)

BG = (6, 8, 18)
WHITE = (235, 240, 255)
DIM = (125, 135, 160)

CYAN = (90, 230, 255)
BLUE = (70, 150, 255)
GOLD = (255, 210, 90)
PINK = (255, 110, 190)
GREEN = (120, 255, 160)
VIOLET = (180, 120, 255)
RED = (255, 90, 90)
TEAL = (80, 230, 200)

# ----------------------------------------------------------
# Globale Zustände
# ----------------------------------------------------------
time_factor = 1.0
paused = False

horizon_strength = 0.65       # kosmischer Informationshorizont
field_strength = 0.55         # freies Feld
water_order = 0.55            # Wasserstoffbrücken / Wasserordnung
human_field = 0.55            # G_body / gefühlte Feldstärke
ai_circuit = 0.55             # Bedeutungs-/Schaltkreisaktivität
memory_trace = 0.45           # Erinnerungsspur
engine_state = 0.45           # App/Engine/Handlungszustand
unknown_potential = 0.50      # ?+

noise = 0.25
fatigue = 0.25
attention = 0.65
meaning = 0.70

particles = []
links = []
history = []

MAX_HISTORY = 260

# ----------------------------------------------------------
# Nodes: Name, Position, Farbe, Wert-Key
# ----------------------------------------------------------
nodes = {
    "unknown_left": {
        "label": "?₋ / Vor-Unbekannt",
        "x": 105, "y": 350, "color": VIOLET,
        "value": lambda: horizon_strength
    },
    "horizon": {
        "label": "?₀ Horizont / Rand",
        "x": 245, "y": 210, "color": BLUE,
        "value": lambda: horizon_strength
    },
    "field": {
        "label": "A Freies Feld",
        "x": 430, "y": 210, "color": CYAN,
        "value": lambda: field_strength
    },
    "water": {
        "label": "Wasser / H₂O-Brücken",
        "x": 610, "y": 160, "color": TEAL,
        "value": lambda: water_order
    },
    "human": {
        "label": "Mensch / G_body",
        "x": 610, "y": 310, "color": PINK,
        "value": lambda: human_field
    },
    "ai": {
        "label": "KI / Schaltkreise",
        "x": 610, "y": 465, "color": VIOLET,
        "value": lambda: ai_circuit
    },
    "event": {
        "label": "B Ereignis",
        "x": 790, "y": 310, "color": GOLD,
        "value": lambda: (water_order + human_field + ai_circuit + field_strength) / 4
    },
    "memory": {
        "label": "?₁ Erinnerung/Hypothese",
        "x": 950, "y": 235, "color": GREEN,
        "value": lambda: memory_trace
    },
    "engine": {
        "label": "App / Engine / Handlung",
        "x": 950, "y": 390, "color": CYAN,
        "value": lambda: engine_state
    },
    "unknown_right": {
        "label": "?₊ Potenzial",
        "x": 1030, "y": 560, "color": GOLD,
        "value": lambda: unknown_potential
    },
}

# Hauptverbindungen
connections = [
    ("unknown_left", "horizon"),
    ("horizon", "field"),
    ("field", "water"),
    ("field", "human"),
    ("field", "ai"),
    ("water", "event"),
    ("human", "event"),
    ("ai", "event"),
    ("event", "memory"),
    ("memory", "engine"),
    ("engine", "unknown_right"),
    ("unknown_right", "unknown_left"),
]

# ----------------------------------------------------------
# Hilfsfunktionen
# ----------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def draw_text(text, x, y, color=WHITE, font=FONT, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
        screen.blit(surf, rect)
    else:
        screen.blit(surf, (x, y))

def add_particle(x, y, color, amount=12, power=2.2):
    for _ in range(amount):
        ang = random.random() * math.tau
        speed = random.uniform(0.4, power)
        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(ang) * speed,
            "vy": math.sin(ang) * speed,
            "life": random.uniform(30, 90),
            "size": random.uniform(2, 5),
            "color": color
        })

def update_particles():
    global particles
    for p in particles:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vx"] *= 0.985
        p["vy"] *= 0.985
        p["life"] -= 1
    particles = [p for p in particles if p["life"] > 0]

def draw_particles():
    for p in particles:
        alpha = clamp(p["life"] / 90)
        color = tuple(int(c * alpha) for c in p["color"])
        pygame.draw.circle(screen, color, (int(p["x"]), int(p["y"])), int(p["size"]))

def node_value(name):
    return clamp(nodes[name]["value"]())

def draw_node(name):
    n = nodes[name]
    x, y = n["x"], n["y"]
    color = n["color"]
    value = node_value(name)

    radius = 44 + int(value * 18)

    # Glow
    for i in range(4):
        r = radius + 22 - i * 6
        glow = tuple(int(c * (0.055 + i * 0.025)) for c in color)
        pygame.draw.circle(screen, glow, (x, y), r)

    pygame.draw.circle(screen, (16, 20, 38), (x, y), radius)
    pygame.draw.circle(screen, color, (x, y), radius, 3)

    inner = int(radius * value)
    if inner > 3:
        pygame.draw.circle(screen, color, (x, y), inner)

    draw_text(n["label"], x, y + radius + 20, WHITE, SMALL, center=True)
    draw_text(f"{value:.2f}", x, y - 7, BG if value > 0.55 else WHITE, SMALL, center=True)

def draw_connection(a, b, frame):
    na = nodes[a]
    nb = nodes[b]
    va = node_value(a)
    vb = node_value(b)
    strength = (va + vb) / 2

    x1, y1 = na["x"], na["y"]
    x2, y2 = nb["x"], nb["y"]

    color = tuple(int((na["color"][i] + nb["color"][i]) / 2) for i in range(3))
    width = max(1, int(1 + strength * 5))

    pygame.draw.line(screen, color, (x1, y1), (x2, y2), width)

    # wandernder Puls
    k = (math.sin(frame * 0.035 + x1 * 0.01) + 1) / 2
    px = x1 + (x2 - x1) * k
    py = y1 + (y2 - y1) * k

    pygame.draw.circle(screen, WHITE, (int(px), int(py)), 4 + int(strength * 4))

def draw_bar(label, value, x, y, w, h, color):
    pygame.draw.rect(screen, (24, 28, 48), (x, y, w, h), border_radius=8)
    pygame.draw.rect(screen, color, (x, y, int(w * clamp(value)), h), border_radius=8)
    pygame.draw.rect(screen, (70, 80, 115), (x, y, w, h), 2, border_radius=8)
    draw_text(f"{label}: {value:.2f}", x, y - 20, WHITE, SMALL)

def draw_history():
    if len(history) < 2:
        return

    gx, gy = 75, 635
    gw, gh = 900, 55

    pygame.draw.rect(screen, (16, 20, 38), (gx, gy, gw, gh), border_radius=10)
    pygame.draw.rect(screen, (75, 85, 120), (gx, gy, gw, gh), 2, border_radius=10)

    points = []
    for i, v in enumerate(history):
        x = gx + int((i / MAX_HISTORY) * gw)
        y = gy + gh - int(v * gh)
        points.append((x, y))

    pygame.draw.lines(screen, GOLD, False, points, 2)
    draw_text("Emergenz-Verlauf: Ereignisstärke aus Feld + Wasser + Mensch + KI", gx, gy - 22, DIM, SMALL)

def draw_horizon_circle(frame):
    # Kreis links als "Informationshorizont"
    cx, cy = 245, 210
    base = 82 + int(18 * math.sin(frame * 0.025))
    for i in range(3):
        pygame.draw.circle(screen, (40, 90, 180), (cx, cy), base + i * 18, 1)

def draw_water_molecules(frame):
    # kleine H2O-Tanzpunkte um Wasser-Node
    cx, cy = nodes["water"]["x"], nodes["water"]["y"]
    for i in range(18):
        a = i * math.tau / 18 + frame * 0.025
        r = 80 + 12 * math.sin(frame * 0.035 + i)
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r * 0.45
        pygame.draw.circle(screen, TEAL, (int(x), int(y)), 3)
        if i % 2 == 0:
            x2 = cx + math.cos(a + 0.35) * (r * 0.85)
            y2 = cy + math.sin(a + 0.35) * (r * 0.45)
            pygame.draw.line(screen, (60, 180, 180), (x, y), (x2, y2), 1)

def draw_human_field(frame):
    cx, cy = nodes["human"]["x"], nodes["human"]["y"]
    for i in range(7):
        r = 45 + i * 11 + 5 * math.sin(frame * 0.04 + i)
        pygame.draw.ellipse(screen, (75, 30, 75), (cx - r, cy - r*0.7, r*2, r*1.4), 1)

def draw_ai_circuit(frame):
    cx, cy = nodes["ai"]["x"], nodes["ai"]["y"]
    for i in range(16):
        x = cx - 90 + (i % 4) * 60
        y = cy - 65 + (i // 4) * 42
        pygame.draw.circle(screen, VIOLET, (x, y), 3)
        if i % 4 != 3:
            pygame.draw.line(screen, (95, 55, 145), (x, y), (x + 60, y), 1)
        if i < 12:
            pygame.draw.line(screen, (95, 55, 145), (x, y), (x, y + 42), 1)

    # Datenpuls
    p = frame % 16
    x = cx - 90 + (p % 4) * 60
    y = cy - 65 + (p // 4) * 42
    pygame.draw.circle(screen, GOLD, (x, y), 7)

def recompute_emergence():
    return clamp(
        0.18 * horizon_strength +
        0.18 * field_strength +
        0.16 * water_order +
        0.16 * human_field +
        0.16 * ai_circuit +
        0.08 * memory_trace +
        0.08 * engine_state
    )

def reset_values():
    global horizon_strength, field_strength, water_order, human_field
    global ai_circuit, memory_trace, engine_state, unknown_potential
    global noise, fatigue, attention, meaning, history

    horizon_strength = 0.65
    field_strength = 0.55
    water_order = 0.55
    human_field = 0.55
    ai_circuit = 0.55
    memory_trace = 0.45
    engine_state = 0.45
    unknown_potential = 0.50
    noise = 0.25
    fatigue = 0.25
    attention = 0.65
    meaning = 0.70
    history = []

# ----------------------------------------------------------
# Main Loop
# ----------------------------------------------------------
running = True
frame = 0
last_random_pulse = time.time()

while running:
    dt = clock.tick(60) / 1000.0 * time_factor
    frame += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_p:
                paused = not paused

            if event.key == pygame.K_r:
                reset_values()

            # Thema gezielt verstärken
            if event.key == pygame.K_1:
                horizon_strength = clamp(horizon_strength + 0.12)
                add_particle(nodes["horizon"]["x"], nodes["horizon"]["y"], BLUE, 30)

            if event.key == pygame.K_2:
                water_order = clamp(water_order + 0.12)
                add_particle(nodes["water"]["x"], nodes["water"]["y"], TEAL, 30)

            if event.key == pygame.K_3:
                human_field = clamp(human_field + 0.12)
                add_particle(nodes["human"]["x"], nodes["human"]["y"], PINK, 30)

            if event.key == pygame.K_4:
                ai_circuit = clamp(ai_circuit + 0.12)
                add_particle(nodes["ai"]["x"], nodes["ai"]["y"], VIOLET, 30)

            if event.key == pygame.K_5:
                memory_trace = clamp(memory_trace + 0.14)
                add_particle(nodes["memory"]["x"], nodes["memory"]["y"], GREEN, 30)

            if event.key == pygame.K_6:
                engine_state = clamp(engine_state + 0.14)
                add_particle(nodes["engine"]["x"], nodes["engine"]["y"], CYAN, 30)

            # Aufmerksamkeit / Rauschen / Müdigkeit / Bedeutung
            if event.key == pygame.K_UP:
                attention = clamp(attention + 0.07)
            if event.key == pygame.K_DOWN:
                attention = clamp(attention - 0.07)
            if event.key == pygame.K_RIGHT:
                noise = clamp(noise + 0.07)
            if event.key == pygame.K_LEFT:
                noise = clamp(noise - 0.07)
            if event.key == pygame.K_f:
                fatigue = clamp(fatigue + 0.08)
            if event.key == pygame.K_g:
                fatigue = clamp(fatigue - 0.08)
            if event.key == pygame.K_m:
                meaning = clamp(meaning + 0.08)
            if event.key == pygame.K_n:
                meaning = clamp(meaning - 0.08)

    if not paused:
        # Natürliche Dynamik: alles pulsiert, verblasst, koppelt
        decay = (0.015 + noise * 0.025 + fatigue * 0.02) * dt
        boost = (attention * 0.018 + meaning * 0.015) * dt

        field_strength = clamp(field_strength + boost - decay + 0.006 * math.sin(frame * 0.018))
        water_order = clamp(water_order + 0.010 * math.sin(frame * 0.030) - decay * 0.4)
        human_field = clamp(human_field + 0.012 * math.sin(frame * 0.025 + 1.4) - decay * 0.3)
        ai_circuit = clamp(ai_circuit + 0.014 * math.sin(frame * 0.027 + 2.2) + boost * 0.4 - decay * 0.5)

        emergence = recompute_emergence()

        # Ereignis stärkt Erinnerung/Hypothese
        memory_trace = clamp(memory_trace + emergence * 0.018 * dt - decay * 0.65)

        # Erinnerung/Hypothese stärkt Engine/App-Zustand
        engine_state = clamp(engine_state + memory_trace * 0.014 * dt - decay * 0.4)

        # Engine öffnet neues Potenzial
        unknown_potential = clamp(unknown_potential + engine_state * 0.010 * dt - decay * 0.25)

        # Potenzial beeinflusst wieder Horizont
        horizon_strength = clamp(horizon_strength + unknown_potential * 0.006 * dt - decay * 0.2)

        # Zufällige kreative Pulse
        now = time.time()
        if now - last_random_pulse > random.uniform(2.5, 5.5):
            chosen = random.choice(["water", "human", "ai", "field", "memory", "engine"])
            n = nodes[chosen]
            add_particle(n["x"], n["y"], n["color"], amount=18)
            last_random_pulse = now

        update_particles()

        history.append(emergence)
        if len(history) > MAX_HISTORY:
            history.pop(0)

    # ------------------------------------------------------
    # Zeichnen
    # ------------------------------------------------------
    screen.fill(BG)

    draw_text("TIRXY Workspace Live Simulation", 55, 25, WHITE, BIG)
    draw_text("?₋[?₀] → A → B → [?₁]?₊    |    Unbekanntes → Feld → Ereignis → Erinnerung/Hypothese → Potenzial",
              55, 62, DIM, SMALL)

    draw_text("Tasten: 1 Horizont | 2 Wasser | 3 Mensch | 4 KI | 5 Erinnerung | 6 Engine | ↑↓ Aufmerksamkeit | ←→ Rauschen | F/G Müdigkeit | M/N Bedeutung | P Pause | R Reset",
              55, 88, DIM, SMALL)

    draw_horizon_circle(frame)
    draw_water_molecules(frame)
    draw_human_field(frame)
    draw_ai_circuit(frame)

    for a, b in connections:
        draw_connection(a, b, frame)

    draw_particles()

    for name in nodes:
        draw_node(name)

    # Kontrollleisten
    draw_bar("Aufmerksamkeit", attention, 55, 560, 180, 16, GREEN)
    draw_bar("Rauschen", noise, 275, 560, 180, 16, RED)
    draw_bar("Müdigkeit", fatigue, 495, 560, 180, 16, VIOLET)
    draw_bar("Bedeutung", meaning, 715, 560, 180, 16, GOLD)

    emergence = recompute_emergence()

    # Formelbox
    pygame.draw.rect(screen, (15, 18, 34), (300, 505, 525, 42), border_radius=12)
    pygame.draw.rect(screen, (75, 85, 120), (300, 505, 525, 42), 2, border_radius=12)
    draw_text("𝓔(t) = Φ(𝓕, ψ, G, ?)  →  ?₁ ≈ Φ⁻¹(𝓔, 𝓕, ψ, G)",
              330, 518, WHITE, FONT)

    # Status
    if emergence > 0.72:
        status = "Starke Emergenz: Feld, Wasser, Mensch, KI und Erinnerung koppeln sichtbar."
        color = GOLD
    elif memory_trace > 0.62:
        status = "Die Erinnerungsspur ist stark: Aus B wird wieder eine Hypothese ?₁."
        color = GREEN
    elif noise > 0.65:
        status = "Viel Rauschen: Signale sind da, aber schwer zu trennen."
        color = RED
    else:
        status = "Das System tanzt ruhig: unsichtbare Ordnung bewegt sichtbare Wirklichkeit."
        color = WHITE

    draw_text(status, 55, 605, color, FONT)

    draw_history()

    pygame.display.flip()

pygame.quit()