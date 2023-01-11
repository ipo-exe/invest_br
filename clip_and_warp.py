from osgeo import ogr
from osgeo import gdal
import os

# -----------------------------------------------------------------------------
# SETUP
# set input path
s_input_dir = "C:/gis/invest"
# set the grid file path
s_grid_file = "{}/grid_br_aoi.gpkg".format(s_input_dir)
# set the grid layer name
s_grid_lyr_name = "grid_br_aoi"
# set the LULC file path
# todo change by lulc_aoi.tif
s_lulc_file = "{}/mapbiomas_aoi.tif".format(s_input_dir)
# set output path
s_output_dir = "C:/bin/invest_br"

# -----------------------------------------------------------------------------
# AUX VARIABLES
# define projections
dct_projs = {
    'UTM 18N': 'EPSG:31972, SIRGAS 2000 / UTM zone 18N',
    'UTM 19N': 'EPSG:31973, SIRGAS 2000 / UTM zone 19N',
    'UTM 20N': 'EPSG:31974, SIRGAS 2000 / UTM zone 20N',
    'UTM 21N': 'EPSG:31975, SIRGAS 2000 / UTM zone 21N',
    'UTM 22N': 'EPSG:31976, SIRGAS 2000 / UTM zone 22N',
    'UTM 18S': 'EPSG:31978, SIRGAS 2000 / UTM zone 18S',
    'UTM 19S': 'EPSG:31979, SIRGAS 2000 / UTM zone 19S',
    'UTM 20S': 'EPSG:31980, SIRGAS 2000 / UTM zone 20S',
    'UTM 21S': 'EPSG:31981, SIRGAS 2000 / UTM zone 21S',
    'UTM 22S': 'EPSG:31982, SIRGAS 2000 / UTM zone 22S',
    'UTM 23S': 'EPSG:31983, SIRGAS 2000 / UTM zone 23S',
    'UTM 24S': 'EPSG:31984, SIRGAS 2000 / UTM zone 24S',
    'UTM 25S': 'EPSG:31985, SIRGAS 2000 / UTM zone 25S',
}

# -----------------------------------------------------------------------------
# OPEN DATASETS

# Open the grid GeoPackage
ds_grid = ogr.Open(s_grid_file)
# Get the grid layer
lyr_grid = ds_grid.GetLayerByName(s_grid_lyr_name)
# Count the features
n_feature_count = lyr_grid.GetFeatureCount()
zero_size = len(str(n_feature_count))

# -----------------------------------------------------------------------------

# Iterate over the features in the layer
n_count = 1
for feature in lyr_grid:
    # Get the feature's attributes
    dct_attributes = feature.items()
    s_id = 'ID{}'.format(dct_attributes['id'])
    s_sector_name = 'S{}_{}'.format(str(n_count).zfill(zero_size), s_id)
    print(s_sector_name)

    # create output folder
    s_lcl_dir = '{}/{}'.format(s_output_dir, s_sector_name)
    os.mkdir(s_lcl_dir)

    # name output file
    s_filepath_out = '{}/lulc.tif'.format(s_lcl_dir)

    # get bbox
    min_x = dct_attributes['left']   # -39.85121,
    max_y = dct_attributes['top']    # -14.36413
    max_x = dct_attributes['right']  # -39.19078,
    min_y = dct_attributes['bottom'] # -15.03517

    # deploy extent list
    lst_extent = [
        min_x,
        min_y,
        max_x,
        max_y
    ]
    # get projection full name
    s_proj = dct_projs[dct_attributes['Fuso UTM']]

    # define options
    options = gdal.WarpOptions(
        format='GTiff',
        outputBounds=lst_extent,
        outputBoundsSRS='EPSG:4326, WGS 84',
        xRes=30,
        yRes=30,
        srcSRS='EPSG:4326, WGS 84',
        dstSRS=s_proj,
        outputType=0,
        resampleAlg='near',
        dstNodata=255
    )
    print('processing ...')

    # call WARP
    ds_out = gdal.Warp(
        s_filepath_out,
        s_lulc_file,
        options=options
    )
    n_count = n_count + 1
    print()
