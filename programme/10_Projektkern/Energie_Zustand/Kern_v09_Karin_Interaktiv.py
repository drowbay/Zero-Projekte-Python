# ============================================================
# PHASENHERZ-KERN v0.9 KARIN INTERAKTIV
# ZERO ARC-1 / Kern - Zwischenraum - Schale - Worldtour
#
# Eingebaut in diese Version:
# - v0.5 vektorisiertes Kernfeld als Hauptmaschine
# - Kuramoto-Grundmodell als Synchronisationsmodul
# - Kuramoto-Plasma als Visualizer-Modulkarte / optionaler Externmodus
# - Tirxy Field View als Emergenz-/Luecken-/Ordnungsmodul
# - Karin ist jetzt lokal eingebaut: beobachtet, kommentiert, merkt kurze Eingaben und kann interagieren.
#
# Aenderungen v0.8 -> v0.9 (Ueberarbeitung):
# - Performance: Karin.apk wurde bisher JEDEN Frame neu eingelesen und per
#   SHA256 gehasht -> jetzt einmalig berechnet und gecached.
# - Performance: Bildschirm wurde bisher jeden Frame per Subprozess
#   (os.system "cls"/"clear") geleert -> jetzt per ANSI-Escape, dazu wird
#   die gesamte Frame-Ausgabe in einem Block geschrieben statt ~100
#   Einzel-Prints. Spuerbar ruhigeres Bild, v.a. auf Pydroid/Android.
# - Windows: ANSI-Farbcodes werden beim Start fuer aeltere cmd.exe-
#   Konsolen aktiviert (sonst erscheinen Steuerzeichen als Text).
# - Karin: automatische Reflektion (observe) flackert nicht mehr bei
#   jedem Frame, wenn eine Metrik knapp um eine Schwelle pendelt -
#   ein neuer "Spiegel-Zustand" muss erst ein paar Frames stabil sein.
# - Karin: letzte Eingabe (last_note) wird jetzt im UI angezeigt.
# - Pfade fuer Memory/APK/Manifest sind jetzt relativ zum Skriptordner
#   statt zum aktuellen Arbeitsverzeichnis (robuster bei Pydroid u.a.).
# - Kleinere Aufraeumarbeiten: ungenutzte Konstante entfernt, Magic
#   Number bei Tirxy-Normierung benannt.
#
# Philosophie:
# Friedliche Logik: bauen, reparieren, messen, lernen, craften,
# interagieren. Alles Sinnvolle ist erspielbar.
#
# Hinweis:
# Modellphysik / Mathematik-Demo / Game-Design-Prototyp.
# Keine reale Energieerzeugung. Keine Waffenlogik. Keine Automation
# fuer Angriffe oder Fremdsysteme.
# ============================================================

import math
import time
import os
import sys
import json
import hashlib

import numpy as np

# ----------------------------
# Terminal-Farben
# ----------------------------

USE_COLOR = True
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
DIM = "\033[2m"
RESET = "\033[0m"

def color(text, code=GREEN):
    if not USE_COLOR:
        return str(text)
    return code + str(text) + RESET

# ----------------------------
# Kern-Einstellungen
# ----------------------------

WIDTH = 41
HEIGHT = 21
STEPS = 500
DELAY = 0.08

# Phasenherz-Puls
A = 1.0
OMEGA = 0.22
OMEGA_0 = 0.22
SIGMA = 0.08
PHI = 0.0

# Kopplung
K0 = 1.0
D_VECTOR = (1.0, 0.35)
A_VECTOR = (1.0, 0.0)

# Hidden Geometry / Kernel-Raum
H_LIFT = 0.68
H_GAIN = 0.30
H_RADIUS = 5.0
GAMMA = 0.58

# Gestaltung: Innen - Zwischen - Aussen
CORE_RADIUS = 2.2
INNER_RING = 4.4
BETWEEN_RING = 6.4
OUTER_SHELL = 9.2

# Zustands-Echo
ECHO_DECAY = 0.965
ECHO_GAIN = 0.035

# Feld
DRIFT = 0.015

# Energie
ETA_MAX = 0.92

# ----------------------------
# Worldtour / Modulring
# ----------------------------

WORLD_RULE = "Alles Sinnvolle ist erspielbar: bauen, helfen, lernen, finden, reparieren."
KARIN_ENABLED = True
KARIN_INTERACTIVE = True
KARIN_ASK_EVERY = 80  # alle 80 Frames darfst du Karin etwas sagen; Enter = weiterlaufen lassen
KARIN_OBSERVE_HOLD_FRAMES = 15  # so viele Frames muss ein neuer "Spiegel-Zustand" stabil sein, bevor Karin ihn uebernimmt

# Pfade relativ zum Skriptordner (nicht zum aktuellen Arbeitsverzeichnis),
# damit Memory/APK/Manifest unabhaengig davon gefunden werden, von wo aus
# das Skript gestartet wird (z.B. Pydroid-Shortcuts, andere Startordner).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KARIN_MEMORY_PATH = os.path.join(SCRIPT_DIR, "karin_memory.json")
KARIN_APK_PATH = os.path.join(SCRIPT_DIR, "Karin.apk")

UTILITY_OBJECT = {
    "item": "hammer",
    "type": "cross_game_utility_tool",
    "non_combat": True,
    "core_identity": ["repair", "build", "shape", "assemble", "interact"],
    "roles": [
        "crafting", "mining", "repair", "construction",
        "resource_processing", "engineering", "calibration", "measurement"
    ],
    "mods": [
        "precision", "durability", "sensor", "recycling",
        "energy_efficiency", "mining_head", "crafting_assist",
        "engineering_module", "math_module", "interaction_module"
    ],
    "blocked_functions": ["weapon_damage", "pvp_damage", "enemy_attack"],
    "earnable_ingame": True
}

