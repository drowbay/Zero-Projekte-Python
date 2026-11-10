#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fünf Beobachter – Python-Übertragung der interaktiven Simulation.

Installation: python -m pip install matplotlib
Start:        python fuenf_beobachter.py

Modell: spezielle Relativität in einer Raumdimension, c = 1 Lichtsekunde/s.
L und R blitzen im Ausgangssystem bei t=0 an x=-1 und x=+1 auf.
Beobachter bewegen sich geradlinig: x(t)=x0+v*t, |v|<1.
Zeilen im Bild sind nur eine grafische Trennung, keine Querabstände.
Alle Positionen sind berechnete gleichzeitige Positionen im gewählten
Bezugssystem, keine optische Kameraansicht. A/B und C/D/E werden physikalisch
identisch behandelt; Beobachten verursacht keine zusätzliche Zeitänderung.

Lorentz-Transformation: t'=gamma*(t-u*x), x'=gamma*(x-u*t).
Die Wahl A–E legt die Geschwindigkeit u fest. Der Koordinatenursprung bleibt
am gemeinsamen Ausgangsereignis (t,x)=(0,0), nicht beim Standort der Person.
Ereignisdifferenz R-L: -2*gamma(v)*v.
Empfangsdifferenz: Eigenzeit zwischen beiden Lichtankünften an der Person.
Geschwindigkeitsänderungen erzeugen ein neues Inertialszenario, keine
physikalische Beschleunigung während desselben Experiments.

