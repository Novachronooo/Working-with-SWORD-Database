import requests
import json
import pprint
import xarray as xr
import geojson
import matplotlib.pyplot as plt
import contextily as cx
import plotly.graph_objects as go
from IPython.display import JSON, Image
import earthaccess
import pandas as pd
import os
import time
from pathlib import Path

# Authentication for Earth Access
auth = earthaccess.login(persist=True)

def response_to_FeatureCollection(response):
    """
    This function will return a geojson.FeatureCollection representation of the features found in the provided response.
    Parameters
    ----------
        response : requests.Response - a Response object returned from a GET request on the rivers or nodes endpoint.
    Returns
    -------
        geojson.FeatureCollection - FeatureCollection containing all features extracted from the response.
    """
    featureList = []
    for reach_id, reach_json in response.json()['results'].items():
        reach_feature = geojson.loads(json.dumps(reach_json))
        reach_feature['properties']={k:v for k,v in reach_json.items() if k not in ['geojson', 'geometry']}
        featureList.append(reach_feature)
    featureCollection = geojson.FeatureCollection(featureList)
    return featureCollection

def download_data_for_reach(reach_id, base_download_dir="datasets/data_downloads"):
    """
    Download SWOT data for a specific reach ID.
    
    Parameters
    ----------
    reach_id : str
        The reach ID to download data for
    base_download_dir : str
        Base directory for downloads
    
    Returns
    -------
    bool : True if successful, False if failed
    """
    try:
        print(f"Processing reach ID: {reach_id}")
        
        # Get reach information
        response_reach = requests.get(f"https://fts.podaac.earthdata.nasa.gov/rivers/reach/{reach_id}")
        
        if response_reach.status_code != 200:
            print(f"  Error: Could not fetch data for reach {reach_id}. Status code: {response_reach.status_code}")
            return False
        
        featureCollection_reach = response_to_FeatureCollection(response_reach)
        
        if not featureCollection_reach['features']:
            print(f"  Warning: No features found for reach {reach_id}")
            return False
        
        # Extract coordinates
        lats = [xy[1] for feature in featureCollection_reach['features'] for xy in feature['coordinates']]
        lons = [xy[0] for feature in featureCollection_reach['features'] for xy in feature['coordinates']]
        
        if not lats or not lons:
            print(f"  Warning: No coordinates found for reach {reach_id}")
            return False
        
        # Find bounding box
        maxlat, maxlon, minlat, minlon = max(lats), max(lons), min(lats), min(lons)
        
        print(f"  Bounding box: ({minlon:.4f}, {minlat:.4f}, {maxlon:.4f}, {maxlat:.4f})")
        
        # Search for SWOT data
        results = earthaccess.search_data(
            short_name='SWOT_L2_HR_Raster_2.0', 
            bounding_box=(minlon, minlat, maxlon, maxlat)
        )
        
        if not results:
            print(f"  Warning: No SWOT data found for reach {reach_id}")
            return False
        
        # Create download directory for this reach
        reach_download_dir = os.path.join(base_download_dir, f"reach_{reach_id}")
        Path(reach_download_dir).mkdir(parents=True, exist_ok=True)
        
        # Download data
        print(f"  Found {len(results)} datasets. Downloading first dataset...")
        downloaded_files = earthaccess.download([results[0]], reach_download_dir)
        
        print(f"  Successfully downloaded data for reach {reach_id}")
        print(f"  Files saved to: {reach_download_dir}")
        
        return True
        
    except Exception as e:
        print(f"  Error processing reach {reach_id}: {str(e)}")
        return False

def main():
    # Path to your CSV file
    csv_file_path = r"C:\Project\SWORD\sword_discharge_data_combined.csv"
    
    try:
        # Read CSV file
        print("Reading CSV file...")
        df = pd.read_csv(csv_file_path)
        
        # Extract unique reach IDs
        unique_reach_ids = df['reach_id'].unique()
        print(f"Found {len(unique_reach_ids)} unique reach IDs")
        
        # Create base download directory
        base_download_dir = "datasets/data_downloads"
        Path(base_download_dir).mkdir(parents=True, exist_ok=True)
        
        # Process each reach ID
        successful_downloads = 0
        failed_downloads = 0
        
        for i, reach_id in enumerate(unique_reach_ids, 1):
            print(f"\n[{i}/{len(unique_reach_ids)}] Processing reach ID: {reach_id}")
            
            success = download_data_for_reach(reach_id, base_download_dir)
            
            if success:
                successful_downloads += 1
            else:
                failed_downloads += 1
            
            # Add a small delay between requests to be respectful to the server
            time.sleep(1)
        
        # Summary
        print(f"\n=== Download Summary ===")
        print(f"Total reach IDs processed: {len(unique_reach_ids)}")
        print(f"Successful downloads: {successful_downloads}")
        print(f"Failed downloads: {failed_downloads}")
        print(f"Success rate: {successful_downloads/len(unique_reach_ids)*100:.1f}%")
        
    except FileNotFoundError:
        print(f"Error: Could not find CSV file at {csv_file_path}")
        print("Please check the file path and make sure the file exists.")
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")

if __name__ == "__main__":
    main()