#!/usr/bin/env python
#coding=utf-8

import matplotlib.pyplot as plt
import numpy as np
import cv2
import tensorflow as tf

from sklearn.cluster import OPTICS # for clustering algorithm
import math # for tilt_correction
from scipy import misc, ndimage # for tilt_correction
import time # for recording timings
import io #for saving to memory
from modules.preprocessing import auto_crop, distance1, cluster_OPTICS

def optimized_path_new(coords, start=None):
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

    # if there are any large jumps in distance, there is likely a mistake
    # therefore, the points after this jump should be ignored
    if 1:
        dists = []
        for i, point in enumerate(path):
            if i < len(path)-1:
                dists.append(distance1(path[i], path[i+1]))
        jump_idx = []
        for i, dist in enumerate(dists):
            if dist > 5:
                jump_idx.append(i)
        if len(jump_idx)>0:
            path = path[:jump_idx[0]]

    return path

def prepare_hydrophobic_new(coords,xi=0.8,display=False):
    """takes an array (n,2) of coordinate points, and returns the left and right halfdrops of the contour.
    xi determines the minimum steepness on the reachability plot that constitutes a cluster boundary of the
    clustering algorithm.
    deg is the degree of the polynomial used to describe the shape of the droplet.

    This code is adapted from the prepare module, but this version differs in that it assumes that the drop
    is hydrophobic."""
    # scan for clusers to remove noise and circle from lensing effect
                ################  MAY NEED TO OPTIMIZE eps/xi TO FIND APPROPRIATE GROUPINGS  ####################
    if display: # turn this off bc using synthetic drops without lensing effect
        input_contour = coords
        dic,dic2 = cluster_OPTICS(input_contour,xi=xi),cluster_OPTICS(input_contour,out_style='xy',xi=xi)

        #print("number of groups: ",len(list(dic.keys())))

        jet= plt.get_cmap('jet')
        colors = iter(jet(np.linspace(0,1,len(list(dic.keys())))))
        for k in dic.keys():
            plt.plot(dic2[str(k)+'x'],dic2[str(k)+'y'], 'o',color=next(colors))
        plt.title(str(len(dic.keys()))+" groups found by clustering")
        plt.show()
        plt.close()
        maxkey=max(dic, key=lambda k: len(dic[k]))

        #print('key to longest dictionary entry is: ',maxkey)

        # take the longest group
        longest = dic[maxkey]

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

    dists = [] # find the average distance between points
    for n,co in enumerate(top_array):
        if 1<n:
            a = top_array[n]
            dist = np.linalg.norm(top_array[n]-top_array[n-1])
            dists.append(dist)

    if display:
        #print(dists)
        print()
        print('Max dist between points is: ',max(dists))
        print('Average dist between points is: ',sum(dists)/len(dists))
        print('20% over the Max dist is: ', max(dists)*1.2)
        print()
        print('Sort using cluster_OPTICS with an epsilon value of ',max(dists)*1.2)

    # how epsilon is chosen here is important
    #eps = (sum(dists)/len(dists))*2 # eps is 2 times the average distance between points
    eps = (sum(dists)/len(dists))*1.5 # eps is 2.5 times the average distance between points
    input_contour = longest
    dic,dic2 = cluster_OPTICS(input_contour,eps=eps),cluster_OPTICS(input_contour,out_style='xy',eps=eps)

    #print("number of groups: ",len(list(dic.keys())))
    if display:
        jet= plt.get_cmap('jet')
        colors = iter(jet(np.linspace(0,1,len(list(dic.keys())))))
        for k in dic.keys():
            plt.plot(dic2[str(k)+'x'],dic2[str(k)+'y'], 'o',color=next(colors))
        plt.title('Groups found by clustering with epsilon value of '+str(eps))
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
    #print('The x value of the apex is: ',xapex)

    l_drop = []
    r_drop = []
    for n in longest:
        if n[0] < xapex:
            l_drop.append(n)
        if n[0] > xapex:
            r_drop.append(n)
    l_drop = np.array(l_drop)
    r_drop = np.array(r_drop)



    # transpose both half drops so that they both face right and the apex of both is at 0,0
    r_drop[:,[0]] = r_drop[:,[0]] - xapex
    l_drop[:,[0]] = -l_drop[:,[0]] + xapex

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
        xhalfdrop = halfdrop[:,[0]].reshape(len(halfdrop[:,[0]]))
        yhalfdrop = halfdrop[:,[1]].reshape(len(halfdrop[:,[1]]))

        # isolate the bottom of the drop to help identify contact points (may not need to do this for all scenarios)
        bottom = []
        top = [] # will need this later
        #print('isolate the bottom ',percent*100,'% of the contour:') # percent defined above
        div_line_value = min(halfdrop[:,[1]]) + (max(halfdrop[:,[1]]) - min(halfdrop[:,[1]]))*percent
        for n in halfdrop:
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

        if display: # plot the bottom 10% of the contour
            plt.plot(xbottom, ybottom, 'b,')
            plt.title('bottom 10% of the contour')
            #plt.xlim([130,200])
            plt.show()
            plt.close()

        #### Continue here assuming that the drop is hydrophobic ####


        if 1:
            # order all halfdrop points using optimized_path (very quick but occasionally makes mistakes)

            new_halfdrop = sorted(halfdrop.tolist(), key=lambda x: (x[0],-x[1])) #top left to bottom right
            new_halfdrop = optimized_path(new_halfdrop)#[::-1]

            xnew_halfdrop = new_halfdrop[:,[0]].reshape(len(new_halfdrop[:,[0]]))
            ynew_halfdrop = new_halfdrop[:,[1]].reshape(len(new_halfdrop[:,[1]]))

            xCP = min(xbottom)
            yCP = []
            for coord in new_halfdrop:
                if coord[0]==xCP:
                    yCP.append(coord[1])
            yCP =min(yCP)
            CPs[counter] = [xCP, yCP]

            if display: #check
                plt.plot(new_halfdrop[:,0],new_halfdrop[:,1])
                plt.show()
                plt.close()

            # remove surface line past the contact point

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
                            #print('indexes of the CP are: ',xCP_index[0],', ',yCP_index[0])
                            if new_halfdrop[xCP_index[0]+1][1]>new_halfdrop[xCP_index[0]-1][1]:
                                new_halfdrop = new_halfdrop[xCP_index[0]:]
                            else:
                                new_halfdrop = new_halfdrop[:xCP_index[0]+1]
                if raise_error == True:
                    print('The index of the contact point x value is: ', new_halfdrop[xCP_index])
                    print('The index of the contact point y value is: ', new_halfdrop[yCP_index])
                    raise 'indexes of x and y values of the contact point are not the same'

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
                                raise 'indexes of x and y values of the contact point are not the same'
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
            #print('Indexes of contour points past drop: ',surface_past_drop_index)


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
                    raise 'indexes of x and y values of the contact point are not the same'

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
                                #print('indexes of the CP are: ',xCP_index[0],', ',yCP_index[0])
                                if new_halfdrop[xCP_index[0]+1][1]>new_halfdrop[xCP_index[0]-1][1]:
                                    new_halfdrop = new_halfdrop[xCP_index[0]:]
                                else:
                                    new_halfdrop = new_halfdrop[:xCP_index[0]+1]
                    if raise_error == True:
                        print('The index of the contact point x value is: ', new_halfdrop[xCP_index])
                        print('The index of the contact point y value is: ', new_halfdrop[yCP_index])
                        raise 'indexes of x and y values of the contact point are not the same'

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

    # flip contour back to original orientation
    for coord in coords:
        coord[1] = -coord[1]

    return profile,CPs

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

