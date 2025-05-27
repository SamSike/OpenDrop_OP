from modules.ift.younglaplace.younglaplace import YoungLaplaceFitResult
from modules.ift.circle import circle_fit, CircleFitResult
from modules.ift.needle import needle_fit, NeedleFitResult
from modules.image.select_regions import get_ift_regions
from utils.geometry import Rect2, Vector2
from utils.misc import rotation_mat2d

from typing import NamedTuple, Optional, Tuple, List
import math
import cv2
import numpy as np

__all__ = ("PendantFeatures", "extract_pendant_features", "find_pendant_apex")

# Math constants.
PI = math.pi

RotatedRect = Tuple[Vector2[float], Vector2[float], Vector2[float], Vector2[float]]


class PendantFeatures(NamedTuple):
    labels: np.ndarray

    drop_points: np.ndarray = np.empty((2, 0), dtype=int)

    drop_apex: Optional[Vector2[int]] = None
    drop_radius: Optional[float] = None
    drop_rotation: Optional[float] = None

    needle_rect: Optional[RotatedRect] = None
    needle_diameter: Optional[float] = None

    def __eq__(self, other: "PendantFeatures") -> bool:
        if not isinstance(other, PendantFeatures):
            return False

        for v1, v2 in zip(self, other):
            if isinstance(v1, np.ndarray):
                if not (v1 == v2).all():
                    return False
            else:
                if not (v1 == v2):
                    return False
        else:
            return True


