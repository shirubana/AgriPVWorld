# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 15:30:40 2022

@author: sayala
"""
import os
import pandas as pd

def getEPW():
    """
    Subroutine to download nearest epw files to latitude and longitude provided,
    into the directory \EPWs\
    based on github/aahoo.
    
    .. warning::
        verify=false is required to operate within NREL's network.
        to avoid annoying warnings, insecurerequestwarning is disabled
        currently this function is not working within NREL's network.  annoying!
    
    Parameters
    ----------
    lat : decimal 
        Used to find closest EPW file.
    lon : decimal 
        Longitude value to find closest EPW file.
    GetAll : boolean 
        Download all available files. Note that no epw file will be loaded into memory
    
    
    """

    import requests, re
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    hdr = {'User-Agent' : "Magic Browser",
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
           }

    path_to_save = 'EPWs' # create a directory and write the name of directory here
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    def _returnEPWnames():
        ''' return a dataframe with the name, lat, lon, url of available files'''
        r = requests.get('https://github.com/NREL/EnergyPlus/raw/develop/weather/master.geojson', verify=False)
        data = r.json() #metadata for available files
        #download lat/lon and url details for each .epw file into a dataframe
        df = pd.DataFrame({'url':[], 'lat':[], 'lon':[], 'name':[]})
        for location in data['features']:
            match = re.search(r'href=[\'"]?([^\'" >]+)', location['properties']['epw'])
            if match:
                url = match.group(1)
                name = url[url.rfind('/') + 1:]
                lontemp = location['geometry']['coordinates'][0]
                lattemp = location['geometry']['coordinates'][1]
                dftemp = pd.DataFrame({'url':[url], 'lat':[lattemp], 'lon':[lontemp], 'name':[name]})
                #df = df.append(dftemp, ignore_index=True)
                df = pd.concat([df, dftemp], ignore_index=True)
        return df

    def _findClosestEPW(lat, lon, df):
        #locate the record with the nearest lat/lon
        errorvec = np.sqrt(np.square(df.lat - lat) + np.square(df.lon - lon))
        index = errorvec.idxmin()
        url = df['url'][index]
        name = df['name'][index]
        return url, name

    def _downloadEPWfile(url, path_to_save, name):
        r = requests.get(url, verify=False, headers=hdr)
        if r.ok:
            filename = os.path.join(path_to_save, name)
            # py2 and 3 compatible: binary write, encode text first
            with open(filename, 'wb') as f:
                f.write(r.text.encode('ascii', 'ignore'))
            print(' ... OK!')
        else:
            print(' connection error status code: %s' %(r.status_code))
            r.raise_for_status()

    # Get the list of EPW filenames and lat/lon
    df = _returnEPWnames()

    print("STARTING DOWNLOAD")
    for index, row in df.iterrows():
        print('Getting weather file: ' + row['name'])
        _downloadEPWfile(row['url'], path_to_save, row['name'])

    print("FINISHED")
    return

getEPW()