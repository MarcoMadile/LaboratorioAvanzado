import folium
import webbrowser
import pandas as pd
import numpy as np
import glob
#quiero levantar todos los csv 
#e ir graficando trayectorias por fecha 
#me armo un vector que tenga la union de todas las fechas y de ahí paso fecha por fecha recorriendo los csv y graficando 
#elijo una fecha recorro todos los csv 
#trayectoriasGPS is the path where i have each csv for each tortugue, it can be changed
files=glob.glob("trayectoriasGPS\*.csv")
df=[]
for a in files:
    df.append( pd.read_csv(a,sep=";"))

colors=["red","green","yellow","grey","pink","aqua","purple","white","black","brown","lime","beige"]
dates=[]
for tort in df:
    dates.append(np.unique(tort["date"]))
dates=np.unique(np.concatenate(dates).ravel())
minDat=10 #min cuantity of data for one tortugue on an specific  day 
for day in dates:
    coords=[-40.585390,-64.996220]
    map1 = folium.Map(location = coords,zoom_start=15)
    #this tile is for seeing the terrain  
    folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community").add_to(map1)
    name=str(day)+".html"
    name=name.replace("/","_")
    for j in range(len(df)):
        if len(df[j].loc[df[j]['date']==day])>minDat:
            points=zip(df[j].loc[df[j]['date']==day]["lat"],df[j].loc[df[j]['date']==day]["lon"])
            points=list(points)
            folium.PolyLine(points,color=colors[j],weight=2.5, opacity=0.5).add_to(map1)
            for x in points:
                folium.CircleMarker(x,radius=3,stroke=False,fill=True,fill_color=colors[j],fill_opacity=1).add_to(map1)
    map1.save(name)
# %%
from geopy import distance
# %%