def prepare_hydrophobic(coords,xi=0.8,display=False):
    """takes an array (n,2) of coordinate points, and returns the left and right halfdrops of the contour.
    xi determines the minimum steepness on the reachability plot that constitutes a cluster boundary of the
    clustering algorithm.
    deg is the degree of the polynomial used to describe the shape of the droplet.

    This code is adapted from the prepare module, but this version differs in that it assumes that the drop
    is hydrophobic."""
    # scan for clusers to remove noise and circle from lensing effect
                ################  MAY NEED TO OPTIMIZE eps/xi TO FIND APPROPRIATE GROUPINGS  ####################
    if display: # turn this off bc using synthetic drops without lensing effect
        input_contour = coords
        dic,dic2 = cluster_OPTICS(input_contour,xi=xi),cluster_OPTICS(input_contour,out_style='xy',xi=xi)

        #print("number of groups: ",len(list(dic.keys())))

        jet= plt.get_cmap('jet')
        colors = iter(jet(np.linspace(0,1,len(list(dic.keys())))))
        for k in dic.keys():
            plt.plot(dic2[str(k)+'x'],dic2[str(k)+'y'], 'o',color=next(colors))
        plt.title(str(len(dic.keys()))+" groups found by clustering")
        plt.show()
        plt.close()
        maxkey=max(dic, key=lambda k: len(dic[k]))

        #print('key to longest dictionary entry is: ',maxkey)

        # take the longest group
        longest = dic[maxkey]

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
    percent = 0.1
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

    dists = [] # find the average distance between points
    for n,co in enumerate(top_array):
        if 1<n:
            a = top_array[n]
            dist = np.linalg.norm(top_array[n]-top_array[n-1])
            dists.append(dist)

    if display:
        #print(dists)
        print()
        print('Max dist between points is: ',max(dists))
        print('Average dist between points is: ',sum(dists)/len(dists))
        print('20% over the Max dist is: ', max(dists)*1.2)
        print()
        print('Sort using cluster_OPTICS with an epsilon value of ',max(dists)*1.2)

    # how epsilon is chosen here is important
    #eps = (sum(dists)/len(dists))*2 # eps is 2 times the average distance between points
    eps = (sum(dists)/len(dists))*2.5 # eps is 2.5 times the average distance between points
    input_contour = longest
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
    #print('The x value of the apex is: ',xapex)

    l_drop = []
    r_drop = []
    for n in longest:
        if n[0] < xapex:
            l_drop.append(n)
        if n[0] > xapex:
            r_drop.append(n)
    l_drop = np.array(l_drop)
    r_drop = np.array(r_drop)



    # transpose both half drops so that they both face right and the apex of both is at 0,0
    r_drop[:,[0]] = r_drop[:,[0]] - xapex
    l_drop[:,[0]] = -l_drop[:,[0]] + xapex

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
        xhalfdrop = halfdrop[:,[0]].reshape(len(halfdrop[:,[0]]))
        yhalfdrop = halfdrop[:,[1]].reshape(len(halfdrop[:,[1]]))

        # isolate the bottom of the drop to help identify contact points (may not need to do this for all scenarios)
        bottom = []
        top = [] # will need this later
        #print('isolate the bottom ',percent*100,'% of the contour:') # percent defined above
        div_line_value = min(halfdrop[:,[1]]) + (max(halfdrop[:,[1]]) - min(halfdrop[:,[1]]))*percent
        for n in halfdrop:
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

        if display: # plot the bottom 10% of the contour
            plt.plot(xbottom, ybottom, 'b,')
            plt.title('bottom 10% of the contour')
            #plt.xlim([130,200])
            plt.show()
            plt.close()

        #### Continue here assuming that the drop is hydrophobic ####

        xCP = min(xbottom)
        yCP = []
        for coord in halfdrop:
            if coord[0]==xCP:
                yCP.append(coord[1])
        yCP =min(yCP)
        #print('The first few coordinates of xhalfdrop are: ', xhalfdrop[:3])

        #print('The coordinates of the contact point are (',xCP,',',yCP,')')

        CPs[counter] = [xCP, yCP]
        if 1:
            # order all halfdrop points using optimized_path (very quick but occasionally makes mistakes)

            new_halfdrop = sorted(halfdrop.tolist(), key=lambda x: (x[0],-x[1])) #top left to bottom right
            new_halfdrop = optimized_path(new_halfdrop)#[::-1]
            xnew_halfdrop = new_halfdrop[:,[0]].reshape(len(new_halfdrop[:,[0]]))
            ynew_halfdrop = new_halfdrop[:,[1]].reshape(len(new_halfdrop[:,[1]]))

            # remove surface line past the contact point

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
                            #print('indexes of the CP are: ',xCP_index[0],', ',yCP_index[0])
                            if new_halfdrop[xCP_index[0]+1][1]>new_halfdrop[xCP_index[0]-1][1]:
                                new_halfdrop = new_halfdrop[xCP_index[0]:]
                            else:
                                new_halfdrop = new_halfdrop[:xCP_index[0]+1]
                if raise_error == True:
                    print('The index of the contact point x value is: ', new_halfdrop[xCP_index])
                    print('The index of the contact point y value is: ', new_halfdrop[yCP_index])
                    raise 'indexes of x and y values of the contact point are not the same'

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
                                raise 'indexes of x and y values of the contact point are not the same'
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
            #print('Indexes of contour points past drop: ',surface_past_drop_index)


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
                    raise 'indexes of x and y values of the contact point are not the same'

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
                                #print('indexes of the CP are: ',xCP_index[0],', ',yCP_index[0])
                                if new_halfdrop[xCP_index[0]+1][1]>new_halfdrop[xCP_index[0]-1][1]:
                                    new_halfdrop = new_halfdrop[xCP_index[0]:]
                                else:
                                    new_halfdrop = new_halfdrop[:xCP_index[0]+1]
                    if raise_error == True:
                        print('The index of the contact point x value is: ', new_halfdrop[xCP_index])
                        print('The index of the contact point y value is: ', new_halfdrop[yCP_index])
                        raise 'indexes of x and y values of the contact point are not the same'

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

    # flip contour back to original orientation
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

