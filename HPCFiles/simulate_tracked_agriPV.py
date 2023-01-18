'''

'''

import os
import numpy as np
from time import sleep
import bifacial_radiance as br
from timeit import default_timer as timer
from dask.distributed import Client
from itertools import product
import pandas as pd
from datetime import datetime as dt
from datetime import date


def gcs1axis(startdate=None, enddate=None, location=None, hub_height=None, pitch=None, xgap = None, rootPath=None):
    '''
    Perform the simulation
    This will be run through Dask in parallel
    '''

    # Remove non-ideal combinations for Agri or PV
    if (pitch == 5) & (hub_height == 2.4):
        return

    #head, tail = os.path.split()
    locname = location[:-4].replace(".","__")
    mymonthstart = startdate.month
    mymonthend = enddate.month


    #startdate = None
    #enddate = None
    simpath = f'{locname}_hh{hub_height}_rtr{pitch}_xgap{xgap}_from_{mymonthstart}TO{mymonthend}'
    path = os.path.join(rootPath,simpath)
    results_path = os.path.join(path, 'results')

    #Check if simulation has already completed
    if os.path.exists(results_path):
        if len(os.listdir(results_path)) > 42:
            print("***** SIM Done for ", simpath)
            return

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    radObj = br.RadianceObj(simpath,path)

    alb = 0.2
    metfile = os.path.join('/home/sayala/JordanWorld/EPWs', location)
    radObj.setGround(alb)
    metData = radObj.readWeatherFile(metfile, starttime=startdate, endtime=enddate, coerce_year=2021)
    
    y = 2
    gcr = 2/pitch
    
    # -- establish tracking angles
    trackerParams = {'limit_angle':50,
                     'angledelta':5,
                     'backtrack':True,
                     'gcr':gcr,
                     'cumulativesky':True}

    trackerdict = radObj.set1axis(**trackerParams)
    print(trackerdict.keys())
    # -- generate sky   

    trackerdict = radObj.genCumSky1axis()

    sceneDict = {'gcr':gcr, 
                 'hub_height': hub_height,
                 'nMods': 19,
                 'nRows': 7}

    modWanted = 10
    rowWanted = 4

    modulename = 'PVmodule'
    if (hub_height == 2.4) & (xgap == 0):
        modulename = 'PVmodule2up'
    if (hub_height == 2.4) & (xgap == 1.0):
        modulename = 'PVmodule2up_1mxgap'
    if (hub_height == 1.5) & (xgap == 1.0):
        modulename = 'PVmodule_1mxgap'

    trackerdict = radObj.makeScene1axis(module=modulename,sceneDict=sceneDict)

    # -- build oct file
    trackerdict = radObj.makeOct1axis()

    # -- run analysis
    resolutionGround = 0.1  # use 1 for faster test runs
    numsensors = int((pitch/resolutionGround)+1)
    print(trackerdict.keys())
    trackerdict = radObj.analysis1axis(trackerdict, customname = 'Module', sensorsy=9, modWanted=modWanted, rowWanted=rowWanted)
    modscanfront = {'xstart': 0, 
                    'zstart': 0.05,
                    'xinc': resolutionGround,
                    'zinc': 0,
                    'Ny':numsensors}     
   
    # Analysis for GROUND
    trackerdict = radObj.analysis1axis(trackerdict, customname = 'Ground', modWanted=modWanted, rowWanted=rowWanted,
                                        modscanfront=modscanfront, sensorsy=1)
    #trackerdict = radObj.calculateResults()

    #os.chdir('..')  # comment out for HPC

def run_simulations_dask(sim_list, startdates, enddates, rootPath=None):
        
    # Create client
    scheduler_file = '/scratch/sayala/dask_testing2/scheduler.json'
    client = Client(scheduler_file=scheduler_file)
    
    # Iterate over inputs
    futures = []
    for dd in range(0, len(startdates)):
        startdate = startdates[dd]
        enddate = enddates[dd]
        for ii in range(0,len(sim_list)):
            params = sim_list.iloc[ii].to_dict()
            params['rootPath'] = rootPath
            futures.append(client.submit(gcs1axis, startdate, enddate, **params))
    
    client.gather(futures)

    try:
        client.shutdown()
    except:
        pass

    client.close()
    

if __name__ == "__main__":

    rootPath = r'/scratch/sayala/JordanWorld/'

    # locations ['STATE_City',lat,lon]
    locations = os.listdir(r'/home/sayala/JordanWorld/EPWs')
    #locations = os.listdir(r'/home/sayala/EPWs')
    #locations = [x for x in locations if x.startswith('USA_AZ')]  # 27
    #locations = ['USA_MI_Houghton.727440_TMY2.epw']
    locations = [x for x in locations if x.startswith('USA')]  # 1478 

    # array hub-height
    hub_height = [1.5, 2.4] # meters
    pitch = [5.0, 10.0]# ,6.0] # meters
    xgap = [0, 1.0]# ,6.0] # meters

    startdates = [pd.to_datetime('2021-05-01 6:0:0'), #
                    pd.to_datetime('2021-06-01 6:0:0'),
                    pd.to_datetime('2021-07-01 6:0:0'),
                    pd.to_datetime('2021-08-01 6:0:0'),
                    pd.to_datetime('2021-09-01 6:0:0'),
                    pd.to_datetime('2021-05-01 6:0:0')]
    enddates = [pd.to_datetime('2021-05-31 6:0:0'),       # May
                    pd.to_datetime('2021-06-30 20:0:0'),   # June
                    pd.to_datetime('2021-07-31 20:0:0'),   # etc.
                    pd.to_datetime('2021-08-31 20:0:0'),
                    pd.to_datetime('2021-09-30 20:0:0'), 
                    pd.to_datetime('2021-09-30 20:0:0')]   # Season

    sim_list = pd.DataFrame(list(product(locations,hub_height, pitch, xgap)),
                            columns=['location','hub_height', 'pitch', 'xgap'])



    # =========== Perform Simulation Set ===========

    start = timer()
    run_simulations_dask(sim_list, startdates, enddates, rootPath)


    stop = timer()
    runTime = round(stop-start,2)
    min = int(runTime//60)
    sec = int(round((runTime/60 - min)*60,0))
    print('=======================================')
    print(f'Simulation Run Time: {min:02}:{sec:02}')
    print('=======================================')
    #compile(rootPath)