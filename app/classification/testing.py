import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')

import geemap
import ee
ee.Initialize()

import imagery
import sampleRegions
import imageToVectors

bands = ['SR_B2_mean', 'SR_B3_mean', 'SR_B4_mean', 'SR_B5_mean', 'SR_B6_mean', 'SR_B7_mean', 'NDVI', 'NDWI', 'SAVI']
featureCollection = geemap.geojson_to_ee('./data/input/test.geojson')
#asset = ee.data.getAsset('users/andreasrey/TrainingPoints_GMB_Kerewan')
#geojson = geemap.ee_to_geojson(asset)
trainingDataset = ee.FeatureCollection('users/andreasrey/TrainingPoints_GMB_Kerewan')
print("1 - retrieving reference image (2020)")
referenceImage = imagery.get(featureCollection, '2020-01-01', '2020-12-31')
print("2 - sampling regions")
training = sampleRegions.sampleRegions(referenceImage, bands, trainingDataset)
#geemap.ee_export_geojson(training, './data/output/training.geojson')
classifier = ee.Classifier.smileRandomForest(100)
print("3 - train classifier")
trained = classifier.train(training, 'class', bands)

print("4 - retrieving image to be classified")
image = imagery.get(featureCollection, '2021-01-01', '2021-12-31')

print("5 - classify image")
classified = image.select(bands).classify(trained)
croplands_classification = classified.eq(0).selfMask()
print("6 - vectorise classified area")
subCroplands_Classification = imageToVectors.imageToVectors(croplands_classification, featureCollection.first())
print("7 - export results")
print(type(subCroplands_Classification))
geemap.ee_export_geojson(subCroplands_Classification, './data/output/classification.geojson')
print("8 - processing complete")