import sys
sys.path.append('./imagery/')
sys.path.append('./utils/')
import os.path
import json

import main

def run (
  bands: list,
  aoi: str,
  subNameField: str,
  extent: str,
  outputFolder: str,
  trainingDataset: str,
  classificationImage_year: str,
  outputMode: int,
  classificationImage_startDate: str,
  classificationImage_endDate: str,
  nameProp: str,
  referenceImage_startDate: str,
  referenceImage_endDate: str,
  outputFolder_images: str,
  outputFolder_vectors: str
):

  file_exists = os.path.exists(outputFolder + 'batch.json')
  print(file_exists)
  if (file_exists == False):
    ref = {}
    ref['nextFeatureIndex'] = 0
    ref['attempts'] = 0
    ref['errors'] = []
    with open(outputFolder + 'batch.json', 'w') as batchRefFile:
      json.dump(ref, batchRefFile)
      batchRefFile.close()
      print(outputFolder + 'batch.json created')
      main.main(
          bands,
          aoi,
          subNameField,
          extent,
          outputFolder,
          outputMode,
          trainingDataset,
          classificationImage_year + '-' + classificationImage_startDate,
          classificationImage_year + '-' + classificationImage_endDate,
          nameProp,
          referenceImage_startDate,
          referenceImage_endDate,
          outputFolder_images,
          outputFolder_vectors
    )
  else:
    print('ref file already Exists')
    main.main(
      bands,
      aoi,
      subNameField,
      extent,
      outputFolder,
      outputMode,
      trainingDataset,
      classificationImage_year + '-' + classificationImage_startDate,
      classificationImage_year + '-' + classificationImage_endDate,
      nameProp,
      referenceImage_startDate,
      referenceImage_endDate,
      outputFolder_images,
      outputFolder_vectors
    )