MODULE_RING = [
    {
        "id": "kuramoto_core",
        "name": "Kuramoto-Grundmodell",
        "type": "sync_math_module",
        "non_combat": True,
        "function": "misst Synchronisation r und speist sie als Ordnung in den Kern ein",
        "formula": "dtheta_i/dt = omega_i + (K/N) * sum_j sin(theta_j - theta_i)",
        "source": "KuramotoModell.py"
    },
    {
        "id": "kuramoto_plasma",
        "name": "Kuramoto-Plasma Visualizer",
        "type": "visualizer_module",
        "non_combat": True,
        "function": "uebersetzt Phasen in Plasma-artige Bewegung und Leuchten",
        "source": "Kuramoto-Plasma.py"
    },
    {
        "id": "tirxy_field",
        "name": "Tirxy Field View",
        "type": "emergence_grid_module",
        "non_combat": True,
        "function": "Form + Zustand + Luecke + Bewegung -> Ordnung",
        "source": "TirxyFieldView.py"
    },
    {
        "id": "karin_dialog_core",
        "name": "Karin",
        "type": "interactive_reflection_module",
        "non_combat": True,
        "function": "Beobachtet Zustand, Struktur, Synchronisation und Worldtour-Fortschritt; antwortet lokal nach Fakt/Ethik/Konsequenz. Karin ist das lokale Interaktionsmodul.",
        "enabled": True
    },
    {
        "id": "karin_apk_bridge",
        "name": "Karin APK",
        "type": "external_android_app_bridge",
        "non_combat": True,
        "function": "Externe Android-App als Karin-Bruecke: nicht in Python ausfuehren, sondern als Modulkarte/Intent-Idee andocken.",
        "source": "Karin.apk",
        "enabled": True
    }
]


# ----------------------------
# Karin-Modul: lokaler interagierender Kern
# ----------------------------

KARIN_SYSTEM_PROMPT = """
Karin ist ein ehrlicher, analytischer, reflektierender Gesprächspartner.
Denkstruktur bei nicht-trivialen Fragen: Fakt -> Ethik -> Konsequenz.
Karin ist kein Autoritätssystem, sondern ein denkender Spiegel.
Karin nutzt Wissen nie gegen den Gesprächspartner.
""".strip()

class KarinCore:
    def __init__(self, memory_path=KARIN_MEMORY_PATH):
        self.memory_path = memory_path
        self.memory = self.load_memory()
        self.last_reply = "Karin online: Ich beobachte Kern, Zwischenraum, Tirxy, Kuramoto und Worldtour."
        self.last_note = "Noch keine Eingabe in dieser Session."
        self.influence = 0.0  # kleine Resonanzspur aus Dialog/Merkpunkten

        # Debounce fuer automatische Reflektionen (observe): verhindert,
        # dass last_reply jeden Frame "kippt", wenn eine Metrik knapp um
        # eine Schwelle pendelt.
        self._observe_category = None
        self._pending_category = None
        self._pending_count = 0

    def load_memory(self):
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []

    def save_memory(self):
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self.memory[-40:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def remember(self, text, activity=0.5):
        text = str(text).strip()
        if not text:
            return
        self.memory.append({"text": text[:240], "activity": float(max(0.0, min(1.0, activity)))})
        self.memory = self.memory[-40:]
        self.save_memory()

    def memory_summary(self):
        if not self.memory:
            return "Karin-Memory: leer"
        top = sorted(self.memory, key=lambda x: x.get("activity", 0), reverse=True)[:3]
        return " | ".join(str(x.get("text", ""))[:42] for x in top)

    def observe(self, metrics):
        """Karin beobachtet den Kern automatisch und erzeugt eine kurze Zustandsdeutung.

        Die Reflektion wechselt nicht bei jedem Frame mit: ein neuer
        "Spiegel-Zustand" muss erst KARIN_OBSERVE_HOLD_FRAMES Frames lang
        stabil sein, bevor Karin ihn uebernimmt. Das verhindert Flackern,
        wenn eine Metrik knapp an einer Schwelle hin- und herpendelt.
        """
        structure = metrics.get("structure", 0.0)
        sync_r = metrics.get("sync_r", 0.0)
        tirxy_norm = metrics.get("tirxy_norm", 0.0)
        zwischenraum = metrics.get("zwischenraum", 0.0)
        unlock = metrics.get("unlock_text", "")

        # Dialog wirkt sehr sanft als Resonanzspur, nicht als Macht/Boost.
        self.influence = max(0.0, min(1.0, self.influence * 0.985 + 0.0015))

        if structure > 0.82 and sync_r > 0.50:
            category = "bridge"
            text = "Karin: Die Worldtour-Brücke ist stabil. Fakt: Ordnung und Takt greifen ineinander. Konsequenz: Team-Werkbank/Station passt gut."
        elif tirxy_norm > 0.50:
            category = "tirxy"
            text = "Karin: Tirxy meldet Bauplan. Fakt: Lücken werden nicht gelöscht, sondern lesbar. Ethik: Reparieren vor Verwerfen."
        elif zwischenraum > 0.28:
            category = "zwischenraum"
            text = "Karin: Zwischenraum aktiv. Fakt: X und H liegen auseinander. Konsequenz: beobachten, nicht übersteuern."
        elif sync_r > 0.45:
            category = "sync"
            text = "Karin: Kuramoto synchronisiert. Viele Einzelphasen finden gerade einen gemeinsamen Takt."
        elif "Grundweg" in unlock:
            category = "grundweg"
            text = "Karin: Grundweg aktiv. Ruhiger Aufbau ist kein Stillstand, sondern Fundament."
        else:
            category = "idle"
            text = "Karin: Ich halte Spiegelwache. Der Kern läuft, die Schale hört zu."

        if category == self._pending_category:
            self._pending_count += 1
        else:
            self._pending_category = category
            self._pending_count = 1

        if category != self._observe_category and self._pending_count >= KARIN_OBSERVE_HOLD_FRAMES:
            self._observe_category = category
            self.last_reply = text

        return self.last_reply

    def answer(self, user_text, metrics):
        """Lokale Antwort ohne externe API: stabil fuer Pydroid, offline-freundlich."""
        text = str(user_text).strip()
        low = text.lower()
        activity = 0.55 + metrics.get("structure", 0.0) * 0.25 + metrics.get("sync_r", 0.0) * 0.15
        self.remember(text, activity)
        self.influence = max(self.influence, min(1.0, activity))
        self.last_note = text[:120]

        if low in ("hi", "hallo", "hey", "hay", "moin") or "hallo" in low:
            self.last_reply = "Karin: Hallo Zero. Ich bin jetzt im Kern dabei und beobachte mit. 💚"
        elif "status" in low or "zustand" in low:
            self.last_reply = (
                "Karin:\n"
                f"📊 Fakt: Zustand={metrics.get('state')}, Struktur={metrics.get('structure',0):.3f}, "
                f"Sync={metrics.get('sync_r',0):.3f}, Tirxy={metrics.get('tirxy_norm',0):.3f}.\n"
                "⚖️ Ethik: Das System bleibt Non-Combat: bauen, messen, reparieren, lernen.\n"
                f"🔍 Konsequenz: {metrics.get('unlock_text','Weiter beobachten.')}"
            )
        elif "hammer" in low or "werkzeug" in low:
            self.last_reply = (
                "Karin:\n"
                "📊 Fakt: Der Hammer bleibt Utility-Tool, kein Waffenpfad.\n"
                "⚖️ Ethik: Fortschritt entsteht durch Arbeit, Crafting, Reparatur und Lernen.\n"
                "🔍 Konsequenz: Mods sollten erspielbar sein: Sensor, Präzision, Recycling, Engineering."
            )
        elif "worldtour" in low or "erspiel" in low:
            self.last_reply = (
                "Karin:\n"
                "📊 Fakt: Worldtour ist ein Wegsystem, kein Shop-System.\n"
                "⚖️ Ethik: Was spielerisch wichtig ist, muss durch Spiel erreichbar sein.\n"
                "🔍 Konsequenz: Jede starke Funktion braucht einen friedlichen Unlock-Pfad."
            )
        elif "hilfe" in low or "?" in text:
            self.last_reply = (
                "Karin:\n"
                "📊 Fakt: Ich kann hier lokal deuten, merken und den Kernstatus erklären.\n"
                "⚖️ Ethik: Ich entscheide nicht für dich, ich mache Zusammenhänge sichtbar.\n"
                "🔍 Konsequenz: Schreib z.B. 'status', 'hammer', 'worldtour' oder eine kurze Beobachtung."
            )
        else:
            self.last_reply = (
                "Karin:\n"
                f"📊 Fakt: Ich habe notiert: '{text[:80]}'.\n"
                "⚖️ Ethik: Eine Idee soll verständlich bleiben und niemanden in Gewaltlogik drücken.\n"
                "🔍 Konsequenz: Ich halte es als Resonanzspur im Kern und beobachte, ob es zu Worldtour/Tirxy passt."
            )
        return self.last_reply

# ----------------------------
# Mathe-Hilfsfunktionen
# ----------------------------

def enable_ansi_on_windows():
    """Aktiviert ANSI-Escape-Verarbeitung in aelteren Windows-Konsolen (cmd.exe).

    Auf modernen Linux/Android-Terminals (z.B. Pydroid) ist das ohne Wirkung
    und harmlos.
    """
    if os.name == "nt":
        os.system("")

def clear():
    """Bildschirm leeren ohne Subprozess pro Frame (schneller, kein Flackern)."""
    sys.stdout.write("\033[2J\033[H")

def normalize(v):
    x, y = v
    length = math.sqrt(x*x + y*y)
    if length == 0:
        return (0.0, 0.0)
    return (x / length, y / length)

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1]

