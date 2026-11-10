#!/usr/bin/env python3
"""
lumye_radio_engine.py
Lumyè Radio Engine – Sven's Logic / Annotated Binary Truth + Groove

Bausteine:
- LumiBit: 0/1 + soft (~) + fx (Vertrauen/Gewichtung)
- WaveEngine: sin, cos, tan mit π
- DrumEngine: b/c/h/_/B2 Pattern -> Zeitleiste
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, List, Optional
import math

# ============================================================
# 1. Sven's Logic – Annotated Binary Truth
# ============================================================

BitValue = Literal[0, 1]

@dataclass
class LumiBit:
    """
    value : 0 oder 1   (harte Wahrheitsebene)
    soft  : ~-Markierung (weich / annotiert)
    fx    : Vertrauensfaktor 0.0 – 1.0
    """
    value: BitValue
    soft: bool = False
    fx: float = 1.0

    def __str__(self) -> str:
        base = str(self.value)
        if self.soft:
            base = "~" + base
        if self.fx != 1.0:
            base = f"{base}@fx={self.fx:.2f}"
        return base


def parse_lumi_bits(code: str) -> List[LumiBit]:
    """
    Parst eine einfache Notation wie:
        "1 ~1 0 ~0 1@0.5 ~1@0.3"

    Regeln:
      - '~1' oder '~0'  -> soft=True
      - '@fx=0.7' oder '@0.7' -> fx setzen
    """
    bits: List[LumiBit] = []

    for token in code.split():
        soft = token.startswith("~")
        t = token[1:] if soft else token

        fx = 1.0
        if "@fx=" in t:
            core, fx_part = t.split("@fx=", 1)
            fx = float(fx_part)
        elif "@" in t:
            core, fx_part = t.split("@", 1)
            fx = float(fx_part)
        else:
            core = t

        if core not in ("0", "1"):
            raise ValueError(f"Ungültiger Bit-Wert: {token}")

        bits.append(LumiBit(value=int(core), soft=soft, fx=fx))

    return bits


# ============================================================
# 2. WaveEngine – sin, cos, tan (π-Welt)
# ============================================================

class WaveEngine:
    """
    Kleine Helfer für Wellen / Phasen:
    - t = Zeit (z. B. in Sekunden oder Takten)
    """

    @staticmethod
    def sin_phase(t: float, freq: float = 1.0) -> float:
        """Sinuswelle, Wertbereich [-1, 1]."""
        return math.sin(2 * math.pi * freq * t)

    @staticmethod
    def cos_phase(t: float, freq: float = 1.0) -> float:
        """Cosinuswelle, Wertbereich [-1, 1]."""
        return math.cos(2 * math.pi * freq * t)

    @staticmethod
    def tan_phase(t: float, freq: float = 1.0) -> float:
        """Tangens – Vorsicht, kann stark ausschlagen."""
        return math.tan(2 * math.pi * freq * t)

    @staticmethod
    def wave_mix(t: float, freq: float, fx: float = 1.0) -> float:
        """
        Beispiel-Mix: (sin + cos) * fx
        Kann z. B. als Lautstärke-Envelope oder Modulation benutzt werden.
        """
        val = WaveEngine.sin_phase
