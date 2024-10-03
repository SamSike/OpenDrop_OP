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


from pathlib import Path
from typing import Union, MutableSequence

import cv2
import subprocess
import numpy as np

from .image_sequence import ImageSequenceAcquirer


class Flea3Acquirer(ImageSequenceAcquirer):
    def __init__(self) -> None:
        super().__init__()

    def load_image(self, color_image: int = 0, file_name: Union[Path, str] = 'FCG.pgm'):
        subprocess.call(["./FCGrab"])
        image = cv2.imread(file_name, color_image)

        if image is None:
            raise ValueError(f"Failed to load image from '{file_name}'")

        image.flags.writeable = False
        images: MutableSequence[np.ndarray] = [image]
        self.bn_images.set(images)
