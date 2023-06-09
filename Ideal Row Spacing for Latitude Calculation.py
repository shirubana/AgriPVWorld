#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


print(br.__version__)
print(bifacialvf.__version__)


# In[48]:


lat = 39.7407
lon = -105.1686
sazm = 180 
y = 2 # Collector Width for 1-up
tz = -8
lat = 49.1756  # NorthWest Angle Minnesota
lon = -95.0110  # NorthWest Angle Minnesota
lat = 71.2320 # Alaska Point Barrow
lon = -156.28  # Alaska Point Barrow

#lat = 47.6062 # Seattle
#lon = -122.3321 # Seattle


# In[50]:


10/2


# In[49]:


# Distance betwee5b\n rows for no shading on Dec 21 at 9 am (Northern Hemisphere) or Jun 21st (Southern Hemisphere)
DD = bifacialvf.vf.rowSpacing(np.round(lat), sazm, lat, lon, tz, 9, 0.0)
DD


# In[ ]:


radObj = br.RadianceObj('Setup',testfolder)
epwfile = radObj.getEPW(lat, lon) 
metData = radObj.readWeatherFile(epwfile)


# In[ ]:


# Distance between rows for no shading on Dec 21 at 9 am (Northern Hemisphere) or Jun 21st (Southern Hemisphere)
DD = bifacialvf.vf.rowSpacing(np.round(metData.latitude), sazm, metData.latitude, metData.longitude, metData.timezone, 9, 0.0)
DD


# In[ ]:


normalized_pitch = DD + np.cos(np.round(metData.latitude) / 180.0 * np.pi)
pitch = normalized_pitch*y*pitchfactor
pitch


# In[8]:


import math

def rowSpacing(beta, sazm, lat, lng, tz, hour, minute):
    """
    This method determines the horizontal distance D between rows of PV panels
    (in PV module/panel slope lengths) for no shading on December 21 (north
    hemisphere) June 21 (south hemisphere) for a module tilt angle beta and
    surface azimuth sazm, and a given latitude, longitude, and time zone and
    for the time passed to the method (typically 9 am).

    (Ref: the row-to-row spacing is then ``D + cos(beta)``)
    8/21/2015

    Parameters
    ----------
    beta : double
        Tilt from horizontal of the PV modules/panels (deg)
    sazm : double
        Surface azimuth of the PV modules/panels (deg)
    lat : double
        Site latitude (deg)
    lng : double
        Site longitude (deg)
    tz : double
        Time zone (hrs)
    hour : int
        hour for no shading criteria
    minute: double
        minute for no shading

    Returns
    -------
    D : numeric
        Horizontal distance between rows of PV panels (in PV panel slope
        lengths)
    """     
    DTOR = math.pi / 180.0  # Factor for converting from degrees to radians

    beta = beta * DTOR  # Tilt from horizontal of the PV modules/panels, in radians
    sazm = sazm * DTOR  # Surface azimuth of PV module/pamels, in radians
    if lat >= 0:
        [azm, zen, elv, dec, sunrise, sunset, Eo, tst] = solarPos (2014, 12, 21, hour, minute, lat, lng, tz)
    else:
        [azm, zen, elv, dec, sunrise, sunset, Eo, tst] = solarPos (2014, 6, 21, hour, minute, lat, lng, tz)
    tst = 8.877  ##DLL Forced value
    minute -= 60.0 * (tst - hour);      # Adjust minute so sun position is calculated for a tst equal to the
      # time passed to the function

    if lat >= 0:
        [azm, zen, elv, dec, sunrise, sunset, Eo, tst] = solarPos(2014, 12, 21, hour, minute, lat, lng, tz)
    else:
        [azm, zen, elv, dec, sunrise, sunset, Eo, tst] = solarPos(2014, 6, 21, hour, minute, lat, lng, tz)
      
    # Console.WriteLine("tst = {0} azm = {1} elv = {2}", tst, azm * 180.0 / Math.PI, elv * 180.0 / Math.PI);
    D = math.cos(sazm - azm) * math.sin(beta) / math.tan(elv)
    return D


# In[10]:


