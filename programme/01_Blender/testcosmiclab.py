import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation

print("======================================")
print("COSMO FIELD LAB")
print("Simulation + TLS + Bloch + Druckkarte")
print("======================================")
print("Controls:")
print("Play / Pause / << / >>  -> Zeitsteuerung")
print("Speed Slider            -> Geschwindigkeit")
print("Diffusion Slider        -> Feldverteilung")
print("Z-Slice Slider          -> Druckkarten-Ebene")
print("======================================")

# ----------------------------------
# Parameter
# ----------------------------------

SIZE = 20
DIFFUSION = 0.15

space = np.zeros((SIZE,SIZE,SIZE))
cx = cy = cz = SIZE//2
space[cx,cy,cz] = 5

frames = []
current_frame = 0
running = True
speed = 1

# ----------------------------------
# Simulation
# ----------------------------------

def step(field, diff):

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
                ) / 6

                new[x,y,z] += diff*(neighbors-field[x,y,z])

    return new

# ----------------------------------
# Energie → HSV
# ----------------------------------

def energy_to_hsv(e):

    h = (e % 1)
    s = min(abs(e),1)
    v = min(abs(e)/5,1)

    return h,s,v

# ----------------------------------
# HSV → TLS
# ----------------------------------

def hsv_to_tls(h,s,v):

    phi = 2*np.pi*h

    x = s*np.cos(phi)
    y = s*np.sin(phi)
    z = v

    return x,y,z

# ----------------------------------
# HSV → Bloch
# ----------------------------------

def hsv_to_qubit(h,v):

    phi = 2*np.pi*h
    theta = np.pi*(1-v)

    x = np.sin(theta)*np.cos(phi)
    y = np.sin(theta)*np.sin(phi)
    z = np.cos(theta)

    return x,y,z

# ----------------------------------
# Feld → Punktwolke
# ----------------------------------

def field_to_points(field):

    xs,ys,zs,colors = [],[],[],[]

    for x in range(SIZE):
        for y in range(SIZE):
            for z in range(SIZE):

                e = field[x,y,z]

                if abs(e) > 0.01:

                    h,s,v = energy_to_hsv(e)
                    tx,ty,tz = hsv_to_tls(h,s,v)

                    xs.append(tx)
                    ys.append(ty)
                    zs.append(tz)

                    colors.append((h,s,v))

    return xs,ys,zs,colors

# ----------------------------------
# Fenster
# ----------------------------------

fig = plt.figure(figsize=(12,6))

ax_tls = fig.add_subplot(221,projection='3d')
ax_bloch = fig.add_subplot(222,projection='3d')
ax_map = fig.add_subplot(212)

ax_tls.set_title("TLS Punktwolke")
ax_bloch.set_title("Bloch Sphere")
ax_map.set_title("Energie Druckkarte")

ax_tls.set_xlim(-1,1)
ax_tls.set_ylim(-1,1)
ax_tls.set_zlim(0,1)

ax_bloch.set_xlim(-1,1)
ax_bloch.set_ylim(-1,1)
ax_bloch.set_zlim(-1,1)

scatter = ax_tls.scatter([],[],[],s=5)
bloch_point = ax_bloch.scatter([0],[0],[1],color="red",s=100)

slice_z = SIZE//2
heatmap = ax_map.imshow(space[:,:,slice_z], cmap="plasma", origin="lower")
plt.colorbar(heatmap, ax=ax_map)

# ----------------------------------
# Slider
# ----------------------------------

ax_diff = plt.axes([0.25,0.02,0.3,0.02])
slider_diff = Slider(ax_diff,"Diffusion",0.01,0.5,valinit=DIFFUSION)

ax_speed = plt.axes([0.65,0.02,0.3,0.02])
slider_speed = Slider(ax_speed,"Speed",0.1,5,valinit=1)

ax_slice = plt.axes([0.25,0.05,0.7,0.02])
slider_slice = Slider(ax_slice,"Z-Slice",0,SIZE-1,valinit=slice_z,valstep=1)

# ----------------------------------
# Buttons
# ----------------------------------

ax_play = plt.axes([0.02,0.02,0.05,0.04])
ax_pause = plt.axes([0.08,0.02,0.05,0.04])
ax_back = plt.axes([0.14,0.02,0.05,0.04])
ax_forward = plt.axes([0.20,0.02,0.05,0.04])

btn_play = Button(ax_play,"Play")
btn_pause = Button(ax_pause,"Pause")
btn_back = Button(ax_back,"<<")
btn_forward = Button(ax_forward,">>")

# ----------------------------------
# Button Funktionen
# ----------------------------------

def play(event):
    global running
    running = True

def pause(event):
    global running
    running = False

def back(event):
    global current_frame
    if current_frame > 0:
        current_frame -= 1

def forward(event):
    global current_frame
    if current_frame < len(frames)-1:
        current_frame += 1

btn_play.on_clicked(play)
btn_pause.on_clicked(pause)
btn_back.on_clicked(back)
btn_forward.on_clicked(forward)

# ----------------------------------
# Simulation Frame
# ----------------------------------

def simulate_step():

    global space

    space = step(space, slider_diff.val)
    frames.append(space.copy())

# ----------------------------------
# Update Loop
# ----------------------------------

def update(frame):

    global current_frame, space

    speed = slider_speed.val

    if running:
        simulate_step()
        current_frame = len(frames)-1

    field = frames[current_frame]

    xs,ys,zs,colors = field_to_points(field)

    scatter._offsets3d = (xs,ys,zs)
    scatter.set_color(colors)

    # Bloch Zentrum
    e = field[cx,cy,cz]
    h,s,v = energy_to_hsv(e)
    bx,by,bz = hsv_to_qubit(h,v)

    bloch_point._offsets3d = ([bx],[by],[bz])

    # Heatmap
    slice_z = int(slider_slice.val)
    slice_data = field[:,:,slice_z]

    heatmap.set_data(slice_data)
    heatmap.set_clim(vmin=np.min(field), vmax=np.max(field))

    return scatter,

# ----------------------------------

frames.append(space.copy())

ani = FuncAnimation(fig, update, interval=100)

plt.show()