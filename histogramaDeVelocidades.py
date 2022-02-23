import pandas as pd 
import glob
import numpy as np
from geopy import distance
from matplotlib import pyplot as plt 
# I have problems with time, sometimes time comes like "28" and i need it to come like "0028"
def fixing_time(x):
    x=str(x)
    if len(x)==4:
        return x
    elif len(x)==2:
        return "00"+x
    else:
        return "0"+x
#getting all files in folder trayectoriasGPS
files=glob.glob("trayectoriasGPS/*.csv")
df=[]
for a in files:
    df.append(pd.read_csv(a,sep=";"))
dates=[]
#having unique dates so i can calculate velocity with data from same date
for j in range(len(df)):
    dates.append(np.unique(df[j]["date"]))
    df[j]["time"]=df[j]["time"].apply(fixing_time)
dates=np.unique(np.concatenate(dates).ravel())
mindata=4 # only calculate velocity when you have at least mindata for one specific date
velocities=np.empty(1)
for day in dates:
    for j in range(len(df)):
        if len(df[j].loc[df[j]['date']==day])>mindata:
            points=zip(df[j].loc[df[j]['date']==day]["lat"],df[j].loc[df[j]['date']==day]["lon"])
            points=np.array(list(points))
            dist = [distance.distance(x,y).m for x, y in zip(points[1:],points[:-1])]
            dist=(np.array(dist)).astype("int")
            time=pd.to_datetime(df[j].loc[df[j]['date']==day]["time"],format="%H%M")#getting time column
            time=np.array(time)
            deltatimes=((time[1:]-time[:-1]).astype('timedelta64[s]')).astype("int") #delta time in minutes as int
            vel=np.divide(dist,deltatimes)
            velocities=np.append(velocities,vel)


print("Cantidad de velocidades calculadas = "+str(len(velocities)))
print("Cantidad de velocidades menores a 0.03 m/s = "+str(len(velocities[velocities<0.03])))
print("Cantidad de velocidades que dan infinito = "+str(len(velocities[velocities==np.inf])))
print("Cantidad de velocidades mayores a 10 m/s = "+str(len(velocities[velocities>10])))
velocities[velocities == np.inf] = 0
velocities=velocities[velocities<10]
velocities=velocities[velocities>0.03]
print("Cantidad de velocidades que sirven = "+str(len(velocities)))

plt.hist(velocities,density=False ,bins=25  ,edgecolor='black')
plt.xlabel("V[m/s]")
plt.title("Distribución de velocidades")
plt.ylabel("Repeticiones")
plt.show()