def extract_edges_CV(img):
    '''
    give the image and return a list of [x.y] coordinates for the detected edges

    '''
    IGNORE_EDGE_MARGIN = 1
    img = img.astype("uint8")
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        gray = img
    #ret, thresh = cv2.threshold(gray,threshValue,255,cv2.THRESH_BINARY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
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
    return output

def tilt_correction(img, baseline):
    """img is an image input
    baseline is defined by two points in the image"""

    p1,p2 = baseline
    x1,y1 = p1
    x2,y2 = p2

    #assert(not x1 == x2 or y1 == y2)
    if y1 == y2:
        return img

    t = float(y2 - y1) / (x2 - x1)
    rotate_angle = math.degrees(math.atan(t))
    if rotate_angle > 45:
        rotate_angle = -90 + rotate_angle
    elif rotate_angle < -45:
        rotate_angle = 90 + rotate_angle
    rotate_img = ndimage.rotate(img, rotate_angle)
    #print('image rotated by '+str(rotate_angle)+' degrees')

    # crop black edges created when rotating
    width = np.sin(np.deg2rad(rotate_angle))
    side = math.ceil(abs(width*rotate_img.shape[1]))
    roof = math.ceil(abs(width*rotate_img.shape[0]))
    rotate_img_crop = rotate_img[roof:-roof,side:-side]

    return rotate_img_crop

