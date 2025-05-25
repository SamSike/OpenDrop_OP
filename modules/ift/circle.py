from utils.geometry import Vector2

from typing import Sequence, NamedTuple, Optional
from enum import IntEnum, auto
import numpy as np
import scipy.optimize

__all__ = (
    "CircleFitResult",
    "circle_fit",
)

DELTA_TOL = 1.0e-8
GRADIENT_TOL = 1.0e-8
OBJECTIVE_TOL = 1.0e-8


class CircleFitResult(NamedTuple):
    center: Vector2[float]
    radius: float

    objective: float
    residuals: np.ndarray


def circle_fit(
    data: np.ndarray,
    *,
    loss: str = "linear",
    f_scale: float = 1.0,
    xc: Optional[float] = None,
    yc: Optional[float] = None,
    radius: Optional[float] = None,
    verbose: bool = False,
) -> Optional[CircleFitResult]:
    if data.shape[1] == 0:
        return None

    model = CircleModel(data)

    def fun(params: Sequence[float]) -> np.ndarray:
        model.set_params(params)
        residuals = model.residuals.copy()
        return residuals

    def jac(params: Sequence[float]) -> np.ndarray:
        model.set_params(params)
        jac = model.jac.copy()
        return jac

    initial_params = np.empty(len(CircleParam))

    if xc is None or yc is None:
        xc, yc = data.mean(axis=1)

    if radius is None:
        tx, ty = data[0] - xc, data[1] - yc
        radius = np.median(np.sqrt(tx**2 + ty**2))

    initial_params[CircleParam.CENTER_X] = xc
    initial_params[CircleParam.CENTER_Y] = yc
    initial_params[CircleParam.RADIUS] = radius
    model.set_params(initial_params)

    try:
        optimize_result = scipy.optimize.least_squares(
            fun,
            model.params,
            jac,
            method="lm" if loss == "linear" else "trf",
            loss=loss,
            f_scale=f_scale,
            x_scale="jac",
            ftol=OBJECTIVE_TOL,
            xtol=DELTA_TOL,
            gtol=GRADIENT_TOL,
            max_nfev=50,
            verbose=2 if verbose else 0,
        )
    except ValueError:
        return None

    # Update model parameters to final result.
    model.set_params(optimize_result.x)

    result = CircleFitResult(
        center=Vector2(
            model.params[CircleParam.CENTER_X], model.params[CircleParam.CENTER_Y]
        ),
        radius=model.params[CircleParam.RADIUS],
        objective=(model.residuals**2).sum() / model.dof,
        residuals=model.residuals,
    )

    return result


class CircleModel:
    def __init__(self, data: np.ndarray) -> None:
        if data.flags.writeable:
            data = data.copy()
            data.flags.writeable = False

        self.data = data

        self._params = np.empty(len(CircleParam))
        self._params_set = False
        self._residuals = np.empty(shape=(self.data.shape[1],))
        self._jac = np.empty(shape=(self.data.shape[1], len(self._params)))
        self._lmask = np.empty(shape=(self.data.shape[1],), dtype=bool)

    def set_params(self, params: Sequence[float]) -> None:
        if self._params_set and (self._params == params).all():
            return

        xc = params[CircleParam.CENTER_X]
        yc = params[CircleParam.CENTER_Y]
        R = params[CircleParam.RADIUS]

        e = self._residuals
        de_dxc = self._jac[:, CircleParam.CENTER_X]
        de_dyc = self._jac[:, CircleParam.CENTER_Y]
        de_dR = self._jac[:, CircleParam.RADIUS]

        x, y = self.data
        tx = x - xc
        ty = y - yc
        r = np.sqrt(tx**2 + ty**2)

        e[:] = r - R
        de_dxc[:] = -tx / r
        de_dyc[:] = -ty / r
        de_dR[:] = -1

        self._params[:] = params

    @property
    def params(self) -> Sequence[int]:
        params = self._params[:]
        params.flags.writeable = False
        return params

    @property
    def dof(self) -> int:
        return self.data.shape[1] - len(self.params) + 1

    @property
    def jac(self) -> np.ndarray:
        jac = self._jac[:]
        jac.flags.writeable = False
        return jac

    @property
    def residuals(self) -> np.ndarray:
        residuals = self._residuals[:]
        residuals.flags.writeable = False
        return residuals


class CircleParam(IntEnum):
    CENTER_X = 0
    CENTER_Y = auto()
    RADIUS = auto()
