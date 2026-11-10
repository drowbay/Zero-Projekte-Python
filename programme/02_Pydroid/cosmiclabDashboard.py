import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

# -------------------------
# Daten erzeugen
# -------------------------

t = np.linspace(0,4*np.pi,200)

x = np.cos(t)*t*0.1
y = np.sin(t)*t*0.1
z = t*0.1

# Heatmap
size = 24
grid = np.zeros((size,size))

for i in range(size):
    for j in range(size):
        grid[i,j] = np.sin(i*0.3)+np.cos(j*0.3)

# FFT
fft = np.abs(np.fft.fftshift(np.fft.fft2(grid)))

# -------------------------
# Figure Layout
# -------------------------

fig = plt.figure(figsize=(10,8))

# TLS Punktwolke
ax1 = fig.add_subplot(221, projection='3d')
ax1.scatter(x,y,z,c=z,cmap='Greens')
ax1.set_title("TLS Punktwolke")

# Bloch Sphere
ax2 = fig.add_subplot(222, projection='3d')

phi = np.linspace(0,2*np.pi,40)
theta = np.linspace(0,np.pi,40)

phi,theta = np.meshgrid(phi,theta)

xs = np.sin(theta)*np.cos(phi)
ys = np.sin(theta)*np.sin(phi)
zs = np.cos(theta)

ax2.plot_surface(xs,ys,zs,alpha=0.2,color='cyan')

ax2.quiver(0,0,0,0.7,0.2,0.5,color='green')
ax2.set_title("Bloch Sphere")

# Druckkarte
ax3 = fig.add_subplot(223)
ax3.imshow(grid,cmap='magma')
ax3.set_title("Druckkarte")

# FFT
ax4 = fig.add_subplot(224)
ax4.imshow(fft,cmap='inferno')
ax4.set_title("FFT")

plt.tight_layout()
plt.show()