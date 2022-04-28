from folium import Popup
import matplotlib.pyplot as plt 
import pandas as pd 
import glob
import numpy as np
import folium.plugins
from geopy import distance 
import ipdb
import itertools

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
def get_files_and_dates(folder,rename4thCol=False,TakeYaguiOut=False):
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
        if rename4thCol: 
            df[j].rename(columns={df[j].columns[5]: "metodologia"}, inplace=True)
        if TakeYaguiOut:
            k1=len(df[j])
            df[j]=df[j][df[j]["metodologia"]!="yagui"]
            #print("Se sacaron ",-len(df[j])+k1," puntos por ser yagui a la tortuga"+tnames[j])
            df[j]=df[j].reset_index(drop=True)
        
    dates=np.unique(np.concatenate(dates).ravel())
    
    return df,dates,tnames


def fix_some_points(df,dates,v0):
    mindata=10 #minimum amount of data to fix points 
    for day in dates:
        for j in range(len(df)):
            if len(df[j].loc[df[j]['date']==day])>mindata:
                points=zip(df[j].loc[df[j]['date']==day]["lat"],df[j].loc[df[j]['date']==day]["lon"])
                points=np.array(list(points))
                dist = [distance.distance(x,y).meters for x, y in zip(points[1:],points[:-1])]
                dist=(np.array(dist)).astype("int")
                time=pd.to_datetime(df[j].loc[df[j]['date']==day]["timeGMT"],format="%H%M")
                time=np.array(time)
                deltatimes=((time[1:]-time[:-1]).astype('timedelta64[m]')).astype("int")
                vel=np.divide(dist,deltatimes)
                vel=np.array(vel)
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

#idea insted of geting each coordinate, que las coordenadas me queden espaciadas en 5 minutos. Como lograr eso? mirar dos puntos que tengan e ir trazando una lineal en t pero que quede en 10 minutos despues ir pasando eso 
def get_distances_each_day(df,dates,n,tnames):
    distancessF=[]
    dtimesF=[]
    distancessM=[]
    dtimesM=[]
    for day in dates:
        for j in range(len(df)):
            if len(df[j].loc[df[j]['date']==day])>10:
                time=pd.to_datetime(df[j].loc[df[j]['date']==day]["timeGMT"],format="%H%M")
                time=np.array(time)
                deltatimes=((time[1:]-time[:-1]).astype('timedelta64[m]')).astype("int")
                deltatimes=np.array(deltatimes)
                if ((time[-1]-time[0]).astype('timedelta64[m]')).astype("int")>=n:
                    if df[j]["sexo"].iloc[0]=="hembra":
                        dtimesF.append(deltatimes)
                        latitude=df[j].loc[df[j]['date']==day]["lat"]
                        longitud=df[j].loc[df[j]['date']==day]["lon"]
                        metodo=str(df[j]["metodologia"].iloc[0])
                        distancessF.append(make_displacements_inTime(deltatimes,latitude,longitud,tnames[j],day,metodo))
                    # pdb.set_trace()
                    elif df[j]["sexo"].iloc[0]=="macho":
                        dtimesM.append(deltatimes)
                        latitude=df[j].loc[df[j]['date']==day]["lat"]
                        longitud=df[j].loc[df[j]['date']==day]["lon"]
                        metodo=str(df[j]["metodologia"].iloc[0])
                        distancessM.append(make_displacements_inTime(deltatimes,latitude,longitud,tnames[j],day,metodo))
    return distancessM,distancessF,dtimesM,dtimesF

def make_displacements_inTime(deltatimes,longs,lats,tname,day,metodologia):
    displacements=[]
    for h in range(len(lats)-1):
        if deltatimes[h]>1:
            #ipdb.set_trace()
            auxdislat=np.linspace(lats.iloc[h],lats.iloc[h+1],deltatimes[h],endpoint=True)
            auxdislon=np.linspace(longs.iloc[h],longs.iloc[h+1],deltatimes[h],endpoint=True)
            distances=np.zeros(len(auxdislat))
            for i in range(len(auxdislat)):
                distances[i]=distance.distance((auxdislat[i],auxdislon[i]),(lats.iloc[0],longs.iloc[0])).meters
                if distances[i]>500:print("distancia mayor a 500",day,tname,metodologia)
            displacements.append(distances)
        else:print(tname+" no tiene mas de un minuto entre puntos",day,str(metodologia))
    #flatten the list, so that is only one list of coordinates.
    displacements=list(itertools.chain.from_iterable(displacements))

    return displacements


def msd(df,dates,n,tnames):
    disM,disF,dtimesM,dtimesF=get_distances_each_day(df,dates,n,tnames)
    print("cantidad de dias distintos o tortugas para machos :",len(disM))
    print("cantidad de dias distintos o tortugas para hembras :",len(disF))
    sqdisM,sqdisF=np.zeros((len(disM),n)),np.zeros((len(disF),n))
    #ipdb.set_trace()
    for i in range(len(disM)):
        sqdisM[i]=np.array(disM[i][:n])**2
    for i in range(len(disF)):
        sqdisF[i]=np.array(disF[i][:n])**2
    #pdb.set_trace()
    msdF,msdM=np.zeros(n),np.zeros(n)
    for i in range(n):
        msdF[i]=np.mean(sqdisF[:,i])
        msdM[i]=np.mean(sqdisM[:,i])
    t=np.arange(n)
    #make plot axis in log scale, only "y" axis

    ipdb.set_trace()
    plt.plot(t,msdF,label="females")
    plt.plot(t,msdM,label="males")
    #plt.plot(t,(msdM+msdF)/2,label="Ambas")
    #plt.yscale("log")
    plt.legend()
    #plt.xlim(left=10)
    plt.xlabel("time (min)")
    plt.ylabel(r"MSD (m$^2$)")	
    plt.show()

def make_maps(df,dates,n,tnames):
    for day in dates:
        coords=[-40.585390,-64.996220]
        map1 = folium.Map(location = coords,zoom_start=15)
        colors=["red","green","yellow","grey","pink","aqua","purple","white","black","brown","lime","beige"]*10
        #this tile is for seeing the terrain  
        folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community").add_to(map1)
        name=str(day)+"char.html"
        name=name.replace("/","_")
        for j in range(len(df)):
            if len(df[j].loc[df[j]['date']==day])>n:
                points=zip(df[j].loc[df[j]['date']==day]["lat"],df[j].loc[df[j]['date']==day]["lon"])
                points=list(points)
                folium.PolyLine(points,color=colors[j],weight=2.5, opacity=0.5).add_to(map1)
                for x in points: 
                    folium.CircleMarker(x,radius=3,stroke=False,fill=True,fill_color=colors[j],fill_opacity=1,popup=tnames[j]).add_to(map1)
        map1.save(name)

folder="todaslascampanas"
df,dates,tnames=get_files_and_dates(folder,rename4thCol=True,TakeYaguiOut=True)
df=fix_some_points(df,dates,v0=14)
#make_maps(df,dates,n=10,tnames=tnames)
msd(df,dates,360,tnames)