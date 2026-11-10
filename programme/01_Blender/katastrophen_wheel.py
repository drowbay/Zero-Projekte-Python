#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Katastrophen-Wheel – Zero x Lumi (71383) 💙
- Keine externen Libraries (100% Standard-Python) -> roaming/pip-friendly
- Dreht ein Zufallsrad mit Naturkatastrophen + Film/Serien-Prompt-Idee
"""

import random
import time

MANTRA = "71383"

CATEGORIES = [
    "Erdbeben", "Tsunami", "Vulkan", "Tornado", "Hurrikan",
    "Sturmflut", "Überschwemmung", "Dürre", "Waldbrand", "Lawine",
    "Erdrutsch", "Kältewelle", "Hitzewelle", "Sandsturm", "Blizzard",
    "Meteorit", "Sonnensturm", "Pandemie (fiktional)", "Superzelle", "Megagewitter",
]

SETTINGS = [
    "Großstadt", "Kleinstadt", "Insel", "Gebirge", "U-Bahn-System",
    "Kreuzfahrtschiff", "Klinik", "Schule", "Flughafen", "Forschungsstation",
    "Wüste", "Dschungel", "Arktis", "Staudamm", "Küstenstraße"
]

TWISTS = [
    "Stromausfall überall", "Kein Handynetz", "Evakuierung scheitert", "Falscher Alarm zuerst",
    "Zwei Katastrophen gleichzeitig", "Zeitdruck: 60 Minuten", "Einer hat Insiderwissen",
    "Rettungsteam ist selbst betroffen", "Wetter schlägt um", "Ein Tier wird zum Schlüssel",
    "Ein Kind ist verschwunden", "Ein Zug steckt fest", "Brücke stürzt ein", "Wasser wird knapp",
]

TONE = [
    "realistisch", "düster", "hoffnungsvoll", "heroisch", "dokumentarisch", "trashig (B-Movie)", "emotional"
]

def spin_animation(seconds=2.2):
    chars = "|/-\\"
    end = time.time() + seconds
    i = 0
    while time.time() < end:
        print("\rDrehe Wheel " + chars[i % len(chars)] + "  " + MANTRA, end="")
        time.sleep(0.06)
        i += 1
    print("\r" + " " * 40 + "\r", end="")

def pick():
    cat = random.choice(CATEGORIES)
    setting = random.choice(SETTINGS)
    twist = random.choice(TWISTS)
    tone = random.choice(TONE)
    return cat, setting, twist, tone

def main():
    print("🌪️ Katastrophen-Wheel – Zero x Lumi 💙 71383")
    print("Tippe ENTER zum Drehen. Tippe 'q' und ENTER zum Beenden.\n")

    while True:
        cmd = input(">> ")
        if cmd.strip().lower() == "q":
            print("Okay. Wheel schläft. 🌙")
            break

        spin_animation()
        cat, setting, twist, tone = pick()

        print(f"🎯 Ergebnis:")
        print(f"  • Katastrophe: {cat}")
        print(f"  • Setting:     {setting}")
        print(f"  • Twist:       {twist}")
        print(f"  • Ton:         {tone}")
        print(f"\n📝 Prompt-Idee (Film/Serie):")
        print(f"  „Eine Story über {cat} in einer {setting}-Umgebung,")
        print(f"   mit dem Twist: {twist}. Stil: {tone}.“")
        print(f"  [{MANTRA}]\n")

if __name__ == "__main__":
    main()
