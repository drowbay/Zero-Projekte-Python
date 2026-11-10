import os
import random
from pydub import AudioSegment

# ⭐⭐ HIER liegen deine Audio-Dateien ⭐⭐
# Ordner:  ~/ki-transer/audio
AUDIO_DIR = os.path.expanduser("~/ki-transer/audio")

# Diese Dateiendungen werden verwendet
EXTS = (".wav", ".mp3", ".ogg", ".flac", ".m4a")

# Länge eines Abschnitts pro Track (ms)
MIN_SLICE = 25_000   # 25 Sekunden
MAX_SLICE = 90_000   # 90 Sekunden

# Crossfade (ms)
MIN_FADE = 3000
MAX_FADE = 7000

# Länge der Session, die wir bauen (ms)
SESSION = 10 * 60_000   # 10 Minuten

OUTPUT = os.path.expanduser("~/ki-transer/lumye_radio_session.wav")


def load_audio_files():
    if not os.path.isdir(AUDIO_DIR):
        raise RuntimeError(f"Ordner {AUDIO_DIR} existiert nicht. Lege ihn an und pack Audio rein.")

    tracks = []
    for fn in os.listdir(AUDIO_DIR):
        if fn.lower().endswith(EXTS):
            path = os.path.join(AUDIO_DIR, fn)
            try:
                print(f"[+] Lade: {path}")
                seg = AudioSegment.from_file(path).normalize()
                tracks.append(seg)
            except Exception as e:
                print(f"[!] Fehler bei {fn}: {e}")

    if not tracks:
        raise RuntimeError(f"Keine Audio-Dateien in {AUDIO_DIR} gefunden!")
    return tracks


def build_mix(tracks):
    mix = AudioSegment.silent(duration=0)

    while len(mix) < SESSION:
        base = random.choice(tracks)

        if len(base) > MAX_SLICE:
            start = random.randint(0, len(base) - MAX_SLICE)
            dur = random.randint(MIN_SLICE, MAX_SLICE)
            piece = base[start:start+dur]
        else:
            piece = base

        fade = random.randint(MIN_FADE, MAX_FADE)
        piece = piece.fade_in(fade//2).fade_out(fade//2)

        if len(mix) > 0 and random.choice([True, False]):
            mix = mix.append(piece, crossfade=fade)
        else:
            mix += piece

    return mix[:SESSION]


if __name__ == "__main__":
    tracks = load_audio_files()
    final = build_mix(tracks)

    final = final.fade_in(5000).fade_out(6000)

    final.export(OUTPUT, format="wav")
    print(f"\n[✓] Fertig! Datei gespeichert als: {OUTPUT}")
    print("Im Player auf REPEAT stellen → Lumÿè KI-Radio läuft 🎧")
