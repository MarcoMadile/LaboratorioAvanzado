from matplotlib.pyplot import draw
import pandas as pd 
import glob
import numpy as np
from geopy import distance 
import folium
from datetime import datetime

#fixing time because some files have time=8 when i want time= 0008 (so then i have it in same format)
def fixing_time(x):
    x=str(x)
    if len(x)==4:
        return x
    elif len(x)==2:
        return "00"+x
    else:
        return "0"+x

#getting all files in folder 
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

def check_encounters(df,dates,mindist):
    colors=["red","green","yellow","grey","pink","aqua","purple","white","black","brown","lime","beige"]
    for day in dates: 
        map1=get_map()
        for i in range(len(df)):
            for j in range(i+1,len(df)):
                draw_near_points(df[i],df[j],colors[i],colors[j],map1,mindist,day)
        name=str(day)+"_nearpoints"+".html"
        name=name.replace("/","_")
        print("guarde el día ",day)
        map1.save(name)

def get_map():
    coords=[-40.585390,-64.996220]
    map1 = folium.Map(location = coords,zoom_start=15)
    folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community").add_to(map1)
    return map1 


def draw_near_points(df1,df2,color1,color2,map1,mindist,day):
    #draw1=lambda x,y: folium.CircleMarker((x,y),radius=3,stroke=False,fill=True,fill_color=color1,fill_opacity=1).add_to(map1)
    #vfun1=np.vectorize(draw1)
    points1=get_cordinates_from_day(df1,day)
    points2=get_cordinates_from_day(df2,day)
    if ((len(points1)>0) and (len(points2)>0)):
        for point1 in points1:
            distances=np.array([(distance.distance(x,point1).m) for x in points2]).astype(int)
            indexes=np.where(distances<mindist)#where the distance is smaller from min distance
            for k in indexes[0]:
                
                dt=get_delta_time(df1,df2,day,point1,points2[k])
                dx=distances[k]
                x2=points2[k]
                folium.PolyLine([x2,point1],color=color1,weight=2.5, opacity=0.5,popup="dt = "+str(dt)+" and dr ="+str(dx)).add_to(map1)

                folium.CircleMarker([x2[0],x2[1]],radius=3,stroke=False,fill=True,fill_color=color2,fill_opacity=1).add_to(map1)

                folium.CircleMarker([point1[0],point1[1]],radius=3,stroke=False,fill=True,fill_color=color1,fill_opacity=1).add_to(map1)
    

def get_cordinates_from_day(df,day):
    points=zip(df.loc[df['date']==day]["lat"],df.loc[df['date']==day]["lon"])
    points=np.array(list(points))
    return points

def get_delta_time(df1,df2,day,point1,point2):
    t1=pd.to_datetime(df1.loc[df1["date"]==day].loc[df1["lat"]==point1[0]]["time"],format="%H%M")
    t2=pd.to_datetime(df2.loc[df2["date"]==day].loc[df2["lat"]==point2[0]]["time"],format="%H%M")
    t1=t1.to_numpy()
    t2=t2.to_numpy()
    dt=((t1[0]-t2[0]).astype('timedelta64[s]')).astype("int")
    return dt/60

folder="TrayectoriasGPS"
df,dates=get_files_and_dates(folder)
mindist=20
check_encounters(df,dates,mindist)