def preprocess(img, display=False):
    """This code serves as a discrete instance of image preprocessing before contact
    angle fit software is implemented.

    This includes automatic identification of the drop through Hough transform,
    followed by cropping of the image to isolate the drop. Tilt correction is then
    performed using the identified contact points of the drop.
    An isolated (cropped) and tilt corrected image is outputted.
    """
    # preprocessing
    img_crop, bounds = auto_crop(img.copy())
    L,R,T,B = bounds
    edges_pts = extract_edges_CV(img_crop) # array of x,y coords where lines are detected

    if display:
        plt.imshow(img_crop)
        plt.plot(edges_pts[:,0],edges_pts[:,1])
        plt.title('drop found by hough transform')
        plt.show()
        plt.close()

    profile,CPs = prepare_hydrophobic(edges_pts,display)
    baseline = [CPs[0],CPs[1]]

    tilt_corrected_crop= tilt_correction(img_crop, baseline)

    if display:
        plt.imshow(tilt_corrected_crop)
        plt.title('tilt corrected and cropped image')
        plt.show()
        plt.close()

    return tilt_corrected_crop

def process_halfdrop(coords, percent=0.15, display=False):
    # isolate the top of the contour so excess surface can be deleted
    percent = 0.15
    bottom = []
    top = [] # will need this later
    div_line_value = min(coords[:,1]) + (max(coords[:,1]) - min(coords[:,1]))*percent
    for n in coords:
        if n[1] < div_line_value:
            bottom.append(n)
        else:
            top.append(n)

    bottom = np.array(bottom)
    top = np.array(top)

    # find the apex of the drop
    xtop,ytop = top[:,0],top[:,1] # isolate top 90% of drop
    xapex = (max(xtop) + min(xtop))/2

    del_indexes = []
    for index,coord in enumerate(coords):
        if coord[0]>max(top[:,0]) or coord[0]<min(top[:,0]):
            del_indexes.append(index)
    #halfdrop = np.delete(halfdrop,del_indexes)
    coords = np.delete(coords,del_indexes,axis=0)

    if display:
        plt.title('isolated coords, length: '+str(len(coords)))
        plt.plot(coords[:,0],coords[:,1])
        plt.show()
        plt.close()

    r_drop = []
    for n in coords:
        if n[0] > xapex:
            r_drop.append(n)
    r_drop = np.array(r_drop)

    #print('length of left drop is: ',len(l_drop))
    #print('length of right drop is: ', len(r_drop))

    # transpose half drop so the apex is at 0,0
    r_drop[:,[0]] = r_drop[:,[0]] - xapex
    halfdrop = r_drop

    if halfdrop[0,1]<halfdrop[-1,1]:
        halfdrop = halfdrop[::-1]

    X = halfdrop[:,0]
    Z = halfdrop[:,1]

    lowest = min(Z)
    Z = Z+abs(lowest)

    X = X/max(Z)
    Z = Z/max(Z)

    return X, Z