Matplotlib benötigt für die Bedienung ein interaktives Grafik-Backend.
Auf Android hängt dessen Verfügbarkeit von der Python-App ab.
"""
from math import sqrt
from time import perf_counter
from dataclasses import dataclass


@dataclass
class Observer:
    name: str
    v: float
    x0: float


def gamma(v):
    if abs(v) >= 1:
        raise ValueError('Der Betrag von v/c muss kleiner als 1 sein.')
    return 1 / sqrt(1 - v*v)


def reception_time(observer, source_x):
    distance = source_x - observer.x0
    direction = 1 if distance > 0 else -1 if distance < 0 else 0
    return abs(distance) / (1 + direction * observer.v)


def differences(observer):
    g = gamma(observer.v)
    return (-2*g*observer.v,
            (reception_time(observer, 1)-reception_time(observer, -1))/g)


def position(observer, frame_v, frame_time):
    g = gamma(frame_v)
    return (observer.x0/g + (observer.v-frame_v)*frame_time)/(1-frame_v*observer.v)


def order(delta, reception=False):
    if abs(delta) < 1e-9:
        return 'zusammen empfangen' if reception else 'gleichzeitig'
    return ('R' if delta < 0 else 'L') + (' zuerst empfangen' if reception else ' früher')


def number(value):
    return f'{0 if abs(value)<0.0005 else value:.3f}'.replace('.', ',')


class Simulation:
    def __init__(self):
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Slider, Button, RadioButtons
        self.plt = plt
        self.people = [Observer('A',0,0), Observer('B',-.6,0),
                       Observer('C',0,.5), Observer('D',.4,-.3), Observer('E',0,-.5)]
        self.frame = 'A'
        self.running = False
        self.last = perf_counter()
        self.fig = plt.figure(figsize=(10, 10))
        self.fig.canvas.manager.set_window_title('Zero · Fünf Beobachter')
        self.fig.suptitle('Fünf Beobachter · zwei Lichtblitze', fontsize=17)
        self.scene = self.fig.add_axes([.11,.62,.84,.28])
        self.fig.text(.11,.925,'Berechnete Positionen · Zeilen schematisch · L durchgezogen / R gestrichelt', fontsize=9)
        self.radio_ax = self.fig.add_axes([.04,.36,.12,.17])
        self.radio_ax.set_title('Ansicht', fontsize=10)
        self.radio = RadioButtons(self.radio_ax, list('ABCDE'))
        self.radio.on_clicked(self.change_frame)
        self.time_slider = Slider(self.fig.add_axes([.24,.535,.49,.025]), 'Zeit (s)', -3, 6,
                                  valinit=0, valstep=.01, valfmt='%1.2f')
        self.time_slider.on_changed(self.draw)
        self.play = Button(self.fig.add_axes([.82,.525,.13,.045]), 'Abspielen')
        self.play.on_clicked(self.toggle)
        self.sliders = []
        for i,p in enumerate(self.people):
            ax = self.fig.add_axes([.33,.48-i*.033,.56,.019])
            slider = Slider(ax, f'{p.name}  v/c', -.85,.85,valinit=p.v,valstep=.05,valfmt='%1.2f')
            slider.on_changed(lambda val, index=i: self.change_speed(index,val))
            self.sliders.append(slider)
        self.results = self.fig.add_axes([.06,.09,.89,.235])
        self.results.axis('off')
        self.fig.text(.06,.058,'Differenzen: R minus L · Geschwindigkeiten relativ zum Ausgangssystem', fontsize=9)
        self.fig.text(.06,.035,'Blitzabstand: 2 Lichtsekunden · Ereignisse dort bei t = 0 s · Abspieltempo: 0,55 s/s', fontsize=9)
        self.timer = self.fig.canvas.new_timer(interval=40)
        self.timer.add_callback(self.tick)
        self.fig.canvas.mpl_connect('close_event', lambda event: self.timer.stop())
        self.draw()

    def pause(self):
        self.running = False
        self.timer.stop()
        self.play.label.set_text('Abspielen')

    def change_frame(self, name):
        self.pause()
        self.frame = name
        self.draw()

    def change_speed(self, index, value):
        self.people[index].v = float(value)
        self.draw()

    def toggle(self, event=None):
        if self.running:
            self.pause()
        else:
            if self.time_slider.val >= 6:
                self.time_slider.set_val(-3)
            self.running = True
            self.last = perf_counter()
            self.play.label.set_text('Pause')
            self.timer.start()
        self.fig.canvas.draw_idle()

    def tick(self):
        if not self.running:
            return
        now = perf_counter()
        value = min(6, self.time_slider.val+(now-self.last)*.55)
        self.last = now
        self.time_slider.set_val(value)
        if value >= 6:
            self.pause()
            self.fig.canvas.draw_idle()

    def draw(self, unused=None):
        t = self.time_slider.val
        u = next(p.v for p in self.people if p.name == self.frame)
        g = gamma(u)
        positions = [position(p,u,t) for p in self.people]
        fronts = []
        for source, name, color, style in [(-1,'L','tab:blue','-'),(1,'R','tab:orange','--')]:
            event_t = -g*u*source
            if t >= event_t:
                for direction in [-1,1]:
                    fronts.append((g*source+direction*(t-event_t),name,color,style))
        extent = max([3]+[abs(x) for x in positions]+[abs(f[0]) for f in fronts])+.4
        ax = self.scene
        ax.clear()
        ax.set_xlim(-extent,extent)
        ax.set_ylim(4.65,-.8)
        ax.set_yticks(range(5), list('ABCDE'))
        ax.set_xlabel("Ort x′ (Lichtsekunden) · Maßstab passt sich an")
        ax.grid(True, alpha=.2)
        ax.scatter(positions,range(5),color='0.2',s=65,zorder=4)
        for x,name,color,style in fronts:
            ax.axvline(x,color=color,linestyle=style,linewidth=1.8)
            ax.text(x,-.48,name,color=color,ha='center',va='center')
        ax.set_title(f'Bezugssystem {self.frame} · u/c = {u:.2f} · t′ = {t:.2f} s',fontsize=11)
        rows = []
        for p in self.people:
            dt,dr = differences(p)
            rows.append([p.name, number(dt)+' s\n'+order(dt),number(dr)+' s\n'+order(dr,True)])
        self.results.clear()
        self.results.axis('off')
        table = self.results.table(cellText=rows,colLabels=['Person','Ereignisse Δt','Lichtempfang Δτ'],
                                   cellLoc='center',colWidths=[.13,.435,.435],bbox=[0,0,1,1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        for (r,c),cell in table.get_celld().items():
            cell.set_edgecolor('0.85')
            if r == 0:
                cell.set_facecolor('0.94')
        self.fig.canvas.draw_idle()

    def show(self):
        self.plt.show()


def main():
    try:
        Simulation().show()
    except ModuleNotFoundError as exc:
        if exc.name == 'matplotlib':
            raise SystemExit('Matplotlib fehlt. Installation: python -m pip install matplotlib') from exc
        raise


if __name__ == '__main__':
    main()
