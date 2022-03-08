#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 17:27:33 2021

@author: julien_joseph
"""

from math import*
import numpy as np
from random import*
import os
import sys
import matplotlib.pyplot as plt
import argparse


parser = argparse.ArgumentParser(
        description='This program allows you detect the hotspots from a recombination map in a bed format'
                    'For more information read the userguide',
        usage='python hotspot_detection.py -dirpath [WORKING DIRECTORY PATHWAY] -i [RECOMBINATION MAP] -o [OUTPUT NAME] -fld [Fold] -bck [Background size] -size [Hotspot size] -rcol [Recrate column] -sm -res [Resolution]',
        formatter_class=argparse.RawTextHelpFormatter, add_help=False)
parser.add_argument("-o", "--output_file", help="bed file")
parser.add_argument("-idir", "--input_directory", help="bed file")
parser.add_argument("-h", "--help", help="help", action="store_true")
args = parser.parse_args()



def circular_hist(ax, x, bins=16, density=True, offset=0, gaps=True):
    """
    Produce a circular histogram of angles on ax.

    Parameters
    ----------
    ax : matplotlib.axes._subplots.PolarAxesSubplot
        axis instance created with subplot_kw=dict(projection='polar').

    x : array
        Angles to plot, expected in units of radians.

    bins : int, optional
        Defines the number of equal-width bins in the range. The default is 16.

    density : bool, optional
        If True plot frequency proportional to area. If False plot frequency
        proportional to radius. The default is True.

    offset : float, optional
        Sets the offset for the location of the 0 direction in units of
        radians. The default is 0.

    gaps : bool, optional
        Whether to allow gaps between bins. When gaps = False the bins are
        forced to partition the entire [-pi, pi] range. The default is True.

    Returns
    -------
    n : array or list of arrays
        The number of values in each bin.

    bins : array
        The edges of the bins.

    patches : `.BarContainer` or list of a single `.Polygon`
        Container of individual artists used to create the histogram
        or list of such containers if there are multiple input datasets.
    """
    # Wrap angles to [-pi, pi)
    x = (x+np.pi) % (2*np.pi) - np.pi
    # Force bins to partition entire circle
    if not gaps:
        bins = np.linspace(-np.pi, np.pi, num=bins+1)

    # Bin data and record counts
    n, bins = np.histogram(x, bins=bins)
    print(n)

    # Compute width of each bin
    widths = np.diff(bins)
    print(widths)

    # By default plot frequency proportional to area
    if density:
        # Area to assign each bin
        area = n / x.size
        # Calculate corresponding bin radius
        radius = (area/np.pi) ** .5
    # Otherwise plot frequency proportional to radius
    else:
        radius = n
    print(radius)
    # Plot data on ax
    patches = ax.bar(bins[:-1], radius, zorder=1, align='edge', width=widths,
                     edgecolor='black', linewidth=1, color='lightgrey')

    # Set the direction of the zero angle
    ax.set_theta_offset(offset)

    # Remove ylabels for area plots (they are mostly obstructive)
    if density:
        ax.set_yticks([])

    return n, bins, patches

def turning_angles(file):
    fichier=open(file,'r')
    txt=fichier.readline().split()
    X=[]
    Y=[]
    angle=[]
    xinit=float(txt[0])
    yinit=float(txt[1])
    while txt!=[]:
        X.append((float(txt[0])-xinit)*55800)
        Y.append((float(txt[1])-yinit)*55800)
        del txt
        txt=fichier.readline().split()
    for i in range(2,len(X)):
        x=X[i]-X[i-1]
        y=Y[i]-Y[i-1]
        d=sqrt(x**2+y**2)
        x1=X[i-1]-X[i-2]
        y1=Y[i-1]-Y[i-2]
        d1=sqrt(x1**2+y1**2)
        if d*d1!=0:
            p=x*y1-x1*y
            a=(x*x1+y*y1)/(d1*d)
            a=np.clip(a,-1,1)
            if p<0:
                alpha=np.arccos(a)
            else:
                alpha=-np.arccos(a)
            angle.append(alpha)
    #plt.plot(X,Y)
    #plt.grid()
    #plt.show()
    return(angle)

angle=[]
for file in os.listdir(args.input_directory):
    angle=angle+turning_angles(args.input_directory+'/'+file)
print(len(angle))
fig, ax = plt.subplots(1, 1, subplot_kw=dict(projection='polar'))
#rose_plot(ax[0],np.asarray(angle_vertical))
circular_hist(ax,np.asarray(angle))
fig.tight_layout()
plt.savefig(args.output_file,dpi=500)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        