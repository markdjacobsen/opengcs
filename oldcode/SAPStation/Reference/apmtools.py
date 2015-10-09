# Old code, kept in the project for reference only

__author__ = 'markjacobsen'

from pymavlink import mavwp
import simplekml
from math import *
import geopy
from geopy.distance import VincentyDistance

class route:
    def __init__(self,wps=None):
        self.name = "New Route"
        self.description = ""
        self.waypoints = None
        self.starttime = None
        self.color = None

        if wps == None:
            return
        else:
            self.waypoints = wps

    def loadFromFile(self,filename):
        self.waypoints = []
        loader = mavwp.MAVWPLoader()
        loader.load(filename)

        # Isolate part of filename before period
        splittext = filename.split('.')
        self.name = splittext[0]
        for x in range(0,loader.count()):
            self.waypoints.append(loader.wpoints[x]) # Add the waypoint to the route object

    def getFlightPlanText(self):
        completestring = ""
        for x in range(0,len(self.waypoints)):
            w = self.waypoints[x]               # Create an easy reference for printing purposes
            s = repr(x) + ".   " +\
                repr(w.frame) + ',' +\
                repr(w.command) + ',' +\
                repr(w.current) + ',' +\
                repr(w.autocontinue) + ',' +\
                repr(w.param1) + ',' +\
                repr(w.param2) + ',' +\
                repr(w.param3) + ',' +\
                repr(w.param4) + ',' +\
                repr(w.x) + ',' +\
                repr(w.y) + ',' +\
                repr(w.z)
            completestring += (s+ '\n')
        return completestring

    def addToKML(self, kml):

        # Create a KML folder
        fol = kml.newfolder(name=self.name)

        mycoords = []

        # Create placemarks for each waypoint, and build a list of coordinates
        # that will be used for the LineString below
        for x in range(0,len(self.waypoints)):
            w = self.waypoints[x]
            fol.newpoint(name=repr(x), coords=[(w.y,w.x)])
            mycoords.append((w.y,w.x))

        # Create a LineString showing the route
        lin = fol.newlinestring(name=self.name, description=self.description,coords=mycoords)

class navtools:
    def getHeadingToWaypoint(self,origin,destination):

        lat1 = origin.y
        lat2 = destination.y
        lon1 = origin.x
        lon2 = destination.x
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        # This formula is from http://mathforum.org/library/drmath/view/55417.html
        y = sin(lon2-lon1)*cos(lat2)
        x = cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1)
        if y > 0:
            if x > 0:
                tc1 = atan(y/x)
            if x < 0:
                tc1 = pi - atan(-y/x)
            if x == 0:
                tc1 = pi/2
        if y < 0:
            if x > 0:
                tc1 = -atan(-y/x)
            if x < 0:
                tc1 = atan(y/x)-pi
            if x == 0:
                tc1 = 1.5 * pi
        if y == 0:
            if x > 0:
                tc1 = 0
            if x < 0:
                tc1 = pi
            if x == 0:
                tc1 = -1
        if tc1 > 0:
            tc1 = degrees(tc1)


        angle = degrees(atan2(destination.y - origin.y, destination.x - origin.x))
        bearing1 = (angle + 360) % 360
        bearing2 = (90 - angle) % 360
        return bearing1

    def createOffsetPoint(self,origin,bearing,offset_distance):


        #offset_bearing will be the bearing to the new waypoint (i.e. due left or right of origin)
        if offset_distance > 0:
            offset_bearing = bearing + 90
            if offset_bearing >= 360:
                offset_bearing -= 360
        else:
            offset_bearing = bearing - 90
            if offset_bearing < 0:
                offset_bearing += 360

        print("Input: %f, %f, %d, %d, %f" % (origin.y, origin.x, bearing, offset_bearing, offset_distance))
        #code taken from http://stackoverflow.com/questions/877524/calculating-coordinates-given-a-bearing-and-a-distance
        rEarth = 6371.01
        epsilon = 0.000001
        rlat1 = radians(origin.y)
        rlon1 = radians(origin.x)
        rbearing = radians(offset_bearing)
        rdistance = offset_distance / rEarth # normalize linear distance to radian angle

        rlat = asin( sin(rlat1) * cos(rdistance) + cos(rlat1) * sin(rdistance) * cos(rbearing))

        if cos(rlat) == 0 or abs(cos(rlat)) < epsilon: # Endpoint a pole
    	    rlon=rlon1
        else:
    	    rlon = ( (rlon1 - asin( sin(rbearing)* sin(rdistance) / cos(rlat) ) + pi ) % (2*pi) ) - pi

        lat = degrees(rlat)
        lon = degrees(rlon)
        print("Method 1 Output: %f,%f" % (lat,lon))
        #return (lat,lon)

        #version 2
        mypoint = geopy.Point(origin.y, origin.x)
        vd = VincentyDistance(kilometers=offset_distance)
        destination = vd.destination(mypoint, offset_bearing)
        print("Method 2 Output: %f,%f" % (destination.latitude,destination.longitude))
        #return (destination.latitude,destination.longitude)

        #version 3
        R = 6378.1 #Radius of the Earth
        brng = rbearing #Bearing is 90 degrees converted to radians.
        d = offset_distance #Distance in km

        lat1 = radians(origin.y) #Current lat point converted to radians
        lon1 = radians(origin.x) #Current long point converted to radians

        lat2 = asin( sin(lat1)*cos(d/R) +
        cos(lat1)*sin(d/R)*cos(brng))

        lon2 = lon1 + atan2(sin(brng)*sin(d/R)*cos(lat1),
             cos(d/R)-sin(lat1)*sin(lat2))

        lat2 = degrees(lat2)
        lon2 = degrees(lon2)

        return (lat2,lon2)


r = route()
r.loadFromFile('flightplan.txt')
kml = simplekml.Kml()
r.addToKML(kml)
kml.save('flightplan.kml')
