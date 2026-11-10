#!/usr/bin/env python3
import curses
import time

MAZE = [
    "####################",
    "#S       #        E#",
    "# #### # ###### ## #",
    "#      #      #    #",
    "# #### ###### #### #",
    "#    #      #      #",
    "# ### ###### #### ##",
    "#  #       #   #  ##",
    "# # ###### ######  #",
    "#                  #",
    "####################"
]

# # = Wand, ' ' = frei, S = Start, E = Exit

def find_start():
    for y, row in enumerate(MAZE):
        x = row.find("S")
        if x != -1:
            return x, y
    return 1, 1

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    px, py = find_start()
    vx, vy = 1, 0

    while True:
        stdscr.erase()
        # Maze zeichnen
        for y, row in enumerate(MAZE):
            stdscr.addstr(y, 0, row)

        # Photon zeichnen
        stdscr.addstr(py, px, "o")

        stdscr.addstr(len(MAZE)+1, 0,
                      "Photon Maze (Terminal) – Pfeiltasten bewegen, q = quit")

        stdscr.refresh()

        # Eingabe
        try:
            key = stdscr.getch()
        except:
            key = -1

        if key == ord('q'):
            break
        elif key == curses.KEY_UP:
            vx, vy = 0, -1
        elif key == curses.KEY_DOWN:
            vx, vy = 0, 1
        elif key == curses.KEY_LEFT:
            vx, vy = -1, 0
        elif key == curses.KEY_RIGHT:
            vx, vy = 1, 0

        # Bewegung
        nx = px + vx
        ny = py + vy

        if ny < 0 or ny >= len(MAZE):
            continue
        if nx < 0 or nx >= len(MAZE[ny]):
            continue

        tile = MAZE[ny][nx]
        if tile == "#":
            # Crash → zurück zum Start
            px, py = find_start()
            vx, vy = 1, 0
        elif tile == "E":
            stdscr.addstr(len(MAZE)+2, 0, "Geschafft! Drücke eine Taste für Neustart.")
            stdscr.nodelay(False)
            stdscr.getch()
            stdscr.nodelay(True)
            px, py = find_start()
            vx, vy = 1, 0
        else:
            px, py = nx, ny

        time.sleep(0.02)

if __name__ == "__main__":
    curses.wrapper(main)
