import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')
import ee 

#*
 # @license
 # Copyright 2019 The Google Earth Engine Community Authors
 #
 # Licensed under the Apache License, Version 2.0 (the "License")
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 #     http:#www.apache.Org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
 #

# ################################################################
# ### FUNCTIONS ###
# ################################################################

# Define coefficients supplied by Roy et al. (2016) for translating ETM+ \
# surface reflectance to OLI surface reflectance.
ee.Initialize()
coefficients = {
  'itcps': ee.Image.constant([0.0003, 0.0088, 0.0061, 0.0412, 0.0254, 0.0172]).multiply(10000),
  'slopes': ee.Image.constant([0.8474, 0.8483, 0.9047, 0.8462, 0.8937, 0.9071])
}

# Define function to get and rename bands of interest from OLI.
def renameOli(img):
  return img.select(
      ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'pixel_qa'],
      ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa'])


# Define function to get and rename bands of interest from ETM+.
def renameEtm(img):
  return img.select(
      ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'pixel_qa'],
      ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2', 'pixel_qa'])


# Define function to apply harmonization transformation.
def etmToOli(img):
  return img.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2']) \
      .multiply(coefficients['slopes']) \
      .add(coefficients['itcps']) \
      .round() \
      .toShort() \
      .addBands(img.select('pixel_qa'))


# Define function to mask out clouds and cloud shadows.
def fmask(img):
  cloudShadowBitMask = 1 << 3
  cloudsBitMask = 1 << 5
  qa = img.select('pixel_qa')
  mask = qa.bitwiseAnd(cloudShadowBitMask) \
                  .eq(0) \
                  .And(qa.bitwiseAnd(cloudsBitMask).eq(0))
  return img.updateMask(mask)


# Define function to calculate NBR.
def calcNbr(img):
  return img.normalizedDifference(['NIR', 'SWIR2']).rename('NBR')


# Define function to prepare OLI images.
def prepOli(img):
  orig = img
  img = renameOli(img)
  img = fmask(img)
  # img = calcNbr(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))


# Define function to prepare ETM+ images.
def prepEtm(img):
  orig = img
  img = renameEtm(img)
  img = fmask(img)
  img = etmToOli(img)
  # img = calcNbr(img)
  return ee.Image(img.copyProperties(orig, orig.propertyNames()))


# ################################################################
# ### APPLICATION ###
# ################################################################


  # Define a point on the north slope of Mount Hood, OR
  # to extract time series for.
  aoi = ee.Geometry.Point([-121.70938, 45.43185])

def getHarmonizedCollection(
  aoi: ee.FeatureCollection,
  startDate: str,
  endDate: str
) -> ee.ImageCollection :

  # Get Landsat surface reflectance collections for OLI, ETM+ and TM sensors.
  oliCol = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
  etmCol = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')
  tmCol = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')


  startDoy = ee.Date(startDate).getRelative('day', 'year')
  endDoy = ee.Date(endDate).getRelative('day', 'year')
  # Define a collection filter.
  colFilter = ee.Filter.And(
      ee.Filter.bounds(aoi), ee.Filter.calendarRange(startDoy, endDoy, 'day_of_year'),
      ee.Filter.lt('CLOUD_COVER', 50), ee.Filter.lt('GEOMETRIC_RMSE_MODEL', 10),
      ee.Filter.Or(
          ee.Filter.eq('IMAGE_QUALITY', 9),
          ee.Filter.eq('IMAGE_QUALITY_OLI', 9)))

  # Filter collections and prepare them for merging.
  oliCol = oliCol.filter(colFilter).map(prepOli)
  etmCol = etmCol.filter(colFilter).map(prepEtm)
  tmCol = tmCol.filter(colFilter).map(prepEtm)

  # Merge the collections.
  col = oliCol.merge(etmCol).merge(tmCol)

  return col

# Calculate median NBR for pixels intersecting the AOI for
# each image in the collection. Add the value as an image property.

# def func_pvi(img):
#     obs = img.reduceRegion(
#         {'geometry': aoi, 'reducer': ee.Reducer.median(), 'scale': 30})
#     return img.set('NBR', obs.get('NBR'))

#   allObs = col.map(func_pvi)






#   # Make a chart of all observations where color distinguishes sensor.
#   chartAllObs =
#       ui.Chart.feature.groups(allObs, 'system:time_start', 'NBR', 'SATELLITE') \
#           .setChartType('ScatterChart') \
#           .setSeriesNames(['TM', 'ETM+', 'OLI']) \
#           .setOptions({
#             'title': 'All Observations',
#             'colors': ['f8766d', '00ba38', '619cff'],
#             'hAxis': '{title': 'Date'},
#             'vAxis': '{title': 'NBR'},
#             'pointSize': 6,
#             'dataOpacity': 0.5
#           })
#   print(chartAllObs)

#   # Reduce the ImageCollection to intra-annual median.
#   # Need to identify same-year images by a join.
#   # Start by adding a 'year' property to each image.

# def func_tly(img):
#     return img.set('year', img.date().get('year'))

#   col = col.map(func_tly)




