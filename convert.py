from osgeo import gdal
import numpy as np

# -----------------------------------------------------------------------------
# DEFINE FILES AND FOLDERS

# table of mapbiomas
s_table_file = "C:/gis/invest/mapbiomas_c7_table.txt"

# mapbiomas map in AOI
s_mapbiomas_file = "C:/gis/invest/mapbiomas_aoi.tif"

# biomas map in AOI
s_biomas_file = "C:/gis/invest/biomas_aoi.tif"

# output directory
s_output_dir = "C:/gis/invest"

# boolean control
b_skip_raster = False

# -----------------------------------------------------------------------------
# DEFINE VARIABLES

# deploy dict for biomes
dct_biomas = {
    1 : "Amazonia",
    2 : "Caatinga",
    3 : "Cerrado",
    4 : "Mata Atlantica",
    5 : "Pampa",
    6 : "Pantanal"
}

# -----------------------------------------------------------------------------
# READ TABLE
f = open(s_table_file, 'r')
lst_lines_full = f.readlines()
f.close()

# -----------------------------------------------------------------------------
# SPLIT NATURAL FROM UNNATURAL
# deploy empty lists
lst_natural = []
lst_natural_ids = []
lst_unnatural = []
lst_unnatural_ids = []
# loop
for line in lst_lines_full:
    lst_line = line[:-1].split(";")
    if lst_line[2].lower() == "natural":
        # append line
        lst_natural.append(line[:-1])
        # append id
        lst_natural_ids.append(int(lst_line[0]))
    elif lst_line[2].lower() == "unnatural":
        # append line
        lst_unnatural.append(line[:-1])
        # append id
        lst_unnatural_ids.append(int(lst_line[0]))

# -----------------------------------------------------------------------------
# READ RASTER FILES
print("reading")
# -- Mapbiomas

# Open the raster file using gdal
raster_mapbiomas = gdal.Open(s_mapbiomas_file)

# Get the raster band
band_mapbiomas = raster_mapbiomas.GetRasterBand(1)

# Read the raster data as a numpy array
grid_mapbiomas = band_mapbiomas.ReadAsArray()

# truncate to byte integer
grid_mapbiomas = grid_mapbiomas.astype(np.uint8)

# -- Biomas

# Open the raster file using gdal
raster_biomas = gdal.Open(s_biomas_file)

# Get the raster band
band_biomas = raster_biomas.GetRasterBand(1)

# Read the raster data as a numpy array
grid_biomas = band_biomas.ReadAsArray()

# truncate to byte integer
grid_biomas = grid_biomas.astype(np.uint8)

# -- Collect useful metadata

raster_x_size = raster_mapbiomas.RasterXSize
raster_y_size = raster_mapbiomas.RasterYSize
raster_projection = raster_mapbiomas.GetProjection()
raster_geotransform = raster_mapbiomas.GetGeoTransform()

# -- Close the rasters

raster_mapbiomas = None
raster_biomas = None

# -----------------------------------------------------------------------------
# PROCESSING -- GET UNIQUE BIOMAS ID
print('processing ... unique values')
# call np.unique()
lst_unique_biomas_full = np.unique(grid_biomas)
# get non-zero values
lst_unique_biomas = []
for e in lst_unique_biomas_full:
    if e == 0:
        pass
    else:
        lst_unique_biomas.append(e)
n_biomas = len(lst_unique_biomas)

# -----------------------------------------------------------------------------
# PROCESSING -- GET CONVERSION TABLE
print("processing ... table")
lst_new_table = []
# append header
lst_line = lst_lines_full[0].split(";")
# change Type to Biome
lst_line[2] = "Biome"
lst_line = lst_line[:-1]
s_row = ";".join(lst_line)

lst_new_table.append("{}\n".format(s_row))
# deploy conversion dict
dct_convert = {}
# deploy counter
n_counter = 1

