import ee

import calculateExtraBands

dataset = "LANDSAT/LC08/C02/T1_L2"
NIR = "SR_B5_mean"
Red = "SR_B4_mean"
SWIR = "SR_B6_mean"

def provideDataset(
    aoi: ee.FeatureCollection,
    startDate: str, # YYYY-MM-DD format
    endDate: str # YYYY-MM-DD format
) -> ee.ImageCollection:
    return ee.ImageCollection(dataset).filterDate(startDate, endDate).filterBounds(aoi.geometry().bounds()).map(bandsScaleFactor)

def bandsScaleFactor(
    image: ee.Image
) -> ee.Image:
    opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True)

def ref(
    aoi: ee.FeatureCollection,
    startDate: str, # YYYY-MM-DD format
    endDate: str # YYYY-MM-DD format
) -> ee.Image:
    imageCollection = provideDataset(aoi, startDate, endDate)
    image = imageCollection.reduce('mean').clip(aoi)
    return calculateExtraBands.calculateExtraBands(image, NIR, Red, SWIR)