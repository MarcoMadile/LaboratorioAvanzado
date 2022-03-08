#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 15:49:09 2021

@author: julien_joseph
"""

from math import*
import numpy as np
from random import*
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.axes as ax
import argparse
from scipy import stats
import seaborn as sns
import copy
from collections import OrderedDict

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
    
import geopy.distance

coords_1 = (52.2296756, 21.0122287)
coords_2 = (52.406374, 16.9251681)

print(geopy.distance.distance(coords_1, coords_2).m)


def draw_trajectory(file,x,y,t,d,metodo,tfilter):
    sortie=open('coordenadas.txt','a')
    output=open(file+'.filtered','w')
    #print(file)
    day_color={'29/11/2020':'blue','30/11/2020':'orange','1/12/2020':'black','2/12/2020':'red','3/12/2020':'darkgreen','6/3/2020':'blue','7/3/2020':'orange','10/1/2021':'blue','11/1/2021':'orange','12/1/2021':'black','13/1/2021':'red','14/1/2021':'darkgreen','15/1/2021':'dimgrey'}
    day_color2={'29/11/2020':'blue','30/11/2020':'blue','1/12/2020':'blue','2/12/2020':'blue','3/12/2020':'blue','6/3/2020':'lime','7/3/2020':'lime','10/1/2021':'darkred','11/1/2021':'darkred','12/1/2021':'darkred','13/1/2021':'darkred','14/1/2021':'darkred','15/1/2021':'darkred'}
    macho={'macho':'purple','hembra':'orange'}
    day_marker={'29/11/2020':'x','30/11/2020':'x','1/12/2020':'x','2/12/2020':'x','3/12/2020':'x','6/3/2020':'.','7/3/2020':'.','10/1/2021':'s','11/1/2021':'s','12/1/2021':'s','13/1/2021':'s','14/1/2021':'s','15/1/2021':'s'}
    fichier=open(file,'r')
    txt=fichier.readline().split()
    del txt
    txt=fichier.readline().split()
    xinit=float(txt[x])
    yinit=float(txt[y])
    xi=float(txt[x])
    yi=float(txt[y])
    X=[]
    Y=[]
    T=[]
    S=[]
    max_dist=[]
    ti=txt[t]
    del txt
    txt=fichier.readline().split()
    day='0'
    Distance=[]
    while txt!=[]:
        sexo=txt[6]
        #if txt[metodo]!='GPS':
            #print(txt[metodo])
        if txt[metodo]=='GPS':
            if day!=txt[d] and day!='0':
                #plt.plot(X,Y,label=day,color=day_color2[day],alpha=0.5)
                #print(txt)
                sexo=txt[6]
                #print(sexo)
                plt.scatter(X,Y,s=10,color=day_color2[day],alpha=0.5,label=day)#,marker=day_marker[day])
                #plt.legend()
                #plt.scatter(X[0],Y[0],s=40)
                if Distance!=[]:
                    max_dist.append(max(Distance))
                X=[]
                Y=[]
                T=[]
                Distance=[]
                ti=txt[t]
                xinit=float(txt[x])
                yinit=float(txt[y])
                xi=float(txt[x])
                yi=float(txt[y])
            day=txt[d]
            coords_1=(float(txt[x]),float(txt[y]))
            coords_2=(float(txt[x]),float(txt[y]))
            a=geopy.distance.distance(coords_1, coords_2).km(float(txt[x])-xinit)
            b=(float(txt[y])-yinit)
            if X!=[]:
                a1=a-X[-1]
                b1=b-Y[-1]
                time=time2minute(T[-1],txt[t])
                #print(T[-1])
            else:
                a1=(float(txt[x])-xi)
                b1=(float(txt[y])-yi)
                time=time2minute(ti,txt[t])
            #print(time2minute(tinit,txt[t]))
            coords_1=(float(txt[x]),float(txt[y]))
            coords_2=(xi,yi)
            step=geopy.distance.distance(coords_1, coords_2).km
            dist=geopy.distance.distance(coords_1, coords_2).km
            print(step)
            if time!=0:
                speed=60*step/(time)
                if speed!=0 and speed<0.5:
                    #print(txt[x],speed)
                    for i in range(len(txt)-1):
                        output.write(txt[i]+'\t')
                    output.write(txt[-1]+'\n')
                    #print(speed,step,time,txt[t])
                    #print()
                    #if float(ti)<1200 and int(txt[t])>1200 and int(txt[t])<2200:
                    #if sexo == 'hembra':
                    Distance.append(dist)
                    X.append(a)
                    Y.append(b)
                    sortie.write(str(a)+'\t'+str(b)+'\n')
                    if a<-200:
                        print(a)
                    if b<-200:
                        print(b)
                    T.append(txt[t])
                    if time==10:
                        #print(file)
                        S.append(log10(step/10))
        del txt
        txt=fichier.readline().split()
    #plt.plot(X,Y,label=day,color=day_color2[day],alpha=0.5)
    if day!='0':
        a=0
        #plt.scatter(X,Y,s=10,color=day_color2[day],alpha=0.5)#,marker=day_marker[day])
    fichier.close()
    if Distance!=[]:
        max_dist.append(max(Distance))
    plt.xlabel('x (meters)')
    plt.ylabel('y (meters)')
    sortie.close()
    #print(max_dist)
    #plt.legend()
    #plt.savefig(/home/julien_joseph/Tortugas/figures/file.strip('.txt')+'.png',dpi=500)
    #plt.show()
    #if Distance!=[]:
        #print(max(Distance))
    output.close()
    #plt.xlim(right=0.001,left=-0.0005)
    #plt.ylim(top=0.001,bottom=-0.001)
    return(max_dist)

plt.grid()
os.chdir("/home/julien_joseph/Tortugas/data/noviembre-diciembre_2020")

S=[]
#S=S+draw_trajectory('T10_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T11_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T12_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T29_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T30_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T55_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T56_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T79_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T100_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T133_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T169_2020.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T171_2020.txt',0,1,3,2,5,0)


os.chdir("/home/julien_joseph/Tortugas/data/enero_2021")

#S=S+draw_trajectory('T010_2021.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T030_2021.txt',0,1,3,2,5,0)
S=S+draw_trajectory('T079_2021.txt',0,1,3,2,5,0)
#S=S+draw_trajectory('T129_2021.txt',0,1,3,2,5,0)

os.chdir("/home/julien_joseph/Tortugas/data/marzo_2020")

#S=S+draw_trajectory('T29_marzo_2020.txt',0,1,3,2,5,0)
#print(max(S))
os.chdir("/home/julien_joseph/Tortugas/figures")
handles, labels = plt.gca().get_legend_handles_labels()
#for i in range(len(labels)):
#    if labels[i]=='macho':
#        labels[i]='males'
#    if labels[i]=='hembra':
#        labels[i]='females'
for i in range(len(labels)):
    if labels[i][-1]=='1':
        labels[i]='2021'
    if labels[i][-1]=='0':
        labels[i]='2020'

by_label = OrderedDict(zip(labels, handles))
print(labels)
#print(by_label.keys())
#by_label['03/2020']=by_label['/3/2020']
#by_label['01/2021']=by_label['/1/2021']
#del by_label['/3/2020']
#del by_label['/1/2021']
plt.legend(by_label.values(), by_label.keys())
plt.savefig('all_turtles_sexo.png',dpi=500)
plt.show()
"""
plt.hist(S,bins=30,color='grey',edgecolor='dimgrey')
#plt.axvline(x=-1.35,color='red')
plt.xlabel('log(speed) in m/min')
plt.ylabel('number of 10 minutes intervals')
plt.savefig('speed_distribution.png',dpi=500)
plt.show()
"""
"""
SmGPS=[36.427144345436744, 76.84170571309537, 134.96505541297165, 222.25350142072992, 75.4415380919532, 62.191772284392925, 51.294072225776354, 22.88058570734175, 78.48267520447567, 104.91481811237333, 29.097493061095147]
ShGPS=[94.53114544455605, 15.200763941433689, 72.53512806686997, 298.1931586567473, 119.8503986159212, 46.80352855917577, 6.002067544036755, 51.16799149086804, 17.745891447150818, 13.457983696033214, 8.049137911713572, 42.09794749587106, 52.483719239433974, 43.60894057718359, 119.99138376854376, 89.16750957003737, 74.78407514416604, 142.0634795761865, 20.11557107969486, 126.57981252735179, 32.16118572293186, 142.68797579740593, 316.57686306489353, 25.38973581337036, 37.376546118275684, 40.880079299546615, 22.256087243582744, 129.4154063514252, 136.2677243847934, 74.91629532181857, 214.8871040734464, 17.82956261599421, 4.165611086160071, 36.666035213421736, 55.52327120982203]

