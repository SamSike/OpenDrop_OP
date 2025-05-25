# Copyright © 2020, Joseph Berry, Rico Tabor (opendrop.dev@gmail.com)
# OpenDrop is released under the GNU GPL License. You are free to
# modify and distribute the code, but always under the same license
#
# If you use this software in your research, please cite the following
# journal articles:
#
# J. D. Berry, M. J. Neeson, R. R. Dagastine, D. Y. C. Chan and
# R. F. Tabor, Measurement of surface and interfacial tension using
# pendant drop tensiometry. Journal of Colloid and Interface Science 454
# (2015) 226–237. https://doi.org/10.1016/j.jcis.2015.05.012
#
# E. Huang, T. Denning, A. Skoufis, J. Qi, R. R. Dagastine, R. F. Tabor
# and J. D. Berry, OpenDrop: Open-source software for pendant drop
# tensiometry & contact angle measurements, submitted to the Journal of
# Open Source Software
#
# These citations help us not only to understand who is using and
# developing OpenDrop, and for what purpose, but also to justify
# continued development of this code and other open source resources.
#
# OpenDrop is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this software.  If not, see <https://www.gnu.org/licenses/>.

from utils.misc import rotation_mat2d
from modules.ift.younglaplace.shape import YoungLaplaceShape

from typing import Sequence, Tuple, NamedTuple, Optional
from enum import IntEnum, auto
import math
import numpy as np
import scipy.optimize


__all__ = (
    "YoungLaplaceFitResult",
    "young_laplace_fit",
)

DELTA_TOL = 1.0e-8
GRADIENT_TOL = 1.0e-8
OBJECTIVE_TOL = 1.0e-8
MAX_STEPS = 50
# Math constants.
PI = math.pi
NAN = math.nan


class YoungLaplaceFitResult(NamedTuple):
    bond: float
    radius: float
    apex_x: float
    apex_y: float
    rotation: float

    objective: float
    residuals: np.ndarray
    closest: np.ndarray
    arclengths: np.ndarray

    volume: float
    surface_area: float


def young_laplace_fit(data: Tuple[np.ndarray, np.ndarray], verbose: bool = False):
    model = YoungLaplaceModel(data)

    def fun(params: Sequence[float], model: YoungLaplaceModel) -> np.ndarray:
        model.set_params(params)
        return model.residuals

    def jac(params: Sequence[float], model: YoungLaplaceModel) -> np.ndarray:
        model.set_params(params)
        return model.jac

    initial_params = young_laplace_guess(data)
    if initial_params is None:
        raise ValueError("Parameter estimatation failed for this data set")

    model.set_params(initial_params)

    optimize_result = scipy.optimize.least_squares(
        fun,
        model.params,
        jac,
        args=(model,),
        x_scale="jac",
        method="lm",
        ftol=OBJECTIVE_TOL,
        xtol=DELTA_TOL,
        gtol=GRADIENT_TOL,
        verbose=2 if verbose else 0,
        max_nfev=MAX_STEPS,
    )

    # Update model parameters to final result.
    model.set_params(optimize_result.x)

    result = YoungLaplaceFitResult(
        bond=model.params[YoungLaplaceParam.BOND],
        radius=model.params[YoungLaplaceParam.RADIUS],
        apex_x=model.params[YoungLaplaceParam.APEX_X],
        apex_y=model.params[YoungLaplaceParam.APEX_Y],
        rotation=model.params[YoungLaplaceParam.ROTATION],
        objective=(model.residuals**2).sum() / model.dof,
        residuals=model.residuals,
        closest=model.closest,
        arclengths=model.arclengths,
        volume=model.volume,
        surface_area=model.surface_area,
    )

    return result


def young_laplace_guess(data: Tuple[np.ndarray, np.ndarray]) -> Optional[tuple]:
    from modules.ift.pendant import find_pendant_apex

    params = np.empty(len(YoungLaplaceParam))

    ans = find_pendant_apex(data)
    if ans is None:
        return None

    apex, radius, rotation = ans

    r, z = rotation_mat2d(-rotation) @ (data - np.reshape(apex, (2, 1)))
    bond = _bond_selected_plane(r, z, radius)

    params[YoungLaplaceParam.BOND] = bond
    params[YoungLaplaceParam.RADIUS] = radius
    params[YoungLaplaceParam.APEX_X] = apex.x
    params[YoungLaplaceParam.APEX_Y] = apex.y
    params[YoungLaplaceParam.ROTATION] = rotation

    return params


