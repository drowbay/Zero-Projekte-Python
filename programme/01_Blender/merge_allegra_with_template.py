#!/usr/bin/env python3
"""
Merge Allegra MIDI with Orchestral Template
-------------------------------------------
Legt deine Allegra-MIDI in das Piano-Track des Orchester-Templates.
Ergebnis: Allegra_Epic.mid
"""

from mido import MidiFile, MidiTrack, Message

# Dateien anpassen:
ALLEGRA_MIDI = "Allegra.mid"                  # deine extrahierte Piano-MIDI
TEMPLATE_MIDI = "orchestra_template.mid"      # vom Template-Script erzeugt
OUTPUT_MIDI = "Allegra_Epic.mid"

def merge_files():
    allegra = MidiFile(ALLEGRA_MIDI)
    template = MidiFile(TEMPLATE_MIDI)
    merged = MidiFile()

    # Template-Tracks kopieren
    for track in template.tracks:
        new_track = MidiTrack()
        for msg in track:
            new_track.append(msg.copy())
        merged.tracks.append(new_track)

    # Allegra-Piano (nur Note-On/Off) auf Kanal 0 schreiben
    piano_track = merged.tracks[0]
    for track in allegra.tracks:
        for msg in track:
            if msg.type in ["note_on", "note_off"]:
                piano_track.append(
                    Message(msg.type, note=msg.note, velocity=msg.velocity,
                            time=msg.time, channel=0)
                )

    merged.save(OUTPUT_MIDI)
    print(f"✅ Fertig: {OUTPUT_MIDI}")

if __name__ == "__main__":
    merge_files()
