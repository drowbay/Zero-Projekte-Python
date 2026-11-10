import math
import random
from dataclasses import dataclass

@dataclass
class Qubit:
    # Bloch sphere angles
    theta: float = 0.0  # 0..pi
    phi: float = 0.0    # 0..2pi

    def state_amplitudes(self):
        # |ψ> = cos(theta/2)|0> + e^{iφ} sin(theta/2)|1>
        a0 = math.cos(self.theta / 2.0)
        a1_mag = math.sin(self.theta / 2.0)
        # store phase separately (we don't need complex math for probabilities)
        return a0, a1_mag, self.phi

    def probs(self):
        a0, a1_mag, _ = self.state_amplitudes()
        p0 = a0 * a0
        p1 = a1_mag * a1_mag
        # numerical safety
        s = p0 + p1
        if s == 0:
            return 1.0, 0.0
        return p0 / s, p1 / s

    def measure(self) -> int:
        p0, p1 = self.probs()
        r = random.random()
        return 0 if r < p0 else 1

    def set_angles(self, theta: float, phi: float):
        # clamp into ranges
        self.theta = max(0.0, min(math.pi, theta))
        # normalize phi to [0, 2pi)
        two_pi = 2.0 * math.pi
        self.phi = phi % two_pi

    def summary(self) -> str:
        p0, p1 = self.probs()
        return (
            f"Qubit |ψ> (Bloch)\n"
            f"  θ = {self.theta:.6f} rad, φ = {self.phi:.6f} rad\n"
            f"  P(0) = {p0:.4f}, P(1) = {p1:.4f}"
        )

def shots(qubit: Qubit, n: int = 100) -> str:
    n = max(1, min(1_000_000, int(n)))
    c0 = 0
    for _ in range(n):
        c0 += 1 if qubit.measure() == 0 else 0
    c1 = n - c0
    return f"Shots={n} → 0:{c0} ({c0/n:.3f}) | 1:{c1} ({c1/n:.3f})"