S2020GPS=[36.427144345436744, 94.53114544455605, 15.200763941433689, 72.53512806686997, 298.1931586567473, 119.8503986159212, 46.80352855917577, 6.002067544036755, 51.16799149086804, 17.745891447150818, 13.457983696033214, 8.049137911713572, 42.09794749587106, 52.483719239433974, 43.60894057718359, 119.99138376854376, 89.16750957003737, 76.84170571309537, 134.96505541297165, 222.25350142072992, 75.4415380919532, 62.191772284392925]
S2021GPS=[51.294072225776354, 22.88058570734175, 78.48267520447567, 104.91481811237333, 29.097493061095147, 74.78407514416604, 142.0634795761865, 20.11557107969486, 126.57981252735179, 32.16118572293186, 142.68797579740593, 316.57686306489353, 25.38973581337036, 37.376546118275684, 40.880079299546615, 22.256087243582744, 129.4154063514252, 136.2677243847934, 74.91629532181857, 214.8871040734464, 17.82956261599421, 4.165611086160071]

Sh=[52.12150132076367, 116.65536843172605, 13.622516067292718, 64.71356735654702, 56.45735796162545, 94.53114544455605, 15.200763941433689, 69.41486358466294, 298.1931586567473, 47.75335832594279, 32.95508507061656, 19.24088864863067, 161.27068834769713, 14.773833760871687, 6.1633114475725375, 45.8284825896892, 51.16799149086804, 17.745891447150818, 13.457983696033214, 42.09794749587106, 52.483719239433974, 45.27773744172287, 119.99138376854376, 74.78407514416604, 142.0634795761865, 20.11557107969486, 126.57981252735179, 32.16118572293186, 316.57686306489353, 25.38973581337036, 37.376546118275684, 40.880079299546615, 22.256087243582744, 136.2677243847934, 74.91629532181857, 214.8871040734464, 17.82956261599421, 36.666035213421736]
Sm=[74.87395288119195, 63.076217324940245, 244.9969519485661, 44.935459716775526, 38.55420634471257, 16.297039363121154, 116.14579329477512, 173.1104508105891, 51.70164349409744, 55.16303447124727, 82.47270202903611, 8.499202786030605, 21.012238148494514, 235.71454978430796, 69.88735595479089, 136.14180010949056, 223.73034180684584, 75.4415380919532, 51.294072225776354, 22.88058570734175, 78.48267520447567, 104.91481811237333]

