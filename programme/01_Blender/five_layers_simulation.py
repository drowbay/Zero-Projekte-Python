
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

FPS=10; DURATION=10; FRAMES=FPS*DURATION; N=90; EXTENT=3.0
x=np.linspace(-EXTENT,EXTENT,N); y=np.linspace(-EXTENT,EXTENT,N)
X,Y=np.meshgrid(x,y); R=np.sqrt(X**2+Y**2)+1e-9; TH=np.arctan2(Y,X)

def fluct(t): return 0.55*np.sin(2.0*X - 1.1*t) + 0.45*np.cos(2.1*Y + 0.8*t)
def grad(t): return np.exp(-0.35*(X**2+Y**2)) + 0.4*np.exp(-1.8*(R-1.3-0.08*np.sin(0.7*t))**2) + 0.15*(np.cos(0.5*t)*X)
def prob(t):
    raw = 0.8*np.sin(1.0*X - 0.7*t) + 0.6*np.cos(0.9*Y + 0.6*t)
    return 1/(1+np.exp(-raw))
def symm(t): return np.cos(1.7*X)*np.cos(1.7*Y) + 0.3*np.tanh(0.9*X + 0.4*np.sin(t))
def info(t):
    a = np.sin(1.9*X + 0.5*t); b = np.cos(1.7*Y - 0.6*t)
    return np.abs(a-b)
def norm(z): z=z-np.mean(z); return z/(np.std(z)+1e-9)
def total(t): return 0.85*norm(fluct(t)) + 0.75*norm(grad(t)) + 0.65*norm(prob(t)) + 0.8*norm(symm(t)) + 0.7*norm(info(t))
def vec(t):
    z = total(t); gy,gx = np.gradient(z); s = symm(t)
    u = 0.65*gx - 0.30*gy + 0.10*np.sin(s)
    v = 0.65*gy + 0.30*gx + 0.10*np.cos(s)
    return u,v

fig,axs=plt.subplots(2,3,figsize=(10,6.4)); axs=axs.ravel()
titles=["Fluctuation","Gradient","Probability bias","Symmetry breaking","Information","Combined field"]
funcs=[fluct,grad,prob,symm,info,total]
ims=[]
for i,ax in enumerate(axs):
    arr=funcs[i](0.0)
    im=ax.imshow(arr,origin="lower",extent=(-EXTENT,EXTENT,-EXTENT,EXTENT),interpolation="bilinear",alpha=0.92)
    ax.set_title(titles[i]); ax.set_xticks([]); ax.set_yticks([]); ims.append(im)
stream=None
def remove_stream(sp):
    if sp is None: return
    try: sp.lines.remove()
    except Exception: pass
    try:
        for p in sp.arrows.patches: p.remove()
    except Exception: pass
def update(frame):
    global stream
    t=frame/FPS
    for i in range(6):
        arr=funcs[i](t); ims[i].set_data(arr)
        lo,hi=np.percentile(arr,5),np.percentile(arr,95)
        ims[i].set_clim(lo, hi if hi>lo else lo+1e-9)
    remove_stream(stream)
    u,v=vec(t)
    speed=np.sqrt(u*u+v*v)
    stream=axs[5].streamplot(x,y,u,v,density=1.0,linewidth=0.35+0.8*speed/(np.max(speed)+1e-9),arrowsize=0.7)
    fig.suptitle(f"Five-layer emergence model   t={t:4.1f}s")
    return ims
ani=FuncAnimation(fig, update, frames=FRAMES, interval=1000/FPS, blit=False)
plt.show()
