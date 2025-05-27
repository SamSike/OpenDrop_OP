from utils.geometry import Rect2

from typing import Sequence, Tuple, NamedTuple, Optional
from enum import IntEnum, auto
from scipy.ndimage import gaussian_filter
import math
import numpy as np
import scipy.signal
import scipy.optimize

try:
    from modules.ift.hough import hough
except ImportError:
    raise RuntimeError(
        "❗ Failed to load native Cython module 'hough'.\n"
        "This is likely due to a missing or incompatible build for your architecture.\n"
        "Please run: `python setup.py build_ext --inplace`\n"
        "Refer to the README section: 'Troubleshooting: Architecture Mismatch (macOS)'"
    )


__all__ = (
    "NeedleFitResult",
    "needle_fit",
)

DELTA_TOL = None
GRADIENT_TOL = 1.0e-8
OBJECTIVE_TOL = 1.0e-8

ANGLE_STEPS = 200
DIST_STEPS = 64

# def hough(data: np.ndarray, diagonal: float) -> np.ndarray:
#     votes = np.zeros((ANGLE_STEPS, DIST_STEPS + 2), dtype=np.int32)
#     thetas = np.arange(ANGLE_STEPS) / ANGLE_STEPS * np.pi
#     for i in range(data.shape[1]):
#         x = data[0, i]
#         y = data[1, i]
#         rhos = x * np.sin(thetas) - y * np.cos(thetas)
#         bins = np.round((rhos + 0.5 * diagonal) / diagonal * (DIST_STEPS - 1)).astype(int) + 1
#         for theta_i, rho_i in enumerate(bins):
#             votes[theta_i, rho_i] += 1
#     return votes


class NeedleFitResult(NamedTuple):
    rotation: float
    rho: float
    radius: float

    objective: float
    residuals: np.ndarray

    lmask: np.ndarray


def needle_fit(
    data: Tuple[np.ndarray, np.ndarray], verbose: bool = False
) -> Optional[NeedleFitResult]:
    if data.shape[1] == 0:
        return None

    model = NeedleModel(data)

    def fun(params: Sequence[float], model: NeedleModel) -> np.ndarray:
        model.set_params(params)
        residuals = model.residuals.copy()
        return residuals

    def jac(params: Sequence[float], model: NeedleModel) -> np.ndarray:
        model.set_params(params)
        jac = model.jac.copy()
        return jac

    try:
        optimize_result = scipy.optimize.least_squares(
            fun,
            needle_guess(data),
            jac,
            args=(model,),
            x_scale="jac",
            method="trf",
            loss="arctan",
            f_scale=2.0,
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

    result = NeedleFitResult(
        rotation=model.params[NeedleParam.ROTATION],
        rho=model.params[NeedleParam.RHO],
        radius=math.fabs(model.params[NeedleParam.RADIUS]),
        objective=(model.residuals**2).sum() / model.dof,
        residuals=model.residuals,
        lmask=model.lmask,
    )

    return result


def needle_guess(data: np.ndarray) -> Sequence[float]:
    params = np.empty(len(NeedleParam))
    data = data.astype(float)

    extents = Rect2(data.min(axis=1), data.max(axis=1))
    diagonal = int(math.ceil((extents.w**2 + extents.h**2) ** 0.5))
    data -= np.reshape(extents.center, (2, 1))
    votes = hough.hough(data, diagonal)

    needles = np.zeros(shape=(votes.shape[0], 3))
    for i in range(votes.shape[0]):
        peaks, props = scipy.signal.find_peaks(votes[i], prominence=0)
        if len(peaks) < 2:
            continue
        ix = np.argsort(props["prominences"])[::-1]
        peak1_i, peak2_i = peaks[ix[:2]]
        prom1, prom2 = props["prominences"][ix[:2]]
        if prom2 < prom1 / 2:
            continue

        peak1 = ((peak1_i - 1) / (len(votes[i]) - 3) - 0.5) * diagonal
        peak2 = ((peak2_i - 1) / (len(votes[i]) - 3) - 0.5) * diagonal

        needles[i][0] = (peak1 + peak2) / 2
        needles[i][1] = math.fabs(peak1 - peak2) / 2
        needles[i][2] = prom1 + prom2

    scores = gaussian_filter(needles[:, 2], sigma=10, mode="wrap")
    needle_i = scores.argmax()

    theta = -np.pi / 2 + (needle_i / len(needles)) * np.pi
    rho, radius = needles[needle_i][:2]

    rho_offset = np.cos(theta) * extents.xc + np.sin(theta) * extents.yc
    rho += rho_offset

    params[NeedleParam.ROTATION] = theta
    params[NeedleParam.RHO] = rho
    params[NeedleParam.RADIUS] = radius

    return params


class NeedleModel:
    def __init__(self, data: Tuple[np.ndarray, np.ndarray]) -> None:
        self.data = np.copy(data)
        self.data.flags.writeable = False

        self._params = np.empty(len(NeedleParam))
        self._params_set = False
        self._residuals = np.empty(shape=(self.data.shape[1],))
        self._jac = np.empty(shape=(self.data.shape[1], len(self._params)))
        self._lmask = np.empty(shape=(self.data.shape[1],), dtype=bool)

    def set_params(self, params: Sequence[float]) -> None:
        if self._params_set and (self._params == params).all():
            return

        w = params[NeedleParam.ROTATION]
        rho = params[NeedleParam.RHO]
        radius = params[NeedleParam.RADIUS]

        residuals = self._residuals
        de_dw = self._jac[:, NeedleParam.ROTATION]
        de_drho = self._jac[:, NeedleParam.RHO]
        de_dR = self._jac[:, NeedleParam.RADIUS]
        lmask = self._lmask

        Q = np.array([[np.cos(w), -np.sin(w)], [np.sin(w), np.cos(w)]])

        data_x, data_y = self.data
        data_r, data_z = Q.T @ (data_x, data_y) - [[rho], [0]]

        e = np.abs(data_r) - radius

        lmask[:] = data_r < 0
        rmask = ~lmask

        residuals[:] = e
        de_dw[rmask] = data_z[rmask]
        de_dw[lmask] = -data_z[lmask]
        de_dR[:] = -1
        de_drho[rmask] = -1
        de_drho[lmask] = 1

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

    @property
    def lmask(self) -> np.ndarray:
        lmask = self._lmask[:]
        lmask.flags.writeable = False
        return lmask


class NeedleParam(IntEnum):
    ROTATION = 0
    RHO = auto()
    RADIUS = auto()
