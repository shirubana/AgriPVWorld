#!/usr/bin/env python
# coding: utf-8

# In[1]:


import bifacial_radiance as br
import pandas as pd
import pickle


# In[2]:


br.__version__


# In[3]:


import pickle


# In[4]:


df1 = r'untouched/df_219559.pkl'
meta1 = 'untouched/meta_219559.pkl'
df2 = 'untouched/df_219563.pkl'
meta2 = 'untouched/meta_219563.pkl'


# In[5]:


df1=pd.read_pickle(df1)
df2=pd.read_pickle(df2)


# In[6]:


with open(meta1, 'rb') as fp:
    meta1 = pickle.load(fp)
with open(meta2, 'rb') as fp:
    meta2 = pickle.load(fp)


# In[7]:


df1loc = r'untouched/df_convert_219559.pkl'
df2loc = 'untouched/df_convert_219563.pkl'
df1loc = pd.read_pickle(df1loc)
df2loc = pd.read_pickle(df2loc)


# In[8]:


meta1


# In[9]:


meta2


# In[10]:


import matplotlib.pyplot as plt


# In[11]:


plt.plot(df1.index)


# In[12]:


df2.loc['2021-06-23 14:30:00+00:00']


# In[13]:


df1.loc['2021-06-23 14:30:00+00:00']


# In[14]:


df1.head(12)


# In[15]:


df1loc


# In[16]:


type(df1loc.index)


# In[17]:


foo1 = df1loc.groupby(df1loc.index.day)
foo2 = df2loc.groupby(df2loc.index.day)


# In[18]:


foo1


# In[19]:


df2loc


# In[20]:


df1loc


# In[21]:


fig = plt.figure()
plt.plot(df1loc.loc['2021-06-21 0:30:00-08:00':'2021-06-23 23:30:00-08:00']['dni'])
plt.plot(df2loc.loc['2021-06-21 0:30:00-07:00':'2021-06-23 23:30:00-07:00']['dni'])
fig.autofmt_xdate(rotation=45)


# In[22]:


import bifacial_radiance


# In[23]:


radObj = br.RadianceObj('sim', 'TEMP')
radObj.setGround(0.2) 


# In[24]:


meta1


# In[25]:


df1loc


# In[46]:


startdate_8TZ = pd.to_datetime('2021-06-23 9:30:00-08:00')


# In[27]:


meta2


# In[28]:


import pytz


# In[29]:


startdate_7TZ = startdate_8TZ.tz_convert(pytz.FixedOffset(meta2['timezone']*60))
startdate_7TZ


# In[30]:


startdate_7TZ = startdate_7TZ.replace(tzinfo=None)


# In[31]:


startdate_7TZ = pd.to_datetime('2021-06-23 4:30:00')


# In[47]:


startdatenew = pd.to_datetime('2021-06-23 4:30:00')


# In[51]:


startdatenew.tz_localize(-7*60)


# In[62]:


meta2['TZ']=-4


# In[63]:


meta2


# In[54]:


metData = radObj.NSRDBWeatherData(meta2, df2loc)


# In[56]:


metData.datetime


# In[57]:


A = metData.datetime
#A = [i.replace(tzinfo=None) for i in A]


# In[58]:


with open('datelist.txt', 'w') as fp:
    for item in A:
        # write each item on a new line
        fp.write("%s\n" % item)
    print('Done')


# In[43]:


len([i.replace(tzinfo=None) for i in A])


# In[34]:


metData.dni


# In[38]:


metData.solpos


# In[37]:


metData.solpos['zenith'][0]


# In[ ]:


startdate_8TZ = startdate_8TZ.replace(tzinfo=None)


# In[ ]:


metData = radObj.NSRDBWeatherData(meta1, df1loc, starttime=startdate_8TZ, 
                                      endtime=startdate_8TZ)


# In[ ]:


metData.datetime


# In[ ]:


metData.dni


# In[ ]:


metData.solpos


# In[42]:


hub_height = 1.5
pitch = 5
sazm = 180  # Tracker axis azimuth
modulename = 'PVmodule'
bedsWanted = 3
fixed_tilt_angle = None
gcr = 2/pitch


# In[43]:


trackerParams = {'limit_angle':50,
                 'angledelta':5,
                 'backtrack':True,
                 'gcr':gcr,
                 'cumulativesky':False,
                 'azimuth': sazm,
                 'fixed_tilt_angle': fixed_tilt_angle,
                 }


# In[44]:


trackerdict = radObj.set1axis(**trackerParams)


# In[52]:


metData.timezone


# In[51]:


trackerdict[list(trackerdict.keys())[0]]


# In[ ]:


metData = radObj.NSRDBWeatherData(meta2, df2loc, starttime=startdate, 
                                      endtime=startdate)


# In[ ]:


metData.solpos


# In[ ]:


trackerdict = radObj.set1axis(**trackerParams)


# In[ ]:


trackerdict


# In[ ]:


df2loc.loc['2021-06-23 0:30:00-07:00':'2021-06-23 23:30:00-07:00']


# In[ ]:


df1loc.loc['2021-06-23 0:30:00-08:00':'2021-06-23 23:30:00-08:00']


