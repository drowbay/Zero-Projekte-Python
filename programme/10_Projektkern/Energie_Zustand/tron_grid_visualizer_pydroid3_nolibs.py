# tron_grid_visualizer_pydroid3_nolibs.py
# Zero-dependency Pydroid 3 Version: braucht KEIN numpy, KEIN matplotlib, KEIN ffmpeg.
# Ausgabe: HTML-Animation + SVG-Bilder im Ordner tron_output

import math
import random
from pathlib import Path

ETA_AIR = 1.8e-5
GAMMA = 0.072
M_DROP = 1e-7
R_DROP = 3e-4

B_DRAG = 6 * math.pi * ETA_AIR * R_DROP
F_CAP = 2 * math.pi * R_DROP * GAMMA

HEIGHT = 32
WIDTH = 32
FREQS = [2200, 2600, 3200, 4000, 4800, 5600]
AMPLITUDE_M = 8.0e-6  # kleiner als Original, damit man Fortschritt sieht
SEED = 123


def r_ratio(freq_hz, amplitude_m):
    omega = 2 * math.pi * freq_hz
    f_inert = M_DROP * (omega ** 2) * amplitude_m
    f_drag = B_DRAG * omega * amplitude_m
    return f_inert / (F_CAP + f_drag)


def build_frames():
    random.seed(SEED)
    threshold = []
    for _y in range(HEIGHT):
        row = []
        for _x in range(WIDTH):
            row.append(random.uniform(0.9, 1.6))
        threshold.append(row)

    cleared = [[False for _x in range(WIDTH)] for _y in range(HEIGHT)]
    frames = []
    ratios = []

    for freq in FREQS:
        ratio = r_ratio(freq, AMPLITUDE_M)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (not cleared[y][x]) and ratio > threshold[y][x]:
                    cleared[y][x] = True
        frames.append([row[:] for row in cleared])
        ratios.append(ratio)

    return frames, ratios


def percent(frame):
    total = HEIGHT * WIDTH
    count = 0
    for row in frame:
        for cell in row:
            if cell:
                count += 1
    return 100.0 * count / total


def frame_to_svg(frame, title):
    cell = 14
    pad = 24
    w = WIDTH * cell + pad * 2
    h = HEIGHT * cell + pad * 2 + 42

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">')
    parts.append('<rect width="100%" height="100%" fill="#050712"/>')
    parts.append(f'<text x="{pad}" y="28" fill="#9fffe0" font-family="monospace" font-size="18">{title}</text>')

    y0 = pad + 34
    for y in range(HEIGHT):
        for x in range(WIDTH):
            fill = '#39ffb6' if frame[y][x] else '#0b1a33'
            stroke = '#183b66'
            px = pad + x * cell
            py = y0 + (HEIGHT - 1 - y) * cell
            parts.append(f'<rect x="{px}" y="{py}" width="{cell-2}" height="{cell-2}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')

    parts.append('</svg>')
    return '\n'.join(parts)


def save_svgs(frames, ratios, out_dir):
    svg_files = []
    for i, frame in enumerate(frames):
        p = percent(frame)
        title = f'TRON Grid | {FREQS[i]} Hz | R={ratios[i]:.3f} | {p:.1f}% frei'
        svg = frame_to_svg(frame, title)
        name = f'tron_frame_{i+1}_{FREQS[i]}hz.svg'
        path = out_dir / name
        path.write_text(svg, encoding='utf-8')
        svg_files.append(name)
    return svg_files


def save_html(frames, ratios, out_dir):
    frame_html = []
    for i, frame in enumerate(frames):
        cells = []
        for y in range(HEIGHT - 1, -1, -1):
            for x in range(WIDTH):
                cls = 'cell on' if frame[y][x] else 'cell off'
                cells.append(f'<div class="{cls}"></div>')
        p = percent(frame)
        label = f'{FREQS[i]} Hz | R={ratios[i]:.3f} | {p:.1f}% frei'
        display = 'grid' if i == 0 else 'none'
        frame_html.append(f'''
<section class="frame" style="display:{display}">
  <h2>{label}</h2>
  <div class="grid">{''.join(cells)}</div>
</section>''')

    html = f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TRON Grid Cleaning</title>
<style>
body {{
  margin: 0;
  background: #050712;
  color: #9fffe0;
  font-family: monospace;
  text-align: center;
}}
h1 {{ margin: 18px 8px 6px; font-size: 22px; }}
h2 {{ margin: 8px; font-size: 16px; font-weight: normal; }}
.grid {{
  display: grid;
  grid-template-columns: repeat({WIDTH}, 1fr);
  gap: 2px;
  width: min(92vw, 620px);
  margin: 14px auto;
}}
.cell {{
  aspect-ratio: 1 / 1;
  border: 1px solid #183b66;
  box-sizing: border-box;
}}
.on {{ background: #39ffb6; box-shadow: 0 0 6px #39ffb6; }}
.off {{ background: #0b1a33; }}
button {{
  background: #10284a;
  color: #9fffe0;
  border: 1px solid #39ffb6;
  padding: 10px 14px;
  border-radius: 8px;
  margin: 6px;
}}
.note {{ color: #c7fff0; margin: 10px 18px 22px; font-size: 13px; }}
</style>
</head>
<body>
<h1>TRON Grid Cleaning Progress</h1>
<div>
<button onclick="prevFrame()">Zurück</button>
<button onclick="togglePlay()" id="playbtn">Pause</button>
<button onclick="nextFrame()">Weiter</button>
</div>
{''.join(frame_html)}
<p class="note">Pydroid-3-No-Libs-Version: läuft ohne numpy, matplotlib und ffmpeg. Datei einfach im Browser öffnen.</p>
<script>
let index = 0;
let playing = true;
const frames = Array.from(document.querySelectorAll('.frame'));
function show(i) {{
  frames[index].style.display = 'none';
  index = (i + frames.length) % frames.length;
  frames[index].style.display = 'block';
}}
function nextFrame() {{ show(index + 1); }}
function prevFrame() {{ show(index - 1); }}
function togglePlay() {{
  playing = !playing;
  document.getElementById('playbtn').innerText = playing ? 'Pause' : 'Play';
}}
setInterval(() => {{ if (playing) nextFrame(); }}, 1000);
</script>
</body>
</html>'''
    path = out_dir / 'tron_grid_cleaning.html'
    path.write_text(html, encoding='utf-8')
    return path


def main():
    out_dir = Path('tron_output')
    out_dir.mkdir(exist_ok=True)

    frames, ratios = build_frames()
    svg_files = save_svgs(frames, ratios, out_dir)
    html_path = save_html(frames, ratios, out_dir)

    print('TRON Grid Visualizer - Pydroid 3 NO-LIBS Edition')
    print('------------------------------------------------')
    print('Keine Zusatzpakete nötig. Kein numpy. Kein matplotlib. Kein ffmpeg.')
    print()
    for freq, ratio, frame in zip(FREQS, ratios, frames):
        print(f'{freq:5d} Hz | R={ratio:.3f} | frei={percent(frame):.1f}%')
    print()
    print('[OK] HTML gespeichert:', html_path)
    for name in svg_files:
        print('[OK] SVG gespeichert: ', out_dir / name)
    print()
    print('Öffne diese Datei im Browser:')
    print(html_path)


if __name__ == '__main__':
    main()
