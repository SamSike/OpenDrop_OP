""" give inputs to python script from command line """

import argparse
import sys

import os
import numpy as np
import matplotlib
import cv2
import matplotlib.pyplot as plt

import time
#import psutil
from scipy.integrate import odeint
import io #for saving to memory
import pickle

def yl_eqs(y, x, Bo):
    # Here U is a vector such that y=U[0] and z=U[1]. This function should return [y', z']
    return [2 + Bo * y[2] - np.sin(y[0]) / (y[1] + 1e-14), np.cos(y[0]), np.sin(y[0])]

def draw_drop(angle,
             Bo,
             scaler,
             roughness,
             N_pts_drop,
             dpi=256,
             save_dir=None,
             debug=False):
    """Creates an image for a set of parameters.

    min_angle is the lower bound of the possible contact angles
    max_angle is the upper bound of the possible contact angles
    N_angles is the number of images of difference contact angles created, the contact angles of these drops will
        be evenly spaced between the lower and upper bounds, inclusive of bound values
    min_Bo, max_Bo, and N_Bo alter the Bond number parameter of the dataset
    min_scaling, max_scaling, N_scaled_drops alter the scaling of the drop within the image, acting as a proxy
        resolution parameter
    min_roughness, max_roughness, and N_roughness alter the roughness of the baseline. 0 roughness is a perfectly
        smooth baseline, while 1e-2 is the recomended maximum value.
    N_pts_drop is the number of points used when drawing the shape of the halfdrop contour after solving the Young-
        Lacplace equation. A number significantly larger than the resolution of the image is recommended, so that the
        limiting value is the saved images resolution rather than the resolution of the solution to the Young-Laplace
        equation.
    debug (True or Flase). Set to true to visualise outputs while debugging.
    """

    s0 = [0, 0, 0]
    # the second term in s converts the angle to radians
    s = np.linspace(0, np.pi * angle / 180, N_pts_drop)
    # s = np.linspace(0, (np.pi*angle/180), N_pts_drop)
    # odeint solves ds0/ds = yl_eqs(s0,s)
    # soln is an array of triplet arrays
    soln = odeint(yl_eqs, s0, s, args=(Bo,))

    # phi is all the 0th terms of soln in degrees
    phi = 180 * soln[:, 0] / np.pi

    for i in range(1, len(phi)):
        if phi[i] < phi[i - 1]:
            phi[i] = phi[i] + 180.

    # X values of the contour are the 1th values of soln, X values exist between 0 and 1
    # Z values of the contour are the 2th values of soln
    X = soln[:, 1]
    Z = soln[:, 2]

    # Chops of the values on the contour which over-reach the set contact angle
    X = X[phi <= angle]
    Z = Z[phi <= angle]

    # flips Z coords so that the apex of drop is the max Z value
    Z = -Z + max(Z)

    X = X / max(Z)
    Z = Z / max(Z)  # normalize so that apex is at z=1

    if debug:  # plot contour
        plt.plot(X, Z, '-')
        plt.title('Theoretical halfdrop contour')
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
        plt.close()
        print('X: \n',X)



    shape_scale = 1.5  # alter the x-axis size so that the baseline fits in the image
    if 2*max(X) > 1.5 * max(Z):
        #if true, drop will be too wide for frame before it is too tall
        img_width = 2 * max(X) * 4/3 * scaler
        img_height = img_width / shape_scale
        shift = (32 / 1024) * img_height  # baseline is a bit above bottom of frame
        xlim = [(-img_width / 2), (img_width / 2)]
        ylim = [-shift, img_height - shift]
    else:
        # drop must fit into the frame vertically
        img_height = max(Z) * 4/3 * scaler  # top of drop with some room and multiply scaler
        max_img_width = img_height * shape_scale  # from scaling difference in HD images
        shift = (32 / 1024) * img_height  # baseline is a bit above bottom of frame
        ylim = [-shift, img_height - shift]
        xlim = [(-max_img_width / 2), (max_img_width / 2)]
        #xlim = [(-max_img_width / 2), (max_img_width / 2)]
        img_width = xlim[1] - xlim[0]

    if debug:  # check that scaling is correct, should be 1:1.5

        img_height = ylim[1] - ylim[0]
        print('ratio of y to x is ', img_height / img_height, ' : ', img_width / img_height)  # correct
        # print('Angle is '+str(angle)+'\nBond number is:'+str(Bo)+'\nScaler is '+str(scaler))

    if roughness >= 0:# draw surface - named here as baseline
        baselinex = np.linspace(xlim[0], xlim[1], 100)
        # have baseline extend one extra point in both directions in case randomisation moves x coord of baseline inwards
        gap = baselinex[1]-baselinex[0]
        #extra_point_left = baselinex[0]-(gap*2)
        #extra_point_right = baselinex[-1]+(gap*2)
        #baselinex = np.array([extra_point_left] + list(baselinex) + [extra_point_right])
        baselinez = []
        #for n in range(102):
        for n in range(100):
            baselinez.append(shift)
        Z = Z + shift

        coords_right = np.array(list(zip(X,Z)))
        coords_left = np.array(list(zip(-X,Z)))
        coords = np.concatenate((coords_left[::-1],coords_right), axis=0)
        CPs = [[-X[-1], Z[-1]],[X[-1], Z[-1]]]

        # to smooth roughness near CP, determine baselinex points near CPs
        left_dists = [CPs[0][0] - x for x in baselinex]
        left_dist, left_nearest_i = min([(value, idx) for idx, value in enumerate(left_dists) if value > 0], key=lambda x:x[0])
        right_dists = [CPs[1][0] - x for x in baselinex]
        right_dist, right_nearest_i = max([(value, idx) for idx, value in enumerate(right_dists) if value < 0], key=lambda x:x[0])

        # roughen surface with randomisation
        for i in range(len(baselinex)):
            dpX = float(np.random.uniform(-roughness * img_height, roughness * img_height))
            dpZ = float(np.random.uniform(-roughness * img_height, 0)) # so that the contact point is never obscured
            pX = baselinex[i]
            pZ = baselinez[i]
            if i in [0,len(baselinex)-1]: #for surface line at image edges
                baselinex[i] = pX # no roughness added horizontally to keep the image dimensions the same
                baselinez[i] = pZ + dpZ
            elif i in [left_nearest_i, right_nearest_i]:
                baselinex[i] = pX # no roughness added horizontally to keep the image dimensions the same
                baselinez[i] = pZ + (dpZ/2)
            elif xlim[0] < (pX + dpX) < coords[0,0]: # if new surface b/w img edge and drop on left
                baselinex[i] = pX + dpX
                baselinez[i] = pZ + dpZ
            elif coords[-1,0] < (pX + dpX) < xlim[1]: # if new surface b/w drop on right and img edge
                baselinex[i] = pX + dpX
                baselinez[i] = pZ + dpZ

    else: #if roughness is negative - surface is reflective
        ref_ratio = -roughness
        # ref_ratio should be a ratio of image height (not drop height)
        div_line = min(Z) + img_height*ref_ratio
        coords = np.column_stack((X,Z))
        reflection = coords[coords[:,1] < div_line][::-1]
        reflection[:,1] = -reflection[:, 1]
        reflection_height = abs(max(reflection[:,1])) - abs(min(reflection[:,1]))
        reflection[:,1] = reflection[:,1] + (shift - min(reflection[:,1])) # raise into frame
        if debug:
            jet= plt.get_cmap('jet')
            colors = iter(jet(np.linspace(0,1,len(reflection))))
            for k in reflection:
                plt.plot(k[0],k[1], 'o',color=next(colors))
            plt.axis('equal')
            plt.title('Reflection in order')
            plt.show()
            plt.close()

        Z = Z + shift + (max(reflection[:,1]) - min(reflection[:,1])) # raise rest of drop to accomodate reflection
        CPs = [[-X[-1], Z[-1]],[X[-1], Z[-1]]]
        # add reflection line to X and Z
        X = np.append(X,reflection[:,0])
        Z = np.append(Z,reflection[:,1])
        #draw rest of surface line
        baselinex = np.linspace(xlim[0], xlim[1], 100)
        # have baseline extend one extra point in both directions in case randomisation moves x coord of baseline inwards
        gap = baselinex[1]-baselinex[0]
        extra_point_left = baselinex[0]-(gap*2)
        extra_point_right = baselinex[-1]+(gap*2)
        baselinex = np.array([extra_point_left] + list(baselinex) + [extra_point_right])
        baselinez = []
        for n in range(102):
            baselinez.append(shift)

    if debug: # show outline
        plt.title('Outline')
        plt.plot(X,Z)
        plt.axis('equal')
        plt.show()
        plt.close()

    # save image to working memory
    plt.figure(figsize=(15, 10))
    plt.ioff()
    plt.fill_between(baselinex, baselinez, min(ylim)-1, facecolor='black', linewidth=0)
    plt.fill_betweenx(Z, -X, X, facecolor='black')
    plt.fill_between([-X[-1],X[-1]], [Z[-1],Z[-1]], min(ylim)-1, facecolor='black', linewidth=0)
    plt.plot([0,0],[shift, min(ylim)-1], color='black', linewidth=1)
    #plt.axis('equal')
    plt.xlim(xlim) # set lims to define aspect ratio of 1.5 wide
    plt.ylim(ylim)
    plt.axis('off')
    plt.gca().margins(0)
    #plt.tight_layout()
    #CPs = [[-X[-1], Z[-1]],[X[-1], Z[-1]]]

    if debug: #check - note that saving to mem won't work if this is switched on
        plt.axis('on')
        plt.title('check figure before conversion to image\nCPs:'+str(CPs)+'\nAspect ratio: '+str(img_width / img_height))
        #plt.plot(CPs[0][0],CPs[0][1], 'ro')
        #plt.plot(CPs[1][0],CPs[1][1], 'bo')
        #plt.plot(baselinex[left_nearest_i], baselinez[left_nearest_i],'yo')
        #plt.plot(baselinex[right_nearest_i], baselinez[right_nearest_i],'go')
        plt.show()
        plt.close()

        #repeat after showing the above deregisters plot
        plt.fill_between(baselinex, baselinez, min(ylim)-1, facecolor='black', linewidth=0)
        plt.fill_betweenx(Z, -X, X, facecolor='black')
        plt.fill_between([-X[-1],X[-1]], [Z[-1],Z[-1]], min(ylim)-1, facecolor='black', linewidth=0)
        plt.plot([0,0],[shift, min(ylim)-1], color='black', linewidth=1)
        #plt.axis('equal')
        plt.xlim(xlim) # set lims to define aspect ratio of 1.5 wide
        plt.ylim(ylim)
        plt.axis('off')
        plt.gca().margins(0)
    # 0 x value is in the middle
    #plt.tight_layout()

    buf = io.BytesIO()
    #plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',pad_inches=0)# 256
    plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',pad_inches=0)# ratio is close enough but drawn shape is padded in white on the left and right sides
    #plt.savefig('synthetic_drop.png', format='png', dpi=dpi, bbox_inches='tight')
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(img_arr, 1)
    plt.close()
    buf.close()

    # determine image CP coordinates using position relative to frame
    img_width = max(xlim) - min(xlim)
    img_height = max(ylim) - min(ylim)
    #left_CP_w_ratio = (-max(X) - min(baselinex))/(max(baselinex) - min(baselinex))# dist from left edge to CP over dist from left edge to right edge
    #left_CP_w_ratio = (CPs[0][0] - min(baselinex))/(max(baselinex) - min(baselinex))# dist from left edge to CP over dist from left edge to right edge
    left_CP_w_ratio = (CPs[0][0] - min(xlim))/(img_width)# dist from left edge to CP over dist from left edge to right edge
    #right_CP_w_ratio = (max(X) - min(baselinex))/(max(baselinex) - min(baselinex))# dist from left edge to CP over dist from left edge to right edge
    #right_CP_w_ratio = (CPs[1][0] - min(baselinex))/(max(baselinex) - min(baselinex))# dist from left edge to CP over dist from left edge to right edge
    right_CP_w_ratio = (CPs[1][0] - min(xlim))/(img_width)# dist from left edge to CP over dist from left edge to right edge
    #left_CP_h_ratio = min(Z)/((max(baselinex) - min(baselinex)))
    left_CP_h_ratio = (CPs[0][1] - min(ylim))/(img_height)
    right_CP_h_ratio = (CPs[1][1] - min(ylim))/(img_height)

    #CPs_img = [[img.shape[1]*left_CP_w_ratio, img.shape[0]-(img.shape[0]*CP_h_ratio)],[img.shape[1]*right_CP_w_ratio, img.shape[0]-(img.shape[0]*CP_h_ratio)]]
    left_x = round(img.shape[1]*left_CP_w_ratio)
    #left_z = min([i for i,val in enumerate(img[:,left_x]) if val.all() == np.array([0,0,0]).all()])
    left_z = round(img.shape[0] - (img.shape[0]*left_CP_h_ratio))
    right_x = round(img.shape[1]*right_CP_w_ratio)
    #right_z = min([i for i,val in enumerate(img[:,right_x]) if val.all() == np.array([0,0,0]).all()])
    right_z = round(img.shape[0] - (img.shape[0]*right_CP_h_ratio))
    CPs_img = [[left_x, left_z], [right_x, right_z]]

    if debug:
        plt.figure(figsize=(15,10))
        plt.title('Drawn drop \nContact points at: '+str(CPs_img)+'\nImage aspect ratio: '+str(img.shape[1]/img.shape[0]))
        plt.imshow(img)
        plt.plot(CPs_img[0][0],CPs_img[0][1], 'ro', label='Left Contact Point', fillstyle='none')
        plt.plot(CPs_img[1][0],CPs_img[1][1], 'bo', label='Right Contact Point', fillstyle='none')
        plt.legend()
        plt.show()
        plt.close()

    return img, CPs_img

