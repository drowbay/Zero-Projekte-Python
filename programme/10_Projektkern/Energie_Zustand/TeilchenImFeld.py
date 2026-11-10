import numpy as np
import matplotlib.pyplot as plt

size=50
x=np.linspace(-5,5,size)
y=np.linspace(-5,5,size)
X,Y=np.meshgrid(x,y)

# Feld
Ex = -X
Ey = -Y

# Teilchen
px = np.random.uniform(-4,4,20)
py = np.random.uniform(-4,4,20)

for i in range(50):
    for j in range(len(px)):
        px[j] += Ex[int((py[j]+5)/10*(size-1)),
                    int((px[j]+5)/10*(size-1))]*0.1
        py[j] += Ey[int((py[j]+5)/10*(size-1)),
                    int((px[j]+5)/10*(size-1))]*0.1

plt.quiver(X,Y,Ex,Ey)
plt.scatter(px,py,color='red')
plt.title("Teilchen im Feld")
plt.show()