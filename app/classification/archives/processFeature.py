import geemap
import ee

def geojsonCollection(
    features
):
    geojson = {
        "type": "FeatureCollection",
        "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
        "features": features
    }
    return geojson

def processFeature(
    features,
    suffix,
    function
):
    output = ee.FeatureCollection(geojsonCollection(features)).map(function)
    geemap.ee_export_geojson(output, './data/output/NER_geom_' +  str(suffix) + '.geojson')
    print("processed " + str(suffix) + " chunk")

def processFeature2(
    features
):
    output = ee.FeatureCollection(geojsonCollection(features))
    return output