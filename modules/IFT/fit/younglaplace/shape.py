import numpy as np
from typing import Sequence

class YoungLaplaceShape:
    def __init__(self, bond: float) -> None:
        # Initialize the shape with the given bond
        self.bond = bond

    def __call__(self, s: float) -> np.ndarray:
        return self.call(s)

    def call(self, s: float) -> np.ndarray:
        if isinstance(s, (float, int)):  # Single value
            return self.call_single(s)
        elif isinstance(s, np.ndarray):  # Array of values
            return self.call_array(s)

    def call_single(self, s: float) -> np.ndarray:
        # Example function for the single value. Replace with your actual computation.
        return np.array([self.bond * s, self.bond * s])

    def call_array(self, s: np.ndarray) -> np.ndarray:
        # Example for array input. Replace with your actual computation.
        out = np.empty((2, s.shape[0]))
        for i in range(s.shape[0]):
            out[0, i], out[1, i] = self.call_single(s[i])
        return out

    def DBo(self, s: float) -> np.ndarray:
        return self.DBo_single(s)

    def DBo_single(self, s: float) -> np.ndarray:
        # Example function for the DBo computation. Replace with actual computation.
        return np.array([self.bond * s, self.bond * s])

    def DBo_array(self, s: np.ndarray) -> np.ndarray:
        out = np.empty((2, s.shape[0]))
        for i in range(s.shape[0]):
            out[:, i] = self.DBo_single(s[i])
        return out

    def z_inv(self, z: float) -> float:
        # Example function for z_inv computation. Replace with actual computation.
        return 1 / z

    def closest(self, r: np.ndarray, z: np.ndarray) -> np.ndarray:
        if r.shape[0] != z.shape[0]:
            raise ValueError("r and z must have equal lengths")

        out = np.empty(r.shape[0])
        for i in range(r.shape[0]):
            out[i] = self.closest_single(r[i], z[i])
        return out

    def closest_single(self, r: float, z: float) -> float:
        # Example closest computation. Replace with your actual logic.
        return r - z

    def volume(self, s: float) -> float:
        # Example volume computation. Replace with actual logic.
        return self.bond * s * s * s

    def surface_area(self, s: float) -> float:
        # Example surface area computation. Replace with actual logic.
        return self.bond * s * s

    @property
    def bond(self) -> float:
        return self._bond

    @bond.setter
    def bond(self, value: float) -> None:
        self._bond = value
