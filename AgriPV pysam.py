#!/usr/bin/env python
# coding: utf-8

# In[1]:


import PySAM.Pvsamv1 as PV
import PySAM.Grid as Grid
import PySAM.Utilityrate5 as UtilityRate
import PySAM.Cashloan as Cashloan
import pathlib
import json
import os

sif2 = 'AgriPV_SAMJsons'


# In[2]:


import PySAM


# In[3]:


PySAM.__version__


# In[4]:


file_names = ["pvsamv1", "grid", "utilityrate5", "cashloan"]

pv2 = PV.new()  # also tried PVWattsSingleOwner
grid2 = Grid.from_existing(pv2)
ur2 = UtilityRate.from_existing(pv2)
so2 = Cashloan.from_existing(grid2, 'FlatPlatePVCommercial')


# In[5]:


for count, module in enumerate([pv2, grid2, ur2, so2]):
    filetitle= 'AgriPV_SAM' + '_' + file_names[count] + ".json"
    with open(os.path.join(sif2,filetitle), 'r') as file:
        data = json.load(file)
        for k, v in data.items():
            if k == 'number_inputs':
                continue
            try:
                module.value(k, v)
            except AttributeError:
                # there is an error is setting the value for ppa_escalation
                print(module, k, v)


# In[6]:


#pv2.SolarResource.solar_resource_file = weatherfile

grid2.SystemOutput.gen = [0] * 8760  # p_out   # let's set all the values to 0
pv2.execute()
grid2.execute()
ur2.execute()
so2.execute()

results = pv2.Outputs.export()


# In[16]:


len(results['subarray1_ground_rear_spatial'])


# In[28]:


type(results['subarray1_ground_rear_spatial'])


# In[23]:


results['subarray1_ground_rear_spatial'][0]


# In[24]:


results['subarray1_ground_rear_spatial'][1]


# In[27]:


results['subarray1_ground_rear_spatial'][2]


# In[26]:


results['subarray1_ground_rear_spatial'][10]


# In[15]:


len(results['subarray1_dc_gross'])


# In[ ]:


power2 = list(results['subarray1_dc_gross']) # normalizing by the system_capacity
celltemp2 = list(results['subarray1_celltemp'])
rear2 = list(results['subarray1_poa_rear'])
front2 = list(results['subarray1_poa_front'])



simtyp = [orga.loc[ii]['Sim']] * 8760

res = pd.DataFrame(list(zip(simtyp, power2, celltemp2, rear2, front2,
                           power4, celltemp4, rear4, front4,
                           power8, celltemp8, front8,
                            power9, celltemp9, rear9, front9, dni, dhi, alb)),
       columns = ['Sim', 'Power2' , 'CellTemp2', 'Rear2', 'Front2',
                 'Power4' , 'CellTemp4', 'Rear4', 'Front4',
                 'Power8' , 'CellTemp8', 'Front8',
                 'Power9' , 'CellTemp9', 'Rear9', 'Front9', 'DNI', 'DHI', 'Alb'])

res = res[0:8760]
res['index'] = res.index
res['Power2']= res['Power2']/system_capacity2 # normalizing by the system_capacity
res['Power4']= res['Power4']/system_capacity4 # normalizing by the system_capacity
res['Power8']= res['Power8']/system_capacity8 # normalizing by the system_capacity
res['Power9']= res['Power9']/system_capacity9 # normalizing by the system_capacity
res['datetimes'] = datelist
res['Year'] = years
res['Month'] = months
res['Hour'] = hours

#    res.index = timestamps
res.to_pickle('Results\Sim_'+orga.loc[ii]['Sim']+'.pkl')
dfAll = pd.concat([dfAll, res], ignore_index=True, axis=0)

dfAll.to_pickle('Results_pysam.pkl')

