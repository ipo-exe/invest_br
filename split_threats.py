from osgeo import gdal
import shutil
import numpy as np 
import os


# -----------------------------------------------------------------------------
# DEFINE FILES AND FOLDERS

# table of lulc
s_lulc_table = "C:/gis/invest/lulc.csv"

# table of threats
s_threats_table = "C:/gis/invest/threats.csv"

# main directory
s_dir = "C:/bin/invest_br"

# dirs:
lst_dir = os.listdir(s_dir)

# get driver
driver_tiff = gdal.GetDriverByName('GTiff') 

# -----------------------------------------------------------------------------
# GET THREATS DICT

# read lulc table:
f = open(s_lulc_table, "r")
lst_lulc_lines = f.readlines()
f.close()

# read threats table:
f = open(s_threats_table, "r")
lst_threat_lines = f.readlines()
f.close()

# collect names and filenames
lst_threats_names = []
lst_threats_files = []
for i in range(1, len(lst_threat_lines)):
    s_row = lst_threat_lines[i]
    s_threat_name = s_row.split(",")[0].lower().strip().replace("_", " ")
    s_threat_filename = s_row.split(",")[-1].strip()
    lst_threats_names.append(s_threat_name)
    lst_threats_files.append(s_threat_filename)

# collect ids
lst_threats_ids = []
for threat in lst_threats_names:
    for line in lst_lulc_lines[1:]:
        lcl_lulc = line.split(",")[1].lower()
        if threat.lower() == lcl_lulc:
            lcl_id = int(line.split(",")[0])
            lst_threats_ids.append(lcl_id)

# built dict
dct_threats = {}
for i in range(len(lst_threats_files)):
    dct_threats[lst_threats_files[i]] = lst_threats_ids[i]

# -----------------------------------------------------------------------------
# MAIN LOOP IN DIRS
for d in lst_dir:
    # define local dir
    s_lcl_dir = '{}/{}'.format(s_dir, d)
    
    # copy threat table
    shutil.copyfile(
    s_threats_table,
    '{}/threats.csv'.format(s_lcl_dir)
    )
    
    # define lulc input file
    s_lulc_input = '{}/lulc.tif'.format(s_lcl_dir)

    # read array
    raster_lulc = gdal.Open(s_lulc_input, 0)
    grd_lulc = raster_lulc.GetRasterBand(1).ReadAsArray()
    # truncate to byte integer
    grd_lulc = grd_lulc.astype(np.uint8)
    
    # get resolutions
    x = raster_lulc.RasterXSize 
    y = raster_lulc.RasterYSize 
    
    # threats loop
    for t in dct_threats:
        # get number id
        n_threat = dct_threats[t]
        s_output = '{}/{}'.format(s_lcl_dir, t)
            
        # set output raster
        raster_threat = driver_tiff.Create(
            s_output,
            xsize=x,
            ysize=y,
            bands=1,
            eType=gdal.GDT_Byte
        )
        # set geotranform 
        raster_threat.SetGeoTransform(raster_lulc.GetGeoTransform()) 

        # set proj
        raster_threat.SetProjection(raster_lulc.GetProjection()) 

        # read band 1
        grd_threat = ds_threat.GetRasterBand(1).ReadAsArray() 
        #
        # compute threat boolean
        grd_threat = 1 * (grd_lulc == n_threat)
        #
        #
        # overwrite 
        raster_threat.GetRasterBand(1).WriteArray(grd_threat ) 
        # close layers 
        raster_threat = None