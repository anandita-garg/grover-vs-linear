"""Entanglement basics: Bell state + quantum teleportation."""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity
from qiskit_aer import AerSimulator


def bell_state():
    qc = QuantumCircuit(2, 2)
    qc.h(0)          # qubit 0 -> (|0> + |1>)/sqrt2
    qc.cx(0, 1)      # entangle: (|00> + |11>)/sqrt2
    qc.measure([0, 1], [0, 1])
    counts = AerSimulator().run(qc, shots=2048).result().get_counts()
    print("Bell state counts (only 00 and 11 appear):", counts)


def teleport(theta=1.2, phi=0.7):
    """Teleport the state cos(t/2)|0> + e^{i phi} sin(t/2)|1> from q0 to q2."""
    qc = QuantumCircuit(3)
    qc.ry(theta, 0); qc.rz(phi, 0)       # state to send, on Alice's qubit

    qc.h(1); qc.cx(1, 2)                  # shared Bell pair: q1 (Alice), q2 (Bob)
    qc.cx(0, 1); qc.h(0)                  # Alice's Bell measurement basis change
    qc.cx(1, 2); qc.cz(0, 2)              # Bob's corrections (deferred measurement)

    bob = partial_trace(Statevector.from_instruction(qc), [0, 1])
    original = QuantumCircuit(1); original.ry(theta, 0); original.rz(phi, 0)
    f = state_fidelity(bob, Statevector.from_instruction(original))
    print(f"Teleportation fidelity (1.0 = perfect): {f:.4f}")


if __name__ == "__main__":
    bell_state()
    teleport()
