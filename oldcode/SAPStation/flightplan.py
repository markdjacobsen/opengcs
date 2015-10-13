"""
The Syria Airlift Project

This file is subject to the terms and conditions defined in
the file 'LICENSE.txt', which is part of this source code package.

This package contains objects related to building Mission and Flight Plan objects.

As a general rule, flight plans are stored in object types from pymavlink like MAVWPLoader.
Geographic manipulations are done using geopy objects. The geopy point class is powerful and can utilize
many different latitude-longitude formats, meaning we can add new functionality later.

Dependencies:
  simplekml:    for importing geographic information in Google Earth KML/KMZ format and exporting to these formats
  geopy:        used for Point objects and some geographical calculations
  pymavlink:    for loading, saving, and manipulating APM flight plans
"""

# TODO more control over flight plan filenames
# TODO different types of deviation (fixed interval, uniform distribution, etc.)
# TODO embed placemark icons, so they don't have to be accessed online
# TODO replace aircraft hardcoded filename

__author__ = 'markjacobsen'
from pymavlink import mavwp
import simplekml
from geopy.distance import VincentyDistance
import geopy
from math import *
import random
import os
import config

#if os.getenv('MAVLINK10'):
#    import mavlinkv10 as mavlink
#else:
#    import mavlink

# These colors are used for drawing the flight plans in Google Earth. Each successive
# flight plan loops through these colors.
colors = [simplekml.Color.white,
          simplekml.Color.red,
          simplekml.Color.orange,
          simplekml.Color.yellow,
          simplekml.Color.green,
          simplekml.Color.blue,
          simplekml.Color.purple,
          simplekml.Color.brown,
          simplekml.Color.black,
          simplekml.Color.aqua,
          simplekml.Color.beige,
          simplekml.Color.cornflowerblue,
          simplekml.Color.darkgrey]

STATUS_DRAFT        = 0
STATUS_SCHEDULED    = 1
STATUS_PREFLIGHTED  = 2
STATUS_AIRBORNE     = 3
STATUS_LANDED       = 4
STATUS_CANCELLED    = 5
STATUS_ABORTED      = 6

class Roster:
    """
    A Roster is the highest-level data structure in SAPStation, and essentially represents a flying
    schedule of operations for a given period. It contains a list of swarms, which in turn contain
    a list of flights.
    """
    def __init__(self):
        self._swarms = []

    def add_swarm(self,swarm):
        if swarm not in self._swarms:
            self._swarms.append(swarm)

    def remove_swarm(self,swarm):
        if swarm in self._swarms:
            self._swarms.remove(swarm)

class Swarm:
    """
    A Swarm represents a swarm of aircraft participating in the same mission to the same drop zone.
    Each individual aircraft is reresented by a Flight object.
    The entire swarm shares a base flight plan, takeoff profile, and landing profile.
    """

    def __init__(self):
        """
        Initialize the Swarm object with default parameters
        """

        # Metadata about the swarm
        self.name = ""
        self.operator = ""
        self.aircraft = ""
        self.description = ""
        self.num_flights = 1

        self.flights = []

        # Flight plans
        self.enroute_plan = ""
        self.takeoff_plan = ""
        self.land_plan = ""
        self.cruise_altitude = 100
        self.lateral_variation = -0.1
        self.altitude_variation = 50
        self.cruise_speed = 15
        self.cruise_headwind = 0

        # Drop zone
        self.drop_altitude = 100
        self.drop_wind_dir = 0
        self.drop_wind_speed = 0
        self.drop_latitude = 0
        self.drop_longitude = 0

        # This is used when generating flights to assign each flight a unique number
        self.counter = 0

        return

    def generate_flight_plans(self):
        """
        Erase any existing flight plans in the swarm, and create a new set based on Swarm parameters.
        :return:
        """

        # Load the takeoff and landing flight plans, which will be the same for all flights
        loader_takeoff = mavwp.MAVWPLoader()
        loader_land = mavwp.MAVWPLoader()

        loader_takeoff.load(get_takeoff_path(self.takeoff_plan))
        loader_land.load(get_land_path(self.land_plan))

        # Delete any existing flights in the mission so we can start with a clean slate
        self.flights = []

        counter = 0

        # For every Flight in the Mission, create a Flight and call its generate_flight_plan() method
        for i in range(0, self.num_flights):
            print("Generating flight number " + str(i))

            # Load the en route flight plan, which will be modified for each route
            # We reload it each time because we don't want to retain the modifications
            # on subsequent flights
            loader_enroute = mavwp.MAVWPLoader()
            loader_enroute.load(get_enroute_path(self.enroute_plan))

            # Create a new Flight and add it to the Mission
            flight = Flight(self, counter)
            self.flights.append(flight)

            # Generate the waypoints
            flight.add_waypoints(loader_takeoff, include_home=True)
            flight.add_waypoints(loader_enroute)
            flight.add_waypoints(loader_land)

            # Offset en route waypoints
            # We leave the takeoff and landing waypoints fixed, and only apply the
            # offset to the enroute portion
            first_offset_waypoint = len(loader_takeoff.wpoints)
            last_offset_waypoint = first_offset_waypoint + len(loader_enroute.wpoints) - 1
            offset = self.lateral_variation * i
            alt_offset = round(random.uniform(0,self.altitude_variation),0)

            flight.offset_segment(first_offset_waypoint,last_offset_waypoint,offset,alt_offset)

            # TODO: add DO_SET_SPEED events for each leg, based on wind

            # TODO: shift CARP

            # TODO validation of flight plans

            counter += 1


        return

    def save_kml(self, filename='output.kml'):
        """
        Generate a KML file of the entire mission

        :param filename: kml filename. Defaults to output.kml
        """

        # Create a new kml file object
        kml = simplekml.Kml()

        # For each flight in the mission, call its add_to_kml() function
        for flight in self.flights:
            flight.add_to_kml(kml)

        # save the kml to a file
        kml.save_settings(filename)
        return

    def save_flight_plans(self):
        """
        Generate a flight plan file for each Flight in the Mission
        """
        for flight in self.flights:
            flight.save_flight_plan()


