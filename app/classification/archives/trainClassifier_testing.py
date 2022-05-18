import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')
import ee
ee.Initialize()
import geemap
import imagery

import trainClassifier

bands = ['SR_B2_mean', 'SR_B3_mean', 'SR_B4_mean', 'SR_B5_mean', 'SR_B6_mean', 'SR_B7_mean', 'NDVI', 'NDWI', 'SAVI']
aoi = geemap.geojson_to_ee('./data/input/test.geojson')
trainingDataset = ee.FeatureCollection('users/andreasrey/TrainingPoints_GMB_Kerewan')

referenceImage = imagery.get(aoi, '2020-01-01', '2020-12-31')

classifier = trainClassifier.trainClassifier(referenceImage, bands, trainingDataset)
#geemap.ee_export_geojson(classifier, './data/temp/trained.geojson')
geemap.ee_export_geojson(classifier, './data/temp/trained.geojson')