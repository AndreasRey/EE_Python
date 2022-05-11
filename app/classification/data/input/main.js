var imageToVectors = require('users/andreasrey/CroplandClassification:ImageToVectors');
var sampleRegions = require('users/andreasrey/CroplandClassification:TrainingSampleRegions');
var Utils = require('users/andreasrey/CroplandsClassificationProcessings:Utils');

var imageryProvider = require('users/andreasrey/CroplandsClassificationProcessings:Imagery');
var bands = imageryProvider.bands()
function getImagery(aoi, startDate, endDate) {
  var imagery = imageryProvider.image(aoi, startDate, endDate)
  return [
    { image: imagery.image, first: imagery.first, scales: [30] }
  ]
}



/**
 * -- run
 * prefixFileName : [String] First part of the export tasks names
 * suffixFileName : [String] Last part of the export tasks names
 *  - name : [String] label of the imagery row
 *  - startDate : [String] Date as string under the YYYY-MM-DD format
 *  - endDate : [String] Date as string under the YYYY-MM-DD format
 *  - image : [ee.Image]
 *  - bands : [Array] List of strings designating bands in the Image
 *  - scales : [Array] List of integers mentionning the different scales to be considered
 * classifiers : [Array] Collection of the following :
 *  - name : [String] label of the classifier
 *  - classifier : [ee.Classifier]
 * regions : [Array] Collection of the following :
 *  - full : [ee.FeatureCollection] Full zone (should contain only one feature) for the classification
 *  - subs : [ee.FeatureCollection] Sub zones, included inside the full zone, the subs are used for NDVI calculations
 *  - subName : [String] Property of subs that contains the individual identifiers of its features
 * periods : [Array] Collection of the following :
 *  - start : [String] Date as string under the YYYY-MM-DD format
 *  - end : [String] Date as string under the YYYY-MM-DD format
 *  - label : [String] Title of the period
 * trainingDataset : [ee.FeatureCollection] Training data for the classifiers (included features should have a property "class" - the "0" value identifies crops)
 */
