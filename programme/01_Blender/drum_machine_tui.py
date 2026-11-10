#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Lumÿè Drum Machine – TUI (Text User Interface)
#
# Steuerung:
#   Pfeiltasten  : Cursor bewegen
#   x            : Step an/aus toggeln
#   p            : Play / Stop
#   + / -        : BPM hoch/runter
#   q            : Beenden
#
# Läuft im Terminal (kein DISPLAY nötig).
# Audio über pygame.mixer.

import os
import time
import curses

try:
    import pygame
    HAVE_PYGAME = True
except ImportError:
    HAVE_PYGAME = False

# =========================
# KONFIG
# =========================

# Pfade zu deinen Samples – bei Bedarf anpassen
SAMPLE_FILES = {
    "Kick":   "/sdcard/ki-transfer/audio/Drums 1_tiny.mp3",
    "Snare":  "/sdcard/ki-transfer/audio/Snare 2_tiny.mp3",
    "Hat":    "/sdcard/ki-transfer/audio/Audio 6_tiny.mp3",
    "FX":     "/sdcard/ki-transfer/audio/Crystals_tiny.mp3",
}

TRACK_NAMES = list(SAMPLE_FILES.keys())
NUM_TRACKS = len(TRACK_NAMES)
NUM_STEPS = 16
DEFAULT_BPM = 100

# =========================
# DRUM-MASCHINE
# =========================

class DrumMachineTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.bpm = DEFAULT_BPM
        self.is_playing = False
        self.current_step = 0
        self.cursor_track = 0
        self.cursor_step = 0

        # Grid: [track][step] -> bool
        self.steps = [
            [False] * NUM_STEPS for _ in range(NUM_TRACKS)
        ]

        self.sounds = {}
        if HAVE_PYGAME:
            pygame.mixer.init()
            self._load_sounds()

        # curses setup
        curses.curs_set(0)
        self.stdscr.nodelay(True)   # keine blockierende Eingabe
        self.stdscr.keypad(True)

        self.last_step_time = time.monotonic()

    def _load_sounds(self):
        for name, path in SAMPLE_FILES.items():
            if os.path.isfile(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"Fehler beim Laden von {path}: {e}")
            else:
                print(f"Sample nicht gefunden: {path}")

    def toggle_step(self):
        self.steps[self.cursor_track][self.cursor_step] = not self.steps[self.cursor_track][self.cursor_step]

    def run(self):
        while True:
            self._handle_input()
            self._update_playback()
            self._draw()
            time.sleep(0.01)  # CPU schonen

    def _handle_input(self):
        try:
            key = self.stdscr.getch()
        except KeyboardInterrupt:
            raise SystemExit

        if key == -1:
            return

        if key in (ord('q'), ord('Q')):
            raise SystemExit

        # Play/Stop
        if key in (ord('p'), ord('P')):
            self.is_playing = not self.is_playing
            if self.is_playing:
                self.current_step = 0
                self.last_step_time = time.monotonic()

        # Toggle Step
        if key in (ord('x'), ord('X'), ord(' ')):
            self.toggle_step()

        # BPM ändern
        if key == ord('+'):
            self.bpm = min(260, self.bpm + 1)
        if key == ord('-'):
            self.bpm = max(40, self.bpm - 1)

        # Cursor bewegen
        if key == curses.KEY_UP:
            self.cursor_track = (self.cursor_track - 1) % NUM_TRACKS
        elif key == curses.KEY_DOWN:
            self.cursor_track = (self.cursor_track + 1) % NUM_TRACKS
        elif key == curses.KEY_LEFT:
            self.cursor_step = (self.cursor_step - 1) % NUM_STEPS
        elif key == curses.KEY_RIGHT:
            self.cursor_step = (self.cursor_step + 1) % NUM_STEPS

    def _update_playback(self):
        if not self.is_playing or not HAVE_PYGAME:
            return

        # Dauer eines 16tels in Sekunden
        sec_per_step = 60.0 / (self.bpm * 4.0)
        now = time.monotonic()
        if now - self.last_step_time >= sec_per_step:
            self.last_step_time = now
            # aktuellen Step abspielen
            self._play_step(self.current_step)
            # nächsten Step wählen
            self.current_step = (self.current_step + 1) % NUM_STEPS

    def _play_step(self, step):
        for track_idx, track_name in enumerate(TRACK_NAMES):
            if self.steps[track_idx][step]:
                snd = self.sounds.get(track_name)
                if snd is not None:
                    try:
                        snd.play()
                    except Exception as e:
                        # Kein harter Crash, nur loggen
                        print(f"Fehler beim Abspielen von {track_name}: {e}")

    def _draw(self):
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()

        # Header
        title = "Lumÿè Drum Machine TUI"
        self.stdscr.addstr(0, max(0, (max_x - len(title)) // 2), title, curses.A_BOLD)

        # Status-Zeile
        status = f"BPM: {self.bpm}   Mode: {'PLAY' if self.is_playing else 'STOP'}"
        self.stdscr.addstr(2, 2, status)

        # Hilfe
        help_line = "P=Play/Stop  +/-=BPM  X/Space=Toggle  Pfeile=Move  Q=Quit"
        self.stdscr.addstr(3, 2, help_line)

        # Grid
        top = 5
        left = 4

        # Spalten-Header (Steps)
        for s in range(NUM_STEPS):
            label = f"{(s+1)%10}"
            self.stdscr.addstr(top, left + s*3, label)

        # Tracks & Steps
        for t, tname in enumerate(TRACK_NAMES):
            row_y = top + 2 + t
            # Track-Name
            self.stdscr.addstr(row_y, 0, tname[:3].ljust(3))

            for s in range(NUM_STEPS):
                ch = "·"
                attr = curses.A_DIM

                if self.steps[t][s]:
                    ch = "●"
                    attr = curses.A_BOLD

                # aktueller Step Marker
                if s == self.current_step and self.is_playing:
                    attr |= curses.A_STANDOUT

                # Cursor Marker
                if t == self.cursor_track and s == self.cursor_step:
                    attr |= curses.A_REVERSE

                self.stdscr.addstr(row_y, left + s*3, ch, attr)

        self.stdscr.refresh()


def main(stdscr):
    if not HAVE_PYGAME:
        stdscr.addstr(0, 0, "pygame nicht installiert. Bitte: pip install pygame")
        stdscr.refresh()
        time.sleep(3)
        return

    app = DrumMachineTUI(stdscr)
    try:
        app.run()
    except SystemExit:
        pass


if __name__ == "__main__":
    curses.wrapper(main)