def extract_edges_CV(img):
    '''
    give the image and return a list of [x.y] coordinates for the detected edges

    '''
    IGNORE_EDGE_MARGIN = 1
    threshValue = 50
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray,threshValue,255,cv2.THRESH_BINARY)
    #ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # Each contour has shape (n, 1, 2) where 'n' is the number of points. Presumably this is so each
    # point is a size 2 column vector, we don't want this so reshape it to a (n, 2)
    contours = [contour.reshape(contour.shape[0], 2) for contour in contours]

    # Sort the contours by arc length, descending order
    contours.sort(key=lambda c: cv2.arcLength(c, False), reverse=True)

    #Assume that the drop is the largest contour
    #drop_profile = contours[0]
    drop_profile = contours[0]

    #Put the drop contour coordinates in order (from ?? to ??)
    #drop_profile_squish = squish_contour(drop_profile)

    # Ignore points of the drop profile near the edges of the drop image
    width, height = img.shape[1::-1]
    if not (width < IGNORE_EDGE_MARGIN or height < IGNORE_EDGE_MARGIN):
        mask = ((IGNORE_EDGE_MARGIN < drop_profile[:, 0]) & (drop_profile[:, 0] < width - IGNORE_EDGE_MARGIN) &
            (IGNORE_EDGE_MARGIN < drop_profile[:, 1]) & (drop_profile[:, 1] < height - IGNORE_EDGE_MARGIN))
        drop_profile = drop_profile[mask]

    return drop_profile

