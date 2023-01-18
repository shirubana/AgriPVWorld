import numpy as np
import os
import pandas as pd
import time
from dask.distributed import Client
import math
import sys
from rex import NSRDBX
import PVDegradationTools as pvd
import PySAM.Pvsamv1 as PV
import PySAM.Grid as Grid
import PySAM.Utilityrate5 as UtilityRate
import PySAM.Cashloan as Cashloan
import pathlib
import json


# Run simulation using the given timestamp and wavelength
def simulate_single(NSRDBFile):    
    
    file_names = ["pvsamv1", "grid", "utilityrate5", "cashloan"]
    pv2 = PV.new()  # also tried PVWattsSingleOwner
    grid2 = Grid.from_existing(pv2)
    ur2 = UtilityRate.from_existing(pv2)
    so2 = Cashloan.from_existing(grid2, 'FlatPlatePVCommercial')

    for count, module in enumerate([pv2, grid2, ur2, so2]):
        filetitle= 'AgriPVSAM' + '_' + file_names[count] + ".json"
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

    pv2.SolarResource.solar_resource_file = NSRDBFile

    grid2.SystemOutput.gen = [0] * 8760  # p_out   # let's set all the values to 0
    pv2.execute()
    grid2.execute()
    ur2.execute()
    so2.execute()

    results = pv2.Outputs.export()
    power2 = list(results['subarray1_dc_gross']) # normalizing by the system_capacity
    celltemp2 = list(results['subarray1_celltemp'])
    rear2 = list(results['subarray1_poa_rear'])
    front2 = list(results['subarray1_poa_front'])
    
    results = [power2, celltemp2, rear2, front2]

    return results


def run_simulations_dask(df_weather, meta, state):

    
    # Iterate over inputs
    futures = []
    
    #loop through dataframe and perform computation
    for gid, row in meta.iterrows():
        #prepare input for PVDegTools
        meta_dict = row.loc[['latitude', 'longitude']].to_dict()

        df_tmy = df_weather.loc[:, gid]
        
        futures.append(client.submit(simulate_single, df_tmy, meta_dict)) 

    # Get results for all simulations
    res = client.gather(futures)
    
    # try:
    #     # Close client
    #     client.close()
    # except:
    #     pass

    res2 = pd.DataFrame(res, columns=('latitude', 'longitude', 'x'))
    res2.to_pickle('/home/mspringe/deg_maps/res_dist_{}.pkl'.format(state))

    try:
        client.shutdown()
    except:
        pass

    client.close()
    
    print('FINISHED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    return res


if __name__ == "__main__":

    #TMY data located on eagle about 900GB
    nsrdb_file = '/datasets/NSRDB/current/nsrdb_tmy-2021.h5'

    #Load weather data
    parameters = ['air_temperature', 'wind_speed', 'dhi', 'ghi', 'dni']

    #Input
    #region = 'Nevada'# 'Arizona'
    region_col = 'state' # 'state'

    with NSRDBX(nsrdb_file, hsds=False) as f:
        meta = f.meta
        
    meta_USA = meta[meta['country'] == 'United States']


    # Create client
    
    scheduler_file = '/scratch/mspringe/dask_testing/scheduler.json'
    client = Client(scheduler_file=scheduler_file)


    for state in meta_USA['state'].unique():
        region = state
    
        #Load time and geographical infos
        with NSRDBX(nsrdb_file, hsds=False) as f:
            # Get time index
            times = f.time_index
            # Get geographical index for region of interest
            gids = f.region_gids(region=region, region_col=region_col)   
            # Get meta data
            meta = f.meta[f.meta.index.isin(gids)]

        data = []
        with NSRDBX(nsrdb_file, hsds=False) as f:
            for p in parameters:
                data.append(f.get_gid_df(p, gids)) #.values

        #Create multi-level dataframe
        columns = pd.MultiIndex.from_product([parameters, gids], names=["par", "gid"])
        df_weather = pd.concat(data, axis=1)
        df_weather.columns = columns
        df_weather = df_weather.swaplevel(axis=1).sort_index(axis=1)

        print(len(df_weather))
        # Pass variables being looped on, and kwargs
        run_simulations_dask(df_weather, meta, state)

        print("*********** DONE ************")

    client.shutdown()
