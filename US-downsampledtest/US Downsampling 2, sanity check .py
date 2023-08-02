#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from pyproj import CRS
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import numpy as np
import pickle


# In[2]:


USmap = True
if USmap:
    states = gpd.read_file('../tl_2022_us_state/tl_2022_us_state.shp')


# In[3]:


#datafile = r'ALLSetups_new_Puerto Rico.csv'
datafile = r'C:\Users\sayala\Box\AGRIPVWORLDPICKLES\DNI_US_Downsample_2.pkl'


# In[4]:


import pickle


# In[5]:


with open(datafile, "rb") as fp:   # Unpickling
    df = pickle.load(fp)


# In[7]:


vmin = np.round(df['dni'].min(),2)
vmax = np.round(df['dni'].max(),2)


# In[8]:


df.keys()


# In[9]:


# create an axis with 2 insets − this defines the inset sizes

geo_conti = gpd.GeoDataFrame(df['dni'], 
                 geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])],
                 crs = CRS('EPSG:4326')).to_crs(states.crs)


fig, continental_ax = plt.subplots(figsize=(15, 15))


# Set bounds to fit desired areas in each plot
#continental_ax.set_xlim(3E6, 3.4E6)
#continental_ax.set_xlim(-67.5, -65)
#continental_ax.set_ylim(17.5, 19)
#continental_ax.axis('off')

# Plot the data per area - requires passing the same choropleth parameters to each call
# because different data is used in each call, so automatically setting bounds won’t work

#vmin = 200.0
#vmax = 600.0

bound_plot = {'color':'gray', 'lw':0.75 }

#states.boundary.plot(ax=continental_ax, **bound_plot)


cont_plot = {'column':'dni', 'cmap':'viridis', 'marker': 's', 'markersize': 1, 'facecolor': 'b',
             'vmin':vmin, 'vmax':vmax} #
legend_kwds={'shrink':0.75, 'drawedges':False, 'label':'Ground Cumulative Irradiance [W/m$^2$]', #'ticks': np.linspace(0,15, 16), 
             'pad':0, 'aspect':30}

geo_conti.plot(ax=continental_ax, legend=True, legend_kwds=legend_kwds, **cont_plot)

#continental_ax.set_title('Ground Irradiance Testbed C in June', fontsize=20, y=0.95)

plt.title('DNI')
plt.tight_layout()
#plt.savefig('AgriPV_TestbedC_June.png', dpi=600)


# In[ ]:




