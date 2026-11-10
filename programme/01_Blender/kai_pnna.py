import numpy as np
import json
import os

# ---------------------------
# Einstellungen
# ---------------------------

NEURONS = 1000
MEMORY_FILE = "kai_memory.json"

# ---------------------------
# PNNA Netzwerk
# ---------------------------

class PNNA:

    def __init__(self, neurons=1000):
        self.neurons = neurons

        # Zufällige Gewichte
        self.weights = np.random.randn(neurons)

    def process(self, text):

        # Text in Zahlen umwandeln
        text_value = sum([ord(c) for c in text]) % self.neurons

        # Aktivierung berechnen
        activation = np.tanh(self.weights[text_value])

        # Aktivität normalisieren
        activity = abs(activation)

        return activity


# ---------------------------
# Gedächtnis
# ---------------------------

class Memory:

    def __init__(self):

        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f:
                self.data = json.load(f)
        else:
            self.data = []

    def add(self, text, activity):

        entry = {
            "text": text,
            "activity": float(activity)
        }

        self.data.append(entry)

        with open(MEMORY_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def stats(self):

        if len(self.data) == 0:
            return 0,0

        activities = [d["activity"] for d in self.data]

        avg = sum(activities)/len(activities)
        maxv = max(activities)

        return avg, maxv


# ---------------------------
# Agent Logik
# ---------------------------

def interpret_activity(activity):

    if activity > 0.7:
        return "Kai ist stark aktiviert und analysiert deine Frage intensiv."
    elif activity > 0.4:
        return "Kai denkt aufmerksam über deine Frage nach."
    else:
        return "Kai denkt entspannt über deine Frage nach."


# ---------------------------
# Hauptprogramm
# ---------------------------

def main():

    pnna = PNNA(NEURONS)
    memory = Memory()

    print("================================")
    print("Kai + PNNA Netzwerk gestartet")
    print("Neuronen:", NEURONS)
    print("================================")

    while True:

        user_input = input("\nDu: ")

        if user_input.lower() in ["exit","quit"]:
            print("Kai: Gespräch beendet.")
            break

        activity = pnna.process(user_input)

        response = interpret_activity(activity)

        memory.add(user_input, activity)

        avg,maxv = memory.stats()

        print("\n🧠 PNNA Aktivität:", round(activity,3))
        print("Kai:", response)

        print("\n📊 Statistik")
        print("Gespräche:", len(memory.data))
        print("Durchschnitt Aktivität:", round(avg,3))
        print("Max Aktivität:", round(maxv,3))


# ---------------------------

if __name__ == "__main__":
    main()