def prepare_contour(coords, CPs, given_input_len=1100, right_only=False):
    """Take the contour of the whole drop, split it into left and right sides"""

    # flip
    coords[:,1] = -coords[:,1].astype(int)
    CPs[0][1] = -CPs[0][1]
    CPs[1][1] = -CPs[1][1]

    # define apex position as the between contact points
    xapex = (min(np.array(CPs)[:,0]) + max(np.array(CPs)[:,0]))/2

    # determine left and right sides of the drop using the apex x coord
    l_drop = []
    r_drop = []
    for n in coords:
        if n[0] < xapex:
            l_drop.append(n)
        if n[0] > xapex:
            r_drop.append(n)
    l_drop = np.array(l_drop)
    r_drop = np.array(r_drop)

    ### transpose both half drops so that they both face right and the apex of both is at x=0
    left_max_x = max(l_drop[:,0])
    right_min_x = min(r_drop[:,0])
    CPs[0][0] = -CPs[0][0] + left_max_x
    CPs[1][0] = CPs[1][0] - right_min_x
    l_drop[:,0] = -l_drop[:,0] + left_max_x
    r_drop[:,0] = r_drop[:,0] - right_min_x

    ### transpose both halfdrops so that the min y value is at 0
    CPs[0][1] = CPs[0][1] + abs(min(l_drop[:,1]))
    CPs[1][1] = CPs[1][1] + abs(min(r_drop[:,1]))
    l_drop[:,1] = l_drop[:,1] - min(l_drop[:,1])
    r_drop[:,1] = r_drop[:,1] - min(r_drop[:,1])

    ###check that CPs are in the contour, sometimes it's just off
    CPs = np.array(CPs)
    if np.any(np.all(l_drop == np.array(CPs[0]), axis=1)) == False: # check that CP is in the contour
        ###find nearest contour point and use that as the CP
        #print('CP not in contour: ', CP)
        CPs[0] = list(min(l_drop, key=lambda x: ((CPs[0][0] - x[0])**2 + (CPs[0][1] - x[1])**2) ** 0.5))
        #print('CPs are now: ',CPs)
    if np.any(np.all(r_drop == np.array(CPs[1]), axis=1)) == False: # check that CP is in the contour
        ###find nearest contour point and use that as the CP
        #print('CP not in contour: ', CP)
        CPs[1] = list(min(r_drop, key=lambda x: ((CPs[1][0] - x[0])**2 + (CPs[1][1] - x[1])**2) ** 0.5))
        #print('CPs are now: ',CPs)

    if 0: # normalise so that the drop apex is at y=1
        CPs[1][0] = CPs[1][0]/max(r_drop[:,1])
        CPs[1][1] = CPs[1][1]/max(r_drop[:,1])
        r_drop[:,0] = r_drop[:,0]/max(r_drop[:,1])
        r_drop[:,1] = r_drop[:,1]/max(r_drop[:,1])

    if right_only == True:
        #check CPs in in the contour
        if CPs[1] not in r_drop:
            raise 'Error, CPs not in contour, code must be revised'

        pred_ds = r_drop

    else:
        #check CPs in in the contour
        if CPs[0] not in l_drop:
            raise 'Error, CPs not in contour, code must be revised'
        if CPs[1] not in r_drop:
            raise 'Error, CPs not in contour, code must be revised'

        pred_ds = np.zeros((2,input_len,2))
        pred_ds[0] = l_drop
        pred_ds[1] = r_drop

    return pred_ds, CPs

