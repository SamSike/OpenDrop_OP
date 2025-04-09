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


import asyncio
import math
import time
from asyncio import Future
from enum import Enum
from typing import Optional
import numpy as np

from .pendant import *
from .younglaplace import YoungLaplaceFitService, YoungLaplaceFitResult
from utils.bindable import AccessorBindable
from utils.geometry import Rect2, Vector2


PI = math.pi


class PendantAnalysisService:
    def analyse(self, experimental_drop, experimental_setup):
        return PendantAnalysisJob(
            experimental_drop = experimental_drop,
            experimental_setup = experimental_setup,
        )


class PendantAnalysisJob:
    class Status(Enum):
        WAITING_FOR_IMAGE = ('Waiting for image', False)
        EXTRACTING_FEATURES = ('Extracting features', False)
        FITTING = ('Fitting', False)
        FINISHED = ('Finished', True)
        CANCELLED = ('Cancelled', True)

        def __init__(self, display_name: str, is_terminal: bool) -> None:
            self.display_name = display_name
            self.is_terminal = is_terminal

        def __str__(self) -> str:
            return self.display_name

    def __init__(self, experimental_drop, experimental_setup):

        self._ylfit_service = YoungLaplaceFitService()

        self._time_start = time.time()
        self._time_end = math.nan

        self._status = self.Status.WAITING_FOR_IMAGE
        self.bn_status = AccessorBindable(
            getter=self._get_status,
            setter=self._set_status,
        )

        self._image = None  # type: Optional[np.ndarray]

        self._experimental_setup = experimental_setup
        self._experimental_drop = experimental_drop

        self.bn_is_done = AccessorBindable(getter=self._get_is_done)
        self.bn_is_cancelled = AccessorBindable(getter=self._get_is_cancelled)
        self.bn_progress = AccessorBindable(self._get_progress)
        self.bn_time_start = AccessorBindable(self._get_time_start)
        self.bn_time_est_complete = AccessorBindable(self._get_time_est_complete)

        self.bn_status.on_changed.connect(self.bn_is_done.poke)
        self.bn_status.on_changed.connect(self.bn_progress.poke)

        self._image_ready(experimental_drop.image)

        self._features = None
        self._ylfit = None

    def _image_ready(self, image) -> None:
        features = extract_pendant_features(
            image=image,
            drop_region=Rect2(*(self._experimental_setup.drop_region)),
            needle_region=self._experimental_setup.needle_region,
            thresh1=self._experimental_setup.ift_thresh1,
            thresh2=self._experimental_setup.ift_thresh2
        )
        self._features_done(features)
        self.bn_status.set(self.Status.EXTRACTING_FEATURES)


    def _features_done(self, features: PendantFeatures) -> None:
        self.bn_drop_profile_extract = features.drop_points.T
        self.bn_needle_width_px = features.needle_diameter

        self.bn_status.set(self.Status.FITTING)

        result = self._ylfit_service.fit(features.drop_points)
        self._ylfit_done(result)

    def _ylfit_done(self, result: YoungLaplaceFitResult) -> None:
        continuous_density = self._experimental_setup.continuous_density
        needle_diameter = self._experimental_setup.needle_diameter
        pixel_scale = self._experimental_setup.pixel_scale or np.nan
        gravity = self._experimental_setup.gravity

        print("setup: ", vars(self._experimental_setup))

        bond = result.bond
        apex_x = result.apex_x
        apex_y = result.apex_y
        rotation = result.rotation
        residuals = result.residuals
        closest = result.closest
        arclengths = result.arclengths
        radius_px = result.radius
        surface_area_px = result.surface_area
        volume_px = result.volume

        # Keep rotation angle between -90 to 90 degrees.
        rotation = (rotation + np.pi / 2) % np.pi - np.pi / 2

        needle_diameter_px = self.bn_needle_width_px
        if needle_diameter_px is not None or np.isfinite(pixel_scale):
            if np.isfinite(pixel_scale):
                px_size = 1 / pixel_scale
            else:
                px_size = needle_diameter / needle_diameter_px

            delta_density = abs(self._experimental_setup.drop_density - continuous_density)

            radius = radius_px * px_size
            surface_area = surface_area_px * px_size ** 2
            volume = volume_px * px_size ** 3
            ift = delta_density * gravity * radius ** 2 / bond

            if needle_diameter is not None:
                worthington = (delta_density * gravity * volume) / (PI * ift * needle_diameter)
            else:
                worthington = math.nan
        else:
            radius = math.nan
            surface_area = math.nan
            volume = math.nan
            ift = math.nan
            worthington = math.nan

        self._experimental_drop.bond_number = bond
        self._experimental_drop.apex_coords_px = Vector2(apex_x, apex_y)
        self._experimental_drop.apex_radius_px = radius_px
        self._experimental_drop.rotation = rotation
        self._experimental_drop.residuals = residuals
        self._experimental_drop.arclengths = arclengths
        self._experimental_drop.drop_profile_fit = closest.T[np.argsort(arclengths)]
        self._experimental_drop.apex_radius = radius
        self._experimental_drop.surface_area = surface_area
        self._experimental_drop.volume = volume
        self._experimental_drop.interfacial_tension = ift
        self._experimental_drop.worthington = worthington

        self.bn_status.set(self.Status.FINISHED)

    def cancel(self) -> None:
        if self.bn_status.get().is_terminal:
            return

        if self.bn_status.get() is self.Status.WAITING_FOR_IMAGE:
            self._experimental_setup.image.cancel()

        if self._features is not None:
            self._features.cancel()

        if self._ylfit is not None:
            self._ylfit.cancel()

        self.bn_status.set(self.Status.CANCELLED)

    def _get_status(self) -> Status:
        return self._status

    def _set_status(self, new_status: Status) -> None:
        self._status = new_status
        self.bn_is_cancelled.poke()

        if new_status.is_terminal:
            self._time_end = time.time()

    def _get_image(self) -> Optional[np.ndarray]:
        return self._image

    def _get_is_done(self) -> bool:
        return self.bn_status.get().is_terminal

    def _get_is_cancelled(self) -> bool:
        return self.bn_status.get() is self.Status.CANCELLED

    def _get_progress(self) -> float:
        if self.bn_is_done.get():
            return 1
        else:
            return 0

    def _get_time_start(self) -> float:
        return self._time_start

    def _get_time_est_complete(self) -> float:
        if self._experimental_setup.image is None:
            return math.nan

        return self._experimental_setup.image.est_ready

    def calculate_time_elapsed(self) -> float:
        time_start = self._time_start

        if math.isfinite(self._time_end):
            time_elapsed = self._time_end - time_start
        else:
            time_now = time.time()
            time_elapsed = time_now - time_start

        return time_elapsed

    def calculate_time_remaining(self) -> float:
        if self.bn_is_done.get():
            return 0

        time_est_complete = self.bn_time_est_complete.get()
        time_now = time.time()
        time_remaining = time_est_complete - time_now

        return time_remaining
