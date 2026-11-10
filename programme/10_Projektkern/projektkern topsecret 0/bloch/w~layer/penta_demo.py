import math
import time
import pygame

# ============================================================
# Zero – Penta / Bloch / w-Layer Simulation für Pydroid 3
# ------------------------------------------------------------
# Benötigt: pygame
# In Pydroid ggf. im Pip-Menü installieren: pygame
#
# WICHTIG:
# - Bloch-Sphere / Qubit sind reale physikalische Konzepte.
# - Sinus/Maxus, Penta-Orbit und w-Layer sind hier ein
#   experimentelles Visualisierungsmodell.
# ============================================================

pygame.init()

W, H = 1000, 700
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Zero – Penta Bloch w-Layer")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)
small = pygame.font.SysFont(None, 20)
big = pygame.font.SysFont(None, 34)

# Farben
BG = (10, 13, 22)
GRID = (45, 52, 70)
WHITE = (235, 240, 248)
MUTED = (150, 160, 180)
BLUE = (70, 155, 255)
PINK = (255, 80, 165)
CYAN = (70, 230, 230)
YELLOW = (255, 220, 90)
GREEN = (80, 220, 135)

# Penta-Zustandsfolge
PENTA = [0, 2, 4, 1, 3]
penta_index = 0

# Simulationszustand
t = 0.0
dt = 0.025
x_prev = 0.0
phase = 0.0
w_layer = 0
running = True

history = []
dx_history = []

# Schwellenwert, ab dem ein starker Ausschlag w verändert
W_THRESHOLD = 0.085

def demo_signal(t):
    """
    Demo-Messsignal.
    Später kann diese Funktion durch echte Sensor-/GOES-Daten ersetzt werden.
    """
    base = (
        0.50 * math.sin(2.0 * math.pi * 0.33 * t)
        + 0.22 * math.sin(2.0 * math.pi * 0.91 * t + 0.8)
        + 0.10 * math.sin(2.0 * math.pi * 1.75 * t)
    )

    # gelegentliche stärkere Impulse, damit w-Layer sichtbar springen
    pulse = 0.0
    p = t % 7.0
    if 2.20 < p < 2.35:
        pulse += 0.55 * math.sin((p - 2.20) / 0.15 * math.pi)
    if 5.10 < p < 5.25:
        pulse -= 0.65 * math.sin((p - 5.10) / 0.15 * math.pi)

    return base + pulse


def draw_text(txt, x, y, color=WHITE, f=None):
    if f is None:
        f = font
    screen.blit(f.render(txt, True, color), (x, y))


def draw_signal_panel(rect, hist, dx_hist):
    x0, y0, ww, hh = rect
    pygame.draw.rect(screen, (15, 19, 30), rect, border_radius=16)
    pygame.draw.rect(screen, GRID, rect, 2, border_radius=16)

    mid = y0 + hh // 2
    pygame.draw.line(screen, GRID, (x0 + 20, mid), (x0 + ww - 20, mid), 1)

    draw_text("Signal x(t) + Δx", x0 + 18, y0 + 12, WHITE, small)

    if len(hist) < 2:
        return

    maxn = min(260, len(hist))
    vals = hist[-maxn:]
    dxs = dx_hist[-maxn:]

    scale_y = hh * 0.34
    pts = []
    dx_pts = []

    for i, v in enumerate(vals):
        px = x0 + 20 + i * (ww - 40) / max(1, maxn - 1)
        py = mid - v * scale_y
        pts.append((int(px), int(py)))

    for i, v in enumerate(dxs):
        px = x0 + 20 + i * (ww - 40) / max(1, maxn - 1)
        py = mid - v * scale_y * 4.0
        dx_pts.append((int(px), int(py)))

    if len(pts) >= 2:
        pygame.draw.lines(screen, BLUE, False, pts, 3)
    if len(dx_pts) >= 2:
        pygame.draw.lines(screen, PINK, False, dx_pts, 2)


