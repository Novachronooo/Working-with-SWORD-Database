import glob
import h5netcdf
import xarray as xr
import pandas as pd
import geopandas as gpd
import contextily as cx
import numpy as np
import matplotlib.pyplot as plt
import hvplot.xarray
import zipfile
import earthaccess

input_shapefile = "D:\\Environment Engineering\\Project\\ARCGIS\\OHIO_Basin_Extracted_From_HB74.shp"

#read shapefile using geopandas
Ohio_Basin_df = gpd.read_file(input_shapefile)

pass_numbers = set()

column_name = 'swot_orbit'
#loop through each row in the shapefile
for index, row in Ohio_Basin_df.iterrows():
    #split the pass numbers in 'swot_orbit' column column 
    if pd.notna(row[column_name]) and row[column_name] is not None:
        orbit_values = [values.strip() for values in row[column_name].split()]

        #add the pass numbers to the set
        pass_numbers.update(orbit_values)

#convert the set to a list
pass_numbers = list(pass_numbers)  
print(pass_numbers)