# In[ ]:





# In[ ]:





# In[ ]:


ii=0
week = 1

fig = plt.figure(figsize=(12,4))
plt.title('week '+str(week))

for jj in range(0,365):
    foo1 = df1loc.iloc[24*jj:(24+24*jj)]
    foo2 = df2loc.iloc[24*jj:(24+24*jj)]
    plt.plot(foo1.dni, 'r')
    plt.plot(foo2.dni, 'b')
    fig.autofmt_xdate(rotation=45)
    ii+=1
    if ii==7:
        plt.figure(figsize=(12,4))
        ii = 0
        week+=1
        plt.title('week '+str(week))

    


# In[ ]:


radObj = br.RadianceObj('test','TEMP')
radObj.setGround(0.2) 


# In[ ]:


metData1 = radObj.NSRDBWeatherData(meta1, df1, coerce_year=2021)


# In[ ]:


metData2 = radObj.NSRDBWeatherData(meta2, df2, coerce_year=2021)


# In[ ]:


print(metData1.solpos)


# In[ ]:


print(metData2.solpos)


# In[ ]:


metData2.datetime


# In[ ]:


metData1.datetime


# In[ ]:


gcr = 0.33

# -- establish tracking angles
trackerParams = {'limit_angle':50,
                 'angledelta':5,
                 'backtrack':True,
                 'gcr':gcr,
                 'cumulativesky':True,
                 'azimuth': 180,
                 'fixed_tilt_angle': None,
                 }

metData1 = radObj.NSRDBWeatherData(meta2, df2, coerce_year=2021)
trackerdict = radObj.set1axis(**trackerParams)


# In[ ]:


metData1 = radObj.NSRDBWeatherData(meta1, df1, coerce_year=2021)
trackerdict = radObj.set1axis(**trackerParams)


# ## Hourly

# In[ ]:


# -- establish tracking angles
trackerParams = {'limit_angle':50,
                 'angledelta':5,
                 'backtrack':True,
                 'gcr':gcr,
                 'cumulativesky':False,
                 'azimuth': 180,
                 'fixed_tilt_angle': None,
                 }


# In[ ]:


trackerdict = radObj.set1axis(**trackerParams)


# In[ ]:


len(trackerdict)


# In[ ]:


trackerdict.keys()


# In[ ]:


startdates = [pd.to_datetime('2021-06-21 12:30:0')]


# In[ ]:


metData = radObj.NSRDBWeatherData(meta1, df1, starttime=startdates[0], 
                                  endtime=startdates[0], coerce_year=2021)


# In[ ]:


metData.solpos


# In[ ]:


trackerdict = radObj.set1axis(**trackerParams)


# In[ ]:


trackerdict = radObj.gendaylit1axis()


# In[ ]:


sceneDict = {'pitch':7, 
             'hub_height': 2.3,
             'nMods': 2,
             'nRows': 1,
            'tilt': None,  
            'sazm': 180
             }


# In[ ]:


mymod = radObj.makeModule('mymod', x=1,y=2)


# In[ ]:


trackerdict = radObj.makeScene1axis(module=mymod,sceneDict=sceneDict)


# In[ ]:


trackerdict = radObj.makeOct1axis()


# In[ ]:


trackerdict = radObj.analysis1axis(trackerdict, customname = 'Module',
                                   sensorsy=9, modWanted=2,
                                   rowWanted=1)


# In[ ]:


trackerdict = radObj.calculateResults(agriPV=False)


# In[ ]:


radObj.CompiledResults


# In[ ]:


radObj.CompiledResults.iloc[0]['Gfront_mean']


# In[ ]:


radObj.CompiledResults.iloc[0]['Grear_mean']


# In[ ]:


resolutionGround = 0.1  # use 1 for faster test runs
numsensors = int((5/resolutionGround)+1)
modscanback = {'xstart': 0, 
                'zstart': 0.05,
                'xinc': resolutionGround,
                'zinc': 0,
                'Ny':numsensors,
                'orient':'0 0 -1'}


# In[ ]:


trackerdict = radObj.analysis1axis(trackerdict, customname = 'Ground',
                                       modWanted=2, rowWanted=1,
                                        modscanback=modscanback, sensorsy=1)


# In[ ]:


import os


# In[ ]:


filesall = os.listdir('results')
filestoclean = [e for e in filesall if e.endswith('_Front.csv')]
for cc in range(0, len(filestoclean)):
    filetoclean = filestoclean[cc]
    os.remove(os.path.join('results', filetoclean))


# In[ ]:


trackerdict = radObj.calculateResults(agriPV=True)


# In[ ]:


ResultPVGround = radObj.CompiledResults.iloc[0]


# In[ ]:


mykey = list(radObj.trackerdict.keys())[0]


# In[ ]:


metData.ghi


# In[ ]:


ResultPVGround = radObj.trackerdict[mykey]['Results'][0]['AnalysisObj'].Wm2Back


# In[ ]:


df_temp = ResultPVGround


# In[ ]:


import numpy as np


# In[ ]:


edgemean = np.mean(df_temp[:xp] + df_temp[-xp:])


# In[ ]:




