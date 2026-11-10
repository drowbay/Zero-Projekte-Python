import pygame
import random
import math
import time

# ==========================================================
# Live Simulation: Gedanke -> Kurzzeitgedächtnis -> Spur -> Trigger
# PyDroid / PC kompatibel
# ==========================================================

pygame.init()

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Live Simulation: Gedanke, Erinnerung, Trigger")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 20)
BIG = pygame.font.SysFont("arial", 30, bold=True)
SMALL = pygame.font.SysFont("arial", 16)

# Farben
BG = (8, 10, 22)
WHITE = (235, 240, 255)
DIM = (120, 130, 155)
BLUE = (80, 180, 255)
CYAN = (90, 240, 240)
PINK = (255, 100, 190)
GOLD = (255, 210, 90)
GREEN = (120, 255, 150)
RED = (255, 90, 90)
VIOLET = (170, 120, 255)

# ----------------------------------------------------------
# Zustandswerte
# ----------------------------------------------------------
idea_strength = 0.0       # aktuelle aktive Idee
memory_trace = 0.0        # Spur im Gedächtnis
attention = 0.75          # Aufmerksamkeit
noise = 0.25              # Ablenkung / Rauschen
fatigue = 0.25            # Müdigkeit
meaning = 0.65            # Bedeutung / Emotion
trigger_strength = 0.0    # Trigger, der Erinnerung zurückholt

time_speed = 1.0
paused = False

particles = []
trigger_particles = []

# Graph-Verlauf
history_idea = []
history_trace = []
history_trigger = []
MAX_HISTORY = 320

last_auto_idea = time.time()
last_auto_trigger = time.time()

# ----------------------------------------------------------
# Hilfsfunktionen
# ----------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def draw_text(text, x, y, color=WHITE, font=FONT):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def draw_bar(label, value, x, y, w, h, color):
    pygame.draw.rect(screen, (30, 35, 55), (x, y, w, h), border_radius=8)
    pygame.draw.rect(screen, color, (x, y, int(w * clamp(value)), h), border_radius=8)
    pygame.draw.rect(screen, (80, 90, 120), (x, y, w, h), 2, border_radius=8)
    draw_text(f"{label}: {value:.2f}", x, y - 24, WHITE, SMALL)

def add_particles(kind, amount=20):
    for _ in range(amount):
        angle = random.random() * math.tau
        speed = random.uniform(0.5, 2.6)
        if kind == "idea":
            x, y = 250, 310
            color = CYAN
        elif kind == "memory":
            x, y = 510, 310
            color = GOLD
        else:
            x, y = 760, 310
            color = PINK

        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.uniform(40, 90),
            "color": color,
            "size": random.uniform(2, 5)
        })

def add_trigger_wave():
    for _ in range(45):
        angle = random.random() * math.tau
        speed = random.uniform(1.0, 4.0)
        trigger_particles.append({
            "x": 760,
            "y": 310,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.uniform(30, 70),
            "size": random.uniform(2, 6)
        })

def update_particles():
    global particles, trigger_particles

    for p in particles:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vx"] *= 0.98
        p["vy"] *= 0.98
        p["life"] -= 1

    particles = [p for p in particles if p["life"] > 0]

    for p in trigger_particles:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vx"] *= 0.97
        p["vy"] *= 0.97
        p["life"] -= 1

    trigger_particles = [p for p in trigger_particles if p["life"] > 0]

def draw_particles():
    for p in particles:
        alpha = clamp(p["life"] / 90)
        color = tuple(int(c * alpha) for c in p["color"])
        pygame.draw.circle(screen, color, (int(p["x"]), int(p["y"])), int(p["size"]))

    for p in trigger_particles:
        alpha = clamp(p["life"] / 70)
        color = (int(PINK[0] * alpha), int(PINK[1] * alpha), int(PINK[2] * alpha))
        pygame.draw.circle(screen, color, (int(p["x"]), int(p["y"])), int(p["size"]))

