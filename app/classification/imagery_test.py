import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')
import ee 
import imported
import geemap
import imagery
featureCollection = geemap.geojson_to_ee('./data/input/test_square84.geojson')
test = imagery.get(
    featureCollection,
    '2012-01-01',
    '2012-12-31'
)
bands1 = test.bandNames()
print(bands1.getInfo())