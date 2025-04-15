#!/usr/bin/env python
#coding=utf-8

"""This code serves as a discrete instance of image preprocessing before contact
angle fit software is implemented

This includes automatic identification of the drop through Hough transform,
followed by cropping of the image to isolate the drop. Tilt correction is then
performed using the identified contact points of the drop.
"""

from sklearn.cluster import OPTICS # for clustering algorithm
import numpy as np
import matplotlib.pyplot as plt
import cv2 #for image reading, contour detection
import math #for tilt_correction
from scipy import misc, ndimage #for tilt_correction
from scipy import signal #for CP ID
from scipy.odr import Model, Data, ODR #for linear fit

def auto_crop(img, low=50, high=150, apertureSize=3, verbose=0): # DS 08/06/23
    '''
    Automatically identify where the crop should be placed within the original
    image

    This function utilizes the opencv circular and linear Hough transfrom
    implementations to identify the most circular object in the image
    (the droplet), and center it within a frame that extends by padding to each
    side.

    :param img: 2D numpy array of [x,y] coordinates of the edges of the
                  image
    :param low: Value of the weak pixels in the dual thresholding
    :param high: Value of the strong pixels in the dual thresholding
    :param apertureSize: The aperture size variable given to cv2.Canny during
                        edge detection
    :param verbose: Integer values from 0 to 2, giving varying degrees of detail
    :return: list of [left, right, top, bottom] values for the edges of the
             bounding box
    '''


    if verbose >=1:
        print('Performing auto-cropping, please wait...')

    # find edges in the image
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,low,high,apertureSize = apertureSize)

    #hough circle to find droplet - minRadius at 5% img width
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1,
                              minDist=max(img.shape), #one circle
                              param1=30, #30
                              param2=10, #15
                              minRadius=int(img.shape[1]*0.02), #0.05
                              maxRadius=0)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

            if verbose >= 2:
                circle1 = plt.Circle(center, 1, color='r')
                # now make a circle with no fill, which is good for hi-lighting key results
                circle2 = plt.Circle(center, radius, color='r', fill=False)

                ax = plt.gca()
                ax.axis('equal')

                ax.add_patch(circle1)
                ax.add_patch(circle2)

                fig = plt.gcf()
                fig.set_size_inches(10, 10)

                plt.imshow(img)
                plt.title("Hough circle")
                plt.show()
                plt.close()
    else:
        #hough circle to find droplet - minRadius at 0
        circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1,
                                  minDist=max(img.shape), #one circle
                                  param1=30,
                                  param2=20,
                                  minRadius=0,
                                  maxRadius=0)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

            if verbose >= 2:
                circle1 = plt.Circle(center, 1, color='r')
                # now make a circle with no fill, which is good for hi-lighting key results
                circle2 = plt.Circle(center, radius, color='r', fill=False)

                ax = plt.gca()
                ax.axis('equal')

                ax.add_patch(circle1)
                ax.add_patch(circle2)

                fig = plt.gcf()
                fig.set_size_inches(10, 10)

                plt.imshow(img)
                plt.title("Hough circle")
                plt.show()
                plt.close()
    else:
        print('Hough circle failed to identify a drop')

    #crop image based on circle found (this prevents hough line identifying the needle)
    bottom = int(center[1] + (radius * 1.2)) # add 20% padding
    if bottom>img.shape[0]:
        bottom = img.shape[0]
    top = int(center[1] - (radius * 1.2)) #add 20% padding
    if top < 0:
        top=0

    img = img[top:bottom,:]
    edges = cv2.Canny(img,50,150,apertureSize = 3)
    center = (center[0], -(center[1] - bottom)) #reassign circle center to new cropped image

    if verbose>=2:
        plt.imshow(img)
        plt.title('image after top and bottom crop')
        plt.show()
        plt.close()

    #hough lines to find baseline
    lines = cv2.HoughLines(edges,1,np.pi/180,100)

    if lines is not None: # if the HoughLines function is successful
        if verbose >= 2:
            print('shape of image: ',img.shape)
        for i,line in enumerate(lines):
            if i==0:
                rho,theta = line[0]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0)
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - img.shape[1]*(-b))
                y2 = int(y0 - 1000*(a))
                if verbose >= 2:
                    plt.title('hough approximated findings')
                    plt.imshow(img)
                    circle1 = plt.Circle(center, 1, color='r')
                    circle2 = plt.Circle(center, radius, color='r', fill=False)
                    ax = plt.gca()
                    ax.add_patch(circle1)
                    ax.add_patch(circle2)
                    fig = plt.gcf()

                    plt.plot([x1,x2],[y1,y2],'r')
                    fig = plt.gcf()
        p1,p2 = (x1,y1),(x2,y2) # baseline exists between these points
        if verbose >= 2:
            print('baseline goes from ',p1,' to ',p2)

        # now find bounds

        # find intercept of line and circle
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]

        a = dx**2 + dy**2
        b = 2 * (dx * (p1[0] - center[0]) + dy * (p1[1] - center[1]))
        c = (p1[0] - center[0])**2 + (p1[1] - center[1])**2 - radius**2

        discriminant = b**2 - 4 * a * c
        if discriminant > 0:
            t1 = (-b + discriminant**0.5) / (2 * a)
            t2 = (-b - discriminant**0.5) / (2 * a)

            intersect1, intersect2 = None,None
            intersect1, intersect2 = (dx * t1 + p1[0], dy * t1 + p1[1]), (dx * t2 + p1[0], dy * t2 + p1[1])

            if intersect1 == None or intersect2 == None:
                raise 'found baseline does not intersect with found circle'

            if verbose >= 2:
                plt.plot(intersect1[0],intersect1[1],'o',color='orange')
                plt.plot(intersect2[0],intersect2[1],'o',color='orange')

                plt.show()
                plt.close()

            bottom = int(max([intersect1[1],intersect2[1]]))          #max value of intersect points
            top = int(center[1] - radius)                             #assume top of drop is in image
            if center[1] < max([intersect1[1],intersect2[1]]):
                right = int(center[0] + radius)
            else:
                right = int(max([intersect1[0],intersect2[0]]))
            if center[1] < min([intersect1[1],intersect2[1]]):
                left = int(center[0] - radius)
            else:
                left = int(min([intersect1[0],intersect2[0]]))
        else:
            # bounds is (left,right,top,bottom)
            print('No baseline-drop intercept found')
            left = int(center[0] - radius)
            right = int(center[0] + radius)
            top = int(center[1] - radius)
            bottom = int(center[1] + radius)

    else: #if the HoughLine function cannot identify a surface line, use the circle as a guide for bounds
        left = int(center[0] - radius)
        right = int(center[0] + radius)
        top = int(center[1] - radius)
        bottom = int(center[1] + radius)

    pad = int(max([right - left,bottom-top])/4)

    top -= pad
    bottom += pad
    left -= pad
    right += pad

    if left < 0:
        left = 0
    if top < 0:
        top = 0
    if bottom > img.shape[0]:
        bottom = img.shape[0]
    if right > img.shape[1]:
        right = img.shape[1]

    if verbose >= 2:
        print('lower most y coord of drop: ', bottom)
        print('upper most y coord of drop: ', top)
        print('right most x coord of drop: ', right)
        print('left most x coord of drop: ', left)

    bounds = [left,right,top,bottom]
    new_img = img[top:bottom,left:right]

    if verbose >= 1:
        plt.title('cropped drop')
        plt.imshow(new_img)
        plt.show()
        plt.close()

    return new_img, bounds

def cluster_OPTICS(sample, out_style='coords',xi=None,eps=None,verbose=0):
    """Takes an array (or list) of the form [[x1,y1],[x2,y2],...,[xn,yn]].
    Clusters are outputted in the form of a dictionary.

    If out_style='coords' each dictionary entry is a group, and points are outputted in as a numpy array
    in coordinate form.
    If out_xy='xy' there are two dictionary entries for each group, one labeled as nx and one as ny
    (where n is the label of the group). Each of these are 1D numpy arrays

    If xi (float between 0 and 1) is not None and eps is None, then the xi clustering method is used.
    The optics algorithm defines clusters based on the minimum steepness on the reachability plot.
    For example, an upwards point in the reachability plot is defined by the ratio from one point to
    its successor being at most 1-xi.

    If eps (float) is not None and xi is None, then the dbscan clustering method is used. Where eps is the
    maximum distance between two samples for one to be considered as in the neighborhood of the other.

    https://stackoverflow.com/questions/47974874/algorithm-for-grouping-points-in-given-distance
    https://scikit-learn.org/stable/modules/generated/sklearn.cluster.OPTICS.html
    """
    if eps != None and xi==None:
        clustering = OPTICS(min_samples=2,cluster_method = 'dbscan',eps = eps).fit(sample) # cluster_method changed to dbscan (so eps can be set)
    elif xi != None and eps==None:
        clustering = OPTICS(min_samples=2,xi=xi).fit(sample) # original had xi = 0.05, xi as 0.1 in function input
    else:
        raise 'Error: only one of eps and xi can be chosen but not neither nor both'
    groups = list(set(clustering.labels_))

    if verbose==2:
        print(clustering.labels_)
    elif verbose==1:
        print(groups)
    elif verbose==0:
        pass

    dic = {}
    for n in groups:
        if n not in dic:
            dic[n] = []
        for i in range(len(sample)):
            if clustering.labels_[i] == n:
                dic[n].append(list(sample[i]))
        dic[n] = np.array(dic[n])

    # separate points and graph
    dic2={}
    for k in dic.keys():
        x = []
        y = []
        for i in range(len(dic[k])):
            x.append(dic[k][i][0])
        dic2[str(k)+'x'] = np.array(x)
        for i in range(len(dic[k])):
            y.append(dic[k][i][1])
        dic2[str(k)+'y'] = np.array(y)


    if out_style=='coords':
        return dic
    elif out_style=='xy':
        return dic2

def distance1(P1, P2):
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
        nearest = min(pass_by, key=lambda x: distance1(path[-1], x))
        path.append(nearest)
        pass_by.remove(nearest)
    path = np.array(path)
    return path

