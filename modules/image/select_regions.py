#!/usr/bin/env python
#coding=utf-8
from __future__ import print_function
# from classes import ExperimentalDrop
# from subprocess import call
# import numpy as np
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter.messagebox as msgbox
import tkinter.simpledialog as simpledialog
from utils.enums import FittingMethod
from utils.keymap import *
# import time
# import datetime
# from Tkinter import *
# import tkFileDialog

import sys
from scipy import optimize # DS 7/6/21 - for least squares fit
import tensorflow as tf # DS 9/6/21 - for loading ML model

from modules.preprocessing.preprocessing import prepare_hydrophobic, tilt_correction
from utils.config import *
from utils.geometry import Rect2

# import os

MAX_IMAGE_TO_SCREEN_RATIO = 0.8

def set_drop_region(experimental_drop, experimental_setup, index=0):
    # select the drop and needle regions in the image
    screen_size = experimental_setup.screen_resolution
    image_size = experimental_drop.image.shape
    scale = set_scale(image_size, screen_size)
    screen_position = set_screen_position(screen_size)
    if experimental_setup.drop_ID_method == "Automated":
        from modules.preprocessing.preprocessing import auto_crop
        experimental_drop.cropped_image, (left,right,top,bottom) = auto_crop(experimental_drop.image)
        print("experimental_drop.cropped_image",experimental_drop.cropped_image is None)
        if experimental_setup.original_boole == 1: #show found drop
        
            plt.title(f"Original image {index}")
            plt.imshow(experimental_drop.image)
            plt.show()
            plt.close()

        if experimental_setup.cropped_boole == 1:
            plt.title(f"Cropped image {index}")
            plt.imshow(experimental_drop.cropped_image)
            plt.show()
            plt.close()
        experimental_setup.drop_region = [(left, top),(right,bottom)]
    elif experimental_setup.drop_ID_method == "User-selected":
        experimental_setup.drop_region = user_ROI(experimental_drop.image, f"Select drop region for Image {index}", scale, screen_position)
        experimental_drop.cropped_image = image_crop(experimental_drop.image, experimental_setup.drop_region)
 #   experimental_setup.needle_region = user_line(experimental_drop.image, 'Select needle region', scale, screen_position)

def find_image_edge(img, low=50, high=150, apertureSize=3):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,low,high,apertureSize = apertureSize)
    return edges