def create_contour(angle,
                  Bo,
                  scaler,
                  roughness,
                  savedir='./',
                  input_len=1100,
                  display=False):
    filename = filename = str(angle) + "_" + str(Bo) + "_" + str(scaler) + "_" + str(roughness) + "_.npy"

    drop, CPs = draw_drop(angle, Bo, scaler, roughness, 5000, debug=display)

    contour = extract_edges_CV(drop)
    right, CPs = prepare_contour(contour, CPs, given_input_len=None, right_only=True)

    if display==True:
        plt.plot(right[:,0],right[:,1],'o')
        plt.show()
        plt.close()

    return right, CPs

def create_contour_dataset(angle,
                            roughness,
                            min_Bo, max_Bo, N_Bos,
                            min_scaler, max_scaler, N_scalers,
                            sampling_window_size=110, window_shift_start=-10, window_shift_end=10,
                            input_len=None,
                            save_dir=None,
                            debug=False):
    """Creates a dataset of contact angle images based on the given parameters.

    min_angle is the lower bound of the possible contact angles
    max_angle is the upper bound of the possible contact angles
    N_angles is the number of images of difference contact angles created, the contact angles of these drops will
        be evenly spaced between the lower and upper bounds, inclusive of bound values
    min_Bo, max_Bo, and N_Bo alter the Bond number parameter of the dataset
    min_scaling, max_scaling, N_scaled_drops alter the scaling of the drop within the image, acting as a proxy
        resolution parameter
    min_roughness, max_roughness, and N_roughness alter the roughness of the baseline. 0 roughness is a perfectly
        smooth baseline, while 1e-2 is the recomended maximum value.
    N_pts_drop is the number of points used when drawing the shape of the halfdrop contour after solving the Young-
        Lacplace equation. A number significantly larger than the resolution of the image is recommended, so that the
        limiting value is the saved images resolution rather than the resolution of the solution to the Young-Laplace
        equation.
    debug (True or Flase). Set to true to visualise outputs while debugging.
    """
    if debug == False: # uncomment this big when running on server
        matplotlib.use('Agg')

    start_time = time.time()
    #psutil.cpu_percent(interval=0)
    #psutil.virtual_memory()

    Bos = np.linspace(min_Bo, max_Bo, N_Bos)
    print('Dataset includes ', N_Bos, ' drops of bond numberss between ', min_Bo, ' and ', max_Bo)

    scalers = np.geomspace(min_scaler, max_scaler, N_scalers)
    print('Dataset includes ', N_scalers, ' drops with scaling values  logarithmically spaced between ', min_scaler, ' and ',
          max_scaler)

    print('Total size of data set is :',N_Bos * N_scalers)
    print()

    dst = 'angle'+str(angle)+'_BondNumbers'+str(min_Bo)+'-'+str(max_Bo)+'_'+str(N_Bos)+'_scalers'+str(min_scaler)+'-'+str(max_scaler)+'_'+str(N_scalers)+'_roughness'+str(roughness)
    if debug == False and save_dir is not None:
        assert (not os.path.isfile(str(save_dir)+str(dst)+'.pkl'))  # make sure the directory does not exist, to avoid confusion

    created = 0

    contours = {}

    print('Creating contours...')
    for i, Bo in enumerate(Bos):
        for j, scaler in enumerate(scalers):
            right_side, CPs = create_contour(angle,Bo,scaler,roughness,input_len=None,display=debug)
            key = str(angle)+'_'+str(Bo)+'_'+str(scaler)+'_'+str(roughness)+'_'+str(CPs[1][0])+'_'+str(CPs[1][1])+'_'+str(0)+'_'+str(0)
            print(key)
            contours[key] = right_side

    print('Sampling...')
    sampled_output = sampling(contours, sampling_window_size, window_shift_start, window_shift_end, 10, debug)
    print('Normalising...')
    ds = normalize_ds(sampled_output)

    if save_dir is not None:
        #dst = 'data'+str(a)+'_'+str(b)+'_'+note+model_letter+'_'+str(drops)+'_scaled'+str(N_scaled_drops)
        #np.save(file=dst,arr=contours)
        with open(save_dir + dst + '.pkl', 'wb') as f:
            pickle.dump(ds, f, pickle.HIGHEST_PROTOCOL)
        print('Contours saved to: ',save_dir+dst+'.pkl')
    print("%s seconds since starting " % (time.time() - start_time))
    return ds

