import numpy as np import matplotlib.pyplot as plt from matplotlib.animation import FuncAnimation from matplotlib.colors import ListedColormap

============================================================

TIRXY FIELD VIEW — Milestone 1

------------------------------------------------------------

Idee:

Tirxy = Form + Zustand + Regel + Lücke + Bewegung -> Emergenz



Dieses Script zeigt:

- ein Raster/Feld

- Tetris-artige Formen als Zustandsbausteine

- fallende/platzierte Formen

- Lücken/Defekte

- Ordnungslinien

- einen einfachen Emergenz-Score



Benötigt:

pip install numpy matplotlib



Start:

python tirxy_field_view.py

============================================================

np.random.seed(7)

-----------------------------

Feld-Einstellungen

-----------------------------

WIDTH = 14 HEIGHT = 22 FRAMES = 700 SPAWN_EVERY = 18 DROP_SPEED = 1

Zustände im Feld

EMPTY = 0 STABLE = 1 ORDER = 2 TENSION = 3 DEFECT = 4 ACTIVE = 5 EMERGENCE = 6

Farbkarte:

0 leer / 1 stabil / 2 Ordnung / 3 Spannung / 4 Defekt / 5 aktiv / 6 Emergenz

cmap = ListedColormap([ "#05070d",  # leerer Raum "#2166f3",  # stabiler Zustand "#20c997",  # Ordnung "#ffd43b",  # Spannung "#ff4d4d",  # Defekt "#b197fc",  # aktiver Stein "#ffffff",  # Emergenz ])

-----------------------------

Tirxy-Formen

Jede Form besteht aus lokalen Koordinaten.

-----------------------------

SHAPES = { "I": np.array([[0, 0], [1, 0], [2, 0], [3, 0]]), "O": np.array([[0, 0], [1, 0], [0, 1], [1, 1]]), "T": np.array([[0, 0], [1, 0], [2, 0], [1, 1]]), "L": np.array([[0, 0], [0, 1], [0, 2], [1, 2]]), "S": np.array([[1, 0], [2, 0], [0, 1], [1, 1]]), }

def rotate_shape(shape): """Dreht eine Form um 90 Grad und normalisiert sie zurück ins positive Raster.""" rotated = np.array([[y, -x] for x, y in shape]) rotated[:, 0] -= rotated[:, 0].min() rotated[:, 1] -= rotated[:, 1].min() return rotated

def random_shape(): """Erzeugt einen zufälligen Tirxy-Stein mit zufälliger Rotation.""" name = np.random.choice(list(SHAPES.keys())) shape = SHAPES[name].copy() rotations = np.random.randint(0, 4) for _ in range(rotations): shape = rotate_shape(shape) return name, shape

def can_place(field, shape, pos): """Prüft, ob eine Form an einer Position platziert werden kann.""" px, py = pos for x, y in shape: gx = px + x gy = py + y if gx < 0 or gx >= WIDTH or gy < 0 or gy >= HEIGHT: return False if field[gy, gx] != EMPTY: return False return True

def place_shape(field, shape, pos, value=STABLE): """Schreibt eine Form ins Feld.""" px, py = pos for x, y in shape: gx = px + x gy = py + y if 0 <= gx < WIDTH and 0 <= gy < HEIGHT: field[gy, gx] = value

def draw_active(base, shape, pos): """Zeichnet den aktiven Stein in eine Kopie des Feldes.""" view = base.copy() place_shape(view, shape, pos, ACTIVE) return view

def mark_tension_and_defects(field): """ Markiert Lücken und Spannung.

Idee:
Eine leere Zelle unter oder zwischen belegten Zellen ist keine reine Leere,
sondern eine strukturelle Spannung: eine mögliche spätere Ordnung.
"""
marked = field.copy()

for y in range(1, HEIGHT - 1):
    for x in range(1, WIDTH - 1):
        if field[y, x] == EMPTY:
            left = field[y, x - 1] != EMPTY
            right = field[y, x + 1] != EMPTY
            below = field[y + 1, x] != EMPTY
            above = field[y - 1, x] != EMPTY

            # Leere zwischen Struktur = Spannung
            if (left and right) or (above and below):
                marked[y, x] = TENSION

            # Leere über tragender Struktur = Defekt/Lücke
            if below and (left or right):
                marked[y, x] = DEFECT

return marked

def detect_order_lines(field): """Erkennt volle Reihen und markiert sie als Ordnung.""" marked = field.copy() full_rows = []

for y in range(HEIGHT):
    occupied = np.count_nonzero(field[y, :] != EMPTY)
    if occupied >= WIDTH - 1:
        full_rows.append(y)
        marked[y, :] = ORDER

return marked, full_rows

def collapse_order(field, full_rows): """ Entfernt geordnete Reihen und lässt das Feld nachrücken. Das ist die Tetris-Logik als Ordnungs-Relaxation. """ if not full_rows: return field

remaining = np.delete(field, full_rows, axis=0)
new_empty = np.zeros((len(full_rows), WIDTH), dtype=int)
return np.vstack([new_empty, remaining])

def emergence_score(field): """Ein einfacher Score für Ordnung minus Defektspannung.""" occupied = np.count_nonzero(field == STABLE) tension = np.count_nonzero(field == TENSION) defects = np.count_nonzero(field == DEFECT) order = np.count_nonzero(field == ORDER)

score = occupied + 2 * order - tension - 2 * defects
return max(score, 0)

-----------------------------

Startzustand

-----------------------------

field = np.zeros((HEIGHT, WIDTH), dtype=int)

active_name, active_shape = random_shape() active_pos = [WIDTH // 2 - 2, 0] frame_counter = 0 score_history = [] last_full_rows = []

-----------------------------

Plot vorbereiten

-----------------------------

fig, ax = plt.subplots(figsize=(6, 9)) fig.canvas.manager.set_window_title("Tirxy Field View — Zero/Lumora")

image = ax.imshow(field, cmap=cmap, vmin=0, vmax=6, interpolation="nearest") ax.set_xticks(np.arange(-0.5, WIDTH, 1), minor=True) ax.set_yticks(np.arange(-0.5, HEIGHT, 1), minor=True) ax.grid(which="minor", color="#243044", linewidth=0.5) ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

text = ax.text( 0.02, 1.02, "", transform=ax.transAxes, fontsize=10, color="white", bbox=dict(facecolor="#111827", alpha=0.8, edgecolor="none", boxstyle="round,pad=0.4"), )

ax.set_title("TIRXY FIELD VIEW", fontsize=16, pad=18)

def spawn_new_piece(): """Erzeugt einen neuen aktiven Stein.""" name, shape = random_shape() max_x = WIDTH - shape[:, 0].max() - 1 start_x = np.random.randint(0, max(1, max_x)) return name, shape, [start_x, 0]

def update(frame): global field, active_name, active_shape, active_pos, frame_counter, last_full_rows

frame_counter += 1

# Aktiven Stein fallen lassen
if frame_counter % DROP_SPEED == 0:
    next_pos = [active_pos[0], active_pos[1] + 1]

    if can_place(field, active_shape, next_pos):
        active_pos = next_pos
    else:
        # Stein wird Teil der Struktur
        place_shape(field, active_shape, active_pos, STABLE)

        # Ordnung prüfen
        order_view, full_rows = detect_order_lines(field)
        last_full_rows = full_rows

        # Bei Ordnung kurz markieren, dann kollabieren lassen
        if full_rows:
            field[:] = order_view
        else:
            active_name, active_shape, active_pos = spawn_new_piece()

# Wenn Ordnung markiert wurde, nach kurzer Phase relaxen
if last_full_rows and frame_counter % 10 == 0:
    field = collapse_order(field, last_full_rows)
    last_full_rows = []
    active_name, active_shape, active_pos = spawn_new_piece()

# Falls Spawn blockiert ist: Feld weich zurücksetzen
if not can_place(field, active_shape, active_pos):
    field[:] = 0
    active_name, active_shape, active_pos = spawn_new_piece()

# Ansicht bauen
view = draw_active(field, active_shape, active_pos)
view = mark_tension_and_defects(view)

# Emergenz-Flackern bei hoher Ordnung
score = emergence_score(view)
score_history.append(score)
if len(score_history) > 80:
    score_history.pop(0)

avg_score = np.mean(score_history) if score_history else 0
if score > avg_score + 20:
    stable_cells = np.argwhere(view == STABLE)
    if len(stable_cells) > 0:
        chosen = stable_cells[np.random.choice(len(stable_cells), size=min(8, len(stable_cells)), replace=False)]
        for y, x in chosen:
            view[y, x] = EMERGENCE

image.set_data(view)

text.set_text(
    f"Stein: {active_name}   Frame: {frame}\n"
    f"Emergenz-Score: {score:.0f}\n"
    f"Tirxy-Regel: Form + Zustand + Lücke + Bewegung -> Ordnung"
)

return image, text

ani = FuncAnimation(fig, update, frames=FRAMES, interval=60, blit=False)

plt.tight_layout() plt.show()