def set_needle_region(experimental_drop, experimental_setup, center_x=None):
    if experimental_setup.needle_region_method == "Automated":
        img = experimental_drop.image

        # find edges in the image
        edges = find_image_edge(img)
        
        height, width = img.shape[:2]
        cx = center_x if center_x is not None else width // 2

        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
        vertical_lines = []

        # Collect near-vertical lines in upper-middle region
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                deg = np.rad2deg(theta)

                if deg < 5 or deg > 175:  # very vertical
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    x1 = int(x0 + 1000 * (-b))
                    y1 = int(y0 + 1000 * (a))
                    x2 = int(x0 - 1000 * (-b))
                    y2 = int(y0 - 1000 * (a))

                    y_min = min(y1, y2)
                    y_max = max(y1, y2)
                    x_avg = (x1 + x2) // 2

                    # Must be near center and top
                    if abs(x_avg - cx) < width * 0.4 and y_min < height * 0.2:
                        vertical_lines.append({
                            "x": x_avg,
                            "theta": theta,
                            "y_min": y_min,
                            "y_max": y_max,
                            "pts": ((x1, y1), (x2, y2))
                        })

        # If exactly 2 vertical lines were found, just use them
        if len(vertical_lines) == 2:
            l1, l2 = vertical_lines[0], vertical_lines[1]
            best_pair = (l1, l2)
        else:
            # Try to find a good pair
            best_pair = None
            best_score = float("inf")

            for i in range(len(vertical_lines)):
                for j in range(i + 1, len(vertical_lines)):
                    l1 = vertical_lines[i]
                    l2 = vertical_lines[j]

                    # Height similarity
                    height_diff = abs((l1["y_max"] - l1["y_min"]) - (l2["y_max"] - l2["y_min"]))
                    if height_diff > 20:
                        continue

                    # Theta similarity
                    angle_diff = abs(l1["theta"] - l2["theta"])
                    if angle_diff > np.deg2rad(1):  # ~1 degree
                        continue

                    # Prefer taller + closer lines
                    avg_height = (l1["y_max"] - l1["y_min"] + l2["y_max"] - l2["y_min"]) / 2
                    score = angle_diff + height_diff / 10 - avg_height / 50

                    if score < best_score:
                        best_score = score
                        best_pair = (l1, l2)

        if best_pair:
            x1 = min(best_pair[0]["x"], best_pair[1]["x"])
            x2 = max(best_pair[0]["x"], best_pair[1]["x"])
            y_top = min(best_pair[0]["y_min"], best_pair[1]["y_min"])
            y_bot = max(best_pair[0]["y_max"], best_pair[1]["y_max"])

            width = x2 - x1
            height = y_bot - y_top

            x_padding = int(0.2 * width)
            y_padding = int(0.2 * height)

            x1 = max(x1 - x_padding, 0)
            x2 = x2 + x_padding
            y_top = y_top + y_padding  # subtract padding from top = move it down
            y_bot = max(y_bot - y_padding, y_top)  # subtract padding from bottom = move it up

            # Optional: draw
            # cv2.rectangle(img, (x1, y_top), (x2, y_bot), (0, 255, 0), 2)

            experimental_setup.needle_region = Rect2((x1, y_top), (x2, y_bot))
            return
        
        print("error: can't find needle. Please use user-selected method")
    
    elif experimental_setup.needle_region_method == "User-selected":
        # TODO: user-selected method implementation
        return

def crop_needle(img):
    padding=10
    angle_tolerance=15
    original_img = img.copy()
    # adjustable parameters
    vertical_pct = 0.8     # fraction of height to keep from top
    horizontal_pct = 0.5   # fraction of width to keep, centered
    # initial crop of the image
    h, w = img.shape[:2]
    top = int(h * vertical_pct)
    side_margin = int((w * (1 - horizontal_pct)) / 2)
    img = img[:top, side_margin : w - side_margin]

    # a veriable used to eliminate the vertical lines that exist in the bottom half of the image
    bottom_verticals_threshold=0.7
    # 1. Preprocess: grayscale & edges
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #if img.ndim == 3 else img.copy()
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 180, apertureSize=3)

    # 2. Detect line segments via probabilistic Hough
    lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=45,
                             minLineLength=1, maxLineGap=50)
    if lines is None or len(lines) < 2:
        print("Insufficient line segments detected.")
        return original_img

    # 3. Optimized vertical filter
    dx = lines[:,0,2] - lines[:,0,0]
    dy = lines[:,0,3] - lines[:,0,1]
    raw_angles = np.degrees(np.arctan2(dy, dx))  # -180..+180
    orient = (raw_angles + 90) % 180             # 0 = vertical up, 180 = vertical down
    mask = (orient <= angle_tolerance) | (orient >= 180 - angle_tolerance)
    vertical = lines[mask]
    if vertical.shape[0] < 2:
        print("Could not find two vertical lines within tolerance.")
        return original_img
    
    
    # Create a mask for lines where both y-coordinates are in the top half
    # A line (x1,y1,x2,y2) is in the top half if both y1 and y2 are less than y_midpoint
    
    y_midpoint = abs(h * bottom_verticals_threshold)
    top_half_mask = (vertical[:,0,1] < y_midpoint) & (vertical[:,0,3] < y_midpoint)
    vertical = vertical[top_half_mask]

    if vertical.shape[0] < 2:
        print("Could not find two vertical lines in the top half of the image within tolerance.")
        return original_img
    # Extract endpoints
    vertical = vertical[:,0]  # shape (N,4)


    #min_dist = int(w * min_dist_pct)

    # 4. Select two longest vertical lines
    def length_sq(l): return (l[2] - l[0])**2 + (l[3] - l[1])**2
    sorted_lines = sorted(vertical, key=length_sq, reverse=True)
    min_dist = 10  # your minimum x-distance in pixels

    # find the longest pair whose centers are >= min_dist apart
    for i, l1 in enumerate(sorted_lines):
        x1 = (l1[0] + l1[2]) // 2
        for l2 in sorted_lines[i+1:]:
            x2 = (l2[0] + l2[2]) // 2
            if abs(x2 - x1) >= min_dist:
                # we found a valid pair
                break
        else:
            # no valid partner for l1, continue with next
            continue
        # break out of outer loop as well
        break
    else:
        print(f"Could not find two vertical lines ≥ {min_dist}px apart.")
        return original_img
    # 5. Compute bounding coords
    x1 = (l1[0] + l1[2]) // 2
    x2 = (l2[0] + l2[2]) // 2
    left_x, right_x = int(min(x1, x2)), int(max(x1, x2))
    ys = [l1[1], l1[3], l2[1], l2[3]]
    top_y, bottom_y = int(min(ys)), int(max(ys))

    # 6. Pad and clamp
    h, w = gray.shape[:2]
    left = max(0, left_x - padding)
    right = min(w, right_x + padding)
    top = max(0, top_y - padding)
    bottom = min(h, bottom_y + padding)

    # 8. Crop and return
    img = img[top:bottom, left:right]

    
    return img

