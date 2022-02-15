#%%
import folium
import webbrowser
import pandas as pd
import numpy as np

#it makes a color map from strings, so each date has a color
#%%
def string_to_color(domain):
   domain_unique=np.unique(domain)
   colors=["red","green","yellow","grey","pink","aqua","purple"]
   colors=colors[:len(domain_unique)] 
   zip_iterator = zip(domain_unique,colors)
   color_dictionari = dict(zip_iterator)
   return color_dictionari
#%%
#Define coordinates of where we want to center our map
coords=[-40.585390,-64.996220]
map = folium.Map(location = coords,zoom_start=15)
#this tile is for seeing the terrain  
folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community").add_to(map)
#%%
file="trayectoriasGPS\T11_2020.csv"
df=pd.read_csv(file,sep=";")
#%%
#it makes a color map from strings, so each date has a color
cmap=string_to_color(df["date"])
#it makes all the circles in the map, it applys the same function to each element in row of data frame
df.apply(lambda row:folium.CircleMarker(location=[row["lat"],row["lon"]],radius=3,stroke=False,fill=True,fill_color=cmap[row["date"]],fill_opacity=1).add_to(map),axis=1)
# %%
def draw_lines(df,map,cmap):
    dates=np.unique(df["date"])
    for date in dates:
        if len(df.loc[df['date']==date])>1:#it needs to be greather than one so i can draw lines
            lines=zip(df.loc[df['date']==date]["lat"],df.loc[df['date']==date]["lon"])
            lines=list(lines)
            folium.PolyLine(lines,color=cmap[date],weight=2.5, opacity=0.5).add_to(map)
#%%
draw_lines(df,map,cmap)
map.save("map.html")
webbrowser.open("map.html")
