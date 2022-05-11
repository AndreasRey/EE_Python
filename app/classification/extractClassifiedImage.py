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

print ('EE Data extraction - starting')
time_start = datetime.now()

# chunks = chunkFeatureSource.chunkFeatureSource('./data/input/grid_test_4326.geojson')
# chunks = chunkFeatureSource.chunkFeatureSource2('./data/input/GMB/GMB_intersection.geojson')

bands = ['SR_B2_mean', 'SR_B3_mean', 'SR_B4_mean', 'SR_B5_mean', 'SR_B6_mean', 'SR_B7_mean', 'NDVI', 'NDWI', 'SAVI']
# aoi = geemap.geojson_to_ee('./data/input/NER_chunks_admin01.geojson')
extent = geemap.geojson_to_ee('./data/input/GMB/GMB_extent.geojson')
aoi = geemap.geojson_to_ee('./data/input/GMB/GMB_intersection8.geojson')
nameProp = 'uid'
trainingDataset = geemap.geojson_to_ee('./data/input/GMB/GMB_samplePoints.geojson')
referenceImage = imagery.get(extent, '2020-01-01', '2020-12-31')
trained = trainClassifier.trainClassifier(referenceImage, bands, trainingDataset)

image = imagery.get(extent, '2021-01-01', '2021-12-31')
classified = image.select(bands).classify(trained)
croplands_classification = classified.eq(0).selfMask()
table = geemap.geojson_to_ee('./data/input/GMB/GMB_intersection8.geojson')
count = 0
values = []
time_init = datetime.now()
duration_init = time_init - time_start
print ('Script initialized in ' + str(duration_init))

time_loop_start = datetime.now()
with open('./data/input/GMB/GMB_intersection8.geojson', 'r') as file:
    data = json.load(file)
    length = len(data['features'])
    print('##### Processing ' + str(length) + ' features')
    for x in data['features']:
        time_feature_start = datetime.now()
        # Get the current feature ID to filter out the featureCollection 
        uid = str(x['properties']['uid'])
        filtered = table.filter("uid == " + uid)

        subName = x['properties']['adm1_name']
        count = count + 1
        print('##### ' + str(count) + '/' + str(length) + ' - feature id: ' + str(uid) + ' (' + subName + ')')

        time_image_start = datetime.now()
        # Export the classified image clipped with the featureCollection geometry
        singleImage = croplands_classification.clip(filtered.geometry())
        # geemap.ee_export_image(singleImage, './data/output/GMB_images/' + str(uid) + '.tif', 30)
        time_image_end = datetime.now()
        duration_image = time_image_end - time_image_start
        print('##### feature id: ' + str(uid) + ' (' + subName + ')' + ' Image processed successfully in ' + str(duration_image))

        # Export the croplands geometry and the calculated values
        time_vector_start = datetime.now()
        subCroplands_Classification = imageToVectors.imageToVectors(singleImage, filtered.first())
        
        props = {
          'id': uid,
          'period': '2021',
          'subregion': subName
        }
        time_values_start = datetime.now()
        if subCroplands_Classification.size().getInfo() > 0:
          # geemap.ee_export_geojson(subCroplands_Classification, './data/output/GMB_vectors/' + str(uid) + '.geojson')
          time_vector_end = datetime.now()
          duration_vector = time_vector_end - time_vector_start
          print('##### feature id: ' + str(uid) + ' (' + subName + ')' + ' Vectors processed successfully in ' + str(duration_vector))

          time_values_start = datetime.now()
          geom = subCroplands_Classification.geometry()
          area_Classification_sqM = geemap.ee_num_round(geom.area(1), 0)
          imageForValues = image.select(['NDVI']).clip(geom)
          indicators = getPolygonData.getPolygonData(imageForValues, 'NDVI', geom, 4)
          props['area_sqm'] = area_Classification_sqM.getInfo()
          props['croplands_min'] = indicators['min'].getInfo()
          props['croplands_mean'] = indicators['mean'].getInfo()
          props['croplands_max'] = indicators['max'].getInfo()
          props['croplands_stddev'] = indicators['stdDev'].getInfo()
        else:
          time_values_start = datetime.now()
          props['area_sqm'] = 0
          props['croplands_min'] = -999
          props['croplands_mean'] = -999
          props['croplands_max'] = -999
          props['croplands_stddev'] = -999
  
        time_values_end = datetime.now()
        duration_values = time_values_end - time_values_start

        props['duration_image'] = str(duration_image)
        props['duration_vector'] = str(duration_vector)
        props['duration_values'] = str(duration_values)
        props['duration_values'] = str(duration_values)

        time_feature_end = datetime.now()
        duration_feature = time_feature_end - time_feature_start

        props['duration_total'] = str(duration_feature)
        
        print('##### feature id: ' + str(uid) + ' (' + subName + ')' + ' Values retrieved successfully in ' + str(duration_values))
        # print('##### feature id: ' + str(uid) + ' (' + subName + ')' + ' props:')
        # print(props)

        print('##### feature id: ' + str(uid) + ' (' + subName + ')' + ' done in ' + str(duration_feature))
        values.append(props)
        # single_valueFile = open('./data/output/GMB_values/' + str(uid) + '.json', 'w')
        with open('./data/output/GMB_values/' + str(uid) + '.json', 'w') as single_valueFile:
          json.dump(props, single_valueFile)
        # single_valueFile.close()

    # all_valuesFile = open('./data/output/GMB_values/' + 'VALUES' + '.json', 'w')
    with open('./data/output/GMB_values/' + 'VALUES' + '.json', 'w') as all_valuesFile:
      json.dump(values, all_valuesFile)

    time_loop_end = datetime.now()
    duration_loop = time_loop_end - time_loop_start
    print('##### Processed ' + str(length) + ' features in ' + str(duration_loop))
  

time_end = datetime.now()
duration_all = time_end - time_start
print('##### Extraction completed in ' + str(duration_all))