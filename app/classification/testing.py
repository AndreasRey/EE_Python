import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')

import geemap
import ee
ee.Initialize()

import imagery
import sampleRegions

bands = ['SR_B2_mean', 'SR_B3_mean', 'SR_B4_mean', 'SR_B5_mean', 'SR_B6_mean', 'SR_B7_mean', 'NDVI', 'NDWI', 'SAVI']
featureCollection = geemap.geojson_to_ee('./data/input/test.geojson')
#asset = ee.data.getAsset('users/andreasrey/TrainingPoints_GMB_Kerewan')
#geojson = geemap.ee_to_geojson(asset)
trainingDataset = ee.FeatureCollection('users/andreasrey/TrainingPoints_GMB_Kerewan')
image = imagery.get(featureCollection, '2020-01-01', '2020-12-31')
print(type(trainingDataset))
training = sampleRegions.sampleRegions(image, bands, trainingDataset)
geemap.ee_export_geojson(training, './data/output/training.geojson')