def sampling0(ds, n_drop_samples, n_surface_samples):
    """Samples half-drop contour by cutting contour points out on either side of the contact point (CP).
    ds (dictionary) - the unsampled data set of contours. Dictionary keys are expected to be of the format
                    key = str(angle)+'_'+str(Bo)+'_'+str(scaler)+'_'+str(roughness)+'_'+str(CP[0])+'_'
                    +str(CP[1])+'_'+str(n_drop_sample)+'_'+str(n_surface_sample)
    n_drop_samples (int) - the number of evenly spaced cuts made to the drop side of the halfdrop
    n_surface_samples (int) - the number of cuts made to the surface side of the halfdrop

    n_drop_sample (int) - the integer included in the dictionary key which denotes the sample cut which is
                    being used. Where 0 is no sampling has occured, and the maximum value is the n_drop_samples
                    value.
    n_surface_sample (int) - the integer included in the dictionary key which denotes the sample cut which is
                    being used. Where 0 is no sampling has occured, and the maximum value is the
                    n_surface_samples value.

    Drop side sampling example:
        If drop sampling numbers exist in the range of 0-3, then there are 3 drop sampling cut points between
        the apex and the contact point. 0 denotes no sampling, and 3 denotes that the third evenly spaced cut
        point from the apex (the cut closest to the CP) is used. And so the one quarter of the drop is included
        in the sampled contour. The same is true for the sample side, with the slice closer to the CP being the
        contour which remains.
    """

    output = {}

    for key in ds.keys():
        print('key of data point being sampled: ', key)
        contour = ds[key]
        angle = key.split('_')[0]
        Bo = key.split('_')[1]
        scale = key.split('_')[2]
        roughness = key.split('_')[3]
        CP = [eval(key.split('_')[4]),eval(key.split('_')[5])]
        output[key] = ds[key]

        # what index is CP
        print(CP)
        idx = contour[:,0].tolist().index(CP[0])

        # define indexes of drop side cut points
        for n_drop_sample in range(n_drop_samples+1):
            for n_surface_sample in range(n_surface_samples+1):
                    left_cut = int((idx*n_drop_sample)/(n_drop_samples+1))
                    #left_cut = int((idx*n_drop_sample)/(n_drop_samples+1))
                    right_cut = int(len(contour) - ((len(contour)-idx-1)*n_surface_sample) / (n_surface_samples+1))
                    right_cut = int(len(contour) - ((len(contour)-idx-1)*n_surface_sample) / (n_surface_samples+1))
                    key = str(angle)+'_'+str(Bo)+'_'+str(scaler)+'_'+str(roughness)+'_'+str(CP[0])+'_'+str(CP[1])+'_'+str(n_drop_sample)+'_'+str(n_surface_sample)
                    output[key] = contour[left_cut:right_cut]
    return output

