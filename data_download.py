import pass_extract
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

# Authentication for Earth Access
auth = earthaccess.login(persist=True)

continent_code = "NA"

# List to store download links
links_list = []

# Fetch data links for each pass number
for p in pass_extract.pass_numbers:
    try:
        river_results = earthaccess.search_data(short_name='SWOT_L2_HR_RIVERSP_2.0', 
                                                temporal=('2023-01-01 00:00:00', '2024-08-31 23:59:59'),
                                                granule_name="*Reach*_" + p + "_" + continent_code + "*")
        
        for result in river_results:
            river_link = earthaccess.results.DataGranule.data_links(result, access='external')[0]
            links_list.append(river_link)

    except IndexError as e:
        pass

# Download files (if uncommented, ensure the directory exists)
earthaccess.download(links_list, "./data_downloads")

# Extract files
filenames = [link.split("/")[-1] for link in links_list]
for filename in filenames:
    with zipfile.ZipFile(f'data_downloads/{filename}', 'r') as zip_ref:
        zip_ref.extractall('data_downloads')

filename_shps = [filename.replace('zip', 'shp') for filename in filenames]

# Load shapefiles into GeoDataFrames
SWOT_HR_shps = [gpd.read_file(f'data_downloads/{filename_shp}') for filename_shp in filename_shps]

# Combine all GeoDataFrames into one
SWOT_HR_df = gpd.GeoDataFrame(pd.concat(SWOT_HR_shps, ignore_index=True))

#replacing -999999999999 with NaN
SWOT_HR_df.replace(-999999999999, np.nan,inplace=True)
SWOT_HR_df['time'] = SWOT_HR_df['time'].astype(str)
SWOT_HR_df['time_tai'] = SWOT_HR_df['time_tai'].astype(str)
SWOT_HR_df['p_wid_var'] = SWOT_HR_df['p_wid_var'].astype(str)
SWOT_HR_df['area_tot_u'] = SWOT_HR_df['area_tot_u'].astype(str)
SWOT_HR_df['area_det_u'] = SWOT_HR_df['area_det_u'].astype(str)
SWOT_HR_df['width_u'] = SWOT_HR_df['width_u'].astype(str)
#convert any column that starts with 'dschg' to string
# Loop through columns that start with 'dschg'
for col in SWOT_HR_df.columns:
    if col.startswith('dschg'):
        SWOT_HR_df[col] = SWOT_HR_df[col].astype(str)

#filter out the SWOT_HR_df such that it contains only those rows where the value from pass_extract.rivers is present
SWOT_HR_df = SWOT_HR_df[SWOT_HR_df['river_name'].isin(pass_extract.rivers)]
# Write shapefile 
SWOT_HR_df.to_file("Ohio_Basin_shapefile_output_filtered.shp")
print(f"Filtered shapefile saved to {'Ohio_Basin_shapefile_output_filtered.shp'}") 