def save_to_new_dpi(img, dpi=256):
    plt.imshow(img)
    plt.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',pad_inches=0)# 256
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(img_arr, 1)
    plt.close()
    buf.close()

    return img

def prepare4model_v03_img(img, cluster=True, input_len=1223, right_only=False, display=False):
    """Take the contour of the whole drop, and chop it into left and right sides ready for model input"""

    edges = extract_edges_CV(img)

    if cluster == True:
        #xi = 0.8
        #dic,dic2 = cluster_OPTICS(edges,xi=xi),cluster_OPTICS(edges,out_style='xy',xi=xi)
        eps = 3
        dic,dic2 = cluster_OPTICS(edges,eps=eps),cluster_OPTICS(edges,out_style='xy',eps=eps)

        if display:
            jet= plt.get_cmap('jet')
            colors = iter(jet(np.linspace(0,1,len(list(dic.keys())))))
            for k in dic.keys():
                plt.plot(dic2[str(k)+'x'],dic2[str(k)+'y'], 'o',color=next(colors))
            plt.axis('equal')
            plt.title(str(len(dic.keys()))+" groups found by clustering")
            plt.show()
            plt.close()
        maxkey=max(dic, key=lambda k: len(dic[k]))

        # take the longest group
        longest = dic[maxkey]
    else:
        longest = edges

    coords = np.array(longest)

    coords[:,1] = - coords[:,1] # flip image coords to cartesian coords

    counter = 0
    CV_contours = {}
    flipped = np.copy(coords)
    flipped[:,0] = -coords[:,0]

    repeat = False
    for coords in [flipped,coords.copy()]: # for flipped and right side
        if 0:
            plt.title('check')
            plt.plot(coords[:,0],coords[:,1])
            plt.show()
            plt.close()

        # isolate the top of the contour so excess surface can be deleted
        X, Z = process_halfdrop(coords, display=display)

        # zero padd contours
        if input_len == None:
            input_len = len(X)

        coordinates = []

        # if image is too large and contour is too long, decrease image resolution
        max_contour_len = 599
        if len(X)>max_contour_len: # was input_len but was lowered to the max scaler 2 contour len
            if display==True:
                plt.plot(X,Z)
                plt.title('half-drop contour, length of '+str(len(X)))
                plt.show()
                plt.close()

                target_dpi = 100
                print("Contour of length "+str(len(X))+" is too long for the designated output dimensionality of ("+str(input_len)+",2)")
                print("reducing image resolution to "+str(target_dpi)+" dpi...")

                img = save_to_new_dpi(img, dpi=target_dpi)
                repeat = True
                break

            if display == True:
                plt.plot(X,Z)
                plt.title('half-drop contour, length of '+str(len(X)))
                plt.show()
                plt.close()
        elif len(X)<112:
            print('WARNING: contour shorter than shortest training data, inaccurate predictions likely')
            print('length of input is '+str(len(X)))

        for i in range(input_len):
            if i < len(X):
                a = X[i]
                b = Z[i]
                coord = [a,b]
                coordinates.append(coord)
            else:
                coordinates.append([0,0])
        if display:
            jet= plt.get_cmap('jet')
            colors = iter(jet(np.linspace(0,1,len(coordinates))))
            for k in coordinates:
                plt.plot(k[0],k[1], 'o',color=next(colors))
            if counter == 0:
                plt.title('Left halfdrop')
            elif counter == 1:
                plt.title('Right halfdrop')
            plt.show()
            plt.close()
        #key = image.split('/')[-1].split('_')[-1][:-4]
        key = counter
        CV_contours[key]= np.array(coordinates)

        counter += 1

    if repeat == True: #repeat the above with the resolution dropped
        edges = extract_edges_CV(img)

        if cluster == True:
            #xi = 0.8
            #dic,dic2 = cluster_OPTICS(edges,xi=xi),cluster_OPTICS(edges,out_style='xy',xi=xi)
            eps = 3
            dic,dic2 = cluster_OPTICS(edges,eps=eps),cluster_OPTICS(edges,out_style='xy',eps=eps)

            if display:
                jet= plt.get_cmap('jet')
                colors = iter(jet(np.linspace(0,1,len(list(dic.keys())))))
                for k in dic.keys():
                    plt.plot(dic2[str(k)+'x'],dic2[str(k)+'y'], 'o',color=next(colors))
                plt.axis('equal')
                plt.title(str(len(dic.keys()))+" groups found by clustering")
                plt.show()
                plt.close()
            maxkey=max(dic, key=lambda k: len(dic[k]))

            # take the longest group
            longest = dic[maxkey]
        else:
            longest = edges

        coords = np.array(longest)

        coords[:,1] = - coords[:,1] # flip image coords to cartesian coords

        counter = 0
        CV_contours = {}
        flipped = np.copy(coords)
        flipped[:,0] = -coords[:,0]
        for coords in [flipped,coords.copy()]: # for flipped and right side
            if 0:
                plt.title('check')
                plt.plot(coords[:,0],coords[:,1])
                plt.show()
                plt.close()

            # isolate the top of the contour so excess surface can be deleted
            X, Z = process_halfdrop(coords, display=display)

            # zero padd contours
            if input_len == None:
                input_len = len(X)

            coordinates = []

            # if image is too large and contour is too long, decrease image resolution
            if len(X)>max_contour_len:
                if display==True:
                    plt.plot(X,Z)
                    plt.title('half-drop contour, length of '+str(len(X)))
                    plt.show()
                    plt.close()

                print("Half-drop contour of length "+str(len(X))+" is too long for the designated output dimensionality of ("+str(input_len)+",2)")
                print("Continuing with every second point of the contour removed")

                X = X[::2]
                Z = Z[::2]

                if display == True:
                    plt.plot(X,Z)
                    plt.title('half-drop contour, length of '+str(len(X)))
                    plt.show()
                    plt.close()
            elif len(X)<112:
                print('WARNING: half-drop contour shorter than shortest training data, inaccurate predictions likely')
                print('length of input is '+str(len(X)))
            else:
                print('Half-drop contour of length '+str(len(X))+' is now in range')

            for i in range(input_len):
                if i < len(X):
                    a = X[i]
                    b = Z[i]
                    coord = [a,b]
                    coordinates.append(coord)
                else:
                    coordinates.append([0,0])
            if display:
                jet= plt.get_cmap('jet')
                colors = iter(jet(np.linspace(0,1,len(coordinates))))
                for k in coordinates:
                    plt.plot(k[0],k[1], 'o',color=next(colors))
                if counter == 0:
                    plt.title('Left halfdrop')
                elif counter == 1:
                    plt.title('Right halfdrop')
                plt.show()
                plt.close()
            #key = image.split('/')[-1].split('_')[-1][:-4]
            key = counter
            CV_contours[key]= np.array(coordinates)

            counter += 1

    if right_only == True:
        pred_ds = CV_contours[1]
    else:
        if input_len == None: # arrays must have consistent dimensions
            pred_ds = {}
            for counter in [0,1]:
                pred_ds[counter] = CV_contours[counter]
        else: #
            pred_ds = np.zeros((2,input_len,2))
            for counter in [0,1]:
                pred_ds[counter] = CV_contours[counter]

    return pred_ds

