
"""
Qubit-Mandala (NumPy-Statevector, ohne Qiskit)

Überlegungen:
- Superposition via Hadamard auf allen Qubits → alle 2^N Basiszustände sind "aktiv".
- Ring-CZ fügt zustandsabhängige Phasen hinzu → Interferenzkämme (sichtbare Muster in der Heatmap).
- Eine kleine Rz(theta) auf Qubit 0 bricht die perfekten Symmetrien → feinere Kontraste.
- 2D-Mapping: Für N gerade wird 2^N als Quadrat 2^(N/2) × 2^(N/2) visualisiert (High-Bits = Zeilen, Low-Bits = Spalten).
- Größere N, andere Kopplungstopologien, variable Phasen → andere "Mandalas".
- Dies ist idealisiert (kein Rauschen). Echte Hardware/Noise-Modelle machen das Muster weicher.

Nutzung:
    python qubit_mandala_numpy.py
"""

import numpy as np
import matplotlib.pyplot as plt

def hadamard():
    return (1/np.sqrt(2)) * np.array([[1, 1],[1, -1]], dtype=complex)

def apply_single_qubit(state, gate, qubit, num_qubits):
    tensor = state.reshape((2,) * num_qubits)
    tensor = np.moveaxis(tensor, qubit, 0)
    tensor = np.tensordot(gate, tensor, axes=([1], [0]))
    tensor = np.moveaxis(tensor, 0, qubit)
    return tensor.reshape(-1)

def apply_h_all(state, num_qubits):
    for q in range(num_qubits):
        state = apply_single_qubit(state, hadamard(), q, num_qubits)
    return state

def apply_cz_ring(state, num_qubits, pairs=None, phase=-1.0):
    if pairs is None:
        pairs = [(i, (i+1) % num_qubits) for i in range(num_qubits)]
    state = state.copy()
    for idx in range(state.size):
        for (i, j) in pairs:
            if ((idx >> i) & 1) and ((idx >> j) & 1):
                state[idx] *= phase
    return state

def rz(theta):
    return np.array([[np.exp(-1j*theta/2), 0],[0, np.exp(1j*theta/2)]], dtype=complex)

def normalize(state):
    n = np.linalg.norm(state)
    return state / n if n != 0 else state

def sample_counts_from_state(state, shots=4096):
    probs = np.abs(state)**2
    probs = probs / probs.sum()
    outcomes_idx = np.random.choice(len(probs), size=shots, p=probs)
    counts = {}
    num_qubits = int(np.log2(len(probs)))
    for idx in outcomes_idx:
        b = format(idx, f"0{num_qubits}b")
        counts[b] = counts.get(b, 0) + 1
    return counts

def counts_to_heatmap(counts, num_qubits):
    assert num_qubits % 2 == 0, "N gerade wählen (4, 6, 8, ...) für quadratische Heatmap."
    size = 2 ** (num_qubits // 2)
    heatmap = np.zeros((size, size), dtype=float)
    for bitstring, c in counts.items():
        index = int(bitstring, 2)
        x, y = divmod(index, size)
        heatmap[x, y] += c
    return heatmap

if __name__ == "__main__":
    num_qubits = 6
    shots = 4096
    theta = 0.7
    cz_phase = -1.0

    state = np.zeros(2**num_qubits, dtype=complex)
    state[0] = 1.0
    state = apply_h_all(state, num_qubits)
    state = apply_cz_ring(state, num_qubits, phase=cz_phase)
    state = apply_single_qubit(state, rz(theta), 0, num_qubits)
    state = normalize(state)

    counts = sample_counts_from_state(state, shots=shots)
    heatmap = counts_to_heatmap(counts, num_qubits)

    plt.figure(figsize=(6,6))
    plt.imshow(heatmap, interpolation="nearest")
    plt.title(f"Qubit-Mandala Heatmap (N={num_qubits}, shots={shots})")
    plt.axis("off")
    plt.colorbar(label="Counts")
    plt.tight_layout()
    plt.show()
