import matplotlib.pyplot as plt 
import pandas as pd 
import glob
import numpy as np
import folium
import matplotlib
from matplotlib import cm

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
    tnames=[]
    for a in files:
        df.append(pd.read_csv(a,sep=";"))
        tort=a.replace(".csv","")
        tort=tort.replace(folder,"")
        tort=tort.replace("\\","")
        tort=tort.split("_", 1)[0]
        tnames.append(str(tort))
    dates=[]
    for j in range(len(df)):
        dates.append(np.unique(df[j]["date"]))
        df[j]["time"]=df[j]["time"].apply(fixing_time)
    dates=np.unique(np.concatenate(dates).ravel())
    
    return df,dates,tnames

def get_map():
    coords=[-40.585390,-64.996220]
    map1 = folium.Map(location = coords,zoom_start=15)
    folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community").add_to(map1)
    return map1 

def get_all_coordinates(df):
    x=np.empty(1)
    y=np.empty(1)
    for i in range(len(df)):
        x=np.hstack((x,np.array(list(df[i]["lat"]))))
        y=np.hstack((y,np.array(list(df[i]["lon"]))))
    #x=x.flatten()
    #y=y.flatten()
    return x,y

def make_countour_map(xs,ys,name):
    map1=get_map()
    gridx = np.linspace(np.min(xs), np.max(xs), 100)
    gridy = np.linspace(np.min(ys), np.max(ys),100)
    grid, xedges, yedges = np.histogram2d(xs, ys, bins=[gridx, gridy])
    plt.pcolormesh(gridx, gridy, grid)
    plt.colorbar()
    plt.show()
    deltax=xedges[0]-xedges[1]
    deltay=yedges[0]-yedges[1]
    vmax=np.max(grid)
    vmin=np.min(grid)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("viridis") 
    for i in range(len(xedges)-1):
        for j in range(len(yedges)-1):
            x=xedges[i]
            y=yedges[j]
            rgb = cmap(norm(abs(grid[i][j])))[:3]
            color = matplotlib.colors.rgb2hex(rgb)
            folium.Polygon([[x,y],[x+deltax,y],[x+deltax,y+deltay],[x,y+deltay]],color=color, fill_opacity=0.55,fill_color=color,opacity=0.55).add_to(map1)
    map1.save(name)


folder="TrayectoriasGPS"
df,dates,tnames=get_files_and_dates(folder)
name="campana2020dic.html"
xs,ys=get_all_coordinates(df)
print(len(xs))
print(len(ys))
#[-40.585390,-64.996220]
sig=np.std(xs)
mean=np.mean(xs)
ys=ys[xs>mean-sig]
xs=xs[xs>mean-sig]
ys=ys[xs<mean+1.5*sig]
xs=xs[xs<mean+1.5*sig]
print(len(xs))
print(len(ys))
sig=np.std(ys)
mean=np.mean(ys)
xs=xs[ys>mean-sig]
ys=ys[ys>mean-sig]
xs=xs[ys<mean+1.5*sig]
ys=ys[ys<mean+1.5*sig]

print(len(xs))
print(len(ys))
make_countour_map(xs,ys,name)