def prepare4model_v03(coords, input_len=1223, right_only=False, display=False):
    """Take the contour of the whole drop, and chop it into left and right sides ready for model input"""
    coords[:,1] = - coords[:,1] # flip image coords to cartesian coords

    counter = 0
    CV_contours = {}
    flipped = np.copy(coords)
    flipped[:,0] = -coords[:,0]

    for coords in [flipped,coords.copy()]: # for flipped and right side
        # isolate the top of the contour so excess surface can be deleted
        percent = 0.15
        bottom = []
        top = [] # will need this later
        div_line_value = min(coords[:,1]) + (max(coords[:,1]) - min(coords[:,1]))*percent
        for n in coords:
            if n[1] < div_line_value:
                bottom.append(n)
            else:
                top.append(n)

        bottom = np.array(bottom)
        top = np.array(top)

        # find the apex of the drop
        xtop,ytop = top[:,0],top[:,1] # isolate top 90% of drop
        xapex = (max(xtop) + min(xtop))/2

        del_indexes = []
        for index,coord in enumerate(coords):
            if coord[0]>max(top[:,0]) or coord[0]<min(top[:,0]):
                del_indexes.append(index)
        #halfdrop = np.delete(halfdrop,del_indexes)
        coords = np.delete(coords,del_indexes,axis=0)

        if display:
            plt.title('isolated coords, length: '+str(len(coords)))
            plt.plot(coords[:,0],coords[:,1])
            plt.show()
            plt.close()

        r_drop = []
        for n in coords:
            if n[0] > xapex:
                r_drop.append(n)
        r_drop = np.array(r_drop)

        #print('length of left drop is: ',len(l_drop))
        #print('length of right drop is: ', len(r_drop))

        # transpose and normalise half drop so the apex is at 0,1
        r_drop[:,[0]] = r_drop[:,[0]] - xapex
        halfdrop = r_drop

        if halfdrop[0,1]<halfdrop[-1,1]:
            halfdrop = halfdrop[::-1]

        X = halfdrop[:,0]
        Z = halfdrop[:,1]

        lowest = min(Z)
        Z = Z+abs(lowest)

        X = X/max(Z)
        Z = Z/max(Z)

        # zero padd contours
        if input_len == None:
            input_len = len(X)

        coordinates = []

        for i in range(input_len):
            if i < len(X):
                coordinates.append([X[i],Z[i]])
            else:
                coordinates.append([0,0])
        if display:
            jet= plt.get_cmap('jet')
            colors = iter(jet(np.linspace(0,1,len(coordinates))))
            for k in coordinates:
                plt.plot(k[0],k[1], 'o',color=next(colors))
            if counter == 0:
                plt.title('Left halfdrop')
            elif counter == 1:
                plt.title('Right halfdrop')
            plt.show()
            plt.close()
        #key = image.split('/')[-1].split('_')[-1][:-4]
        key = counter
        CV_contours[key]= np.array(coordinates)

        counter += 1

    if right_only == True:
        pred_ds = CV_contours[1]
    else:
        if input_len == None: # arrays must have consistent dimensions
            pred_ds = {}
            for counter in [0,1]:
                pred_ds[counter] = CV_contours[counter]
        else: #
            pred_ds = np.zeros((2,input_len,2))
            for counter in [0,1]:
                pred_ds[counter] = CV_contours[counter]

    return pred_ds

