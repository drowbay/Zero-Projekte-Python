#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Lumÿè Drum Machine – GUI mit LED-Buttons & Step-Sequencer
#
# Features:
# - 4 Spuren (Kick, Snare, Hat, FX)
# - 16 Steps
# - Play / Stop
# - BPM-Regler
# - Buttons leuchten wie LEDs (an/aus + aktiver Step)
#
# Zum Anpassen:
#  - SAMPLE_FILES unten mit deinen Pfaden ergänzen/anpassen

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# --- Audio-Backend: pygame ---
try:
    import pygame
    HAVE_PYGAME = True
except ImportError:
    HAVE_PYGAME = False

# ==============================
#  KONFIGURATION
# ==============================

# Hier deine Samples eintragen
# Passe die Pfade an dein System an – z. B.:
#   /sdcard/ki-transfer/audio/...
SAMPLE_FILES = {
    "Kick":   "/sdcard/ki-transfer/audio/Drums 1_tiny.mp3",
    "Snare":  "/sdcard/ki-transfer/audio/Snare 2_tiny.mp3",
    "Hat":    "/sdcard/ki-transfer/audio/Audio 6_tiny.mp3",
    "FX":     "/sdcard/ki-transfer/audio/Crystals_tiny.mp3",
}

TRACK_NAMES = list(SAMPLE_FILES.keys())
NUM_TRACKS = len(TRACK_NAMES)
NUM_STEPS = 16      # 16tel-Grid
DEFAULT_BPM = 100   # Starttempo

# Farben
COLOR_BG       = "#202020"
COLOR_OFF      = "#303030"
COLOR_ON       = "#00ff66"
COLOR_CURRENT  = "#ffff66"
COLOR_ON_CURR  = "#a7ff00"

# ==============================
#  Drum Machine Klasse
# ==============================

class DrumMachine:
    def __init__(self, master):
        self.master = master
        self.master.title("Lumÿè Drum Machine")
        self.master.configure(bg=COLOR_BG)

        # State
        self.bpm = tk.IntVar(value=DEFAULT_BPM)
        self.is_playing = False
        self.current_step = 0
        self.steps = [
            [False] * NUM_STEPS for _ in range(NUM_TRACKS)
        ]

        # pygame init
        self.sounds = {}
        if HAVE_PYGAME:
            pygame.mixer.init()
            self._load_sounds()
        else:
            messagebox.showwarning(
                "Hinweis",
                "pygame ist nicht installiert.\n\n"
                "Bitte mit:\n\npip install pygame\n\ninstallieren, "
                "damit die Drum Machine Sounds abspielen kann."
            )

        self._build_ui()
        self._update_step_highlight()

    def _load_sounds(self):
        for name, path in SAMPLE_FILES.items():
            if os.path.isfile(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"Fehler beim Laden von {path}: {e}")
            else:
                print(f"Sample nicht gefunden: {path}")

    def _build_ui(self):
        # Controls (oben)
        ctrl_frame = tk.Frame(self.master, bg=COLOR_BG)
        ctrl_frame.pack(padx=10, pady=10, fill="x")

        play_btn = ttk.Button(ctrl_frame, text="▶ Play", command=self.start)
        stop_btn = ttk.Button(ctrl_frame, text="■ Stop", command=self.stop)
        play_btn.pack(side="left", padx=5)
        stop_btn.pack(side="left", padx=5)

        bpm_label = tk.Label(ctrl_frame, text="BPM:", fg="white", bg=COLOR_BG)
        bpm_label.pack(side="left", padx=(20, 5))

        bpm_scale = ttk.Scale(
            ctrl_frame,
            from_=60,
            to=180,
            orient="horizontal",
            variable=self.bpm,
            command=lambda v: None
        )
        bpm_scale.pack(side="left", fill="x", expand=True, padx=(0, 10))

        bpm_val_label = tk.Label(
            ctrl_frame,
            textvariable=self.bpm,
            fg="white",
            bg=COLOR_BG,
            width=4
        )
        bpm_val_label.pack(side="left")

        # Grid (unten): LED-Buttons
        grid_frame = tk.Frame(self.master, bg=COLOR_BG)
        grid_frame.pack(padx=10, pady=10)

        self.step_buttons = [
            [None] * NUM_STEPS for _ in range(NUM_TRACKS)
        ]

        for row, track_name in enumerate(TRACK_NAMES):
            # Track-Label
            lbl = tk.Label(
                grid_frame,
                text=track_name,
                fg="white",
                bg=COLOR_BG,
                width=8,
                anchor="e"
            )
            lbl.grid(row=row, column=0, padx=5, pady=3)

            # Steps
            for col in range(NUM_STEPS):
                btn = tk.Button(
                    grid_frame,
                    width=2,
                    height=1,
                    relief="flat",
                    bg=COLOR_OFF,
                    activebackground=COLOR_OFF,
                    command=lambda r=row, c=col: self.toggle_step(r, c)
                )
                btn.grid(row=row, column=col+1, padx=2, pady=2)
                self.step_buttons[row][col] = btn

    def toggle_step(self, track, step):
        self.steps[track][step] = not self.steps[track][step]
        self._update_button_color(track, step)

    def _update_button_color(self, track, step):
        btn = self.step_buttons[track][step]
        active = self.steps[track][step]
        is_current = (step == self.current_step) and self.is_playing

        if active and is_current:
            color = COLOR_ON_CURR
        elif active:
            color = COLOR_ON
        elif is_current:
            color = COLOR_CURRENT
        else:
            color = COLOR_OFF

        btn.configure(bg=color, activebackground=color)

    def _update_step_highlight(self):
        for r in range(NUM_TRACKS):
            for c in range(NUM_STEPS):
                self._update_button_color(r, c)

    def start(self):
        if not HAVE_PYGAME:
            messagebox.showerror(
                "Kein Audio",
                "pygame ist nicht installiert – keine Audioausgabe möglich.\n\n"
                "Installiere es mit:\n\npip install pygame"
            )
            return

        if not self.is_playing:
            self.is_playing = True
            self.current_step = 0
            self._update_step_highlight()
            self._schedule_next_step()

    def stop(self):
        self.is_playing = False
        self._update_step_highlight()

    def _schedule_next_step(self):
        if not self.is_playing:
            return

        bpm = max(1, int(self.bpm.get()))
        # Dauer eines 16tels in ms: 60.000 / (BPM * 4)
        step_ms = int(60000 / (bpm * 4))

        self.master.after(step_ms, self._advance_step)

    def _advance_step(self):
        if not self.is_playing:
            return

        # Aktuellen Step spielen
        self._play_step(self.current_step)

        # Nächster Step
        self.current_step = (self.current_step + 1) % NUM_STEPS
        self._update_step_highlight()
        self._schedule_next_step()

    def _play_step(self, step_index):
        for track_idx, track_name in enumerate(TRACK_NAMES):
            if self.steps[track_idx][step_index]:
                snd = self.sounds.get(track_name)
                if snd is not None:
                    try:
                        snd.play()
                    except Exception as e:
                        print(f"Fehler beim Abspielen von {track_name}: {e}")


def main():
    root = tk.Tk()

    # Tkinter ein bisschen „Windows-Dialog“-Style halten
    try:
        root.iconbitmap("")  # kann leer bleiben oder ein .ico-Pfad sein
    except Exception:
        pass

    app = DrumMachine(root)
    root.mainloop()


if __name__ == "__main__":
    main()
