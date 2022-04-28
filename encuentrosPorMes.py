import matplotlib.pyplot as plt 
import pandas as pd 
import numpy as np 
from dataclasses import replace
from datetime import datetime
from matplotlib.dates import DateFormatter



def draw_encounters_perday(df):
    dates=pd.to_datetime(df["day"],format="%d/%m/%Y")
    df["daytime"]=dates
    dates=dates.to_numpy()
    dates2=np.unique(dates)
    machos=np.zeros(len(dates2))
    hembras=np.zeros(len(dates2))
    dates2=np.sort(dates2)
    for i in range(len(dates2)):
        data=df.loc[df["daytime"]==dates2[i]]
        machos[i]=len(data[data["sex one"]=="macho"])
        machos[i]+=len(data[data["sex two"]=="macho"])
        hembras[i]=len(data[data["sex one"]=="hembra"])
        hembras[i]=len(data[data["sex two"]=="hembra"])

    months1=np.array([date.astype("datetime64[M]").astype(str) for date in dates2])
    for h in range(len(months1)):
        months1[h]=months1[h].split("-",1)[1]
    months2=np.unique(np.array(months1))
    males=np.zeros(len(months2))
    females=np.zeros(len(months2))
    daycount=0
    for i in range(len(months2)):
        for j in range(len(dates2)):
            if months1[j]==months2[i]:
                daycount+=1
                males[i]+=machos[j]
                females[i]+=hembras[j]

        if daycount>0:
            females[i]=females[i]/daycount
            males[i]=males[i]/daycount
        daycount=0
    fig, ax = plt.subplots(figsize=(12, 12))
    monthDict={"01":'Jan', "02":'Feb', "03":'Mar', "04":'Apr', "05":'May', "06":'Jun', "07":'Jul', "08":'Aug', "09":'Sep', "10":'Oct', "11":'Nov', "12":'Dec'}
    print(months2)
    print(type(months2))
    meses=np.vectorize(monthDict.get)(months2)
    print(meses)
    ax.scatter(meses,males,label="Machos")
    ax.scatter(meses,females,color="y",label="Hembras")
    ax.set(xlabel="mes",
       ylabel="Encuentros promedio por dia",
       title="Encuentros en función del mes")

    ax.legend()
    plt.show()

filename="encuentroscompleto.csv"
df=pd.read_csv(filename,sep=";")
draw_encounters_perday(df)