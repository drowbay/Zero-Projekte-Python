#!/usr/bin/env python3
import os

# Ordner mit deinen Radio-Songs
RADIO_DIR = "/sdcard/lumye_radio"

# Playlist-Datei im gleichen Ordner
PLAYLIST_PATH = os.path.join(RADIO_DIR, "lumye_radio.m3u")

# Welche Dateitypen zählen als Audio
AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".flac", ".ogg")

def main():
    if not os.path.isdir(RADIO_DIR):
        print(f"Ordner nicht gefunden: {RADIO_DIR}")
        return

    files = []
    for name in os.listdir(RADIO_DIR):
        if name.lower().endswith(AUDIO_EXTS):
            files.append(name)

    files.sort()

    if not files:
        print("Keine Audiodateien gefunden.")
        return

    with open(PLAYLIST_PATH, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name in files:
            full_path = os.path.join(RADIO_DIR, name)
            f.write(full_path + "\n")

    print(f"Playlist erstellt: {PLAYLIST_PATH}")
    print(f"Anzahl Tracks: {len(files)}")

if __name__ == "__main__":
    main()