def sampling(ds, window_size, window_shift_start, window_shift_end, surface_points=10, display=False):
    """Samples half-drop contour by taking a window of coordinate points either side of the contact point (CP).
    ds (dictionary) - the unsampled data set of contours. Dictionary keys are expected to be of the format
                    key = str(angle)+'_'+str(Bo)+'_'+str(scaler)+'_'+str(roughness)+'_'+str(CP[0])+'_'
                    +str(CP[1])+'_'+str(n_drop_sample)+'_'+str(n_surface_sample)
    window_size (int) - The number of coordinate points taken from the contour during sampling.
    window_shift_start (int) - The number of coordinate point indexes back from the CP the window is moved (given
                                as a negative number).
    window_shift_end (int) - The number of coordinate point indexes forward from the CP the window is moved.
    surface_points (int) - The number of coordinate points given after the contact point when window shift is 0

    Drop side sampling example:
        If the window_size is 110, the window_shift_start is -8, the window_shift_end is 8, and surface_points is 10. 
        Then the 16 contours would be outputted (window_shift_end - window_shift_start), each with 110 coordinate 
        pairs. If window shift is 0 then the window_size-surface_points=100 coordinate points before the contact point 
        and the surface_points=10 coordinate points after the contact point are given. If the window shift is -1 then 
        the 101 coordinates before the CP and the 9 coordinate points after the CP would be used.
    """

    output = {}

    for key in ds.keys():
        if display==True:
            print('key of data point being sampled: ', key)
        contour = ds[key]
        angle = key.split('_')[0]
        Bo = key.split('_')[1]
        scale = key.split('_')[2]
        roughness = key.split('_')[3]
        CP = [eval(key.split('_')[4]),eval(key.split('_')[5])]

        # what index is CP
        index = contour[:,0].tolist().index(CP[0])
        index = np.where(np.all(contour == CP, axis=1))[0][0]

        # define indexes of drop side cut points
        for i in range(window_shift_start, window_shift_end+1):
            no_shift_start_index = int(window_size - surface_points)
            key = str(angle)+'_'+str(Bo)+'_'+str(scale)+'_'+str(roughness)+'_'+str(CP[0])+'_'+str(CP[1])+'_'+str(window_size)+'_'+str(i)
            bound_start = index-no_shift_start_index+i
            bound_end = index-no_shift_start_index+window_size+i

            # may need to include zeropadding if index bounds are exceeded

            output[key] = contour[bound_start:bound_end]

    return output

