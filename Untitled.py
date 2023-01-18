#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


data = pd.read_pickle('Results_Golden.pkl')


# In[10]:


data[(data['hubheight']==1.5) & (data['rtr']==5.0) & (data['xgap']==1.0)]['Wm2Ground']

