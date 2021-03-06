'''
preprocess river data with qgis
either use directly in qgis console
or use in python (commented part, not implemented yet)
'''

import os
import glob
import processing

# extract layer from raster


def calculator(in_file, out_file, extent, expression):
    processing.run('qgis:rastercalculator', {'INPUT': in_file,
                                             'CELLSIZE': 100,
                                             'EXPRESSION': expression,
                                             'CRS': QgsCoordinateReferenceSystem('EPSG:3035'),
                                             'EXTENT': extent,
                                             'OUTPUT': out_file})


# compute layer statistics
def zonal_stat(in_file, zone_file, out_file):
    processing.run('qgis:rasterlayerzonalstats', {'INPUT': in_file,
                                                  'BAND': 1,
                                                  'ZONES': zone_file,
                                                  'ZONES_BAND': 1,
                                                  'OUTPUT_TABLE': out_file})

# reproject a layer


def reproject(in_file, out_file=None, crs='EPSG:4326'):
    if out_file is None:
        out_file = in_file.replace(".tif", "_reprojected.tif")
    processing.run('gdal:warpreproject', {"INPUT": in_file,
                                          "TARGET_CRS": QgsCoordinateReferenceSystem(crs),
                                          "RESAMPLING": 1,
                                          "OUTPUT": out_file})


'''
from qgis.core import QgsApplication, QgsVectorLayer, QgsCoordinateReferenceSystem
from qgis import processing

# Supply path to qgis install location
QgsApplication.setPrefixPath("D:/Software/QGIS/apps/qgis-ltr", True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()
'''

# Write your code here to load some layers, use processing
# algorithms, etc.
year = 2010

# list rivers shapefiles
shapefiles = glob.glob(f"./data/rivers/riparian_zones/{year}/*/*/*.shp")

# convert to vector layers
for shapefile in shapefiles:
    rasterized = shapefile.replace('.shp', '.tif')
    # vlayer = QgsVectorLayer(shapefile, "", "ogr")
    processing.run('gdal:rasterize', {"INPUT": shapefile,
                                      "FIELD": "CODE_1_12",
                                      "UNITS": 1,
                                      "WIDTH": 100.0,
                                      "HEIGHT": 100.0,
                                      "DATA_TYPE": 1,
                                      "OUTPUT": rasterized})

# list raster layers files
projected_tif = glob.glob(
    f"./data/rivers/riparian_zones/{year}/*/*/*.tif")

# merge raster layers
# outfile = f"./data/rivers/riparian_zones/{year}/riparian_zones.tif"
# processing.run('gdal:merge', {"INPUT": tif_files,
#                               "DATA_TYPE": 1,
#                               "OUTPUT": outfile})

processing.run('saga:mosaickrasterlayers', {"GRIDS": tif_files,
                                            "RESAMPLING": 1,
                                            "OVERLAP": 3,
                                            "TARGET_USER_XMIN": -5.125000000,
                                            "TARGET_USER_XMAX": 9.541666667,
                                            "TARGET_USER_YMIN": 41.375000000,
                                            "TARGET_USER_YMAX": 51.083333333,
                                            "TARGET_USER_SIZE": 100,
                                            "TARGET_USER_FITS": 1,
                                            "TARGET_OUT_GRID": outfile})

# Loire, Ebro and Garonne
interest_rivers = ["rpz_DU017A", "rpz_DU019A", "rpz_DU041A"]

extents = ['3240269.8547,3909569.8547,2408574.0426,2944074.0426 [EPSG:3035]',
           '3154460.7381,3758760.7381,1733799.1158,2327699.1158 [EPSG:3035]',
           '3374621.2481,3829821.2481,2198776.3571,2624776.3571 [EPSG:3035]']

interest_tif = [x for x in projected_tif if os.path.basename(x).split(".")[
    0] in interest_rivers]


def extract_zones(tif_file, zone_file, zone, expression, extent):
    out_file = tif_file.replace('.tif', f'_{zone}.tif')
    calculator(tif_file, out_file, extent,
               f'"{os.path.basename(tif_file).split(".")[0]}@1" {expression}')
    reprojected_out = out_file.replace(".tif", "_reprojected.tif")
    reproject(out_file, reprojected_out)
    zonal_stat(reprojected_out, zone_file,
               out_file.replace('.tif', '_stats.gpkg'))


# extract three layers and compute their stats
for i, tif in enumerate(interest_tif):
    zone_file = "./data/rivers/riparian_zones/france_tiles.tif"
    extract_zones(tif, zone_file, "urban", "= 1", extents[i])
    extract_zones(tif, zone_file, "crop", "= 2", extents[i])
    extract_zones(tif, zone_file, "land", ">= 3", extents[i])


'''
# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()
'''
