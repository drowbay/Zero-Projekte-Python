#!/usr/bin/env python3
"""Metal Barrel: Volltrommel, Hohltrommel, beide auf gemeinsamer Achse.

Zoom: + / - Tasten oben, Strg+Mausrad, Strg+0 fuer 100 Prozent.
Scrollen: Scrollleisten, Mausrad; Umschalt+Mausrad fuer seitwaerts.

Start: python barrel_drei_varianten.py
Ohne Grafik / auf dem Handy: python barrel_drei_varianten.py --text
Selbsttest: python barrel_drei_varianten.py --test

CSV wird automatisch neben dem Skript geschrieben (alle 0.1 Simulationssekunden
und bei Befehlen). Ordner muss beschreibbar sein. Waerme ist kumulierte Abgabe,
nicht aktuell gespeicherte Waerme; keine Abkuehlung/Temperatur modelliert.
Ladung bezeichnet verbleibende Drehenergie, keinen elektrischen Akku.

Eigenstaendige Lernsimulation; ersetzt rough.py nicht. Nur Standardbibliothek.
Modell: starre, ausgewuchtete Zylinder, feste Schwerpunktachse, konstante
Drehmomente. Keine Deckel, kein Gravitationsmoment, keine Hardwaresteuerung.
Beide Einzelkoerper haben je 10 kg, R=0.25 m; Hohlzylinder innen 0.20 m.
Das setzt unterschiedliche mittlere Materialdichten voraus, nicht dass beide
aus demselben Metall gefertigt sind. Variante 3 koppelt beide starr: 20 kg.
Start beschleunigt bis 10 rad/s, dann haelt der Motor die Drehzahl.
Auslaufen: Motor aus, Reibung 0.03 Nm. Not-Halt: zusaetzlich 2 Nm Bremse.
Alle Varianten erhalten dasselbe Gesamt-Antriebs-/Bremsmoment.
Eingebrachte Arbeit = Rotationsenergie + abgegebene Waerme (ab Ruhe).
"""

from dataclasses import dataclass
from math import pi, cos, sin, isclose
import sys
import time
import csv
import traceback
from datetime import datetime, timezone
from pathlib import Path

GUI_ROOT = None
GUI_RECORDER = None
GUI_STAGE = "Programmstart"

TARGET = 10.0
MOTOR = 1.0
FRICTION = 0.03
BRAKE = 2.0


@dataclass
class Rotor:
    name: str
    inertia: float
    mass: float
    hollow: bool = False
    omega: float = 0.0
    angle: float = 0.0
    elapsed: float = 0.0
    heat: float = 0.0
    work: float = 0.0
    mode: str = "bereit"
    locked: bool = False

    @property
    def energy(self):
        return 0.5 * self.inertia * self.omega ** 2

    @property
    def charge(self):
        """Percent of rotation energy at target speed; not battery charge."""
        return 100 * (self.omega / TARGET) ** 2

    @property
    def rpm(self):
        return self.omega * 60 / (2 * pi)

    def command(self, action):
        if action == "reset":
            if self.omega > 0:
                return "Erst anhalten; Zuruecksetzen nur im Stillstand."
            self.angle = self.elapsed = self.heat = self.work = 0.0
            self.locked = False
            self.mode = "bereit"
        elif action == "start":
            if self.locked:
                return "Not-Halt verriegelt: erst Stillstand, dann Reset."
            self.mode = "antrieb"
        elif action == "coast" and not self.locked:
            self.mode = "auslaufen"
        elif action == "estop":
            self.locked = True
            self.mode = "not-halt"
        return ""

    def step(self, dt):
        if dt <= 0:
            return
        self.elapsed += dt
        if self.mode == "bereit":
            return
        loss = FRICTION + (BRAKE if self.mode == "not-halt" else 0.0)
        if self.mode == "antrieb":
            accel = (MOTOR - loss) / self.inertia
            ramp = min(dt, max(0.0, (TARGET - self.omega) / accel))
            distance = self.omega * ramp + 0.5 * accel * ramp * ramp
            self.omega = min(TARGET, self.omega + accel * ramp)
            self.work += MOTOR * distance
            self.heat += loss * distance
            hold = self.omega * (dt - ramp)
            self.work += loss * hold
            self.heat += loss * hold
            self.angle += distance + hold
        else:
            # Split at exact stopping time; never reverse due to braking.
            decel = loss / self.inertia
            moving = min(dt, self.omega / decel)
            distance = max(0.0, self.omega * moving - 0.5 * decel * moving ** 2)
            self.angle += distance
            self.heat += loss * distance
            self.omega = max(0.0, self.omega - decel * moving)

    def status(self):
        if self.locked:
            return "BREMST!" if self.omega > 0 else "STEHT / verriegelt"
        if self.omega == 0:
            return "STEHT"
        return "LAEUFT AUS" if self.mode == "auslaufen" else "DREHT"


