import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

size = 100
x = np.linspace(-5,5,size)
y = np.linspace(-5,5,size)
X,Y = np.meshgrid(x,y)

charges = [(-2,0,1),(2,0,-1)]

fig,(ax1,ax2)=plt.subplots(1,2)

def update(frame):
    Ex, Ey = np.zeros_like(X), np.zeros_like(Y)
    
    for cx,cy,q in charges:
        dx = X-cx
        dy = Y-cy
        r2 = dx**2+dy**2+0.2
        Ex += q*np.cos(frame*0.1)*dx/r2
        Ey += q*np.cos(frame*0.1)*dy/r2

    mag = np.sqrt(Ex**2+Ey**2)

    ax1.clear()
    ax1.plot(x,mag[size//2],color='cyan')
    ax1.set_title("Seite Feld")

    ax2.clear()
    ax2.imshow(mag,extent=(-5,5,-5,5),cmap='plasma')
    ax2.quiver(X[::5,::5],Y[::5,::5],
               Ex[::5,::5],Ey[::5,::5],
               color='white')
    ax2.set_title("Top + Vektor")

ani = animation.FuncAnimation(fig,update,frames=100,interval=50)
plt.show()