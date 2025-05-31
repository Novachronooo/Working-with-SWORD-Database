import requests
import json
import pandas as pd
import numpy as np
import os
import time
from pathlib import Path
from io import StringIO
from datetime import datetime

def filter_reach_ids_with_valid_discharge(df):
    """
    Filter reach IDs to only include those where all discharge columns have non-NA values.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The input dataframe with discharge columns
    
    Returns
    -------
    list : List of unique reach IDs with valid discharge data
    """
    print("Filtering reach IDs based on discharge data availability...")
    
    # Find all columns that start with "discharge_"
    discharge_columns = [col for col in df.columns if col.startswith('discharge_')]
    print(f"Found discharge columns: {discharge_columns}")
    
    # Filter rows where all discharge columns are not NA/null
    # Using notna() to check for non-NA values across all discharge columns
    mask = df[discharge_columns].notna().all(axis=1)
    filtered_df = df[mask]
    
    print(f"Original dataset: {len(df)} rows")
    print(f"After filtering for complete discharge data: {len(filtered_df)} rows")
    
    # Get unique reach IDs from filtered data
    unique_reach_ids = filtered_df['reach_id'].unique()
    
    print(f"Unique reach IDs with complete discharge data: {len(unique_reach_ids)}")
    
    return unique_reach_ids

def download_timeseries_for_reach(reach_id, base_download_dir="datasets/timeseries_downloads"):
    """
    Download time series data for a specific reach ID using the API.
    
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
        
        # Define query parameters
        feature = "Reach"
        feature_id = str(reach_id)
        start_time = "2023-03-30T00:00:00Z"
        end_time = "2025-01-25T00:00:00Z"
        output = "csv"
        fields = "reach_id,time_str,wse,width"
        
        # Build the URL
        url = (
            f"https://soto.podaac.earthdatacloud.nasa.gov/hydrocron/v1/timeseries?"
            f"feature={feature}&feature_id={feature_id}&start_time={start_time}"
            f"&end_time={end_time}&output={output}&fields={fields}"
        )
        
        print(f"  Making API request...")
        
        # Make the GET request
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"  Error: API request failed. Status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        # Parse JSON response
        hydrocron_response = response.json()
        
        # Check if results exist
        if 'results' not in hydrocron_response or 'csv' not in hydrocron_response['results']:
            print(f"  Warning: No CSV data found in response for reach {reach_id}")
            return False
        
        # Extract CSV string from the JSON response
        csv_str = hydrocron_response['results']['csv']
        
        if not csv_str or csv_str.strip() == '':
            print(f"  Warning: Empty CSV data for reach {reach_id}")
            return False
        
        # Convert CSV string to DataFrame
        df = pd.read_csv(StringIO(csv_str))
        
        if df.empty:
            print(f"  Warning: Empty DataFrame for reach {reach_id}")
            return False
        
        # Convert time_str to datetime and format as MM/DD/YYYY
        if 'time_str' in df.columns:
            # Parse ISO datetime format and convert to MM/DD/YYYY
            df['time_str'] = pd.to_datetime(df['time_str']).dt.strftime('%m/%d/%Y')
        
        print(f"  Successfully retrieved {len(df)} records")
        
        # Create download directory if it doesn't exist
        Path(base_download_dir).mkdir(parents=True, exist_ok=True)
        
        # Save DataFrame as CSV with reach_id as filename
        output_filename = f"{reach_id}.csv"
        output_path = os.path.join(base_download_dir, output_filename)
        
        df.to_csv(output_path, index=False)
        
        print(f"  Data saved to: {output_path}")
        print(f"  Sample data:")
        print(f"  {df.head(2).to_string(index=False)}")
        
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
        
        print(f"CSV file loaded successfully. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Filter reach IDs based on discharge data availability
        unique_reach_ids = filter_reach_ids_with_valid_discharge(df)
        
        if len(unique_reach_ids) == 0:
            print("No reach IDs found with complete discharge data. Exiting.")
            return
        
        # Create base download directory
        base_download_dir = "datasets/timeseries_downloads"
        Path(base_download_dir).mkdir(parents=True, exist_ok=True)
        
        # Process each reach ID
        successful_downloads = 0
        failed_downloads = 0
        
        for i, reach_id in enumerate(unique_reach_ids, 1):
            print(f"\n[{i}/{len(unique_reach_ids)}] Processing reach ID: {reach_id}")
            
            success = download_timeseries_for_reach(reach_id, base_download_dir)
            
            if success:
                successful_downloads += 1
            else:
                failed_downloads += 1
            
            # Add a delay between requests to be respectful to the server
            time.sleep(2)  # Increased delay for API requests
        
        # Summary
        print(f"\n=== Download Summary ===")
        print(f"Total reach IDs processed: {len(unique_reach_ids)}")
        print(f"Successful downloads: {successful_downloads}")
        print(f"Failed downloads: {failed_downloads}")
        print(f"Success rate: {successful_downloads/len(unique_reach_ids)*100:.1f}%")
        print(f"CSV files saved to: {base_download_dir}")
        
    except FileNotFoundError:
        print(f"Error: Could not find CSV file at {csv_file_path}")
        print("Please check the file path and make sure the file exists.")
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")

if __name__ == "__main__":
    main()