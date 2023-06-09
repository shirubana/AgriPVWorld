#!/usr/bin/env python
# coding: utf-8

# # Compiling and Plotting of Single Location Ground Irradiance
# 
# 1/17/2023

# In[1]:


import pandas as pd
import numpy as np


# # 1. Calculate GHI values for each month

# In[2]:


import bifacial_radiance as br


# In[3]:


radObj = br.RadianceObj(path='TEMP')

startdates = [pd.to_datetime('2021-05-01 6:0:0'), #
                pd.to_datetime('2021-06-01 6:0:0'),
                pd.to_datetime('2021-07-01 6:0:0'),
                pd.to_datetime('2021-08-01 6:0:0'),
                pd.to_datetime('2021-09-01 6:0:0'),
                pd.to_datetime('2021-05-01 6:0:0')]
enddates = [pd.to_datetime('2021-05-31 6:0:0'),       # May
                pd.to_datetime('2021-06-30 20:0:0'),   # June
                pd.to_datetime('2021-07-31 20:0:0'),   # etc.
                pd.to_datetime('2021-08-31 20:0:0'),
                pd.to_datetime('2021-09-30 20:0:0'), 
                pd.to_datetime('2021-09-30 20:0:0')]   # Season


# In[4]:


ghi = []
for ii in range (0, len(startdates)):
    metData = radObj.readWeatherFile('TEMP/USA_CO_Golden-NREL.724666_TMY3.epw', starttime=startdates[ii], endtime=enddates[ii], coerce_year=2021)
    ghi.append(metData.ghi.sum())


# In[5]:


ghi


# In[6]:


data = pd.read_pickle('TEMP/Results_HPC_compiled_rough.pkl')


# In[7]:


# array hub-height
hubheights = [1.5, 2.4] # meters
rtrs = [5.0, 10.0]# ,6.0] # meters
xgaps = [0.0, 1.0]# ,6.0] # meters
periods = ['5TO5', '6TO6', '7TO7', '8TO8', '9TO9','5TO9'] # add more to match other time periods


# In[8]:


newdf = []
xgap_all = []
hubheight_all = []
rtr_all = []
period_all = []
ground_all = []
front_all = []
rear_all = []

for hubheight in hubheights:
    for rtr in rtrs:
        for xgap in xgaps:
            for period in periods:
                
                if period == '5TO5':
                    ii = 0
                if period == '6TO6':
                    ii = 1
                    
                if period == '7TO7':
                    ii = 2
                    
                if period == '8TO8':
                    ii = 3
                    
                if period == '9TO9':
                    ii = 4
                                        
                if period == '5TO9':
                    ii = 5
                    
                foo = data[(data['hubheight']==hubheight) & (data['rtr']==rtr) & (data['xgap']==xgap) &
                          (data['period']==period)]# ['Wm2Ground'].to_frame()

                foo2 = foo['Wm2Ground'].astype(str).str[1:-1]
                ground_all.append(foo2.str.split(',', expand=True).astype(float).sum(axis=0).values/ghi[ii])
                
                foo2 = foo['Wm2Front'].astype(str).str[1:-1]
                front_all.append(foo2.str.split(',', expand=True).astype(float).sum(axis=0).values/ghi[ii])

                foo2 = foo['Wm2Back'].astype(str).str[1:-1]
                rear_all.append(foo2.str.split(',', expand=True).astype(float).sum(axis=0).values/ghi[ii])

                rtr_all.append(rtr)
                hubheight_all.append(hubheight)
                xgap_all.append(xgap)
                period_all.append(period)

df = pd.DataFrame(list(zip(period_all, xgap_all, hubheight_all, rtr_all, ground_all, front_all, rear_all)),
                 columns=['period', 'xgap', 'hubheight', 'rtr', 'ground', 'front', 'rear'])


# In[9]:


df.to_csv('TEMP/results_Austin.csv')


# In[10]:


df


# In[11]:


y1 = df[(df['hubheight']==1.5) & (df['rtr']==5.0) & (df['xgap']==0.0) &
                          (df['period']=='5TO5')]['ground'].values[0]
y2 = df[(df['hubheight']==1.5) & (df['rtr']==5.0) & (df['xgap']==0.0) &
                          (df['period']=='6TO6')]['ground'].values[0]
y3 = df[(df['hubheight']==1.5) & (df['rtr']==5.0) & (df['xgap']==0.0) &
                          (df['period']=='7TO7')]['ground'].values[0]
y4 = df[(df['hubheight']==1.5) & (df['rtr']==5.0) & (df['xgap']==0.0) &
                          (df['period']=='8TO8')]['ground'].values[0]
y5 = df[(df['hubheight']==1.5) & (df['rtr']==5.0) & (df['xgap']==0.0) &
                          (df['period']=='9TO9')]['ground'].values[0]
type(y1)
y1


# In[12]:


import matplotlib.pyplot as plt


# In[13]:


plt.plot(y1, label='May')
plt.plot(y2, label='June')
plt.plot(y3, label='July')
plt.plot(y4, label='August')
plt.plot(y5, label='September')
plt.title("Ground irradiance in a PV array with hh=1.5m, pitch=5m, and no inter-row module spacing")
plt.legend()
plt.ylabel('Irradiance Fraction')
plt.xlabel('Row to Row distance [dm]')