exports.run = function (prefixFileName, suffixFileName, classifiers, regions, periods, trainingDataset) {
  
//  var dictionaries = ee.FeatureCollection([]);
//  var geometries = ee.FeatureCollection([]);

    var referencePeriod = { start: '2020-05-01', end: '2020-10-01'}
    var referenceImage = getImagery(regions[0].full, referencePeriod.start, referencePeriod.end)[0];
    
        // TODO : Do something different with the scales
        var scales = referenceImage.scales;
        
    var training = sampleRegions(referenceImage.image, bands, trainingDataset, scales[0]);
  
  var output = ee.FeatureCollection(regions.map(function (region) {
    var aoi = region.full;
//    LayerUtils.AddUnfilledPolygonLayer(aoi, '000000', 'AoI');
    var subRegions = region.subs;
//    var croplands_ESA = SourceCrops.crops_ESA_WorldCover_v100(aoi);
//    Map.addLayer(croplands_ESA, {palette: 'green', opacity: 0.5}, 'ESA');
    

        
        return ee.FeatureCollection(scales.map(function (scale) {
          
//          var random = trainingDataset.randomColumn('rand');
//          var trainingPolygons = random.filter(ee.Filter.lt('rand', 0.7));
//          var validationPolygons = random.filter(ee.Filter.gte('rand', 0.7));
//          var training = sampleRegions(image, bands, trainingPolygons, scale);
          
          
//          var validation = sampleRegions(image, bands, validationPolygons, scale);
          
          return ee.FeatureCollection(classifiers.map(function (classifier) {
            
//            var classifierName = classifier.name;
//            var classifierID = imageName + '_' + scale + '_' + classifierName + '_' + periodLabel;
            
            

            
            
            var trained = classifier.train(training, 'class', bands);
           


    return ee.FeatureCollection(periods.map(function (period) {
      
      var imagery = getImagery(aoi, period.start, period.end);
      var periodLabel = period.label;

      
      return ee.FeatureCollection(imagery.map(function (imageryData) {
               var image = imageryData.image;
       var classified = image.select(bands).classify(trained);
       
//        var imageName = imageryData.name;
//        var bands = imageryData.bands;
//        var bandsID = ee.String.encodeJSON(bands);
        
//            var validated = validation.classify(trained);
  
//            var train_confusionMatrix = trained.confusionMatrix();
//            var validate_confusionMatrix = validated.errorMatrix('class', 'classification');
//            var train_accuracy = train_confusionMatrix.accuracy();
//            var validate_accuracy = validate_confusionMatrix.accuracy();
//            var explained = trained.explain();
//            var importance = explained.get('importance');
//            var dictionary = ee.FeatureCollection([
//              ee.Feature(null, {
//                'classifiername': classifierName,
//                'classifierid': classifierID,
//                'bandsid': bandsID,
//                'bands': bands,
 //               'train_accuracy': train_accuracy,
//                'train_confusionmatrix': train_confusionMatrix,
//                'validate_accuracy': validate_accuracy,
//                'validate_confusionmatrix': validate_confusionMatrix,
//                'importance': importance
//              })
//            ]);
//            dictionaries = dictionaries.merge(dictionary);
            var croplands_classification = classified.eq(0).selfMask();
//            var layerName = classifierID;
//            Map.addLayer(croplands_classification, { palette: 'red' }, layerName, false);
            
            return ee.FeatureCollection(subRegions.map(function (feature) {
              
              var subName = feature.get(region.subName);
//              var analysisID = classifierID + '_' + subName;
              
//              var subCroplands_ESA = imageToVectors(croplands_ESA, feature, 10);
              var subCroplands_Classification = imageToVectors(croplands_classification, feature, scale);
  
  
//              var Area_ESA = Scripts.roundNum(ee.Number(subCroplands_ESA.vectors.geometry().area(1)).divide(1000000), 1);
              var Area_Classification_sqKm = Utils.roundNum(ee.Number(subCroplands_Classification.vectors.geometry().area(1)).divide(1000000), 2);
              var Area_Classification_sqM = Utils.roundNum(ee.Number(subCroplands_Classification.vectors.geometry().area(1)), 0);
              
              var NDVI_Classification = Utils.getPolygonData(image, 'NDVI', subCroplands_Classification.vectors, 4);
              
              return ee.Feature(null, {
                'period': periodLabel,
                'subregion': subName,
                'area_sqkm': Area_Classification_sqKm,
                'area_sqm': Area_Classification_sqM,
                'min': NDVI_Classification.min,
                'mean': NDVI_Classification.mean,
                'max': NDVI_Classification.max,
                'stddev': NDVI_Classification.stdDev
              });
            }));
          })).flatten();
        })).flatten();
      })).flatten();
    })).flatten();
  })).flatten();
  
  

  // Export output as CSV
  Export.table.toDrive({
    collection: output,
    description: prefixFileName + '_' + 'CSV' + '_' + suffixFileName,
    fileFormat:"CSV",
    folder: "EE_Exports",
    selectors:'period,subregion,area_sqkm,area_sqm,min,mean,max,stddev',
  });
  /**
  */
  /**  
  // Export output with croplands geometries as GeoJSON
  Export.table.toDrive({
    collection: output,
    description: prefixFileName + '_' + 'GeoJSON' + '_' + suffixFileName,
    fileFormat:"GeoJSON",
    folder: "EE_Exports",
    selectors:'image,scale,classifier,period,startdate,enddate,subregion,area_esa,common_area,area_classification,percent_of_esa,train_accuracy,validate_accuracy,min_esa,min_classification,mean_esa,mean_classification,max_esa,max_classification,stddev_esa,stddev_classification,classifierid,bandsid,intersection,diff,diff_esa',
  });

  */
  /**  
  // Export dictionaries as GeoJSON
  Export.table.toDrive({
    collection: dictionaries,
    description: prefixFileName + '_dictionaries_geoJSON' + '_' + suffixFileName,
    fileFormat:"GeoJSON",
    folder: "EE_Exports",
    selectors:'classifiername,classifierid,bandsid,bands,train_accuracy,validate_accuracy,train_confusionmatrix,validate_confusionmatrix,importance'
  });

  */
};
/**
exports.exportESA = function (prefixFileName, suffixFileName, regions) {
  var croplands_ESA = SourceCrops.crops_ESA_WorldCover_v100(regions[0].full);
  var subRegions = regions[0].subs;
  var esa = ee.FeatureCollection(subRegions.map(function (feature) {
    var subCroplands_ESA = imageToVectors(croplands_ESA, feature, 10);
    return ee.Feature(null, {
      'name': 'ESA',
      'geom': subCroplands_ESA.geom
    });
  }));
  Export.table.toDrive({
    collection: esa,
    description: prefixFileName + '_' + 'ESA_export' + '_' + 'GeoJSON' + '_' + suffixFileName,
    fileFormat:"GeoJSON",
    folder: "EE_Exports",
    selectors:'name,geom',
  });
};
*/
/**
exports.exportAoI = function (prefixFileName, suffixFileName, regions) {
  var subRegions = regions[0].subs;
  var aoi = ee.FeatureCollection(subRegions.map(function (feature) {
    var subName = feature.get(regions[0].subName);
    return ee.Feature(null, {
      'name': subName,
      'geom': feature.geometry()
    });
  }));
  Export.table.toDrive({
    collection: aoi,
    description: prefixFileName + '_' + 'AoI_export' + '_' + 'GeoJSON' + '_' + suffixFileName,
    fileFormat:"GeoJSON",
    folder: "EE_Exports",
    selectors:'name,geom',
  });
};
*/