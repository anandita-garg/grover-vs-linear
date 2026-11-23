"""Grover's search in Qiskit, compared with classical linear search.

Run:  python grover.py            (simulator)
      python grover.py --hardware (real IBM device, needs an IBM Quantum account)
"""
import math
import sys

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def oracle(qc, target):
    """Flip the phase of |target>  (|target> -> -|target>)."""
    n = len(target)
    zeros = [i for i, bit in enumerate(reversed(target)) if bit == "0"]
    qc.x(zeros)                       # map |target> to |11...1>
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)  # multi-controlled Z (via H-X-H)
    qc.h(n - 1)
    qc.x(zeros)


def diffuser(qc, n):
    """Reflect all amplitudes about their mean -> target amplitude grows."""
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))


def optimal_iterations(n_qubits):
    return max(1, math.floor(math.pi / 4 * math.sqrt(2 ** n_qubits)))


def grover_circuit(target, iterations=None):
    n = len(target)
    iterations = iterations or optimal_iterations(n)
    qc = QuantumCircuit(n, n)
    qc.h(range(n))                    # equal superposition over all 2^n items
    for _ in range(iterations):
        oracle(qc, target)
        diffuser(qc, n)
    qc.measure(range(n), range(n))
    return qc


def linear_search(items, target):
    """Classical baseline: check items one by one. Returns number of queries."""
    for queries, item in enumerate(items, start=1):
        if item == target:
            return queries
    return len(items)


def run(qc, backend=None, shots=2048):
    backend = backend or AerSimulator()
    result = backend.run(transpile(qc, backend), shots=shots).result()
    return result.get_counts()


def run_on_hardware(qc, shots=2048):
    # One-time setup:  QiskitRuntimeService.save_account(channel="ibm_quantum_platform", token="...")
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False)
    print("Running on", backend.name)
    job = SamplerV2(backend).run([transpile(qc, backend)], shots=shots)
    return job.result()[0].data.c.get_counts()


if __name__ == "__main__":
    target = "101"                    # 3 qubits -> 8 items
    qc = grover_circuit(target)
    print(qc.draw())

    counts = run_on_hardware(qc) if "--hardware" in sys.argv else run(qc)
    shots = sum(counts.values())
    print("Counts:", dict(sorted(counts.items())))
    print(f"P(target={target}) = {counts.get(target, 0) / shots:.1%}")

    items = [format(i, "03b") for i in range(8)]
    print(f"Linear search queries: {linear_search(items, target)} (avg N/2 = 4)")
    print(f"Grover oracle queries: {optimal_iterations(3)}")
