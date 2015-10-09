# LatLon class
#
# This class represents a latitude-longitude coordinate.
# The core of the class are two floats: latitude and longitude.
# Values are assigned with the multiple versions of the Assign function.

import math

class LatLon:
    latitude = 0
    longitude = 0

    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon

    def LatitudeDirection(self):
        if self.latitude >= 0:
            return 'N'
        else:
            return 'S'

    def LongitudeDirection(self):
        if self.longitude >= 0:
            return 'E'
        else:
            return 'W'

    def LatitudeDegrees(self):
        latitudeWhole = int(self.latitude)
        return latitudeWhole

    def LongitudeDegrees(self):
        longitudeWhole = int(self.longitude)
        return longitudeWhole

    
        
            

    
    