def make_rotors():
    solid = 0.5 * 10 * 0.25 ** 2
    hollow = 0.5 * 10 * (0.25 ** 2 + 0.20 ** 2)
    return [Rotor("1 Volltrommel", solid, 10),
            Rotor("2 Hohltrommel", hollow, 10, True),
            Rotor("3 Beide gekoppelt", solid + hollow, 20)]


class Recorder:
    """CSV every 0.1 simulation seconds plus commands; flush every batch.

    Heat is cumulative dissipated energy, not retained heat or temperature.
    The logging clock continues across resets; each row also has rotor time.
    UTC is the actual write time, not a reconstructed simulation wall clock.
    """
    def __init__(self, rotors, destination=None):
        self.rotors = rotors
        self.clock = 0.0
        self.until_sample = 0.1
        self.error = ""
        self.file = None
        self.path = Path(destination) if destination else Path(__file__).resolve().parent / (
            "barrel_messwerte_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".csv")
        try:
            self.file = self.path.open("x", newline="", encoding="utf-8-sig")
            self.writer = csv.writer(self.file, delimiter=";")
            self.writer.writerow(["schreibzeit_utc", "aufzeichnung_s", "variante", "ereignis",
                                  "versuchszeit_s", "zustand", "drehzahl_u_min", "drehenergie_j",
                                  "drehenergie_prozent_ziel", "waerme_kumuliert_j", "motorarbeit_j"])
            self.capture("beginn")
        except OSError as exc:
            self.fail(exc)

    def fail(self, exc):
        self.error = "CSV konnte nicht gespeichert werden: " + str(exc)
        if self.file:
            try:
                self.file.close()
            except OSError:
                pass
        self.file = None

    def capture(self, event):
        if self.file is None:
            return
        try:
            stamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            for r in self.rotors:
                self.writer.writerow([stamp, f"{self.clock:.6f}", r.name, event,
                                      f"{r.elapsed:.6f}", r.status(), f"{r.rpm:.6f}",
                                      f"{r.energy:.9f}", f"{r.charge:.6f}",
                                      f"{r.heat:.9f}", f"{r.work:.9f}"])
            self.file.flush()
        except OSError as exc:
            self.fail(exc)

    def advance(self, dt):
        while dt > 1e-10:
            part = min(dt, self.until_sample)
            for r in self.rotors:
                r.step(part)
            self.clock += part
            dt -= part
            self.until_sample -= part
            if self.until_sample < 1e-10:
                self.capture("messpunkt")
                self.until_sample = 0.1

    def close(self):
        self.capture("ende")
        if self.file:
            try:
                self.file.close()
            except OSError as exc:
                self.fail(exc)
            self.file = None


def text_app():
    rotors = make_rotors()
    recorder = Recorder(rotors)
    print("CSV:", recorder.error or recorder.path)
    print("METAL BARREL / drei Varianten nebeneinander")
    print("Beide gekoppelt = zwei Trommeln fest auf einer gemeinsamen Achse.")
    print("start | aus | not | reset | schritt SEKUNDEN | ende")
    print("Zeit laeuft hier nur mit 'schritt', z.B. schritt 1.")
    mapping = {"start": "start", "aus": "coast", "not": "estop", "reset": "reset"}
    while True:
        print("\n" + " | ".join(f"{r.name:^26}" for r in rotors))
        for values in ([r.status() for r in rotors],
                       [f"{r.rpm:.1f} U/min" for r in rotors],
                       [f"Zeit {r.elapsed:.1f} s" for r in rotors],
                       [f"Drehenergie {r.energy:.2f} J" for r in rotors],
                       [f"Ladung (Drehung) {r.charge:.1f} %" for r in rotors],
                       [f"Waerme gesamt {r.heat:.2f} J" for r in rotors]):
            print(" | ".join(f"{v:^26}" for v in values))
        try:
            parts = input("barrel> ").lower().split()
        except (EOFError, KeyboardInterrupt):
            break
        if recorder.error:
            print(recorder.error)
        if not parts:
            continue
        if parts[0] in ("ende", "exit", "quit"):
            break
        if parts[0] in mapping:
            for rotor in rotors:
                message = rotor.command(mapping[parts[0]])
                if message:
                    print(rotor.name + ": " + message)
            recorder.capture(parts[0])
        elif parts[0] == "schritt" and len(parts) == 2:
            try:
                dt = float(parts[1].replace(",", "."))
                if not 0 < dt <= 3600:
                    raise ValueError
                recorder.advance(dt)
            except ValueError:
                print("Bitte eine Zeit groesser 0 bis 3600 Sekunden eingeben.")
        else:
            print("Befehle: start, aus, not, reset, schritt 1, ende")

    recorder.close()

def gui_app():
    global GUI_ROOT, GUI_RECORDER, GUI_STAGE
    GUI_STAGE = "Grafikfenster erstellen"
    import tkinter as tk
    from tkinter import ttk
    root = tk.Tk()
    GUI_ROOT = root
    root.report_callback_exception = show_callback_error
    GUI_STAGE = "Bedienelemente erstellen"
    root.title("Metal Barrel – drei Varianten")
    root.geometry("1100x740")
    root.minsize(320, 300)
    from tkinter import font as tkfont
    toolbar = ttk.Frame(root, padding=5)
    toolbar.pack(fill="x")
    zoom_label = tk.StringVar(value="100 %")
    viewport_frame = ttk.Frame(root)
    viewport_frame.pack(fill="both", expand=True)
    viewport_frame.rowconfigure(0, weight=1)
    viewport_frame.columnconfigure(0, weight=1)
    viewport = tk.Canvas(viewport_frame, highlightthickness=0)
    vertical = ttk.Scrollbar(viewport_frame, orient="vertical", command=viewport.yview)
    horizontal = ttk.Scrollbar(viewport_frame, orient="horizontal", command=viewport.xview)
    viewport.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    viewport.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")
    body = ttk.Frame(viewport)
    viewport.create_window(0, 0, window=body, anchor="nw")
    body.bind("<Configure>", lambda event: viewport.configure(scrollregion=viewport.bbox("all")))
    zoom = 1.0
    rotors = make_rotors()
    recorder = Recorder(rotors)
    GUI_RECORDER = recorder
    ttk.Label(body, text="METAL BARREL · Drehen verstehen", font=("Arial", 19, "bold")).pack(pady=12)
    ttk.Label(body, text="1 und 2: je 10 kg.   3: beide fest auf einer Achse, zusammen 20 kg.").pack()
    ttk.Label(body, text="Gleicher Motor und gleiche Bremse pro Variante. Alle starten aus dem Stillstand.").pack(pady=4)
    area = ttk.Frame(body)
    area.pack(fill="both", expand=True, padx=12)
    panels = []
    note = tk.StringVar(value="Start druecken. Danach Auslaufen oder Not-Halt ausprobieren.")

    def command(action, chosen=None):
        messages = [r.command(action) for r in (rotors if chosen is None else [chosen])]
        recorder.capture(action + (" / alle" if chosen is None else " / " + chosen.name))
        note.set(next((m for m in messages if m), "Befehl ausgefuehrt."))

    for index, rotor in enumerate(rotors):
        area.columnconfigure(index, weight=1, uniform="panels")
        frame = ttk.LabelFrame(area, text=rotor.name, padding=8)
        frame.grid(row=0, column=index, sticky="nsew", padx=4, pady=10)
        canvas = tk.Canvas(frame, width=230, height=190, bg="#111b2c", highlightthickness=0)
        canvas.pack(fill="x")
        values = tk.StringVar()
        ttk.Label(frame, textvariable=values, font=("Arial", 12), justify="center").pack(pady=10)
        for title, action in [("Start", "start"), ("Auslaufen", "coast"), ("Not-Halt", "estop"), ("Reset im Stillstand", "reset")]:
            ttk.Button(frame, text=title, command=lambda a=action, r=rotor: command(a, r)).pack(fill="x", pady=2)
        panels.append((canvas, values))
    controls = ttk.Frame(body)
    controls.pack(pady=6)
    for title, action in [("ALLE STARTEN", "start"), ("ALLE AUSLAUFEN", "coast"), ("ALLE NOT-HALT", "estop"), ("ALLE RESET", "reset")]:
        ttk.Button(controls, text=title, command=lambda a=action: command(a)).pack(side="left", padx=4)
    ttk.Label(body, textvariable=note, wraplength=760).pack(pady=4)
    ttk.Label(body, text="Lernsimulation · feste, ausgewuchtete Achse · keine echte Maschinensteuerung").pack(pady=6)
    save_status = tk.StringVar(value=recorder.error or "CSV alle 0,1 Sekunden: " + str(recorder.path))
    ttk.Label(body, textvariable=save_status, wraplength=950).pack(pady=4)
    ttk.Label(body, text="Ladung = Drehenergie relativ zur Zieldrehzahl (kein Akku). Waerme = insgesamt abgegeben, keine Temperatur.", wraplength=950).pack(pady=4)
    # Keep toolbar fixed; scale content fonts and drawings together.
    scalable_fonts = []
    scalable_wraps = []
    def collect_fonts(widget):
        for child in widget.winfo_children():
            if isinstance(child, (ttk.Label, ttk.Button, ttk.LabelFrame)):
                base = child.cget("font") if isinstance(child, ttk.Label) else "TkDefaultFont"
                font = tkfont.Font(root=root, font=base or "TkDefaultFont")
                size = int(font.cget("size"))
                if isinstance(child, ttk.Label):
                    child.configure(font=font)
                else:
                    style_name = f"Zoom{len(scalable_fonts)}.{child.winfo_class()}"
                    style = ttk.Style(root)
                    style.configure(style_name, font=font)
                    if isinstance(child, ttk.LabelFrame):
                        style.configure(style_name + ".Label", font=font)
                    child.configure(style=style_name)
                scalable_fonts.append((font, size))
                if isinstance(child, ttk.Label):
                    # Tk may return a Tcl_Obj (pixel distance), not a Python number.
                    length = child.winfo_pixels(str(child.cget("wraplength")))
                    if length > 0:
                        scalable_wraps.append((child, length))
                    else:
                        # Long headers must not hold the entire page wide.
                        child.configure(wraplength=950)
                        scalable_wraps.append((child, 950))
            collect_fonts(child)
    GUI_STAGE = "Zoom-Schriften einrichten"
    collect_fonts(body)

    def set_zoom(value):
        nonlocal zoom
        zoom = max(0.25, min(3.0, round(value, 2)))
        zoom_label.set(f"{zoom * 100:.0f} %")
        for font, size in scalable_fonts:
            font.configure(size=(1 if size >= 0 else -1) * max(4, round(abs(size) * zoom)))
        for label, length in scalable_wraps:
            label.configure(wraplength=max(100, round(length * zoom)))
        for canvas, _ in panels:
            canvas.configure(width=round(230 * zoom), height=round(190 * zoom))
        root.update_idletasks()
        viewport.configure(scrollregion=viewport.bbox("all"))

    toolbar.columnconfigure(0, weight=1)
    toolbar.columnconfigure(2, weight=1)
    ttk.Button(toolbar, text="Verkleinern -", command=lambda: set_zoom(zoom - .1)).grid(row=0, column=0, sticky="ew", padx=2)
    ttk.Label(toolbar, textvariable=zoom_label, width=7, anchor="center").grid(row=0, column=1)
    ttk.Button(toolbar, text="Vergroessern +", command=lambda: set_zoom(zoom + .1)).grid(row=0, column=2, sticky="ew", padx=2)
    ttk.Button(toolbar, text="100 %", command=lambda: set_zoom(1.0)).grid(row=1, column=0, sticky="ew", padx=2, pady=3)
    ttk.Button(toolbar, text="Not-Halt alle", command=lambda: command("estop")).grid(row=1, column=2, sticky="ew", padx=2, pady=3)

    def wheel(event):
        number = getattr(event, "num", None)
        delta = getattr(event, "delta", 0)
        direction = 1 if number == 4 or delta > 0 else -1
        if event.state & 0x0004:  # Ctrl + wheel: zoom
            set_zoom(zoom + direction * .1)
        elif event.state & 0x0001:  # Shift + wheel: horizontal
            viewport.xview_scroll(-direction * 3, "units")
        else:
            viewport.yview_scroll(-direction * 3, "units")
        return "break"
    GUI_STAGE = "Maus- und Tastatursteuerung einrichten"
    root.bind_all("<MouseWheel>", wheel)
    root.bind_all("<Button-4>", wheel)
    root.bind_all("<Button-5>", wheel)
    root.bind("<Control-plus>", lambda event: set_zoom(zoom + .1))
    root.bind("<Control-equal>", lambda event: set_zoom(zoom + .1))
    root.bind("<Control-minus>", lambda event: set_zoom(zoom - .1))
    root.bind("<Control-0>", lambda event: set_zoom(1.0))
    # Drag empty background with finger or left mouse button to pan.
    viewport.bind("<ButtonPress-1>", lambda event: viewport.scan_mark(event.x, event.y))
    viewport.bind("<B1-Motion>", lambda event: viewport.scan_dragto(event.x, event.y, gain=1))
    GUI_STAGE = "Anfangsgroesse einstellen"
    set_zoom(1.0)
    last = time.monotonic()

    def tick():
        nonlocal last
        now = time.monotonic()
        dt, last = now - last, now
        recorder.advance(dt)
        if recorder.error:
            save_status.set(recorder.error)
        for i, (r, (canvas, values)) in enumerate(zip(rotors, panels)):
            canvas.delete("all")
            width = max(canvas.winfo_width(), round(180 * zoom))
            shapes = [(width / 2, 95, 68, r.hollow)] if i < 2 else [(width * .29, 95, 43, False), (width * .71, 95, 43, True)]
            if i == 2:
                canvas.create_line(width * .29, 95, width * .71, 95, fill="white", width=5)
            canvas.scale("all", 0, 0, 1, zoom)
            for cx, cy, radius, hollow in shapes:
                cy *= zoom
                radius *= zoom
                color = "#5cd6bc" if not hollow else "#eeb96a"
                canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, fill=color, outline=color)
                if hollow:
                    inner = radius * .8
                    canvas.create_oval(cx-inner, cy-inner, cx+inner, cy+inner, fill="#111b2c", outline=color)
                angle = r.angle % (2*pi)
                canvas.create_line(cx + radius*.83*cos(angle), cy-radius*.83*sin(angle), cx+radius*cos(angle), cy-radius*sin(angle), fill="#f34b65", width=max(2, round(6 * zoom)))
            values.set(f"{r.status()}\n{r.rpm:.1f} Umdrehungen/min\nZeit: {r.elapsed:.1f} s\n\nDrehenergie: {r.energy:.2f} J\nLadung (Drehung): {r.charge:.1f} %\nWaerme gesamt: {r.heat:.2f} J")
        root.after(33, tick)
    GUI_STAGE = "Animation starten"
    tick()
    GUI_STAGE = "Laufender Betrieb"
    try:
        root.mainloop()
    finally:
        recorder.close()


