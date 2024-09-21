# Working-with-SWORD-Database

Abstract for each script:

"pass_extract.py"
    - Stores the data from shapefile(cropped one) to a geo dataframe(gdf).
    - Loops through the row in gdf and extracts data from the 'swot_orbit' column
    - Since data in the column are separated by space, the script splits the data by space and stores it in a set(to prevent repitition of pass numbers)
    - Converts the set into a list.

"data_download.py"
    - Extracts pass number from previous script, and uses it to download SWOT data.
    - Tackles the issue of missing data for certain pass number by introducing "try...except" statement for IndexError.
    - Converts column within the gdf that have too high values into string such that it doesn't encounter errors.
    - The data obtained using the pass numbers can also contain data from an entirely different basin, therefore filters the data according to the reach ids obtained from previous scripts.
    - Converts the filtered gdf to a shapefile.
    

