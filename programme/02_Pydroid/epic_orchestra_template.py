#!/usr/bin/env python3
"""
Epic Orchestral MIDI Template Generator
---------------------------------------
Creates a modern-cinematic orchestral MIDI template you can open in any DAW.
Tracks:
  1  Piano (place your Allegra melody here)
  2  Violins I
  3  Violins II / Violas
  4  Cellos / Basses
  5  Horns / Trumpets
  6  Percussion (channel 10 – Taikos/Timpani/Snares/Cymbals)
  7  Choir (optional)

Usage:
  pip install midiutil
  python epic_orchestra_template.py

Outputs:
  orchestra_template.mid
  orchestra_template_with_guides.mid  (adds click + low drone for timing/pitch)
"""

from midiutil import MIDIFile

# ---- General MIDI (GM) program numbers (0-127 in most libs) ----
# Using ensemble patches so it sounds full even with simple playback.
GM = {
    "piano": 0,                 # Acoustic Grand Piano (1 in 1-based GM)
    "strings_ens1": 48 - 1,     # String Ensemble 1 (48 -> zero-based 47)
    "strings_ens2": 49 - 1,     # String Ensemble 2 (49 -> zero-based 48)
    "choir_aahs": 53 - 1,       # Choir Aahs (53 -> zero-based 52)
    "brass_section": 62 - 1,    # Brass Section (62 -> zero-based 61)
}

# MIDI channel mapping (0-15), channel 9 is GM Drum channel
CH = {
    "piano": 0,
    "strings_hi": 1,   # Violins I
    "strings_mid": 2,  # Violins II / Violas
    "strings_low": 3,  # Cellos / Basses
    "brass": 4,
    "drums": 9,        # GM percussion
    "choir": 5,
}

def add_program_changes(midi: MIDIFile, tempo: int):
    """Name tracks, set tempo and instruments."""
    names = [
        ("Piano (Allegra)", CH["piano"], GM["piano"]),
        ("Violins I", CH["strings_hi"], GM["strings_ens1"]),
        ("Violins II / Violas", CH["strings_mid"], GM["strings_ens2"]),
        ("Cellos / Basses", CH["strings_low"], GM["strings_ens1"]),
        ("Horns / Trumpets", CH["brass"], GM["brass_section"]),
        ("Percussion (Drums)", CH["drums"], None),  # drums don't use program changes
        ("Choir (Aahs)", CH["choir"], GM["choir_aahs"]),
    ]
    for i, (name, ch, program) in enumerate(names):
        midi.addTrackName(i, 0, name)
        midi.addTempo(i, 0, tempo)
        # Only set program change if not drums
        if program is not None:
            midi.addProgramChange(i, ch, 0, program)

def bars_to_quarter_notes(bars: int, beats_per_bar: int) -> int:
    return bars * beats_per_bar

def add_guide_click(midi: MIDIFile, start_bar: int, total_bars: int, beats_per_bar: int, click_velocity: int = 90):
    """Add a metronome click on the drum channel (channel 10 / index 9)."""
    # GM Drum notes: 37 (Side Stick) for weak beats, 42 (Closed Hi-Hat) for others, 49 (Crash) for downbeats
    strong = 42  # Closed Hi-Hat
    downbeat = 49  # Crash Cymbal 1
    weak = 37  # Side Stick
    for bar in range(start_bar, start_bar + total_bars):
        for beat in range(beats_per_bar):
            note = strong if beat else downbeat
            vel = click_velocity if beat else click_velocity + 10
            midi.addNote(track=5, channel=CH["drums"], pitch=note,
                         time=bar * beats_per_bar + beat, duration=0.25, volume=vel)
            # optional subdivision (weak)
            midi.addNote(track=5, channel=CH["drums"], pitch=weak,
                         time=bar * beats_per_bar + beat + 0.5, duration=0.1, volume=max(40, click_velocity - 20))

def add_low_drone(midi: MIDIFile, channel: int, start_bar: int, length_bars: int, beats_per_bar: int, pitch: int = 36, vel: int = 60):
    """Add a long low drone for pitch reference (Cello/Bass)."""
    total_quarters = bars_to_quarter_notes(length_bars, beats_per_bar)
    start_qn = start_bar * beats_per_bar
    midi.addNote(track=3, channel=channel, pitch=pitch, time=start_qn, duration=total_quarters, volume=vel)

def add_placeholder_pads(midi: MIDIFile, channel: int, start_bar: int, length_bars: int, beats_per_bar: int, pitch: int, vel: int, sustain_bars: int = 2):
    """Sustained pad chords every N bars (very light, editable)."""
    for bar in range(start_bar, start_bar + length_bars, sustain_bars):
        start_qn = bar * beats_per_bar
        dur_qn = sustain_bars * beats_per_bar
        midi.addNote(track=1, channel=channel, pitch=pitch, time=start_qn, duration=dur_qn, volume=vel)

def create_template(filename: str,
                    tempo: int = 120,
                    bars: int = 64,
                    beats_per_bar: int = 4,
                    with_guides: bool = False):
    tracks_total = 7  # as defined above
    midi = MIDIFile(numTracks=tracks_total, removeDuplicates=True, deinterleave=False, ticks_per_quarternote=960)
    add_program_changes(midi, tempo)

    # Count-in: 1 bar silence (so you can come in neatly)
    count_in_bars = 1
    song_start_bar = count_in_bars

    # Optional guides
    if with_guides:
        add_guide_click(midi, start_bar=0, total_bars=bars + count_in_bars, beats_per_bar=beats_per_bar)
        add_low_drone(midi, channel=CH["strings_low"], start_bar=song_start_bar, length_bars=bars, beats_per_bar=beats_per_bar, pitch=36, vel=50)

    # Light placeholder pads (you can delete these later)
    # Violins I: high pad
    add_placeholder_pads(midi, channel=CH["strings_hi"], start_bar=song_start_bar, length_bars=bars, beats_per_bar=beats_per_bar, pitch=72, vel=35, sustain_bars=4)
    # Violins II/Violas: mid pad
    add_placeholder_pads(midi, channel=CH["strings_mid"], start_bar=song_start_bar+2, length_bars=bars-2, beats_per_bar=beats_per_bar, pitch=67, vel=35, sustain_bars=4)
    # Choir: airy pad
    add_placeholder_pads(midi, channel=CH["choir"], start_bar=song_start_bar+4, length_bars=bars-4, beats_per_bar=beats_per_bar, pitch=60, vel=40, sustain_bars=8)

    # Brass: sparse hits on downbeats (edit as needed)
    for bar in range(song_start_bar, song_start_bar + bars, 8):
        time_qn = bar * beats_per_bar
        midi.addNote(track=4, channel=CH["brass"], pitch=55, time=time_qn, duration=2, volume=80)
        midi.addNote(track=4, channel=CH["brass"], pitch=50, time=time_qn + 2, duration=1.5, volume=75)

    # Piano: leave empty – you will paste your Allegra piano MIDI onto channel 1 (CH['piano'])
    # (We add a single very quiet note as a visible placeholder you can delete.)
    midi.addNote(track=0, channel=CH["piano"], pitch=60, time=song_start_bar * beats_per_bar, duration=0.25, volume=1)

    with open(filename, "wb") as f:
        midi.writeFile(f)

if __name__ == "__main__":
    # Main renders
    create_template("orchestra_template.mid", tempo=120, bars=64, beats_per_bar=4, with_guides=False)
    create_template("orchestra_template_with_guides.mid", tempo=120, bars=64, beats_per_bar=4, with_guides=True)
    print("✅ Created: orchestra_template.mid, orchestra_template_with_guides.mid")
