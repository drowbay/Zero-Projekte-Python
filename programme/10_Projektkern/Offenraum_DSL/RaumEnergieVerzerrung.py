import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

size=20
X,Y = np.meshgrid(np.linspace(-5,5,size),np.linspace(-5,5,size))

fig, ax = plt.subplots()

def update(frame):
    ax.clear()
    
    Z = np.sin(np.sqrt(X**2+Y**2) - frame*0.2)
    
    ax.contour(X,Y,Z)
    ax.set_title("Raum-Verzerrung")

ani = animation.FuncAnimation(fig, update, frames=200, interval=50)
plt.show()