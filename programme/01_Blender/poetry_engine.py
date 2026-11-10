import random

lines = [
    "Der Wind flüstert durch die Nacht",
    "Sterne tanzen über dem Meer",
    "Gedanken treiben wie Wolken",
    "Zeit fließt durch stille Räume",
    "Ein Funken Hoffnung glüht im Dunkeln",
]

def generate_poem():
    return "\n".join(random.sample(lines, 3))
