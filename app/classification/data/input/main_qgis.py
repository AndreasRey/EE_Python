import ee 

imageToVectors = require('users/andreasrey/CroplandClassification:ImageToVectors')
sampleRegions = require('users/andreasrey/CroplandClassification:TrainingSampleRegions')
Utils = require('users/andreasrey/CroplandsClassificationProcessings:Utils')

imageryProvider = require('users/andreasrey/CroplandsClassificationProcessings:Imagery')
bands = imageryProvider.bands()
def getImagery(aoi, startDate, endDate):
  imagery = imageryProvider.image(aoi, startDate, endDate)
  return [
    { 'image': imagery.image, 'first': imagery.first, 'scales': [30] }
  ]




#*
 # -- run
 # prefixFileName : [String] First part of the export tasks names
 # suffixFileName : [String] Last part of the export tasks names
 #  - name : [String] label of the imagery row
 #  - startDate : [String] Date as string under the YYYY-MM-DD format
 #  - endDate : [String] Date as string under the YYYY-MM-DD format
 #  - image : [ee.Image]
 #  - bands : [Array] List of strings designating bands in the Image
 #  - scales : [Array] List of integers mentionning the different scales to be considered
 # classifiers : [Array] Collection of the following :
 #  - name : [String] label of the classifier
 #  - classifier : [ee.Classifier]
 # regions : [Array] Collection of the following :
 #  - full : [ee.FeatureCollection] Full zone (should contain only one feature) for the classification
 #  - subs : [ee.FeatureCollection] Sub zones, included inside the full zone, the subs are used for NDVI calculations
 #  - subName : [String] Property of subs that contains the individual identifiers of its features
 # periods : [Array] Collection of the following :
 #  - start : [String] Date as string under the YYYY-MM-DD format
 #  - end : [String] Date as string under the YYYY-MM-DD format
 #  - label : [String] Title of the period
 # trainingDataset : [ee.FeatureCollection] Training data for the classifiers (included features should have a property "class" - the "0" value identifies crops)
 #
def exports.run (prefixFileName, suffixFileName, classifiers, regions, periods, trainingDataset):

#  dictionaries = ee.FeatureCollection([])
#  geometries = ee.FeatureCollection([])

    referencePeriod = { 'start': '2020-05-01', 'end': '2020-10-01'}
    referenceImage = getImagery(regions[0].full, referencePeriod.start, referencePeriod.end)[0]

        # TODO : Do something different with the scales
        scales = referenceImage.scales

    training = sampleRegions(referenceImage.image, bands, trainingDataset, scales[0])


def func_xuj (region):
    aoi = region.full
#    LayerUtils.AddUnfilledPolygonLayer(aoi, '000000', 'AoI')
    subRegions = region.subs