def normalize_ds(ds):
    """Normalize such that the drop apex is at a z value of 1"""
    for key in ds.keys():
        # normalise
        contour = ds[key].copy()
        maxz = max(contour[:,1])
        normalised = contour/maxz

        if normalised[0,0] != 0: # translate so that min x value is 0
            minx = min(normalised[:,0])

            new = normalised.copy()
            new[:,0] -= minx

            ds[key] = new
        else:
            ds[key] = normalised
    return ds

def positive_float(value):
    '''
    Type checking for positive floats passed to the command-line parser

    :param value: Input that is to be type-checked (scalar)
    :return: Input cast to a float
    :raises ArgumentTypeError: If the input is less than, or equal to 0 or
                               cannot be cast to a float
    '''
    if float(value) <= 0:
        raise argparse.ArgumentTypeError(f'{value} is an invalid positive '
                                         'float value')
    return float(value)

def non_negative_float(value):
    '''
    Type checking for non-negative floats passed to the command-line parser

    :param value: Input that is to be type-checked (scalar)
    :return: Input cast to a float
    :raises ArgumentTypeError: If the input is less than 0 or cannot be cast
                               to a float
    '''
    if float(value) < 0:
        raise argparse.ArgumentTypeError(f'{value} is an invalid positive '
                                         'float value')
    return float(value)