class Flight:
    def __init__(self, swarm, swarm_id):
        """
        Create an empty flight.
        :param swarm: A reference to the Mission object that owns the Flight
        :param swarm_id: A unique, sequential numeric identifier for the flight
        """
        self.swarm = swarm
        self.id = swarm_id
        self.status = STATUS_DRAFT

        self.name = swarm.name + "_" + str(self.id)

        self.waypoints = []
        return

    def add_waypoints(self, wps, include_home=False):
        """
        Add a list of waypoints to the Flight.
        :param wps: A MAVWPLoader object containing waypoints to load
        :param include_home: Specify whether or not to include waypoint 0 (Home) in this flight plan. Default no.
        :return:
        """

        # Only include waypoint 0 if the caller specifies to include_home
        # Normally, home will only be added with the takeoff segment, which is why we want
        # the caller to have the option to not include home.
        if include_home is True:
            first_wp = 0
        else:
            first_wp = 1

        for i in range(first_wp, wps.count()):
            self.waypoints.append(wps.wpoints[i])

        return

    def add_to_kml(self, kml):
        """
        This adds the flight to an existing simplekml object. It creates a folder for the Flight,
        then adds placemarks at each waypoint and a linestring connecting all of them.
        :param kml:     An open simplekml object (typically generated by Mission.generate_kml)

        :return:
        """
        folder = kml.newfolder(name=self.name)

        # This will save each coordinate pair, and is used at the end to generate a kml LineString object
        # connecting the waypoints
        all_coords = []

        # Loop through each waypoint, creating a kml point and adding the coordinates to all_coords
        for i in range(0,len(self.waypoints)):
            # s holds a waypoint name, in the format MISSION_POINT
            s = str(self.id) + "_" + str(i)
            wp = self.waypoints[i]
            pnt = folder.newpoint(name=s, coords=[(wp.y, wp.x)])
            pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
            all_coords.append((wp.y, wp.x))

        # Create a LineString showing the entire flight plan
        ls = folder.newlinestring(name=self.name, coords=all_coords)
        #ls = kml.newlinestring(name=self.name, coords=all_coords)

        line_color = self.id % len(colors)
        print("Colors",self.id, line_color)
        ls.style.linestyle.color = colors[line_color]

    def save_flight_plan(self):
        """
        Save a copy of the flight plan
        """
        filename = self.name + ".txt"
        loader = mavwp.MAVWPLoader()
        loader.wpoints = self.waypoints
        loader.save(config.output_directory + "/" + filename)

    def offset_segment(self,wp_first,wp_last,offset,alt_offset):
        """
        Offsets a portion of the flight by a specified amount.

        :param wp_first: The number of the first waypoint to offset
        :param wp_last: The number of the last waypoint to offset
        :param offset: The distance to offset (km). Positive for right, engative for left.
        :param alt_offset: Altitude to offset (m). Positive for up.
        """


        # These will temporarily hold the offset turnpoint
        new_lats = []
        new_lons = []
        new_alts = []

        # Loop through each waypoint, call offset_turnpoint, and get back a tuple with new coordinates.
        # Store this in a couple lists.
        # We can't modify the actual waypoints yet, becuase they are used in subsequent calls to
        # offset_turnpoint
        for wp_idx in range(wp_first,wp_last):
            new_wp = self.offset_waypoint(wp_idx,offset)
            new_lats.append(new_wp[0])
            new_lons.append(new_wp[1])

        # Now copy those new lats and lons into the original waypoints
        for wp_idx in range(wp_first,wp_last):
            self.waypoints[wp_idx].x = new_lats[wp_idx - wp_first]
            self.waypoints[wp_idx].y = new_lons[wp_idx - wp_first]
            self.waypoints[wp_idx].z = self.waypoints[wp_idx].z + alt_offset



    def offset_waypoint(self,wp_num,offset):
        """
        This offsets a single waypoint by a given lateral offset.
        This function is not intended to be used by itself, but is called
        from offset_segment().

        :param wp_num: The index of the waypoint to offset
        :param offset: The amount to offset (km). Positive is right, negative is left.
        :return: A tuple (latitude, longitude)
        """

        # For a zero offset, return the original point
        if offset == 0.0:
            return (self.waypoints[wp_num].x,self.waypoints[wp_num].y)

        current_point = self.waypoints[wp_num]


        # create prev_point, curent_point,next_point
        heading_in = -1
        heading_out = -1

        # Three cases

        # Case 1: if previous point is None, we are at the start of a route, and the offset will
        # simply be 90 degrees off from the outbound heading
        if wp_num == 0:
            heading_out = get_bearing(self.waypoints[wp_num], self.waypoints[wp_num+1])
            range = abs(offset)
            if offset >= 0:
                bearing = wrap_angle(heading_out + 90.0)
            else:
                bearing = wrap_angle(heading_out - 90.0)

        # Case 2: if next point is None, we are at the end of a route and the offset will
        # simply be 90 degrees off from the inbound heading
        if wp_num == len(self.waypoints)-1:
            heading_in = get_bearing(self.waypoints[wp_num-1], self.waypoints[wp_num])
            range = abs(offset)
            if offset >= 0:
                bearing = wrap_angle(heading_in + 90.0)
            else:
                bearing = wrap_angle(heading_in - 90.0)


        # Case 3: for points in the middle, the angle is based on both the inbound and outbound course
        if wp_num is not 0 and wp_num is not len(self.waypoints)-1:
            heading_in = get_bearing(self.waypoints[wp_num-1], self.waypoints[wp_num])
            heading_out = get_bearing(self.waypoints[wp_num], self.waypoints[wp_num+1])

            angle = wrap_angle(abs((180+heading_in) - heading_out))
            half_angle = angle/2.0

            # This computes a range and bearing from the current waypoint to the
            # offset point
            #range = sin(radians(half_angle)) * offset
            print("Half angle:", half_angle, "Offset:",offset)
            range = abs(offset)/sin(radians(half_angle))
            #bearing = wrap_angle(heading_in + 90 + (90.0 - half_angle))

            bearing = wrap_angle(heading_out + half_angle)
            if offset < 0:
                bearing = wrap_angle(bearing + 180.0)



        # Now get lat-lon of a new point
        mypoint = geopy_point(self.waypoints[wp_num])
        vd = VincentyDistance(kilometers=range)
        destination = vd.destination(mypoint, bearing)

        print("Wp: " + str(wp_num) + ", Head In: " + str(heading_in) + ", Head Out: " + str(heading_out) + ","
              "Range:" + str(range) + ", Bearing: " + str(bearing))

        print("Old:",self.waypoints[wp_num].x,self.waypoints[wp_num].y)

        # Return a tuple of the new coordinates
        return (destination.latitude,destination.longitude)