#    croplands_ESA = SourceCrops.crops_ESA_WorldCover_v100(aoi)
#    Map.addLayer(croplands_ESA, {palette: 'green', opacity: 0.5}, 'ESA')



        return ee.FeatureCollection(scales.map(function (scale) {

#          random = trainingDataset.randomColumn('rand')
#          trainingPolygons = random.filter(ee.Filter.lt('rand', 0.7))
#          validationPolygons = random.filter(ee.Filter.gte('rand', 0.7))
#          training = sampleRegions(image, bands, trainingPolygons, scale)


#          validation = sampleRegions(image, bands, validationPolygons, scale)

          return ee.FeatureCollection(classifiers.map(function (classifier) {

#            classifierName = classifier.name
#            classifierID = imageName + '_' + scale + '_' + classifierName + '_' + periodLabel





            trained = classifier.train(training, 'class', bands)



    return ee.FeatureCollection(periods.map(function (period) {

      imagery = getImagery(aoi, period.start, period.end)
      periodLabel = period.label


      return ee.FeatureCollection(imagery.map(function (imageryData) {
               image = imageryData.image
       classified = image.select(bands).classify(trained)

#        imageName = imageryData.name
#        bands = imageryData.bands
#        bandsID = ee.String.encodeJSON(bands)

#            validated = validation.classify(trained)

#            train_confusionMatrix = trained.confusionMatrix()
#            validate_confusionMatrix = validated.errorMatrix('class', 'classification')
#            train_accuracy = train_confusionMatrix.accuracy()
#            validate_accuracy = validate_confusionMatrix.accuracy()
#            explained = trained.explain()
#            importance = explained.get('importance')
#            dictionary = ee.FeatureCollection([
#              ee.Feature(None, {
#                'classifiername': classifierName,
#                'classifierid': classifierID,
#                'bandsid': bandsID,
#                'bands': bands,
 #               'train_accuracy': train_accuracy,
#                'train_confusionmatrix': train_confusionMatrix,
#                'validate_accuracy': validate_accuracy,
#                'validate_confusionmatrix': validate_confusionMatrix,
#                'importance': importance
#              })
#            ])
#            dictionaries = dictionaries.merge(dictionary)
            croplands_classification = classified.eq(0).selfMask()
#            layerName = classifierID
#            Map.addLayer(croplands_classification, { palette: 'red' }, layerName, False)

            return ee.FeatureCollection(subRegions.map(function (feature) {

              subName = feature.get(region.subName)
#              analysisID = classifierID + '_' + subName

#              subCroplands_ESA = imageToVectors(croplands_ESA, feature, 10)
              subCroplands_Classification = imageToVectors(croplands_classification, feature, scale)


#              Area_ESA = Scripts.roundNum(ee.Number(subCroplands_ESA.vectors.geometry().area(1)).divide(1000000), 1)
              Area_Classification_sqKm = Utils.roundNum(ee.Number(subCroplands_Classification.vectors.geometry().area(1)).divide(1000000), 2)
              Area_Classification_sqM = Utils.roundNum(ee.Number(subCroplands_Classification.vectors.geometry().area(1)), 0)

              NDVI_Classification = Utils.getPolygonData(image, 'NDVI', subCroplands_Classification.vectors, 4)

              return ee.Feature(None, {
                'period': periodLabel,
                'subregion': subName,
                'area_sqkm': Area_Classification_sqKm,
                'area_sqm': Area_Classification_sqM,
                'min': NDVI_Classification.min,
                'mean': NDVI_Classification.mean,
                'max': NDVI_Classification.max,
                'stddev': NDVI_Classification.stdDev
              })
            }))
          })).flatten()
        })).flatten()
      })).flatten()
    })).flatten()

  output = ee.FeatureCollection(regions.map(func_xuj
)).flatten()





































































































)).flatten()



  # Export output as CSV
  Export.table.toDrive({
    'collection': output,
    'description': prefixFileName + '_' + 'CSV' + '_' + suffixFileName,
    'fileFormat':"CSV",
    'folder': "EE_Exports",
    'selectors':'period,subregion,area_sqkm,area_sqm,min,mean,max,stddev',
  })
  #*
  #
  #*
  # Export output with croplands geometries as GeoJSON
  Export.table.toDrive({
    'collection': output,
    'description': prefixFileName + '_' + 'GeoJSON' + '_' + suffixFileName,
    'fileFormat':"GeoJSON",
    'folder': "EE_Exports",
    'selectors':'image,scale,classifier,period,startdate,enddate,subregion,area_esa,common_area,area_classification,percent_of_esa,train_accuracy,validate_accuracy,min_esa,min_classification,mean_esa,mean_classification,max_esa,max_classification,stddev_esa,stddev_classification,classifierid,bandsid,intersection,diff,diff_esa',
  })

  #
  #*
  # Export dictionaries as GeoJSON
  Export.table.toDrive({
    'collection': dictionaries,
    'description': prefixFileName + '_dictionaries_geoJSON' + '_' + suffixFileName,
    'fileFormat':"GeoJSON",
    'folder': "EE_Exports",
    'selectors':'classifiername,classifierid,bandsid,bands,train_accuracy,validate_accuracy,train_confusionmatrix,validate_confusionmatrix,importance'
  })

  #

#*
def exports.exportESA (prefixFileName, suffixFileName, regions):
  croplands_ESA = SourceCrops.crops_ESA_WorldCover_v100(regions[0].full)
  subRegions = regions[0].subs

def func_uqz (feature):
    subCroplands_ESA = imageToVectors(croplands_ESA, feature, 10)
    return ee.Feature(None, {
      'name': 'ESA',
      'geom': subCroplands_ESA.geom
    })

  esa = ee.FeatureCollection(subRegions.map(func_uqz
))





))
  Export.table.toDrive({
    'collection': esa,
    'description': prefixFileName + '_' + 'ESA_export' + '_' + 'GeoJSON' + '_' + suffixFileName,
    'fileFormat':"GeoJSON",
    'folder': "EE_Exports",
    'selectors':'name,geom',
  })

#
#*
def exports.exportAoI (prefixFileName, suffixFileName, regions):
  subRegions = regions[0].subs

def func_ewl (feature):
    subName = feature.get(regions[0].subName)
    return ee.Feature(None, {
      'name': subName,
      'geom': feature.geometry()
    })

  aoi = ee.FeatureCollection(subRegions.map(func_ewl
))





))
  Export.table.toDrive({
    'collection': aoi,
    'description': prefixFileName + '_' + 'AoI_export' + '_' + 'GeoJSON' + '_' + suffixFileName,
    'fileFormat':"GeoJSON",
    'folder': "EE_Exports",
    'selectors':'name,geom',
  })

#
