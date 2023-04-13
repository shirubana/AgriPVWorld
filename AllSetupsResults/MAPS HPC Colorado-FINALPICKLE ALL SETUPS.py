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


# In[2]:


# import the United States shape file
states = gpd.read_file('../tl_2022_us_state/tl_2022_us_state.shp')
#states = states.to_crs("EPSG:5070")

# set state code as index, exclude states that we will never display
states = states.set_index('STUSPS').drop(index=['PR', 'VI', 'MP', 'GU', 'AS'])

conti = states.drop(index=['HI', 'AK'])
conti = conti.to_crs("EPSG:5070")

alaska = states.loc[['AK']]
hawaii = states.loc[['HI']]


# In[3]:


datafile = r'PKLs/ALLSetups_Colorado.pkl'


# In[4]:


data = pd.read_pickle(datafile)


# In[5]:


data.keys()


# In[6]:


data


# In[8]:


df = data[(data['setup']==1) & 
         (data['MonthStart']==1) &
         (data['MonthEnd'] == 1)]
#df = df[['latitude', 'longitude', 'testbedA1_normGHI', 'testbedA2_normGHI', 'testbedA3_normGHI', 'inside_normGHI']].reset_index()


# In[13]:


geo_conti = gpd.GeoDataFrame(df['testbedA2_normGHI'], 
                 geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])],
                 crs = CRS('EPSG:4326')).to_crs(conti.crs)


# In[14]:


geo_conti['testbedA2_normGHI'].quantile(q=0.98, interpolation='linear')


# In[15]:


fig, ax = plt.subplots(figsize=(4,4))
geo_conti['testbedA2_normGHI'].plot.hist(bins=1000, density=True, color='dimgray', label='norm. histogram')

ax.legend()

for rect in ax.patches:
    if rect.get_x() < 0.0:
        rect.set_color('firebrick')

#ax.set_xlim(-2.5, 16)
#ax.set_ylim(0, 0.225)
ax.set_xlabel('Ground Irradiance [W/m$^2$]')
ax.set_ylabel('Density')
ax.set_box_aspect(1)
#ax.set_ylim(0, 0.01)
#ax.set_xlim(100,600)
plt.tight_layout()
plt.savefig('asdf.png', dpi=600)
plt.savefig('asdf.pdf')


# In[16]:


# create an axis with 2 insets − this defines the inset sizes
fig, continental_ax = plt.subplots(figsize=(13, 8))


# Set bounds to fit desired areas in each plot
continental_ax.set_xlim(-2.5E6, 2.5E6)
#continental_ax.set_ylim(22, 53)
continental_ax.axis('off')

# Plot the data per area - requires passing the same choropleth parameters to each call
# because different data is used in each call, so automatically setting bounds won’t work

#vmin = 200.0
#vmax = 600.0

bound_plot = {'color':'gray', 'lw':0.75 }

conti.boundary.plot(ax=continental_ax, **bound_plot)

cont_plot = {'column':'testbedA2_normGHI', 'cmap':'viridis', 'marker': 'o', 'markersize': 0.1}
             # 'vmin':vmin, 'vmax':vmax, 'marker':'o', 'markersize':0.1} #
legend_kwds={'shrink':0.75, 'drawedges':False, 'label':'Ground Cumulative Irradiance [W/m$^2$]', #'ticks': np.linspace(0,15, 16), 
             'pad':0, 'aspect':30}

geo_conti.plot(ax=continental_ax, legend=True, legend_kwds=legend_kwds, **cont_plot)

#continental_ax.set_title('Ground Irradiance Testbed C in June', fontsize=20, y=0.95)

plt.tight_layout()
#plt.savefig('AgriPV_TestbedC_June.png', dpi=600)

