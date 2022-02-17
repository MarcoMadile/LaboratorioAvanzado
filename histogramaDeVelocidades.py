import pandas as pd 
import glob
import numpy as np
from geopy import distance
from matplotlib import pyplot as plt 
#falta terminar! 
#getting all files in folder trayectoriasGPS
files=glob.glob("trayectoriasGPS\*.csv")
df=[]
for a in files:
    df.append(pd.read_csv(a,sep=";"))
dates=[]
#having unique dates so i can calculate velocity with data from same date
for tort in df:
    dates.append(np.unique(tort["date"]))
dates=np.unique(np.concatenate(dates).ravel())
mindata=4 # only calculate velocity when you have at least mindata for one specific date
velocities=np.empty(1)
for day in dates:
    for j in range(len(df)):
        if len(df[j].loc[df[j]['date']==day])>mindata:
            points=zip(df[j].loc[df[j]['date']==day]["lat"],df[j].loc[df[j]['date']==day]["lon"])
            print(files[j])
            print(day)
            points=np.array(list(points))
            time=pd.to_datetime(df[j].loc[df[j]['date']==day]["time"],format="%H%M")#getting time column
            time=np.array(time)
            deltatimes=((time[1:]-time[:-1]).astype('timedelta64[s]')).astype("int") #delta time in minutes as int
            dist = [distance.distance(x,y).m for x, y in zip(points[1:],points[:-1])]
            dist=(np.array(dist)).astype("int")
            vel=np.divide(dist,deltatimes)
            velocities=np.append(velocities,vel)
velocities[velocities == np.inf] = 0
velocities[velocities>20]=0
velocities=velocities[velocities>0.3]
velocities=velocities[velocities<50]
plt.hist(velocities[velocities>0],bins=20)
plt.xlabel("V(m/s)")
plt.ylabel("Repeticiones")
plt.show()