def experimental_pred(pred_ds, model, side='both', cluster=True, display=False):
    """Takes an input experimental image, and outputs the predicted contact
    angle based on the contour input model found in this folder:
    './modules/ML_model/'
    """

    start_time = time.time()

    if side == 'left':
        input_left = np.array([pred_ds[0,0]], dtype=np.float32)  # Convert to float32
        ML_prediction_start_time = time.time()

        # Use signatures approach instead of predict
        input_tensor = tf.convert_to_tensor(input_left)
        prediction_left = model.signatures['serving_default'](**{'conv1d_input': input_tensor})
        # Extract from result dictionary if needed
        if isinstance(prediction_left, dict):
            prediction_left = list(prediction_left.values())[0]
        # Convert tensor to numpy if needed
        if hasattr(prediction_left, 'numpy'):
            prediction_left = prediction_left.numpy()

        ML_prediction_time = time.time() - ML_prediction_start_time
        analysis_time = time.time() - start_time

        timings = {}
        timings['fit time'] = ML_prediction_time
        timings['analysis time'] = analysis_time

        if prediction_left > 180:
            prediction_left = 180
        elif prediction_left < 0:
            prediction_left = 0

        return prediction_left, timings

    if side == 'right':
        input_right = np.array([pred_ds[0,1]], dtype=np.float32)  # Convert to float32
        ML_prediction_start_time = time.time()

        # Use signatures approach instead of predict
        input_tensor = tf.convert_to_tensor(input_right)
        prediction_right = model.signatures['serving_default'](**{'conv1d_input': input_tensor})
        # Extract from result dictionary if needed
        if isinstance(prediction_right, dict):
            prediction_right = list(prediction_right.values())[0]
        # Convert tensor to numpy if needed
        if hasattr(prediction_right, 'numpy'):
            prediction_right = prediction_right.numpy()

        ML_prediction_time = time.time() - ML_prediction_start_time
        analysis_time = time.time() - start_time

        timings = {}
        timings['fit time'] = ML_prediction_time
        timings['analysis time'] = analysis_time

        if prediction_right > 180:
            prediction_right = 180
        elif prediction_right < 0:
            prediction_right = 0

        return prediction_right, timings

    if side == 'both':
        # Convert to float32
        pred_ds_float32 = pred_ds.astype(np.float32)
        ML_prediction_start_time = time.time()

        # Use signatures approach instead of predict
        input_tensor = tf.convert_to_tensor(pred_ds_float32)
        predictions = model.signatures['serving_default'](**{'conv1d_input': input_tensor})
        # Extract from result dictionary if needed
        if isinstance(predictions, dict):
            predictions = list(predictions.values())[0]
        # Convert tensor to numpy if needed
        if hasattr(predictions, 'numpy'):
            predictions = predictions.numpy()

        ML_prediction_time = time.time() - ML_prediction_start_time
        analysis_time = time.time() - start_time

        timings = {}
        timings['fit time'] = ML_prediction_time
        timings['analysis time'] = analysis_time

        if predictions[0] > 180:
            predictions[0] = 180
        elif predictions[0] < 0:
            predictions[0] = 0
        if predictions[1] > 180:
            predictions[1] = 180
        elif predictions[1] < 0:
            predictions[1] = 0

        return predictions, timings

