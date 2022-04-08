import numpy
import ee
import geemap

meanReducer = ee.Reducer.mean()
minimumReducer = ee.Reducer.min()
maximumReducer = ee.Reducer.max()
stdDevReducer = ee.Reducer.stdDev()

def getPolygonData(
    image: ee.Image,
    band: str,
    feature: ee.Feature,
    round: int = 3
) -> object:
    geom = feature.geometry()

    reduceMean = image.reduceRegion(
        meanReducer,
        geom,
        100,
        None,
        None,
        True
    )
    mean = ee.Number(reduceMean.get(band))
    Mean = ee.Number(ee.Algorithms.If(mean,mean,-999))
    returnedMean = geemap.ee_num_round(Mean, round)

    reduceMin = image.reduceRegion(
        minimumReducer,
        geom,
        100,
        None,
        None,
        True
    )
    min = ee.Number(reduceMin.get(band))
    Min = ee.Number(ee.Algorithms.If(min,min,-999))
    returnedMin = geemap.ee_num_round(Min, round)

    reduceMax = image.reduceRegion(
        maximumReducer,
        geom,
        100,
        None,
        None,
        True
    )
    max = ee.Number(reduceMax.get(band))
    Max = ee.Number(ee.Algorithms.If(max,max,-999))
    returnedMax = geemap.ee_num_round(Max, round)

    reduceStdDev = image.reduceRegion(
        stdDevReducer,
        geom,
        100,
        None,
        None,
        True
    )
    stdDev = ee.Number(reduceStdDev.get(band))
    StdDev = ee.Number(ee.Algorithms.If(stdDev,stdDev,-999))
    returnedStdDev = geemap.ee_num_round(StdDev, round)

    toReturn = { 'mean': returnedMean.toFloat(), 'min': returnedMin.toFloat(), 'max': returnedMax.toFloat(), 'stdDev': returnedStdDev.toFloat() }
    return toReturn