from qgis.core import *
import qgis.utils
import time

def totlength(layer):
    a = 0
    for feature in layer.getFeatures():
        a = a+int(feature.geometry().length())
    return a
    
def pattern(len,step):
    n = int(len/step)
    patt = []
    for i in range(n):
        patt.append("P "+str(i)+" 1 "+str(i*step))
    file = open("C:/temp/rule.txt", "w")
    for item in patt:
        print(item, file=file)
    
def segments(distance,step):
    n = len(distance)
    patt = []
    for i in range(n-1):
        patt.append("P "+str(i)+" 1 "+str(i*step)+" "+str(distance[i]))
    for i in reversed(range(n-1)):
        patt.append("P "+str(i)+" 1 "+str(i*step)+" -"+str(distance[i]))
#        patt.append("L "+str(i)+" 1 "+str(i*step)+" "+str((i+1)*step)+" "+str(distance[i]))
#        patt.append("L "+str(i)+" 1 "+str(i*step)+" "+str((i+1)*step)+" -"+str(distance[i]))
    file = open("C:/temp/segments.txt", "w")
    for item in patt:
        print(item, file=file)   

#input line
registry = QgsProject.instance()
line = registry.mapLayersByName('Czajkowski tracks')
line = line[0]
#density map
density = registry.mapLayersByName('GZM_density_BREC')
density = density[0]
#parameters
distance = 1000 #buffer distance (in meters)
step = 100 #segments size in meters

#reproject layer to XY
processing.run("qgis:reprojectlayer", {'INPUT': line, 'TARGET_CRS': 'EPSG:2180', 'OUTPUT': 'C:/Temp/reprojectlayer.shp'})
line = iface.addVectorLayer('C:/Temp/reprojectlayer.shp', "line", "ogr")

#counting whole population in buffer
processing.run("native:buffer", {'INPUT': line, 'DISTANCE': distance, 'SEGMENTS': 99, 'OUTPUT': 'C:/Temp/buffer.shp'})
processing.run("native:intersection", {'INPUT': 'C:/Temp/buffer.shp', 'OVERLAY': density, 'OUTPUT': 'C:/Temp/rbuffer.shp'})
bufor = iface.addVectorLayer('C:/Temp/rbuffer.shp', "bufor", "ogr")

totpop = 0
totpop2 = 0
for feature in bufor.getFeatures():
    area = feature.geometry().area()
    div = feature["TOTAL_POP"]*area/feature["area"] #for BREC 
    totpop=totpop+int(div)
QgsProject.instance().removeMapLayers([bufor.id()])

#counting length of line
totlen = totlength(line)
print("TOTAL POPULATION: " + str(totpop))
print("TOTAL LENGTH: " + str(totlen/1000) + " km")
print("TOTAL POPULATION PER KM: " + str(int(1000*totpop/totlen)))

#making popugraf
pattern(totlen,step)
processing.run("grass7:v.segment", {"input": line, "output": "C:/Temp/rule.shp", "rules": "C:/Temp/rule.txt", "GRASS_REGION_PARAMETER": density, "GRASS_SNAP_TOLERANCE_PARAMETER": -1, "GRASS_MIN_AREA_PARAMETER": 0, "GRASS_OUTPUT_TYPE_PARAMETER": 1})
time.sleep(3)
processing.run("native:buffer", {'INPUT': "C:/Temp/rule.shp", 'DISTANCE': distance, 'SEGMENTS': 99, 'OUTPUT': 'C:/Temp/abuffer.shp'})
time.sleep(3)
processing.run("native:intersection", {'INPUT': 'C:/Temp/abuffer.shp', 'OVERLAY': density, 'OUTPUT': 'C:/Temp/arbuffer.shp'})
bufor = iface.addVectorLayer('C:/Temp/arbuffer.shp', "bufor", "ogr")
QgsProject.instance().removeMapLayers([line.id()])

n = int(totlen/step)
population = n*[0]
for feature in bufor.getFeatures():
    area = feature.geometry().area()
    div = feature["TOTAL_POP"]*area/feature["area"] #for BREC 
    cat = feature["cat"]
    population[cat]=population[cat]+int(div)

QgsProject.instance().removeMapLayers([bufor.id()])

#assigning values to segments
segment = iface.addVectorLayer('C:/Temp/rule.shp', "segment", "ogr")
segment.startEditing()
segment.dataProvider().addAttributes([QgsField("population", QVariant.Int)])
segment.commitChanges()
i=0
segment.startEditing()
for feature in segment.getFeatures():
    feature["population"] = population[i]
    i = i+1
    segment.updateFeature(feature)
segment.commitChanges()
    
#segments(population,step)
#processing.runAndLoadResults("grass7:v.segment", {"input": line, "output": "C:/temp/segments.shp", "rules": "C:/temp/segments.txt", "GRASS_REGION_PARAMETER": density, "GRASS_SNAP_TOLERANCE_PARAMETER": -1, "GRASS_MIN_AREA_PARAMETER": 0, "GRASS_OUTPUT_TYPE_PARAMETER": 1})