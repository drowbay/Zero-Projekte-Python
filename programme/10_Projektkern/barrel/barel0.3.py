#!/usr/bin/env python3
"""
ZeroCore Experimental v0.3
Linux terminal prototype

Combines:
- PNNA state evaluation
- psi-field sandbox
- CFDE-style 3D field evolution
- HSV -> TLS mapping
- HSV -> toy qubit mapping

Important:
TLS/Qubit are experimental mathematical simulation mappings,
not measurements of physical quantum hardware.
"""

import math
import random
import shlex
import time
import hashlib
import hmac
import getpass

VERSION = "0.3.2"
SIZE = 12
MAX_STEPS = 100
SAFETY_LIMIT = 1.5
CFDE_SOFTENING = 1.0
ASCII_LEVELS = " .:-=+*#%@"

MODEL_RELATIONS = {
    "direct": "explicitly represented/calculated in the model",
    "indirect": "represented through related model quantities",
    "open": "relationship intentionally left open for investigation",
    "unspecified": "no model definition currently exists",
}

# Reserved research labels: meanings are intentionally not assigned yet.
H_STATES = {f"H{i}": "unassigned" for i in range(26, 33)}

FEATURE_MATRIX = {
    "Hawking/Horizont": {
        "relation_a": "indirect",
        "relation_b": "direct",
        "research_status": "open / unspecified",
        "h_states": list(H_STATES),
    }
}


class PNNA:
    """Mini state evaluator inherited from the SandboxBase concept."""

    def evaluate(self, energy):
        if energy < 0.3:
            return "stable"
        elif energy < 0.7:
            return "flow"
        return "unstable"


class PsiField:
    """Small stochastic psi-field."""

    def __init__(self, size=5):
        self.size = size
        self.grid = [
            [random.random() for _ in range(size)]
            for _ in range(size)
        ]

    def energy(self):
        return sum(sum(row) for row in self.grid) / (self.size * self.size)

    def update(self):
        for x in range(self.size):
            for y in range(self.size):
                self.grid[x][y] += random.uniform(-0.1, 0.1)


class CFDEField:
    """Dependency-free 3D toy field based on the existing CFDE prototype."""

    def __init__(self, size=SIZE):
        self.size = size
        self.cx = self.cy = self.cz = size // 2
        self.space = [
            [[0.0 for _ in range(size)] for _ in range(size)]
            for _ in range(size)
        ]
        self.space[self.cx][self.cy][self.cz] = 5.0

    def gravity_field(self, x, y, z):
        # Softened inverse-square toy term:
        # avoids the near-singularity of 0.62 / r^2 at the center.
        dx = x - self.cx
        dy = y - self.cy
        dz = z - self.cz
        r2 = dx * dx + dy * dy + dz * dz
        return 0.62 / (r2 + CFDE_SOFTENING * CFDE_SOFTENING)

    def step(self):
        old = self.space
        new = [[row[:] for row in plane] for plane in old]

        for x in range(1, self.size - 1):
            for y in range(1, self.size - 1):
                for z in range(1, self.size - 1):
                    neighbors = (
                        old[x + 1][y][z] +
                        old[x - 1][y][z] +
                        old[x][y + 1][z] +
                        old[x][y - 1][z] +
                        old[x][y][z + 1] +
                        old[x][y][z - 1]
                    ) / 6.0

                    new[x][y][z] += 0.1 * (neighbors - old[x][y][z])
                    new[x][y][z] += self.gravity_field(x, y, z)

        self.space = new

    def ascii_slice(self, z=None):
        """Return a normalized XY ASCII slice through the 3D field."""
        if z is None:
            z = self.cz
        z = max(0, min(int(z), self.size - 1))

        values = [
            self.space[x][y][z]
            for y in range(self.size)
            for x in range(self.size)
        ]
        lo, hi = min(values), max(values)
        span = hi - lo

        lines = []
        for y in range(self.size):
            chars = []
            for x in range(self.size):
                value = self.space[x][y][z]
                norm = 0.0 if span == 0 else (value - lo) / span
                idx = min(len(ASCII_LEVELS) - 1,
                          int(norm * (len(ASCII_LEVELS) - 1)))
                chars.append(ASCII_LEVELS[idx])
            lines.append("".join(chars))

        return z, lo, hi, lines

    def total_energy(self):
        return sum(
            value
            for plane in self.space
            for row in plane
            for value in row
        )

    def center_value(self):
        return self.space[self.cx][self.cy][self.cz]


def field_to_hsv(value):
    v = min(abs(value) / 5.0, 1.0)
    s = min(abs(value), 1.0)
    h = 0.33 if value >= 0 else 0.0
    return h, s, v


def hsv_to_tls(h, s, v):
    phi = 2.0 * math.pi * h
    x = s * math.cos(phi)
    y = s * math.sin(phi)
    z = v
    return x, y, z