# --------- append unnatural 
for line in lst_unnatural:
    # get line list
    lst_line = line.split(";")
    
    # get mapbiomas id
    n_mapbiomas_id = int(lst_line[0])
    
    # built key
    dct_convert[n_mapbiomas_id] = n_counter
    
    # change line id
    lst_line[0] = str(n_counter)
    
    # append to new table
    s_row = ";".join(lst_line[:-1])
    lst_new_table.append("{}\n".format(s_row))
    
    # update counter
    n_counter = n_counter + 1

# --------- append roads 
lst_roads = [
    "Road Low Traffic",
    "Road Moderate Traffic",
    "Road High Traffic"
]
for e in lst_roads:
    # get row
    lst_line = ["0", e, "Unnatural"]
    lst_line[0] = str(n_counter)
    
    # append to new table
    s_row = ";".join(lst_line)
    lst_new_table.append("{}\n".format(s_row))
    
    # update counter
    n_counter = n_counter + 1 

# --------- append natural 
for b in lst_unique_biomas:
    s_biome_name = dct_biomas[b]
    for line in lst_natural:
        # get line list
        lst_line = line.split(";")
        
        # change name
        lst_line[2] = s_biome_name
        
        # get mapbiomas id
        n_mapbiomas_id = int(lst_line[0])
        
        # scale id
        n_scale_id = n_mapbiomas_id + (b * 100)
        
        # built key
        dct_convert[n_scale_id] = n_counter
        
        # change line id
        lst_line[0] = str(n_counter)
        
        # change line name
        s_old_name = lst_line[1]
        s_new_name = "{} - {}".format(s_old_name, s_biome_name)
        lst_line[1] = s_new_name
        
        # append to new table
        s_row = ";".join(lst_line[:-1])
        lst_new_table.append("{}\n".format(s_row))
        
        # update counter
        n_counter = n_counter + 1
'''
# --------- print
for line in lst_new_table:
    print(line)
'''

# -----------------------------------------------------------------------------
# EXPORT LULC TABLE
s_file_name = "{}/lulc_table.csv".format(s_output_dir)
with open(s_file_name, "w") as file:
    file.writelines(lst_new_table)


if b_skip_raster:
    # -----------------------------------------------------------------------------
    # PROCESSING -- SCANNING LOOP
    print("processing ... loop")
    tpl_shape = np.shape(grid_mapbiomas)

    # deploy grid
    grid_lulc_noroads = np.zeros(tpl_shape, dtype=np.uint8)

    # main loop
    for i in range(tpl_shape[0]):
        for j in range(tpl_shape[1]):
            n_lcl_mapbiomas = grid_mapbiomas[i][j]
            # off map
            if n_lcl_mapbiomas == 0:
                pass
            else:
                if n_lcl_mapbiomas in lst_unnatural_ids:
                    grid_lulc_noroads[i][j] = dct_convert[n_lcl_mapbiomas]
                else:
                    n_lcl_biomas = grid_biomas[i][j]
                    if n_lcl_biomas == 0:
                        pass
                    else:
                        n_scale_id = n_lcl_mapbiomas + (100 * n_lcl_biomas)
                        grid_lulc_noroads[i][j] = dct_convert[n_scale_id]

    # -----------------------------------------------------------------------------
    # EXPORT RASTER FILE
    print("export ... ")
    # Get the driver to create the new raster
    driver = gdal.GetDriverByName('GTiff')

    # Create a new raster with the same dimensions as the original
    raster_output = driver.Create(
        "{}/lulc_noroads_aoi_v1.tif".format(s_output_dir),
        raster_x_size,
        raster_y_size,
        1,
        gdal.GDT_Int16)

    # Set the projection and geotransform of the new raster to match the original
    raster_output.SetProjection(raster_projection)
    raster_output.SetGeoTransform(raster_geotransform)

    # Write the new data to the new raster
    raster_output.GetRasterBand(1).WriteArray(grid_lulc_noroads)

    # Close
    raster_output = None






