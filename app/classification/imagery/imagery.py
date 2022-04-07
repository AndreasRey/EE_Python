import ee

import LANDSAT_LC08_C02_T1_L2

def get(
    aoi: ee.FeatureCollection,
    startDate: str, # YYYY-MM-DD format
    endDate: str # YYYY-MM-DD format
) -> ee.Image :
    return LANDSAT_LC08_C02_T1_L2.ref(aoi, startDate, endDate)
