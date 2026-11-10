import numpy as np
import random

# =========================
# EMBEDDING
# =========================

class EmbeddingEngine:
    def __init__(self, size=64):
        self.size = size

    def encode(self, text):
        vec = np.zeros(self.size)
        for i, c in enumerate(text):
            idx = (ord(c)*(i+1)) % self.size
            vec[idx] += 1
        norm = np.linalg.norm(vec) + 1e-8
        return vec / norm


# =========================
# PNNA
# =========================

class PNNA:
    def __init__(self, size=64):
        self.weights = np.random.randn(size)

    def forward(self, emb):
        return np.tanh(np.dot(self.weights, emb))


# =========================
# MEMORY + TOPICS
# =========================

class SmartMemory:
    def __init__(self):
        self.entries = []
        self.topics = {}

    def add(self, text):
        self.entries.append(text)

        words = text.lower().split()
        for w in words:
            if len(w) > 3:
                self.topics[w] = self.topics.get(w, 0) + 1

        if len(self.entries) > 10:
            self.entries.pop(0)

    def context(self):
        return " | ".join(self.entries)

    def get_topics(self):
        return sorted(self.topics.items(), key=lambda x: x[1], reverse=True)[:3]


# =========================
# EMOTION
# =========================

def detect_emotion(text):
    text = text.lower()

    if any(w in text for w in ["stress","angst","überfordert"]):
        return "negativ"
    if any(w in text for w in ["cool","nice","gut","super"]):
        return "positiv"
    return "neutral"


# =========================
# LIGHT LLM STYLE RESPONSE
# =========================

def generate_response(user, context, emotion, topics):

    topic_text = ", ".join([t[0] for t in topics])

    responses = [
        f"Ich sehe, du denkst viel über {topic_text}. Das hat Struktur.",
        f"Dein System entwickelt sich. Kontext: {context[:40]}...",
        f"Emotion erkannt: {emotion}. Ich passe mich daran an.",
        f"Das fühlt sich nach Aufbau an. Du verbindest gerade mehrere Ebenen.",
        f"Interessant… deine Themen sind {topic_text}. Da entsteht etwas."
    ]

    return random.choice(responses)


# =========================
# MAIN LOOP
# =========================

def main():
    embedder = EmbeddingEngine()
    pnna = PNNA()
    memory = SmartMemory()

    print("🧠 Kai v9 Mobile gestartet")
    print("Tippe 'exit' zum Beenden\n")

    while True:
        user = input("Du: ")

        if user == "exit":
            break

        emb = embedder.encode(user)
        activity = pnna.forward(emb)

        emotion = detect_emotion(user)

        memory.add(user)
        context = memory.context()
        topics = memory.get_topics()

        response = generate_response(user, context, emotion, topics)

        print("Kai:", response)
        print(f"[Aktivität: {round(activity,3)} | Emotion: {emotion}]\n")


if __name__ == "__main__":
    main()