def draw_node(x, y, radius, value, label, color):
    glow_radius = radius + int(35 * value)

    # Glow
    for i in range(4):
        r = glow_radius - i * 8
        if r > radius:
            glow_color = tuple(int(c * (0.10 + 0.04 * i)) for c in color)
            pygame.draw.circle(screen, glow_color, (x, y), r)

    # Hauptkreis
    pygame.draw.circle(screen, (20, 25, 45), (x, y), radius)
    pygame.draw.circle(screen, color, (x, y), radius, 3)

    # Innenkreis nach Wert
    inner = int(radius * clamp(value))
    if inner > 2:
        pygame.draw.circle(screen, color, (x, y), inner)

    draw_text(label, x - 80, y + radius + 20, WHITE, FONT)
    draw_text(f"{value:.2f}", x - 22, y - 10, BG if value > 0.55 else WHITE, FONT)

def draw_connection(x1, y1, x2, y2, value, color):
    width = max(1, int(2 + value * 8))
    pygame.draw.line(screen, color, (x1, y1), (x2, y2), width)

    # wandernder Impuls
    t = pygame.time.get_ticks() / 700.0
    k = (math.sin(t) + 1) / 2
    px = x1 + (x2 - x1) * k
    py = y1 + (y2 - y1) * k
    pygame.draw.circle(screen, WHITE, (int(px), int(py)), 5)

def draw_graph():
    gx, gy = 80, 560
    gw, gh = 840, 70

    pygame.draw.rect(screen, (18, 22, 40), (gx, gy, gw, gh), border_radius=10)
    pygame.draw.rect(screen, (70, 80, 115), (gx, gy, gw, gh), 2, border_radius=10)

    if len(history_idea) < 2:
        return

    def plot_line(hist, color):
        points = []
        for i, v in enumerate(hist):
            x = gx + int(i / MAX_HISTORY * gw)
            y = gy + gh - int(clamp(v) * gh)
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(screen, color, False, points, 2)

    plot_line(history_idea, CYAN)
    plot_line(history_trace, GOLD)
    plot_line(history_trigger, PINK)

    draw_text("Live-Verlauf: Idee = cyan | Gedächtnisspur = gold | Trigger = pink", gx, gy - 24, DIM, SMALL)

def reset_all():
    global idea_strength, memory_trace, trigger_strength
    idea_strength = 0.0
    memory_trace = 0.0
    trigger_strength = 0.0
    history_idea.clear()
    history_trace.clear()
    history_trigger.clear()

# ----------------------------------------------------------
# Hauptloop
# ----------------------------------------------------------
running = True

