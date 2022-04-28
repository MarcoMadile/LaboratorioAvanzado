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

#get time in hours messuring "macho" for each month and time mesured "hembra" for each month. 
def time_in_hours_per_sex(dfs,dates):
    dfs,months=get_all_months(dfs) #now i have a new column named month in each df
    males_time=np.zeros(len(months))
    females_time=np.zeros(len(months))
    for day in dates:
        for df in dfs:
            time=pd.to_datetime(df.loc[df['date']==day]["timeGMT"],format="%H%M")
            time=np.array(time)
            deltatimes=((time[1:]-time[:-1]).astype('timedelta64[m]')).astype("int")
            if len(deltatimes)>0:
                month_of_date=df.loc[df['date']==day]["month"].iloc[0]
                if df["sexo"].iloc[0]=="macho":
                    males_time[np.where(months==month_of_date)[0][0]]+=np.sum(deltatimes)
                elif df["sexo"].iloc[0]=="hembra":
                    females_time[np.where(months==month_of_date)[0][0]]+=np.sum(deltatimes)

    return months,males_time,females_time

def get_all_months(dfs):
    uniqueMonths=[]
    for df in dfs:
        dates=pd.to_datetime(df["date"],format="%d/%m/%Y")
        dates=dates.to_numpy()
        dates=np.array([date.astype("datetime64[M]").astype(str) for date in dates])
        months=np.copy(dates)
        for h in range(len(dates)):
            months[h]=dates[h].split("-")[1]
        df["month"]=months
        uniqueMonths.append(months)
   
    uniqueMonths=np.hstack(uniqueMonths)
    uniqueMonths=np.unique(np.array(uniqueMonths))
    print(uniqueMonths)
    return dfs,uniqueMonths

def get_encounters_per_month(filename="encuentroscompleto.csv",total_months=['01','09','11','12']):
    #get dataframe from filename
    df=pd.read_csv(filename,sep=";")
    #add month column to df and fill it with months
    dates=pd.to_datetime(df["day"],format="%d/%m/%Y")
    dates=dates.to_numpy()
    dates=np.array([date.astype("datetime64[M]").astype(str) for date in dates])
    months=np.copy(dates)
    for h in range(len(dates)):
        months[h]=dates[h].split("-")[1]
    df["month"]=months
    total_malesEncounters=np.zeros(len(total_months))
    total_femalesEncounters=np.zeros(len(total_months))
    f_fEncounter=np.zeros(len(total_months))
    m_fEncounter=np.zeros(len(total_months))
    m_mEncounter=np.zeros(len(total_months))
    for j in range(len(total_months)):
        data_of_month=df.loc[df['month']==total_months[j]]
        sex_one=data_of_month["sex one"]
        sex_two=data_of_month["sex two"]
        sex_one=sex_one.to_numpy()
        sex_two=sex_two.to_numpy()
        for i in range(len(sex_one)):
            if sex_one[i]=="macho":
                if sex_two[i]=="macho":
                    total_malesEncounters[j]+=2
                    m_mEncounter[j]+=1
                else:
                    total_malesEncounters[j]+=1
                    total_femalesEncounters[j]+=1
                    m_fEncounter[j]+=1
            else:
                if sex_two[i]=="macho":
                    total_malesEncounters[j]+=1
                    total_femalesEncounters[j]+=1
                    m_fEncounter[j]+=1
                else: 
                    total_femalesEncounters[j]+=2
                    f_fEncounter[j]+=1
    return total_malesEncounters,total_femalesEncounters,m_mEncounter,m_fEncounter,f_fEncounter

        
def change_to_first(arr):
    arrout=np.array(arr)
    arrout[0:-1]=arr[1:]
    arrout[-1]=arr[0]
    return arrout