def image_crop(image, points):
    # return image[min(y):max(y), min(x),max(x)]
    return image[int(points[0][1]):int(points[1][1]), int(points[0][0]):int(points[1][0])]

def set_surface_line(experimental_drop, experimental_setup):
    # message = []

    # 
    # if experimental_drop.cropped_image is None:
    #     if experimental_setup.drop_ID_method == "User-selected":
    #         msgbox.showwarning("Warning", "Please select the drop region")
    #         set_drop_region(experimental_drop, experimental_setup)
    #         return  
    #     # autuomatic
    #     else: 
    #         set_drop_region(experimental_drop, experimental_setup)

    # if experimental_setup.threshold_method == "User-selected":
    #     if experimental_setup.threshold_val is None:
    #         threshold = simpledialog.askinteger("Input Required", "Enter the threshold value:")
    #         if threshold is None:  # User pressed "Cancel"
    #             msgbox.showwarning("Warning", "Threshold is required to continue.")
    #             return  
    #         experimental_setup.threshold_val = threshold
    
    
    # extract_drop_profile(experimental_drop, experimental_setup)
    
    if experimental_setup.baseline_method == "Automated":
        experimental_drop.drop_contour, experimental_drop.contact_points = prepare_hydrophobic(experimental_drop.contour)
    elif experimental_setup.baseline_method == "User-selected":
        user_line(experimental_drop, experimental_setup)


def correct_tilt(experimental_drop, experimental_setup):
    if experimental_setup.baseline_method == "Automated":
        experimental_drop.cropped_image = tilt_correction(experimental_drop.cropped_image, experimental_drop.contact_points)

    #gets tricky where the baseline is manually set because under the current workflow users would
    # be required to re-input their baseline until it's flat - when the baseline should be flat
    # and known once it's set and corrected for
    elif experimental_setup.baseline_method == "User-selected":
        rotated_img_crop = tilt_correction(img, experimental_drop.contact_points, user_set_baseline=True)

def set_scale(image_size, screen_size):
    x_ratio = image_size[1]/float(screen_size[0])
    y_ratio = image_size[0]/float(screen_size[1])
    max_ratio = max(x_ratio, y_ratio)
    scale = 1
    if max_ratio > MAX_IMAGE_TO_SCREEN_RATIO:
        scale = MAX_IMAGE_TO_SCREEN_RATIO / max_ratio
    return scale

