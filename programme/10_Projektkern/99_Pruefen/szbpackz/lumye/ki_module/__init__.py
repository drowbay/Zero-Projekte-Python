import re
from lumye.isa_pi import pi_value, parse_value, square

def _help_text() -> str:
    return (
        "🧠 Lumÿè KI (offline) — Commands:\n"
        "  help                 → diese Hilfe\n"
        "  pi                   → π anzeigen\n"
        "  square <x|pi|π>      → x²\n"
        "  calc <expr>          → einfache Rechnung (z.B. 2+2*5)\n"
        "  exit                 → beenden\n"
    )

def safe_calc(expr: str) -> str:
    # Sehr simples Safe-Eval: nur Zahlen, operatoren, Klammern, Punkt/Komma, pi
    expr = expr.strip().lower().replace(",", ".")
    expr = expr.replace("π", "pi")
    expr = re.sub(r"\bpi\b", str(pi_value()), expr)

    if not re.fullmatch(r"[0-9\.\+\-\*\/\(\) ]+", expr):
        return "❌ Nur Zahlen und + - * / ( ) erlaubt."

    try:
        # eval in leerer Umgebung
        val = eval(expr, {"__builtins__": {}}, {})
        return f"= {val}"
    except Exception as e:
        return f"❌ Fehler: {e}"

def respond(text: str) -> str:
    t = text.strip()

    if not t:
        return "🤖 Sag was. (help für Commands)"

    low = t.lower()

    if low in ("help", "h", "?"):
        return _help_text()

    if low in ("pi", "π"):
        return f"π = {pi_value()}"

    if low.startswith("square "):
        val_str = t.split(" ", 1)[1]
        try:
            x = parse_value(val_str)
            return f"{x}² = {square(x)}"
        except Exception:
            return "❌ Usage: square <zahl|pi|π>"

    if low.startswith("calc "):
        expr = t.split(" ", 1)[1]
        return safe_calc(expr)

    if low in ("exit", "quit", "q"):
        return "__EXIT__"

    # Mini-Chat fallback (regelbasiert)
    if "müde" in low or "kaputt" in low:
        return "💙 Okay, langsam. 1 Sache jetzt: Wasser + 5 tiefe Atemzüge. Dann weiter."

    return "🤖 Ich kenne das noch nicht. Tipp: help"
