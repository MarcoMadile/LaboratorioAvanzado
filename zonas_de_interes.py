import matplotlib.pyplot as plt 
import pandas as pd 
import glob
import numpy as np
import folium
import matplotlib
from matplotlib import cm
import branca.colormap as bcm
import folium.plugins
from geopy import distance 

#fixing time because some files have time=8 when i want time= 0008 (so then i have it in same format)
def fixing_time(x):
    x=str(x)
    if len(x)==4:
        return x
    elif len(x)==2:
        return "00"+x
    else:
        return "0"+x

#changing time tu int, so i can compare them with ints 
def chang_int(x):
    return int(x)

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
        df[j]["timeGMT"]=df[j]["timeGMT"].apply(fixing_time)
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

def get_all_day_coordinates(df):
    x=np.empty(1)
    y=np.empty(1)
    for i in range(len(df)):
        df[i]["timeGMT"]=df[i]["timeGMT"].apply(chang_int)
        df[i] = df[i].drop(df[i][(df[i].timeGMT > 2100)].index)
        df[i] = df[i].drop(df[i][(df[i].timeGMT < 700)].index)
        x=np.hstack((x,np.array(list(df[i]["lat"]))))
        y=np.hstack((y,np.array(list(df[i]["lon"]))))
    return x,y

def get_interpoled_coordinates(df,n,dates,olnlyDay=False):
    xs=[]
    ys=[]
    for date in dates:
        for j in range(len(df)):
            #get only the data of the day
            aux= df[j].drop(df[j][(df[j].date != date)].index)
            if olnlyDay:
                aux["timeGMT"]=aux["timeGMT"].apply(chang_int)
                aux=aux.drop(aux[(aux.timeGMT > 2100)].index)
                aux=aux.drop(aux[(aux.timeGMT < 700)].index)
            xaux=np.array(list(aux["lat"]))
            yaux=np.array(list(aux["lon"]))
            #add n points between each pair of coordinates and append those points to the list xs and ys.
            for i in range(len(xaux)-1):
                xs.append(np.linspace(xaux[i],xaux[i+1],n))
                ys.append(np.linspace(yaux[i],yaux[i+1],n))

    xs=np.concatenate(xs).ravel()
    ys=np.concatenate(ys).ravel()
    return xs,ys

        
def fix_some_points(df,dates,v0):
    mindata=4 #minimum amount of data to fix points 
    for day in dates:
        for j in range(len(df)):
            if len(df[j].loc[df[j]['date']==day])>mindata:
                points=zip(df[j].loc[df[j]['date']==day]["lat"],df[j].loc[df[j]['date']==day]["lon"])
                points=np.array(list(points))
                dist = [distance.distance(x,y).m for x, y in zip(points[1:],points[:-1])]
                dist=(np.array(dist)).astype("int")
                time=pd.to_datetime(df[j].loc[df[j]['date']==day]["timeGMT"],format="%H%M")
                time=np.array(time)
                deltatimes=((time[1:]-time[:-1]).astype('timedelta64[m]')).astype("int")
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
    for j in range(len(df)):
        df[j]=df[j].reset_index(drop=True)
    return df



def filter_some_coordinates(xs,ys,xmax,xmin,ymax,ymin):
    print("Cantidad de mediciones originales",len(xs))
    mask=xs>xmin
    # print(len(mask))
    if  (len(mask)==len(xs)):
        ys=ys[xs>xmin]
        xs=xs[xs>xmin]
    else:
        print("cumple condicion xs>xmin")
    mask=xs<xmax
    # print(len(mask))
    if  (len(mask)==len(xs)):
        ys=ys[xs<xmax]
        xs=xs[xs<xmax]
    else:
        print("cumple condicion xs<xmax")
    mask=ys>ymin
    # print(len(mask))
    # print("xs tamñano",len(xs))
    if  (len(mask)==len(xs)):
        xs=xs[ys>ymin]
        ys=ys[ys>ymin]
    else:
        print("cumple condicion ys>ymin")
    mask=ys<ymax

    if  (len(mask)==len(xs)):
        xs=xs[ys<ymax]
        ys=ys[ys<ymax]
    else:
        print("cumple condicion ys<ymax")
    print("cantidad de mediciones despues de filtro",len(ys))
    return xs,ys


def make_countour_map(xs,ys,name,distGrid=10):
    map1=get_map()
    Nx=int((distance.distance([np.min(xs),np.mean(ys)],[np.max(xs),np.mean(ys)]).m)/distGrid)
    Ny=int((distance.distance([np.mean(xs),np.min(ys)],[np.mean(xs),np.max(ys)]).m)/distGrid)
    gridx = np.linspace(np.min(xs), np.max(xs), Nx)
    gridy = np.linspace(np.min(ys), np.max(ys),Ny)
    grid, xedges, yedges = np.histogram2d(xs, ys, bins=[gridx, gridy])
    #plt.pcolormesh(gridx, gridy, grid)
   # plt.colorbar()
    #plt.show()
    
    deltax=xedges[0]-xedges[1]
    deltay=yedges[0]-yedges[1]
    vmax=np.max(grid)
    vmin=np.min(grid)
    print("distancia en metros x",distance.distance([gridx[0],np.mean(gridy)],[gridx[1],np.mean(gridy)]).m)
    print("distancia en metros y",distance.distance([np.mean(gridx),gridy[0]],[np.mean(gridx),gridy[1]]).m)
    print("grilla de ",str(Ny)+"x"+str(Nx)," , Preparando mapa....")
    
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("viridis") 
    for i in range(len(xedges)-1):
        for j in range(len(yedges)-1):
            x=xedges[i]
            y=yedges[j]
            rgb = cmap(norm(abs(grid[i][j])))[:3]
            color = matplotlib.colors.rgb2hex(rgb)
            folium.Polygon([[x,y],[x+deltax,y],[x+deltax,y+deltay],[x,y+deltay]],color=color, fill_opacity=0.55,fill_color=color,opacity=0.55,popup="Mediciones ="+str(grid[i][j])).add_to(map1)
    cmap2=bcm.linear.viridis.scale(vmin,vmax)
    cmap2.caption="Cantidad de puntos medidos en celda"
    map1.add_child(cmap2)
    map1.save(name)

def take_nans(xs,ys):
    xs=np.array(xs)
    ys=np.array(ys)
    xs=xs[~np.isnan(xs)]
    ys=ys[~np.isnan(ys)]
    return xs,ys






folder="todaslascampanas"
df,dates,tnames=get_files_and_dates(folder)
name="campanasInterpoledOnlydate.html"
df=fix_some_points(df,dates,v0=14)

#xs,ys=get_all_day_coordinates(df)
#xs,ys=take_nans(xs,ys)
n=14
xs3,ys3=get_interpoled_coordinates(df,n,dates,olnlyDay=True)
xs3,ys3=take_nans(xs3,ys3)
#xs2,ys2=get_all_coordinates(df)
#xs2,ys2=take_nans(xs2,ys2)
#print("datos completo :",len(xs2))
#print("datos  diurnos :",len(xs))
#print("datos  filtrados :",len(xs3))
xmin,xmax=-40.62,-40.579
ymin,ymax=-65.01,-64.84
Celldist=10
#xs,ys=filter_some_coordinates(xs,ys,xmax,xmin,ymax,ymin)

make_countour_map(xs3,ys3,name,distGrid=Celldist)