import pygame
import math
import sys

pygame.init()

WIDTH = 900
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CosmicLab - Bloch Sphere")

clock = pygame.time.Clock()

angle_x = 0
angle_y = 0

theta = 1.2
phi = 0.8

radius = 200


def rotate(x, y, z, ax, ay):

    cosx = math.cos(ax)
    sinx = math.sin(ax)

    cosy = math.cos(ay)
    siny = math.sin(ay)

    y2 = y*cosx - z*sinx
    z2 = y*sinx + z*cosx

    x2 = x*cosy + z2*siny
    z3 = -x*siny + z2*cosy

    return x2, y2, z3


def project(x, y, z):

    scale = 400 / (z + 6)

    px = x * scale + WIDTH/2
    py = y * scale + HEIGHT/2

    return int(px), int(py)


def draw_sphere():

    for i in range(18):

        lat = math.pi * (-0.5 + i/18)

        for j in range(36):

            lon = 2*math.pi*j/36

            x = math.cos(lat)*math.cos(lon)
            y = math.sin(lat)
            z = math.cos(lat)*math.sin(lon)

            x,y,z = rotate(x,y,z,angle_x,angle_y)

            px,py = project(x,y,z)

            pygame.draw.circle(screen,(80,200,255),(px,py),2)


def draw_qubit():

    x = math.sin(theta)*math.cos(phi)
    y = math.cos(theta)
    z = math.sin(theta)*math.sin(phi)

    x,y,z = rotate(x,y,z,angle_x,angle_y)

    px,py = project(x,y,z)

    pygame.draw.circle(screen,(255,100,100),(px,py),8)


running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT:
                phi -= 0.1

            if event.key == pygame.K_RIGHT:
                phi += 0.1

            if event.key == pygame.K_UP:
                theta -= 0.1

            if event.key == pygame.K_DOWN:
                theta += 0.1

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        angle_y -= 0.05

    if keys[pygame.K_d]:
        angle_y += 0.05

    if keys[pygame.K_w]:
        angle_x -= 0.05

    if keys[pygame.K_s]:
        angle_x += 0.05

    screen.fill((10,10,30))

    draw_sphere()
    draw_qubit()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()