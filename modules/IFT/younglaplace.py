from concurrent.futures import ProcessPoolExecutor
from typing import Tuple

import numpy as np

from .fit import YoungLaplaceFitResult, young_laplace_fit


__all__ = ('YoungLaplaceFitResult', 'YoungLaplaceFitService')


class YoungLaplaceFitService:
    def __init__(self) -> None:
        self._executor = ProcessPoolExecutor(max_workers=1)

    def fit(self, data: Tuple[np.ndarray, np.ndarray]) -> YoungLaplaceFitResult:
        # Directly call `young_laplace_fit` and return the result
        return young_laplace_fit(data)

    def destroy(self) -> None:
        self._executor.shutdown()