def prepare_hydrophobic(coords,xi=0.8,cluster=True,display=False):
    """takes an array (n,2) of coordinate points, and returns the left and right halfdrops of the contour.
    xi determines the minimum steepness on the reachability plot that constitutes a cluster boundary of the
    clustering algorithm.
    deg is the degree of the polynomial used to describe the shape of the droplet.

    This code is adapted from the prepare module, but this version differs in that it assumes that the drop
    is hydrophobic."""
    coords = coords.astype(float)

    # flip contour so that min and max values are correct
    for coord in coords:
        coord[1] = -coord[1]

    longest = coords

    #print("first few coordinates of the longest contour: ",longest[:3])

    xlongest = []
    ylongest = []
    for i in range(len(longest)):
        xlongest.append(longest[i][0])
        ylongest.append(longest[i][1])

    #print("first few x coordinates of the longest contour: ",xlongest[:3])
    #print("first few y coordinates of the longest contour: ",ylongest[:3])


    # Find a appropriate epsilon value for cluster_OPTICS, this will remove noise in the bottom 10% of the drop
    #.   most importantly noise is reduced at contact points.

    # variables in this process are how much and what part of the top of the droplet we use to be representative of
        # the full contour, and whether we use the max(distance) between points or the average between points, or
        # a scalar value of either.

    xtop = [] # isolate top 90% of drop
    ytop = []
    percent = 0.3
    #print('Isolate the top ',100-(percent*100),'% of the contour:')
    for n,y in enumerate(ylongest):
        if y > min(ylongest) + (max(ylongest) - min(ylongest))*percent:
            xtop.append(xlongest[n])
            ytop.append(y)
    xtop = np.array(xtop)
    ytop = np.array(ytop)

    top = []
    for n,x in enumerate(xtop):
        top.append([xtop[n],ytop[n]])
    top = np.array(top)
    top_array = optimized_path(top)

    dists = [] # find the average distance between consecutive points
    for n,co in enumerate(top_array):
        if 1<n:
            a = top_array[n]
            dist = np.linalg.norm(top_array[n]-top_array[n-1])
            dists.append(dist)

    # how epsilon is chosen here is important
    #eps = (sum(dists)/len(dists))*2 # eps is 2 times the average distance between points
    eps = (sum(dists)/len(dists))*1.5 # eps is 2.5 times the average distance between points
    if display:
        #print(dists)
        print()
        print('Max dist between points is: ',max(dists))
        print('Average dist between points is: ',sum(dists)/len(dists))
        print()
        print('Sort using cluster_OPTICS with an epsilon value of ',eps)
    input_contour = np.array(longest)
    dic = cluster_OPTICS(input_contour,eps=eps)
    if display:
        jet= plt.get_cmap('jet')
        colors = iter(jet(np.linspace(0,1,len(list(dic.keys())))))
        for k in dic.keys():
            plt.plot(dic[k][:,0],dic[k][:,1], 'o',color=next(colors))
        plt.title(str(len(dic.keys()))+' groups found by clustering with epsilon value of '+str(eps))
        plt.show()
        plt.close()

    maxkey=max(dic, key=lambda k: len(dic[k]))
    longest = dic[maxkey]
    #print("first few coordinates of the longest contour: ",longest[:3])

    xlongest = []
    ylongest = []
    for i in range(len(longest)):
        xlongest.append(longest[i][0])
        ylongest.append(longest[i][1])

    outline = np.empty((len(xlongest),2))
    for i in range(len(xlongest)):
        outline[i,[0]]=xlongest[i]
        outline[i,[1]]=ylongest[i]


    ############################

    # find the apex of the drop and split the contour into left and right sides

    xtop = [] # isolate top 90% of drop
    ytop = []
    # percent = 0.1 # already defined
    #print('isolate the top ',100-(percent*100),'% of the contour:')
    for n,y in enumerate(ylongest):
        if y > min(ylongest) + (max(ylongest) - min(ylongest))*percent:
            xtop.append(xlongest[n])
            ytop.append(y)
    xapex = (max(xtop) + min(xtop))/2

    l_drop = []
    r_drop = []
    for n in longest:
        if n[0] <= xapex:
            l_drop.append(n)
        if n[0] >= xapex:
            r_drop.append(n)
    l_drop = np.array(l_drop)
    r_drop = np.array(r_drop)

    # transpose both half drops so that they both face right and the apex of both is at 0,0
    r_drop[:,0] = r_drop[:,0] - xapex
    l_drop[:,0] = -l_drop[:,0] + xapex

    if display:
        plt.plot(r_drop[:,[0]], r_drop[:,[1]], 'b,')
        #plt.show()
        #plt.close()
        plt.plot(l_drop[:,[0]], l_drop[:,[1]], 'r,')
        #plt.gca().set_aspect('equal', adjustable='box')
        #plt.xlim([470,530])
        #plt.ylim([-188,-190])
        plt.show()
        plt.close()

    #############################

    # the drop has been split in half

    # this system has a user input which gives a rough indication of the contact point and the surface line

    # isolate the bottom 5% of the contour near the contact point

    drops = {}
    counter = 0
    crop_drop = {}
    CPs = {}
    for halfdrop in [l_drop,r_drop]:
        new_halfdrop = sorted(halfdrop.tolist(), key=lambda x: (x[0],-x[1])) #top left to bottom right
        new_halfdrop = optimized_path(new_halfdrop)#[::-1]

        xnew_halfdrop = new_halfdrop[:,[0]].reshape(len(new_halfdrop[:,[0]]))
        ynew_halfdrop = new_halfdrop[:,[1]].reshape(len(new_halfdrop[:,[1]]))

        # isolate the bottom of the drop to help identify contact points (may not need to do this for all scenarios)
        bottom = []
        top = [] # will need this later
        #print('isolate the bottom ',percent*100,'% of the contour:') # percent defined above
        div_line_value = min(new_halfdrop[:,[1]]) + (max(new_halfdrop[:,[1]]) - min(new_halfdrop[:,[1]]))*percent
        for n in new_halfdrop:
            if n[1] < div_line_value:
                bottom.append(n)
            else:
                top.append(n)

        bottom = np.array(bottom)
        top = np.array(top)

        xbottom = bottom[:,[0]].reshape(len(bottom[:,[0]]))
        ybottom = bottom[:,[1]].reshape(len(bottom[:,[1]]))
        xtop = top[:,[0]].reshape(len(top[:,[0]]))
        ytop = top[:,[1]].reshape(len(top[:,[1]]))

        #print('max x value of halfdrop is: ',max(xhalfdrop))

        if 0: # plot the bottom 10% of the contour, check that the contour ordering is performing
            plt.plot(xbottom, ybottom, 'b,')
            plt.title('bottom 10% of the contour')
            #plt.xlim([130,200])
            plt.show()
            plt.close()

        #### Continue here assuming that the drop is hydrophobic ####
        if 1:
            # order all halfdrop points using optimized_path (very quick but occasionally makes mistakes)

            xCP = min(xbottom)
            #yCP = min([coord[1] for coord in new_halfdrop if coord[0]==xCP])
            yCP = max([coord[1] for coord in bottom if coord[0]==xCP])
            CPs[counter] = [xCP, yCP]

            if display: #check
                plt.plot(new_halfdrop[:,0],new_halfdrop[:,1])
                plt.show()
                plt.close()

            # remove surface line past the contact point
            index = new_halfdrop.tolist().index(CPs[counter]) #?

            new_halfdrop = new_halfdrop[:index+1]

            if 0:
                xCP_index = [i for i, j in enumerate(xnew_halfdrop) if j == xCP]
                #print('xCP_index is: ',xCP_index)
                yCP_index = [i for i, j in enumerate(ynew_halfdrop) if j == yCP]
                #print('yCP_index is: ',yCP_index)

                new_halfdrop = np.zeros((len(xnew_halfdrop),2))
                for n in range(len(xnew_halfdrop)):
                    new_halfdrop[n,[0]]=xnew_halfdrop[n]
                    new_halfdrop[n,[1]]=ynew_halfdrop[n]
                #print('first 3 points of new_halfdrop are: ',new_halfdrop[:3])
                #print('length of new_halfdrop is: ',len(new_halfdrop))

                if xCP_index == yCP_index:
                    if new_halfdrop[xCP_index[0]+1][1]>new_halfdrop[xCP_index[0]-1][1]:
                        new_halfdrop = new_halfdrop[xCP_index[0]:]
                    else:
                        new_halfdrop = new_halfdrop[:xCP_index[0]+1]
                else:
                    raise_error = True
                    for x in xCP_index:
                        for y in yCP_index:
                            if x==y:
                                raise_error = False
                                xCP_index = [x]
                                yCP_index = [y]
                                #print('indices of the CP are: ',xCP_index[0],', ',yCP_index[0])
                                if new_halfdrop[xCP_index[0]+1][1]>new_halfdrop[xCP_index[0]-1][1]:
                                    new_halfdrop = new_halfdrop[xCP_index[0]:]
                                else:
                                    new_halfdrop = new_halfdrop[:xCP_index[0]+1]
                    if raise_error == True:
                        print('The index of the contact point x value is: ', new_halfdrop[xCP_index])
                        print('The index of the contact point y value is: ', new_halfdrop[yCP_index])
                        raise 'indices of x and y values of the contact point are not the same'

        if 0:
            # order all halfdrop points using two-opt (the slower method)

            # before any ordering is done, chop off the surface line that is past the drop edge
            del_indexes = []
            for index,coord in enumerate(bottom):
                if coord[0]>max(xtop):
                    del_indexes.append(index)
                if coord[1]<yCP:
                    del_indexes.append(index)
            #halfdrop = np.delete(halfdrop,del_indexes)
            xbot = np.delete(bottom[:,0],del_indexes)
            ybot = np.delete(bottom[:,1],del_indexes)

            #bottom = np.empty((len(xbot),2))
            #for n, coord in enumerate(bottom):
            #    bottom[n,0] = xbot[n]
            #    bottom[n,1] = ybot[n]

            bottom = np.array(list(zip(xbot,ybot)))

            #print('shape of another_halfdrop is: '+ str(type(another_halfdrop)))
            print('first few points of halfdrop are: ',halfdrop[:3])
            if display:
                colors = iter(jet(np.linspace(0,1,len(bottom))))
                for n,coord in enumerate(bottom):
                    plt.plot(bottom[n,0],bottom[n,1], 'o', color=next(colors))
                plt.title('Cropped bottom of hafldrop')
                plt.show()
                plt.close()


            # order points using traveling salesman two_opt code
            bottom = bottom[::-1] # start at the top
            print('Starting first coordinate of bottom slice of halfdrop is: ',bottom[0])
            new_bot, _ = two_opt(bottom,0.01) # increase improvement_threshold from 0.1 to 0.01
            if new_bot[0,1]<new_bot[-1,1]:
                new_bot = new_bot[::-1]
            xbot,ybot = new_bot[:,[0]],new_bot[:,[1]]

            if display: #display
                colors = iter(jet(np.linspace(0,1,len(bottom))))
                for n,coord in enumerate(bottom):
                    plt.plot(new_bot[n,0],new_bot[n,1], 'o', color=next(colors))
                plt.title('Cropped ordered new_bot of halfdrop (starting from blue)')
                plt.show()
                plt.close()

                plt.plot(new_bot[:,0],new_bot[:,1])
                plt.title('Cropped ordered new_bot of halfdrop (line)')
                plt.show()
                plt.close()

            # order the top 90% so that the y value decreases

            print('Sorting top ',100-(percent*100),'% of the contour by y value...')
            new_top = sorted(list(top), key=lambda x: x[1], reverse=True)
            new_top = np.array(new_top)

            # remove surface by deleting points after the contact point
            xCP_indexs = [i for i, j in enumerate(xbot) if j == xCP]
            #print('xCP_index is: ',xCP_index)
            yCP_indexs = [i for i, j in enumerate(ybot) if j == yCP]
            #print('yCP_index is: ',yCP_index)

            for xCP_index in xCP_indexs:
                for yCP_index in yCP_indexs:
                    if xCP_index == yCP_index:
                        try:
                            if ybot[yCP_index+2] > ybot[yCP_index-1]:
                                new_bot = np.zeros((len(xbot[yCP_index:]),2))
                                for n in range(len(new_bot)):
                                    new_bot[n,[0]] = xbot[xCP_index+n]
                                    new_bot[n,[1]] = ybot[yCP_index+n]
                            else:
                                new_bot = np.zeros((len(xbot[:yCP_index]),2))
                                for n in range(len(new_bot)):
                                    new_bot[n,[0]] = xbot[n]
                                    new_bot[n,[1]] = ybot[n]
                        except:
                            try:
                                if ybot[yCP_index] > ybot[yCP_index-2]:
                                    new_bot = np.zeros((len(xbot[yCP_index:]),2))
                                    for n in range(len(new_bot)):
                                        new_bot[n,[0]] = xbot[xCP_index+n]
                                        new_bot[n,[1]] = ybot[yCP_index+n]
                                else:
                                    new_bot = np.zeros((len(xbot[:yCP_index]),2))
                                    for n in range(len(new_bot)):
                                        new_bot[n,[0]] = xbot[n]
                                        new_bot[n,[1]] = ybot[n]
                            except:
                                print('xCP_indexs are: ', xCP_indexs)
                                print('yCP_indexs are: ', yCP_indexs)
                                raise 'indices of x and y values of the contact point are not the same'
            new_halfdrop = np.concatenate((new_top,new_bot))

        if 0: # order the points so that the baseline can be removed
            # before any ordering is done, chop off the surface line that is past the drop edge
            del_indexes = []
            for index,coord in enumerate(halfdrop):
                if coord[0]>max(xtop):
                    del_indexes.append(index)
            #halfdrop = np.delete(halfdrop,del_indexes)
            xhalfdrop = np.delete(xhalfdrop,del_indexes)
            yhalfdrop = np.delete(yhalfdrop,del_indexes)
            #print('shape of another_halfdrop is: '+ str(type(another_halfdrop)))
            #print('first few points of halfdrop are: ',halfdrop[:3])



            # order half contour points
            xx,yy = sort_to_line(xhalfdrop,yhalfdrop)
            add_top = False
            #print('length of halfdrop is: ', len(halfdrop))
            #print('length of xbottom is: ', len(xbottom))

            #if xx[0]<1: # then graph starts at the top
            surface_past_drop_index = []
            for n,x in enumerate(xx):
                if x>max(xtop):
                    surface_past_drop_index.append(n)
                    #xx = xx[:max(xtop)point]
            #print('indices of contour points past drop: ',surface_past_drop_index)


            # if the sort method will not work
            if len(xx) < len(xhalfdrop): # assumes that the error is on the surface somewhere, so uses bottom of contour
                add_top = True
                print()
                print('sort_to_line is not utilising the full contour, alternate ordering method being used')
                print('check bottom 10% of contour...')
                # this method is much slower than the above, so use as few points as possible
                bot_list = []
                for n in range(len(xbottom)):
                    if xbottom[n]<max(xtop):
                        bot_list.append([xbottom[n],ybottom[n]])
                bot_array = np.array(bot_list)
                new_order, _ = two_opt(bot_array) # 119.8 seconds for 247 points

                xbot,ybot = new_order[:,[0]],new_order[:,[1]]

                if display:
                    plt.plot(xbot,ybot,'b-')
                    plt.title('Bottom of half drop, new order')
                    plt.show()
                    plt.close()

                xCP_index = [i for i, j in enumerate(xbot) if j == xCP]
                #print('xCP_index is: ',xCP_index)
                yCP_index = [i for i, j in enumerate(ybot) if j == yCP]
                #print('yCP_index is: ',yCP_index)

                if 0:
                    new_bot = np.zeros((len(xbot),2))
                    for n in range(len(xx)):
                        new_bot[n,[0]] = xbot[n]
                        new_bot[n,[1]] = ybot[n]
                #xbot[xCP_index[0]:]
                if xCP_index == yCP_index:
                    if ybot[yCP_index[0]+1] > ybot[yCP_index[0]-1]:
                        new_bot = np.zeros((len(xbot[yCP_index[0]:]),2))
                        for n in range(len(new_bot)):
                            new_bot[n,[0]] = xbot[xCP_index[0]+n]
                            new_bot[n,[1]] = ybot[yCP_index[0]+n]
                    else:
                        new_bot = np.zeros((len(xbot[:yCP_index[0]]),2))
                        for n in range(len(new_bot)):
                            new_bot[n,[0]] = xbot[n]
                            new_bot[n,[1]] = ybot[n]
                else:
                    raise 'indices of x and y values of the contact point are not the same'

                # combine new_bot with top_array to give the isolated drop contour without surface
                if 0:
                    top_array = np.zeros((len(xtop),2))
                    for n in range(len(xtop)):
                        top_array[n,[0]] = xtop[n]
                        top_array[n,[1]] = ytop[n]

                new_halfdrop = np.concatenate((top,new_bot))

                # re-order to check that the error was at the surface line
                xx,yy = sort_to_line(new_halfdrop[:,[0]],new_halfdrop[:,[1]])
                if len(xx)<len(new_halfdrop): #then the error was in the top 90% of the drop
                    print('Checking top 90% of contour...')
                    new_top, _ = two_opt(top)
                    new_halfdrop = np.concatenate((new_top,new_bot))
                    xx,yy = sort_to_line(new_halfdrop[:,[0]],new_halfdrop[:,[1]])


            else:  # if sort_to_line worked as expected
                # find the indexs of the contact point and chop off the ends
                xCP_index = [i for i, j in enumerate(xx) if j == xCP]
                #print('xCP_index is: ',xCP_index)
                yCP_index = [i for i, j in enumerate(yy) if j == yCP]
                #print('yCP_index is: ',yCP_index)

                new_halfdrop = np.zeros((len(xx),2))
                for n in range(len(xx)):
                    new_halfdrop[n,[0]]=xx[n]
                    new_halfdrop[n,[1]]=yy[n]
                #print('first 3 points of new_halfdrop are: ',new_halfdrop[:3])
                #print('length of new_halfdrop is: ',len(new_halfdrop))

                if xCP_index == yCP_index:
                    if new_halfdrop[xCP_index[0]+1][1]>new_halfdrop[xCP_index[0]-1][1]:
                        new_halfdrop = new_halfdrop[xCP_index[0]:]
                    else:
                        new_halfdrop = new_halfdrop[:xCP_index[0]+1]
                else:
                    raise_error = True
                    for x in xCP_index:
                        for y in yCP_index:
                            if x==y:
                                raise_error = False
                                xCP_index = [x]
                                yCP_index = [y]
                                #print('indices of the CP are: ',xCP_index[0],', ',yCP_index[0])
                                if new_halfdrop[xCP_index[0]+1][1]>new_halfdrop[xCP_index[0]-1][1]:
                                    new_halfdrop = new_halfdrop[xCP_index[0]:]
                                else:
                                    new_halfdrop = new_halfdrop[:xCP_index[0]+1]
                    if raise_error == True:
                        print('The index of the contact point x value is: ', new_halfdrop[xCP_index])
                        print('The index of the contact point y value is: ', new_halfdrop[yCP_index])
                        raise 'indices of x and y values of the contact point are not the same'

        if counter == 0:
            drops[counter] = new_halfdrop[::-1]
        else:
            drops[counter] = new_halfdrop

        if display: #display
            jet= plt.get_cmap('jet')
            colors = iter(jet(np.linspace(0,1,len(new_halfdrop))))
            for k in new_halfdrop:
                plt.plot(k[0],k[1], 'o',color=next(colors))
            plt.title('outputted halfdrop')
            plt.axis('equal')
            plt.show()
            plt.close()

        counter+=1

    # reflect the left drop and combine left and right

    profile = np.empty((len(drops[0])+len(drops[1]),2))
    for i,n in enumerate(drops[0]):
        flipped = n
        flipped[0] = -flipped[0]
        profile[i] = flipped
    for i,n in enumerate(drops[1]):
        profile[len(drops[0])+i] = n
    CPs[0][0] = -CPs[0][0]

    if display:
        jet= plt.get_cmap('jet')
        colors = iter(jet(np.linspace(0,1,len(profile))))
        for k in profile:
            plt.plot(k[0],k[1], 'o',color=next(colors))
        plt.title('final output')
        #plt.plot(profile[:,0],profile[:,1],'b')
        plt.show()
        plt.close()

        plt.title('final output')
        plt.plot(profile[:,0],profile[:,1],'b')
        plt.show()
        plt.close()

    # flip upside down again so that contour follows image indexing
    # and transform to the right so that x=0 is no longer in line with apex
    for coord in profile:
        coord[1] = -coord[1]
        coord[0] = coord[0] + xapex
    for n in [0,1]:
        CPs[n][1] = -CPs[n][1]
        CPs[n][0] = CPs[n][0] + xapex

    # flip original contour back to original orientation
    for coord in coords:
        coord[1] = -coord[1]

    return profile,CPs

