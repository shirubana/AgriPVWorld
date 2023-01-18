#!/usr/bin/env python
# coding: utf-8

# #  NREL Resource Extraction Tool (NREL-rex)

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sys
from rex import NSRDBX, WindX


# In[2]:


import pvlib
import PVDegradationTools as pvd


# # NSRDBX

# In[3]:


#TMY data located on eagle about 900GB
nsrdb_file = '/datasets/NSRDB/current/nsrdb_tmy-2021.h5'


# In[4]:


#Input
region = 'Boulder'
region_col = 'county'
parameters = ['air_temperature', 'wind_speed', 'dhi', 'ghi', 'dni']


# In[5]:


#Load time and geographical infos
with NSRDBX(nsrdb_file, hsds=False) as f:
    # Get time index
    times = f.time_index
    # Get geographical index for region of interest
    gids = f.region_gids(region=region, region_col=region_col)   
    # Get meta data
    meta = f.meta[f.meta.index.isin(gids)]


# In[ ]:


# --- List of (lon, lat) tuples or Shapely points ---
lon_lats = [(lon, lat)]
nsrdbfetcher.fetch(lon_lats)

# --- Get resource data file path ---
nsrdb_path_dict = nsrdbfetcher.resource_file_paths_dict
nsrdb_fp = nsrdb_path_dict[lon_lats[0]]
if nsrdb_fp is not None:

    # --- Initialize Generator ---
    generator = pv.default('PVWattsSingleOwner')
    generator.SolarResource.assign({'solar_resource_file': nsrdb_fp})


# In[ ]:


#Load weather data
data = []
with NSRDBX(nsrdb_file, hsds=False) as f:
        for p in parameters:
            data.append(f.get_gid_df(p, gids)) #.values


# In[ ]:


#Create multi-level dataframe
columns = pd.MultiIndex.from_product([parameters, gids], names=["par", "gid"])
df_weather = pd.concat(data, axis=1)
df_weather.columns = columns
df_weather = df_weather.swaplevel(axis=1).sort_index(axis=1)


# In[ ]:


#Use PVDegradation tools to calculate ideal installation distance

#Create results dataframe
df_res = meta.loc[:, ['latitude', 'longitude']]
df_res['distance'] = np.nan

#loop through dataframe and perform computation
for gid, row in meta.iterrows():
    #prepare input for PVDegTools
    meta_dict = row.loc[['latitude', 'longitude']].to_dict()
    df_weather_gid = df_weather.loc[:, gid]
    
    #calculate ideal installation distance
    df_res.loc[gid, 'distance'] = pvd.Standards.ideal_installation_distance(df_weather_gid, meta_dict)


# In[ ]:


#Plot Results
fig, ax = plt.subplots()
df_res.plot.scatter(x='longitude', y='latitude', c='distance', ax=ax, marker='.', colormap='plasma',)
plt.show()

