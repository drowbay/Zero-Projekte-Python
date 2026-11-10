import pygame
import math
import random

pygame.init()

W, H = 800, 600
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

center = (W//2, H//2)

particles = []
for _ in range(120):
    angle = random.uniform(0, 2*math.pi)
    radius = random.uniform(50, 200)
    speed = random.uniform(0.01, 0.03)
    particles.append([angle, radius, speed])

def draw_fractal_ring(time):
    for i in range(200):
        angle = i * (2*math.pi / 200)

        # Fraktal-Wellen
        r = 180 + math.sin(angle*8 + time*0.05)*20
        r += math.sin(angle*24 + time*0.1)*8

        x = center[0] + math.cos(angle)*r
        y = center[1] + math.sin(angle)*r

        pygame.draw.circle(screen, (120,200,255), (int(x), int(y)), 1)

def draw_particles(time):
    for p in particles:
        p[0] += p[2]

        r = p[1] + math.sin(time*0.05 + p[0]*5)*10

        x = center[0] + math.cos(p[0])*r
        y = center[1] + math.sin(p[0])*r

        pygame.draw.circle(screen, (255,100,150), (int(x), int(y)), 2)

running = True
t = 0

while running:
    screen.fill((5,5,15))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_fractal_ring(t)
    draw_particles(t)

    # Zentrum (dein "Kern")
    pygame.draw.circle(screen, (20,20,20), center, 40)

    pygame.display.flip()
    clock.tick(60)
    t += 1

pygame.quit()