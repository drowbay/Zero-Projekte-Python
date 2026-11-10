# ==========================================================
# Offenraum Pattern Lab - Vergleichs Display Script
# Modus: Neues Ding -> Vergleich -> Nutzen
# ==========================================================

from dataclasses import dataclass
from typing import List


@dataclass
class SystemBaustein:
    name: str
    kategorie: str
    zustand: str
    dynamik: str
    messung: str
    muster: str
    nutzen: str
    realitaets_status: str


# ----------------------------------------------------------
# Bausteine-Datenbank
# ----------------------------------------------------------

bausteine = [
    SystemBaustein(
        name="Lichtlaser",
        kategorie="Welle / Feld",
        zustand="elektromagnetisches Feld E, B",
        dynamik="Maxwell-Gleichungen, kohärente Ausbreitung",
        messung="Intensität I(x) ∝ |E(x)|²",
        muster="saubere Interferenzstreifen",
        nutzen="Referenzsystem für Kohärenz und Interferenz",
        realitaets_status="direkt experimentell nutzbar"
    ),
    SystemBaustein(
        name="Wasserwelle",
        kategorie="Fluid / klassische Welle",
        zustand="Wellenhöhe h(x,t), Geschwindigkeit v(x,t)",
        dynamik="Fluiddynamik, Wellengleichung, Dämpfung",
        messung="Wellenhöhe, Strömungsbild",
        muster="Wellenkämme, Täler, Überlagerung",
        nutzen="sichtbare Analogie für Wellen und Randbedingungen",
        realitaets_status="direkt beobachtbar"
    ),
    SystemBaustein(
        name="Plasma",
        kategorie="geladenes Fluid + Felder",
        zustand="Elektronendichte ne, Temperatur Te, E-Feld, B-Feld",
        dynamik="Lorentzkraft, MHD, Turbulenz, Filamente",
        messung="Leuchtprofil, Spektrum, Dichteprofil",
        muster="diffuse Peaks, Filamente, Flackern",
        nutzen="Brücke zwischen Materie, Feld und Energie",
        realitaets_status="messbar, aber komplex"
    ),
    SystemBaustein(
        name="Atomlaser / BEC",
        kategorie="kohärente Materiewelle",
        zustand="Materiewellenfunktion ψ(x,t)",
        dynamik="Gross-Pitaevskii-Gleichung",
        messung="Dichte n(x,t)=|ψ(x,t)|²",
        muster="Materiewellen-Interferenz",
        nutzen="Brücke zwischen Quantenmaterie, Welle und Zustandsraum",
        realitaets_status="Laborphysik, real existierend"
    ),
    SystemBaustein(
        name="Qubit-System",
        kategorie="Quantenzustand",
        zustand="|ψ⟩ im Hilbert-Raum",
        dynamik="unitäre Zeitentwicklung, Operatoren",
        messung="Wahrscheinlichkeiten P=|⟨x|ψ⟩|²",
        muster="Wahrscheinlichkeitsverteilung, keine direkte 3D-Form",
        nutzen="Grundbaustein für Zustandsräume und Quanteninformation",
        realitaets_status="mathematisch und experimentell fundiert"
    ),
    SystemBaustein(
        name="Zustandsbasierter Energiespeicher",
        kategorie="Energiespeicher-Prinzip",
        zustand="S0 -> S*",
        dynamik="Laden, Halten, Auskoppeln",
        messung="E_out, Wirkungsgrad η",
        muster="Energie-Zustands-Zyklus",
        nutzen="Batterie als Spezialfall, größere Speicherklasse",
        realitaets_status="teilweise technisch, teilweise Forschung"
    )
]


# ----------------------------------------------------------
# Vergleichsfunktionen
# ----------------------------------------------------------

def finde_baustein(name: str):
    name = name.lower()
    for b in bausteine:
        if name in b.name.lower():
            return b
    return None


def zeige_baustein(b: SystemBaustein):
    print("\n" + "=" * 72)
    print(f"BAUSTEIN: {b.name}")
    print("=" * 72)
    print(f"Kategorie:        {b.kategorie}")
    print(f"Zustand:          {b.zustand}")
    print(f"Dynamik:          {b.dynamik}")
    print(f"Messung:          {b.messung}")
    print(f"Muster:           {b.muster}")
    print(f"Nutzen:           {b.nutzen}")
    print(f"Realitätsstatus:  {b.realitaets_status}")


def vergleiche(a: SystemBaustein, b: SystemBaustein):
    print("\n" + "█" * 72)
    print(f"VERGLEICH: {a.name}  VS  {b.name}")
    print("█" * 72)

    rows = [
        ("Kategorie", a.kategorie, b.kategorie),
        ("Zustand", a.zustand, b.zustand),
        ("Dynamik", a.dynamik, b.dynamik),
        ("Messung", a.messung, b.messung),
        ("Muster", a.muster, b.muster),
        ("Nutzen", a.nutzen, b.nutzen),
        ("Status", a.realitaets_status, b.realitaets_status),
    ]

    for titel, links, rechts in rows:
        print(f"\n[{titel}]")
        print(f"  {a.name}: {links}")
        print(f"  {b.name}: {rechts}")


def gemeinsames_schema():
    print("\n" + "=" * 72)
    print("GEMEINSAMES SCHEMA")
    print("=" * 72)

    print("""
S_in  ->  G  ->  Z  ->  M

S_in = Eingangssystem / Zustand
G    = Geometrie / Randbedingung / Kopplung
Z    = Zwischenzustand / Entwicklung
M    = Messbares Muster

Oder für Energiespeicher:

S0 + E_in -> S* -> S0 + E_out

η = E_out / E_in
""")


def neues_ding_einordnen(name: str, vergleich_mit: List[str]):
    neu = finde_baustein(name)

    if not neu:
        print(f"\nBaustein '{name}' nicht gefunden.")
        print("Verfügbare Bausteine:")
        for b in bausteine:
            print(f"- {b.name}")
        return

    zeige_baustein(neu)

    for vergleich_name in vergleich_mit:
        other = finde_baustein(vergleich_name)
        if other:
            vergleiche(neu, other)
        else:
            print(f"\nVergleichsbaustein '{vergleich_name}' nicht gefunden.")


# ----------------------------------------------------------
# Hauptmenü
# ----------------------------------------------------------

def main():
    print("\nOFFENRAUM PATTERN LAB - DISPLAY SCRIPT")
    print("Neues Ding -> Einordnen -> Vergleichen -> Nutzen")
    print("-" * 72)

    gemeinsames_schema()

    print("\nVerfügbare Bausteine:")
    for i, b in enumerate(bausteine, start=1):
        print(f"{i}. {b.name}")

    print("\nBeispiel-Vergleich:")
    neues_ding_einordnen(
        name="Atomlaser",
        vergleich_mit=["Lichtlaser", "Plasma", "Qubit"]
    )

    print("\n" + "=" * 72)
    print("Eigener Vergleich")
    print("=" * 72)

    name = input("Welches neue Ding willst du anschauen? ").strip()
    vergleich = input("Womit vergleichen? Kommagetrennt, z. B. Lichtlaser, Plasma: ").strip()

    if name:
        vergleichsliste = [v.strip() for v in vergleich.split(",") if v.strip()]
        neues_ding_einordnen(name, vergleichsliste)


if __name__ == "__main__":
    main()