S2020=[74.87395288119195, 63.076217324940245, 244.9969519485661, 44.935459716775526, 38.55420634471257, 16.297039363121154, 52.12150132076367, 116.65536843172605, 13.622516067292718, 64.71356735654702, 56.45735796162545, 94.53114544455605, 15.200763941433689, 69.41486358466294, 298.1931586567473, 47.75335832594279, 32.95508507061656, 19.24088864863067, 161.27068834769713, 116.14579329477512, 173.1104508105891, 51.70164349409744, 55.16303447124727, 14.773833760871687, 6.1633114475725375, 82.47270202903611, 8.499202786030605, 21.012238148494514, 235.71454978430796, 45.8284825896892, 51.16799149086804, 17.745891447150818, 13.457983696033214, 42.09794749587106, 52.483719239433974, 45.27773744172287, 119.99138376854376, 69.88735595479089, 136.14180010949056, 223.73034180684584, 75.4415380919532]
S2021=[51.294072225776354, 22.88058570734175, 78.48267520447567, 104.91481811237333, 74.78407514416604, 142.0634795761865, 20.11557107969486, 126.57981252735179, 32.16118572293186, 316.57686306489353, 25.38973581337036, 37.376546118275684, 40.880079299546615, 22.256087243582744, 136.2677243847934, 74.91629532181857, 214.8871040734464, 17.82956261599421]

plt.show()
plt.grid(ls='--')
print(stats.kruskal(Sm,Sh))
print(stats.kruskal(S2020,S2021))
print((np.asarray(S2020).mean()*len(S2020)+np.asarray(S2021).mean()*len(S2021))/(len(S2020)+len(S2021)))
print((np.asarray(Sm).mean()*len(Sm)+np.asarray(Sh).mean()*len(Sh))/(len(Sm)+len(Sh)))
print(np.asarray(Sm).mean())
print(np.asarray(Sh).mean())
print(stats.sem(np.asarray(Sm+Sh)))
sns.violinplot(data=[S2020,S2021],saturation=1,palette="seismic")#,scale='count')
plt.xticks([0,1],['Spring 2020','Summer 2021'])
plt.ylabel('maximum daily distance (m)')
plt.ylim(bottom=0)
plt.legend(loc='upper left',title='Krustal-Wallis p-value= '+str(round(stats.kruskal(S2020,S2021)[1],2)))
plt.savefig('max_distance_temporadaGPS.png',dpi=500)
"""




    