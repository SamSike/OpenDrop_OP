import cv2
import os
import numpy as np






def fit_needle(img, needle_diameter):
    # known needle diameter in millimeters
    needle_diameter_mm = needle_diameter
    # adjustable parameters
    vertical_pct = 0.5     # fraction of height to keep from top
    horizontal_pct = 1   # fraction of width to keep, centered
    blur_kernel = (3, 3)   # kernel size for Gaussian blur
    canny_thresh1 = 50     # first threshold for Canny edge detection
    canny_thresh2 = 150    # second threshold for Canny edge detection
    # adjustable parameters for Hough line detection
    rho = 1               # distance resolution of the accumulator in pixels
    theta = np.pi / 180    # angle resolution of the accumulator in radians
    hough_thresh = 39    # threshold for the accumulator
    min_line_length = 25  # minimum length of line to be detected
    max_line_gap = 25     # maximum gap between lines to be considered a single line
    min_x_separation = 5 # minimum x-separation between two lines to be considered a pair
    # adjustable parameter: max angle difference (degrees) allowed between paired segments
    pair_angle_tol = 1
    # filter out non-vertical lines using the 0°/180° convention
    angle_tolerance = 5  # degrees
    # filter to the two segments whose y‐centers match most closely
    y_tolerance = 50  # pixels
    #target parameters
    m_per_pixel = None # in meters

    cropped = img.copy()

    # convert to grayscale
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    # blur to reduce noise
    blurred = cv2.GaussianBlur(gray, blur_kernel, 0)
    blurred = cv2.addWeighted(blurred, 1.5, blurred, -0.5, 0)
    # detect edges
    edges = cv2.Canny(blurred, canny_thresh1, canny_thresh2)

    ret, thresh = cv2.threshold(edges, 127, 255,cv2.THRESH_BINARY)

    thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB)

    # detect lines using Probabilistic Hough Transform
    lines = cv2.HoughLinesP(edges, rho, theta, hough_thresh,
                            minLineLength=min_line_length,
                            maxLineGap=max_line_gap)

    
    #print("houghs length of lines: ",len(lines))
    if lines is not None:
        # compute dx, dy for each segment without reshaping
        dx = lines[:,0,2] - lines[:,0,0]
        dy = lines[:,0,3] - lines[:,0,1]
        # raw angle relative to horizontal: -180…+180
        raw_angles = np.degrees(np.arctan2(dy, dx))
        # convert so 0° = vertical up, 180° = vertical down
        orient = (raw_angles + 90) % 180
        # keep only those within tolerance of vertical
        mask = (orient <= angle_tolerance) | (orient >= 180 - angle_tolerance)
        lines = lines[mask]
    else:
        lines = None
    
    
    #print("vertical length of lines: ",len(lines))
    if lines is not None and len(lines) > 1:
        segs = lines.reshape(-1, 4)
        y_centers = (segs[:,1] + segs[:,3]) / 2

        best_i, best_j = None, None
        min_diff = float('inf')
        for i in range(len(segs)):
            for j in range(i+1, len(segs)):
                diff = abs(y_centers[i] - y_centers[j])
                if diff < min_diff:
                    min_diff = diff
                    best_i, best_j = i, j

        if min_diff <= y_tolerance:
            # keep only those two segments
            lines = segs[[best_i, best_j]].reshape(2, 1, 4)
        else:
            lines = None
    else:
        lines = None

    
    #print("best pair length of lines: ",len(lines))
    best_pair = None
    best_dist = 0
    if lines is not None and len(lines) > 1:
        segs = lines.reshape(-1, 4)
        # compute angle and center-x for each segment
        dx = segs[:,2] - segs[:,0]
        dy = segs[:,3] - segs[:,1]
        angles = np.degrees(np.arctan2(dy, dx))
        x_centers = (segs[:,0] + segs[:,2]) / 2

        N = len(segs)
        for i in range(N):
            for j in range(i+1, N):
                if abs(angles[i] - angles[j]) <= pair_angle_tol:
                    dist = abs(x_centers[i] - x_centers[j])
                    if dist >= min_x_separation and dist > best_dist:
                        best_dist = dist
                        best_pair = (i, j)

    # keep only the best pair
    if best_pair:
        i, j = best_pair
        lines = segs[[i, j]].reshape(2, 1, 4)
    else:
        lines = None

    #print("length of lines: ",len(lines))
    # connect the two best segments with a perpendicular (horizontal) yellow line
    if lines is not None and len(lines) == 2:
        segs = lines.reshape(2, 4)
        # compute each segment’s midpoint
        x1_mid = (segs[0,0] + segs[0,2]) // 2
        y1_mid = (segs[0,1] + segs[0,3]) // 2
        x2_mid = (segs[1,0] + segs[1,2]) // 2
        y2_mid = (segs[1,1] + segs[1,3]) // 2

        # perpendicular to vertical ⇒ horizontal line at average y
        y_line  = int((y1_mid + y2_mid) / 2)
        x_start = min(x1_mid, x2_mid)
        x_end   = max(x1_mid, x2_mid)

        # draw a line perpendicular to the segments’ orientation between their midpoints
        segs = lines.reshape(2, 4)
        # compute midpoints
        x1_mid = (segs[0,0] + segs[0,2]) / 2
        y1_mid = (segs[0,1] + segs[0,3]) / 2
        x2_mid = (segs[1,0] + segs[1,2]) / 2
        y2_mid = (segs[1,1] + segs[1,3]) / 2

        # average direction vector of both segments
        dx1, dy1 = segs[0,2] - segs[0,0], segs[0,3] - segs[0,1]
        dx2, dy2 = segs[1,2] - segs[1,0], segs[1,3] - segs[1,1]
        dir_vec = np.array([dx1 + dx2, dy1 + dy2], float)
        dir_vec /= np.linalg.norm(dir_vec)

        # perpendicular unit vector
        perp = np.array([-dir_vec[1], dir_vec[0]])

        # project the midpoint difference onto the perpendicular direction
        delta = np.array([x2_mid - x1_mid, y2_mid - y1_mid], float)
        length = np.dot(delta, perp)

        # compute start/end points
        start = (int(x1_mid), int(y1_mid))
        end   = (int(x1_mid + perp[0] * length), int(y1_mid + perp[1] * length))

        # compute and print the pixel length of the measurement line
        pixel_distance = np.hypot(end[0] - start[0], end[1] - start[1])
        # compute millimeters per pixel
        m_per_pixel = needle_diameter_mm / pixel_distance
        print(f"Needle diameter (pixels): {pixel_distance:.2f} Scale: {m_per_pixel*1000:.24f} m/pixel")
        # draw the yellow diagonal measurement line
        #cv2.line(cropped, start, end, (255, 255, 0), 1)

    else:
        print("Cannot draw diameter: two vertical segments required")

    work = cropped

    return m_per_pixel