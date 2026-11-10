import random
import matplotlib.pyplot as plt

# 5-Zacken-Stern (vereinfacht als Punkte)
points = [
    (0, 100),    # oben
    (95, 30),
    (60, -80),
    (-60, -80),
    (-95, 30)
]

# Startpunkt (irgendwo)
x, y = 0, 0

xs, ys = [], []

for _ in range(60000):
    px, py = random.choice(points)

    # halber Weg (dein "halbieren"-Prinzip)
    x = (x + px) / 2
    y = (y + py) / 2

    xs.append(x)
    ys.append(y)

plt.scatter(xs, ys, s=1)
plt.axis('equal')
plt.show()