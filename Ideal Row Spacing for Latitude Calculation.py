#!/usr/bin/env python
# coding: utf-8

# In[5]:


import os
from pathlib import Path
import bifacial_radiance as br
import numpy as np
import datetime
import pickle
import pandas as pd
import numpy as np
import bifacialvf

# Making folders for saving the simulations
testfolder = os.path.join(os.getcwd(), 'TEMP')


# In[35]:


print(br.__version__)
print(bifacialvf.__version__)


# In[9]:


radObj = br.RadianceObj('Setup',testfolder)

lat = 39.7407
lon = -105.1686
sazm = 180 
y = 2 # Collector Width for 1-up

epwfile = radObj.getEPW(lat, lon) 
metData = radObj.readWeatherFile(epwfile)


# In[34]:


# Distance between rows for no shading on Dec 21 at 9 am (Northern Hemisphere) or Jun 21st (Southern Hemisphere)
DD = bifacialvf.vf.rowSpacing(np.round(metData.latitude), sazm, metData.latitude, metData.longitude, metData.timezone, 9, 0.0)
normalized_pitch = DD + np.cos(np.round(metData.latitude) / 180.0 * np.pi)
pitch = normalized_pitch*y
pitch

