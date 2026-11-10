import math

def pi_value():
    return math.pi

def parse_value(s: str) -> float:
    s = s.strip().lower()
    if s in ("pi", "π"):
        return math.pi
    return float(s)

def square(x: float) -> float:
    return x * x

def info() -> str:
    return "isa_pi ✅ (π tools: pi_value, parse_value, square)"
