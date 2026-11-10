#!/usr/bin/env python3

import numpy as np
import math
import re

# -----------------------------------
# CFDE SIMULATION
# -----------------------------------

SIZE = 12
space = np.zeros((SIZE,SIZE,SIZE))

cx = cy = cz = SIZE//2
space[cx,cy,cz] = 5


def gravity_field(x,y,z):

    dx = x-cx
    dy = y-cy
    dz = z-cz

    r = math.sqrt(dx*dx+dy*dy+dz*dz)+0.0001

    return 0.62/(r*r)


def step(field):

    new = field.copy()

    for x in range(1,SIZE-1):
        for y in range(1,SIZE-1):
            for z in range(1,SIZE-1):

                neighbors = (
                    field[x+1,y,z] +
                    field[x-1,y,z] +
                    field[x,y+1,z] +
                    field[x,y-1,z] +
                    field[x,y,z+1] +
                    field[x,y,z-1]
                )/6

                new[x,y,z] += 0.1*(neighbors-field[x,y,z])
                new[x,y,z] += gravity_field(x,y,z)

    return new


# -----------------------------------
# HSV → TLS → QUBIT
# -----------------------------------

def hsv_to_tls(h,s,v):

    phi = 2*math.pi*h

    x = s*math.cos(phi)
    y = s*math.sin(phi)
    z = v

    return (x,y,z)


def hsv_to_qubit(h,v):

    phi = 2*math.pi*h
    theta = math.pi*(1-v)

    alpha = math.cos(theta/2)
    beta = complex(math.cos(phi),math.sin(phi))*math.sin(theta/2)

    return (alpha,beta)


def field_to_hsv(value):

    v = min(abs(value)/5,1)
    s = min(abs(value),1)

    if value >= 0:
        h = 0.33
    else:
        h = 0.0

    return h,s,v


# -----------------------------------
# TOY KI
# -----------------------------------

def reply(text):

    global space

    tl = text.lower()

    if tl == "exit":
        return "bye", True

    if tl.startswith("/step"):

        space = step(space)

        return "simulation step", False

    if tl.startswith("/energy"):

        e = float(np.sum(space))
        return f"energy {e:.2f}", False

    if tl.startswith("/tls"):

        val = space[cx,cy,cz]

        h,s,v = field_to_hsv(val)

        tls = hsv_to_tls(h,s,v)

        return f"TLS {tls}", False

    if tl.startswith("/qubit"):

        val = space[cx,cy,cz]

        h,s,v = field_to_hsv(val)

        qb = hsv_to_qubit(h,v)

        return f"Qubit {qb}", False

    return f"echo: {text}", False


# -----------------------------------
# CHAT LOOP
# -----------------------------------

print("======================================")
print("CosmoField Dynamics Engine + Toy KI")
print("======================================")
print("")
print("Befehle:")
print("/step    → Simulation einen Schritt weiter")
print("/energy  → Gesamtenergie im Feld anzeigen")
print("/tls     → TLS-Vektor des Zentrums anzeigen")
print("/qubit   → Qubit-Zustand anzeigen")
print("exit     → Programm beenden")
print("")

while True:

    user = input("DU > ")

    resp,stop = reply(user)

    print("KI >",resp)

    if stop:
        break