def draw_bloch(cx, cy, r, theta, phi, layer):
    # Kugel-Schnitt
    pygame.draw.circle(screen, GRID, (cx, cy), r, 2)
    pygame.draw.ellipse(screen, GRID, (cx-r, cy-r//3, 2*r, 2*r//3), 1)
    pygame.draw.line(screen, GRID, (cx-r-15, cy), (cx+r+15, cy), 1)
    pygame.draw.line(screen, GRID, (cx, cy-r-15), (cx, cy+r+15), 1)

    # w-Layer als zusätzliche Ringe
    for k in range(-3, 4):
        if k == 0:
            continue
        rr = int(r * (1.0 - 0.07 * abs(k)))
        yy = cy + k * 18
        color = PINK if k > 0 else BLUE
        pygame.draw.ellipse(
            screen, color,
            (cx-rr, yy-9, rr*2, 18),
            1
        )

    # Zustandspunkt – 2D-Projektion einer Bloch-Richtung
    vx = math.sin(theta) * math.cos(phi)
    vy = math.cos(theta)

    tipx = cx + int(r * 0.78 * vx)
    tipy = cy - int(r * 0.78 * vy)

    pygame.draw.line(screen, CYAN, (cx, cy), (tipx, tipy), 4)
    pygame.draw.circle(screen, CYAN, (tipx, tipy), 9)
    pygame.draw.circle(screen, WHITE, (cx, cy), 4)

    draw_text("|0>", cx + 10, cy-r-6, PINK, small)
    draw_text("|1>", cx + 10, cy+r-18, BLUE, small)
    draw_text(f"w = {layer:+d}", cx-r, cy+r+28, YELLOW, small)


def penta_positions(cx, cy, r):
    # Punkt-Reihenfolge optisch im Kreis: 0,1,2,3,4
    pos = {}
    for label in range(5):
        ang = -math.pi/2 + label * 2*math.pi/5
        pos[label] = (
            cx + int(r * math.cos(ang)),
            cy + int(r * math.sin(ang))
        )
    return pos


def draw_penta(cx, cy, r, active):
    pos = penta_positions(cx, cy, r)

    # Kreis
    pygame.draw.circle(screen, GRID, (cx, cy), r, 2)

    # Ablauf 0 -> 2 -> 4 -> 1 -> 3 -> 0
    seq = PENTA + [PENTA[0]]
    for a, b in zip(seq[:-1], seq[1:]):
        pygame.draw.line(screen, (80, 95, 125), pos[a], pos[b], 2)

    # Punkte
    for n in range(5):
        col = YELLOW if n == active else WHITE
        pygame.draw.circle(screen, col, pos[n], 11)
        pygame.draw.circle(screen, BG, pos[n], 7)
        draw_text(str(n), pos[n][0]-5, pos[n][1]-32, col, small)

    ax, ay = pos[active]
    pygame.draw.circle(screen, PINK if active in (1,3) else BLUE, (ax, ay), 6)


def reset():
    global t, x_prev, phase, w_layer, penta_index, history, dx_history
    t = 0.0
    x_prev = demo_signal(0.0)
    phase = 0.0
    w_layer = 0
    penta_index = 0
    history = [x_prev]
    dx_history = [0.0]


reset()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # Pause / Weiter
                dt = 0.0 if dt > 0 else 0.025
            elif event.key == pygame.K_r:
                dt = 0.025
                reset()

    if dt > 0:
        t += dt
        x = demo_signal(t)
        dx = x - x_prev
        x_prev = x

        history.append(x)
        dx_history.append(dx)
        if len(history) > 500:
            history.pop(0)
            dx_history.pop(0)

        # Sinus / Maxus
        state = "MAXUS (+)" if dx >= 0 else "SINUS (-)"

        # Änderung beeinflusst Phase auf der Kugel
        phase += dx * 4.0

        # Starkes Delta wird NICHT abgeschnitten:
        # es verändert zusätzlich w.
        if abs(dx) >= W_THRESHOLD:
            w_layer += 1 if dx > 0 else -1
            w_layer = max(-5, min(5, w_layer))

            # Penta-Orbit springt bei starkem Ereignis einen Schritt weiter
            penta_index = (penta_index + 1) % len(PENTA)

        active_penta = PENTA[penta_index]

        # Bloch-inspirierte Winkel
        theta = math.pi/2 + 0.95 * math.sin(phase)
        phi = phase * 1.6 + w_layer * 0.42

        p0 = math.cos(theta/2)**2
        p1 = 1.0 - p0

        screen.fill(BG)

        # Titel / Kennwerte
        draw_text("ZERO – Penta / Bloch / w-Layer", 28, 18, WHITE, big)
        draw_text("Experimentelle Messdaten-Visualisierung", 30, 54, MUTED, small)

        panel_y = 92
        draw_signal_panel((28, panel_y, W-56, 190), history, dx_history)

        # Untere Bereiche
        left_cx, left_cy = 255, 475
        right_cx, right_cy = 740, 475

        draw_bloch(left_cx, left_cy, 135, theta, phi, w_layer)
        draw_penta(right_cx, right_cy, 125, active_penta)

        # Kennwerte
        draw_text(f"x(t) = {x:+.3f}", 28, 302, BLUE, small)
        draw_text(f"Δx = {dx:+.4f}", 185, 302, PINK, small)
        draw_text(state, 345, 302, GREEN if dx >= 0 else YELLOW, small)
        draw_text(f"P(0) = {p0*100:5.1f}%", 28, 330, PINK, small)
        draw_text(f"P(1) = {p1*100:5.1f}%", 185, 330, BLUE, small)
        draw_text(f"Penta = {active_penta}", 345, 330, YELLOW, small)
        draw_text(f"Schwelle |Δx| >= {W_THRESHOLD:.3f}", 505, 330, MUTED, small)

        draw_text("Bloch-inspirierter Zustand + w", 105, 636, MUTED, small)
        draw_text("Penta-Orbit: 0 -> 2 -> 4 -> 1 -> 3", 585, 636, MUTED, small)

        draw_text("SPACE = Pause   R = Reset   ESC = Ende", 28, H-32, MUTED, small)

        pygame.display.flip()

    clock.tick(60)

pygame.quit()
