import tkinter as tk

class PyGameLite:

    def __init__(self, width=400, height=400):
        self.root = tk.Tk()
        self.root.title("PyGameLite")

        self.canvas = tk.Canvas(self.root, width=width, height=height, bg="black")
        self.canvas.pack()

    def draw_text(self, text, x, y):
        self.canvas.create_text(x, y, text=text, fill="white", font=("Arial", 14))

    def run(self):
        self.root.mainloop()
