#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 09:27:00 2022

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
parser.add_argument("-odir", "--output_directory", help="bed file")
parser.add_argument("-i", "--input_file", help="bed file")
parser.add_argument("-t", "--threshold", help="in km/h", default=1.0,type=float)
parser.add_argument("-h", "--help", help="help", action="store_true")
args = parser.parse_args()



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

a=pd.read_csv(args.input_file, sep='\t', engine='python')
it=0
p=0
k=1
while k!=0:
    if p==1:
        a=pd.read_csv(args.output_directory+'/temp', sep='\t', engine='python')
    a2=pd.DataFrame.copy(a,deep=True)
    for i in range(1,len(a)):
        dist=gp.distance((a['lat'][i],a['lon'][i]),(a['lat'][i-1],a['lon'][i-1])).km
        tiempo=time2minute(str(a['time'][i-1]),str(a['time'][i]))
        #print(dist,tiempo)
        if tiempo!=0:
            if 60*dist/tiempo>args.threshold:
                a2=a2.drop(labels=i,axis=0)
    k=len(a.index)-len(a2.index)
    a2.to_csv(args.output_directory+'/temp',sep='\t',index=False)
    p=1
    it=it+1

print(args.input_file,it,'iterations')

