#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox

# ====== Maze-Definition ======
# 0 = frei, 1 = Wand, S = Start, E = Exit
MAZE = [
    "11111111111111111111",
    "1S00000001000000000E1",
    "10111110101111101101",
    "10000000100000100001",
    "10111110111110111101",
    "10000010000010000001",
    "10111011110111101101",
    "10001000000100001001",
    "10101111110111111001",
    "10000000000000000001",
    "11111111111111111111"
]

TILE = 20  # Tile-Größe in Pixeln

class PhotonMazeGame:
    def __init__(self, canvas: tk.Canvas, info_label: tk.Label):
        self.canvas = canvas
        self.info_label = info_label
        self.width = len(MAZE[0]) * TILE
        self.height = len(MAZE) * TILE

        self.vx = 1
        self.vy = 0
        self.x = 0
        self.y = 0
        self.running = False

        self._draw_maze()
        self.reset()
    
    def _draw_maze(self):
        self.canvas.delete("all")
        self.canvas.config(width=self.width, height=self.height)
        for j, row in enumerate(MAZE):
            for i, cell in enumerate(row):
                x0 = i * TILE
                y0 = j * TILE
                x1 = x0 + TILE
                y1 = y0 + TILE
                if cell == "1":
                    # Wand
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="#222222", outline="#111111")
                elif cell == "E":
                    # Exit
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="#4b0082", outline="#8800ff")

    def reset(self):
        for j, row in enumerate(MAZE):
            i = row.find("S")
            if i != -1:
                self.x = i * TILE + TILE / 2
                self.y = j * TILE + TILE / 2
                break
        self.vx, self.vy = 1, 0
        self.running = True
        self.info_label.config(text="Photon Maze: Pfeiltasten = Richtung ändern")

    def tile_at(self, px, py):
        tx = int(px // TILE)
        ty = int(py // TILE)
        if ty < 0 or ty >= len(MAZE):
            return "1"
        row = MAZE[ty]
        if tx < 0 or tx >= len(row):
            return "1"
        return row[tx]

    def step(self):
        if not self.running:
            return

        # Hintergrund leicht abdunkeln (Trail-Effekt)
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                     fill="black", outline="", stipple="gray50")
        # Maze-Felder neu zeichnen (sehr simpel)
        self._draw_maze()

        # Bewegung
        self.x += self.vx
        self.y += self.vy

        t = self.tile_at(self.x, self.y)
        if t == "1":
            self.running = False
            messagebox.showinfo("Crash", "Du bist gegen eine Wand geknallt.\nNeuer Versuch!")
            self.reset()
        elif t == "E":
            self.running = False
            messagebox.showinfo("Geschafft!", "Labyrinth gemeistert 🎉")
            self.reset()

        # Photon zeichnen
        r = 4
        self.canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r,
                                fill="cyan", outline="cyan")
        # kleines Glow-Fake
        self.canvas.create_oval(self.x - r*2, self.y - r*2,
                                self.x + r*2, self.y + r*2,
                                outline="#00ffff")

class LumiGameHub:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Lumi Game Hub – Photon Edition")

        # Oberer Bereich (für Titel / Buttons)
        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        self.info_label = tk.Label(top_frame, text="Willkommen im Lumi Game Hub ✨")
        self.info_label.pack(side=tk.LEFT, padx=8, pady=4)

        btn_frame = tk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT, padx=8)

        self.btn_photon = tk.Button(btn_frame, text="Photon Maze starten",
                                    command=self.start_photon_maze)
        self.btn_photon.pack(side=tk.LEFT, padx=4)

        # Placeholder für spätere Spiele
        self.btn_placeholder = tk.Button(btn_frame, text="(frei für nächstes Game)",
                                         state=tk.DISABLED)
        self.btn_placeholder.pack(side=tk.LEFT, padx=4)

        # Canvas für Spiele
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Game-Instanz
        self.photon_game = PhotonMazeGame(self.canvas, self.info_label)

        # Keybindings
        self.root.bind("<Up>", self.on_key)
        self.root.bind("<Down>", self.on_key)
        self.root.bind("<Left>", self.on_key)
        self.root.bind("<Right>", self.on_key)

        # Main-Loop fürs Spiel
        self.loop()

    def start_photon_maze(self):
        self.photon_game.reset()
        self.info_label.config(text="Photon Maze: Labyrinth nicht berühren ✨")

    def on_key(self, event):
        key = event.keysym
        # Richtung ändern – immer nur eine Achse aktiv
        if key == "Up":
            self.photon_game.vx, self.photon_game.vy = 0, -1
        elif key == "Down":
            self.photon_game.vx, self.photon_game.vy = 0, 1
        elif key == "Left":
            self.photon_game.vx, self.photon_game.vy = -1, 0
        elif key == "Right":
            self.photon_game.vx, self.photon_game.vy = 1, 0

    def loop(self):
        # Ein Game-Step
        self.photon_game.step()
        # ca. 60 FPS
        self.root.after(16, self.loop)

def main():
    root = tk.Tk()
    app = LumiGameHub(root)
    root.mainloop()

if __name__ == "__main__":
    main()