def find_contours(image):
    """
        Calls cv2.findContours() on passed image in a way that is compatible with OpenCV 4.x, 3.x or 2.x
        versions. Passed image is a numpy.array.

        Note, cv2.findContours() will treat non-zero pixels as 1 and zero pixels as 0, so the edges detected will only
        be those on the boundary of pixels with non-zero and zero values.

        Returns a numpy array of the contours in descending arc length order.
    """
    if len(image.shape) > 2:
        raise ValueError('`image` must be a single channel image')

    if CV2_VERSION >= (4, 0, 0):
        # In OpenCV 4.0, cv2.findContours() no longer returns three arguments, it reverts to the same return signature
        # as pre 3.2.0.
        contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
    elif CV2_VERSION >= (3, 2, 0):
        # In OpenCV 3.2, cv2.findContours() does not modify the passed image and instead returns the
        # modified image as the first, of the three, return values.
        _, contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
    else:
        contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)

    # Each contour has shape (n, 1, 2) where 'n' is the number of points. Presumably this is so each
    # point is a size 2 column vector, we don't want this so reshape it to a (n, 2)
    contours = [contour.reshape(contour.shape[0], 2) for contour in contours]

    # Sort the contours by arc length, descending order
    contours.sort(key=lambda c: cv2.arcLength(c, False), reverse=True)

    return contours

def hough_baseline(edges, HoughLinesThreshold=40, vertical_threshold=10, display=False):
    """
    Detect the baseline in an image using the Hough Line Transform.

    Args:
        edges (numpy.ndarray): A binary edge image obtained from an edge detection algorithm like Canny.
        HoughLinesThreshold (int, optional): The threshold value for the Hough Line Transform. Defaults to 40.
        vertical_threshold (int, optional): The maximum allowed deviation from the horizontal (in degrees) for
            a line to be considered non-vertical. Defaults to 10.
        display (bool, optional): Whether to display the detected baseline on the image. Defaults to False.

    Returns:
        list: A list containing the start and end points of the detected baseline, represented as [x1, y1, x2, y2].

    This function performs the following steps:
    1. Applies the Hough Line Transform to the input edge image to detect lines.
    2. Filters out vertical lines based on the specified `vertical_threshold`.
    3. Orders the remaining lines from flattest to highest magnitude gradient.
    4. Selects the flattest line as the baseline.
    5. If `display` is True, it plots the detected baseline on the input image.

    Example:
    An appropriate input can be generated using the following, or something similar
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    otsu_thresh, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    edges = cv2.Canny(otsu_thresh,3,5,apertureSize = 3)

    """

    lines = cv2.HoughLines(edges,1,np.pi/180,HoughLinesThreshold)

    # Filter out vertical lines
    #vertical_threshold = 10 # Adjust this value to control the tolerance
    filtered_lines = []
    if lines is not None: # if the HoughLines function is successful
        for line in lines:
            rho, theta = line[0]
            if abs(theta * 180 / np.pi - 90) < vertical_threshold:
            #if 1:
                filtered_lines.append(line)
    else:
        print('No lines found in image')

    # Take the first non-vertical line
    lines = []
    if filtered_lines:
        for line in filtered_lines:
            rho,theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0)
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - edges.shape[1]*(-b))
            y2 = int(y0 - 1000*(a))
            p1,p2 = [x1,y1],[x2,y2]
            lines.append([p1,p2])

    # to take the best line order the lines from flattest to highest magnitude gradient
    gradients = []
    for i, line in enumerate(lines):
        x1, y1 = line[0]
        x2, y2 = line[1]

        if x1 == x2:  # Vertical line
            gradient = float('inf')
        else:
            gradient = (y2 - y1) / (x2 - x1)
        gradients.append((gradient, line))
    sorted_gradients = sorted(gradients, key=lambda x: abs(x[0]))
    sorted_lines = np.array([line for _, line in sorted_gradients])

    if display:
        print('sorted_lines found by Hough Line: ', sorted_lines)
        plt.imshow(edges)
        for i, line in enumerate(sorted_lines):
            #if line[0,0]==0:
            if 1:
                plt.plot(line[:,0], line[:,1])
        plt.show()
        plt.close()
    return sorted_lines[0]

def hough_circle(edges, display):
    #hough circle to find droplet
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1,
                              minDist=max(edges.shape), #one circle
                              param1=40, #30, 40
                              param2=14, #15, 16
                              minRadius=int(edges.shape[1]*0.05), #0.05
                              maxRadius=0)

    # check if the top of the circle is within 10% of the top of the contour
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        center = (i[0], i[1])
        radius = i[2]
    circle_top = center[1] - radius
    edges_top = np.min(np.where(edges == 255)[0])
    if circle_top < edges_top - edges.shape[0]*0.1:
        circles = None

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

    else:
        #hough circle to find droplet - minRadius at 0
        circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1,
                                  minDist=max(edges.shape), #one circle
                                  param1=30,
                                  param2=20,
                                  minRadius=0,
                                  maxRadius=0)

    # if circle goes past the top of the image then set a maxRadius
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

        if radius > center[1]: # top of circle is out of bounds of image
            circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1,
                                      minDist=max(edges.shape), #one circle
                                      param1=40, #30
                                      param2=15,
                                      minRadius=int(edges.shape[1]*0.10), #0.05
                                      maxRadius=int(edges.shape[1]*0.40))

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

            if display:
                circle1 = plt.Circle(center, 1, color='r')
                # now make a circle with no fill, which is good for hi-lighting key results
                circle2 = plt.Circle(center, radius, color='r', fill=False)

                ax = plt.gca()
                ax.axis('equal')

                ax.add_patch(circle1)
                ax.add_patch(circle2)

                fig = plt.gcf()
                fig.set_size_inches(10, 10)

                plt.imshow(edges)
                plt.title("Hough circle")
                plt.show()
                plt.close()

    return center, radius