def experimental_prediction(image, side='both', cluster=True, display=False):
    """Takes an input experimental image, and outputs the predicted contact
    angle based on the contour input model found in this folder:
    './modules/ML_model/'
    """

    start_time = time.time()

    model_path = './'
    model = tf.keras.models.load_model(model_path)

    if side == 'left':
        preprocessing_start_time = time.time()

        both_inputs = prepare4model_v03_img(image, input_len = 1223, cluster=cluster, display=display)
        input_left = np.array([both_inputs[0,0]])

        ML_preprocessing_time = time.time() - preprocessing_start_time
        ML_prediction_start_time = time.time()

        prediction_left = model.predict(input_left)

        ML_prediction_time = time.time() - ML_prediction_start_time
        analysis_time = time.time() - start_time

        timings = {}
        timings['method specific preprocessing time'] = ML_preprocessing_time
        timings['fit time'] = ML_prediction_time
        timings['analysis time'] = analysis_time

        if prediction_left > 180:
            prediction_left = 180
        elif prediction_left < 0:
            prediction_left = 0

        return prediction_left, timings

    if side == 'right':
        preprocessing_start_time = time.time()

        both_inputs = prepare4model_v03_img(image, input_len = 1223, cluster=cluster, display=display)
        input_right = np.array([both_inputs[0,1]])

        ML_preprocessing_time = time.time() - preprocessing_start_time
        ML_prediction_start_time = time.time()

        prediction_right = model.predict(input_right)

        ML_prediction_time = time.time() - ML_prediction_start_time
        analysis_time = time.time() - start_time

        timings = {}
        timings['method specific preprocessing time'] = ML_preprocessing_time
        timings['fit time'] = ML_prediction_time
        timings['analysis time'] = analysis_time

        if prediction_right > 180:
            prediction_right = 180
        elif prediction_right < 0:
            prediction_right = 0

        return prediction_right, timings

    if side == 'both':
        preprocessing_start_time = time.time()

        inputs = prepare4model_v03_img(image, input_len = 1223, cluster=cluster, display=display)

        ML_preprocessing_time = time.time() - preprocessing_start_time
        ML_prediction_start_time = time.time()

        predictions = model.predict(inputs)

        ML_prediction_time = time.time() - ML_prediction_start_time
        analysis_time = time.time() - start_time

        timings = {}
        timings['method specific preprocessing time'] = ML_preprocessing_time
        timings['fit time'] = ML_prediction_time
        timings['analysis time'] = analysis_time

        if predictions[0] > 180:
            predictions[0] = 180
        elif predictions[0] < 0:
            predictions[0] = 0
        if predictions[1] > 180:
            predictions[1] = 180
        elif predictions[1] < 0:
            predictions[1] = 0

        return predictions, timings

if 0:
    IMG_PATH = '../../RICOphobic_cropped.png'
    img = cv2.imread(IMG_PATH)
    predictions, timings = experimental_prediction(img, display=True)
    print()
    print('predictions: ',predictions)
    print('timings: ',timings)

    print()
