#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 14:41:37 2022

@author: julien_joseph
"""


from math import*
import numpy as np
from random import*
import os
import sys
import matplotlib.pyplot as plt
import argparse
import warnings
import pandas as pd
import geopy.distance as gp
import copy


parser = argparse.ArgumentParser(
        description='This program allows you detect the hotspots from a recombination map in a bed format'
                    'For more information read the userguide',
        usage='python hotspot_detection.py -dirpath [WORKING DIRECTORY PATHWAY] -i [RECOMBINATION MAP] -o [OUTPUT NAME] -fld [Fold] -bck [Background size] -size [Hotspot size] -rcol [Recrate column] -sm -res [Resolution]',
        formatter_class=argparse.RawTextHelpFormatter, add_help=False)
parser.add_argument("-o", "--output_file", help="bed file")
parser.add_argument("-i", "--input_file", help="bed file")
parser.add_argument("-t", "--threshold", help="in km/h", default=1.0,type=float)
parser.add_argument("-h", "--help", help="help", action="store_true")
args = parser.parse_args()




dic_color={'1/12/2020':'black','2/12/2020':'crimson','3/12/2020':'dodgerblue','10/1/2021':'dimgrey','11/1/2021':'pink','12/1/2021':'purple','13/1/2021':'orange','14/1/2021':'lime','15/1/2021':'blue','29/11/2020':'green','30/11/2020':'orangered'}

a=pd.read_csv(args.input_file, sep='\t', engine='python')
coord_init=(a['lat'][0],a['lon'][0])
X={}
Y={}
for i in range(len(a)):
    coord=(a['lat'][i],a['lon'][i])
    if a['lat'][i]-a['lat'][0]>0:
        distx=gp.distance((coord[0],0),(coord_init[0],0)).m
    else:
        distx=-gp.distance((coord[0],0),(coord_init[0],0)).m
    if a['lon'][i]-a['lon'][0]>0:
        disty=gp.distance((0,coord[1]),(0,coord_init[1])).m
    else:
        disty=-gp.distance((0,coord[1]),(0,coord_init[1])).m
    if a['date'][i] not in X:
        X[a['date'][i]]=[]
        Y[a['date'][i]]=[]
    X[a['date'][i]].append(distx)
    Y[a['date'][i]].append(disty)

for date in X:
    plt.plot(X[date],Y[date],color=dic_color[date])
    plt.scatter(X[date],Y[date],color=dic_color[date],s=7)
plt.grid()
plt.savefig(args.output_file,dpi=500)
plt.close()























