import tkinter as tk
import random
import time

# -------------------------
# Wave Lab
# -------------------------

def open_wave_lab():

    win = tk.Toplevel()
    win.title("Wave Lab")

    tk.Label(win,text="Wave Lab",font=("Arial",16)).pack(pady=10)
    tk.Label(win,text="Experiments with waves and oscillations").pack()


# -------------------------
# Particle Lab
# -------------------------

def open_particle_lab():

    win = tk.Toplevel()
    win.title("Particle Lab")

    tk.Label(win,text="Particle Lab",font=("Arial",16)).pack(pady=10)
    tk.Label(win,text="Particle interactions and collisions").pack()


# -------------------------
# Quantum Lab
# -------------------------

def open_quantum_lab():

    win = tk.Toplevel()
    win.title("Quantum Lab")

    tk.Label(win,text="Quantum Lab",font=("Arial",16)).pack(pady=10)
    tk.Label(win,text="Bloch Sphere / Qubits").pack()


# -------------------------
# AI Lab
# -------------------------

def open_ai_lab():

    win = tk.Toplevel()
    win.title("AI Lab")

    tk.Label(win,text="AI Lab",font=("Arial",16)).pack(pady=10)
    tk.Label(win,text="PNNA experiments").pack()


# -------------------------
# Color Guess Game
# -------------------------

colors = [
"red","blue","green","yellow","purple",
"orange","pink","cyan","magenta","lime"
]

def open_color_game():

    win = tk.Toplevel()
    win.title("Color Guess Game")

    frame = tk.Frame(win)
    frame.pack(pady=10)

    canvas = tk.Canvas(frame,width=200,height=200,bg="black")
    canvas.pack()

    info = tk.Label(win,text="Guess the hidden color!",font=("Arial",12))
    info.pack(pady=5)

    result = tk.Label(win,text="",font=("Arial",14))
    result.pack(pady=5)

    target = random.choice(colors)

    start_time = time.time()

    def guess(c):

        if time.time() - start_time > 10:
            result.config(text="⏱ Time over!")
            canvas.config(bg=target)
            return

        if c == target:
            canvas.config(bg=target)
            result.config(text="✅ Correct!")
        else:
            result.config(text="❌ Try again!")

    buttons = tk.Frame(win)
    buttons.pack(pady=10)

    for c in random.sample(colors,5):

        tk.Button(
            buttons,
            text=c,
            width=10,
            command=lambda col=c: guess(col)
        ).pack(pady=2)


# -------------------------
# Main CosmicLab Window
# -------------------------

root = tk.Tk()
root.title("Cosmic Lab")
root.geometry("400x450")

title = tk.Label(root,text="COSMIC LAB",font=("Arial",20))
title.pack(pady=20)

tk.Button(root,text="1 Wave Lab",width=25,command=open_wave_lab).pack(pady=5)
tk.Button(root,text="2 Particle Lab",width=25,command=open_particle_lab).pack(pady=5)
tk.Button(root,text="3 Quantum Lab",width=25,command=open_quantum_lab).pack(pady=5)
tk.Button(root,text="4 AI Lab",width=25,command=open_ai_lab).pack(pady=5)
tk.Button(root,text="5 Color Guess Game",width=25,command=open_color_game).pack(pady=10)

root.mainloop()