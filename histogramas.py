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

#metod to fix points when gps doest work well
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

def separe_sexs(df,tnames):
    dfM,dfF,tnamesM,tnamesF=[],[],[],[]
    for j in range(len(df)):
        #ipdb.set_trace()
        if len(df[j])>0:
            if df[j]["sexo"].iloc[0]=="macho":
                dfM.append(df[j])
                tnamesM.append(tnames[j])
            elif df[j]["sexo"].iloc[0]=="hembra":
                dfF.append(df[j])
                tnamesF.append(tnames[j])
    return dfM,dfF,tnamesM,tnamesF

def time_standing_histogram(dfM,dfF,dates):
    times_stand_Males=np.zeros(1)
    times_stand_Females=np.zeros(1)
    for day in dates:
        for j in range(len(dfM)):
            day_male=dfM[j].loc[dfM[j]["date"]==day]
            if len(day_male)>2:
                times_stand_Males=np.hstack((times_stand_Males,get_time_stand(day_male)))
        for j in range(len(dfF)):
            day_female=dfF[j].loc[dfF[j]["date"]==day]
            if len(day_female)>2:
                times_stand_Females=np.hstack((times_stand_Females,get_time_stand(day_female)))

    fig=plt.figure()
    ax1=plt.subplot(211)
    plt.grid(True)
    ax2=plt.subplot(212,sharex = ax1)
    binwidth=8
    ax1.hist(times_stand_Females,bins=np.arange(min(times_stand_Females), max(times_stand_Females) + binwidth, binwidth),density=True)
    ax1.set_title("tiempo parado para hembras")
    ax2.hist(times_stand_Males,bins=np.arange(min(times_stand_Males), max(times_stand_Males) + binwidth,binwidth),density=True)
    ax2.set_xlabel("tiempo parado para los machos")
    plt.subplots_adjust(wspace=0,hspace=0)
    plt.grid(True)
    plt.show()
    return

def get_time_stand(dfDay,mindist=10):
    timesStand=np.zeros(1)
    points=zip(dfDay["lat"],dfDay["lon"])
    points=np.array(list(points))
    time=pd.to_datetime(dfDay["timeGMT"],format="%H%M")
    time=np.array(time)
    deltatimes=((time[1:]-time[:-1]).astype('timedelta64[m]')).astype("int")
    timeAux,i=0,0
    while i < len(points):
        h=1
        timeAux=0
        while h<len(points)-i:
            if int(distance.distance(points[i],points[i+h]).meters)<mindist:
                timeAux+=deltatimes[i+h-1]
                h+=1
            else:
                timesStand=np.hstack((timesStand,timeAux))
                break
        i+=h
    return timesStand


def step_histogram(dfM,dfF,dates):
    step_Males=np.zeros(1)
    step_Females=np.zeros(1)
    for day in dates:
        for j in range(len(dfM)):
            day_male=dfM[j].loc[dfM[j]["date"]==day]
            if len(day_male)>2:
                step_Males=np.hstack((step_Males,get_steps(day_male)))
        for j in range(len(dfF)):
            day_female=dfF[j].loc[dfF[j]["date"]==day]
            if len(day_female)>2:
                step_Females=np.hstack((step_Females,get_steps(day_female)))

    fig=plt.figure()
    ax1=plt.subplot(211)
    plt.grid(True)
    ax2=plt.subplot(212,sharex = ax1)
    binwidth=0.3
    ax1.hist(step_Females,bins=np.arange(min(step_Females), max(step_Females) + binwidth, binwidth),density=True)
    ax1.set_title("tamaño de paso para hembras")
    ax2.hist(step_Males,bins=np.arange(min(step_Males), max(step_Males) + binwidth, binwidth),density=True)
    ax2.set_xlabel("tamaño de paso para los machos")
    plt.subplots_adjust(wspace=0,hspace=0)
    plt.grid(True)
    plt.show()
    return

def get_steps(dfDay,mindist=10):
    points=zip(dfDay["lat"],dfDay["lon"])
    points=np.array(list(points))
    time=pd.to_datetime(dfDay["timeGMT"],format="%H%M")
    time=np.array(time)
    deltatimes=((time[1:]-time[:-1]).astype('timedelta64[m]')).astype("int")
    displacements=np.zeros(1)
    for h in range(len(points)-1):
        if deltatimes[h]>1:
            #ipdb.set_trace()
            auxdislat=np.linspace(points[h][0],points[h+1][0],deltatimes[h],endpoint=True)
            auxdislon=np.linspace(points[h][1],points[h+1][1],deltatimes[h],endpoint=True)
            distances=np.zeros(len(auxdislat))
            for i in range(len(auxdislat)-1):
                distances[i]=distance.distance((auxdislat[i+1],auxdislon[i+1]),(auxdislat[i],auxdislon[i])).meters
                if distances[i]>500:print("distancia mayor a 500")
            displacements=np.hstack((displacements,distances))
        else:print(" no tiene mas de un minuto entre puntos")

    return displacements

    
folder="todaslascampanas"
df,dates,tnames=get_files_and_dates(folder,rename4thCol=True,TakeYaguiOut=True)
df=fix_some_points(df,dates,v0=14)
dfM,dfF,tnamesM,tnamesF=separe_sexs(df,tnames)
time_standing_histogram(dfM,dfF,dates)
step_histogram(dfM,dfF,dates)