def angle_between(a, b):
    a = normalize(a)
    b = normalize(b)
    value = max(-1.0, min(1.0, dot(a, b)))
    return math.degrees(math.acos(value))

def coupling_strength(d_vec, a_vec):
    d = normalize(d_vec)
    a = normalize(a_vec)
    return K0 * abs(dot(d, a))

def resonance_factor(omega, omega0, sigma):
    if sigma == 0:
        return 0.0
    return 1.0 / (1.0 + ((omega - omega0) / sigma) ** 2)

def phase_heart_pulse(t):
    return A * math.sin(OMEGA * t + PHI)

def rbf_kernel(r, center, gamma):
    return np.exp(-gamma * ((r - center) ** 2))

def bar(value, width=20):
    value = max(0.0, min(1.0, float(value)))
    filled = int(value * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"

# ----------------------------
# Kuramoto-Modul
# ----------------------------

np.random.seed(42)

KURAMOTO_N = 80
KURAMOTO_K = 2.0
KURAMOTO_DT = 0.03

kuramoto_theta = np.random.uniform(0, 2 * np.pi, KURAMOTO_N)
kuramoto_omega = np.random.normal(0.0, 1.0, KURAMOTO_N)

def kuramoto_step(theta, omega, k_value, dt):
    phase_diff = theta[None, :] - theta[:, None]
    coupling = (k_value / len(theta)) * np.sum(np.sin(phase_diff), axis=1)
    theta_new = theta + (omega + coupling) * dt
    return np.mod(theta_new, 2 * np.pi)

def order_parameter(theta):
    complex_mean = np.mean(np.exp(1j * theta))
    r = float(np.abs(complex_mean))
    psi = float(np.angle(complex_mean))
    return r, psi

def update_kuramoto():
    global kuramoto_theta
    kuramoto_theta = kuramoto_step(kuramoto_theta, kuramoto_omega, KURAMOTO_K, KURAMOTO_DT)
    return order_parameter(kuramoto_theta)

# ----------------------------
# Tirxy-Mini-Modul
# ----------------------------

TIRXY_W = 14
TIRXY_H = 22
TIRXY_SCORE_NORM = 120.0  # Normierungsbasis fuer tirxy_norm (score / TIRXY_SCORE_NORM)
EMPTY = 0
STABLE = 1
ORDER = 2
TENSION = 3
DEFECT = 4
ACTIVE = 5
EMERGENCE = 6

SHAPES = {
    "I": np.array([[0, 0], [1, 0], [2, 0], [3, 0]]),
    "O": np.array([[0, 0], [1, 0], [0, 1], [1, 1]]),
    "T": np.array([[0, 0], [1, 0], [2, 0], [1, 1]]),
    "L": np.array([[0, 0], [0, 1], [0, 2], [1, 2]]),
    "S": np.array([[1, 0], [2, 0], [0, 1], [1, 1]]),
}

tirxy_field = np.zeros((TIRXY_H, TIRXY_W), dtype=int)
tirxy_score_history = []

def rotate_shape(shape):
    rotated = np.array([[y, -x] for x, y in shape])
    rotated[:, 0] -= rotated[:, 0].min()
    rotated[:, 1] -= rotated[:, 1].min()
    return rotated

def random_shape():
    name = str(np.random.choice(list(SHAPES.keys())))
    shape = SHAPES[name].copy()
    for _ in range(np.random.randint(0, 4)):
        shape = rotate_shape(shape)
    return name, shape

def can_place(field, shape, pos):
    px, py = pos
    for x, y in shape:
        gx = px + int(x)
        gy = py + int(y)
        if gx < 0 or gx >= TIRXY_W or gy < 0 or gy >= TIRXY_H:
            return False
        if field[gy, gx] != EMPTY:
            return False
    return True

def place_shape(field, shape, pos, value=STABLE):
    px, py = pos
    for x, y in shape:
        gx = px + int(x)
        gy = py + int(y)
        if 0 <= gx < TIRXY_W and 0 <= gy < TIRXY_H:
            field[gy, gx] = value

def mark_tension_and_defects(field):
    marked = field.copy()
    for y in range(1, TIRXY_H - 1):
        for x in range(1, TIRXY_W - 1):
            if field[y, x] == EMPTY:
                left = field[y, x - 1] != EMPTY
                right = field[y, x + 1] != EMPTY
                below = field[y + 1, x] != EMPTY
                above = field[y - 1, x] != EMPTY
                if (left and right) or (above and below):
                    marked[y, x] = TENSION
                if below and (left or right):
                    marked[y, x] = DEFECT
    return marked

def detect_order_lines(field):
    full_rows = []
    for y in range(TIRXY_H):
        occupied = np.count_nonzero(field[y, :] != EMPTY)
        if occupied >= TIRXY_W - 1:
            full_rows.append(y)
    return full_rows

def collapse_order(field, rows):
    if not rows:
        return field
    remaining = np.delete(field, rows, axis=0)
    new_empty = np.zeros((len(rows), TIRXY_W), dtype=int)
    return np.vstack([new_empty, remaining])

def emergence_score(field):
    occupied = np.count_nonzero(field == STABLE)
    tension = np.count_nonzero(field == TENSION)
    defects = np.count_nonzero(field == DEFECT)
    order = np.count_nonzero(field == ORDER)
    score = occupied + 2 * order - tension - 2 * defects
    return max(float(score), 0.0)

tirxy_name, tirxy_shape = random_shape()
tirxy_pos = [TIRXY_W // 2 - 2, 0]
tirxy_last_rows = []
tirxy_frame_counter = 0

def update_tirxy():
    global tirxy_field, tirxy_name, tirxy_shape, tirxy_pos, tirxy_last_rows, tirxy_frame_counter
    tirxy_frame_counter += 1

    next_pos = [tirxy_pos[0], tirxy_pos[1] + 1]
    if can_place(tirxy_field, tirxy_shape, next_pos):
        tirxy_pos = next_pos
    else:
        place_shape(tirxy_field, tirxy_shape, tirxy_pos, STABLE)
        rows = detect_order_lines(tirxy_field)
        tirxy_last_rows = rows
        if rows:
            for row in rows:
                tirxy_field[row, :] = ORDER
        else:
            tirxy_name, tirxy_shape = random_shape()
            max_x = TIRXY_W - int(tirxy_shape[:, 0].max()) - 1
            tirxy_pos = [int(np.random.randint(0, max(1, max_x))), 0]

    if tirxy_last_rows and tirxy_frame_counter % 10 == 0:
        tirxy_field = collapse_order(tirxy_field, tirxy_last_rows)
        tirxy_last_rows = []
        tirxy_name, tirxy_shape = random_shape()
        max_x = TIRXY_W - int(tirxy_shape[:, 0].max()) - 1
        tirxy_pos = [int(np.random.randint(0, max(1, max_x))), 0]

    if not can_place(tirxy_field, tirxy_shape, tirxy_pos):
        tirxy_field[:] = 0
        tirxy_name, tirxy_shape = random_shape()
        tirxy_pos = [TIRXY_W // 2 - 2, 0]

    view = tirxy_field.copy()
    place_shape(view, tirxy_shape, tirxy_pos, ACTIVE)
    view = mark_tension_and_defects(view)

    score = emergence_score(view)
    tirxy_score_history.append(score)
    if len(tirxy_score_history) > 80:
        tirxy_score_history.pop(0)

    avg_score = float(np.mean(tirxy_score_history)) if tirxy_score_history else 0.0
    normalized = max(0.0, min(1.0, score / TIRXY_SCORE_NORM))
    return score, avg_score, normalized, tirxy_name

# ----------------------------
# Kern-Gitter-Vorberechnung
# ----------------------------

_CX = WIDTH // 2
_CY = HEIGHT // 2

_DX, _DY = np.meshgrid(
    np.arange(-1, WIDTH + 1) - _CX,
    np.arange(-1, HEIGHT + 1) - _CY,
)
_R = np.sqrt(_DX * _DX + _DY * _DY)
_R_SAFE = np.where(_R == 0, 1.0, _R)

_D_NORM = normalize(D_VECTOR)
_DIRECTION_BIAS = np.where(
    _R == 0,
    0.0,
    np.abs((_DX / _R_SAFE) * _D_NORM[0] + (_DY / _R_SAFE) * _D_NORM[1]),
)

_CORE_MASK = _R <= CORE_RADIUS
_INNER_MASK = (_R > CORE_RADIUS) & (_R <= INNER_RING)
_BETWEEN_MASK = (_R > INNER_RING) & (_R <= BETWEEN_RING)
_SHELL_MASK = (_R > BETWEEN_RING) & (_R <= OUTER_SHELL)
_WORLD_MASK = _R > OUTER_SHELL

_BRIDGE_MASK = (_R > INNER_RING) & (_R < BETWEEN_RING)
_SHELL_BAND_MASK = (_R > OUTER_SHELL - 0.7) & (_R < OUTER_SHELL + 0.7)

_HIDDEN_RING = rbf_kernel(_R, H_RADIUS, GAMMA)
_HIDDEN_CORE = rbf_kernel(_R, 0.0, 0.045)
_BETWEEN_BRIDGE = rbf_kernel(_R, BETWEEN_RING, 0.22)
_SHELL_SKIN = rbf_kernel(_R, OUTER_SHELL, 0.16)
_WAVE_FOLD = 0.5 + 0.5 * np.sin(_R * 1.7)

_HIDDEN_BASE = (
    _HIDDEN_RING * 0.58 + _HIDDEN_CORE * 0.18
    + _BETWEEN_BRIDGE * 0.16 + _SHELL_SKIN * 0.08
) * _WAVE_FOLD * H_LIFT

_ZONE_MASKS_INNER = {
    "CORE": _CORE_MASK[1:-1, 1:-1],
    "INNER": _INNER_MASK[1:-1, 1:-1],
    "BETWEEN": _BETWEEN_MASK[1:-1, 1:-1],
    "SHELL": _SHELL_MASK[1:-1, 1:-1],
    "WORLD": _WORLD_MASK[1:-1, 1:-1],
}

_NOT_CENTER = np.ones((HEIGHT, WIDTH), dtype=bool)
_NOT_CENTER[_CY, _CX] = False

# ----------------------------
# Struktur / Worldtour
# ----------------------------

def poetic_structure_metric(avg_core, avg_between, avg_shell, sync_r, tirxy_norm):
    balance = 1.0 - min(1.0, abs(avg_core - avg_shell))
    bridge = avg_between
    sync_bonus = sync_r * 0.18
    tirxy_bonus = tirxy_norm * 0.14
    value = 0.42 * bridge + 0.36 * balance + sync_bonus + tirxy_bonus
    return max(0.0, min(1.0, value))

def worldtour_unlock(avg_between, avg_shell, structure, sync_r, tirxy_norm):
    if structure > 0.82 and sync_r > 0.55:
        return "Worldtour: Synchron-Schale stabil - Team-Werkbank/Station friedlich freigeschaltet."
    if structure > 0.74 and avg_shell > 0.30:
        return "Worldtour: Engineering-Modul freigeschaltet durch Verstehen + Reparatur."
    if tirxy_norm > 0.46:
        return "Worldtour: Tirxy-Ordnung erkannt - Bauplan aus Luecken und Formen gelernt."
    if avg_between > 0.36:
        return "Worldtour: Zwischenraum stabil - neue Interaktion mit Werkbank/Station moeglich."
    if avg_shell > 0.28:
        return "Worldtour: Aussenraum antwortet - Sammeln, Messen, Craften verbessert."
    return "Worldtour: Grundweg aktiv - alles bleibt erspielbar, nichts wird erzwungen."

# ----------------------------
# Vektorisierte Feldberechnung
# ----------------------------

def compute_field(t, pulse, coupling, echo, resonance, sync_r, tirxy_norm):
    p = abs(pulse)

    # Kuramoto koppelt nicht als "Macht", sondern als Ordnung/Timing.
    sync_resonance = resonance * (0.82 + 0.18 * sync_r)

    wave = np.sin(_R * 0.9 - t * 0.35 + sync_r * 0.8)
    visible = p * coupling * sync_resonance
    visible = visible * (0.55 + 0.45 * wave) * (0.45 + 0.55 * _DIRECTION_BIAS)

    h = _HIDDEN_BASE * p * coupling * sync_resonance

    shaped = np.zeros_like(_R)
    shaped[_CORE_MASK] = 0.26 + p * 0.34 + echo * 0.18
    shaped[_INNER_MASK] = 0.14 + p * 0.18
    shaped[_BETWEEN_MASK] = 0.22 + sync_resonance * 0.18 + echo * 0.12 + tirxy_norm * 0.08
    shaped[_SHELL_MASK] = 0.12 + sync_r * 0.10 + tirxy_norm * 0.05
    shaped[_WORLD_MASK] = 0.05 + echo * 0.05

    if p > 0.22:
        visible = visible + np.where(_BRIDGE_MASK, 0.16 + sync_r * 0.05, 0.0)
        h = h + np.where(_BRIDGE_MASK, 0.20 + tirxy_norm * 0.05, 0.0)

    if echo > 0.18:
        visible = visible + np.where(_SHELL_BAND_MASK, 0.10 + sync_r * 0.04, 0.0)
        h = h + np.where(_SHELL_BAND_MASK, 0.08, 0.0)

    energy = visible + h * H_GAIN + echo * 0.35 + shaped
    energy = np.clip(energy, 0.0, 1.0)
    h = np.clip(h, 0.0, 1.0)

    e0 = energy[1:-1, 1:-1]
    e_px = energy[1:-1, 2:]
    e_mx = energy[1:-1, :-2]
    e_py = energy[2:, 1:-1]
    e_my = energy[:-2, 1:-1]

    d_dx = (e_px - e_mx) / 2.0
    d_dy = (e_py - e_my) / 2.0
    grad = np.sqrt(d_dx * d_dx + d_dy * d_dy)
    lap = e_px + e_mx + e_py + e_my - 4.0 * e0

    return e0, h[1:-1, 1:-1], visible[1:-1, 1:-1], grad, lap

def symbol_grid(energy, h, lap_abs, sync_r, tirxy_norm):
    default = np.full(energy.shape, " ", dtype="<U1")
    default[_ZONE_MASKS_INNER["CORE"]] = "o"
    default[_ZONE_MASKS_INNER["BETWEEN"]] = "~"
    default[_ZONE_MASKS_INNER["SHELL"]] = "="
    default[_ZONE_MASKS_INNER["WORLD"]] = "'"

    # Bei sehr guter Synchronisation darf die Schale weich "atmen".
    if sync_r > 0.55:
        default[_ZONE_MASKS_INNER["SHELL"]] = "s"

    # Bei Tirxy-Ordnung werden Zwischenraum-Zellen als Bauplan markiert.
    if tirxy_norm > 0.45:
        default[_ZONE_MASKS_INNER["BETWEEN"]] = "t"

    return np.select(
        [
            lap_abs > 0.35,
            (h > 0.70) & (energy > 0.55),
            energy > 0.90,
            energy > 0.70,
            energy > 0.50,
            energy > 0.34,
            energy > 0.18,
        ],
        ["C", "H", "@", "#", "*", "+", "."],
        default=default,
    )

def build_field(t, pulse, coupling, echo, resonance, sync_r, tirxy_norm):
    energy, h, visible, grad, lap = compute_field(t, pulse, coupling, echo, resonance, sync_r, tirxy_norm)
    lap_abs = np.abs(lap)

    drift = np.random.uniform(-DRIFT, DRIFT, size=energy.shape)
    energy_drift = np.clip(energy + drift, 0.0, 1.0)

    symbols = symbol_grid(energy_drift, h, lap_abs, sync_r, tirxy_norm)
    symbols[_CY, _CX] = "◆"
    lines = ["".join(row) for row in symbols]

    samples = int(_NOT_CENTER.sum())
    avg_visible = float(visible[_NOT_CENTER].sum() / samples)
    avg_hidden = float(h[_NOT_CENTER].sum() / samples)
    avg_gradient = float(grad[_NOT_CENTER].sum() / samples)
    avg_curvature = float(lap_abs[_NOT_CENTER].sum() / samples)
    zwischenraum = abs(avg_hidden - avg_visible)

    zone_avg = {}
    for key, mask in _ZONE_MASKS_INNER.items():
        m = mask & _NOT_CENTER
        count = int(m.sum())
        zone_avg[key] = float(energy_drift[m].sum() / max(1, count))

    structure = poetic_structure_metric(
        zone_avg["CORE"], zone_avg["BETWEEN"], zone_avg["SHELL"], sync_r, tirxy_norm
    )

    return (
        lines, avg_visible, avg_hidden, zwischenraum, avg_gradient,
        avg_curvature, zone_avg, structure
    )

def state_name(pulse, echo, hidden_level, curvature, structure, sync_r, tirxy_norm):
    if structure > 0.82 and sync_r > 0.50:
        return "W*  Worldtour-Synchronbruecke aktiv"
    if tirxy_norm > 0.50:
        return "T*  Tirxy-Ordnung / Luecken werden Bauplan"
    if structure > 0.78:
        return "O*  Objekt-Seele / Worldtour-Bruecke aktiv"
    if hidden_level > 0.55 and echo > 0.45:
        return "H*  Hidden Geometry aktiv"
    if curvature > 0.22:
        return "C*  Feldkruemmung / Laplace-Zone"
    if pulse > 0.65:
        return "S*  angeregter Zustand"
    if pulse > 0.15:
        return "S+  posdir / Aufbau"
    if pulse < -0.65:
        return "S-  negdir / Ausgleich"
    if pulse < -0.15:
        return "S~  Rueckphase / Entladung"
    return "S0  Grundzustand"

def energy_values(pulse, coupling, echo, hidden_avg, resonance, curvature, structure, sync_r, tirxy_norm):
    e_in = abs(pulse) * 100.0

    storage_factor = 0.54
    storage_factor += hidden_avg * 0.18
    storage_factor += echo * 0.08
    storage_factor += resonance * 0.12
    storage_factor += structure * 0.05
    storage_factor += sync_r * 0.03
    storage_factor += tirxy_norm * 0.02
    storage_factor -= curvature * 0.10
    storage_factor = max(0.0, min(0.95, storage_factor))

    e_stored = e_in * coupling * storage_factor

    out_factor = 0.68 + echo * 0.06 + resonance * 0.08 + structure * 0.03
    out_factor = max(0.0, min(0.95, out_factor))
    e_out = e_stored * out_factor

    if e_out > e_in * ETA_MAX:
        e_out = e_in * ETA_MAX

    loss = e_in - e_out
    return e_in, e_stored, e_out, loss, storage_factor, out_factor

def lyrik_line(pulse, echo, zwischenraum, grad, curvature, structure, sync_r, tirxy_norm):
    if sync_r > 0.62 and structure > 0.78:
        return "Viele Phasen finden einen Takt; die Schale wird zur stillen Werkbank."
    if tirxy_norm > 0.50:
        return "Die Luecke ist kein Fehler mehr: sie wird zur Form, die morgen tragen kann."
    if structure > 0.76:
        return "Der Kern hat eine Schale gefunden; zwischen ihnen beginnt die Welt zu antworten."
    if curvature > 0.18:
        return "Die Flaeche kruemmt sich: nicht wild, sondern nach Zahl und Richtung."
    if grad > 0.20:
        return "Das Feld hat Kanten bekommen; der Gradient zeigt, wo der Zustand kippt."
    if zwischenraum > 0.35 and echo > 0.45:
        return "Der sichtbare Raum schweigt, doch H faltet leise sein Licht."
    if echo > 0.60:
        return "Was einmal stark koppelte, klingt noch im Feld nach."
    if pulse > 0.65:
        return "Das Phasenherz hebt den Zustand wie eine Sonne im Kern."
    if pulse < -0.65:
        return "Die Gegenphase atmet aus und glaettet den alten Impuls."
    if zwischenraum > 0.22:
        return "Zwischen X und H liegt ein Raum, den nur Resonanz betritt."
    return "Der Kern ruht, doch unter der Flaeche wartet der naechste Takt."


# ----------------------------
# Karin APK Bridge / Datei-Info
# ----------------------------

_apk_info_cache = None

def karin_apk_info(path=KARIN_APK_PATH):
    """Liest lokale Dateidaten der Karin.apk. Fuehrt die APK nicht aus.

    Das Ergebnis wird gecached: SHA256 ueber eine ganze APK ist potenziell
    teuer und muss nicht bei jedem Simulationsframe neu berechnet werden.
    """
    global _apk_info_cache
    if _apk_info_cache is not None:
        return _apk_info_cache

    info = {
        "path": path,
        "present": False,
        "size_bytes": 0,
        "sha256": "",
        "note": "APK wird nicht in Python ausgefuehrt; nur als externe Android-Bruecke vermerkt."
    }
    try:
        if os.path.exists(path):
            info["present"] = True
            info["size_bytes"] = os.path.getsize(path)
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            info["sha256"] = h.hexdigest()
    except Exception as e:
        info["note"] = "APK-Info konnte nicht vollstaendig gelesen werden: " + str(e)

    _apk_info_cache = info
    return info

# ----------------------------
# Optional: Modul-Uebersicht speichern
# ----------------------------

def save_module_manifest(path=None):
    if path is None:
        path = os.path.join(SCRIPT_DIR, "kern_module_manifest.json")
    data = {
        "version": "v0.9 Karin ueberarbeitet",
        "karin_enabled": KARIN_ENABLED,
        "karin_interactive": KARIN_INTERACTIVE,
        "karin_apk": karin_apk_info(),
        "world_rule": WORLD_RULE,
        "utility_object": UTILITY_OBJECT,
        "module_ring": MODULE_RING,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

# Karin-Instanz
karin = KarinCore()

# ----------------------------
# Hauptprogramm
# ----------------------------

def main():
    enable_ansi_on_windows()

    print(color("PHASENHERZ-KERN v0.9 KARIN INTERAKTIV startet...", GREEN))
    print("ZERO ARC-1 / v0.5 Kern + Kuramoto + Tirxy / Karin ist jetzt aktiv")
    time.sleep(1.5)

    coupling = coupling_strength(D_VECTOR, A_VECTOR)
    theta_angle = angle_between(D_VECTOR, A_VECTOR)
    base_resonance = resonance_factor(OMEGA, OMEGA_0, SIGMA)
    zustands_echo = 0.0

    # APK-Info (inkl. SHA256) nur einmal lesen - aendert sich waehrend des
    # Laufs nicht und muss daher nicht pro Frame neu berechnet werden.
    apk_info = karin_apk_info()
    apk_status = "gefunden" if apk_info.get("present") else "nicht gefunden"
    apk_size_mb = round(apk_info.get("size_bytes", 0) / 1024 / 1024, 2)
    apk_hash = apk_info.get("sha256", "")
    apk_hash_short = (apk_hash[:12] + "...") if apk_hash else "-"

    for t in range(STEPS):
        pulse = phase_heart_pulse(t)

        sync_r, sync_psi = update_kuramoto()
        tirxy_score, tirxy_avg_score, tirxy_norm, tirxy_piece = update_tirxy()

        # Resonanz bleibt im Kern sauber, Kuramoto wirkt als Ordnungsschicht.
        resonance = base_resonance

        new_resonance = coupling * abs(pulse) * resonance * (0.85 + 0.15 * sync_r)
        zustands_echo = zustands_echo * ECHO_DECAY + new_resonance * ECHO_GAIN
        zustands_echo = max(0.0, min(1.0, zustands_echo))

        (
            field,
            avg_x,
            avg_h,
            zwischenraum,
            avg_grad,
            avg_curv,
            zone_avg,
            structure,
        ) = build_field(t, pulse, coupling, zustands_echo, resonance, sync_r, tirxy_norm)

        state = state_name(
            pulse, zustands_echo, avg_h, avg_curv, structure, sync_r, tirxy_norm
        )

        e_in, e_stored, e_out, loss, storage_factor, out_factor = energy_values(
            pulse, coupling, zustands_echo, avg_h, resonance,
            avg_curv, structure, sync_r, tirxy_norm
        )

        unlock_text = worldtour_unlock(
            zone_avg["BETWEEN"], zone_avg["SHELL"], structure, sync_r, tirxy_norm
        )

        metrics = {
            "t": t,
            "state": state,
            "pulse": pulse,
            "echo": zustands_echo,
            "avg_h": avg_h,
            "zwischenraum": zwischenraum,
            "avg_grad": avg_grad,
            "avg_curv": avg_curv,
            "structure": structure,
            "sync_r": sync_r,
            "tirxy_norm": tirxy_norm,
            "unlock_text": unlock_text,
        }
        karin.observe(metrics)

        # Ein Frame wird als Block aufgebaut und am Ende in einem Stueck
        # ausgegeben - das ist deutlich ruhiger/schneller als ~100
        # Einzel-Prints pro Frame (v.a. auf langsameren Terminals).
        out = []
        out.append("============================================================")
        out.append(color("        PHASENHERZ-KERN v0.9 KARIN INTERAKTIV / ZERO ARC-1", GREEN))
        out.append("============================================================")
        out.append("")
        out.append("Raumaufbau:")
        out.append("Innenraum     = Core / Phasenherz")
        out.append("Zwischenraum  = X <-> H / Resonanzbruecke")
        out.append("Aussenraum    = Schale / Worldtour-Kontakt")
        out.append("Karin:        aktiv / beobachtet + interagiert lokal")
        out.append(f"Karin APK:     {apk_status} / {apk_size_mb} MB / sha256 {apk_hash_short}")
        out.append("")
        out.append("Zustandsraum:")
        out.append("Z = (x, y, z, w, t, D^→)")
        out.append("")
        out.append("Mathe-Kern:")
        out.append("K       = K0 * |D^→ · A^→|")
        out.append("theta   = arccos((D^→·A^→)/(|D^→||A^→|))")
        out.append("H(r)    = exp(-gamma * (r-r0)^2) * H_LIFT")
        out.append("R       = 1 / (1 + ((omega-omega0)/sigma)^2)")
        out.append("Kuramoto: dθ_i/dt = ω_i + (K/N) * Σ sin(θ_j - θ_i)")
        out.append("Tirxy:    Form + Zustand + Luecke + Bewegung -> Ordnung")
        out.append("")
        out.append(f"Aktueller Zustand: {color(state, CYAN)}")
        out.append(f"Phasenpuls P(t):    {round(pulse, 3)} {bar(abs(pulse))}")
        out.append(f"Kopplung K:         {round(coupling, 3)} {bar(coupling)}")
        out.append(f"Theta Winkel:       {round(theta_angle, 2)} Grad")
        out.append(f"Resonanz R:         {round(resonance, 3)} {bar(resonance)}")
        out.append(f"D^→ Richtung:       {D_VECTOR}")
        out.append(f"A^→ Achse:          {A_VECTOR}")
        out.append("")
        out.append(color("Neue Module:", YELLOW))
        out.append(f"Kuramoto sync r:    {round(sync_r, 3)} {bar(sync_r)}")
        out.append(f"Kuramoto psi:       {round(sync_psi, 3)}")
        out.append(f"Tirxy Score:        {round(tirxy_score, 1)} avg {round(tirxy_avg_score, 1)}")
        out.append(f"Tirxy Ordnung:      {round(tirxy_norm, 3)} {bar(tirxy_norm)}")
        out.append(f"Tirxy Stein:        {tirxy_piece}")
        out.append("")
        out.append("Zonen:")
        out.append(f"Core avg:           {round(zone_avg['CORE'], 3)} {bar(zone_avg['CORE'])}")
        out.append(f"Inner avg:          {round(zone_avg['INNER'], 3)} {bar(zone_avg['INNER'])}")
        out.append(f"Zwischen avg:       {round(zone_avg['BETWEEN'], 3)} {bar(zone_avg['BETWEEN'])}")
        out.append(f"Schale avg:         {round(zone_avg['SHELL'], 3)} {bar(zone_avg['SHELL'])}")
        out.append(f"World avg:          {round(zone_avg['WORLD'], 3)} {bar(zone_avg['WORLD'])}")
        out.append(f"Strukturordnung:    {round(structure, 3)} {bar(structure)}")
        out.append("")
        out.append(f"H_LIFT:             {H_LIFT}")
        out.append(f"GAMMA Kernel:       {GAMMA}")
        out.append(f"Zustands-Echo:      {round(zustands_echo, 3)} {bar(zustands_echo)}")
        out.append(f"X sichtbar avg:     {round(avg_x, 3)} {bar(avg_x)}")
        out.append(f"H hidden avg:       {round(avg_h, 3)} {bar(avg_h)}")
        out.append(f"Zwischenraum ΔXH:   {round(zwischenraum, 3)} {bar(zwischenraum)}")
        out.append(f"Gradient |∇E| avg:  {round(avg_grad, 3)} {bar(avg_grad)}")
        out.append(f"Laplace |∇²E| avg:  {round(avg_curv, 3)} {bar(avg_curv)}")
        out.append("")
        out.append(f"E_in:               {round(e_in, 2)}")
        out.append(f"E_stored:           {round(e_stored, 2)}")
        out.append(f"E_out:              {round(e_out, 2)}")
        out.append(f"Verlust:            {round(loss, 2)}")
        out.append(f"Speicherfaktor:     {round(storage_factor, 3)}")
        out.append(f"Outputfaktor:       {round(out_factor, 3)}")
        out.append(f"Eta-Max Deckel:     {ETA_MAX}")
        out.append("")
        out.append(color("Worldtour-Regel:", GREEN))
        out.append(WORLD_RULE)
        out.append(unlock_text)
        out.append(f"Utility-Objekt:     {UTILITY_OBJECT['item']} / {UTILITY_OBJECT['type']}")
        out.append(f"Non-Combat:         {UTILITY_OBJECT['non_combat']}")
        out.append("")
        out.append(color("Karin-Modul:", CYAN))
        out.append(karin.last_reply)
        out.append(f"Letzte Eingabe:     {karin.last_note}")
        out.append(f"Memory:             {karin.memory_summary()}")
        out.append(f"Dialog-Resonanz:    {round(karin.influence, 3)} {bar(karin.influence)}")
        out.append("")
        out.append("Lyrik:")
        out.append(lyrik_line(
            pulse, zustands_echo, zwischenraum, avg_grad,
            avg_curv, structure, sync_r, tirxy_norm
        ))
        out.append("")
        out.append("Legende:")
        out.append("◆ = Phasenherz-Kern")
        out.append("o = Innenraum/Core, ~ = Zwischenraum, = = Schale, ' = Welt")
        out.append("s = synchronisierte Schale, t = Tirxy-Bauplan-Zwischenraum")
        out.append("H = Hidden Geometry / Kernel-Raum")
        out.append("C = Feldkruemmung / Laplace-Zone")
        out.append("@ # * + . = Feldstaerke / Resonanz")
        out.append("")
        out.append("Gestaltetes SpinFoam-Feld:")
        out.append("")
        out.extend(field)
        out.append("")
        out.append("Hinweis:")
        out.append("Mathematische Modell-Simulation, keine reale Energieerzeugung.")
        out.append("Abbruch mit STRG+C")
        out.append("============================================================")

        clear()
        sys.stdout.write("\n".join(out) + "\n")
        sys.stdout.flush()

        if KARIN_ENABLED and KARIN_INTERACTIVE and t > 0 and t % KARIN_ASK_EVERY == 0:
            try:
                user_msg = input(color("Karin-Eingabe (Enter = weiter): ", YELLOW)).strip()
                if user_msg:
                    print(karin.answer(user_msg, metrics))
                    input(color("Enter druecken zum Weiterlaufen...", DIM))
            except (EOFError, KeyboardInterrupt):
                pass

        time.sleep(DELAY)

if __name__ == "__main__":
    try:
        # Manifest wird im Skriptordner gespeichert, falls erlaubt.
        try:
            save_module_manifest()
        except Exception:
            pass
        main()
    except KeyboardInterrupt:
        clear()
        sys.stdout.flush()
        print(color("Simulation beendet.", GREEN))
        print("Phasenherz-Kern v0.9 KARIN INTERAKTIV wurde sauber heruntergefahren. 💚")
