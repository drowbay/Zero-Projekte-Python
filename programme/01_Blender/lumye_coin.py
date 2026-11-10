import json
import os
from datetime import datetime

STATE_FILE = "lumye_state.json"

# Deine legendäre Mega-Zahl 😄
MEGA_NUMBER = 10000000009999999999999999999999899998999999

default_state = {
    "name": "LUMYΞ",
    "supply": MEGA_NUMBER,
    "chains": MEGA_NUMBER,
    "level": 1,
    "purity": 1.0,
    "uses": 0,
    "mood": "😊",
}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return default_state.copy()

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def refine(state):
    state["uses"] += 1

    # Stimmung abhängig von Nutzung
    if state["uses"] % 7 == 0:
        state["level"] += 1
        state["purity"] += 0.1
        state["mood"] = "🎉"
    elif state["uses"] % 3 == 0:
        state["mood"] = "😄"
    else:
        state["mood"] = "😊"

    state["last_update"] = datetime.now().isoformat()
    return state

def display(state):
    print("\n💟 TAMACOTCHI-COIN STATUS 💟")
    print("────────────────────────────")
    print(f"🪙 Name: {state['name']}")
    print(f"📈 Level: {state['level']}")
    print(f"💎 Purity: {round(state['purity'], 2)}")
    print(f"✨ Uses: {state['uses']}")
    print(f"😺 Mood: {state['mood']}")
    print(f"🌐 Chains: {state['chains']}")
    print(f"💰 Total Supply: {state['supply']}")
    print("────────────────────────────\n")

state = load_state()
state = refine(state)
save_state(state)
display(state)
