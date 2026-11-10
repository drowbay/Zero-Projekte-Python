import numpy as np
import matplotlib.pyplot as plt

def bloch_coords(theta, phi):
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return x, y, z

def plot_multi_states(states):
    u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
    xs = np.cos(u)*np.sin(v); ys = np.sin(u)*np.sin(v); zs = np.cos(v)
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_wireframe(xs, ys, zs, color="orange", alpha=0.3)
    colors = ["red","blue","green","purple","black"]
    for i,(theta,phi,label) in enumerate(states):
        x,y,z = bloch_coords(theta,phi)
        ax.quiver(0,0,0,x,y,z,color=colors[i%len(colors)],linewidth=3,label=label)
        ax.scatter([x],[y],[z],color=colors[i%len(colors)],s=50)
    ax.set_xlim([-1,1]); ax.set_ylim([-1,1]); ax.set_zlim([-1,1])
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.set_title("Bloch-Sphere mit mehreren Zuständen")
    ax.legend(); plt.show()

if __name__ == "__main__":
    states=[(0,0,"|0⟩"),(np.pi,0,"|1⟩"),(np.pi/2,0,"(|0⟩+|1⟩)/√2"),(np.pi/2,np.pi/2,"(|0⟩+i|1⟩)/√2")]
    plot_multi_states(states)
