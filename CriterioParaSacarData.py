import pandas as pd 
import glob
import numpy as np
from geopy import distance 
import folium

#it takes out points that went two far and are alone, it also takes out first points if they are far away from each other. To check this it compares velocities. 
def fixing_time(x):
    x=str(x)
    if len(x)==4:
        return x
    elif len(x)==2:
        return "00"+x
    else:
        return "0"+x

#getting all files in folder trayectoriasGPS
def get_files_and_dates(folder):
    filenames=folder+"/*.csv"
    files=glob.glob(filenames)
    df=[]
    for a in files:
        df.append(pd.read_csv(a,sep=";"))
    dates=[]
    for j in range(len(df)):
        dates.append(np.unique(df[j]["date"]))
        df[j]["time"]=df[j]["time"].apply(fixing_time)
    dates=np.unique(np.concatenate(dates).ravel())
    return df,dates

#calculates velocities and extract the points 
def fix_some_points(df,dates,v0):
    mindata=4 #minimum amount of data to fix points 
    for day in dates:
        for j in range(len(df)):
            if len(df[j].loc[df[j]['date']==day])>mindata:
                points=zip(df[j].loc[df[j]['date']==day]["lat"],df[j].loc[df[j]['date']==day]["lon"])
                points=np.array(list(points))
                dist = [distance.distance(x,y).m for x, y in zip(points[1:],points[:-1])]
                dist=(np.array(dist)).astype("int")
                time=pd.to_datetime(df[j].loc[df[j]['date']==day]["time"],format="%H%M")
                time=np.array(time)
                deltatimes=((time[1:]-time[:-1]).astype('timedelta64[s]')).astype("int") 
                vel=np.divide(dist,deltatimes)
                indexes=np.where(vel>v0)
                i=0
                while i < len(indexes[0]):
                    if indexes[0][i]==0:
                        row=df[j].loc[df[j]["date"]==day].loc[df[j]["lat"]==points[0][0]].index[0]
                        df[j] = df[j].drop(labels=row, axis=0)
                        i+=1
                        if i<len(indexes[0]):
                            if indexes[0][i]==1:
                                row=df[j].loc[df[j]["date"]==day].loc[df[j]["lat"]==points[1][0]].index[0]
                                df[j]= df[j].drop(labels=row, axis=0)
                                i+=1
                    if i<len(indexes[0]):
                        if indexes[0][i]==len(vel)-1:
                           # print("antes de borrarcon j= "+str(j)+"  "+str(len(df[j])))
                            row=df[j].loc[df[j]["date"]==day].loc[df[j]["lat"]==points[-1][0]].index[0]
                            print(row)
                            df[j]= df[j].drop(labels=row, axis=0)
                            i+=1
                            #takes last row
                        else: #now i know that this point is in the middle
                            if  i<len(indexes[0])-1:
                                if (indexes[0][i+1]-indexes[0][i])==1:
                                    indx=indexes[0][i+1]
                                    row=df[j].loc[df[j]["date"]==day].loc[df[j]["lat"]==points[indx][0]].index[0]
                                    df[j]=df[j].drop(labels=row, axis=0)
                            i+=1

#makes maps by day, each color represents different tortugues 
def make_day_maps(df,dates):
    colors=["red","green","yellow","grey","pink","aqua","purple","white","black","brown","lime","beige"]
    for day in dates:
        coords=[-40.585390,-64.996220]
        map1 = folium.Map(location = coords,zoom_start=15)
        #this tile is for seeing the terrain  
        folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community").add_to(map1)
        for j in range(len(df)):
            if len(df[j].loc[df[j]['date']==day])>4:
                points=zip(df[j].loc[df[j]['date']==day]["lat"],df[j].loc[df[j]['date']==day]["lon"])
                points=list(points)
                folium.PolyLine(points,color=colors[j],weight=2.5, opacity=0.5).add_to(map1)
                for x in points: 
                    folium.CircleMarker(x,radius=3,stroke=False,fill=True,fill_color=colors[j],fill_opacity=1).add_to(map1)
        name=str(day)+"_fixed"+".html"
        name=name.replace("/","_")
        map1.save(name) #saving the map by day 
                        

#to be changed 
folder="TrayectoriasGPS"
df,dates=get_files_and_dates(folder)
vmax=10
print("antes"+str(len(df[8])))

fix_some_points(df,dates,vmax)
print("despues"+str(len(df[8])))
make_day_maps(df,dates)
