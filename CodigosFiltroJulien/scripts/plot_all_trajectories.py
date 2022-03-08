#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 15:49:21 2022

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
parser.add_argument("-idir", "--input_directory", help="bed file")
parser.add_argument("-c", "--category", help="bed file")
parser.add_argument("-h", "--help", help="help", action="store_true")
args = parser.parse_args()



dic_color_season={'2020':'blue','2021':'darkred'}
dic_color_sex={'macho':'purple','hembra':'orange'}

if args.category=='sex':
    dic_color=dic_color_sex
elif args.category=='season':
    dic_color=dic_color_season
else:
    raise Exception('Wrong category')
    
    

for file in os.listdir(args.input_directory):
    a=pd.read_csv(args.input_directory+'/'+file, sep='\t', engine='python')
    if len(a)==8:
        print(a,file)
    coord_init=(a['lat'][0],a['lon'][0])
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
        if args.category=='sex':
            plt.scatter(distx,disty,color=dic_color_sex[a['sexo'][i]],s=5)
        elif args.category=='season':
            plt.scatter(distx,disty,color=dic_color_season[a['date'][i].split('.')[2]],s=5)
        
plt.grid()
plt.xlabel('x (meters)')
plt.ylabel('y (meters)')
plt.savefig(args.output_file,dpi=500)
plt.close()
