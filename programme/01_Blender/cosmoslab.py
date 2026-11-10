import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys

# -----------------------------
# Kamera Einstellungen
# -----------------------------

angle_x = 40
angle_y = 20
distance = 6

rotation_speed = 0.4
zoom_speed = 0.5

# -----------------------------
# Qubit Zustand (Bloch Sphere)
# -----------------------------

theta = 1.2
phi = 0.8

radius = 1.5


# -----------------------------
# Bloch Sphere zeichnen
# -----------------------------

def draw_bloch_sphere():

    slices = 24
    stacks = 24

    glColor3f(0.3,0.8,1)

    for i in range(stacks):

        lat0 = math.pi * (-0.5 + float(i)/stacks)
        z0 = math.sin(lat0)
        zr0 = math.cos(lat0)

        lat1 = math.pi * (-0.5 + float(i+1)/stacks)
        z1 = math.sin(lat1)
        zr1 = math.cos(lat1)

        glBegin(GL_LINE_LOOP)

        for j in range(slices):

            lng = 2 * math.pi * float(j)/slices

            x = math.cos(lng)
            y = math.sin(lng)

            glVertex3f(radius*x*zr0, radius*z0, radius*y*zr0)
            glVertex3f(radius*x*zr1, radius*z1, radius*y*zr1)

        glEnd()


# -----------------------------
# Qubit Punkt
# -----------------------------

def draw_qubit():

    global theta, phi

    x = radius * math.sin(theta) * math.cos(phi)
    y = radius * math.cos(theta)
    z = radius * math.sin(theta) * math.sin(phi)

    glPointSize(10)

    glBegin(GL_POINTS)
    glColor3f(1,0.3,0.3)
    glVertex3f(x,y,z)
    glEnd()


# -----------------------------
# Zustandsvektor
# -----------------------------

def draw_state_vector():

    x = radius * math.sin(theta) * math.cos(phi)
    y = radius * math.cos(theta)
    z = radius * math.sin(theta) * math.sin(phi)

    glBegin(GL_LINES)

    glColor3f(1,1,0)

    glVertex3f(0,0,0)
    glVertex3f(x,y,z)

    glEnd()


# -----------------------------
# Kamera Position
# -----------------------------

def update_camera():

    camX = distance * math.cos(math.radians(angle_y)) * math.sin(math.radians(angle_x))
    camY = distance * math.sin(math.radians(angle_y))
    camZ = distance * math.cos(math.radians(angle_y)) * math.cos(math.radians(angle_x))

    gluLookAt(
        camX, camY, camZ,
        0,0,0,
        0,1,0
    )


# -----------------------------
# Hauptprogramm
# -----------------------------

def main():

    global angle_x, angle_y, distance
    global theta, phi

    pygame.init()

    display = (900,700)

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("CosmicLab - Bloch Sphere")

    gluPerspective(45, display[0]/display[1], 0.1, 100)

    glEnable(GL_DEPTH_TEST)

    clock = pygame.time.Clock()

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Rotation
            if event.type == pygame.MOUSEMOTION:

                if pygame.mouse.get_pressed()[0]:

                    dx, dy = event.rel

                    angle_x += dx * rotation_speed
                    angle_y += dy * rotation_speed

            # Zoom
            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 4:
                    distance -= zoom_speed

                if event.button == 5:
                    distance += zoom_speed

            # Tastatur Steuerung
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LEFT:
                    phi -= 0.1

                if event.key == pygame.K_RIGHT:
                    phi += 0.1

                if event.key == pygame.K_UP:
                    theta -= 0.1

                if event.key == pygame.K_DOWN:
                    theta += 0.1

                # Kamera Reset
                if event.key == pygame.K_f:

                    angle_x = 40
                    angle_y = 20
                    distance = 6

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        update_camera()

        draw_bloch_sphere()
        draw_state_vector()
        draw_qubit()

        pygame.display.flip()

        clock.tick(60)


if __name__ == "__main__":
    main()