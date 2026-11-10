#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mjays Leuchthorn / Reality Craft
AFK-Schlafradius Demo mit PyTorch

Idee:
- Nutzer steht in einer Chunk-Welt.
- Wenn aktiv: Umgebung ist normal simuliert.
- Wenn AFK: Die Welt rundherum wird ringförmig schlafen gelegt.
- Kein Kick, kein Countdown, keine Strafe.
- Musikraum bleibt als sanfter Kern aktiv.

Benötigt:
    pip install torch

Start:
    python mjays_afk_sleep_bubble_demo.py
"""

from __future__ import annotations

import time
import math
from enum import Enum
from dataclasses import dataclass

import torch


class CellState:
    """Zellwerte im Welt-Tensor."""
    OFF = 0          # komplett aus / nicht geladen
    SLEEP = 1        # Schlafzone
    SOFT = 2         # sanft aktiv
    ACTIVE = 3       # aktiv simuliert
    PLAYER = 9       # Nutzerposition


class UserMode(str, Enum):
    ACTIVE = "ACTIVE"
    SOFT_AFK = "SOFT_AFK"
    DEEP_AFK = "DEEP_AFK"
    RETURNING = "RETURNING"


@dataclass
class AFKConfig:
    world_size: int = 15

    # Zeitgrenzen in Sekunden für Demo.
    # In einer echten App wären das z.B. 60s, 5min, 20min.
    soft_afk_after: float = 4.0
    deep_afk_after: float = 8.0

    # Radien in Chunk-/Zell-Einheiten
    active_radius: int = 4
    soft_core_radius: int = 2
    deep_core_radius: int = 1
    sleep_radius: int = 4

    # Musikraum darf weiterleben
    music_room_enabled: bool = True


class SleepBubbleEngine:
    """
    Kleine Engine für das AFK-Ruhefeld.

    Psychologische Regel:
    AFK ist kein Fehler.
    AFK bedeutet: Die Umgebung schläft, der Mensch darf ruhen.
    """

    def __init__(self, config: AFKConfig):
        self.cfg = config
        self.center = config.world_size // 2

        self.player_pos = torch.tensor([self.center, self.center], dtype=torch.long)

        self.mode = UserMode.ACTIVE
        self.last_input_time = time.time()
        self.returning_started_at = None

        self.world = torch.zeros(
            (self.cfg.world_size, self.cfg.world_size),
            dtype=torch.int64
        )

    def user_input(self):
        """
        Simuliert Nutzereingabe:
        - Taste gedrückt
        - Maus bewegt
        - Touch
        - App-Fokus zurück
        """
        previous = self.mode
        self.last_input_time = time.time()

        if previous in (UserMode.SOFT_AFK, UserMode.DEEP_AFK):
            self.mode = UserMode.RETURNING
            self.returning_started_at = time.time()
        else:
            self.mode = UserMode.ACTIVE

    def update_mode(self):
        """Bestimmt den Zustand anhand der Inaktivitätszeit."""
        now = time.time()
        inactive_for = now - self.last_input_time

        if self.mode == UserMode.RETURNING:
            # Sanftes Wiederaufwachen statt hartem Umschalten.
            if self.returning_started_at and now - self.returning_started_at > 2.0:
                self.mode = UserMode.ACTIVE
            return

        if inactive_for >= self.cfg.deep_afk_after:
            self.mode = UserMode.DEEP_AFK
        elif inactive_for >= self.cfg.soft_afk_after:
            self.mode = UserMode.SOFT_AFK
        else:
            self.mode = UserMode.ACTIVE

    def distance_grid(self) -> torch.Tensor:
        """
        Erstellt eine Matrix mit Entfernungen zur Nutzerposition.
        Nutzt PyTorch, damit später GPU/AI/Heatmaps möglich wären.
        """
        size = self.cfg.world_size

        y = torch.arange(size).view(size, 1)
        x = torch.arange(size).view(1, size)

        py, px = self.player_pos[0], self.player_pos[1]

        dy = y - py
        dx = x - px

        # Euklidische Entfernung
        dist = torch.sqrt(dx.float() ** 2 + dy.float() ** 2)
        return dist

    def rebuild_world(self):
        """
        Baut die Welt je nach Zustand neu auf.

        ACTIVE:
            Radius aktiv.
        SOFT_AFK:
            Kern sanft aktiv, Außenring schläft, Rest aus.
        DEEP_AFK:
            Nur kleiner Kern bleibt, Schlafring außen, Rest aus.
        RETURNING:
            Umgebung wacht ringförmig wieder auf.
        """
        self.update_mode()

        dist = self.distance_grid()
        world = torch.full_like(self.world, CellState.OFF)

        if self.mode == UserMode.ACTIVE:
            world[dist <= self.cfg.active_radius] = CellState.ACTIVE

        elif self.mode == UserMode.SOFT_AFK:
            world[dist <= self.cfg.sleep_radius] = CellState.SLEEP
            world[dist <= self.cfg.soft_core_radius] = CellState.SOFT

        elif self.mode == UserMode.DEEP_AFK:
            world[dist <= self.cfg.sleep_radius] = CellState.SLEEP
            world[dist <= self.cfg.deep_core_radius] = CellState.SOFT

        elif self.mode == UserMode.RETURNING:
            # sanftes Aufwachen: Welle breitet sich aus
            elapsed = time.time() - (self.returning_started_at or time.time())
            wake_radius = min(self.cfg.active_radius, 1 + int(elapsed * 2))

            world[dist <= self.cfg.sleep_radius] = CellState.SLEEP
            world[dist <= wake_radius] = CellState.ACTIVE

        # Musikraum-Sonderregel:
        # Auch bei AFK bleibt der Herzpunkt als ruhiger Klang-/Lichtkern erhalten.
        if self.cfg.music_room_enabled:
            py, px = self.player_pos.tolist()
            world[py, px] = CellState.PLAYER
        else:
            py, px = self.player_pos.tolist()
            world[py, px] = CellState.PLAYER

        self.world = world

    def simulate_light_intensity(self) -> torch.Tensor:
        """
        Beispiel für leuchtendes Horn / Lichtintensität.

        Nicht medizinisch, nicht mystisch berechnet:
        Nur Visualisierung:
        - aktiv = stärker
        - AFK = ruhiger
        - deep AFK = minimal
        """
        dist = self.distance_grid()

        if self.mode == UserMode.ACTIVE:
            base = torch.exp(-dist / 3.0) * 1.0
        elif self.mode == UserMode.SOFT_AFK:
            base = torch.exp(-dist / 2.0) * 0.55
        elif self.mode == UserMode.DEEP_AFK:
            base = torch.exp(-dist / 1.4) * 0.30
        else:
            base = torch.exp(-dist / 2.5) * 0.75

        return torch.clamp(base, 0.0, 1.0)

    def render_ascii(self) -> str:
        """
        Macht aus der Tensor-Welt eine einfache Textansicht.

        Zeichen:
            . = aus
            z = Schlafzone
            ~ = sanft aktiv / Klangkern
            # = aktiv
            @ = Nutzer
        """
        chars = {
            CellState.OFF: ".",
            CellState.SLEEP: "z",
            CellState.SOFT: "~",
            CellState.ACTIVE: "#",
            CellState.PLAYER: "@",
        }

        lines = []
        for row in self.world.tolist():
            line = " ".join(chars.get(cell, "?") for cell in row)
            lines.append(line)

        return "\n".join(lines)

    def status_text(self) -> str:
        inactive = time.time() - self.last_input_time

        if self.mode == UserMode.ACTIVE:
            message = "Aktiv: Die Umgebung ist wach."
        elif self.mode == UserMode.SOFT_AFK:
            message = "Sanft AFK: Du hörst. Das reicht."
        elif self.mode == UserMode.DEEP_AFK:
            message = "Tief AFK: Die Umgebung schläft. Der Klang bleibt."
        else:
            message = "Rückkehr: Die Welt wacht ringförmig wieder auf."

        return (
            f"Modus: {self.mode.value}\n"
            f"Inaktiv seit: {inactive:0.1f}s\n"
            f"{message}"
        )


def demo_loop():
    cfg = AFKConfig(
        world_size=15,
        soft_afk_after=4.0,
        deep_afk_after=8.0,
        active_radius=5,
        soft_core_radius=2,
        deep_core_radius=1,
        sleep_radius=5,
        music_room_enabled=True,
    )

    engine = SleepBubbleEngine(cfg)

    print("\nMjays Leuchthorn - AFK Schlafradius Demo")
    print("---------------------------------------")
    print("Steuerung:")
    print("  ENTER = Nutzereingabe / zurückkommen")
    print("  q     = beenden")
    print()
    print("Lass das Programm einfach laufen, dann geht es automatisch in SOFT_AFK und DEEP_AFK.")
    print()

    while True:
        engine.rebuild_world()
        light = engine.simulate_light_intensity()

        print("\033[2J\033[H", end="")  # Terminal reinigen
        print(engine.status_text())
        print()
        print(engine.render_ascii())
        print()
        print(f"Horn-Licht Mittelwert: {light.mean().item():0.3f}")
        print()
        print("ENTER = Eingabe simulieren | q + ENTER = Ende")

        # Kleine Nicht-Blockier-Simulation ist in reinem Standard-Python nervig.
        # Daher hier blockierend mit Timeout-Ersatz über kurze Schritte.
        # Für echte Apps nimmt man Event-Loop, pygame, tkinter, asyncio oder Android callbacks.
        start = time.time()
        typed = None

        while time.time() - start < 1.0:
            # In einfacher Konsole können wir nicht sauber plattformübergreifend non-blocking lesen.
            # Darum läuft die Demo pro Frame weiter und akzeptiert Eingabe über input unten nicht live.
            time.sleep(0.1)

        # Kleine Eingabe alle paar Frames:
        # Damit das Script anschaubar bleibt, fragen wir nur alle 3 Sekunden.
        if int(time.time()) % 3 == 0:
            try:
                typed = input("Eingabe optional: ").strip().lower()
            except EOFError:
                typed = ""

            if typed == "q":
                print("Zurück ins Leben. Demo beendet.")
                break
            else:
                engine.user_input()


if __name__ == "__main__":
    demo_loop()
