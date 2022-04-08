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

import chunkFeatureSource
import processFeature

start = datetime.now()

chunks = chunkFeatureSource.chunkFeatureSource('./data/input/grid_test_4326.geojson')

bands = ['SR_B2_mean', 'SR_B3_mean', 'SR_B4_mean', 'SR_B5_mean', 'SR_B6_mean', 'SR_B7_mean', 'NDVI', 'NDWI', 'SAVI']
aoi = geemap.geojson_to_ee('./data/input/grid_test_4326.geojson')
nameProp = 'UID'
trainingDataset = ee.FeatureCollection('users/andreasrey/Training_NorthBankEastRegion')

print("1 - retrieving reference image (2020)")
referenceImage = imagery.get(aoi, '2020-01-01', '2020-12-31')
print("2 - sampling regions")
training = sampleRegions.sampleRegions(referenceImage, bands, trainingDataset)
classifier = ee.Classifier.smileRandomForest(100)
print("3 - train classifier")
trained = classifier.train(training, 'class', bands)
print("4 - retrieving image to be classified")
image = imagery.get(aoi, '2021-01-01', '2021-12-31')
print("5 - classify image")
classified = image.select(bands).classify(trained)
croplands_classification = classified.eq(0).selfMask()

def calculatesIndicator(
    feature: ee.Feature
) -> ee.Feature:
    subName = feature.get(nameProp)
    subCroplands_Classification = imageToVectors.imageToVectors(croplands_classification, feature)
    geom = subCroplands_Classification.geometry()
    area_Classification_sqM = geemap.ee_num_round(geom.area(1), 0)
    if area_Classification_sqM.gt(0):
        indicators = getPolygonData.getPolygonData(image, 'NDVI', geom, 4)
        props = {
            'period': '2021',
            'subregion': subName,
            'area_sqm': area_Classification_sqM,
            'croplands_min': indicators['min'],
            'croplands_mean': indicators['mean'],
            'croplands_max': indicators['max'],
            'croplands_stddev': indicators['stdDev']
        }
        return ee.Feature(None, props)
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
        return ee.Feature(None, props)


print("6 - processing features")

global count
count = 0
for n in chunks:
    count = count + 1
    processFeature.processFeature(n, count, calculatesIndicator)

end = datetime.now()
length = end - start

print("7 - processing complete in " + str(length))