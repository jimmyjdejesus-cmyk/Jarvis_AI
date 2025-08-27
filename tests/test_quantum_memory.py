import importlib.util
import random
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "quantum_memory",
    Path(__file__).resolve().parents[1] / "jarvis/memory/quantum_memory.py",
)
quantum_memory = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(quantum_memory)
QuantumMemory = quantum_memory.QuantumMemory


def test_measure_returns_only_experience_when_single_amplitude():
    memory = QuantumMemory()
    memory.store("only", 1 + 0j)
    random.seed(0)
    assert memory.measure() == "only"


def test_amplitude_update_hook_replaces_value():
    def replace(old: complex, new: complex) -> complex:
        return new

    memory = QuantumMemory(amplitude_update=replace)
    memory.store("exp", 1 + 0j)
    memory.store("exp", 2 + 0j)
    assert memory.amplitude_vector()["exp"] == 2 + 0j


def test_interference_hook_zeroes_amplitudes():
    def zero_out(amplitudes):
        return {k: 0j for k in amplitudes}

    memory = QuantumMemory(interference=zero_out)
    memory.store("a", 1 + 0j)
    assert memory.measure() is None
