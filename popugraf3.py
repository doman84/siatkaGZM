from qgis.core import *
import qgis.utils

def totlength(layer):
    a = 0
    
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
line = registry.mapLayersByName('KSS1')
line = line[0]
#density map
density = registry.mapLayersByName('GZM_density_BREC')
density = density[0]
#parameters
distance = 1000 #buffer distance (in meters)
step = 100 #segments size in meters
span = 1500 #max value on popugraf
scale = 20000 #people per span m (needed for offset visualization)

#counting whole population in buffer
processing.run("native:buffer", {'INPUT': line, 'DISTANCE': distance, 'SEGMENTS': 99, 'OUTPUT': 'C:/temp/buffer.shp'})
processing.run("native:intersection", {'INPUT': 'C:/temp/buffer.shp', 'OVERLAY': density, 'OUTPUT': 'C:/temp/rbuffer.shp'})
bufor = iface.addVectorLayer('C:/temp/rbuffer.shp', "bufor", "ogr")

totpop = 0
for feature in bufor.getFeatures():
    totpop = feature["TOTAL_POP"] + totpop
print(totpop)
QgsProject.instance().removeMapLayers([bufor.id()])

#making popugraf
pattern(totlen,step)
processing.run("grass7:v.segment", {"input": line, "output": "C:/temp/rule.shp", "rules": "C:/temp/rule.txt",
"GRASS_REGION_PARAMETER": extent, "GRASS_SNAP_TOLERANCE_PARAMETER": -1, "GRASS_MIN_AREA_PARAMETER": 0, "GRASS_OUTPUT_TYPE_PARAMETER": 1})
processing.run("native:buffer", {'INPUT': "C:/temp/rule.shp", 'DISTANCE': distance, 'SEGMENTS': 99, 'OUTPUT': 'C:/temp/buffer.shp'})
processing.run("native:intersection", {'INPUT': 'C:/temp/buffer.shp', 'OVERLAY': density, 'OUTPUT': 'C:/temp/rbuffer.shp'})
bufor = iface.addVectorLayer('C:/temp/rbuffer.shp', "bufor", "ogr")

n = int(totlen/step)
population = n*[0]
for feature in bufor.getFeatures():
    area = feature.geometry().area()
    div = feature["TOTAL_POP"]*area/feature["area"] #for BREC 
    cat = feature["cat"]
    population[cat]=population[cat]+int(div)

QgsProject.instance().removeMapLayers([bufor.id()])

population = [span*item/scale for item in population]
segments(population,step)
processing.run("grass7:v.segment", {"input": line, "output": "C:/temp/segments.shp", "rules": "C:/temp/segments.txt",
"GRASS_REGION_PARAMETER": extent, "GRASS_SNAP_TOLERANCE_PARAMETER": -1, "GRASS_MIN_AREA_PARAMETER": 0, "GRASS_OUTPUT_TYPE_PARAMETER": 1})