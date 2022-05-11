import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')

from datetime import datetime
import json
import numpy
import geemap
import ee
ee.Initialize()

import imagery
import sampleRegions
import imageToVectors
import getPolygonData
import trainClassifier

import chunkFeatureSource
import processFeature

start = datetime.now()

# chunks = chunkFeatureSource.chunkFeatureSource('./data/input/grid_test_4326.geojson')
# chunks = chunkFeatureSource.chunkFeatureSource2('./data/input/GMB/GMB_intersection.geojson')

bands = ['SR_B2_mean', 'SR_B3_mean', 'SR_B4_mean', 'SR_B5_mean', 'SR_B6_mean', 'SR_B7_mean', 'NDVI', 'NDWI', 'SAVI']
# aoi = geemap.geojson_to_ee('./data/input/NER_chunks_admin01.geojson')
extent = geemap.geojson_to_ee('./data/input/GMB/GMB_extent.geojson')
aoi = geemap.geojson_to_ee('./data/input/GMB/GMB_intersection8.geojson')
nameProp = 'uid'
# trainingDataset = ee.FeatureCollection('users/andreasrey/TrainingPoints_GMB_Kerewan')
trainingDataset = geemap.geojson_to_ee('./data/input/GMB/GMB_samplePoints.geojson')

print("1 - retrieving reference image (2020)")
referenceImage = imagery.get(extent, '2020-01-01', '2020-12-31')
print("3 - train classifier")
trained = trainClassifier.trainClassifier(referenceImage, bands, trainingDataset)
# trained = classifier.train(training, 'class', bands)
print("4 - retrieving image to be classified")
# image = imagery.get(aoi, '2021-01-01', '2021-12-31')
# print("5 - classify image")
# classified = image.select(bands).classify(trained)
# croplands_classification = classified.eq(0).selfMask()
def calculatesIndicator(
    feature: ee.Feature,
    classifiedImage: ee.Image
) -> ee.Feature:
    subName = feature.get(nameProp)
    subCroplands_Classification = imageToVectors.imageToVectors(classifiedImage, feature)
    geom = subCroplands_Classification.geometry()
    outGeom = geom
    # outGeom = None
    area_Classification_sqM = geemap.ee_num_round(geom.area(1), 0)
    if area_Classification_sqM.gt(0):
        indicators = getPolygonData.getPolygonData(classifiedImage, 'NDVI', geom, 4)
        props = {
            'period': '2021',
            'subregion': subName,
            'area_sqm': area_Classification_sqM,
            'croplands_min': indicators['min'],
            'croplands_mean': indicators['mean'],
            'croplands_max': indicators['max'],
            'croplands_stddev': indicators['stdDev']
        }
        # print(props)
        return ee.Feature(outGeom, props)
    else:
        props = {
            'period': '2021',
            'subregion': subName,
            'area_sqm': 0,
            'croplands_min': -999,
            'croplands_mean': -999,
            'croplands_max': -999,
            'croplands_stddev': -999
        }
        # print(props)
        return ee.Feature(outGeom, props)



print("6 - processing features")

global count
count = 0
selectors = [
    'subregion',
    'area_sqm',
    'croplands_min',
    'croplands_mean',
    'croplands_max',
    'croplands_stddev'
]
# for n in chunks:
#     count = count + 1
#     fc = processFeature.processFeature2(n)
#     image = imagery.get(fc, '2021-01-01', '2021-12-31')
#     classified = image.select(bands).classify(trained)
#     croplands_classification = classified.eq(0).selfMask()
#     def eachFeature(
#         feature: ee.Feature
#     ):
#         return calculatesIndicator(feature, croplands_classification)
#     output = fc.map(eachFeature)
#     ee.batch.Export.table.toDrive(output, 'GMB_' + str(count), 'EE_Exports_GMB', 'GMB_' + str(count), 'csv', selectors)
#     # geemap.ee_export_vector(output, './data/output/GMB_' + str(count) + '.csv', selectors)
#     # output = aoi.map(eachFeature)
def eachFeature(
    feature: ee.Feature
):
    image = imagery.get(feature, '2021-01-01', '2021-12-31')
    classified = image.select(bands).classify(trained)
    croplands_classification = classified.eq(0).selfMask()
    return calculatesIndicator(feature, croplands_classification)
# output = ee.FeatureCollection([aoi.first()]).map(eachFeature)
output = aoi.map(eachFeature)

mytask = ee.batch.Export.table.toDrive(output, 'GMB_test', 'EE_Exports_GMB', 'GMB_test', 'csv', selectors)
mytask.start()

# image = imagery.get(aoi.first(), '2021-01-01', '2021-12-31')
# listBands = image.bandNames()
# print(listBands.getInfo())


end = datetime.now()
length = end - start

print("7 - processing complete in " + str(length))