def solarPos( year, month, day, hour, minute, lat, lng, tz ): 		
    # This method is based on a paper by Michalsky published in Solar Energy
    # Vol. 40, No. 3, pp. 227-235, 1988. It calculates solar position for the
    # time and location passed to the method based on the Astronomical
    # Almanac's Algorithm for the period 1950-2050. For data averaged over an
    # interval, the appropriate time passed is the midpoint of the interval.
    # (Example: For hourly data averaged from 10 to 11, the time passed to the
    # method should be 10 hours and 30 minutes). The exception is when the time
    # interval includes a sunrise or sunset. For these intervals, the appropriate
    # time should be the midpoint of the portion of the interval when the sun is
    # above the horizon. (Example: For hourly data averaged from 7 to 8 with a
    # sunrise time of 7:30, the time passed to the method should be 7 hours and
    # and 45 minutes).
    #
    # Revised 5/15/98. Replaced algorithm for solar azimuth with one by Iqbal
    # so latitudes below the equator are correctly handled. Also put in checks
    # to allow an elevation of 90 degrees without crashing the program and prevented
    # elevation from exceeding 90 degrees after refraction correction.
    #			
    # Revised 4/1/03. Converted to C# and simplified in a few places. 
    #
    # This method calls the method Julian to get the julian day of year.
    #
    # List of Parameters Passed to Method:
    # year   = year (e.g. 1986)
    # month  = month of year (e.g. 1=Jan)
    # day    = day of month
    # hour   = hour of day, local standard time, (1-24, or 0-23)
    # minute = minutes past the hour, local standard time
    # lat    = latitude in degrees, north positive
    # lng    = longitude in degrees, east positive
    # tz     = time zone, west longitudes negative
    # List of Out Parameters
    # azm = sun azimuth in radians, measured east from north, 0 to 2*pi
    # zen = sun zenith in radians, 0 to pi
    # elv = sun elevation in radians, -pi/2 to pi/2
    # dec = sun declination in radians
    # sunrise = in local standard time (hrs), not corrected for refraction
    # sunset = in local standard time (hrs), not corrected for refraction
    # Eo = eccentricity correction factor
    # tst = true solar time (hrs)                */

			DTOR = math.pi / 180.0  # Factor for converting from degrees to radians

			pi=math.pi; DTOR=math.pi/180
			zulu = 0.0; jd = 0.0; time = 0.0; mnlong = 0.0; mnanom = 0.0 
			eclong= 0.0; oblqec = 0.0; num = 0.0; den = 0.0; den = 0.0; ra = 0.0
			gmst = 0.0; lmst = 0.0; ha = 0.0; refrac = 0.0; E = 0.0; ws = 0.0; arg = 0.0
     
			jday = julian(year,month,day);		# Get julian day of year
			zulu = hour + minute/60.0 - tz;		# Convert local time to zulu time
			delta = year - 1949;
			leap = int(delta/4);
			jd = 32916.5 + delta*365 + leap + jday + zulu/24.0;
			time = jd - 51545.0;	# Time in days referenced from noon 1 Jan 2000

			mnlong = 280.46 + 0.9856474*time;
			mnlong = iEEERemainder(mnlong,360.0);	# Finds floating point remainder
			if( mnlong < 0.0 ):
				mnlong += 360.0;    # Mean longitude between 0-360 deg

			mnanom = 357.528 + 0.9856003*time;
			mnanom = iEEERemainder(mnanom,360.0);
			if( mnanom < 0.0 ):
				mnanom += 360.0;
			mnanom = mnanom*DTOR;	# Mean anomaly between 0-2pi radians 

			eclong = mnlong + 1.915*math.sin(mnanom) + 0.020*math.sin(2.0*mnanom);
			eclong = iEEERemainder(eclong,360.0);
			if( eclong < 0.0 ):
				eclong += 360.0;
			eclong = eclong*DTOR;	# Ecliptic longitude between 0-2pi radians

			oblqec = ( 23.439 - 0.0000004*time )*DTOR;   # Obliquity of ecliptic in radians
			num = math.cos(oblqec)*math.sin(eclong);
			den = math.cos(eclong);
			ra  = math.atan(num/den);	# Right ascension in radians
			if( den < 0.0 ):
				ra += pi;
			elif( num < 0.0 ):
				ra += 2.0*pi;

			dec = math.asin( math.sin(oblqec)*math.sin(eclong) );  # Declination in radians

			gmst = 6.697375 + 0.0657098242*time + zulu;
			gmst = iEEERemainder(gmst,24.0);
			if( gmst < 0.0 ):
				gmst += 24.0;			# Greenwich mean sidereal time in hours 

			lmst = gmst + lng/15.0;
			lmst = iEEERemainder(lmst,24.0);
			if( lmst < 0.0 ):
				lmst += 24.0;
			lmst = lmst*15.0*DTOR;		# Local mean sidereal time in radians 

			ha = lmst - ra;
			if( ha < -pi ):
				ha += 2*pi;
			elif( ha > pi ):
				ha -= 2*pi;				# Hour angle in radians between -pi and pi 

			lat = lat*DTOR;				# Change latitude to radians 

			arg = math.sin(dec)*math.sin(lat) + math.cos(dec)*math.cos(lat)*math.cos(ha);  # For elevation in radians
			if( arg > 1.0 ):
				elv = pi/2.0;
			elif( arg < -1.0 ):
				elv = -pi/2.0;
			else:
				elv = math.asin(arg);

			if( math.cos(elv) == 0.0 ):
				azm = pi;		# Assign azimuth = 180 deg if elv = 90 or -90
			else:
						# For solar azimuth in radians per Iqbal
				arg = ((math.sin(elv)*math.sin(lat)-math.sin(dec))/(math.cos(elv)*math.cos(lat))); # for azimuth
				if( arg > 1.0 ):
					azm = 0.0;              # Azimuth(radians)
				elif( arg < -1.0 ):
					azm = pi;
				else:
					azm = math.acos(arg);

				if( ( ha <= 0.0 and ha >= -pi) or ha >= pi ):
					azm = pi - azm;
				else:
					azm = pi + azm;
			

			elv = elv/DTOR;		# Change to degrees for atmospheric correction
			if( elv > -0.56 ):
				refrac = 3.51561*( 0.1594 + 0.0196*elv + 0.00002*elv*elv )/( 1.0 + 0.505*elv + 0.0845*elv*elv );
			else:
				refrac = 0.56;
			if( elv + refrac > 90.0 ):
				elv = 90.0*DTOR;
			else:
				elv = ( elv + refrac )*DTOR ; # Atmospheric corrected elevation(radians)

			E = ( mnlong - ra/DTOR )/15.0;       # Equation of time in hours
			if( E < - 0.33 ):   # Adjust for error occuring if mnlong and ra are in quadrants I and IV
				E += 24.0;
			elif( E > 0.33 ):
				E -= 24.0;

			arg = -math.tan(lat)*math.tan(dec);
			if( arg >= 1.0 ):
				ws = 0.0;						# No sunrise, continuous nights
			elif( arg <= -1.0 ):
				ws = pi;						# No sunset, continuous days
			else:
				ws = math.acos(arg);			# Sunrise hour angle in radians

			# Sunrise and sunset in local standard time
			sunrise = 12.0 - (ws/DTOR)/15.0 - (lng/15.0 - tz) - E;
			sunset  = 12.0 + (ws/DTOR)/15.0 - (lng/15.0 - tz) - E;

			Eo = 1.00014 - 0.01671*math.cos(mnanom) - 0.00014*math.cos(2.0*mnanom);  # Earth-sun distance (AU)   
			Eo = 1.0/(Eo*Eo);					# Eccentricity correction factor
			tst = hour + minute/60.0 + (lng/15.0 - tz) + E;  # True solar time (hr) 
			zen = 0.5*pi - elv;					#  Zenith angle		
				# End of SolarPos method
            
            
			return azm, zen, elv, dec, sunrise, sunset, Eo, tst;
			# End of solarPos


