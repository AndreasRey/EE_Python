import sys
import qgis
from qgis import processing
# from qgis import *
# from qgis import (
#      QgsApplication, 
#      QgsProcessingFeedback, 
#      QgsVectorLayer
# )
# from qgis import processing
# Initialize QGIS Application
# QgsApplication.setPrefixPath("C:\\OSGeo4W64\\apps\\qgis", True)
# QgsApplication.setPrefixPath("C:\\Program Files\\QGIS 3.4", True)
# app = QgsApplication([], True)
# QgsApplication.initQgis()

QgsApplication.setPrefixPath('~/anaconda3/envs/ee', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# # Add the path to Processing framework
# sys.path.append('c:\\Users\\Ujaval\\.qgis2\\python\\plugins')

# # Import and initialize Processing framework
# from processing.core.Processing import Processing
# Processing.initialize()

# import processing

print('Hello QGIS!')