#-------------------------------------------------------------------------------
# Name          Polar Plot Streamflow Visualization
# Description:  App to display daily streamflow values in polar coordinates by date
# Author:       Chandler Engel
#               US Army Corps of Engineers
#               Cold Regions Research and Engineering Laboratory (CRREL)
#               Chandler.S.Engel@usace.army.mil
# Created:      07 August 2022
# Updated:      -
#
# Plotting code adapted from temperature plotting example by Christian Hill 
###https://scipython.com/blog/visualizing-the-temperature-in-cambridge-uk/              
#-------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import dataretrieval.nwis as nwis

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
plt.style.use('dark_background')

st.title('Streamflow Polar Plot Visualization')
form = st.form(key='my-form')
site = form.text_input('Enter USGS Gage ID', value='07289000')
submit = form.form_submit_button('Submit')



def get_data(site):
    df =nwis.get_record(sites=site, service='dv', start='1900-01-01', parameterCd='00060')
    df['flow'] = df['00060_Mean']
    df.index.name = 'date'
    df.index = df.index.tz_localize(None)
    return df

def process(df):
    # Select the maximum value on each day of the year.
    df2 = df.groupby(pd.Grouper(level='date', freq='D')).max()

    # Convert the timestamp to the number of seconds since the start of the year.
    df2['secs'] = (df2.index - pd.to_datetime(df2.index.year, format='%Y')).total_seconds()
    # Approximate the angle as the number of seconds for the timestamp divide by
    # the number of seconds in an average year.
    df2['angle'] = - df2['secs'] / (365.25 * 24 * 60 * 60) * 2 * (np.pi)

    # For the colourmap, the minimum is the largest multiple of 5 not greater than
    # the smallest value of T; the maximum is the smallest multiple of 5 not less
    # than the largest value of T, e.g. (-3.2, 40.2) -> (-5, 45).
    Tmin = 5 * np.floor(df2['flow'].min() / 5)
    Tmax = 5 * np.ceil(df2['flow'].max() / 5)

    # Normalization of the colourmap.
    norm = Normalize(vmin=Tmin, vmax=Tmax)
    c = norm(df2['flow'])
    return df2,c,norm

def plot_polar(df2,c,norm):
    fig = plt.figure(figsize=(10, 10), dpi=80)
    ax = fig.add_subplot(projection='polar')
    # We prefer 1 January (0 deg) on the top, but the default is to the
    # right, so offset by 90 deg.
    ax.set_theta_offset(np.pi/2)
    cmap = cm.turbo
    ax.scatter(df2['angle'], df2['flow']+3*np.std(df2.flow), c=cmap(c), s=2)

    # Tick labels.
    ax.set_xticks(np.arange(0, 2 * np.pi, np.pi / 6))
    #clunky/lazy mod to put labels in revese order so the plot goes clockwise
    ax.set_xticklabels(['Jan']+list(reversed(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']))[:-1])
    #ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    #                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.set_yticks([])

    # Add and title the colourbar.
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap),
                        ax=ax, orientation='vertical', pad=0.1)
    cbar.ax.set_title(r'$Q\;/\mathrm{cfs}$')
    
    st.pyplot(fig)
    #plt.show()

#site = '15304000'
def generate(site):
    siteINFO, md = nwis.get_info(sites=site)
    site_name = siteINFO.station_nm[0]
    st.write(site_name)
    
    df = get_data(site)
    df2,c,norm = process(df)
    plot_polar(df2,c,norm)
    
if submit:
    generate(site)
