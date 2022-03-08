#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 17:36:24 2022

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
import seaborn as sns
from scipy import stats

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


def time2minute(x,y):
    #print(x,y)
    while len(y)<4:
        y='0'+y
    while len(x)<4:
        x='0'+x
    h1=int(x[0:2])
    m1=int(x[2:4])
    h2=int(y[0:2])
    m2=int(y[2:4])
    time=60*(h2-h1)+m2-m1
    return(time)
  
    
cat1=[]
cat2=[]
for file in os.listdir(args.input_directory):
    a=pd.read_csv(args.input_directory+'/'+file, sep='\t', engine='python')
    if time2minute(str(a['time'][0]),str(a['time'][len(a)-1]))>600:
        coord_init=(a['lat'][0],a['lon'][0])
        dist_max=0
        for i in range(len(a)):
            coord=(a['lat'][i],a['lon'][i])
            dist=gp.distance(coord,coord_init).m
            dist_max=max(dist,dist_max)
        if args.category=='sex':
            if a['sexo'][0]=='macho':
                cat1.append(dist_max)
            else:
                cat2.append(dist_max)
        if args.category=='season':
            if a['date'][0].split('.')[2]=='2020':
                cat1.append(dist_max)
            else:
                cat2.append(dist_max)
                

if args.category=='sex':
    sns.violinplot(data=[cat1,cat2],saturation=1,palette="PuOr")#,scale='count')
    plt.xticks([0,1],['Males','Females'])
elif args.category=='season':
    sns.violinplot(data=[cat1,cat2],saturation=1,palette="seismic")#,scale='count')
    plt.xticks([0,1],['Spring 2020','Summer 2021'])

plt.ylim(bottom=0)
plt.legend(loc='upper left',title='Krustal-Wallis p-value= '+str(round(stats.kruskal(cat1,cat2)[1],2)))
plt.savefig(args.output_file,dpi=500)
plt.close()
