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


# In[8]:


# PR
df1 = r'df_convert_1480083.pkl'
meta1 = 'meta_convert_1480083.pkl'

# Jefferson County, Colorado
df1 = r'df_loc_323393.pkl'
meta1 = 'meta_loc_323393.pkl'


# In[9]:


df1=pd.read_pickle(df1)


# In[10]:


with open(meta1, 'rb') as fp:
    meta1 = pickle.load(fp)


# In[11]:


meta1


# In[12]:


import bifacial_radiance


# In[13]:


radObj = br.RadianceObj('sim', 'TEMP')
radObj.setGround(0.2) 


# In[ ]:


startdate = pd.to_datetime('2021-06-21 0:30:00-07:00')
enddate = pd.to_datetime('2021-06-25 9:30:00-07:00')


# In[14]:


metData = radObj.NSRDBWeatherData(meta1, df1, )


# In[16]:


A = metData.datetime


# In[17]:


with open('datelist.txt', 'w') as fp:
    for item in A:
        # write each item on a new line
        fp.write("%s\n" % item)
    print('Done')


# In[16]:


# Convert it to Naive
#[i.replace(tzinfo=None) for i in A]