def set_screen_position(screen_size):
    prec_free_space = 0.5 * (1 - MAX_IMAGE_TO_SCREEN_RATIO) # percentage room free
    x_position = int(prec_free_space * screen_size[0])
    y_position = int(0.5 * prec_free_space * screen_size[1]) # 0.5 moves window a little bit higher
    return [x_position, y_position]

def user_ROI(raw_image, title,  scale, screen_position): #, line_colour=(0, 0, 255), line_thickness=2):
    global drawing
    global ix, iy
    global fx, fy
    global image_TEMP
    global img
    # raw_image = raw_image2
    # raw_image = np.flipud(cv2.cvtColor(raw_image2,cv2.COLOR_GRAY2BGR))
    # raw_image = np.flipud(raw_image2)
    drawing = False # true if mouse is pressed
    ix,iy = -1,-1
    fx,fy = -1,-1

    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(title, screen_position[0], screen_position[1])
    cv2.setMouseCallback(title, draw_rectangle)
    #scale =1
    image_TEMP = cv2.resize(raw_image, (0,0), fx=scale, fy=scale)

    img = image_TEMP.copy()

    while(1):
        cv2.imshow(title,img)

        k = cv2.waitKey(1) & 0xFF
        if k != 255:
            if (k == 13) or (k == 32):
                # either 'return' or 'space' pressed
                # break
                if ((fx - ix) * (fy - iy)) != 0: # ensure there is an enclosed region
                    break
            if (k == 27):
                # 'esc'
                kill()

    cv2.destroyAllWindows()
    min_x = min(ix, fx) / scale
    max_x = max(ix, fx) / scale
    min_y = min(iy, fy) / scale
    max_y = max(iy, fy) / scale
    return [(min_x, min_y), (max_x, max_y)]

