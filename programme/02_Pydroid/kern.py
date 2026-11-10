ENERGY_MAP = {
    "1": 1,
    "0": 0,
    "-1": -1,
    "~0": 0.5
}

def combine(a, b):
    return ENERGY_MAP[a] + ENERGY_MAP[b]

def transition(a, b):
    return f"{a} -> {b}"

def evaluate(expression):
    tokens = expression.split()

    if ":" in tokens:
        i = tokens.index(":")
        result = combine(tokens[i-1], tokens[i+1])
        return f"Kombinierte Energie: {result}"

    if "=>" in tokens:
        i = tokens.index("=>")
        return transition(tokens[i-1], tokens[i+1])

    return "Unbekannter Ausdruck"


print(evaluate("1 : ~0"))
print(evaluate("1 => -1"))