def extract_pendant_features(
    image,
    drop_region: Optional[Rect2[int]] = None,
    needle_region: Optional[Rect2[int]] = None,
    *,
    thresh1: float = 80.0,
    thresh2: float = 160.0,
    labels: bool = False,
) -> PendantFeatures:
    """
    Extract needle and drop features from the given image.
    If the regions are not provided, they will be automatically detected.
    Returns a PendantFeatures object containing the extracted features.
    """

    if drop_region is None or needle_region is None:
        automated_drop_region, automated_needle_region = get_ift_regions(image)

        if drop_region is None:
            drop_region = automated_drop_region
        if needle_region is None:
            needle_region = automated_needle_region

    if drop_region is not None:
        drop_image = image[
            drop_region.y0 : drop_region.y1 + 1, drop_region.x0 : drop_region.x1 + 1
        ]
        print(
            f"Drop region: {drop_region.x0}, {drop_region.y0}, {drop_region.x1}, {drop_region.y1}"
        )
        print(f"Drop image shape: {drop_image.shape}")

    if needle_region is not None:
        needle_image = image[
            needle_region.y0 : needle_region.y1 + 1,
            needle_region.x0 : needle_region.x1 + 1,
        ]

    drop_points = np.empty((2, 0), dtype=int)
    drop_apex = None
    drop_radius = None
    drop_rotation = None

    if drop_image is not None:
        if len(drop_image.shape) > 2:
            drop_image = cv2.cvtColor(drop_image, cv2.COLOR_RGB2GRAY)

        drop_points = _extract_drop_edge(drop_image, thresh1, thresh2)

        # There shouldn't be more points than the perimeter of the image.
        if drop_points.shape[1] < 2 * (image.shape[0] + image.shape[1]):
            ans = find_pendant_apex(drop_points)
            if ans is not None:
                drop_apex, drop_radius, drop_rotation = ans

    needle_points = np.empty((2, 0), dtype=int)
    needle_rect = None
    needle_diameter_px = None

    if needle_image is not None:
        if len(needle_image.shape) > 2:
            needle_image = cv2.cvtColor(needle_image, cv2.COLOR_RGB2GRAY)

        blur = cv2.GaussianBlur(needle_image, ksize=(5, 5), sigmaX=0)
        dx = cv2.Scharr(blur, cv2.CV_16S, dx=1, dy=0)
        dy = cv2.Scharr(blur, cv2.CV_16S, dx=0, dy=1)

        # Use magnitude of gradient squared to get sharper edges.
        mask = dx.astype(float) ** 2 + dy.astype(float) ** 2
        mask = (mask / mask.max() * (2**8 - 1)).astype(np.uint8)
        cv2.adaptiveThreshold(
            mask,
            maxValue=1,
            adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            thresholdType=cv2.THRESH_BINARY,
            blockSize=5,
            C=0,
            dst=mask,
        )

        # Hack: Thin edges using cv2.Canny()
        needle_edges = cv2.Canny(
            dx=mask * dx, dy=mask * dy, threshold1=0.0, threshold2=0.0
        )

        needle_points = np.array(needle_edges.nonzero()[::-1])

        # Use left and right-most points only for fitting.
        needle_outer_points = np.block(
            [
                [
                    np.argmax(needle_edges, axis=1),
                    (needle_edges.shape[1] - 1)
                    - np.argmax(needle_edges[:, ::-1], axis=1),
                ],
                [np.arange(needle_edges.shape[0]), np.arange(needle_edges.shape[0])],
            ]
        )

        needle_fit_result: NeedleFitResult = needle_fit(needle_outer_points)
        if needle_fit_result is not None:
            needle_residuals = np.abs(needle_fit_result.residuals)
            needle_lmask = needle_fit_result.lmask
            needle_rmask = ~needle_lmask
            needle_lpoints = needle_outer_points[
                :, (needle_residuals < 1.0) & needle_lmask
            ]
            needle_rpoints = needle_outer_points[
                :, (needle_residuals < 1.0) & needle_rmask
            ]
            n_lpoints = needle_lpoints.shape[1]
            n_rpoints = needle_rpoints.shape[1]

            # Make sure there's an even number of points on the left and right sides, otherwise probably a bad
            # fit.
            if (
                n_lpoints > 0
                and n_rpoints > 0
                and abs(n_lpoints - n_rpoints) / (n_lpoints + n_rpoints) < 0.33
            ):
                needle_rho = needle_fit_result.rho
                needle_radius = needle_fit_result.radius
                needle_rotation = needle_fit_result.rotation

                needle_rotation_mat = rotation_mat2d(needle_rotation)
                needle_perp = needle_rotation_mat @ [1, 0]
                needle_lpoints_z = (needle_rotation_mat.T @ needle_lpoints)[1]
                needle_rpoints_z = (needle_rotation_mat.T @ needle_rpoints)[1]
                needle_min_z = min(needle_lpoints_z.min(), needle_rpoints_z.min())
                needle_max_z = max(needle_lpoints_z.max(), needle_rpoints_z.max())
                needle_tip1 = needle_rotation_mat @ [needle_rho, needle_min_z]
                needle_tip2 = needle_rotation_mat @ [needle_rho, needle_max_z]

                needle_rect = (
                    Vector2(needle_tip1 - needle_perp * needle_radius),
                    Vector2(needle_tip1 + needle_perp * needle_radius),
                    Vector2(needle_tip2 - needle_perp * needle_radius),
                    Vector2(needle_tip2 + needle_perp * needle_radius),
                )
                needle_diameter_px = 2 * needle_radius

    if drop_region is not None:
        drop_points += np.reshape(drop_region.position, (2, 1))
        if drop_apex is not None:
            drop_apex += drop_region.position

    if needle_region is not None:
        needle_points += np.reshape(needle_region.position, (2, 1))
        if needle_rect is not None:
            needle_rect = (
                needle_region.position + needle_rect[0],
                needle_region.position + needle_rect[1],
                needle_region.position + needle_rect[2],
                needle_region.position + needle_rect[3],
            )

    if labels:
        labels_array = np.zeros(image.shape[:2], dtype=np.uint8)
        labels_array[tuple(drop_points)[::-1]] = 1
        labels_array[tuple(needle_points)[::-1]] = 2
    else:
        labels_array = None

    return (
        drop_points,
        needle_diameter_px,
        drop_region,
        needle_region,
        image,
        drop_image,
        needle_fit_result,
    )


def _extract_drop_edge(gray: np.ndarray, thresh1: float, thresh2: float) -> np.ndarray:
    blur = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)
    dx = cv2.Scharr(blur, cv2.CV_16S, dx=1, dy=0)
    dy = cv2.Scharr(blur, cv2.CV_16S, dx=0, dy=1)

    # Use magnitude of gradient squared to get sharper edges.
    grad = dx.astype(float) ** 2 + dy.astype(float) ** 2
    grad /= grad.max()
    grad = (grad * (2**8 - 1)).astype(np.uint8)

    cv2.adaptiveThreshold(
        grad,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=5,
        C=0,
        dst=grad,
    )

    # Hack: Use cv2.Canny() to do non-max suppression edge thinning.
    mask = _largest_connected_component(grad)
    edges = cv2.Canny(dx * mask, dy * mask, thresh1, thresh2)
    points = np.array(edges.nonzero()[::-1])

    return points


