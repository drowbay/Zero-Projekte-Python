import pygame
import math
import random

pygame.init()

W, H = 800, 500
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Atom Simulation - Felder & Teilchen")

clock = pygame.time.Clock()

center_x, center_y = W // 2, H // 2

# Kern
protons = [(random.randint(-15,15), random.randint(-15,15)) for _ in range(6)]
neutrons = [(random.randint(-15,15), random.randint(-15,15)) for _ in range(6)]

# Elektronen
electrons = []
for i in range(12):
    angle = random.uniform(0, math.pi*2)
    radius = random.randint(60, 160)
    speed = random.uniform(0.01, 0.03)
    electrons.append([angle, radius, speed])

def draw_field():
    # Feldlinien vom Kern
    for i in range(40):
        angle = i * (math.pi * 2 / 40)
        length = 80 + math.sin(pygame.time.get_ticks()*0.002 + i) * 20

        x2 = center_x + math.cos(angle) * length
        y2 = center_y + math.sin(angle) * length

        pygame.draw.line(screen, (50,120,255), (center_x, center_y), (x2, y2), 1)

def draw_nucleus():
    for p in protons:
        pygame.draw.circle(screen, (255,80,80), (center_x + p[0], center_y + p[1]), 6)
    for n in neutrons:
        pygame.draw.circle(screen, (180,180,180), (center_x + n[0], center_y + n[1]), 6)

def draw_electrons():
    for e in electrons:
        e[0] += e[2]

        x = center_x + math.cos(e[0]) * e[1]
        y = center_y + math.sin(e[0]) * e[1]

        pygame.draw.circle(screen, (100,200,255), (int(x), int(y)), 4)

        # Spur (Orbit)
        pygame.draw.circle(screen, (40,80,140), (center_x, center_y), int(e[1]), 1)

running = True

while running:
    screen.fill((5, 8, 18))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_field()
    draw_nucleus()
    draw_electrons()

    font = pygame.font.SysFont(None, 24)
    text = font.render("Atom: Protonen, Neutronen, Elektronen + Feld", True, (230,230,255))
    screen.blit(text, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()