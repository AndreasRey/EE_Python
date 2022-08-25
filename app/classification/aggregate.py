import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')

import pandas as pd
import json
# import numpy as np
# https://github.com/jsvine/weightedcalcs
import weightedcalcs as wc
import csv
import fromJsonToCsv

year = "2006"
path = './testing/NER_tillaberi_niamey_dosso/output/TESTING_NER_Say_6_GEOM_' + year + '/VALUES.csv'
joinAttribute = "subregion"
outputFolder = './testing/NER_tillaberi_niamey_dosso/aggregation_say_chirps/'

df = pd.read_csv(path)
unique = pd.unique(df[joinAttribute])

values = []

for x in unique:
    filtered = df[(df[joinAttribute] == x) & df['area_sqm'] != 0]
    length = len(filtered)
    if length > 0:
        records = filtered.to_dict('records')
        refRow = records[0]
        props = {
            'period': refRow['period'],
            'subregion': refRow['subregion'],
            'obs': refRow['obs']
        }
        props['area_sqm'] = int(filtered['area_sqm'].sum())
        filteredMin = filtered[filtered['croplands_ndvi_min'] > 0]
        if filteredMin.empty:
            min = -999
        else:
            min = float(filteredMin['croplands_ndvi_min'].min())
        props['croplands_ndvi_min'] = min
        props['croplands_ndvi_mean'] = float(wc.Calculator('area_sqm').mean(filtered, 'croplands_ndvi_mean'))
        props['croplands_ndvi_median'] = float(wc.Calculator('area_sqm').median(filtered, 'croplands_ndvi_median'))
        props['croplands_ndvi_max'] = float(filtered['croplands_ndvi_max'].max())
        props['croplands_ndvi_stddev'] = float(wc.Calculator('area_sqm').std(filtered, 'croplands_ndvi_stddev'))

        filteredMinChirps = filtered[filtered['chirps_precipitations_min'] > 0]
        if filteredMinChirps.empty:
            minChirps = -999
        else:
            minChirps = float(filteredMinChirps['chirps_precipitations_min'].min())
        props['chirps_precipitations_min'] = minChirps
        props['chirps_precipitations_mean'] = float(wc.Calculator('area_sqm').mean(filtered, 'chirps_precipitations_mean'))
        props['chirps_precipitations_median'] = float(wc.Calculator('area_sqm').median(filtered, 'chirps_precipitations_median'))
        props['chirps_precipitations_max'] = float(filtered['chirps_precipitations_max'].max())
        props['chirps_precipitations_stddev'] = float(wc.Calculator('area_sqm').std(filtered, 'chirps_precipitations_stddev'))

        values.append(props)

with open(outputFolder + 'aggregate_' + year + '.json', 'w') as all_valuesFile:
    json.dump(values, all_valuesFile)
    all_valuesFile.close()

fromJsonToCsv.fromJsonToCsv(outputFolder + 'aggregate_' + year + '.json', outputFolder + 'aggregate_' + year + '.csv')