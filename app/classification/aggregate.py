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

path = './eval/output/TEST_2_harmonized_2021/VALUES.csv'
joinAttribute = "subregion"
outputFolder = './eval/output/'

df = pd.read_csv(path)
unique = pd.unique(df[joinAttribute])

values = []

for x in unique:
    filtered = df[df[joinAttribute] == x]
    refRow = filtered.loc[1].to_dict()
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
    # props['croplands_ndvi_mean'] = np.average(a = filtered['croplands_ndvi_mean'], weights = filtered['area_sqm'])
    props['croplands_ndvi_mean'] = float(wc.Calculator('area_sqm').mean(filtered, 'croplands_ndvi_mean'))
    props['croplands_ndvi_median'] = float(wc.Calculator('area_sqm').median(filtered, 'croplands_ndvi_median'))
    props['croplands_ndvi_max'] = float(filtered['croplands_ndvi_max'].max())
    props['croplands_ndvi_stddev'] = float(wc.Calculator('area_sqm').std(filtered, 'croplands_ndvi_stddev'))

    values.append(props)

with open(outputFolder + 'aggregate' + '.json', 'w') as all_valuesFile:
    json.dump(values, all_valuesFile)
    all_valuesFile.close()

fromJsonToCsv.fromJsonToCsv(outputFolder + 'aggregate' + '.json', outputFolder + 'aggregate' + '.csv')