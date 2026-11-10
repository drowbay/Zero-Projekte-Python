import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

theta = np.linspace(0,2*np.pi,50)
r = 2

fig, ax = plt.subplots()

def update(frame):
    t = frame*0.1
    x = r*np.cos(theta+t)
    y = r*np.sin(theta+t)

    ax.clear()
    ax.plot(x,y)
    ax.scatter(x,y)
    ax.set_xlim(-3,3)
    ax.set_ylim(-3,3)
    ax.set_title("Energie-Zyklus")

ani = animation.FuncAnimation(fig, update, frames=200, interval=50)
plt.show()