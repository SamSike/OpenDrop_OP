#!/usr/bin/env python
# coding=utf-8
from modules.core.classes import ExperimentalDrop
from utils.config import LEFT_ANGLE, RIGHT_ANGLE
from utils.enums import FittingMethod

# from __future__ import print_function


def perform_fits(
    experimental_drop: ExperimentalDrop,
    tangent=False,
    polynomial=False,
    circle=False,
    ellipse=False,
    yl=False,
):
    if tangent == True:
        from modules.fitting.polynomial_fit import polynomial_fit

        tangent_angles, tangent_CPs, tangent_lines, tangent_errors, tangent_timings = (
            polynomial_fit(experimental_drop.drop_contour, polynomial_degree=1)
        )
        experimental_drop.contact_angles[FittingMethod.TANGENT_FIT] = {}
        experimental_drop.contact_angles[FittingMethod.TANGENT_FIT][LEFT_ANGLE] = (
            tangent_angles[0]
        )
        experimental_drop.contact_angles[FittingMethod.TANGENT_FIT][RIGHT_ANGLE] = (
            tangent_angles[1]
        )
        experimental_drop.contact_angles[FittingMethod.TANGENT_FIT][
            "contact points"
        ] = tangent_CPs
        experimental_drop.contact_angles[FittingMethod.TANGENT_FIT][
            "tangent lines"
        ] = tangent_lines
        experimental_drop.contact_angles[FittingMethod.TANGENT_FIT][
            "errors"
        ] = tangent_errors
        experimental_drop.contact_angles[FittingMethod.TANGENT_FIT][
            "timings"
        ] = tangent_timings

    if polynomial == True:
        from modules.fitting.polynomial_fit import polynomial_fit

        (
            polynomial_angles,
            polynomial_CPs,
            polynomial_lines,
            polynomial_errors,
            polynomial_timings,
        ) = polynomial_fit(experimental_drop.drop_contour, polynomial_degree=2)
        experimental_drop.contact_angles[FittingMethod.POLYNOMIAL_FIT] = {}
        experimental_drop.contact_angles[FittingMethod.POLYNOMIAL_FIT][LEFT_ANGLE] = (
            polynomial_angles[0]
        )
        experimental_drop.contact_angles[FittingMethod.POLYNOMIAL_FIT][RIGHT_ANGLE] = (
            polynomial_angles[1]
        )
        experimental_drop.contact_angles[FittingMethod.POLYNOMIAL_FIT][
            "contact points"
        ] = polynomial_CPs
        experimental_drop.contact_angles[FittingMethod.POLYNOMIAL_FIT][
            "tangent lines"
        ] = polynomial_lines
        experimental_drop.contact_angles[FittingMethod.POLYNOMIAL_FIT][
            "errors"
        ] = polynomial_errors
        experimental_drop.contact_angles[FittingMethod.POLYNOMIAL_FIT][
            "timings"
        ] = polynomial_timings

    if circle == True:
        from modules.fitting.circular_fit import circular_fit

        (
            circle_angles,
            circle_center,
            circle_radius,
            circle_intercepts,
            circle_errors,
            circle_timings,
        ) = circular_fit(experimental_drop.drop_contour)
        experimental_drop.contact_angles[FittingMethod.CIRCLE_FIT] = {}
        experimental_drop.contact_angles[FittingMethod.CIRCLE_FIT][LEFT_ANGLE] = (
            circle_angles[0]
        )
        experimental_drop.contact_angles[FittingMethod.CIRCLE_FIT][RIGHT_ANGLE] = (
            circle_angles[1]
        )
        experimental_drop.contact_angles[FittingMethod.CIRCLE_FIT][
            "baseline intercepts"
        ] = circle_intercepts
        experimental_drop.contact_angles[FittingMethod.CIRCLE_FIT][
            "circle center"
        ] = circle_center
        experimental_drop.contact_angles[FittingMethod.CIRCLE_FIT][
            "circle radius"
        ] = circle_radius
        experimental_drop.contact_angles[FittingMethod.CIRCLE_FIT][
            "errors"
        ] = circle_errors
        experimental_drop.contact_angles[FittingMethod.CIRCLE_FIT][
            "timings"
        ] = circle_timings

    if ellipse == True:
        from modules.fitting.ellipse_fit import ellipse_fit

        (
            ellipse_angles,
            ellipse_intercepts,
            ellipse_center,
            ellipse_ab,
            ellipse_rotation,
            ellipse_errors,
            ellipse_timings,
        ) = ellipse_fit(experimental_drop.drop_contour)
        experimental_drop.contact_angles[FittingMethod.ELLIPSE_FIT] = {}
        experimental_drop.contact_angles[FittingMethod.ELLIPSE_FIT][LEFT_ANGLE] = (
            ellipse_angles[0]
        )
        experimental_drop.contact_angles[FittingMethod.ELLIPSE_FIT][RIGHT_ANGLE] = (
            ellipse_angles[1]
        )
        experimental_drop.contact_angles[FittingMethod.ELLIPSE_FIT][
            "baseline intercepts"
        ] = ellipse_intercepts
        experimental_drop.contact_angles[FittingMethod.ELLIPSE_FIT][
            "ellipse center"
        ] = ellipse_center
        experimental_drop.contact_angles[FittingMethod.ELLIPSE_FIT][
            "ellipse a and b"
        ] = ellipse_ab
        experimental_drop.contact_angles[FittingMethod.ELLIPSE_FIT][
            "ellipse rotation"
        ] = ellipse_rotation
        experimental_drop.contact_angles[FittingMethod.ELLIPSE_FIT][
            "errors"
        ] = ellipse_errors
        experimental_drop.contact_angles[FittingMethod.ELLIPSE_FIT][
            "timings"
        ] = ellipse_timings

    if yl == True:
        from modules.fitting.BA_fit import yl_fit

        (
            yl_angles,
            yl_bo,
            yl_baselinewidth,
            yl_volume,
            yl_shape,
            yl_baseline,
            yl_errors,
            sym_errors,
            yl_timings,
        ) = yl_fit(experimental_drop.drop_contour)
        experimental_drop.contact_angles[FittingMethod.YL_FIT] = {}
        experimental_drop.contact_angles[FittingMethod.YL_FIT][LEFT_ANGLE] = yl_angles[
            0
        ]
        experimental_drop.contact_angles[FittingMethod.YL_FIT][RIGHT_ANGLE] = yl_angles[
            1
        ]
        experimental_drop.contact_angles[FittingMethod.YL_FIT]["bond number"] = yl_bo
        experimental_drop.contact_angles[FittingMethod.YL_FIT][
            "baseline width"
        ] = yl_baselinewidth
        experimental_drop.contact_angles[FittingMethod.YL_FIT]["volume"] = yl_volume
        experimental_drop.contact_angles[FittingMethod.YL_FIT]["fit shape"] = yl_shape
        experimental_drop.contact_angles[FittingMethod.YL_FIT]["baseline"] = yl_baseline
        experimental_drop.contact_angles[FittingMethod.YL_FIT]["errors"] = yl_errors
        experimental_drop.contact_angles[FittingMethod.YL_FIT][
            "symmetry errors"
        ] = sym_errors
        experimental_drop.contact_angles[FittingMethod.YL_FIT]["timings"] = yl_timings