def user_line(experimental_drop, experimental_setup):
    #scale = set_scale(experimental_drop.image.shape, experimental_setup.screen_resolution)
    screen_position = set_screen_position(experimental_setup.screen_resolution)
    raw_image = experimental_drop.cropped_image
    drop_data = experimental_drop.contour.astype(float)
    CPs = experimental_drop.contact_points
    title = 'Define surface line'

    #line = experimental_drop.surface_data # not set yet
    region = experimental_setup.drop_region

    global drawing
    global ix, iy
    global fx, fy
    global image_TEMP
    global img

    DRAW_TANGENT_LINE_WHILE_SETTING_BASELINE = True
    TEMP = False
    baseline_def_method = 'use user-inputted points'

    # raw_image = raw_image2
    # raw_image = np.flipud(cv2.cvtColor(raw_image2,cv2.COLOR_GRAY2BGR))
    # raw_image = np.flipud(raw_image2)
    drawing = True # true if mouse is pressed
    ix,iy = -1,-1
    fx,fy = -1,-1

    region = np.floor(region)
    # print(region)

    # print(region[0,0])
    # print(region[1,0])
    # print(region[0,1])
    # print(region[1,1])

    #    cv2.setMouseCallback(title, draw_line)

    scale = 1
    if TEMP:
        image_TEMP = cv2.resize(raw_image[int(region[0,1]):int(region[1,1]),int(region[0,0]):int(region[1,0])], (0,0), fx=scale, fy=scale)
    else:
        image_TEMP = raw_image.copy()
    img = image_TEMP.copy()

    # set surface line starting estimate
    N = np.shape(drop_data)[0]
    A = 1 #50 # maybe lower this?
    xx = np.concatenate((drop_data[0:A,0],drop_data[N-A:N+1,0]))
    yy = np.concatenate((drop_data[0:A,1],drop_data[N-A:N+1,1]))
    coefficients = np.polyfit(xx, yy, 1)
    line = np.poly1d(coefficients)

    xx = np.array([0,img.shape[1]])
    yy = line(xx) #gives a starting guess for the line position

    ix0,fx0 = xx.astype(int)
    iy0,fy0 = yy.astype(int)

    ix,fx = ix0,fx0
    iy,fy = iy0,fy0

    # cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    # cv2.moveWindow(title, screen_position[0], screen_position[1])
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 800, 600)  # or image.shape[1], image.shape[0]
    try:
        cv2.setWindowProperty(title, 5, 0)  # Lock size (if supported)
    except:
        pass  # Safe fallback for macOS or older OpenCV
    cv2.moveWindow(title, screen_position[0], screen_position[1])

    if DRAW_TANGENT_LINE_WHILE_SETTING_BASELINE: #so that things can be drawn over the image which surface line is changed
        conans = {}
        if 0:
            for i,n in enumerate(drop_data):
                if n[0]==CPs[0][0] and int(n[1])==int(CPs[0][1]):
                    start_index = i
                if int(n[0])==int(CPs[1][0]) and int(n[1])==int(CPs[1][1]):
                    end_index = i
            auto_drop = drop_data.copy()[start_index:end_index]
        else:
            auto_drop = drop_data

    # Add guidance for the user
    print("\nKeyboard Controls:")
    print("W = Move Up")
    print("S = Move Down")
    print("A = Rotate Left")
    print("D = Rotate Right")
    print("O = Reset to Original Position")
    print("P = Print Debug Info")
    print("ENTER/SPACE = Confirm Selection")
    print("ESC = Exit\n")

    while(1):
        cv2.imshow(title,img)
        #cv2.circle(img,(200,200),5,(255,255,0),2)
        cv2.line(img,(ix,iy),(fx,fy), (0, 255, 0), 2)# #line_colour,line_thickness)
        #Plot pixels above line
        #cv2.waitKey(0)
        v1 = (ix-fx,iy-fy) #(1,coefficients[1])   # Vector 1

        #print(np.shape(drop_data))
        #print(drop_data)

        #Plot pixels above line
        v1 = (ix-fx,iy-fy) 

        if 1:
            drop = []
            for i in drop_data:
                cx,cy = i
                v2 = (cx-ix, cy-iy)   # Vector 1
                xp = v1[0]*v2[1] - v1[1]*v2[0]  # Cross product
                if xp > 0:
                    drop.append([cx,cy])
                    cv2.circle(img,(int(cx),int(cy)),2,(255,255,255),1)
        else:
            drop = []
            for i in drop_data:
                cx,cy = i
                #if contour point y value less than line y value
                if cy < line(cx):
                    drop.append([cx,cy])
                    cv2.circle(img,(int(cx),int(cy)),2,(255,255,255),1)


        drop = np.asarray(drop).astype(float) #drop is the contour above the user-inputted line

        if 0:
            plt.imshow(img)
            plt.title('check contour after being cut by baseline')
            plt.plot(drop[:,0],drop[:,1])
            plt.show()
            plt.close()

        experimental_drop.drop_contour = drop
        CPs = {0: drop[0], 1:drop[-1]}
        experimental_drop.contact_points = CPs

        if DRAW_TANGENT_LINE_WHILE_SETTING_BASELINE:
            methods_boole = experimental_setup.analysis_methods_ca
            if methods_boole[FittingMethod.TANGENT_FIT] or methods_boole[FittingMethod.POLYNOMIAL_FIT] or methods_boole[FittingMethod.CIRCLE_FIT] or methods_boole[FittingMethod.ELLIPSE_FIT]:
                from modules.fitting.fits import perform_fits
                perform_fits(experimental_drop, tangent=methods_boole[FittingMethod.TANGENT_FIT], polynomial=methods_boole[FittingMethod.POLYNOMIAL_FIT], circle=methods_boole[FittingMethod.CIRCLE_FIT],ellipse=methods_boole[FittingMethod.ELLIPSE_FIT])
            if methods_boole[FittingMethod.TANGENT_FIT]:
                tangent_lines = tuple(experimental_drop.contact_angles['tangent fit']['tangent lines'])
                cv2.line(img, (int(tangent_lines[0][0][0]),int(tangent_lines[0][0][1])),(int(tangent_lines[0][1][0]),int(tangent_lines[0][1][1])), (0, 0, 255), 2)
                cv2.line(img, (int(tangent_lines[1][0][0]),int(tangent_lines[1][0][1])),(int(tangent_lines[1][1][0]),int(tangent_lines[1][1][1])),(0, 0, 255), 2)
            if methods_boole[FittingMethod.POLYNOMIAL_FIT] == True and not methods_boole[FittingMethod.TANGENT_FIT]:
                tangent_lines = tuple(experimental_drop.contact_angles['polynomial fit']['tangent lines'])
                cv2.line(img, tangent_lines[0][0],tangent_lines[0][1], (0, 0, 255), 2)
                cv2.line(img, tangent_lines[1][0],tangent_lines[1][1], (0, 0, 255), 2)
            if methods_boole[FittingMethod.CIRCLE_FIT]:
                xc,yc = experimental_drop.contact_angles['circle fit']['circle center']
                r = experimental_drop.contact_angles['circle fit']['circle radius']
                cv2.circle(img,(int(xc),int(yc)),int(r),(255,150,0),1)
            if methods_boole[FittingMethod.ELLIPSE_FIT]:
                center = experimental_drop.contact_angles['ellipse fit']['ellipse center']
                axes = experimental_drop.contact_angles['ellipse fit']['ellipse a and b']
                phi = experimental_drop.contact_angles['ellipse fit']['ellipse rotation']
                cv2.ellipse(img, (int(center[0]),int(center[1])), (int(axes[0]),int(axes[1])), phi, 0, 360, (0, 88, 255), 1)

        # Get key press with a simpler approach
        k = cv2.waitKey(1) & 0xFF

        # Process key presses using WASD controls instead of arrow keys
        if k == 13 or k == 32:  # ENTER / SPACE
            if ((fx - ix) * (fy - iy)) != 0:  # Ensure enclosed region
                break
            else:
                print('something is not right...')
                print(fx, ix, fy, iy, (fx - ix) * (fy - iy))
                break

        elif k == 27:  # ESC
            kill()

        elif k == ord('s'):  # 's' for DOWN
            print("DOWN key pressed (s)")
            fy += 1
            iy += 1

        elif k == ord('w'):  # 'w' for UP
            print("UP key pressed (w)")
            fy -= 1
            iy -= 1

        elif k == ord('o') or k == ord('O'):  # 'o' key
            print("O key pressed")
            fx, fy = fx0, fy0
            ix, iy = ix0, iy0

        elif k == ord('a'):  # 'a' for LEFT rotation
            print("LEFT key pressed (a)")
            x0 = np.array([ix, iy])
            x1 = np.array([fx, fy])
            xc = 0.5 * (x0 + x1)
            theta = 0.1 / 180 * np.pi
            theta = -theta  # counter-clockwise
            
            rotation = np.array([
                [np.cos(theta), -np.sin(theta)],
                [np.sin(theta),  np.cos(theta)]
            ])
            x0r = rotation @ (x0 - xc).T + xc
            x1r = rotation @ (x1 - xc).T + xc
            
            ix, iy = x0r.astype(int)
            fx, fy = x1r.astype(int)

        elif k == ord('d'):  # 'd' for RIGHT rotation
            print("RIGHT key pressed (d)")
            x0 = np.array([ix, iy])
            x1 = np.array([fx, fy])
            xc = 0.5 * (x0 + x1)
            theta = 0.1 / 180 * np.pi
            # No negation for clockwise rotation
            
            rotation = np.array([
                [np.cos(theta), -np.sin(theta)],
                [np.sin(theta),  np.cos(theta)]
            ])
            x0r = rotation @ (x0 - xc).T + xc
            x1r = rotation @ (x1 - xc).T + xc
            
            ix, iy = x0r.astype(int)
            fx, fy = x1r.astype(int)

        elif k == ord('p') or k == ord('P'):  # 'p' key
            for key in conans.keys():
                print(key, ':', conans[key])
            print()

        # Redraw the image after any update
        if TEMP:
            image_TEMP = cv2.resize(
                raw_image[int(region[0, 1]):int(region[1, 1]), int(region[0, 0]):int(region[1, 0])],
                (0, 0), fx=scale, fy=scale)
        else:
            image_TEMP = raw_image.copy()

        img = image_TEMP.copy()
        # cv2.line(img, (ix, iy), (fx, fy), (0, 255, 0), 2)
        cv2.putText(img, "Use W/A/S/D to move. Enter/Space = confirm. ESC = cancel.",
                    (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.25, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.line(img, (ix, iy), (fx, fy), (0, 255, 0), 2)


    cv2.destroyAllWindows()
    min_x = min(ix, fx) / scale
    max_x = max(ix, fx) / scale
    min_y = min(iy, fy) / scale
    max_y = max(iy, fy) / scale


def run_set_surface_line(experimental_drop, experimental_setup,result_queue):
    
    set_surface_line(experimental_drop, experimental_setup)
    result_queue.put(experimental_drop.contact_angles)

# mouse callback function
def draw_rectangle(event,x,y,flags,param):
    global ix,iy,drawing
    global fx, fy
    global image_TEMP
    global img

    if event == cv2.EVENT_LBUTTONDOWN:
        img = image_TEMP.copy()
        drawing = True
        ix,iy = x,y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            img = image_TEMP.copy()
            cv2.rectangle(img,(ix,iy),(x,y), (0, 0, 255), 2)# line_colour,line_thickness)

    elif event == cv2.EVENT_LBUTTONUP:
        img = image_TEMP.copy()
        drawing = False
        fx, fy = x, y
        cv2.rectangle(img,(ix,iy),(fx, fy), (0, 255, 0), 2)# #line_colour,line_thickness)

# mouse callback function
def draw_line(event,x,y,flags,param):
    global ix,iy,drawing
    global fx, fy
    global image_TEMP
    global img

    if event == cv2.EVENT_LBUTTONDOWN:
        img = image_TEMP.copy()
        drawing = True
        ix,iy = x,y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            img = image_TEMP.copy()
            cv2.line(img,(ix,iy),(x,y), (0, 0, 255), 2)# line_colour,line_thickness)

    elif event == cv2.EVENT_LBUTTONUP:
        img = image_TEMP.copy()
        drawing = False
        fx, fy = x, y
        cv2.line(img,(ix,iy),(fx, fy), (0, 255, 0), 2)# #line_colour,line_thickness)

def kill():
    sys.exit()

def distance(P1, P2):
    """This function computes the distance between 2 points defined by
    P1 = (x1,y1) and P2 = (x2,y2) """
    return ((P1[0] - P2[0])**2 + (P1[1] - P2[1])**2) ** 0.5

def optimized_path(coords, start=None):
    """This function finds the nearest point to a point
    coords should be a list in this format coords = [ [x1, y1], [x2, y2] , ...]
    https://stackoverflow.com/questions/45829155/sort-points-in-order-to-have-a-continuous-curve-using-python"""
    if isinstance(coords,list) == False:
        coords = coords.tolist()
    if 0 :
        if isinstance(start,list) == False:
            try:
                start = start.tolist()
            except:
                start = list(start)
    if start is None:
        start = coords[0]
    pass_by = coords
    path = [start]
    pass_by.remove(start)
    while pass_by:
        nearest = min(pass_by, key=lambda x: distance(path[-1], x))
        path.append(nearest)
        pass_by.remove(nearest)
    path = np.array(path)
    return path



def intersection(center, radius, p1, p2):

    """ find the two points where a secant intersects a circle """

    dx, dy = p2[0] - p1[0], p2[1] - p1[1]

    a = dx**2 + dy**2
    b = 2 * (dx * (p1[0] - center[0]) + dy * (p1[1] - center[1]))
    c = (p1[0] - center[0])**2 + (p1[1] - center[1])**2 - radius**2

    discriminant = b**2 - 4 * a * c
    assert (discriminant > 0), 'Not a secant!'

    t1 = (-b + discriminant**0.5) / (2 * a)
    t2 = (-b - discriminant**0.5) / (2 * a)

    return (dx * t1 + p1[0], dy * t1 + p1[1]), (dx * t2 + p1[0], dy * t2 + p1[1])

def ML_prepare_hydrophobic(coords_in):
    coords = coords_in
    coords[:,1] = - coords[:,1] # flip
    #print('length of coords: ',len(coords))

    # isolate the top of the contour so excess surface can be deleted
    percent = 0.1
    bottom = []
    top = [] # will need this later
    div_line_value = min(coords[:,[1]]) + (max(coords[:,[1]]) - min(coords[:,[1]]))*percent
    for n in coords:
        if n[1] < div_line_value:
            bottom.append(n)
        else:
            top.append(n)

    bottom = np.array(bottom)
    top = np.array(top)

    del_indexes = []
    for index,coord in enumerate(coords):
        if coord[0]>max(top[:,0]) or coord[0]<min(top[:,0]):
            del_indexes.append(index)
    #halfdrop = np.delete(halfdrop,del_indexes)
    coords = np.delete(coords,del_indexes,axis=0)

    if 0:
        plt.title('isolated coords, length: '+str(len(coords)))
        plt.plot(coords[:,0],coords[:,1])
        plt.show()
        plt.close()



    # find the apex of the drop and split the contour into left and right sides

    xtop,ytop = top[:,0],top[:,1] # isolate top 90% of drop

    xapex = (max(xtop) + min(xtop))/2
    #yapex = max(ytop)
    #coords[:,1] = -coords[:,1]

    l_drop = []
    r_drop = []
    for n in coords:
        if n[0] < xapex:
            l_drop.append(n)
        if n[0] > xapex:
            r_drop.append(n)
    l_drop = np.array(l_drop)
    r_drop = np.array(r_drop)

    #print('length of left drop is: ',len(l_drop))
    #print('length of right drop is: ', len(r_drop))

    # transpose both half drops so that they both face right and the apex of both is at 0,0
    #r_drop[:,[0]] = r_drop[:,[0]] - min(r_drop[:,[0]])
    #l_drop[:,[0]] = -l_drop[:,[0]] + max(l_drop[:,[0]])
    r_drop[:,[0]] = r_drop[:,[0]] - xapex
    l_drop[:,[0]] = -l_drop[:,[0]] + xapex

    counter = 0
    CV_contours = {}

    for halfdrop in [l_drop,r_drop]:
        if halfdrop[0,1]<halfdrop[-1,1]:
            halfdrop = halfdrop[::-1]

        X = halfdrop[:,0]
        Z = halfdrop[:,1]

        lowest = min(Z)
        Z = Z+abs(lowest)

        X = X/max(Z)
        Z = Z/max(Z)

        # zero padd contours to
        coordinates = []
        input_len = 1100
        len_cont = len(X)

        #if len(X) > global_max_len:
        #    global_max_len = len(X)

        if len(X)>input_len:
            print(len(X))
            raise Exception("Contour of length "+str(len(X))+" is too long for the designated output dimensionality of ("+str(input_len)+",2)")

        for i in range(input_len):
            if i < len(X):
                a = X[i]
                b = Z[i]
                coord = [a,b]
                coordinates.append(coord)
            else:
                coordinates.append([0,0])
        if 0:
            jet= plt.get_cmap('jet')
            colors = iter(jet(np.linspace(0,1,len(coordinates))))
            for k in coordinates:
                plt.plot(k[0],k[1], 'o',color=next(colors))
            plt.title('Halfdrop')
            plt.show()
            plt.close()
        #key = image.split('/')[-1].split('_')[-1][:-4]
        key = counter
        CV_contours[key]= np.array(coordinates)

        counter += 1

    pred_ds = np.zeros((2,input_len,2))
    for counter in [0,1]:
        pred_ds[counter] = CV_contours[counter]

    return pred_ds