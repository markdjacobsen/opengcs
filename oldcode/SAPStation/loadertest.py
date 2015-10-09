from sap_frame_preflight import *

__author__ = 'markjacobsen'

from pymavlink import mavwp
from flightplan import *





# Create and initialize a Mission object from the specified arguments
print("Creating mission")
mission = Swarm()
mission.aircraft = "Fx61"
mission.name = "Test Mission"
mission.operator = ""
mission.description = ""
mission.num_flights = 1
mission.cruise_altitude = 1000
mission.altitude_variation = 0
mission.cruise_speed = 15
mission.cruise_headwind = 5
mission.drop_altitude = 200
mission.drop_wind_dir = 0
mission.drop_wind_speed = 0
mission.drop_latitude = 0
mission.drop_longitude = 0
mission.takeoff_plan = "lagunita_takeoff.txt"
mission.land_plan = "lagunita_land.txt"
mission.enroute_plan = "lagunita_box.txt"
mission.generate_flight_plans()
mission.save_flight_plans()

app = wx.App()
frame = SAPFramePreflight(None,mission.flights[0])
frame.Show()
app.MainLoop()