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


df1 = '219559_tmy.pkl'
meta1 = '219559_meta.pkl'
df2 = '219563_tmy.pkl'
meta2 = '219563_meta.pkl'


# In[5]:


df1=pd.read_pickle(df1)
df2=pd.read_pickle(df2)


# In[6]:


with open(meta1, 'rb') as fp:
    meta1 = pickle.load(fp)
with open(meta2, 'rb') as fp:
    meta2 = pickle.load(fp)


# In[7]:


meta1


# In[8]:


meta2


# In[9]:


df1.head(10)


# In[10]:


df2.head(10)


# In[ ]:





# In[11]:


radObj = br.RadianceObj('test','TEMP')
radObj.setGround(0.2) 


# In[12]:


metData1 = radObj.NSRDBWeatherData(meta1, df1, coerce_year=2021)


# In[13]:


metData2 = radObj.NSRDBWeatherData(meta2, df2, coerce_year=2021)


# In[14]:


print(metData1.solpos)


# In[15]:


print(metData2.solpos)


# In[16]:


metData2.datetime


# In[17]:


metData1.datetime


# In[18]:


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


# In[19]:


metData1 = radObj.NSRDBWeatherData(meta1, df1, coerce_year=2021)
trackerdict = radObj.set1axis(**trackerParams)


# ## Hourly

# In[20]:


# -- establish tracking angles
trackerParams = {'limit_angle':50,
                 'angledelta':5,
                 'backtrack':True,
                 'gcr':gcr,
                 'cumulativesky':False,
                 'azimuth': 180,
                 'fixed_tilt_angle': None,
                 }


# In[21]:


trackerdict = radObj.set1axis(**trackerParams)


# In[22]:


len(trackerdict)


# In[23]:


trackerdict.keys()


# In[24]:


startdates = [pd.to_datetime('2021-06-21 12:30:0')]


# In[26]:


metData = radObj.NSRDBWeatherData(meta1, df1, starttime=startdates[0], 
                                  endtime=startdates[0], coerce_year=2021)


# In[28]:


metData.solpos


# In[29]:


trackerdict = radObj.set1axis(**trackerParams)


# In[30]:


trackerdict = radObj.gendaylit1axis()


# In[31]:


sceneDict = {'pitch':7, 
             'hub_height': 2.3,
             'nMods': 2,
             'nRows': 1,
            'tilt': None,  
            'sazm': 180
             }


# In[32]:


mymod = radObj.makeModule('mymod', x=1,y=2)


# In[33]:


trackerdict = radObj.makeScene1axis(module=mymod,sceneDict=sceneDict)


# In[34]:


trackerdict = radObj.makeOct1axis()


# In[35]:


trackerdict = radObj.analysis1axis(trackerdict, customname = 'Module',
                                   sensorsy=9, modWanted=2,
                                   rowWanted=1)


# In[36]:


trackerdict = radObj.calculateResults(agriPV=False)


# In[37]:


radObj.CompiledResults


# In[38]:


radObj.CompiledResults.iloc[0]['Gfront_mean']


# In[39]:


radObj.CompiledResults.iloc[0]['Grear_mean']


# In[40]:


resolutionGround = 0.1  # use 1 for faster test runs
numsensors = int((5/resolutionGround)+1)
modscanback = {'xstart': 0, 
                'zstart': 0.05,
                'xinc': resolutionGround,
                'zinc': 0,
                'Ny':numsensors,
                'orient':'0 0 -1'}


# In[41]:


trackerdict = radObj.analysis1axis(trackerdict, customname = 'Ground',
                                       modWanted=2, rowWanted=1,
                                        modscanback=modscanback, sensorsy=1)


# In[42]:


import os


# In[43]:


filesall = os.listdir('results')
filestoclean = [e for e in filesall if e.endswith('_Front.csv')]
for cc in range(0, len(filestoclean)):
    filetoclean = filestoclean[cc]
    os.remove(os.path.join('results', filetoclean))


# In[44]:


trackerdict = radObj.calculateResults(agriPV=True)


# In[45]:


ResultPVGround = radObj.CompiledResults.iloc[0]


# In[68]:


mykey = list(radObj.trackerdict.keys())[0]


# In[83]:


metData.ghi


# In[84]:


ResultPVGround = radObj.trackerdict[mykey]['Results'][0]['AnalysisObj'].Wm2Back


# In[85]:


df_temp = ResultPVGround


# In[88]:


import numpy as np


# In[89]:


edgemean = np.mean(df_temp[:xp] + df_temp[-xp:])


# In[ ]:




