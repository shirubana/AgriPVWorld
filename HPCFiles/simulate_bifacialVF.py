import numpy as np
import os
import pandas as pd
import time
from dask.distributed import Client
import math
import sys
import pathlib
import pytz
import bifacialvf
from rex import NSRDBX


# Run simulation using the given timestamp and wavelength
def simulate_single(df_weather_gid, meta_dict, gid):    
    
    # Variables
    tilt = 30                   # PV tilt (deg)
    sazm = 180                  # PV Azimuth(deg) or tracker axis direction
    cw = 2.0   
    albedo = 0.2               # 
    clearance_height=1.5/cw            #1.5m / 2m collector width
    gcr = 0.35
    pitch = cw/0.4/cw              # 1 / 0.35 where 0.35 is gcr --- row to row spacing in normalized panel lengths. 
    rowType = "interior"        # RowType(first interior last single)
    transFactor = 0             # TransmissionFactor(open area fraction)
    sensorsy = 12                # sensorsy(# hor rows in panel)   <--> THIS ASSUMES LANDSCAPE ORIENTATION 
    PVfrontSurface = "glass"    # PVfrontSurface(glass or ARglass)
    PVbackSurface = "glass"     # PVbackSurface(glass or ARglass)

    # Calculate PV Output Through Various Methods    
    calculateBilInterpol = False   # Only works with landscape at the moment.
    calculatePVMismatch = False
    portraitorlandscape='portrait'   # portrait or landscape
    cellsnum = 72
    bififactor = 1.0

    # Tracking instructions
    tracking=False
    backtrack=True
    limit_angle = 50

    savefilevar = '/scratch/sayala/bifacialR/bifacialvf_results'+str(gid)+'.csv'
    
    meta_dict['TZ'] = meta_dict['timezone']
    meta_dict['Name'] = meta_dict['county']
    meta_dict['altitude'] = meta_dict['elevation']
    tilt = np.round(meta_dict['latitude'])
    df_weather_gid = df_weather_gid.rename(columns={'dni': 'DNI',
                                'dhi': 'DHI',
                                'ghi': 'GHI'
                                })

    bifacialvf.simulate(df_weather_gid, meta_dict, writefiletitle=savefilevar, 
                 tilt=tilt, sazm=sazm, pitch=pitch, clearance_height=clearance_height, 
                 rowType=rowType, transFactor=transFactor, sensorsy=sensorsy, 
                 PVfrontSurface=PVfrontSurface, PVbackSurface=PVbackSurface,
                 albedo=albedo, tracking=tracking, backtrack=backtrack, 
                 limit_angle=limit_angle, calculatePVMismatch=calculatePVMismatch,
                 cellsnum = cellsnum, bififactor=bififactor,
                 calculateBilInterpol=calculateBilInterpol,
                 portraitorlandscape=portraitorlandscape,
                 deltastyle='SAM', agriPV=True)
    
    data, meta = bifacialvf.loadVFresults(savefilevar)
    data.set_index(pd.to_datetime(data.date), inplace=True)

    ground = data['Ground Irradiance Values'].str.strip('[]').str.split(' ', expand=True).astype(float)
    
    # Calculate geometry
    xp = np.cos(np.radians(float(meta['Tilt(deg)'])))
    u = int(np.ceil(100*xp/pitch))
    b = 100-u
    bA = int(np.floor(b/3.0))
    bC = int(bA)
    bB = int(b-bA-bC)

    underpanel = []
    bedA = []
    bedB = []
    bedC = []
    for mmonths in range (5, 10):
        datestart = data[data.index.month == mmonths].iloc[0].date
        dateend = data[data.index.month == mmonths].iloc[-1].date
        mask = (data.index >= datestart) & (data.index <= dateend)
        underpanel.append(ground[mask].iloc[:,0:u].mean(axis=1).mean())
        bedA.append(ground[mask].iloc[:,u:u+bA].mean(axis=1).mean())
        bedB.append(ground[mask].iloc[:,u+bA:u+bA+bB].mean(axis=1).mean())
        bedC.append(ground[mask].iloc[:,u+bA+bB:].mean(axis=1).mean())
    x = underpanel, bedA, bedB, bedC

    results = [meta_dict['latitude'], meta_dict['longitude'], x]
    return results


def run_simulations_dask(df_weather, meta, state):

    
    # Iterate over inputs
    futures = []
    
    #loop through dataframe and perform computation
    for gid, row in meta.iterrows():
        #prepare input for PVDegTools
        meta_dict = row.to_dict()
        df_tmy = df_weather.loc[:, gid]
        tz_convert_val = meta_dict['timezone']
        df_tmy = df_tmy.tz_convert(pytz.FixedOffset(tz_convert_val*60))
        df_tmy.index =  df_tmy.index.map(lambda t: t.replace(year=2021)) 
        df_tmy = df_tmy.sort_index()
        futures.append(client.submit(simulate_single, df_tmy, meta_dict, gid)) 

    # Get results for all simulations
    res = client.gather(futures)
    
    # try:
    #     # Close client
    #     client.close()
    # except:
    #     pass

    res2 = pd.DataFrame(res, columns=('latitude', 'longitude', 'x'))
    res2.to_pickle('/home/sayala/JordanWorld/res_dist_{}.pkl'.format(state))

    return res


if __name__ == "__main__":

    #TMY data located on eagle about 900GB
    nsrdb_file = '/datasets/NSRDB/current/nsrdb_tmy-2021.h5'

    #Load weather data
    parameters = ['air_temperature', 'wind_speed', 'dhi', 'ghi', 'dni', 'surface_albedo']

    #Input
    #region = 'Nevada'# 'Arizona'
    region_col = 'state' # 'state'

    with NSRDBX(nsrdb_file, hsds=False) as f:
        meta = f.meta
        
    meta_USA = meta[meta['country'] == 'United States']
    meta_USA = meta_USA[meta_USA['state'] != 'Alaska']

    # For debug
#    meta_USA = meta[meta['county'] == 'Boulder']
#    region_col = 'county' # 'state'

    # Create client
    
    scheduler_file = '/scratch/sayala/dask_testing/scheduler.json'
    client = Client(scheduler_file=scheduler_file)


    for state in meta_USA['state'].unique():
#    for state in meta_USA['county'].unique():
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
  
    print('FINISHED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    client.shutdown()
