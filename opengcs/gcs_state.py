from pymavlink.mavutil import *
import threading
import xmltodict

from enum import Enum
#class ConnectionType(Enum):
#    serial = 0
#    tcp = 1
#    udp = 2

class GCSState():
    """
    Root data model item for gcsstation.

    This class contains the state of the gcs, to include lists of connections, mavs,
    and mavlink components, fleet management data, and configuration  data
    """
    def __init__(self):
        self.connections = []
        self.mavs = []
        self.components = []
        self.config = GCSConfig()

        return

class Connection:
    """
    Encapsulates a connection via serial, TCP, or UDP ports, etc.
    """
    def __init__(self):
        self.port = ""
        self.number = ""
        self.mavs = []

    def __init__(self, port, number):
        self.port = port
        self.number = number

        # TODO figure out how to handle these
        if port == "UDP" or port == "TCP":
            return

        # TODO
        # The vision is to ulimately split connections and MAVs, so one connection
        # can support multiple MAVs. For now, we cheat and just build a single MAV
        # per connection, with the pymavlink.mavlink_connection() object stored in
        # the MAV object.
        newmav = MAV()
        newmav.connect(port, number)

    def getPortDead(self):
        """
        Returns whether the connection is alive or dead
        """
        if len(self.mavs) == 0:
            return True
        else:
            return self.mavs[0].portdead

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
        self.systemid = None
        self.master = None

        # The class exposes a number of events that other code can subscribe to
        self.on_heartbeat = []
        self.on_param_received = []
        self.on_mission_event = []
        # etc... these are just placeholders for now to illustrate how this might work

    def connect(self, port, number):
        self.master = mavlink_connection(port, baud=number)
        self.thread = threading.Thread(target=self.process_messages)
        self.thread.setDaemon(True)
        self.thread.start()

        self.master.message_hooks.append(self.check_heartbeat)

    def check_heartbeat(self,caller,msg):
        """
        Listens for a heartbeat message

        Once this function is subscribed to the dispatcher, it listens to every
        incoming MAVLINK message and watches for a 'HEARTBEAT' message. Once
        that message is received, the function updates the GUI and then
        unsubscribes itself.
        """

        if msg.get_type() ==  'HEARTBEAT':
            print("Heartbeat received from APM (system %u component %u)\n" % (self.master.target_system, self.master.target_system))
            self.system_id = self.master.target_system
            self.master.message_hooks.remove(self.check_heartbeat)

class GCSConfig:
    def __init__(self):
        self.settings = {}
        self.load()

    def load(self):
        with open('settings.xml') as fd:
            self.settings = xmltodict.parse(fd.read())['settings']
        print(self.settings)
        return

    def save(self):
        return