while running:
    dt = clock.tick(60) / 1000.0 * time_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # Neue Idee erzeugen
            if event.key == pygame.K_SPACE:
                idea_strength = clamp(idea_strength + 0.75)
                memory_trace = clamp(memory_trace + 0.20 * meaning)
                add_particles("idea", 35)

            # Trigger auslösen
            if event.key == pygame.K_t:
                trigger_strength = clamp(trigger_strength + 0.85)
                add_trigger_wave()

            # Aufmerksamkeit
            if event.key == pygame.K_UP:
                attention = clamp(attention + 0.08)
            if event.key == pygame.K_DOWN:
                attention = clamp(attention - 0.08)

            # Ablenkung
            if event.key == pygame.K_RIGHT:
                noise = clamp(noise + 0.08)
            if event.key == pygame.K_LEFT:
                noise = clamp(noise - 0.08)

            # Müdigkeit
            if event.key == pygame.K_f:
                fatigue = clamp(fatigue + 0.10)
            if event.key == pygame.K_g:
                fatigue = clamp(fatigue - 0.10)

            # Bedeutung
            if event.key == pygame.K_m:
                meaning = clamp(meaning + 0.10)
            if event.key == pygame.K_n:
                meaning = clamp(meaning - 0.10)

            # Pause / Reset
            if event.key == pygame.K_p:
                paused = not paused
            if event.key == pygame.K_r:
                reset_all()

    if not paused:
        # --------------------------------------------------
        # Dynamik
        # --------------------------------------------------

        # Idee fällt ab: schneller bei Ablenkung/Müdigkeit, langsamer bei Aufmerksamkeit/Bedeutung
        decay = 0.20 + noise * 0.55 + fatigue * 0.45 - attention * 0.25 - meaning * 0.15
        decay = max(0.04, decay)

        idea_strength -= decay * dt
        idea_strength = clamp(idea_strength)

        # Gedächtnisspur wird aufgebaut, wenn Idee aktiv ist
        encoding = idea_strength * (0.25 + attention * 0.55 + meaning * 0.45) * dt
        memory_trace += encoding

        # Spur verblasst langsam
        trace_decay = (0.025 + fatigue * 0.025 + noise * 0.025) * dt
        memory_trace -= trace_decay
        memory_trace = clamp(memory_trace)

        # Trigger holt Idee zurück, wenn Spur vorhanden ist
        recall = trigger_strength * memory_trace * (0.65 + attention * 0.35)
        if recall > 0.02:
            idea_strength = clamp(idea_strength + recall * dt * 1.6)
            add_particles("memory", 1)

        # Trigger fällt ab
        trigger_strength -= 0.65 * dt
        trigger_strength = clamp(trigger_strength)

        # Auto-Idee selten, wie zufälliger Gedanke
        now = time.time()
        if now - last_auto_idea > random.uniform(9, 16):
            if random.random() < 0.35:
                idea_strength = clamp(idea_strength + random.uniform(0.25, 0.55))
                add_particles("idea", 18)
            last_auto_idea = now

        # Auto-Trigger gelegentlich
        if now - last_auto_trigger > random.uniform(12, 22):
            if random.random() < 0.45 and memory_trace > 0.15:
                trigger_strength = clamp(trigger_strength + random.uniform(0.35, 0.75))
                add_trigger_wave()
            last_auto_trigger = now

        # Verlauf speichern
        history_idea.append(idea_strength)
        history_trace.append(memory_trace)
        history_trigger.append(trigger_strength)

        if len(history_idea) > MAX_HISTORY:
            history_idea.pop(0)
            history_trace.pop(0)
            history_trigger.pop(0)

        update_particles()

    # ------------------------------------------------------
    # Zeichnen
    # ------------------------------------------------------
    screen.fill(BG)

    draw_text("Live-Simulation: Idee, Kurzzeitgedächtnis, Spur und Trigger", 60, 25, WHITE, BIG)

    draw_text("SPACE = neue Idee   T = Trigger   ↑↓ Aufmerksamkeit   ←→ Ablenkung", 60, 65, DIM, SMALL)
    draw_text("F/G = Müdigkeit hoch/runter   M/N = Bedeutung hoch/runter   P = Pause   R = Reset   ESC = Ende", 60, 85, DIM, SMALL)

    # Verbindungen zwischen Knoten
    draw_connection(250, 310, 510, 310, idea_strength, CYAN)
    draw_connection(510, 310, 760, 310, trigger_strength, PINK)

    draw_particles()

    # Knoten
    draw_node(250, 310, 72, idea_strength, "A: aktive Idee", CYAN)
    draw_node(510, 310, 72, memory_trace, "B: Gedächtnisspur", GOLD)
    draw_node(760, 310, 72, trigger_strength, "?: Trigger / Abruf", PINK)

    # Formel
    pygame.draw.rect(screen, (15, 18, 35), (205, 430, 590, 56), border_radius=14)
    pygame.draw.rect(screen, (70, 80, 120), (205, 430, 590, 56), 2, border_radius=14)
    draw_text("Idee(t) → Spur(t) → Trigger → Erinnerung", 270, 447, WHITE, FONT)

    # Werte
    draw_bar("Aufmerksamkeit", attention, 70, 150, 180, 18, GREEN)
    draw_bar("Ablenkung / Rauschen", noise, 290, 150, 180, 18, RED)
    draw_bar("Müdigkeit", fatigue, 510, 150, 180, 18, VIOLET)
    draw_bar("Bedeutung / Emotion", meaning, 730, 150, 180, 18, GOLD)

    # Statussatz
    if idea_strength > 0.65:
        status = "Die Idee ist stark aktiv im Arbeitsgedächtnis."
        color = CYAN
    elif memory_trace > 0.45 and idea_strength < 0.25:
        status = "Die Idee ist gerade weg, aber die Gedächtnisspur ist noch da."
        color = GOLD
    elif trigger_strength > 0.35:
        status = "Ein Trigger sucht die Spur und kann Erinnerung zurückholen."
        color = PINK
    elif memory_trace < 0.12 and idea_strength < 0.12:
        status = "Kaum aktive Idee: ohne Anker wird es schwerer, sie zurückzuholen."
        color = DIM
    else:
        status = "Der Gedanke schwebt zwischen aktiv und vergessen."
        color = WHITE

    draw_text(status, 260, 505, color, FONT)

    draw_graph()

    pygame.display.flip()

pygame.quit()