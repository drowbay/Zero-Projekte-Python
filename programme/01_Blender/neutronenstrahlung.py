import random
import math

class Neutron:
    def __init__(self, energy_mev):
        self.energy_mev = energy_mev
        self.alive = True

    def lose_energy(self, material):
        """Neutron verliert Energie je nach Material."""
        loss = material.slowdown_factor * random.uniform(0.5, 1.5)
        self.energy_mev = max(0, self.energy_mev - loss)

        if self.energy_mev <= 0.01:
            self.alive = False


class ShieldMaterial:
    def __init__(self, name, absorption_chance, slowdown_factor):
        self.name = name
        self.absorption_chance = absorption_chance
        self.slowdown_factor = slowdown_factor

    def interact(self, neutron):
        """Material kann Neutron abbremsen oder absorbieren."""
        if random.random() < self.absorption_chance:
            neutron.alive = False
            return "absorbiert"

        neutron.lose_energy(self)
        return "abgebremst"


def simulate_neutron_radiation(
    neutron_count=1000,
    start_energy_mev=14.0,
    shield_layers=None
):
    if shield_layers is None:
        shield_layers = [
            ShieldMaterial("Wasser", absorption_chance=0.08, slowdown_factor=2.0),
            ShieldMaterial("Polyethylen", absorption_chance=0.12, slowdown_factor=2.5),
            ShieldMaterial("Bor-Schicht", absorption_chance=0.35, slowdown_factor=1.0),
            ShieldMaterial("Regolith/Mondstaub", absorption_chance=0.10, slowdown_factor=1.5),
        ]

    absorbed = 0
    escaped = 0
    total_final_energy = 0

    for _ in range(neutron_count):
        neutron = Neutron(start_energy_mev)

        for layer in shield_layers:
            if not neutron.alive:
                break
            layer.interact(neutron)

        if neutron.alive:
            escaped += 1
            total_final_energy += neutron.energy_mev
        else:
            absorbed += 1

    avg_energy = total_final_energy / escaped if escaped > 0 else 0

    print("=== Neutronenstrahlungs-Simulation ===")
    print(f"Gestartete Neutronen: {neutron_count}")
    print(f"Startenergie pro Neutron: {start_energy_mev} MeV")
    print(f"Absorbiert: {absorbed}")
    print(f"Durchgedrungen: {escaped}")
    print(f"Durchdringungsrate: {(escaped / neutron_count) * 100:.2f}%")
    print(f"Ø Restenergie der durchgedrungenen Neutronen: {avg_energy:.2f} MeV")


if __name__ == "__main__":
    simulate_neutron_radiation()