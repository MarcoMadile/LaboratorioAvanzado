from dataclasses import replace
from matplotlib.pyplot import draw
import pandas as pd 
import glob
import numpy as np
from geopy import distance 
import matplotlib.pyplot as plt 
from matplotlib.transforms import Affine2D

#fixing time because some files have time=8 when i want time= 0008 (so then i have it in same format)
def fixing_time(x):
    x=str(x)
    if len(x)==4:
        return x
    elif len(x)==2:
        return "00"+x
    else:
        return "0"+x

#some files have dates like: "2022-01-21" and I want all dates in same format: "21/01/2022"
def fixing_dates(x):
    x=str(x)
    if "-" in x:
        aux=x.split("-")
        return aux[2]+"/"+aux[1]+"/"+aux[0]
    else:
        return x

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
        df[j]["date"]=df[j]["date"].apply(fixing_dates)
    dates=np.unique(np.concatenate(dates).ravel())
    return df,dates,tnames



#saves distance per day in csv file, then draws mean distance per day and returns the dataframe with distance per day per tortugue.
def get_distance_tort(dfs,tnames,dates,vmax=12):

    columnnames=["day","T name","sex","distance"]
    dfout=pd.DataFrame(columns=columnnames,dtype=str)
    dfs=fix_some_points(dfs,dates,vmax) #takes out points that are not posible
    for j in range(len(dfs)):
        dates=get_days(dfs[j])
        distances=get_distance_perday(dfs[j],dates) 
        name=[tnames[j] for k in range(len(dates))]
        sex=[dfs[j]["sexo"].iloc[0] for k in range(len(dates))]
        dict={"day":list(dates),"T name":name,"sex":sex,"distance":distances}#make dict
        dfaux=pd.DataFrame(dict,dtype=str)
        dfout=pd.concat([dfout,dfaux],ignore_index=True) 
    dfout.to_csv("distancia_por_tortu.csv",index=False,sep=";")
    draw_disntace_persex(dfout)
    return dfout


#returns numpy array of total distances for each day, numpy array lenght is equal to quantity of days in df
def get_distance_perday(df,dates):
    distances=np.zeros(len(dates))
    for i in range(len(dates)): #for each i in the cuantity of days 
        points=get_cordinates_from_day(df,dates[i])
        distancesi=np.array([(distance.distance(points[i],points[i+1]).m) for i in range(len(points)-1)]).astype(int)
        distances[i]=np.sum(np.abs(distancesi))

    return distances.astype(int)


def get_days(df):
    days=np.unique(df["date"])
    return days

#what the name suggest 
def get_cordinates_from_day(df,day):
    points=zip(df.loc[df['date']==day]["lat"],df.loc[df['date']==day]["lon"])
    points=np.array(list(points))
    return points

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
    return df

def draw_disntace_persex(df):
    dates=pd.to_datetime(df["day"],format="%d/%m/%Y")
    df["day"]=dates
    dates=dates.to_numpy()
    dates2=np.unique(dates)
    machos=np.zeros(len(dates2))
    hembras=np.zeros(len(dates2))
    emachos=np.copy(machos)
    ehembras=np.copy(hembras)
    dates2=np.sort(dates2)
    
    for i in range(len(dates2)):

        data=df[df["day"]==dates2[i]]
        dmachos=(data[data["sex"]=="macho"]["distance"]).to_numpy().astype(int)
        dhembras=(data[data["sex"]=="hembra"]["distance"]).to_numpy().astype(int)

        dmachos=dmachos[dmachos<750]
        machos[i]=np.sum(dmachos)
        
        hembras[i]=np.sum(dhembras)
    months1=np.array([date.astype("datetime64[M]").astype(str) for date in dates2])
    for h in range(len(months1)):
        months1[h]=months1[h].split("-")[1]
    months2=np.unique(np.array(months1))
    males=np.zeros(len(months2))
    females=np.zeros(len(months2))
    emales=np.copy(males)
    efemales=np.copy(females)
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.scatter(dates2,machos,label="Machos")
    ax.scatter(dates2,hembras,color="y",label="Hembras")
    ax.set(xlabel="mes",
       ylabel="distancia recorrida promedio por dia",
       title="distancia recorrida en función del mes")
    
    ax.legend()
    plt.show()
    tiempo_machos=[ 52.86666667,  49.36666667 ,203.93333333 ,158.15]
    tiempo_hembras=[232.98333333,  42.66666667, 176.9,243.26666667]
    for i in range(len(months2)):
        
        males[i]=np.sum(machos[months1==months2[i]])/tiempo_machos[i]
        females[i]=np.sum(hembras[months1==months2[i]])/tiempo_hembras[i]
        emales[i]=np.std(machos[months1==months2[i]])/tiempo_machos[i]
        efemales[i]=np.std(hembras[months1==months2[i]])/tiempo_hembras[i]

    fig, ax = plt.subplots(figsize=(12, 12))
    monthDict={"01":'Enero', "02":'Febrero', "03":'Marzo', "04":'Abril', "05":'Mayo', "06":'Junio', "07":'Julio', "08":'Aug', "09":'Septiembre', "10":'Octubre', "11":'Noviembre', "12":'Diciembre'}
    print(months2)
    months2=change_to_first(months2)
    print(months2)
    meses=np.vectorize(monthDict.get)(months2)
    
    trans1 = Affine2D().translate(-0.02, 0.0) + ax.transData
    trans2 = Affine2D().translate(+0.02, 0.0) + ax.transData
    ax.errorbar(meses,change_to_first(males),change_to_first(emales),label="Machos",fmt="o",transform=trans1)
    ax.errorbar(meses,change_to_first(females),change_to_first(efemales),color="y",label="Hembras",fmt="o",transform=trans2)
    
    ax.set(xlabel="mes",
       ylabel="distancia promedio por hora medida [m/h]",)
    #set legend to left corner
    ax.legend(loc='upper left')
    plt.show()
    return

def change_to_first(arr):
    arrout=np.array(arr)
    arrout[0:-1]=arr[1:]
    arrout[-1]=arr[0]
    return arrout