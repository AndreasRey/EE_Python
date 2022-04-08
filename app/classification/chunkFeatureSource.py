# import sys
# sys.path.append('./imagery/')
# sys.path.append('./utils/')

import json
import numpy
import geemap
import ee

def chunkFeatureSource(
    pathToFile: str
) -> list:
    file = open(pathToFile)
    j = json.load(file)
    numberOfChunks = numpy.ceil(len(j['features']) / 100)
    chunks = numpy.array_split(j['features'], numberOfChunks)
    print("Source contains " + str(len(j['features'])) + " feature(s), splitted into " + str(len(chunks)) + " chunk(s).")
    return chunks