def get_bearing(origin,destination):
        """
        Get the bearing betwen two waypoints.

        :param origin: (MAV waypoint) origin coordinate
        :param destination: (MAV waypoint) destination coordinate
        :return: bearing from origin to destination in degrees
        """

        # Rename for ease of reference
        lat1 = origin.x
        lat2 = destination.x
        lon1 = origin.y
        lon2 = destination.y

        # Compute the difference in lat and lon
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        # Do a bunch of trigonometry
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
        #if tc1 > 0:
        tc1 = degrees(tc1)
        angle = tc1

        # An old method I had some trouble with... kept for reference

        #angle = degrees(atan2(destination.x - origin.x, destination.y - origin.y))

        # Normalize the bearing between 0 and 360
        return wrap_angle(angle)


def wrap_angle(angle):
    """
    This simply checks to ensure that an angle is between 0 and 360 degrees, and normalizes it if not.

    :param angle: unnormalized angle in degrees
    :return normalized angle between 0 and 360 degrees:
    """
    return (angle + 360) % 360


def geopy_point(point):
    """
    Convert a MAVWP point to a geopy.Point

    :param point: a MAVWP point
    :return geopy.Point:
    """
    new_point = geopy.Point()
    new_point.latitude = point.x
    new_point.longitude = point.y
    return new_point

def get_takeoff_plans():
    all_files = [ f for f in os.listdir(config.takeoff_flightplan_directory) if os.path.isfile(os.path.join(config.takeoff_flightplan_directory,f))]
    return all_files

def get_enroute_plans():
    all_files = [ f for f in os.listdir(config.enroute_flightplan_directory) if os.path.isfile(os.path.join(config.enroute_flightplan_directory,f))]
    return all_files

def get_landing_plans():
    all_files = [ f for f in os.listdir(config.landing_flightplan_directory) if os.path.isfile(os.path.join(config.landing_flightplan_directory,f))]
    return all_files

def get_takeoff_path(filename):
    print filename
    return config.takeoff_flightplan_directory + "/" + filename

def get_land_path(filename):
    return config.landing_flightplan_directory + "/" + filename

def get_enroute_path(filename):
    return config.enroute_flightplan_directory + "/" + filename