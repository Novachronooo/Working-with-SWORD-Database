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
    river_results = earthaccess.search_data(short_name='SWOT_L2_HR_RIVERSP_2.0', 
                                            temporal=('2023-01-01 00:00:00', '2024-08-31 23:59:59'),
                                            granule_name="*Reach*_" + p + "_" + continent_code + "*")
    
    for result in river_results:
        river_link = earthaccess.results.DataGranule.data_links(result, access='external')[0]
        links_list.append(river_link)

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

output_shapefile = "C:\\Project\\Working with SWOT\\Ohio_Basin_shapefile_output.shp"

# Write shapefile
SWOT_HR_df.to_file(output_shapefile)