#   # Subset collection to a set of distinct year representatives.
#   distinctYearCol = col.distinct('year')

#   # Define a filter that identifies images from the complete
#   # collection that match the 'year' from the distinct year collection
#   # (distinctYearCol).
#   filter = ee.Filter.equals({'leftField': 'year', 'rightField': 'year'})

#   # Define a join.
#   join = ee.Join.saveAll('year_matches')

#   # Apply the join and convert the resulting FeatureCollection to an
#   # ImageCollection.
#   joinCol = ee.ImageCollection(join.apply(distinctYearCol, col, filter))

#   # Apply median reduction among matching year collections.

# def func_ykj(img):
#     yearCol = ee.ImageCollection.fromImages(img.get('year_matches'))
#     return yearCol.reduce(ee.Reducer.median()) \
#         .set('system:time_start', img.date().update({month: 8, day: 1}))

#   medianComp = joinCol.map(func_ykj)






#   # Make a chart that displays the annual median NBR composite.
#   chartMedianComp = ui.Chart.image \
#                             .series({
#                               'imageCollection': medianComp,
#                               'region': aoi,
#                               'reducer': ee.Reducer.median(),
#                               'scale': 30,
#                               'xProperty': 'system:time_start',
#                             }) \
#                             .setSeriesNames(['NBR Median']) \
#                             .setOptions({
#                               'title': 'Intra-annual Median',
#                               'colors': ['619cff'],
#                               'hAxis': '{title': 'Date'},
#                               'vAxis': '{title': 'NBR'},
#                               'lineWidth': 6
#                             })
#   print(chartMedianComp)

  # ################################################################
  # ### ALTERNATIVE TRANSFORMATION FUNCTIONS ###
  # ################################################################

  # Roy et al. (2016) Table 2 provides OLS and RMA regression coefficients
  # to transform ETM+ surface reflectance to OLI surface reflectance and vice
  # versa. The above tutorial demonstrates only ETM+ to OLI transformation by OLS
  # regression. Below are functions for all transformation options. Modify the
  # above `prepOli` and `prepEtm` wrapper functions as needed to
  # add/remove/replace transformation functions. Additionally, use the below
  # `coefficients` dictionary instead of the one defined above (the following one
  # includes all sets of coefficients).

  # # Define OLS and RMA surface regression coefficients['
  # coefficients = {
  #   'etmToOliOls': {
  #     'itcps': ee.Image.constant([0.0003, 0.0088, 0.0061, 0.0412, 0.0254, 0.0172]) \
  #                .multiply(10000),
  #     'slopes': ee.Image.constant([0.8474, 0.8483, 0.9047, 0.8462, 0.8937, 0.9071])
  #   },
  #   'oliToEtmOls': {
  #     'itcps': ee.Image.constant([0.0183, 0.0123, 0.0123, 0.0448, 0.0306, 0.0116]) \
  #                .multiply(10000),
  #     'slopes': ee.Image.constant([0.885, 0.9317, 0.9372, 0.8339, 0.8639, 0.9165])
  #   },
  #   'rma': {
  #     'itcps':
  #         ee.Image.constant([-0.0095, -0.0016, -0.0022, -0.0021, -0.0030, 0.0029]) \
  #             .multiply(10000),
  #     'slopes': ee.Image.constant([0.9785, 0.9542, 0.9825, 1.0073, 1.0171, 0.9949])
  #   }
  # }

  # # Define function to apply OLS ETM+ to OLI transformation.
  # def etmToOliOls(img):
  #   return img.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2']) \
  #       .multiply(coefficients['etmToOliOls.slopes) \
  #       .add(coefficients['etmToOliOls.itcps) \
  #       .round() \
  #       .toShort() \
  #       .addBands(img.select('pixel_qa'))


  # # Define function to apply OLS OLI to ETM+ transformation.
  # def oliToEtmOls(img):
  #   return ee.Image(img.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2']) \
  #                       .multiply(coefficients['oliToEtmOls.slopes) \
  #                       .add(coefficients['oliToEtmOls.itcps) \
  #                       .round() \
  #                       .toShort() \
  #                       .addBands(img.select('pixel_qa')) \
  #                       .copyProperties(img, ['system:time_start']))


  # # Define function to apply RMA OLI to ETM+ transformation.
  # def oliToEtmRma(img):
  #   return ee.Image(img.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2']) \
  #                       .subtract(coefficients['rma.itcps) \
  #                       .divide(coefficients['rma.slopes) \
  #                       .round() \
  #                       .toShort() \
  #                       .addBands(img.select('pixel_qa')) \
  #                       .copyProperties(img, ['system:time_start']))


  # # Define function to apply RMA ETM+ to OLI transformation.
  # def etmToOliRma(img):
  #   return ee.Image(img.select(['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2']) \
  #                       .multiply(coefficients['rma.slopes) \
  #                       .add(coefficients['rma.itcps) \
  #                       .round() \
  #                       .toShort() \
  #                       .addBands(img.select('pixel_qa')) \
  #                       .copyProperties(img, ['system:time_start']))


