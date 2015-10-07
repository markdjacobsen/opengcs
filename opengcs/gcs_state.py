from pymavlink.mavutil import *

class Connection:
    def __init__(self):
        self.port = ""
        self.baud = ""

class MAV:
    """
    This class encapsulates a micro air vehicle (MAV), and theoretically represents the
    state of that vehicle at any moment in time. It is the responsibility of this class to
    communicate with the MAV and keep its internal state up to date.

    My vision is to separate serial connections from MAVs, so that one connection can
    have multiple MAVs. Unfortunately pymavlink doesn't work this way... the connection
    and MAV are interwoven in one mavfile object from pymavlink.mavutil. For now I am
    wrapping the mavfile object inside the MAV class, with the hope that we can later
    separate the two. Most of that work will probably be done inside the MAV class and
    Connection class.
    """
    def __init__(self):
        self.file = None

        # The class exposes a number of events that other code can subscribe to
        self.on_heartbeat = []
        self.on_param_received = []
        self.on_mission_event = []
        # etc... these are just placeholders for now to illustrate how this might work

    def connect(self, fd, address, source_system=255, notimestamps=False, input=True, use_native=default_native):
        self.file = mavfile(fd, address, source_system, notimestamps, input, use_native)