def _bond_selected_plane(r: np.ndarray, z: np.ndarray, radius: float) -> float:
    """Estimate Bond number by method of selected plane."""
    z_ix = np.argsort(z)
    if np.searchsorted(z, 2.0 * radius, sorter=z_ix) < len(z):
        lower, upper = np.searchsorted(z, [1.95 * radius, 2.05 * radius], sorter=z_ix)
        radii = np.abs(r[z_ix][lower : upper + 1])
        x = radii.mean() / radius
        bond = max(0.10, 0.1756 * x**2 + 0.5234 * x**3 - 0.2563 * x**4)
    else:
        bond = 0.15

    return bond


class YoungLaplaceModel:
    _shape: Optional[YoungLaplaceShape] = None

    def __init__(self, data: Tuple[np.ndarray, np.ndarray]) -> None:
        self.data = np.copy(data)
        self.data.flags.writeable = False

        self._params = np.empty(len(YoungLaplaceParam))
        self._params_set = False
        self._s = np.empty(shape=(self.data.shape[1],))
        self._residuals = np.empty(shape=(self.data.shape[1],))
        self._jac = np.empty(shape=(self.data.shape[1], len(self._params)))

    def set_params(self, params: Sequence[float]) -> None:
        if self._params_set and (self._params == params).all():
            return

        bond = params[YoungLaplaceParam.BOND]
        radius = params[YoungLaplaceParam.RADIUS]
        X0 = params[YoungLaplaceParam.APEX_X]
        Y0 = params[YoungLaplaceParam.APEX_Y]
        w = params[YoungLaplaceParam.ROTATION]

        s = self._s

        residuals = self._residuals
        de_dBo = self._jac[:, YoungLaplaceParam.BOND]
        de_dR = self._jac[:, YoungLaplaceParam.RADIUS]
        de_dX0 = self._jac[:, YoungLaplaceParam.APEX_X]
        de_dY0 = self._jac[:, YoungLaplaceParam.APEX_Y]
        de_dw = self._jac[:, YoungLaplaceParam.ROTATION]

        shape = self._get_shape(bond)
        Q = rotation_mat2d(w)

        data_x, data_y = self.data
        data_r, data_z = Q.T @ (data_x - X0, data_y - Y0)

        s[:] = shape.closest(data_r / radius, data_z / radius)
        r, z = radius * shape(s)
        dr_dBo, dz_dBo = radius * shape.DBo(s)
        e_r = data_r - r
        e_z = data_z - z
        e = np.hypot(e_r, e_z)

        # Set residues for points inside the drop as negative and outside as positive.
        e[np.signbit(e_r) != np.signbit(r)] *= -1

        residuals[:] = e
        de_dBo[:] = -(e_r * dr_dBo + e_z * dz_dBo) / e  # derivative w.r.t. Bond number
        de_dR[:] = -(e_r * r + e_z * z) / (radius * e)  # derivative w.r.t. radius
        # derivative w.r.t. apex (x, y)-coordinates
        de_dX0[:], de_dY0[:] = -Q @ (e_r, e_z) / e
        # derivative w.r.t. rotation
        de_dw[:] = (e_r * z - e_z * r) / e

        self._params[:] = params

    def _get_shape(self, bond: float) -> YoungLaplaceShape:
        if self._shape is None or self._shape.bond != bond:
            self._shape = YoungLaplaceShape(bond)

        return self._shape

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
    def closest(self) -> np.ndarray:
        xy = np.empty_like(self.data, dtype=float)

        bond = self._params[YoungLaplaceParam.BOND]
        radius = self._params[YoungLaplaceParam.RADIUS]
        X0 = self._params[YoungLaplaceParam.APEX_X]
        Y0 = self._params[YoungLaplaceParam.APEX_Y]
        w = self._params[YoungLaplaceParam.ROTATION]

        shape = self._get_shape(bond)
        Q = rotation_mat2d(w)
        s = self._s

        rz = radius * shape(s)
        xy[:] = Q @ rz + [[X0], [Y0]]

        return xy

    @property
    def arclengths(self) -> np.ndarray:
        s = self._s[:]
        s.flags.writeable = False
        return s

    @property
    def volume(self) -> float:
        bond = self._params[YoungLaplaceParam.BOND]
        radius = self._params[YoungLaplaceParam.RADIUS]

        shape = self._get_shape(bond)
        s = self._s

        return radius**3 * shape.volume(s.max())

    @property
    def surface_area(self) -> float:
        bond = self._params[YoungLaplaceParam.BOND]
        radius = self._params[YoungLaplaceParam.RADIUS]

        shape = self._get_shape(bond)
        s = self._s

        return radius**2 * shape.surface_area(s.max())


class YoungLaplaceParam(IntEnum):
    BOND = 0
    RADIUS = auto()
    APEX_X = auto()
    APEX_Y = auto()
    ROTATION = auto()