def _largest_connected_component(gray: np.ndarray) -> np.ndarray:
    mask: np.ndarray

    # Values returned are n_labels, labels, stats, centroids.
    _, labels, stats, _ = cv2.connectedComponentsWithStats(gray, connectivity=4)

    ix = np.argsort(stats[:, cv2.CC_STAT_WIDTH] * stats[:, cv2.CC_STAT_HEIGHT])[::-1]
    if len(ix) > 1:
        if ix[0] == 0:
            # Label 0 is the background.
            biggest_label = ix[1]
        else:
            biggest_label = ix[0]

        mask = labels == biggest_label
    else:
        mask = np.ones(gray.shape, dtype=bool)

    return mask


def find_pendant_apex(data: Tuple[np.ndarray, np.ndarray]) -> Optional[tuple]:

    x, y = data

    if len(x) == 0 or len(y) == 0:
        return None

    xc = x.mean()
    yc = y.mean()
    radius = np.hypot(x - xc, y - yc).mean()

    # Fit a circle to the most circular part of the data.
    circle_fit_result: CircleFitResult = circle_fit(
        data,
        loss="arctan",
        f_scale=radius / 100,
    )
    if circle_fit_result is None:
        return None

    xc, yc = circle_fit_result.center
    radius = circle_fit_result.radius
    resids = np.abs(circle_fit_result.residuals)
    resids_50ptile = np.quantile(resids, 0.5)

    # The somewhat circular-ish part of the drop profile.
    bowl_mask = resids < 10 * resids_50ptile
    bowl_x = x[bowl_mask]
    bowl_y = y[bowl_mask]

    if len(bowl_x) == 0:
        return None

    # Don't need these variables anymore.
    del resids, resids_50ptile

    # Find the symmetry axis of bowl.
    Ixx, Iyy, Ixy = _calculate_inertia(bowl_x, bowl_y)

    # Eigenvector calculation for a symmetric 2x2 matrix.
    rotation = 0.5 * np.arctan2(2 * Ixy, Ixx - Iyy)
    unit_r = np.array([np.cos(rotation), np.sin(rotation)])
    unit_z = np.array([-np.sin(rotation), np.cos(rotation)])

    bowl_r = unit_r @ [bowl_x - xc, bowl_y - yc]
    bowl_z = unit_z @ [bowl_x - xc, bowl_y - yc]
    bowl_r_ix = np.argsort(bowl_r)
    bowl_z_ix = np.argsort(bowl_z)

    # Calculate "asymmetry" along each axis. We define this to be the squared difference between the left and
    # right points, integrated along the axis.
    ma_kernel = np.ones(max(1, len(bowl_r) // 10))
    ma_kernel /= len(ma_kernel)
    asymm_r = (
        np.convolve((bowl_z - bowl_z.mean())[bowl_r_ix], ma_kernel, mode="valid") ** 2
    ).sum()
    asymm_z = (
        np.convolve((bowl_r - bowl_r.mean())[bowl_z_ix], ma_kernel, mode="valid") ** 2
    ).sum()
    if asymm_z > asymm_r:
        # Swap axes so z is the symmetry axis.
        rotation -= PI / 2
        unit_r, unit_z = -unit_z, unit_r
        bowl_r, bowl_z = -bowl_z, bowl_r
        bowl_r_ix, bowl_z_ix = bowl_z_ix[::-1], bowl_r_ix

    # No longer useful variables (and potentially incorrect after axes swapping).
    del asymm_r, asymm_z

    bowl_z_hist, _ = np.histogram(bowl_z, bins=2 + len(bowl_z) // 10)
    if bowl_z_hist.argmax() > len(bowl_z_hist) / 2:
        # Rotate by 180 degrees since points are accumulating (where dz/ds ~ 0) at high z, i.e. drop apex is
        # not on the bottom.
        rotation += PI
        unit_r *= -1
        unit_z *= -1
        bowl_r *= -1
        bowl_z *= -1
        bowl_r_ix = bowl_r_ix[::-1]
        bowl_z_ix = bowl_z_ix[::-1]

    bowl_z_ix_apex_arc_stop = np.searchsorted(
        np.abs(bowl_r), 0.3 * radius, side="right", sorter=bowl_z_ix
    )
    apex_arc_ix = bowl_z_ix[:bowl_z_ix_apex_arc_stop]
    apex_arc_x = bowl_x[apex_arc_ix]
    apex_arc_y = bowl_y[apex_arc_ix]

    if len(apex_arc_ix) > 10:
        # Fit another circle to a smaller arc around the apex. Points within 0.3 radians of the apex should
        # have roughly constant curvature across typical Bond values.
        circle_fit_result = circle_fit(
            np.array([apex_arc_x, apex_arc_y]),
            xc=xc,
            yc=yc,
        )
        if circle_fit_result is not None:
            xc, yc = circle_fit_result.center
            radius = circle_fit_result.radius

    apex_x, apex_y = [xc, yc] - radius * unit_z

    # Restrict rotation to [-pi, pi].
    rotation = (rotation + PI) % (2 * PI) - PI

    return Vector2(apex_x, apex_y), radius, rotation


def _calculate_inertia(x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
    x = x - x.mean()
    y = y - y.mean()

    Ixx = (y**2).sum()
    Iyy = (x**2).sum()
    Ixy = -(x @ y)

    return Ixx, Iyy, Ixy


def _circle_residues(params, x, y):
    xc, yc, radius = params
    r = np.hypot(x - xc, y - yc)
    return r - radius


def _circle_jac(params, x, y):
    jac = np.empty((len(x), 3))

    xc, yc, radius = params
    dist_x = x - xc
    dist_y = y - yc
    r = np.hypot(dist_x, dist_y)

    jac[:, 0] = -dist_x / r
    jac[:, 1] = -dist_y / r
    jac[:, 2] = -1

    return jac


def analyze_ift(
    fit_result: YoungLaplaceFitResult,
    *,
    drop_density: float,
    continuous_density: float = 0,
    needle_diameter_mm: float,
    needle_diameter_px: float = 0,
):
    gravity = 9.81
    # 1) figure out how many pixels per millimetre
    px_per_mm = needle_diameter_mm / needle_diameter_px

    # 2) unpack the pixel‐space results
    radius_px = fit_result.radius  # ensure positive
    volume_px = fit_result.volume
    surface_area_px = fit_result.surface_area
    bond = fit_result.bond
    delta_density = abs(drop_density - continuous_density)
    radius = radius_px * px_per_mm
    surface_area = surface_area_px * px_per_mm**2
    volume = volume_px * px_per_mm**3
    IFT = (delta_density * gravity * radius**2 / bond) / 1000

    # 5) Worthington number
    worthington = (
        (delta_density * gravity * volume) / (PI * IFT * needle_diameter_mm)
    ) / 1000

    return [IFT, volume, surface_area, bond, worthington, None]


def auto_crop(
    img: np.ndarray,
    padding: int = 5,
    area_thresh: int = 1,
    drop_frac: float = 1,
    scharr_block: int = 5,
    canny1: float = 80,
    canny2: float = 160,
) -> Tuple[np.ndarray, tuple]:

    original = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    H, W = gray.shape
    # Applying 7x7 Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # 1) rough mask via inverted Otsu + largest CC
    threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(thr, 8)

    analysis = cv2.connectedComponentsWithStats(threshold, 8)
    (totalLabels, label_ids, stats, centroids) = analysis
    if totalLabels <= 1:
        print("drops found.")
        return original, None

        # Filter for components entering from the top and find the largest among them
    top_entering_blobs_indices = []
    for i in range(1, totalLabels):  # Iterate through all components (0 is background)
        if stats[i, cv2.CC_STAT_TOP] == 0:
            top_entering_blobs_indices.append(i)

    if not top_entering_blobs_indices:
        print("No blobs found entering from the top of the frame.")
        return original, None

    # Select the largest blob among those entering from the top
    blob = -1
    max_area_found = -1
    for idx in top_entering_blobs_indices:
        area = stats[idx, cv2.CC_STAT_AREA]
        if area > max_area_found:
            max_area_found = area
            blob = idx

    if blob == -1:  # Should not happen if top_entering_blobs_indices was populated
        print("Error selecting largest top-entering blob.")
        return original, None

    if stats[blob, cv2.CC_STAT_AREA] < area_thresh:
        print(
            f"Largest top-entering blob (ID: {blob}, Area: {stats[blob, cv2.CC_STAT_AREA]}) too small (threshold: {area_thresh})."
        )
        return original, None

    x, y, bw, bh, _ = stats[blob]
    # print(f"Blob ID: {blob}, Area: {stats[blob, cv2.CC_STAT_AREA]}, Bounding box: (x= {x}, y= {y}) - (w= {bw}, h= {bh})")
    roi = gray[y : y + bh, x : x + bw]
    roi_mask = (label_ids[y : y + bh, x : x + bw] == blob).astype(np.uint8) * 255

    # 2) Scharr→adaptiveThresh→Canny inside ROI
    blur = cv2.GaussianBlur(roi, (scharr_block, scharr_block), 0)
    dx = cv2.Scharr(blur, cv2.CV_16S, 1, 0)
    dy = cv2.Scharr(blur, cv2.CV_16S, 0, 1)
    grad = dx.astype(float) ** 2 + dy.astype(float) ** 2
    grad = np.uint8(255 * (grad / grad.max()))
    cv2.adaptiveThreshold(
        grad,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=scharr_block,
        C=0,
        dst=grad,
    )
    grad = cv2.bitwise_and(grad, grad, mask=roi_mask)
    edges = cv2.Canny(grad, canny1, canny2)

    # 3) collect edge points *only* in the bottom (1-drop_frac) of ROI:
    pts = np.column_stack(np.nonzero(edges))  # (row, col)
    if len(pts) < 20:
        print("Too few edges.")
        return original, None
    # Calculate width of the blob at each row within the ROI
    blob_widths_at_each_row = np.sum(roi_mask // 255, axis=1)
    # Define the upper part of the blob to estimate needle width
    # Consider top 15% of blob height, but at least 3px and at most 20px
    initial_needle_scan_height = max(3, min(int(bh * 0.15), 500))
    # Ensure scan height is less than blob height for sensible indexing
    if initial_needle_scan_height >= bh and bh > 0:
        initial_needle_scan_height = bh - 1
    elif bh == 0:  # Should not happen if blob found
        initial_needle_scan_height = 0
    avg_needle_width = 0
    if initial_needle_scan_height > 0:
        candidate_needle_widths = blob_widths_at_each_row[:initial_needle_scan_height]
        if np.any(candidate_needle_widths > 0):
            avg_needle_width = np.median(
                candidate_needle_widths[candidate_needle_widths > 0]
            )

    if (
        avg_needle_width <= 1
    ):  # If needle width is too small or not found, use a small portion of top widths
        fallback_scan_height = max(1, int(bh * 0.05))
        if bh > 0 and np.any(blob_widths_at_each_row[:fallback_scan_height] > 0):
            avg_needle_width = np.mean(
                blob_widths_at_each_row[:fallback_scan_height][
                    blob_widths_at_each_row[:fallback_scan_height] > 0
                ]
            )
        if avg_needle_width <= 0:  # Absolute fallback if still no valid width
            avg_needle_width = 1
    expansion_factor = 1  # Drop should be significantly wider than needle
    search_start_row = initial_needle_scan_height

    found_expansion_point = False
    calculated_row_thresh = 0
    for current_row in range(search_start_row, bh):
        # Add small absolute diff
        if (
            blob_widths_at_each_row[current_row] > expansion_factor * avg_needle_width
            and blob_widths_at_each_row[current_row] > avg_needle_width + 2
        ):
            calculated_row_thresh = current_row
            found_expansion_point = True
            # print(f"Dynamic row_thresh: Initial needle width ~{avg_needle_width:.1f}px. Expansion at row {current_row} (width {blob_widths_at_each_row[current_row]}px).")
            break

    if not found_expansion_point:
        print(
            f"No clear expansion point found. Initial needle width ~{avg_needle_width:.1f}px. Using drop_frac based fallback: {calculated_row_thresh}."
        )
        # Already defaulted to drop_frac based
    row_thresh = calculated_row_thresh

    # print(f"Row threshold for drop detection: {row_thresh} (calculated)")
    # --- End of dynamic row_thresh determination ---
    def create_bounds_array(x1, y1, x2, y2):
        # Ensure coordinates are integers for array creation if they are not None
        if any(v is None for v in [x1, y1, x2, y2]):
            return None
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        return np.array(
            [
                [[x1, y1, x2, y1]],  # top edge
                [[x2, y1, x2, y2]],  # right edge
                [[x2, y2, x1, y2]],  # bottom edge
                [[x1, y2, x1, y1]],  # left edge
            ],
            dtype=np.int32,
        )

    # Create the bounding box for the entire ROI
    x1_roi = x
    y1_roi = y
    x2_roi = x + bw
    y2_roi = y + bh
    # Create the absolute bounding box for the entire ROI
    abs_bounds = create_bounds_array(x1_roi, y1_roi, x2_roi, y2_roi)
    # Create the cropped bounding box for the entire ROI
    crop_bounds = create_bounds_array(x1_roi, y1_roi, x2_roi, y2_roi)
    crop_roi = original[y1_roi:y2_roi, x1_roi:x2_roi]
    if not found_expansion_point:
        needle_pts = pts[pts[:, 0] < row_thresh]
        pts_xy_needle = needle_pts[:, ::-1]  # (x, y) coordinates
        if pts_xy_needle.shape[0] > 0:  # Ensure there are points to process
            # These are min/max coordinates of the needle points, *relative to the ROI's top-left corner*
            needle_x1_roi = np.min(pts_xy_needle[:, 0])
            needle_x2_roi = np.max(pts_xy_needle[:, 0])
            needle_y1_roi = np.min(pts_xy_needle[:, 1])
            needle_y2_roi = np.max(pts_xy_needle[:, 1])
            needle_abs_bounds = create_bounds_array(
                x + needle_x1_roi - padding,
                y + needle_y1_roi,
                x + needle_x2_roi + padding,
                y + needle_y2_roi - padding,
            )
            needle_crop_bounds = create_bounds_array(
                needle_x1_roi - padding,
                needle_y1_roi,
                needle_x2_roi + padding,
                needle_y2_roi - padding,
            )
            # Crop the original image using the final absolute bounding box coordinates
            crop = original[
                needle_y1_roi:needle_y2_roi, x + needle_x1_roi : x + needle_x2_roi
            ]
            needle_rect = Rect2(
                (x + needle_x1_roi, y + needle_y1_roi),
                (x + needle_x2_roi, y + needle_y2_roi),
            )
            return needle_rect
    else:
        needle_pts = pts[pts[:, 0] < row_thresh]
        pts_xy_needle = needle_pts[:, ::-1]  # (x, y) coordinates
        if pts_xy_needle.shape[0] > 0:  # Ensure there are points to process
            # These are min/max coordinates of the needle points, *relative to the ROI's top-left corner*
            needle_x1_roi = np.min(pts_xy_needle[:, 0]) - padding
            needle_x2_roi = np.max(pts_xy_needle[:, 0]) + padding
            needle_y1_roi = np.min(pts_xy_needle[:, 1])
            needle_y2_roi = np.max(pts_xy_needle[:, 1]) - padding
            needle_abs_bounds = create_bounds_array(
                x + needle_x1_roi,
                y + needle_y1_roi,
                x + needle_x2_roi,
                y + needle_y2_roi,
            )
            needle_crop_bounds = create_bounds_array(
                needle_x1_roi - padding, needle_y1_roi, needle_x2_roi, needle_y2_roi
            )
            needle_rect = Rect2(
                (x + needle_x1_roi, y + needle_y1_roi),
                (x + needle_x2_roi, y + needle_y2_roi),
            )

        drop_pts = pts[pts[:, 0] >= row_thresh]
        pts_xy_drop = drop_pts[:, ::-1]  # (x, y) coordinates
        if pts_xy_drop.shape[0] > 0:  # Ensure there are points to process
            # These are min/max coordinates of the drop points, *relative to the ROI's top-left corner*
            drop_x1_roi = np.min(pts_xy_drop[:, 0]) - padding
            drop_x2_roi = np.max(pts_xy_drop[:, 0]) + padding
            drop_y1_roi = np.min(pts_xy_drop[:, 1])  # - padding
            drop_y2_roi = np.max(pts_xy_drop[:, 1]) + padding
            drop_abs_bounds = create_bounds_array(
                x + drop_x1_roi, y + drop_y1_roi, x + drop_x2_roi, y + drop_y2_roi
            )
            drop_crop_bounds = create_bounds_array(
                drop_x1_roi, drop_y1_roi, drop_x2_roi, drop_y2_roi
            )
            drop_rect = Rect2(
                (x + drop_x1_roi, y + drop_y1_roi), (x + drop_x2_roi, y + drop_y2_roi)
            )

        crop = original[drop_y1_roi:drop_y2_roi, x + drop_x1_roi : x + drop_x2_roi]
        return drop_rect, needle_rect