def extract_edges_CV(img, threshold_val=None, return_thresholed_value=False, display=False):
    '''
    give the image and return a list of [x.y] coordinates for the detected edges

    '''
    IGNORE_EDGE_MARGIN = 1
    img = img.astype("uint8")
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        gray = img

    if 1:# blur
        blurred = cv2.GaussianBlur(gray, (3, 3), 0) #blur size of 3

        if threshold_val == None:
            #ret, thresh = cv2.threshold(gray,threshValue,255,cv2.THRESH_BINARY)
            ret, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            ret, thresh = cv2.threshold(blurred,threshold_val,255,cv2.THRESH_BINARY)
    else:
        if threshold_val == None:
            #ret, thresh = cv2.threshold(gray,threshValue,255,cv2.THRESH_BINARY)
            ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            ret, thresh = cv2.threshold(gray,threshold_val,255,cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    #contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # Each contour has shape (n, 1, 2) where 'n' is the number of points. Presumably this is so each
    # point is a size 2 column vector, we don't want this so reshape it to a (n, 2)
    contours = [contour.reshape(contour.shape[0], 2) for contour in contours]

    # Sort the contours by arc length, descending order
    contours.sort(key=lambda c: cv2.arcLength(c, False), reverse=True)

    #Assume that the drop is the largest contour
    #drop_profile = contours[0]
    drop_profile = contours[0]

    #Put the drop contour coordinates in order (from ?? to ??)
    #drop_profile = squish_contour(drop_profile)

    # Ignore points of the drop profile near the edges of the drop image
    width, height = img.shape[1::-1]
    if not (width < IGNORE_EDGE_MARGIN or height < IGNORE_EDGE_MARGIN):
        mask = ((IGNORE_EDGE_MARGIN < drop_profile[:, 0]) & (drop_profile[:, 0] < width - IGNORE_EDGE_MARGIN) &
            (IGNORE_EDGE_MARGIN < drop_profile[:, 1]) & (drop_profile[:, 1] < height - IGNORE_EDGE_MARGIN))
        drop_profile = drop_profile[mask]

    output = []
    for coord in drop_profile:
        if list(coord) not in output:
            output.append(list(coord))
    output = np.array(output)

    if return_thresholed_value==True:
        return output, ret
    else:
        return output

def line_circle_intersection(line_point1, line_point2, circle_center, circle_radius):
    import numpy as np

    # Convert inputs to numpy arrays of float64 to prevent integer overflow
    p1 = np.array(line_point1, dtype=np.float64)
    p2 = np.array(line_point2, dtype=np.float64)
    c = np.array(circle_center, dtype=np.float64)
    r = float(circle_radius)  # ensure radius is float

    # Calculate the direction vector of the line
    direction = p2 - p1

    # Calculate the vector from circle center to line start
    f = p1 - c

    # Calculate quadratic equation coefficients
    a = np.dot(direction, direction)
    b = 2 * np.dot(f, direction)
    c = np.dot(f, f) - r**2

    # Calculate the discriminant
    discriminant = b**2 - 4*a*c

    # Check the number of solutions
    if discriminant < 0:
        return []  # No intersection
    elif discriminant == 0:
        t = -b / (2*a)
        return [p1 + t * direction]
    else:
        t1 = (-b + np.sqrt(discriminant)) / (2*a)
        t2 = (-b - np.sqrt(discriminant)) / (2*a)
        coords = np.array([p1 + t1 * direction, p1 + t2 * direction])
        sorted_coords = coords[coords[:, 0].argsort()]
        return sorted_coords


def tilt_correction(img, baseline, user_set_baseline=False):
    """img is an image input
    baseline is defined by two points in the image"""

    p1,p2 = baseline[0],baseline[1]
    x1,y1 = p1
    x2,y2 = p2

    #assert(not x1 == x2 or y1 == y2)
    if y1 == y2: # image is level
        return img

    if user_set_baseline == True:
        img = img[:int(max([y1,y2])), :]

    t = float(y2 - y1) / (x2 - x1)
    rotate_angle = math.degrees(math.atan(t))
    if rotate_angle > 45:
        rotate_angle = -90 + rotate_angle
    elif rotate_angle < -45:
        rotate_angle = 90 + rotate_angle
    rotate_img = ndimage.rotate(img, rotate_angle)
    print('image rotated by '+str(rotate_angle)+' degrees')

    # crop black edges created when rotating
    width = np.sin(np.deg2rad(rotate_angle))
    side = math.ceil(abs(width*rotate_img.shape[1]))
    roof = math.ceil(abs(width*rotate_img.shape[0]))
    rotate_img_crop = rotate_img[roof:-roof,side:-side]

    return rotate_img_crop

def isolate_contour(img_orig, DISPLAY=False):
    """
    Isolate the contour of a drop and its surrounding surface from an input image.

    Args:
        img_orig (numpy.ndarray): The input image containing the drop and surface.
        DISPLAY (bool, optional): Whether to display intermediate results and plots. Defaults to False.

    Returns:
        tuple: A tuple containing two numpy arrays:
            - longest (numpy.ndarray): An array of (x, y) coordinates representing the contour of the drop and surface.
            - drop_only (numpy.ndarray): An array of (x, y) coordinates representing an approximate contour of the drop only.

    This function performs the following steps:
    1. Removes interference from the needle (if present) in the input image.
    2. Extracts edges from the input image using the `extract_edges_CV` function.
    3. Clusters the edges using the `cluster_OPTICS` function and finds the longest contour group.
    4. Attempts to find a surface line (baseline) using the `hough_baseline` function.
    5. If a baseline is found, performs tilt correction on the input image.
    6. Attempts to find a circular drop using the `hough_circle` function.
    7. Displays the identified shapes of interest (baseline and circle) if `DISPLAY` is True.
    8. Crops the image based on the detected baseline and circle, with some padding.
    9. Extracts edges from the cropped image and clusters them using `cluster_OPTICS`.
    10. Determines an approximate contour for the drop only, based on the detected baseline or circle.
    11. If `DISPLAY` is True, plots the contours of the drop and surface, as well as the drop only.
    12. Returns the contours of the drop and surface (`longest`), and the approximate contour of the drop only (`drop_only`).
    """
    ### declare flags
    info = {}
    BASELINE = np.array([[None, None],[None,None]])
    CIRCLE = None

    ### remove interferance from the needle straight away
    ### won't work for high tilt systems, but shouldn't interfere

    # find longest group
    ### find edges
    edges, threshold = extract_edges_CV(img_orig, return_thresholed_value=True)

    groups = cluster_OPTICS(edges, xi=0.8)
    keys = sorted(groups.keys(), key=lambda k: len(groups[k]), reverse=True)
    maxkey=keys[0]
    longest_contour = np.array(groups[maxkey])
    if 0:
        plt.imshow(img_orig)
        plt.plot(longest_contour[:,0],longest_contour[:,1])
        plt.show()
        plt.close()

    # check that the longest contour is not the needle
    # look for contour points which are close together and touch the top of the image
    top_of_image = []
    for coord in longest_contour:
        if coord[1] <= 10:
            maybe_needle = True
            top_of_image.append(coord)
        else:
            maybe_needle = False
    if maybe_needle == True:
        top_of_image = np.array(top_of_image)
        top_of_image = top_of_image[top_of_image[:, 0].argsort()] #order by x coord
        midpoint = top_of_image[0,0] + (top_of_image[-1,0] - top_of_image[0,0])/2
        left_of_midpoint = top_of_image.copy()[top_of_image.copy()[:,0] < midpoint]
        right_of_midpoint = top_of_image.copy()[top_of_image.copy()[:,0] > midpoint]
        left_of_midpoint = left_of_midpoint[left_of_midpoint[:, 0].argsort()][-1][0] #get max x
        right_of_midpoint = right_of_midpoint[right_of_midpoint[:, 0].argsort()][0][0] #get min x
        # if dist between these points is less than 15% of image width, it's probably the needle
        # 5< in case there is a lighting issue that isn't the needle
        if 5 < right_of_midpoint - left_of_midpoint < img_orig.shape[1]*0.10:
            maxkey = keys[1]
            longest_contour = np.array(groups[maxkey])

    if DISPLAY:
        plt.title('image with longest found contour that is not the needle')
        plt.imshow(img_orig)
        #plt.plot(edges[:,0],edges[:,1])
        plt.plot(longest_contour[:,0],longest_contour[:,1], '.')
        plt.axis('equal')
        plt.show()
        plt.close()

    # convert edges to img shape for hough transform input
    canny_input = np.zeros((img_orig.shape[0],img_orig.shape[1]), dtype=np.uint8)
    for x,y in longest_contour:
        canny_input[y, x] = 255 #y,x because image coordinates

    if DISPLAY:
        plt.title('canny input')
        plt.imshow(canny_input)
        plt.axis('equal')
        plt.show()
        plt.close()

    ### Try find a surface line
    try:
        hough_line = np.array(hough_baseline(canny_input, 20, display=False))
        if 0:
            print('Hough lines found: ',hough_line)
            plt.title('Hough baseline before tilt')
            plt.imshow(img_orig)
            plt.plot(hough_line[:,0], hough_line[:,1],'r')
            plt.show()
            plt.close()
        if min(hough_line[:,1]) <= min(longest_contour[:,1]): # check that line isn't just the drop of a flat drop
            hough_line = 0 #this will break the try loop
        elif hough_line[1,1] - hough_line[0,1] <=1:
            #sometimes hough line will give slight gradient when there isn't any
            img = img_orig
        else:
            img = tilt_correction(img_orig, hough_line)

        #refind canny_input
        edges = extract_edges_CV(img)
        groups = cluster_OPTICS(edges, xi=0.8)
        longest_contour = np.array(groups[maxkey])
        canny_input = np.zeros((img_orig.shape[0],img_orig.shape[1]), dtype=np.uint8)
        for x,y in longest_contour:
            canny_input[y, x] = 255 #y,x because image coordinates

        hough_line = hough_baseline(canny_input, display=False)
        BASELINE = np.array(hough_line)
        if DISPLAY:
            plt.title('Hough baseline after tilt')
            plt.imshow(img)
            plt.plot(BASELINE[:,0], BASELINE[:,1],'r')
            plt.axis('equal')
            plt.show()
            plt.close()
    except:
        img = img_orig
        print('No surface line could be found')

    ### Try find a roughly circular drop
    try:
        CIRCLE = hough_circle(canny_input, False)
    except:
        print('Hough circle failed to identify a drop')

    if DISPLAY:
        plt.title('Identified shapes of interest')
        plt.imshow(img)
        try:
            center, radius = CIRCLE
            circle1 = plt.Circle(center, 1, color='r')
            # now make a circle with no fill, which is good for hi-lighting key results
            circle2 = plt.Circle(center, radius, color='r', fill=False)

            ax = plt.gca()
            ax.axis('equal')

            ax.add_patch(circle1)
            ax.add_patch(circle2)

            fig = plt.gcf()
            fig.set_size_inches(10, 10)
        except:
            pass
        try:
            plt.plot(BASELINE[:,0], BASELINE[:,1],'r')
        except:
            pass
        plt.axis('equal')
        plt.show()
        plt.close()

    ### crop the image accordingly
    padding = 0.05
    if CIRCLE != None and BASELINE.any() != None: # both found
        center, radius = CIRCLE
        top = int(center[1] - radius - img.shape[0]*padding)
        bottom = int(max(BASELINE[:,1]) + img.shape[0]*padding)
    elif CIRCLE != None: # circle found but no line found - assume level surface
        center, radius = CIRCLE
        top = int(center[1] - radius - img.shape[0]*padding*1.5)
        bottom = int(center[1] + radius + img.shape[0]*padding*1.5)
    elif BASELINE.any() != None: # line found but no circle - assume low CA drop
        top = min(longest_contour[:,1])
        bottom = int(max(BASELINE[:,1]) + img.shape[0]*padding)
    else: # neither found
        top = 0
        bottom = img.shape[0]

    ### make sure the found bounds don't exceed the original image bounds
    if top < 0:
        top = 0
    if bottom > img.shape[0]:
        bottom = img.shape[0]

    img_processed = img.copy()

    ### group contour
    #edges = model_pred.extract_edges_CV(img_processed[top:bottom,])
    #groups = model_pred.cluster_OPTICS(edges, xi=0.8)
    #maxkey=max(groups, key=lambda k: len(groups[k]))
    #longest_contour = np.array(groups[maxkey])

    ### convert contours back to full image coordinates
    #longest_contour[:,1] += top

    ### determine an approximate 'drop only' contour
    if CIRCLE != None and BASELINE.any() != None: #set bounds using both the found circle and a line
        lowest_point = max(BASELINE[:,1])
        intersections = line_circle_intersection(BASELINE[0], BASELINE[1], center, radius)
        if len(intersections)==0:
            # if no intersect, ignore the baseline
            print('intersects not found')
            BASELINE = np.array([[None, None],[None,None]])

    if BASELINE.any() != None:
        div_line = min(BASELINE[:,1]) - (min(BASELINE[:,1]) - min(longest_contour[:,1]))*0.2
    elif CIRCLE != None:
        div_line = center[1] + radius/2
    else:
        #neither found use the top 50%
        div_line = min(longest_contour[:,1]) + (max(longest_contour[:,1]) - min(longest_contour[:,1]))*0.5

    drop_only = np.array([[x, y] for x, y in longest_contour if y < div_line])

    ### now that the drop region has been roughly identified, repeat the edge detection over this cropped region
    ### doing this will result in a more accurate threshold value being selected, giving an more accurate edge

    if CIRCLE != None and BASELINE.any() != None: #set bounds using both the found circle and a line
        lowest_point = max(BASELINE[:,1])
        #intersections = line_circle_intersection(BASELINE[0], BASELINE[1], center, radius)
        x1, y1 = intersections[0]
        x2, y2 = intersections[1]
        midpoint = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
        if center[1] < midpoint[1] - radius*0.4: # high angle system, slight bias for consistency
            try: # account for Hough circle inaccuracy
                right_of_center = []
                left_of_center = []
                for coord in longest_contour:
                    if coord[1] == center[1] and coord[0] > center[0]:
                        right_of_center.append(coord)
                    if coord[1] == center[1] and coord[0] < center[0]:
                        left_of_center.append(coord)
                right_of_center = np.array(right_of_center)
                left_of_center = np.array(left_of_center)
                if len(right_of_center) >= 1 and len(left_of_center) >= 1:
                    right_of_center = right_of_center[right_of_center[:, 0].argsort()][0] #min x coord
                    left_of_center = left_of_center[left_of_center[:, 0].argsort()][-1] #max x coord
                    right_dist = abs(center[0] - right_of_center[0])
                    left_dist = abs(center[0] - left_of_center[0])
                    radius = max([left_dist, right_dist])
            except:
                pass
            bounds_temp = [int(center[1] - radius*1.2), #top, 20% padding
                           int(lowest_point + (lowest_point - center[1] + radius)*0.4), #bottom
                           int(center[0] - radius*1.2), #left
                           int(center[0] + radius*1.2)] #right
        else: # low angle system?
            # guess the CPs as the points closest to each circle/line intersect
            left_guess = min(longest_contour, key=lambda x: distance1(intersections[0], x))
            right_guess = min(longest_contour, key=lambda x: distance1(intersections[1], x))
            width = round(distance1(left_guess, right_guess))

            bounds_temp = [int(center[1] - radius*1.2), #top, 20% padding
                           int(lowest_point + (lowest_point - center[1] + radius)*0.4), #bottom
                           int(center[0] - width/2*1.5), #left
                           int(center[0] + width/2*1.5)] #right
    elif CIRCLE != None:
        bounds_temp = [int(center[1] - radius*1.2), #20% padding
                       int(center[1] + radius*1.2),
                       int(center[0] - radius*1.5), # for high bond number systems (Bo=1)
                       int(center[0] + radius*1.5)] # for high bond number systems (Bo=1)
    else:
        height = max(longest_contour[:,1]) - min(longest_contour[:,1])
        width = max(drop_only[:,0]) - min(drop_only[:,0])
        bounds_temp = [int(min(longest_contour[:,1]) - height*0.4),
                       int(max(longest_contour[:,1]) + height*0.4),
                       int(min(drop_only[:,0]) - width*0.4),
                       int(max(drop_only[:,0]) + width*0.4)]

    ### keep to img bounds
    if bounds_temp[0] < 0:
        bounds_temp[0] = 0
    if bounds_temp[1] > img_processed.shape[0]:
        bounds_temp[1] = img_processed.shape[0]
    if bounds_temp[2] < 0:
        bounds_temp[2] = 0
    if bounds_temp[3] > img_processed.shape[1]:
        bounds_temp[3] = img_processed.shape[1]

    img_crop = img_processed[bounds_temp[0]:bounds_temp[1],bounds_temp[2]:bounds_temp[3]]

    gray = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if DISPLAY:
        print('cropped threshold value: ', ret)
        plt.title('drop region')
        plt.imshow(thresh)
        plt.show()
        plt.close()
    edges = extract_edges_CV(img_orig, ret) #edges = extract_edges_CV(img_crop, ret)

    # mask contour to identified drop region
    x_mask = (edges[:, 0] >= bounds_temp[2]) & (edges[:, 0] <= bounds_temp[3])
    y_mask = (edges[:, 1] >= bounds_temp[0]) & (edges[:, 1] <= bounds_temp[1])
    mask = x_mask & y_mask

    # Apply the mask to get the filtered coordinates
    filtered_coords = edges[mask]
    groups = cluster_OPTICS(filtered_coords, eps=2) #xi=0.8
    maxkey=max(groups, key=lambda k: len(groups[k]))
    filtered_coords = np.array(groups[maxkey])

    div_line = min(filtered_coords[:,1]) + (max(filtered_coords[:,1]) - min(filtered_coords[:,1]))*0.5
    drop_only = np.array([[x, y] for x, y in filtered_coords if y < div_line])

    if DISPLAY:
        plt.imshow(img_processed)
        plt.plot(filtered_coords[:,0],filtered_coords[:,1],'r,')
        plt.plot(drop_only[:,0],drop_only[:,1], 'b.')
        plt.show()
        plt.close()

    info['line'] = BASELINE
    info['circle'] = CIRCLE
    info['bounds'] = bounds_temp
    info['threshold'] = threshold

    return img_processed, filtered_coords, drop_only, info

def linear_fit(coords, display=False):
    """
    Fit a line to an array of coordinates using Orthogonal Distance Regression (ODR).
    This method correctly fits vertical lines if needed.

    Args:
        coords (list): A list of (x, y) coordinate tuples.
        display (bool): If True, displays the contour, fitted line, and RMSE.

    Returns:
        tuple: A tuple containing the slope (m), intercept (c), and RMSE value.
    """
    x_coords, y_coords = np.array(coords).T

    if np.std(x_coords) < 1e-6:  # Detect vertical line
        return np.inf, np.mean(x_coords), 0  # Slope = infinity, Intercept = mean x

    # Define linear function for ODR
    def linear_func(beta, x):
        return beta[0] * x + beta[1]

    # Use initial guess from OLS (to handle non-vertical cases well)
    A = np.vstack([x_coords, np.ones_like(x_coords)]).T
    m_init, c_init = np.linalg.lstsq(A, y_coords, rcond=None)[0]

    # Fit using ODR
    model = Model(linear_func)
    data = Data(x_coords, y_coords)
    odr = ODR(data, model, beta0=[m_init, c_init])
    out = odr.run()

    m, c = out.beta  # Best-fit parameters

    # Calculate RMSE using perpendicular distances
    distances = np.abs(y_coords - (m * x_coords + c)) / np.sqrt(1 + m ** 2)
    rmse_value = np.sqrt(np.mean(distances**2))

    # Display the plot if required
    if display:
        plt.scatter(x_coords, y_coords, color='blue', label='Data Points')

        # Plot fitted line
        x_line = np.linspace(min(x_coords), max(x_coords), 100)
        y_line = m * x_line + c
        plt.plot(x_line, y_line, color='red', label=f'Fitted Line: y = {m:.2f}x + {c:.2f}')

        # Display the equation and RMSE
        plt.text(0.05, 0.95, f'Slope: {m:.2f}\nIntercept: {c:.2f}\nRMSE: {rmse_value:.2f}',
                 transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', alpha=0.5))

        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('ODR Linear Fit')
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.gca().invert_yaxis()
        plt.legend()
        plt.show()

    return m, c, rmse_value

def linear_fit_ols(coords, display=False):
    """
    Fit a line to an array of coordinates using the least squares method.
    Optionally displays the fitted line and contour points.

    Args:
        coords (list): A list of (x, y) coordinate tuples.
        display (bool): If True, displays the contour, fitted line, line equation, and RMSE.

    Returns:
        tuple: A tuple containing the slope (m), intercept (c), and RMSE value.
    """
    x_sum = 0
    y_sum = 0
    xy_sum = 0
    x_squared_sum = 0
    n = len(coords)

    # Calculate the sum of x, y, xy, and x^2
    for x, y in coords:
        x_sum += x
        y_sum += y
        xy_sum += x * y
        x_squared_sum += x ** 2

    # Compute denominator to check for vertical line
    denominator = n * x_squared_sum - x_sum ** 2

    if denominator == 0:  # Vertical line case
        x_value = x_sum / n  # All x values are (approximately) the same
        rmse_value = np.sqrt(np.mean([(x - x_value) ** 2 for x, y in coords]))  # RMSE based on x deviation
        return np.inf, x_value, rmse_value

    # Calculate the slope and intercept using the least squares method
    m = (n * xy_sum - x_sum * y_sum) / denominator
    c = (y_sum - m * x_sum) / n

    # Calculate the RMSE
    total_error = 0
    for x, y in coords:
        # Calculate the normal error (shortest distance from point to line)
        numerator = abs(y - m * x - c)
        denominator = np.sqrt(1 + m ** 2)
        normal_error = numerator / denominator
        total_error += normal_error ** 2

    rmse_value = np.sqrt(total_error / n)

    # Display the plot if required
    if display:
        # Plot the contour points
        x_coords, y_coords = zip(*coords)
        plt.scatter(x_coords, y_coords, color='blue', label='Contour Points')

        # Plot the fitted line
        x_line = np.array([min(x_coords), max(x_coords)])
        y_line = m * x_line + c
        plt.plot(x_line, y_line, color='red', label=f'Fitted Line: y = {m:.2f}x + {c:.2f}')

        # Display the line equation and RMSE on the plot
        plt.text(0.05, 0.95, f'Slope: {m:.2f}\nIntercept: {c:.2f}\nRMSE: {rmse_value:.2f}',
                 transform=plt.gca().transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', alpha=0.5))

        # Set axis limits to fit the data tightly
        plt.xlim(min(x_coords) - 10, max(x_coords) + 10)
        plt.ylim(min(y_coords) - 10, max(y_coords) + 10)

        # Add labels and legend
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Contour and Fitted Line')
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.gca().invert_yaxis()
        plt.legend()

        # Display the plot
        plt.show()

    return m, c, rmse_value

def check_RMSE_gap(previous_same,previous_gap,following_same,following_gap):
    if previous_same and following_same:
        return True
    if previous_same and following_gap:
        return True
    if previous_gap and following_same:
        return True
    if previous_gap and following_gap:
        return True
    else:
        return False

def remove_close_values(values, threshold=10):
    """
    Remove values from a list if they are within a specified threshold of the previous kept value.

    This function iterates through the input list and keeps values that are more than
    the specified threshold away from the last kept value. It always keeps the first
    value in the list.

    Args:
        values (list): A list of numeric values to process.
        threshold (float, optional): The minimum distance between kept values.
                                     Defaults to 10.

    Returns:
        list: A new list with values removed if they are within the threshold
              of the previous kept value.

    Example:
        >>> original_list = [1, 5, 15, 20, 25, 30, 45, 50, 55, 70, 80, 85]
        >>> remove_close_values(original_list)
        [1, 15, 25, 45, 55, 70, 85]
        >>> remove_close_values(original_list, threshold=20)
        [1, 25, 45, 70]
    """
    if not values:
        return []

    result = [values[0]]  # Always keep the first value

    for i in range(1, len(values)):
        if abs(values[i] - result[-1]) > threshold:
            result.append(values[i])

    return result

def find_CP_static_Lfit(contour, drop_len, percentage=2.5, height=0, prominence=0, width=3, display=False):
    """Takes the contour of an contact angle experimental image, and returns the
    coordinates of the contact points. These point is found by tracking the gradient
    of lines fitted to every n_pts coordinates change along the contour.
    contour - a list or numpy array of coordinates of one half of the image, this is
        assumed to include the needle.
    n_pts - the gradient is calculated between coordinate i and coordinate i+n_pts
    gradient_lower_bound and gradient_upper_bound are used to identify points of gradient
        change
    height - used to find signal peak in graph of RMSE. Specifies the minimum height
        (vertical distance from the base) that a peak must have to be considered a
        valid peak. Must be a non-negative value.
    prominence - used to find signal peak in graph of RMSE. Specifies the minimum
        vertical distance that a peak must have from its surrounding data (i.e., the
        closest higher peak) to be considered a valid peak. Must be a non-negative value.
    width - used to find signal peak in graph of RMSE. Specifies the minimum width (in
        number of data points) that a peak must have to be considered a valid peak. Must
        be a positive integer, 1 means no width requirement.
    display - set to True to visualise progress
    Note that the point where the drop meets the needle is a point of gradient change
        and so this point is not returned.
    The points which this function identifies are the points of low gradient which occur
        after large changes in gradient - this can be visualised by setting display
        to True
    """

    n_pts = int(drop_len*percentage/100)
    print(f'n_pts could be int(drop_len*percentage/100): {int(drop_len*percentage/100)}')
    if n_pts < 10:
        n_pts = 10
    print(f'iterative fit approach using {n_pts} points')

    # define output variables
    CPs_output = []

    # determine drop_guess using n_pts between widest points
    if len(contour) >= 110:
        # find drop apex and split into left and right sides
        divline = int(min(contour[:,1])+(max(contour[:,1] - min(contour[:,1])*0.2)))

        top = np.array([[x, y] for x, y in contour if y <= divline])
        #bottom = np.array([[x, y] for x, y in contour if y < divline])
        apex = np.array([[x, y] for x, y in top if y == min(top[:,1])])
        xapex = min(apex[:,0]) + (max(apex[:,0]) - min(apex[:,0]))/2

        left = np.array([[x, y] for x, y in contour if x <= xapex])
        right = np.array([[x, y] for x, y in contour if x > xapex])
    elif len(contour) == 2:
        left = contour[0]
        right = contour[1]
    else:
        print(f'Number of contours is not correct for find_CP_static_Lft, contour.shape[0] == {contour.shape[0]}')
        print('Taking first 2 contours')

    contours = [left,right]

    for side, contour in enumerate(contours):
        if type(contour) != list:
            contour = contour.tolist()
        # order the contour
        if side == 0:
            top_down = sorted(contour[::-1], key=lambda x: x[1])
        else:
            top_down = sorted(contour, key=lambda x: x[1])
        contour = optimized_path(top_down,start=top_down[0])

        if display:
            jet= plt.get_cmap('jet')
            colors = iter(jet(np.linspace(0,1,len(contour))))
            for n,coord in enumerate(contour):
                plt.plot(contour[n,0],contour[n,1], 'o', color=next(colors))
            plt.title('ordered points, starting from blue')
            plt.axis('equal')
            plt.show()
            plt.close()

        # perform iterative linear fits
        gradients = []
        RMSEs = []
        for i, coord in enumerate(contour):
            if i < len(contour) - n_pts:
                m, c, rmse = linear_fit(contour[i:i+n_pts])
                gradients.append(m)
                RMSEs.append(rmse)

        # set the gradient of vertical lines to be the same as the previous point
        for i,m in enumerate(gradients):
            if str(m)=='inf' or str(m)=='-inf':
                gradients[i] = gradients[i-1]

        ### return the indices of each RMSE peak
        #RMSE_peaks_indices = signal.find_peaks(RMSEs, height=max(RMSEs)*0.3, prominence=0.5, width=5)[0] # height was 1
        #RMSE_peaks_indices = signal.find_peaks(RMSEs, height=max(RMSEs)*0.2, prominence=0.3, width=5)[0] # height was 1
        RMSE_peaks_indices = signal.find_peaks(RMSEs, height=max(RMSEs)*0.3, prominence=0.3, width=5)[0]
        RMSE_peaks_indices = sorted(RMSE_peaks_indices.tolist())
        if display == True:
            print('found indices using signal.find_peaks: ',RMSE_peaks_indices)
            if len(RMSE_peaks_indices) == 0:
                print('No peaks found in RMSE plot')

        # return the index of the max RMSE point, often this is missed by the signal package - so add it manually
        #if len(RMSE_peaks_indices)==0:
        max_RMSE_idx = RMSEs.index(np.nanmax(RMSEs))
        if max_RMSE_idx not in RMSE_peaks_indices:
            RMSE_peaks_indices.append(max_RMSE_idx)
        RMSE_peaks_indices = sorted(RMSE_peaks_indices)

        # if using regularly - check that max RMSE isn't right next to an already identified point
        #for idx in RMSE_peaks_indices:
        #    if idx == max_RMSE_idx:
        #        pass
        #    elif abs(max_RMSE_idx - idx) < n_pts*1.2: # if max RMSE index is within n_pts many points of another already found peak
                #RMSE_peaks_indices.append(max_RMSE_idx)
                #if idx in RMSE_peaks_indices:
        #        RMSE_peaks_indices.remove(idx) # remove the close one found by signal in favour of the one with the higher RMSE

        if 0:
            plt.title('initial RMSEs and those flagged')
            # show found indicies
            for i, RMSE in enumerate(RMSEs):
                plt.plot(i,RMSE, 'bo')
            for index in RMSE_peaks_indices:
                plt.plot(index, RMSEs[index], 'rx')
            plt.xlabel('index')
            plt.ylabel('RMSE')
            plt.show()
            plt.close()



        # include index of points where the gradient is near zero and changes sign - to catch reflections
        threshold = (max(gradients) - min(gradients))*0.3 # was 0.1
        sign_changes = np.where(abs(np.diff(np.sign(gradients)))>=1)[0]
        near_zero_indices = np.where(np.abs(gradients) < threshold)[0]
        gradient_change_indices = [val for val in near_zero_indices if val in sign_changes]

        # put indices of gradient change and high RMSE together into a list
        #indices = sorted(RMSE_peaks_indices + gradient_change_indices)
        indices = gradient_change_indices + RMSE_peaks_indices[::-1] # order this way to leave the most likely index last

        # check that the sign change index isn't next to an already identified point
        # if using this would need to fix it
        #for idx in RMSE_peaks_indices:
        #    for new in indices:
        #        if abs(idx - new) < n_pts*1.2 and new < idx:
        #            RMSE_peaks_indices.append(new)
        #            if idx in RMSE_peaks_indices:
        #                RMSE_peaks_indices.remove(idx) # remove the RMSE point in favout or the gradient change point

        # remove any duplicates
        indices = list(set(indices))

        if display == True:
            print('found indices using RMSE peaks and points of gradient change: ',sorted(indices))

        # remove any points that are right next to each other
        #indices = remove_close_values(indices, int(len(contour)*0.01))
        # remove any points that are right next to each other, choose the gradient change point

        # don't use the first or last points
        indices = [idx for idx in indices if idx != 0 and idx != len(RMSEs)-1]
        # don't use points at the very start of the curve
        indices = [idx for idx in indices if idx >= 3*n_pts]
        # don't use points where the RMSE immediately before or after is 0 - this might just be where the line is verical
        indices = [index for index in indices if RMSEs[index - 1] != 0 and RMSEs[index + 1] != 0]

        # set variables for exclusion search
        RMSE_h = max(RMSEs) - min(RMSEs)
        gradient_h = max(gradients) - min(gradients)
        #print('INDEX: ',idx)
        RMSE_jump_too_high = 0.2 #0.15
        RMSE_tolerance = 0.2 #was 0.15, 0.5
        gradient_tolerance = 0.12 # was 0.1
        floor_tolerance = 0.01 # to ignore points right on next to each other on plots

        indices.sort()
        # Filter out indices with too high RMSE jumps
        indices = [idx for idx in indices if len(indices) <= 1 or
                   (abs(RMSEs[idx] - RMSEs[idx-1]) <= RMSE_h*RMSE_jump_too_high and
                    abs(RMSEs[idx] - RMSEs[idx+1]) <= RMSE_h*RMSE_jump_too_high)]
        # print (but would need to define some new variable names for indices)
        #for idx in sorted(list(set(indices) - set(new_indices))):
            #print(f'Removing index {idx} due to RMSE jump of {RMSE_jump_too_high}')

        # remove points where the RMSE jump is way too high and it must be an error
        #for idx in sorted(indices):
        #    previous = idx - 1
        #    following = idx + 1
        #    if len(indices) > 1:
        #        if abs(RMSEs[idx] - RMSEs[previous]) > RMSE_h*RMSE_jump_too_high or abs(RMSEs[idx] - RMSEs[following]) > RMSE_h*RMSE_jump_too_high:
        #        #if abs(RMSEs[idx] - RMSEs[previous]) > RMSE_h*RMSE_jump_too_high and abs(RMSEs[idx] - RMSEs[following]) > RMSE_h*RMSE_jump_too_high:
        #            print(f'Removing index {idx} due to RMSE jump of {RMSE_jump_too_high}')
        #            indices.remove(idx)

        #indices = indices[::-1]
        print('indices before comparing RMSEs and gradients: ', sorted(indices))
        # remove points with big jumps in RMSE but slow changing gradient (round edges of high angle drops)
        if 0:
            for idx in indices:
                previous = idx - 1
                following = idx + 1

                print()
                print(f'running idx: {idx}, RMSE of {RMSEs[idx]}, gradient of {gradients[idx]}')
                print('RMSE_tolerance: ', RMSE_tolerance)
                print('abs(RMSEs[idx] - RMSEs[previous]) : ', abs(RMSEs[idx] - RMSEs[previous])/RMSE_h)
                print('abs(RMSEs[idx] - RMSEs[following]) : ', abs(RMSEs[idx] - RMSEs[following])/RMSE_h)
                #print('using: ', idx[previous:following])
                print('RMSE gap:', check_RMSE_gap(RMSE_h*floor_tolerance > abs(RMSEs[idx] - RMSEs[previous]),
                                    abs(RMSEs[idx] - RMSEs[previous]) > RMSE_h*RMSE_tolerance,
                                    RMSE_h*floor_tolerance > abs(RMSEs[idx] - RMSEs[following]),
                                    abs(RMSEs[idx] - RMSEs[following]) > RMSE_h*RMSE_tolerance
                                    ))

                print('previous_same: ',RMSE_h*floor_tolerance > abs(RMSEs[idx] - RMSEs[previous]))
                print('previous_gap: ',abs(RMSEs[idx] - RMSEs[previous]) > RMSE_h*RMSE_tolerance)
                print('following_same: ',RMSE_h*floor_tolerance > abs(RMSEs[idx] - RMSEs[following]))
                print('following_gap: ',abs(RMSEs[idx] - RMSEs[following]) > RMSE_h*RMSE_tolerance)

                if check_RMSE_gap(RMSE_h*floor_tolerance > abs(RMSEs[idx] - RMSEs[previous]),
                                    abs(RMSEs[idx] - RMSEs[previous]) > RMSE_h*RMSE_tolerance,
                                    RMSE_h*floor_tolerance > abs(RMSEs[idx] - RMSEs[following]),
                                    abs(RMSEs[idx] - RMSEs[following]) > RMSE_h*RMSE_tolerance
                                    ):
                #if (RMSE_h*floor_tolerance > abs(RMSEs[idx] - RMSEs[previous]) or RMSE_h*floor_tolerance > abs(RMSEs[idx] - RMSEs[previous]) > RMSE_h*RMSE_tolerance)
                #and
                #(RMSE_h*floor_tolerance > abs(RMSEs[idx] - RMSEs[following]) or RMSE_h*floor_tolerance > abs(RMSEs[idx] - RMSEs[following]) > RMSE_h*RMSE_tolerance): #0.3
                    print('RMSE GAP')
                    print('gradient difference with previous (% of gradient height): ', abs(gradients[idx] - gradients[previous])/gradient_h)
                    print('gradient difference with following (% of gradient height): ', abs(gradients[idx] - gradients[following])/gradient_h)
                    if abs(gradients[idx] - gradients[previous]) < gradient_h*gradient_tolerance and abs(gradients[idx] - gradients[following]) < gradient_h*gradient_tolerance: # >
                        print('NO GRADIENT GAP - removing unless only peak found')
                        if len(indices)>1: #don't remove if only one point in the list
                            indices.remove(idx)
            if display == True:
                print('found indices after removing large RMSE jumps with small gradient jumps: ',sorted(indices))

        # take out any indices near the drop apex (first 15% of drop contour points)
        indices = [value for value in indices if value > drop_len*0.15]

        # remove any points that are now out of range of the length of the contour
        indices = [idx for idx in indices if idx <= len(gradients)]

        #peak_gradients = [gradients[int(idx - n_pts/2)] for idx in indices]
        peak_gradients = [gradients[idx] for idx in indices]

        # take out any indices for points higher than the 60% contour height
        div_line = min(contour[:,1]) + (max(contour[:,1]) - min(contour[:,1]))*0.4
        # take out any indices for points higher than the 40% contour height
        #div_line = min(contour[:,1]) + (max(contour[:,1]) - min(contour[:,1]))*0.6
        indices = [idx for idx in indices if contour[idx,1] >= div_line]

        # now order lowest to highest
        indices = sorted(indices)

        # if none left use the max RMSE
        if len(indices) < 1:
            indices.append(max_RMSE_idx)

        if display:
            print()
            #print('peak_gradients: ', peak_gradients)
            #print('RMSE peaks found: ', RMSE_peaks_indices)
            print('indices of interest found: ',indices)

            plt.title('plot of fit RMSEs')
            plt.plot(range(len(RMSEs)), RMSEs,'.')
            h = max(RMSEs) - min(RMSEs)
            w = len(RMSEs)
            for i, idx in enumerate(indices):
                #if idx in RMSE_peaks_indices:
                if i==0:
                    plt.plot(idx,RMSEs[idx],'r+')
                else:
                    plt.plot(idx,RMSEs[idx],'+', color='pink')
                label = f"({idx:.2f}, {RMSEs[idx]:.2f})"
                plt.annotate(label, xy=(idx, RMSEs[idx]), xytext=(idx + w*0.1, RMSEs[idx] - h*0.1), textcoords="data", arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
            plt.xlabel('coordinate index')
            plt.ylabel('RMSE')
            plt.show()
            plt.close()

            plt.title('plot of gradients')
            plt.plot(range(len(gradients)), gradients,'.')
            #for idx in RMSE_peaks_indices:
            for i,idx in enumerate(indices):
                #if idx in gradient_change_indices:
                if i==0:
                    plt.plot(idx,gradients[idx],'r+')
                else:
                    plt.plot(idx,gradients[idx],'+', color='pink')
                label = f"({idx:.2f}, {gradients[idx]:.2f})"
                plt.annotate(label, xy=(idx, gradients[idx]), xytext=(idx + w*0.1, gradients[idx] - h*0.1), textcoords="data", arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))

            plt.xlabel('coordinate index')
            plt.ylabel('gradient')
            plt.show()
            plt.close()



        # the first idx of the line is not always where the contact point would be, it would be in the middle of the line, correct for this
        #for idx in indices:
        #    if idx not in gradient_change_indices: #only identified as gradient change
        #        indices.append(idx)
        #    else:
        #        indices.append(idx + round(n_pts/2)) # other ones, i.e. identified for RMSE

        CP_indices = []
        for idx in indices:
            CP_indices.append(idx + round(n_pts/2))


        if display:
            print('index of identified points of interest: ',CP_indices)
            #print('final corrected list contact points:\n',np.array([contour[idx] for idx in CP_indices]))
            plt.title('Points of interest')
            plt.plot(contour[:,0],contour[:,1],',')
            h = max(contour[:,1]) - min(contour[:,1])
            w = len(contour[:,0])
            for i, idx in enumerate(CP_indices):
                if i==0:
                    plt.plot(contour[idx,0],contour[idx,1],'r+')
                    label = f"({contour[idx,0]:.2f}, {contour[idx,1]:.2f})"
                    plt.annotate(label, xy=(contour[idx,0],contour[idx,1]), xytext=(contour[idx,0], contour[idx,1] + 100), textcoords="data", arrowprops=dict(arrowstyle="->", connectionstyle="arc3")) #h*0.05
                else:
                    plt.plot(contour[idx,0],contour[idx,1],'r+')
            plt.plot(contour[:n_pts,0],contour[:n_pts,1], 'g.')
            plt.gca().invert_yaxis()
            plt.axis('equal')
            plt.show()
            plt.close()


        CPs_output.append(contour[CP_indices].tolist())

    return CPs_output

def iterative_Lfit(contour, n_pts, height=0, prominence=0, width=3, display=False):
    """Takes the contour of an contact angle experimental image, and returns the
    coordinates of the contact points. These point is found by tracking the gradient
    of lines fitted to every n_pts coordinates change along the contour.
    contour - a list or numpy array of coordinates of one half of the image, this is
        assumed to include the needle.
    n_pts - the gradient is calculated between coordinate i and coordinate i+n_pts
    height - used to find signal peak in graph of RMSE. Specifies the minimum height
        (vertical distance from the base) that a peak must have to be considered a
        valid peak. Must be a non-negative value.
    prominence - used to find signal peak in graph of RMSE. Specifies the minimum
        vertical distance that a peak must have from its surrounding data (i.e., the
        closest higher peak) to be considered a valid peak. Must be a non-negative value.
    width - used to find signal peak in graph of RMSE. Specifies the minimum width (in
        number of data points) that a peak must have to be considered a valid peak. Must
        be a positive integer, 1 means no width requirement.
    display - set to True to visualise progress
    Note that the point where the drop meets the needle is a point of gradient change
        and so this point is not returned.
    The points which this function identifies are the points of low gradient which occur
        after large changes in gradient - this can be visualised by setting display
        to True
    """

    if n_pts < 12:
        n_pts = 12
    print(f'iterative fit approach using {n_pts} points')

    # define output variables
    CPs_output = []

    # determine drop_guess using n_pts between widest points
    if len(contour) >= 110:
        # find drop apex and split into left and right sides
        divline = int(min(contour[:,1])+(max(contour[:,1] - min(contour[:,1])*0.2)))

        top = np.array([[x, y] for x, y in contour if y <= divline])
        #bottom = np.array([[x, y] for x, y in contour if y < divline])
        apex = np.array([[x, y] for x, y in top if y == min(top[:,1])])
        xapex = min(apex[:,0]) + (max(apex[:,0]) - min(apex[:,0]))/2

        left = np.array([[x, y] for x, y in contour if x <= xapex])
        right = np.array([[x, y] for x, y in contour if x > xapex])
    elif len(contour) == 2:
        left = contour[0]
        right = contour[1]
    else:
        print(f'Number of contours is not correct for find_CP_static_Lft, contour.shape[0] == {contour.shape[0]}')
        print('Taking first 2 contours')

    contours = [left,right]

    for side, contour in enumerate(contours):
        if type(contour) != list:
            contour = contour.tolist()
        # order the contour
        if side == 0:
            top_down = sorted(contour[::-1], key=lambda x: x[1])
        else:
            top_down = sorted(contour, key=lambda x: x[1])
        contour = optimized_path(top_down,start=top_down[0])

        if display:
            jet= plt.get_cmap('jet')
            colors = iter(jet(np.linspace(0,1,len(contour))))
            for n,coord in enumerate(contour):
                plt.plot(contour[n,0],contour[n,1], 'o', color=next(colors))
            plt.title('ordered points, starting from blue')
            plt.axis('equal')
            plt.show()
            plt.close()

        # perform iterative linear fits
        gradients = []
        RMSEs = []
        for i, coord in enumerate(contour):
            if i < len(contour) - n_pts:
                m, c, rmse = linear_fit(contour[i:i+n_pts])
                gradients.append(m)
                RMSEs.append(rmse)

        # set the gradient of vertical lines to be the same as the previous point
        for i,m in enumerate(gradients):
            if str(m)=='inf' or str(m)=='-inf':
                gradients[i] = gradients[i-1]

        ### return the indices of each RMSE peak
        #RMSE_peaks_indices = signal.find_peaks(RMSEs, height=max(RMSEs)*0.3, prominence=0.5, width=5)[0] # height was 1
        #RMSE_peaks_indices = signal.find_peaks(RMSEs, height=max(RMSEs)*0.2, prominence=0.3, width=5)[0] # height was 1
        RMSE_peaks_indices = signal.find_peaks(RMSEs, height=max(RMSEs)*0.3, prominence=0.3, width=5)[0]
        RMSE_peaks_indices = sorted(RMSE_peaks_indices.tolist())
        if display == True:
            print('found indices using signal.find_peaks: ',RMSE_peaks_indices)
            if len(RMSE_peaks_indices) == 0:
                print('No peaks found in RMSE plot')

        # return the index of the max RMSE point, often this is missed by the signal package - so add it manually
        #if len(RMSE_peaks_indices)==0:
        max_RMSE_idx = RMSEs.index(np.nanmax(RMSEs))
        if max_RMSE_idx not in RMSE_peaks_indices:
            RMSE_peaks_indices.append(max_RMSE_idx)
        RMSE_peaks_indices = sorted(RMSE_peaks_indices)

        if 0:
            plt.title('initial RMSEs and those flagged')
            # show found indicies
            for i, RMSE in enumerate(RMSEs):
                plt.plot(i,RMSE, 'bo')
            for index in RMSE_peaks_indices:
                plt.plot(index, RMSEs[index], 'rx')
            plt.xlabel('index')
            plt.ylabel('RMSE')
            plt.show()
            plt.close()

        # include index of points where the gradient is near zero and changes sign - to catch reflections
        threshold = (max(gradients) - min(gradients))*0.3 # was 0.1
        sign_changes = np.where(abs(np.diff(np.sign(gradients)))>=1)[0]
        near_zero_indices = np.where(np.abs(gradients) < threshold)[0]
        gradient_change_indices = [val for val in near_zero_indices if val in sign_changes]

        # put indices of gradient change and high RMSE together into a list
        #indices = sorted(RMSE_peaks_indices + gradient_change_indices)
        indices = gradient_change_indices + RMSE_peaks_indices[::-1] # order this way to leave the most likely index last

        # remove any duplicates
        indices = list(set(indices))

        if display == True:
            print('found indices using RMSE peaks and points of gradient change: ',sorted(indices))

        # don't use the first or last points
        indices = [idx for idx in indices if idx != 0 and idx != len(RMSEs)-1]
        # don't use points at the very start of the curve
        indices = [idx for idx in indices if idx >= 3*n_pts]
        # don't use points where the RMSE immediately before or after is 0 - this might just be where the line is verical
        indices = [index for index in indices if RMSEs[index - 1] != 0 and RMSEs[index + 1] != 0]

        # set variables for exclusion search
        RMSE_h = max(RMSEs) - min(RMSEs)
        gradient_h = max(gradients) - min(gradients)
        RMSE_jump_too_high = 0.25 #0.15
        RMSE_tolerance = 0.2 #was 0.15, 0.5
        gradient_tolerance = 0.12 # was 0.1
        floor_tolerance = 0.01 # to ignore points right on next to each other on plots

        indices.sort()
        # Filter out indices with too high RMSE jumps at high gradients
        indices = [idx for idx in indices if len(indices) <= 1 or
                   ((abs(RMSEs[idx] - RMSEs[idx-1]) <= RMSE_h*RMSE_jump_too_high and
                    abs(RMSEs[idx] - RMSEs[idx+1]) <= RMSE_h*RMSE_jump_too_high) or abs(gradients[idx]) <= 0.5)]
        # print (but would need to define some new variable names for indices)
        #for idx in sorted(list(set(indices) - set(new_indices))):
            #print(f'Removing index {idx} due to RMSE jump of {RMSE_jump_too_high}')

        #indices = indices[::-1]
        print('indices before comparing RMSEs and gradients: ', sorted(indices))

        # take out any indices near the drop apex (first 15% of drop contour points)
        indices = [value for value in indices if value > len(contour)*0.15]

        # remove any points that are now out of range of the length of the contour
        indices = [idx for idx in indices if idx <= len(gradients)]

        #peak_gradients = [gradients[int(idx - n_pts/2)] for idx in indices]
        peak_gradients = [gradients[idx] for idx in indices]

        # take out any indices for points higher than the 60% contour height
        div_line = min(contour[:,1]) + (max(contour[:,1]) - min(contour[:,1]))*0.4
        # take out any indices for points higher than the 40% contour height
        #div_line = min(contour[:,1]) + (max(contour[:,1]) - min(contour[:,1]))*0.6
        indices = [idx for idx in indices if contour[idx,1] >= div_line]

        # now order lowest to highest
        indices = sorted(indices)

        # if none left use the max RMSE
        if len(indices) < 1:
            indices.append(max_RMSE_idx)

        if display:
            print()
            #print('peak_gradients: ', peak_gradients)
            #print('RMSE peaks found: ', RMSE_peaks_indices)
            print('indices of interest found: ',indices)

            plt.title('plot of fit RMSEs')
            plt.plot(range(len(RMSEs)), RMSEs,'.')
            h = max(RMSEs) - min(RMSEs)
            w = len(RMSEs)
            for i, idx in enumerate(indices):
                #if idx in RMSE_peaks_indices:
                if i==0:
                    plt.plot(idx,RMSEs[idx],'r+')
                else:
                    plt.plot(idx,RMSEs[idx],'+', color='pink')
                label = f"({idx:.2f}, {RMSEs[idx]:.2f})"
                plt.annotate(label, xy=(idx, RMSEs[idx]), xytext=(idx + w*0.1, RMSEs[idx] - h*0.1), textcoords="data", arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
            plt.xlabel('coordinate index')
            plt.ylabel('RMSE')
            plt.show()
            plt.close()

            plt.title('plot of gradients')
            plt.plot(range(len(gradients)), gradients,'.')
            #for idx in RMSE_peaks_indices:
            for i,idx in enumerate(indices):
                #if idx in gradient_change_indices:
                if i==0:
                    plt.plot(idx,gradients[idx],'r+')
                else:
                    plt.plot(idx,gradients[idx],'+', color='pink')
                label = f"({idx:.2f}, {gradients[idx]:.2f})"
                plt.annotate(label, xy=(idx, gradients[idx]), xytext=(idx + w*0.1, gradients[idx] - h*0.1), textcoords="data", arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))

            plt.xlabel('coordinate index')
            plt.ylabel('gradient')
            plt.show()
            plt.close()

        CP_indices = []
        for idx in indices:
            CP_indices.append(idx + round(n_pts/2))


        if display:
            print('index of identified points of interest: ',CP_indices)
            #print('final corrected list contact points:\n',np.array([contour[idx] for idx in CP_indices]))
            plt.title('Points of interest')
            plt.plot(contour[:,0],contour[:,1],',')
            h = max(contour[:,1]) - min(contour[:,1])
            w = len(contour[:,0])
            for i, idx in enumerate(CP_indices):
                if i==0:
                    plt.plot(contour[idx,0],contour[idx,1],'r+')
                    label = f"({contour[idx,0]:.2f}, {contour[idx,1]:.2f})"
                    plt.annotate(label, xy=(contour[idx,0],contour[idx,1]), xytext=(contour[idx,0], contour[idx,1] + 100), textcoords="data", arrowprops=dict(arrowstyle="->", connectionstyle="arc3")) #h*0.05
                else:
                    plt.plot(contour[idx,0],contour[idx,1],'r+')
            plt.plot(contour[:n_pts,0],contour[:n_pts,1], 'g.')
            plt.gca().invert_yaxis()
            plt.axis('equal')
            plt.show()
            plt.close()

        CPs_output.append(contour[CP_indices].tolist())

    return CPs_output

def find_CP_static_hydrophobic(contour, display=False):
    """Find the contact points of a drop contour by taking the inner most points of the bottom 10% of the drop contour.
    contour (array) - a 2D array of coordinate pairs (in image format).
    display (Boolean) - set to True to output images during use.
    """

    top = []
    percent = 0.1
    #print('isolate the bottom ',percent*100,'% of the contour:') # percent defined above
    #div_line_value = max(contour[:,1]) + (min(contour[:,1]) - max(contour[:,1]))*percent
    #print('gap: ', (max(contour[:,1]) - min(contour[:,1]))*percent)
    #print('max: ', max(contour[:,1]))

    div_line_value = max(contour[:,1]) - (max(contour[:,1]) - min(contour[:,1]))*percent
    #print('div_line_value: ', div_line_value)
    for coord in contour:
        if coord[1] < div_line_value:
            top.append(coord)
    top = np.array(top)

    if display:
        plt.plot(contour[:,0], contour[:,1], 'r,', label='contour')
        plt.plot(top[:,0], top[:,1], 'b.', label='top section')
        plt.gca().invert_yaxis()
        plt.legend()
        plt.show()
        plt.close()

    xapex = (max(top[:,0]) + min(top[:,0]))/2
    #print('The x value of the apex is: ',xapex)

    l_drop = []
    r_drop = []
    for n in contour:
        if n[0] < xapex:
            l_drop.append(n)
        if n[0] >= xapex:
            r_drop.append(n)
    l_drop = np.array(l_drop)
    r_drop = np.array(r_drop)

    if display:
        plt.plot(l_drop[:,[0]], l_drop[:,[1]], 'r,', label='left side')
        plt.plot(r_drop[:,[0]], r_drop[:,[1]], 'b,', label='right side')
        plt.gca().invert_yaxis()
        plt.legend()
        plt.show()
        plt.close()

    # determine CPs
    percent = 0.2#0.3
    #print('isolate the bottom ',percent*100,'% of the contour:') # percent defined above
    div_line_value = max(contour[:,1]) + (min(contour[:,1]) - max(contour[:,1]))*percent

    CPs = []
    l_drop_bottom = l_drop.copy()[l_drop.copy()[:,1] > div_line_value]
    xCP = max(l_drop_bottom[:,0])
    yCP = []
    for coord in l_drop_bottom:
        if coord[0]==xCP:
            yCP.append(coord[1])
    yCP =min(yCP)
    CPs.append([xCP, yCP])

    r_drop_bottom = r_drop.copy()[r_drop.copy()[:,1] > div_line_value]
    xCP = min(r_drop_bottom[:,0])
    yCP = []
    for coord in r_drop_bottom:
        if coord[0]==xCP:
            yCP.append(coord[1])
    yCP =min(yCP)
    CPs.append([xCP, yCP])

    CPs = np.array(CPs)

    if display:
        plt.title('Found contact points')
        plt.plot(contour[:,0], contour[:,1], ',', label='full contour')
        plt.plot(l_drop_bottom[:,0],l_drop_bottom[:,1],'.', label='left side of bottom 50%')
        plt.plot(CPs[0,0], CPs[0,1], 'o', label='left contact point: '+str(CPs[0]))
        plt.plot(r_drop_bottom[:,0],r_drop_bottom[:,1],'.', label='right side of bottom 50%')
        plt.plot(CPs[1,0], CPs[1,1], 'o', label='right contact point: '+str(CPs[1]))
        plt.gca().invert_yaxis()
        plt.axis('equal')
        plt.legend()
        plt.show()
        plt.close()

    #print('CPs: ',CPs)
    return CPs

def find_leftmost_coordinates(coordinates: np.ndarray) -> np.ndarray:
    """
    Find the leftmost (minimum x) coordinate for each unique y value in the input array.

    This function takes a 2D numpy array of x,y coordinates and returns a new array
    containing only the leftmost coordinate for each unique y value.

    Args:
        coordinates (np.ndarray): A 2D numpy array of shape (n, 2) where each row
                                  represents an (x, y) coordinate pair.

    Returns:
        np.ndarray: A 2D numpy array of shape (m, 2) where m is the number of unique
                    y values in the input. Each row contains the leftmost (x, y)
                    coordinate for a unique y value.

    Raises:
        ValueError: If the input array is not 2D or doesn't have exactly 2 columns.

    Example:
        >>> coords = np.array([[1, 2], [3, 2], [2, 3], [4, 3], [0, 1], [5, 1]])
        >>> find_leftmost_coordinates(coords)
        array([[0, 1],
               [1, 2],
               [2, 3]])
    """
    # Check if the input array has the correct shape
    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError("Input must be a 2D array with 2 columns (x, y)")

    # Sort the array by y values (column 1) and then by x values (column 0)
    sorted_coords = coordinates[np.lexsort((coordinates[:, 0], coordinates[:, 1]))]

    # Find the indices where y values change
    y_changes = np.diff(sorted_coords[:, 1]).nonzero()[0]

    # Get the leftmost coordinates for each unique y value
    leftmost_coords = np.vstack((sorted_coords[0], sorted_coords[y_changes + 1]))

    return leftmost_coords

def find_rightmost_coordinates(coordinates: np.ndarray) -> np.ndarray:
    """
    Find the rightmost (maximum x) coordinate for each unique y value in the input array.

    This function takes a 2D numpy array of x,y coordinates and returns a new array
    containing only the rightmost coordinate for each unique y value.

    Args:
        coordinates (np.ndarray): A 2D numpy array of shape (n, 2) where each row
                                  represents an (x, y) coordinate pair.

    Returns:
        np.ndarray: A 2D numpy array of shape (m, 2) where m is the number of unique
                    y values in the input. Each row contains the rightmost (x, y)
                    coordinate for a unique y value.

    Raises:
        ValueError: If the input array is not 2D or doesn't have exactly 2 columns.

    Example:
        >>> coords = np.array([[1, 2], [3, 2], [2, 3], [4, 3], [0, 1], [5, 1]])
        >>> find_rightmost_coordinates(coords)
        array([[5, 1],
               [3, 2],
               [4, 3]])
    """
    # Check if the input array has the correct shape
    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError("Input must be a 2D array with 2 columns (x, y)")

    # Sort the array by y values (column 1) and then by x values in descending order (column 0)
    sorted_coords = coordinates[np.lexsort((-coordinates[:, 0], coordinates[:, 1]))]

    # Find the indices where y values change
    y_changes = np.diff(sorted_coords[:, 1]).nonzero()[0]

    # Get the rightmost coordinates for each unique y value
    rightmost_coords = np.vstack((sorted_coords[0], sorted_coords[y_changes + 1]))

    return rightmost_coords

def check_order(contour):
    jet= plt.get_cmap('jet')
    colors = iter(jet(np.linspace(0,1,len(contour))))
    for n,coord in enumerate(contour):
        plt.plot(contour[n,0],contour[n,1], 'o', color=next(colors))
    plt.title('ordered points, starting from blue')
    plt.axis('equal')
    plt.gca().invert_yaxis()
    plt.show()
    plt.close()

def calculate_contact_angle(gradient, side='left'):
    """
    Calculates the internal contact angle from a given gradient for either the left or right side,
    taking into account the flipped y-axis in image coordinates.

    Parameters:
    gradient (float): The slope of the line (gradient).
    side (str): Either 'left' or 'right', specifying which side's contact angle to calculate.

    Returns:
    float: The contact angle in degrees, measured from the horizontal.
    """
    if np.isnan(gradient):
        gradient = np.inf

    # Adjust the gradient for the image coordinate system where the y-axis is flipped
    gradient = -gradient

    # Calculate the angle in radians using the arctangent of the adjusted gradient
    angle_radians = np.arctan(gradient)

    # Convert the angle to degrees
    angle_degrees = np.degrees(angle_radians)

    if side == 'left':
        # For the left side, ensure the angle is counter-clockwise from the horizontal
        if angle_degrees < 0:
            angle_degrees += 180
    elif side == 'right':
        # For the right side, ensure the angle is clockwise from the horizontal
        angle_degrees = -angle_degrees
        if angle_degrees < 0:
            angle_degrees += 180
    else:
        raise ValueError("The 'side' parameter must be either 'left' or 'right'.")

    return angle_degrees

def check_for_high_angle(contour, display=False):

    #check the shape of the input contour
    if len(contour) > 110:
        # input is a single contour, needle out of drop

        # find drop apex and split into left and right sides
        divline = int(min(contour[:,1])+(max(contour[:,1] - min(contour[:,1])*0.2)))

        top = np.array([[x, y] for x, y in contour if y <= divline])
        #bottom = np.array([[x, y] for x, y in contour if y < divline])
        apex = np.array([[x, y] for x, y in top if y == min(top[:,1])])
        xapex = min(apex[:,0]) + (max(apex[:,0]) - min(apex[:,0]))/2

        left = np.array([[x, y] for x, y in contour if x <= xapex])
        right = np.array([[x, y] for x, y in contour if x > xapex])
    elif len(contour) == 2:
        # input is several contours, needle inside drop
        # assuming two contours
        left = contour[0]
        right = contour[1]

        # check that the first point of each contour is the highest point on the contour
        if left[0,1] < min(left[:,1]):
            # take the highest and left most point as the starting point of the left contour
            apex = min(left, key=lambda point: (point[1], point[0]))
            start = np.where((left == apex).all(axis=1))[0][0]
            left = left[start:]
        if right[0,1] < min(right[:,1]):
            # take the highest and right most point as the starting point of the right contour
            apex = min(right, key=lambda point: (point[1], -point[0]))
            start = np.where((right == apex).all(axis=1))[0][0]
            right = right[start:]
    else:
        print(f'Number of contours is not correct for check_for_high_angle, contour.shape[0] == {contour.shape[0]}')
        print('Taking first 2 contours')
    CP_guesses = []
    widest_points = []

    for i, edge in enumerate([left, right]):
        if i==0:
            edge = find_rightmost_coordinates(edge) # to ignore any rough surface points
        elif i==1:
            edge = find_leftmost_coordinates(edge)

        if 0:
            check_order(edge)

        widest = edge[10]
        CP_guess = None

        curves_cut_in = False
        for idx, coord in enumerate(edge):
            if idx > 10: # skip the first 10 to miss any edge detection errors at the apex
                if i==0: # left
                    if CP_guess is None:
                        if coord[0] < widest[0] and coord[1] > widest[1] and abs(coord[0] - widest[0]) < 15:
                            widest = coord
                        if coord[0] > widest[0] and coord[1] > widest[1] and curves_cut_in == False:
                            CP_guess = coord
                    else: #CP_guess is not None
                        if coord[0] < widest[0] and coord[1] > widest[1] and coord[1] <= CP_guess[1]:
                            widest = coord
                        if coord[0] < CP_guess[0]:
                            curves_cut_in = True
                        if coord[0] >= CP_guess[0] and coord[1] > CP_guess[1]:
                            CP_guess = coord
                        elif coord[0] < CP_guess[0] and coord[1] > CP_guess[1]: #if it starts widening again after CP_guess found then stop
                            break
                elif i==1: # right
                    if CP_guess is None:
                        if coord[0] > widest[0] and coord[1] > widest[1] and abs(coord[0] - widest[0]) < 15:
                            widest = coord
                        if coord[0] < widest[0] and coord[1] > widest[1] and curves_cut_in == False:
                            CP_guess = coord
                    else: #CP_guess is not None
                        if coord[0] > widest[0] and coord[1] > widest[1] and coord[1] <= CP_guess[1]:
                            widest = coord
                        if coord[0] > CP_guess[0]:
                            curves_cut_in = True
                        if coord[0] <= CP_guess[0] and coord[1] > CP_guess[1]:
                            CP_guess = coord
                        elif coord[0] > CP_guess[0] and coord[1] > CP_guess[1]: #if it starts widening again after CP_guess found then stop
                            break
        if CP_guess is None:
            CP_guess = widest
        else:
            if 0:# check for a column, and have the widest point be the middle point
                widest_index = np.where((edge == widest).all(axis=1))[0][0]
                widest2_top_index = widest_index
                for i, coord in enumerate(edge):
                    if i > widest_index:
                        if coord[0] == widest[0]:
                            widest2_top_index = i
                        else:
                            break
                widest_index = int((widest_index + widest2_top_index)/2)
                widest = edge[widest_index]
            else: # take the highest point
                widest = widest

        if 0: # good for debugging
            plt.plot(edge[:,0], edge[:,1], '.')
            plt.plot(CP_guess[0], CP_guess[1],'.',label=f'CP_guess - {CP_guess}')
            plt.plot(widest[0], widest[1],'.',label=f'widest - {widest}')
            plt.gca().invert_yaxis()
            plt.axis('equal')
            plt.legend()
            plt.show()
            plt.close()

        # load outputs to lists
        CP_guesses.append(CP_guess)
        widest_points.append(widest)

    #convert lists to arrays
    CP_guesses = np.array(CP_guesses)
    widest_points = np.array(widest_points)

    if display:
        plt.title(f'check outputted vals\nwidest points:{widest_points}\nCP guesses:{CP_guesses}')
        plt.plot(left[:,0], left[:,1], 'C0,')
        plt.plot(right[:,0], right[:,1], 'C0,')
        plt.plot(CP_guesses[0,0], CP_guesses[0,1], 'C1.', label='CP guess left')
        plt.plot(CP_guesses[1,0], CP_guesses[1,1], 'C2.', label='CP guess right')
        plt.plot(widest_points[:,0], widest_points[:,1], 'C3.', label='widest points guesses')
        #plt.plot(contour[:,0], contour[:,1], 'C0,')
        plt.gca().invert_yaxis()
        plt.axis('equal')
        plt.legend()
        plt.show()
        plt.close()
    return CP_guesses, widest_points

def CP_ID_static(longest_contour, drop_guess, info, display):
    """
    Code to identify the contact points.
    """
    if info['circle'] != None and info['line'].any() != None:
        center, radius = info['circle']
        intersections = line_circle_intersection(info['line'][0], info['line'][1], center, radius)
        x1, y1 = intersections[0]
        x2, y2 = intersections[1]
        midpoint = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
        if info['circle'][0][1] > midpoint[1] - radius*0.3: # low angle system, slight bias for consistency, was 0.2 / 0.3
            if display:
                print('low circle identified - likely low angle system')
            CPs_output = find_CP_static_Lfit(longest_contour,len(drop_guess), display=display)
            CPs_chosen = np.array([CPs_output[0][0],CPs_output[1][0]])
        else: #high angle system
            if display:
                print('high circle identified - likely high angle system')
            CPs_chosen = find_CP_static_hydrophobic(longest_contour, display=display)
    elif info['circle'] != None:
        if max(longest_contour[:,1]) < info['circle'][0][1]:# low angle system
            if display:
                print('low circle identified - likely low angle system')
            CPs_output = find_CP_static_Lfit(longest_contour,len(drop_guess), display=display)
            CPs_chosen = np.array([CPs_output[0][0],CPs_output[1][0]])
        else: #high angle system
            if display:
                print('high circle identified - likely high angle system')
            CPs_chosen = find_CP_static_hydrophobic(longest_contour, display=display)
            #CPs_chosen = np.array([[CPs_chosen[0,0], CPs_chosen[0,1]],[CPs_chosen[1,0], CPs_chosen[1,1]]])
    else:
        if display:
            print('circle not identified')
        CPs_output = find_CP_static_Lfit(longest_contour,len(drop_guess),percentage=2.0, display=display)
        CPs_chosen = np.array([CPs_output[0][0],CPs_output[1][0]])

    return CPs_chosen

def CPID(contour, display=False):
    """
    Identifies the contact points (CPs) from a given contour based on its shape and angles.

    This function first determines candidate CPs and the widest points of the contour. Depending on the number of contour points,
    it calculates an appropriate number of points for a linear fit (Lfit) approach. The function then checks whether the candidate CPs
    match the widest points. If they do, it applies an Lfit method to determine the final CPs. Otherwise, it estimates contact angles
    at the widest points and selects the CPs based on predefined angle thresholds.

    Parameters:
    ----------
    contour : np.ndarray
        A 2D array representing the contour coordinates.
    display : bool, optional
        If True, prints debugging information about the CP determination process (default is False).

    Returns:
    -------
    np.ndarray
        A 2D array containing the coordinates of the final contact points.

    Notes:
    ------
    - If the number of contour points is 110 or more, the function treats it as a single contour.
    - If there are exactly 2 contours, it processes them separately.
    - If the determined CPs match the widest points, an Lfit approach is used.
    - Otherwise, the function estimates contact angles and classifies the system as reflective, hydrophobic, or low-angle reflective.

    """
    # check for CP guesses and the widest points
    CP_guesses, widest_points = check_for_high_angle(contour, display=True)

    if len(contour) == 2: #if working with two contours (left and right)
        contour = np.concatenate(contour, axis=0)
        print('contour concatenated into a single line')
        if 0: #check
            plt.plot(contour[:,0], contour[:,1], '.')
            plt.gca().invert_yaxis()
            plt.axis('equal')
            plt.show()
            plt.close()

    # determine drop_guess using n_pts between widest points
    if len(contour) > 110:
        # for a single contour
        widest_index1 = np.where((contour == widest_points[0]).all(axis=1))[0][0]
        widest_index2 = np.where((contour == widest_points[1]).all(axis=1))[0][0]
        dist_between_widest = widest_index2 - widest_index1
        #print('CP_guesses: ',CP_guesses)
        #print('widest_points: ', widest_points)
        #print('dist between widest: ', dist_between_widest)

        percentage = 2.5
        Lfit_n_pts = int(dist_between_widest*percentage/100)
    elif len(contour) == 2:
        # for two contours
        widest_index1 = np.where((contour[0] == widest_points[0]).all(axis=1))[0][0]
        widest_index2 = np.where((contour[1] == widest_points[1]).all(axis=1))[0][0]
        dist_between_widest = widest_index2 + widest_index1
        #print('CP_guesses: ',CP_guesses)
        #print('widest_points: ', widest_points)
        #print('dist between widest: ', dist_between_widest)

        percentage = 2.5
        Lfit_n_pts = int(dist_between_widest*percentage/100)
    else:
        print(f'Number of contours is not correct for CPID, contour.shape[0] == {contour.shape[0]}')
        print('Taking first 2 contours')

    n_pts = 10

    # first check if any of the CP_guesses are the same as any of the widest points
    if np.any(np.all(CP_guesses[:, None] == widest_points, axis=2)):
        # use Lfit
        restriction1 = max(0, widest_index1 - 4*n_pts)
        restriction2 = min(len(contour), widest_index2 + 4*n_pts)
        restricted_contour = contour[restriction1 : restriction2]
        if 0:
            plt.title('plot restricted contour')
            plt.plot(restricted_contour[:,0], restricted_contour[:,1], '.')
            plt.plot(widest_points[:,0], widest_points[:,1], '.', label='widest points')
            plt.legend()
            plt.axis('equal')
            plt.show()
            plt.close()

        Lfit_out = iterative_Lfit(restricted_contour, Lfit_n_pts, display=display)
        left_Lfit, right_Lfit = Lfit_out[0][0], Lfit_out[1][0]

        # take the right most point of those determined by Lfit and widest points
        final_left  = max([left_Lfit, widest_points[0]], key=lambda point: point[0])
        # take the left most point of those determined by Lfit and widest points
        final_right  = min([right_Lfit, widest_points[1]], key=lambda point: point[0])

        final_CPs = np.array([final_left,final_right])
        print(f'final_CPs outputted by Lfit: {final_CPs}')

    else:
        shuffle = 0 # to account for bend at reflection points

        # angles of left side
        if len(contour) >= 110:
            widest1_bottom_m, widest1_bottom_c, widest1_bottom_rmse = linear_fit(contour[widest_index1-shuffle-n_pts:widest_index1-shuffle])
            widest1_top_m, widest1_top_top_c, widest1_top_rmse = linear_fit(contour[widest_index1:widest_index1+n_pts])
        elif len(contour) == 2:
            widest1_bottom_m, widest1_bottom_c, widest1_bottom_rmse = linear_fit(contour[0][widest_index1-shuffle:widest_index1+n_pts-shuffle])
            widest1_top_m, widest1_top_top_c, widest1_top_rmse = linear_fit(contour[0][widest_index1-n_pts:widest_index1])
        widest1_bottom_angle = calculate_contact_angle(widest1_bottom_m, 'left')
        widest1_top_angle = calculate_contact_angle(widest1_top_m, 'left')
        #print('widest1_bottom_angle: ',widest1_bottom_angle)
        #print('widest1_top_angle: ', widest1_top_angle)

        # angles of right side
        if len(contour) >= 110:
            widest2_bottom_m, widest2_bottom_c, widest2_bottom_rmse = linear_fit(contour[widest_index2+shuffle:widest_index2+n_pts+shuffle])
            widest2_top_m, widest2_top_c, widest2_top_rmse = linear_fit(contour[widest_index2-n_pts:widest_index2])
        elif len(contour) == 2:
            widest2_bottom_m, widest2_bottom_c, widest2_bottom_rmse = linear_fit(contour[1][widest_index2+shuffle:widest_index2+n_pts+shuffle])
            widest2_top_m, widest2_top_c, widest2_top_rmse = linear_fit(contour[1][widest_index2-n_pts:widest_index2])
        widest2_bottom_angle = calculate_contact_angle(widest2_bottom_m, 'right')
        widest2_top_angle = calculate_contact_angle(widest2_top_m, 'right')
        #print('widest2_bottom_angle: ',widest2_bottom_angle)
        #print('widest2_top_angle: ', widest2_top_angle)

        # angles between widest points and apex
        #xapex = int(min(widest_points[:,0]) + (max(widest_points[:,0]) - min(widest_points[:,0]))/2)
        #apex = min([coord for coord in contour if coord[0] == xapex], key=lambda coord: coord[1])

        #widest1_to_apex = calculate_contact_angle((apex[1] - widest_points[0][1]) / (apex[0] - widest_points[0][0]), 'left')
        #widest2_to_apex = calculate_contact_angle((apex[1] - widest_points[1][1]) / (apex[0] - widest_points[1][0]), 'right')
        #print(f'angles to apex {widest1_to_apex}, and {widest2_to_apex}')

        error_margin = 18
        final_CPs = []
        full_Lfit = False
        #if widest1_top_angle < 60 or widest2_top_angle < 60:
        #print('widest1_top_angle: ', widest1_top_angle)
        #print('180 - widest1_bottom_angle: ',180 - widest1_bottom_angle)
        #print('widest2_top_angle: ', widest2_top_angle)
        #print('180 - widest2_bottom_angle: ',180 - widest2_bottom_angle)
        buffer = 2

        # is the top angle at the widest point high?
        #if widest1_top_angle > 180 - widest1_bottom_angle - buffer or widest2_top_angle > 180 - widest2_bottom_angle - buffer: #4 for error
        if widest1_top_angle > 90 - error_margin or widest2_top_angle > 90 - error_margin:
            # if the angle under the widest point is big enough then it should be reflective
            if widest1_bottom_angle > 100 or widest2_bottom_angle > 100:
                print('large angles under widest points - low angle reflective')
                print(f'angles preceding widest point are {widest1_top_angle}, {widest2_top_angle}')
                print(f'angles proceeding widest point are {widest1_bottom_angle}, {widest2_bottom_angle}')
                final_CPs = widest_points
            # are the angles above and below the widest point reflective?
            #elif 180 - widest1_bottom_angle - widest1_top_angle < 1 or 180 - widest2_bottom_angle - widest2_top_angle < 1:
            #    print('found reflective')
            #    print(f'angles preceding widest point are {widest1_top_angle}, {widest2_top_angle}')
            #    print(f'angles proceeding widest point are {widest1_bottom_angle}, {widest2_bottom_angle}')
            #    print(f'180 - widest1_bottom_angle - widest1_top_angle = {180 - widest1_bottom_angle - widest1_top_angle}')
            #    print(f'180 - widest2_bottom_angle - widest2_top_angle = {180 - widest2_bottom_angle - widest2_top_angle}')
            #    final_CPs = widest_points

            # check if the angles over and under the widest point are close to each other, and the bottom angle is harsh enough - then reflective
            elif (180 - widest1_top_angle - widest1_bottom_angle < 8 and widest1_bottom_angle > 99) or (180 - widest2_top_angle - widest2_bottom_angle < 8 and widest1_bottom_angle > 99):
                print('angles on either side of widest points are similar - reflective')
                print(f'angles preceding widest point are {widest1_top_angle}, {widest2_top_angle}')
                print(f'angles proceeding widest point are {widest1_bottom_angle}, {widest2_bottom_angle}')
                final_CPs = widest_points

            # if not reflective, then is the angle under the widest point high enough for it to a high angle system?
            elif 180 - widest1_bottom_angle > 79 or 180 - widest2_bottom_angle > 79: #78
                # high angle systems that may appear to the code as reflective
                print('looks reflective but is high angle')
                print(f'angles preceding widest point are {widest1_top_angle}, {widest2_top_angle}')
                print(f'angles proceeding widest point are {widest1_bottom_angle}, {widest2_bottom_angle}')
                final_CPs = CP_guesses

            # otherwise use Lfit if unsure
            else:
                #final_CPs = widest_points

                # restrict contour to just past CP_guesses
                CP_guess_index1 = np.where((contour == CP_guesses[0]).all(axis=1))[0][0]
                CP_guess_index2 = np.where((contour == CP_guesses[1]).all(axis=1))[0][0]
                restricted_contour = contour[CP_guess_index1 - 4*n_pts : CP_guess_index2 + 4*n_pts]
                if 0:
                    plt.title('plot restricted contour')
                    plt.plot(restricted_contour[:,0], restricted_contour[:,1], '.')
                    plt.plot(CP_guesses[:,0], CP_guesses[:,1], '.', label='CP_guesses')
                    plt.legend()
                    plt.axis('equal')
                    plt.show()
                    plt.close()
                # if this isn't quite working, can use L_fit here
                final = iterative_Lfit(restricted_contour, Lfit_n_pts, display=display)
                left_CP, right_CP = final[0][0], final[1][0]
                final_CPs = np.array([left_CP,right_CP])

                print(f'assumed low angle reflective')
                print(f'angles preceding widest point are {widest1_top_angle}, {widest2_top_angle}')
                print(f'angles proceeding widest point are {widest1_bottom_angle}, {widest2_bottom_angle}')
                #print('widest1_top_angle: ',widest1_top_angle)
                #print('widest1_bottom_angle: ', 180 - widest1_bottom_angle - buffer)
                #print('widest2_top_angle:  ', widest2_top_angle)
                #print('widest2_bottom_angle: ',180 - widest2_bottom_angle - buffer)
        elif widest1_top_angle < 65 or widest2_top_angle < 65:
            print(f'low angle - angles preceding widest point are {widest1_top_angle}, {widest2_top_angle}')
            final_CPs = widest_points
        elif 65 < widest1_top_angle < 90 - error_margin or 65 < widest2_top_angle < 90 - error_margin:
            #final_CPs.append(widest_points[0])
            print(f'maybe high angle, Lfit - angles preceding widest point are {widest1_top_angle}, {widest2_top_angle}')
            print(f'angles proceeding widest point are {widest1_bottom_angle}, {widest2_bottom_angle}')

            # restrict contour to just past CP_guesses
            CP_guess_index1 = np.where((contour == CP_guesses[0]).all(axis=1))[0][0]
            CP_guess_index2 = np.where((contour == CP_guesses[1]).all(axis=1))[0][0]
            restricted_contour = contour[CP_guess_index1 - 4*n_pts : CP_guess_index2 + 4*n_pts]
            if 0:
                plt.title('plot restricted contour')
                plt.plot(restricted_contour[:,0], restricted_contour[:,1], '.')
                plt.plot(CP_guesses[:,0], CP_guesses[:,1], '.', label='CP_guesses')
                plt.legend()
                plt.axis('equal')
                plt.show()
                plt.close()
            # if this isn't quite working, can use L_fit here
            final = iterative_Lfit(restricted_contour, Lfit_n_pts, display=display)
            left_CP, right_CP = final[0][0], final[1][0]
            final_CPs = np.array([left_CP,right_CP])

        else:  # should do the full Lfit approach here
            #final_CPs.append(CP_guesses[0])
            final_CPs = CP_guesses
            print(f'assumed hydrophobic - angles preceding widest point are {widest1_top_angle}, {widest2_top_angle}')
            print(f'angles proceeding widest point are {widest1_bottom_angle}, {widest2_bottom_angle}')
        # for right side
        #if widest2_top_angle < 90 - error_margin:
        #    final_CPs.append(widest_points[1])
        #    print(f'right angle at widest point is {widest2_angle}')
        #else: # should do the full Lfit approach here
        #    final_CPs.append(CP_guesses[1])
        #final_CPs = np.array(final_CPs)
    return final_CPs

def preprocess(img, display=False):
    """This code serves as a discrete instance of image preprocessing before contact
    angle fit software is implemented.
    """
    img_processed, longest_contour, drop_guess, info = isolate_contour(img,DISPLAY=display)

    CPs_chosen = CP_ID_static(longest_contour, drop_guess, info, display=display)

    if 0: #if info['line'].any() == None:
        # this is only sometimes appropriate, best to assume a decent image is taken
        img = tilt_correction(img, CPs_chosen)
        img_processed, longest_contour, drop_guess, info = isolate_contour(img,DISPLAY=display)
        CPs_chosen = CP_ID_static(longest_contour, drop_guess, info, display=display)

    if display:
        plt.imshow(img_processed)
        plt.plot(longest_contour[:,0],longest_contour[:,1],',')
        plt.plot(CPs_chosen[0,0],CPs_chosen[0,1],'.',label='Left contact points: '+str(CPs_chosen[0]))
        plt.plot(CPs_chosen[1,0],CPs_chosen[1,1],'.',label='Right contact points: '+str(CPs_chosen[0]))
        plt.legend()
        plt.show()
        plt.close()

    # define drop profile contour as the contour between contact points
    idx_leftCP = np.where((longest_contour == CPs_chosen[0]).all(axis=1))[0][0]
    idx_rightCP = np.where((longest_contour == CPs_chosen[1]).all(axis=1))[0][0]
    # ensure idx_leftCP is smaller than idx_rightCP
    if idx_leftCP > idx_rightCP:
        idx_leftCP, idx_rightCP = idx_rightCP, idx_leftCP
    profile = longest_contour[idx_leftCP:idx_rightCP+1]

    return img_processed, CPs_chosen, longest_contour

if 0: #test
    IMG_PATH = '/Users/dgshaw/OneDrive - The University of Melbourne/experimental-image-database/Current/10.bmp'

    img = cv2.imread(IMG_PATH, cv2.IMREAD_COLOR)

    if 1:
        plt.title('loaded image')
        plt.imshow(img)
        plt.show()
        plt.close()

    print('beginning preprocessing')
    img, profile, longest_contour = preprocess(img, display=True)

    if 1:
        plt.title('processed image')
        plt.imshow(img)
        plt.show()
        plt.close()
    print('preprocessing ended')
    print()
    print('repeating preprocessing with display off')

    img, profile, longest_contour = preprocess(img, display=False)