def hsv_to_qubit(h, v):
    phi = 2.0 * math.pi * h
    theta = math.pi * (1.0 - v)
    alpha = math.cos(theta / 2.0)
    beta = complex(math.cos(phi), math.sin(phi)) * math.sin(theta / 2.0)
    return alpha, beta


class ZeroCore:
    def __init__(self):
        self.pnna = PNNA()
        self.psi = PsiField()
        self.cfde = CFDEField()
        self.steps = 0
        self.running = True
        self.password_hash = None
        self.locked = False

    def banner(self):
        print(f"""
ZEROCORE EXPERIMENTAL v{VERSION}
────────────────────────────────
FIELD ψ     : ONLINE
PNNA        : ONLINE
CFDE        : ONLINE
SANDBOX     : LOCKED

Zero bleibt Mensch.
Die Maschine bleibt Werkzeug.

Tippe 'help' für Befehle.
""")

    def status(self):
        psi_e = self.psi.energy()
        state = self.pnna.evaluate(psi_e)
        print(f"ψ Energy    : {psi_e:.6f}")
        print(f"PNNA State  : {state}")
        print(f"CFDE Energy : {self.cfde.total_energy():.6f}")
        print(f"Center      : {self.cfde.center_value():.6f}")
        print(f"Steps       : {self.steps}/{MAX_STEPS}")

    def step(self, count=1):
        count = max(1, min(count, 20))

        for _ in range(count):
            if self.steps >= MAX_STEPS:
                print("⛔ Sandbox-Schrittlimit erreicht.")
                return

            self.psi.update()
            self.cfde.step()
            self.steps += 1

            psi_e = self.psi.energy()
            state = self.pnna.evaluate(psi_e)

            if abs(psi_e) > SAFETY_LIMIT:
                print("⛔ ψ-Energie außerhalb der Sandbox-Grenze → STOP")
                self.running = False
                return

            print(
                f"Step {self.steps:03d} | "
                f"ψ={psi_e:.4f} | PNNA={state} | "
                f"CFDE={self.cfde.total_energy():.4f}"
            )

    def field_monitor(self, z=None):
        z, lo, hi, lines = self.cfde.ascii_slice(z)
        print(f"CFDE ASCII FIELD | XY slice z={z}")
        print(f"range {lo:.6f} .. {hi:.6f}")
        print("+" + "-" * self.cfde.size + "+")
        for line in lines:
            print("|" + line + "|")
        print("+" + "-" * self.cfde.size + "+")
        print("low=' '  high='@' (normalized per slice)")

    @staticmethod
    def _hash_password(password):
        return hashlib.sha256(password.encode("utf-8")).digest()

    def password_command(self):
        if self.password_hash is None:
            first = getpass.getpass("Neues lokales ZeroCore-Passwort: ")
            if not first:
                print("Passwort darf nicht leer sein.")
                return
            second = getpass.getpass("Wiederholen: ")
            if first != second:
                print("Passwörter stimmen nicht überein.")
                return
            self.password_hash = self._hash_password(first)
            print("🔐 Passwort für diese Sitzung gesetzt.")
            return

        print("Passwort ist bereits gesetzt.")
        print("Nutze 'lock', um die Konsole zu sperren.")

    def lock(self):
        if self.password_hash is None:
            print("Noch kein Passwort gesetzt. Erst 'psswd' ausführen.")
            return
        self.locked = True
        print("🔒 ZeroCore-Konsole gesperrt.")

    def unlock(self):
        if not self.locked:
            print("Konsole ist nicht gesperrt.")
            return
        attempt = getpass.getpass("ZeroCore-Passwort: ")
        if hmac.compare_digest(self._hash_password(attempt), self.password_hash):
            self.locked = False
            print("🔓 ZeroCore-Konsole entsperrt.")
        else:
            print("⛔ Falsches Passwort.")

    def relations(self):
        print("MODEL RELATION CLASSIFICATION")
        print("-----------------------------")
        for key, value in MODEL_RELATIONS.items():
            print(f"{key:12s}: {value}")

    def hstates(self):
        print("H26-H32 RESEARCH SLOTS")
        print("----------------------")
        for key, value in H_STATES.items():
            print(f"{key}: {value}")
        print("Status: reserved / meanings not yet verified.")

    def matrix(self):
        print("FEATURE MATRIX")
        print("--------------")
        for feature, data in FEATURE_MATRIX.items():
            print(feature)
            print(f"  A              : {data['relation_a']}")
            print(f"  B              : {data['relation_b']}")
            print(f"  research status: {data['research_status']}")
            print(f"  H slots        : {', '.join(data['h_states'])}")

    def tls(self):
        value = self.cfde.center_value()
        h, s, v = field_to_hsv(value)
        x, y, z = hsv_to_tls(h, s, v)
        print(f"Center value : {value:.6f}")
        print(f"HSV          : ({h:.6f}, {s:.6f}, {v:.6f})")
        print(f"TLS vector   : ({x:.6f}, {y:.6f}, {z:.6f})")

    def qubit(self):
        value = self.cfde.center_value()
        h, _, v = field_to_hsv(value)
        alpha, beta = hsv_to_qubit(h, v)
        norm = abs(alpha) ** 2 + abs(beta) ** 2
        print(f"α            : {alpha:.6f}")
        print(f"β            : {beta.real:.6f}{beta.imag:+.6f}j")
        print(f"Norm         : {norm:.6f}")
        print("(Toy mapping — keine physische Qubit-Messung.)")

    def observe(self):
        psi_e = self.psi.energy()
        state = self.pnna.evaluate(psi_e)
        center = self.cfde.center_value()

        print("OBSERVATION")
        print("───────────")
        print(f"ψ-Feld       : {psi_e:.6f}")
        print(f"Muster       : {state}")
        print(f"CFDE-Zentrum : {center:.6f}")

        if state == "stable":
            print("Interpretation: geringe simulierte Feldaktivität.")
        elif state == "flow":
            print("Interpretation: mittlere simulierte Feldaktivität / Flow.")
        else:
            print("Interpretation: hohe simulierte Feldaktivität.")

    @staticmethod
    def help():
        print("""
Befehle:
  help              Befehle anzeigen
  status            Systemstatus
  step [n]          1 bis 20 Simulationsschritte
  energy            Energieübersicht
  tls               TLS-Vektor des CFDE-Zentrums
  qubit             Toy-Qubit-Mapping
  observe           PNNA/Feld-Beobachtung
  relations          Modellklassen anzeigen
  matrix             Feature-Matrix anzeigen
  hstates            Forschungs-Slots H26-H32 anzeigen
  field [z]          ASCII-Feldmonitor; optional Z-Ebene 0..11
  psswd              Sitzungspasswort setzen
  lock               Konsole sperren
  unlock             Konsole entsperren
  reset              Simulation zurücksetzen
  clear             Terminal leeren
  about             Hinweise zum Modell
  exit / quit       ZeroCore beenden
""")

    @staticmethod
    def about():
        print(f"""ZeroCore Experimental v{VERSION}

PNNA klassifiziert die simulierte ψ-Feldenergie.
CFDE entwickelt ein diskretes 3D-Toy-Feld.
TLS und Qubit sind mathematische Abbildungen des Simulationswertes.\nSie stellen keine reale Quantenhardware oder physikalische Messung dar.\n\nv0.3.2: Modellklassen plus reservierte H26-H32-Forschungsslots.\nH26-H32 bleiben bis zur Quellenprüfung unassigned.\n""")

    def reset(self):
        self.pnna = PNNA()
        self.psi = PsiField()
        self.cfde = CFDEField()
        self.steps = 0
        print("↻ ZeroCore-Simulation zurückgesetzt.")

    def execute(self, line):
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            print(f"Eingabefehler: {exc}")
            return

        if not parts:
            return

        cmd = parts[0].lower()

        if self.locked and cmd not in ("unlock", "exit", "quit"):
            print("🔒 Konsole gesperrt. Nutze 'unlock'.")
            return

        if cmd == "help":
            self.help()
        elif cmd == "status":
            self.status()
        elif cmd in ("step", "/step"):
            count = 1
            if len(parts) > 1:
                try:
                    count = int(parts[1])
                except ValueError:
                    print("Bitte eine ganze Zahl verwenden, z.B. step 5")
                    return
            self.step(count)
        elif cmd in ("energy", "/energy"):
            print(f"ψ Energy    : {self.psi.energy():.6f}")
            print(f"CFDE Energy : {self.cfde.total_energy():.6f}")
        elif cmd in ("tls", "/tls"):
            self.tls()
        elif cmd in ("qubit", "/qubit"):
            self.qubit()
        elif cmd == "observe":
            self.observe()
        elif cmd == "relations":
            self.relations()
        elif cmd == "matrix":
            self.matrix()
        elif cmd == "hstates":
            self.hstates()
        elif cmd == "field":
            z = None
            if len(parts) > 1:
                try:
                    z = int(parts[1])
                except ValueError:
                    print("Z muss eine ganze Zahl sein, z.B. field 6")
                    return
            self.field_monitor(z)
        elif cmd == "psswd":
            self.password_command()
        elif cmd == "lock":
            self.lock()
        elif cmd == "unlock":
            self.unlock()
        elif cmd == "reset":
            self.reset()
        elif cmd == "clear":
            print("\033[2J\033[H", end="")
        elif cmd == "about":
            self.about()
        elif cmd in ("exit", "quit"):
            self.running = False
        else:
            print(f"Unbekannter Befehl: {cmd!r}. 'help' zeigt die Befehle.")

    def run(self):
        self.banner()

        while self.running:
            try:
                line = input("zero> ")
            except (EOFError, KeyboardInterrupt):
                print()
                break

            self.execute(line)

        print("ZeroCore beendet. Gute Nacht, Zero.")


if __name__ == "__main__":
    ZeroCore().run()
