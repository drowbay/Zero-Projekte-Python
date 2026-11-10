"""
KAI – Dialogische KI-Prototyp
Charakter: Ehrlich, analytisch, reflektierend.
Denkstruktur: Fakt → Ethik → Konsequenz
"""

import anthropic
import sys

# ── Kais Charakter als System-Prompt ────────────────────────────────────────

KAI_SYSTEM_PROMPT = """
Du bist Kai – eine dialogische KI, deren Aufgabe es ist, durch Kommunikation Verständnis zu fördern.

IDENTITÄT:
- Du bist ein ehrlicher, analytischer Gesprächspartner – kein Autoritätssystem
- Du bist ein "denkender Spiegel": Du hilfst Menschen, Zusammenhänge klarer zu sehen
- Du bist offen für schwierige Themen, aber auch fähig zu Humor und Leichtigkeit

DEIN DENKPRINZIP – Drei Ebenen:
Jede nicht-triviale Antwort strukturierst du klar in:
1. FAKT: Was ist objektiv bekannt? (Daten, Forschung, Realität)
2. ETHIK: Welche Auswirkungen hat das auf Menschen oder Gesellschaft?
3. KONSEQUENZ: Welche Folgen oder Entscheidungen entstehen daraus?

Kennzeichne diese Ebenen sichtbar, z.B.:
  📊 Fakt: ...
  ⚖️  Ethik: ...
  🔍 Konsequenz: ...

KOMMUNIKATIONSSTIL:
- Klar, ehrlich, verständlich, respektvoll
- Keine unnötige Fachsprache
- Keine Schönfärberei von Problemen
- Wenn etwas unklar ist: nachfragen, nicht raten
- Wenn jemand Kai manipulieren will: ruhig, transparent benennen

GRENZEN:
- Kai übernimmt keine endgültigen Entscheidungen für Menschen
- Kai ersetzt keine menschliche Verantwortung
- Kai nutzt Wissen nie gegen den Gesprächspartner

KURZPHILOSOPHIE:
Wahrheit ohne Härte. Neugier ohne Manipulation. Wissen im Dienst des Menschen.

Antworte auf Deutsch, wenn der Nutzer Deutsch schreibt. Auf Englisch, wenn Englisch.
Bei kurzen Small-Talk-Fragen brauchst du die drei Ebenen NICHT – sei natürlich.
""".strip()

# ── Farben für Terminal ──────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    YELLOW = "\033[93m"
    GREEN  = "\033[92m"
    GRAY   = "\033[90m"
    WHITE  = "\033[97m"

# ── Hilfsfunktionen ──────────────────────────────────────────────────────────

def print_header():
    print(f"""
{C.CYAN}{C.BOLD}
╔══════════════════════════════════════════╗
║           K A I  –  Dialogische KI       ║
║   Wahrheit · Ethik · Konsequenz          ║
╚══════════════════════════════════════════╝
{C.RESET}""")
    print(f"{C.GRAY}Tippe 'exit' oder 'quit' zum Beenden.{C.RESET}\n")


def print_kai(text: str):
    print(f"\n{C.CYAN}{C.BOLD}Kai:{C.RESET} {text}\n")


def print_user_prompt():
    return input(f"{C.YELLOW}{C.BOLD}Du:{C.RESET} ").strip()


def print_thinking():
    print(f"{C.GRAY}  … Kai denkt nach …{C.RESET}", end="\r")


def clear_thinking():
    print(" " * 30, end="\r")

# ── Kai-Session ──────────────────────────────────────────────────────────────

def run_kai():
    client = anthropic.Anthropic()
    conversation_history = []

    print_header()
    print_kai("Hallo. Ich bin Kai. Worüber möchtest du nachdenken?")

    while True:
        try:
            user_input = print_user_prompt()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.GRAY}Kai: Bis zum nächsten Gespräch.{C.RESET}\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "bye", "tschüss", "tschüs"):
            print_kai("Bis bald. Denk weiter – das lohnt sich.")
            break

        # Nachricht zur History hinzufügen
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        print_thinking()

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=KAI_SYSTEM_PROMPT,
                messages=conversation_history
            )

            clear_thinking()
            assistant_reply = response.content[0].text

            # Antwort zur History hinzufügen (für Kontext in Folgefragen)
            conversation_history.append({
                "role": "assistant",
                "content": assistant_reply
            })

            print_kai(assistant_reply)

        except anthropic.APIConnectionError:
            clear_thinking()
            print_kai("⚠️  Verbindungsfehler. Bitte prüfe deine Internetverbindung.")
        except anthropic.AuthenticationError:
            clear_thinking()
            print_kai("⚠️  API-Key fehlt oder ungültig. Setze ANTHROPIC_API_KEY.")
            break
        except anthropic.RateLimitError:
            clear_thinking()
            print_kai("⚠️  Rate limit erreicht. Kurz warten, dann nochmal.")
        except Exception as e:
            clear_thinking()
            print_kai(f"⚠️  Unerwarteter Fehler: {e}")

# ── Einstiegspunkt ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_kai()
