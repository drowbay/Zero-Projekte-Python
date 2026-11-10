#!/usr/bin/env python3
import os
import random
import subprocess
import tempfile

# Ordner mit deinen Audiofiles
AUDIO_DIR = os.path.expanduser("/sdcard/ki-transfer/audio")

# Welche Endungen nehmen wir?
EXTS = (".wav", ".mp3", ".ogg", ".flac", ".m4a")

# Wie viele Tracks für einen Mix ungefähr?
TRACK_COUNT = 15   # kannst du erhöhen oder verringern

# Ausgabe-Datei
OUTPUT = os.path.expanduser("~/ki-transer/lumye_radio_session.mp3")


def collect_files():
    if not os.path.isdir(AUDIO_DIR):
        raise SystemExit(f"Ordner {AUDIO_DIR} existiert nicht. Lege ihn an und pack Audio rein.")

    files = []
    for fn in os.listdir(AUDIO_DIR):
        if fn.lower().endswith(EXTS):
            full = os.path.join(AUDIO_DIR, fn)
            files.append(full)

    if not files:
        raise SystemExit(f"Keine Audio-Dateien in {AUDIO_DIR} gefunden.")

    return files


def build_concat_list(files):
    # temporäre Datei für ffmpeg concat
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    path = tmp.name

    with open(path, "w", encoding="utf-8") as f:
        for fp in files:
            # ffmpeg concat braucht dieses Format:
            # file '/pfad/zur/datei'
            f.write(f"file '{fp}'\n")

    return path


def main():
    all_files = collect_files()

    # zufällige Reihenfolge
    random.shuffle(all_files)

    # ggf. auf Limit kürzen
    sel = all_files[:TRACK_COUNT]

    print("[*] Baue Mix aus folgenden Dateien:")
    for f in sel:
        print("   -", f)

    concat_list = build_concat_list(sel)

    # ffmpeg-Aufruf: concat ohne Re-Encode (wenn möglich)
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        OUTPUT,
    ]

    print("\n[*] Starte ffmpeg...")
    print(" ", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("[!] ffmpeg Fehler:", e)
        raise SystemExit(1)

    print(f"\n[✓] Fertig! Datei gespeichert als: {OUTPUT}")
    print("Im Player auf REPEAT stellen → Lumÿè KI-Radio läuft 🎧")


if __name__ == "__main__":
    main()
