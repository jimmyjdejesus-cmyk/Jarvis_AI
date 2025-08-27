"""Quantum-inspired memory modeled with complex amplitudes.

This module provides a minimal classical simulation of a quantum memory where
experiences are represented as complex-amplitude vectors. Retrieval uses a
measurement process that selects an experience probabilistically based on the
squared magnitude of its amplitude.

The simulation assumes classical execution; it does *not* provide quantum
speedups or true superposition, but it offers a convenient abstraction for
reasoning about interference and amplitude updates. Hooks are provided for
custom amplitude-update logic and interference handling.

Example:
    >>> from jarvis.memory.quantum_memory import QuantumMemory
    >>> memory = QuantumMemory()
    >>> memory.store("greeting", 1+0j)
    >>> memory.store("parting", 0+1j)
    >>> retrieved = memory.measure()
    >>> if retrieved:
    ...     print(f"Agent recalled: {retrieved}")
    >>> # Integration with an agent's reasoning loop
    >>> for thought in agent.reason():
    ...     memory.store(thought, 1+0j)
    ...     recall = memory.measure()
    ...     agent.observe(recall)
"""

from __future__ import annotations

from typing import Callable, Dict, Optional
import random

AmplitudeUpdateFn = Callable[[complex, complex], complex]
InterferenceFn = Callable[[Dict[str, complex]], Dict[str, complex]]


class QuantumMemory:
    """A simple quantum-inspired memory buffer.

    Args:
        amplitude_update: Function controlling how existing and new amplitudes
            are combined when storing experiences. Defaults to summing the
            amplitudes.
        interference: Function applied to the amplitude vector prior to
            measurement to model interference effects. Defaults to a no-op.
    """

    def __init__(
        self,
        amplitude_update: AmplitudeUpdateFn | None = None,
        interference: InterferenceFn | None = None,
    ) -> None:
        self.amplitudes: Dict[str, complex] = {}
        self._amplitude_update = (
            amplitude_update or self.default_amplitude_update
        )
        self._interference = interference or self.default_interference

    @staticmethod
    def default_amplitude_update(old: complex, new: complex) -> complex:
        """Add the new amplitude to the existing amplitude."""

        return old + new

    @staticmethod
    def default_interference(
        amplitudes: Dict[str, complex],
    ) -> Dict[str, complex]:
        """Return the amplitudes without modification."""

        return amplitudes

    def store(self, experience: str, amplitude: complex) -> None:
        """Store an experience with a complex amplitude.

        Args:
            experience: Identifier of the experience.
            amplitude: Complex amplitude associated with the experience.
        """

        old = self.amplitudes.get(experience, 0j)
        self.amplitudes[experience] = self._amplitude_update(old, amplitude)

    def measure(self) -> Optional[str]:
        """Retrieve an experience via measurement.

        The probability of each experience being selected is proportional to
        the squared magnitude of its (potentially interfered) amplitude.

        Returns:
            The selected experience or ``None`` if the memory is empty or all
            amplitudes cancel out.
        """

        if not self.amplitudes:
            return None

        amplitudes = self._interference(self.amplitudes.copy())
        probabilities = {exp: abs(amp) ** 2 for exp, amp in amplitudes.items()}
        total = sum(probabilities.values())
        if total == 0:
            return None

        threshold = random.random() * total
        cumulative = 0.0
        for experience, prob in probabilities.items():
            cumulative += prob
            if threshold <= cumulative:
                return experience
        return None

    def amplitude_vector(self) -> Dict[str, complex]:
        """Return a copy of the current amplitude vector."""

        return self.amplitudes.copy()