def contact_angle(value):
    '''
    Type checking for contact angles passed to the command-line parser

    :param value: Input that is to be type-checked (scalar)
    :return: Input cast to a float
    :raises ArgumentTypeError: If the input is less than 0, greater than 180,
                                or cannot be cast to a float
    '''
    if float(value) <= 0:
        raise argparse.ArgumentTypeError(f'{value} is an invalid contact '
                                         'angle value')
    if float(value) > 180:
        raise argparse.ArgumentTypeError(f'{value} is an invalid contact '
                                         'angle value')
    return float(value)

def non_negative_integer(value):
    '''
    Type checking for number of contact angles per degree passed to the
    command-line parser

    :param value: Input that is to be type-checked (scalar)
    :return: Input cast to a positive integer
    :raises ArgumentTypeError: If the input is less than 0, or cannot be cast to
                               a non-negative interget
    '''
    if int(value) < 0:
        raise argparse.ArgumentTypeError(f'{value} is an invalid integer'
                                         'angle value')

    return int(value)

def parse_cmdline(argv=None):
    '''
    Extract command line arguments to change program execution

    :param argv: List of strings that were passed at the command line
    :return: Namespace of arguments and their values
    '''
    parser = argparse.ArgumentParser(description='Create a dataset of synthetic'
                                     ' contact angle measurement images for '
                                     'the given parameters')
    parser.add_argument('save_dir', help='Relative or absolute path to '
                                     'the desired directory where synthetic'
                                     ' images will be saved. If the directory '
                                     ' does not exist then one will be created.',
                        default='./')
    parser.add_argument('-a', '--angle', type=contact_angle,
                        help='The desired contact angle of the synthetic drop',
                        action='store', dest='angle')
    parser.add_argument('-b', '--bond_number', type=non_negative_float,
                        help='The desired Bond number of the synthetic drop',
                        default=0, action='store', dest='bond_number')
    parser.add_argument('-s', '--scale', type=positive_float,
                        help='The scale of the synthetic drop image. At a value'
                        ' of 1 the drop occupies a majority of the image. '
                        'Increasing the scale value makes the drop smaller. '
                        'The recommended maximum value is 10.',
                        default=1, action='store', dest='scale')
    parser.add_argument('-r', '--roughness', type=float,
                        help='The desired roughess of the surface in the '
                        'synthetic drop image. A value of 0 will give a smooth '
                        ' surface. The recommended maximum value is 1e-2.',
                        default=0, action='store', dest='roughness')
    args = parser.parse_args(argv)

    return args

def main(argv=None):
    '''Create a pkl file of a single angle and single roughness value, with 21
    scaler and 11 roughness values.
    '''
    args = parse_cmdline(argv)

    # Set default numerical arguments
    save_dir=str(args.save_dir)
    angle = args.angle
    bond_number = args.bond_number
    scale = args.scale
    roughness = args.roughness

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    if 0: #test
        angle = 150
        Bo = 0.5
        scaler = 4
        roughness = 0
        debug = False
        right_side, CPs = create_contour(angle, Bo, scaler, roughness, input_len=None, display=debug)
        print('works')
        print(right_side)
        print(CPs)
    else:
        create_contour_dataset(angle,
                   roughness,
                   0,1,11, #super dense: 0.1,0.2,5,
                   1,4,7,
                   sampling_window_size=110,
                   debug=False,
                   save_dir = save_dir)

if __name__ == '__main__':
    main()