# In[15]:





# In[14]:


def iEEERemainder(x,y):
    z = x-y*round(x/y)
    return z;
    
def julian(year, month, day):
    		
	# Returns julian day of year
    i=1; jday=0; k=0;
    nday = [31,28,31,30,31,30,31,31,30,31,30,31];

    if( year % 4 == 0 ):
        k = 1;
    while( i < month ):
        jday += nday[i-1];
        i += 1;
    if( month > 2 ):
        jday += k + day;
    else:
        jday += day;	
    
    return jday;


# In[16]:


# Distance between rows for no shading on Dec 21 at 9 am (Northern Hemisphere) or Jun 21st (Southern Hemisphere)
DD = rowSpacing(beta = np.round(metData.latitude), sazm, metData.latitude, metData.longitude, metData.timezone, 9, 0.0)
DD


# In[66]:


#(beta, sazm, lat, lng, tz, hour, minute):
    
beta = np.round(metData.latitude)
sazm = sazm
lat = metData.latitude
lng = metData.longitude
tz = metData.timezone
hour = 9
minute = 0.0


# In[52]:


lat = 51.88999938964844 
lng = -178.05999755859375
tz = -10
beta = np.round(lat)
beta
sazm = 180


# In[105]:


lat = 47.6062
lng = -122.3321
beta = 20
tz = -7
sazm = 180


# In[106]:


DD = bifacialvf.vf.rowSpacing(beta, sazm, lat, lng, tz, 9, 0.0)
DD


# In[107]:


normalized_pitch = DD + np.cos(np.round(lat) / 180.0 * np.pi)
pitch = normalized_pitch*y*1
pitch


# In[108]:


normalized_pitch


# In[68]:


DTOR = math.pi / 180.0  # Factor for converting from degrees to radians

beta = beta * DTOR  # Tilt from horizontal of the PV modules/panels, in radians
sazm = sazm * DTOR  # Surface azimuth of PV module/pamels, in radians


# In[69]:


if lat >= 0:
    print("Yes")


# In[70]:


[azm, zen, elv, dec, sunrise, sunset, Eo, tst] = solarPos (2014, 12, 21, hour, minute, lat, lng, tz)
[azm, zen, elv, dec, sunrise, sunset, Eo, tst]


# In[61]:


tst = 8.877  ##DLL Forced value
minute -= 60.0 * (tst - hour);


# In[62]:


[azm, zen, elv, dec, sunrise, sunset, Eo, tst] = solarPos(2014, 12, 21, hour, minute, lat, lng, tz)
[azm, zen, elv, dec, sunrise, sunset, Eo, tst] 


# In[63]:


D = math.cos(sazm - azm) * math.sin(beta) / math.tan(elv)
D

