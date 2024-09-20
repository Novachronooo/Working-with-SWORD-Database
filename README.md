# Working-with-SWORD-Database

Abstract for each script:

"pass_extract.py"
    - Stores the data from shapefile(cropped one) to a geo dataframe(gdf).
    - Loops through the row in gdf and extracts data from the 'swot_orbit' column
    - Since data in the column are separated by space, the script splits the data by space and stores it in a set(to prevent repitition of pass numbers)
    - Converts the set into a list.

