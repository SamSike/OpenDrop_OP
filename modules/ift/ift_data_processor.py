from modules.core.classes import ExperimentalSetup
from modules.image.select_regions import (
    user_roi,
    set_scale,
    set_screen_position,
    user_select_region,
)
from modules.ift.younglaplace.younglaplace import young_laplace_fit
from modules.ift.younglaplace.shape import YoungLaplaceShape
from modules.ift.pendant import extract_pendant_features, analyze_ift
from utils.misc import rotation_mat2d
from utils.enums import RegionSelect
from utils.config import MAX_ARCLENGTH
from utils.geometry import Rect2

from PIL import Image
from typing import Callable
import cv2
import os
import csv
import numpy as np
import timeit

# from modules.PlotManager import PlotManager


class IftDataProcessor:
    def process_data(
        self, user_input_data: ExperimentalSetup, callback: Callable = None
    ):

        n_frames = user_input_data.number_of_frames
        time = 0

        for i in range(len(user_input_data.import_files)):
            # Load the image (assuming OpenCV)
            image = user_input_data.import_files[i]
            if image is None:
                print(f"Failed to load image: {image}")
                continue
            print("\nProcessing frame %d of %d..." % (i + 1, n_frames))
            input_file = user_input_data.import_files[i]
            print("\nProcessing " + input_file)
            time_start = timeit.default_timer()
            # 1. Extract drop and needle regions
            # drop_points, needle_diameter_px, drop_region, needle_region, image, drop_image, needle_fit_result = extract_pendant_features(image)
            print(user_input_data.fit_result[i])
            analyzed_ift = analyze_ift(
                user_input_data.fit_result[i],
                drop_density=user_input_data.drop_density,
                continuous_density=user_input_data.density_outer,
                needle_diameter_mm=user_input_data.needle_diameter_mm,
                needle_diameter_px=user_input_data.needle_diameter_px[i],
            )
            self.draw_fitted_shape(user_input_data, i, image)
            time_end = timeit.default_timer()
            duration = time_end - time_start
            analyzed_ift[5] = time + i * user_input_data.frame_interval
            # Save the analyzed IFT results
            # print("Analyzed IFT:", analyzed_ift)
            user_input_data.ift_results[i] = analyzed_ift

            print("Time taken for frame %d: %.2f seconds" % (i + 1, duration))
            print("callback: ", i)

        if callback:
            callback(user_input_data)

    def process_preparation(self, user_input_data: ExperimentalSetup):
        n_frames = user_input_data.number_of_frames
        # Initialize drop_images if not already
        print(
            "####################################: ", len(
                user_input_data.import_files)
        )
        user_input_data.drop_images = ["None"] * n_frames
        # num_of_images = len(user_input_data.import_files)
        user_input_data.drop_points = ["None"] * n_frames
        user_input_data.needle_diameter_px = ["None"] * n_frames
        user_input_data.drop_region = ["None"] * n_frames
        user_input_data.needle_region = ["None"] * n_frames
        user_input_data.fit_result = ["None"] * n_frames
        user_input_data.ift_results = ["None"] * n_frames
        user_input_data.drop_contour_images = ["None"] * n_frames
        user_input_data.processed_images = ["None"] * n_frames

        for i in range(len(user_input_data.import_files)):
            print("\nProcessing frame %d of %d..." % (i + 1, n_frames))
            input_file = user_input_data.import_files[i]
            print("\nProcessing " + input_file)
            time_start = timeit.default_timer()
            # Load the image (assuming OpenCV)
            image_file = user_input_data.import_files[i]
            drop_region = None
            needle_region = None

            if image_file is None:
                print(f"Failed to load image: {input_file}")
                continue

            image = cv2.imread(image_file, cv2.IMREAD_COLOR)
            if image is None:
                print(f"Could not load image at {image_file}")

            screen_size = user_input_data.screen_resolution
            image_size = image.shape
            scale = set_scale(image_size, screen_size)
            screen_position = set_screen_position(screen_size)

            if user_input_data.drop_id_method == RegionSelect.USER_SELECTED:
                print("Select drop region for Image {i}")
                [(min_x, min_y), (max_x, max_y)], _ = user_select_region(
                    image, f"Select drop region for Image {i}", scale, screen_position
                )
                drop_region = Rect2(int(min_x), int(min_y),
                                    int(max_x), int(max_y))
                print("Drop region: ", drop_region)

            if user_input_data.needle_region_method == RegionSelect.USER_SELECTED:
                print("Select needle region for Image {i}")
                [(min_x, min_y), (max_x, max_y)], _ = user_select_region(
                    image, f"Select needle region for Image {i}", scale, screen_position
                )
                needle_region = Rect2(int(min_x), int(
                    min_y), int(max_x), int(max_y))
                print("Needle region: ", needle_region)

            (
                drop_points,
                needle_diameter_px,
                drop_region,
                needle_region,
                image,
                drop_image,
                needle_fit_result,
            ) = extract_pendant_features(image, drop_region, needle_region)
            user_input_data.fit_result[i] = young_laplace_fit(
                drop_points, verbose=True)
            user_input_data.drop_points[i] = drop_points
            user_input_data.needle_diameter_px[i] = needle_diameter_px
            user_input_data.drop_region[i] = drop_region
            user_input_data.needle_region[i] = needle_region
            self.draw_regions(user_input_data, i, image)

    def draw_regions(
        self, user_input_data: ExperimentalSetup, i: int, image: np.ndarray
    ):
        drop_region = user_input_data.drop_region[i]
        needle_region = user_input_data.needle_region[i]
        regions_image = image.copy()
        # Draw drop_region (blue)
        if drop_region is not None:
            regions_image = cv2.rectangle(
                regions_image,
                (int(drop_region.x0), int(drop_region.y0)),
                (int(drop_region.x1), int(drop_region.y1)),
                (255, 0, 0),
                2,
            )
        # Draw needle_region (red)
        if needle_region is not None:
            regions_image = cv2.rectangle(
                regions_image,
                (int(needle_region.x0), int(needle_region.y0)),
                (int(needle_region.x1), int(needle_region.y1)),
                (0, 0, 255),
                2,
            )
        image_pil = Image.fromarray(
            cv2.cvtColor(regions_image, cv2.COLOR_BGR2RGB))
        user_input_data.processed_images[i] = image_pil

    def draw_fitted_shape(
        self, user_input_data: ExperimentalSetup, drop_index: int, image: np.ndarray
    ):
        fit_result = user_input_data.fit_result[drop_index]
        shape = YoungLaplaceShape(fit_result.bond)
        _ = shape(MAX_ARCLENGTH)
        # 2. Pick arclength values to sample.  We’ll reuse the ones from the fit:
        s_values = fit_result.arclengths
        # 3. Generate (r, z) coordinates pointwise
        #    shape(s) returns a length‐2 array [r, z]
        rz = np.array([shape(s) for s in s_values])  # shape (N,2)
        r_coords = rz[:, 0]
        z_coords = rz[:, 1]
        # 4. Now transform into image coords:
        #    a) scale by fitted radius
        rz_scaled = fit_result.radius * rz.T  # shape (2, N)
        #    b) rotate by fitted rotation
        Q = rotation_mat2d(fit_result.rotation)
        xy_fitted = Q @ rz_scaled  # still (2, N)
        #    c) translate to apex location
        apex = np.array([fit_result.apex_x, fit_result.apex_y]).reshape(2, 1)
        xy_fitted += apex
        # Crop the original BGR image using drop_region
        drop_region = user_input_data.drop_region[drop_index]
        y0 = int(drop_region.y0)
        y1 = int(drop_region.y1)
        x0 = int(drop_region.x0)
        x1 = int(drop_region.x1)
        image = cv2.imread(image)

        # Make a copy to draw on (still BGR)
        img_to_draw_on = image
        # Translate fitted points to be relative to the cropped image
        translated_fitted_x = xy_fitted[0, :]
        translated_fitted_y = xy_fitted[1, :]
        # Draw the fitted shape as individual points on the cropped BGR image
        point_radius = 0  # As in your existing code
        point_color_bgr = (0, 0, 255)
        point_thickness = -1
        for i in range(len(translated_fitted_x)):
            x_coord = int(translated_fitted_x[i])
            y_coord = int(translated_fitted_y[i])
            cv2.circle(
                img_to_draw_on,
                (x_coord, y_coord),
                point_radius,
                point_color_bgr,
                point_thickness,
            )

        # (cross-platform)
        save_dir = os.path.join(
            os.path.join(os.path.expanduser("~")),
            "OpenDrop",
            "outputs",
            "contour_images"
        )
        os.makedirs(save_dir, exist_ok=True)

        original_path = user_input_data.import_files[drop_index]
        original_name = os.path.basename(original_path)

        save_path = os.path.join(save_dir, original_name)
        cv2.imwrite(save_path, img_to_draw_on)

        user_input_data.drop_contour_images[drop_index] = save_path

    def save_result(self, user_input_data: ExperimentalSetup, output_file_path: str):
        """
        Save experiment results to a CSV file with columns:
        Filename, Time, IFT, V, SA, Bond, Worth
        """
        with open(output_file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "Filename",
                    "Time",
                    "IFT (mN/m)",
                    "Volume (mm^3)",
                    "Surface Area (mm^2)",
                    "Bond",
                    "Worth",
                ]
            )
            for i, result in enumerate(user_input_data.ift_results):
                if result is not None and result != "None":
                    # result: [IFT, V, SA, Bond, Worth, Time]
                    writer.writerow(
                        [
                            user_input_data.import_files[i],
                            f"{result[5]:.1f}",
                            f"{result[0]:.1f}",
                            f"{result[1]:.2f}",
                            f"{result[2]:.2f}",
                            f"{result[3]:.4f}",
                            f"{result[4]:.4f}",
                        ]
                    )