def self_test():
    for r in make_rotors():
        r.command("start")
        r.step(30)
        assert isclose(r.omega, TARGET)
        assert isclose(r.work, r.energy + r.heat, abs_tol=1e-9)
        r.command("coast")
        before = r.omega
        r.step(1)
        assert 0 < r.omega < before
        r.command("estop")
        assert r.command("start")
        r.step(100)
        assert r.omega == 0 and r.locked
        assert isclose(r.work, r.heat, abs_tol=1e-9)
        r.command("reset")
        assert not r.locked and r.work == 0
    one, two, both = make_rotors()
    assert isclose(both.inertia, one.inertia + two.inertia)
    for r in (one, two, both):
        r.command("start")
        r.step(1)
    assert one.omega > two.omega > both.omega
    print("OK: Energiebilanz, Auslaufen, Not-Halt, Verriegelung und drei Traegheiten.")


def show_callback_error(kind, value, tb):
    show_gui_error("".join(traceback.format_exception(kind, value, tb)))


def show_gui_error(details):
    """Keep ordinary Python/Tk errors visible instead of terminal fallback.

    Native process crashes cannot be intercepted by Python.
    """
    message = "BARREL FEHLERANZEIGE / Diagnose 1\nAbschnitt: " + GUI_STAGE + "\n\n" + details
    if GUI_RECORDER is not None:
        GUI_RECORDER.close()
    saved = None
    for directory in (Path(__file__).resolve().parent, Path.home()):
        try:
            saved = directory / "barrel_fehler.txt"
            saved.write_text(message, encoding="utf-8")
            break
        except OSError:
            saved = None
    print(message, flush=True)
    try:
        import tkinter as tk
        root = GUI_ROOT
        if root is None:
            root = tk.Tk()
        # Stop all outstanding animation callbacks before removing controls.
        for pending in root.tk.splitlist(root.tk.call("after", "info")):
            root.after_cancel(pending)
        root.report_callback_exception = lambda *args: traceback.print_exception(*args)
        for child in root.winfo_children():
            child.destroy()
        root.title("Barrel – Fehleranzeige")
        root.geometry("650x650")
        tk.Label(root, text="Bitte diese Fehlermeldung fotografieren.", wraplength=300).pack(pady=8)
        box = tk.Text(root, wrap="word", font=("Arial", 12), height=20, width=35)
        scroll = tk.Scrollbar(root, command=box.yview)
        scroll.pack(side="right", fill="y")
        box.configure(yscrollcommand=scroll.set)
        box.pack(fill="both", expand=True)
        box.insert("1.0", message)
        box.see("end")
        box.configure(state="disabled")
        if saved:
            tk.Label(root, text="Auch gespeichert: " + str(saved), wraplength=300).pack()
        tk.Button(root, text="Schliessen", command=root.destroy).pack(pady=8)
        root.mainloop()
    except Exception:
        traceback.print_exc()
        print("Grafik-Fehleranzeige nicht verfuegbar. Fehlerdatei:", saved, flush=True)


if __name__ == "__main__":
    if "--test" in sys.argv:
        self_test()
    elif "--text" in sys.argv:
        text_app()
    else:
        try:
            gui_app()
        except Exception:
            show_gui_error(traceback.format_exc())
