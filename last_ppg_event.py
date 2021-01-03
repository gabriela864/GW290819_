import arcpy
from arcpy import env
import pandas as pd
from numpy import array
from math import sqrt, pi, atan, fabs, acos

env.overwriteOutput = 1
env.workspace = "D:\semestr 2\ppg_egz\GW290819_-main"

# funkcja sprawdzajaca dlugosc
def segment_length(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    length = sqrt((dx ** 2) + (dy ** 2))
    return length

# funkcja odpowiedzialna za kat
def azimuth(x1, y1, x2, y2):
    global azymut
    try:
        dx = x2 - x1
        dy = y2 - y1
        fi = (atan((fabs (dx)) / (fabs(dy)))) * 180 / pi
    except ZeroDivisionError:
        fi = 90

    if dx >= 0 and dy > 0:
        azymut = fi
    elif dx < 0 and dy >= 0:
        azymut = 360 - fi
    elif dx > 0 and dy <= 0:
        azymut = 180 - fi
    elif dx <= 0 and dy < 0:
        azymut = 180 + fi
    return azymut

def vertex_angle(x1, y1, x2, y2, x3, y3):
    angle =  azimuth(x1, y1, x2, y2) - azimuth(x2, y2, x3, y3) + 180
    if angle < 0:
        return angle + 360
    elif angle > 360:
        return angle - 360
    else:
        return angle

def listOfMinimumGeometries(geometry):
    arcpy.MinimumBoundingGeometry_management(geometry, "D:\semestr 2\ppg_egz\GW290819_-main\RECTANGLE_BY_AREA.shp","RECTANGLE_BY_AREA")
    arcpy.MinimumBoundingGeometry_management(geometry, "D:\semestr 2\ppg_egz\GW290819_-main\RECTANGLE_BY_WIDTH.shp","RECTANGLE_BY_WIDTH")
    arcpy.MinimumBoundingGeometry_management(geometry, "D:\semestr 2\ppg_egz\GW290819_-main\CONVEX_HULL", "CONVEX_HULL")
    arcpy.MinimumBoundingGeometry_management(geometry, "D:\semestr 2\ppg_egz\GW290819_-main\CIRCLE.shp", "CIRCLE")
    arcpy.MinimumBoundingGeometry_management(geometry, "D:\semestr 2\ppg_egz\GW290819_-main\ENVELOPE.shp", "ENVELOPE")

    list_of_minimum_geometries = [r"D:\semestr 2\ppg_egz\GW290819_-main\RECTANGLE_BY_AREA.shp",
             r"D:\semestr 2\ppg_egz\GW290819_-main\RECTANGLE_BY_WIDTH.shp",
             r"D:\semestr 2\ppg_egz\GW290819_-main\CONVEX_HULL.shp",
             r"D:\semestr 2\ppg_egz\GW290819_-main\CIRCLE.shp",
             r"D:\semestr 2\ppg_egz\GW290819_-main\ENVELOPE.shp"]
    return list_of_minimum_geometries


gmlID='PL.PZGIK.BDOT10k.BUBDA.18.6317842' # wybor id obiektu
where_clause = '"' + 'gmlId' + '" = ' + "'" + gmlID + "'"

arcpy.Select_analysis("BUBD.shp", 'BUBD_ID.shp', where_clause)
arcpy.FeatureVerticesToPoints_management('BUBD_ID.shp','BUBD_IDPKT.shp', "ALL")


wspBUBD_ID = []
data_list = []
for row in arcpy.da.SearchCursor('BUBD_IDPKT.shp', ["FID", "SHAPE@XY"]):
    IDobiekt = row[0]
    XYobiekt = row[1]
    wspBUBD_ID.append((IDobiekt, ) + XYobiekt)

#wspolrzedne punktow
#print wspBUBD_ID

arcpy.management.FindIdentical('BUBD_IDPKT.shp', 'BUBD_IDPKT_iden.txt', ["Shape"], output_record_option='ONLY_DUPLICATES')

list_of_duplicateID = []
with open('D:\semestr 2\ppg_egz\GW290819_-main\BUBD_IDPKT_iden.txt') as file:
    next(file)
    for line in file:
        row = line.split(',')
        list_of_duplicateID.append(int(row[1]))

list_of_begin_pointID = list_of_duplicateID[0::2]
list_of_end_pointID = list_of_duplicateID[1::2]

#lista punktow poczatkowych i koncowych
print list_of_begin_pointID
print list_of_end_pointID

index = 0

pointID_end = wspBUBD_ID[list_of_end_pointID[index]][0]
pointID_begin = wspBUBD_ID[list_of_begin_pointID[index]][0]

for pkt in wspBUBD_ID:
    pointID = pkt[0]
    X_point = pkt[1]
    Y_point = pkt[2]

    print('Punkt : %s' %pointID)

    if pointID == min(array(wspBUBD_ID)[:, 0]):
        pointID_in = wspBUBD_ID[list_of_end_pointID[0] - 1][0]
        X_in = wspBUBD_ID[list_of_end_pointID[0] - 1][1]
        Y_in = wspBUBD_ID[list_of_end_pointID[0] - 1][2]
        pointID_out = wspBUBD_ID[list_of_begin_pointID[0] + 1][0]
        X_out = wspBUBD_ID[list_of_begin_pointID[0] + 1][1]
        Y_out = wspBUBD_ID[list_of_begin_pointID[0] + 1][2]

        length_in = segment_length(X_point, Y_point, X_in, Y_in)
        length_out = segment_length(X_point, Y_point, X_out, Y_out)
        angle_in = vertex_angle(X_in, Y_in, X_point, Y_point, X_out, Y_out)
        print('dlugosc segmentu przed punktem : od %s do %s : %0.3f [m]' % (pointID_in, pointID, length_in))
        print('dlugosc segmentu po punkcie : od %s do %s : %0.3f [m]' % (pointID, pointID_out, length_out))
        print('kat miedzy punktami : %s - %s - %s: %0.6f [deg]' %(pointID_in, pointID, pointID_out, angle_in))


    elif (pointID < max(array(wspBUBD_ID)[:, 0])) and (pointID > min(array(wspBUBD_ID)[:, 0])):
        pointID_in = wspBUBD_ID[pointID - 1][0]
        X_in = wspBUBD_ID[pointID - 1][1]
        Y_in = wspBUBD_ID[pointID - 1][2]
        pointID_out = wspBUBD_ID[pointID + 1][0]
        X_out = wspBUBD_ID[pointID + 1][1]
        Y_out = wspBUBD_ID[pointID + 1][2]


        if pointID in list_of_end_pointID:
            length_in = segment_length(X_in, Y_in, X_point, Y_point)
            length_out = segment_length(X_point, Y_point, wspBUBD_ID[pointID_begin + 1][1], wspBUBD_ID[pointID_begin + 1][2])
            angle_in = vertex_angle(X_in, Y_in, X_point, Y_point, wspBUBD_ID[pointID_begin + 1][1], wspBUBD_ID[pointID_begin + 1][2])
            print('dlugosc segmentu przed punktem : %s - %s : %0.3f [m]' % (pointID_in, pointID, length_in))
            print('dlugosc segmentu po punkcie : %s - %s : %0.3f [m]' % (pointID, pointID_begin + 1, length_out))
            print('kat miedzy punktami : %s - %s - %s: %0.6f [deg]' % (pointID_in, pointID, pointID_begin + 1, angle_in))


            if index < len(list_of_end_pointID)-1:
                index += 1
                pointID_end = wspBUBD_ID[list_of_end_pointID[index]][0]
                pointID_begin = wspBUBD_ID[list_of_begin_pointID[index]][0]

        elif pointID in list_of_begin_pointID:
            length_in = segment_length(wspBUBD_ID[pointID_end - 1][1], wspBUBD_ID[pointID_end - 1][2], X_point, Y_point)
            length_out = segment_length(X_point, Y_point, X_out, Y_out)
            angle_in = vertex_angle(wspBUBD_ID[pointID_end - 1][1], wspBUBD_ID[pointID_end - 1][2], X_point, Y_point, X_out, Y_out)
            print('dlugosc segmentu przed punktem :%s - %s : %0.3f [m]' % (pointID_end - 1, pointID, length_in))
            print('dlugosc segmentu po punkcie : %s - %s : %0.3f [m]' % (pointID, pointID_out, length_out))
            print('kat miedzy punktami : %s - %s - %s: %0.6f [deg]' % (pointID_end - 1, pointID, pointID_out, angle_in))

        else:
            length_in = segment_length(X_in, Y_in, X_point, Y_point)
            length_out = segment_length(X_point, Y_point, X_out, Y_out)
            angle_in = vertex_angle(X_in, Y_in, X_point, Y_point, X_out, Y_out)
            print('dlugosc segmentu przed punktem :%s - %s : %0.3f [m]' % (pointID_in, pointID, length_in))
            print('dlugosc segmentu po punkcie : %s - %s : %0.3f [m]' % (pointID, pointID_out, length_out))
            print('kat miedzy punktami : %s - %s - %s: %0.6f [deg]' % (pointID_in, pointID, pointID_out, angle_in))

    else:
        pointID_in = wspBUBD_ID[pointID - 1][0]
        X_in = wspBUBD_ID[pointID - 1][1]
        Y_in = wspBUBD_ID[pointID - 1][2]
        pointID_out = wspBUBD_ID[list_of_begin_pointID[-1] + 1][0]
        X_out = wspBUBD_ID[list_of_begin_pointID[-1] + 1][1]
        Y_out = wspBUBD_ID[list_of_begin_pointID[-1] + 1][2]
        length_in = segment_length(X_point, Y_point, X_in, Y_in)
        length_out = segment_length(X_point, Y_point, X_out, Y_out)
        angle_in = vertex_angle(X_in, Y_in, X_point, Y_point, X_out, Y_out)
        print('dlugosc segmentu przed punktem : %s - %s : %0.3f [m]' % (pointID_in, pointID, length_in))
        print('dlugosc segmentu po punkcie : %s - %s : %0.3f [m]' % (pointID, pointID_out, length_out))
        print('kat miedzy punktami : %s - %s - %s: %0.6f [deg]' %(pointID_in, pointID, pointID_out, angle_in))


    data_list.append([ gmlID, pointID, length_in, length_out, angle_in])
#print data_list

wspBUBD_ID = listOfMinimumGeometries('BUBD_IDPKT.shp')

for geometry in wspBUBD_ID:
    near_features = arcpy.FeatureToLine_management(geometry, str(geometry)[:-4] + '_Linia.shp', "0.001 Meters", "ATTRIBUTES")
    in_features = 'BUBD_IDPKT.shp'
    arcpy.Near_analysis(in_features, near_features)
    i = 0
    for row in arcpy.da.SearchCursor(in_features, ["NEAR_DIST"]):
        data_list[i].append(float(row[0]))
        i += 1

results = pd.DataFrame(array(data_list), columns=['gmlid', 'vertex', 'length_in', 'length_out',
                               'angle_in', 'deflection_to_RECTANGLE_BY_AREA',
                               'deflection_to_RECTANGLE_BY_WIDTH', 'deflection_to_CONVEX_HULL',
                               'deflection_to_CIRCLE', 'deflection_to_ENVELOPE'])

results.to_csv('D:\semestr 2\ppg_egz\GW290819_-main\Results.csv', index=False)
print results