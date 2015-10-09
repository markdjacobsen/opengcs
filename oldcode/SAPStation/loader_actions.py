"""
This class contains actions that are called by the SAPLoader. Each action is a self-contained
piece of code inherited from LoaderAction(). The SAPLoader class contains a list of these
actions and calls each one in sequence.

An action must be initialized with a call to connect()
An action is started with a call to begin()
An action terminates with a call to finish().
Observers are added to the action with add_observer(). When the action finishes, each of these
observers is notified.
The process_message() method listens for and processes messages from the MAV. It is assigned
observer status by the calling code in SAPLoader()

"""


# TODO replace print with log and standardize messages
# TODO error checking, return errors
# TODO figure out RNGFND2_SETTLE_M vs RNGFND2_SETTLE


__author__ = 'markjacobsen'

from pymavlink import mavwp
from pymavlink import mavutil
import os
import time
import console

str_action_wp = "Upload waypoints"
str_action_param = "Upload parameters"
str_action_arm = "Arm the motor"
str_action_auto = "Prepare for AUTO takeoff"

filename_exclusion = "../exclude_parameters.txt"

class LoaderAction(object):
    def __init__(self):
        """
        Assign empty values
        """
        self.name = ""
        self.label = ""
        self.running = False
        self._observers = []

    def begin(self):
        """
        Begin executing this action. The action will continue until finish() is called
        """
        console.log(1,self.name + ": begin()")
        self.finish(1)
        return

    def finish(self,status):
        """
        Finish executing this action and notify any observers.
        :param status: 1 for success, 0 for failure
        """
        self.running = False
        for observer in self._observers:
            observer(status)
        self._observers = []
        return

    def process_message(self,msg):
        """
        Listens for and processes messages from the dispatcher
        :param msg: An incoming message from the MAV
        """
        print(self.name, ": processing:",msg)
        return

    def connect(self,master):
        """
        Initializes the 'master' instance variable, after 'master' has been
        connected to the MAV.
        :param master: An initialized master object
        :return:
        """
        console.log(1,self.name + ": connect()")
        self.master = master

    def add_observer(self,observer):
        """
        Add an observer function, which will be notified when the action is complete
        :param observer: An observer function
        """
        if not observer in self._observers:
            self._observers.append(observer)

    def remove_observer(self,observer):
        """
        Remove an observer function from the list to be notified after the action is complete.
        :param observer: An observer function
        :return:
        """
        self._observers.remove(observer)


class Action_WP(LoaderAction):
    """
    This action loads a sequence of waypoints from a flight plan file and transmits them to
    the MAV. It completes once the waypoints are uploaded and verified.

    Much of this code is taken directly from MAVProxy by Andrew Tridgell
    https://github.com/tridge/MAVProxy
    See mavproxy_wp.py, mavutil.py, mavlink10.py

    Before calling begin(), be sure to specify self.filename

    See MAVLINK documentation for the right sequence of messages. Note that
    this documentation specifies messages titled WAYPOINT_*, but this is from
    v0.9 and has been replaced with MISSION_* in v1.0. Also note that the calls
    to pymavlink will only work if the MAVLINK10 environment variable is set.
    """
    def __init__(self):
        super(Action_WP, self).__init__()
        self.name = "Waypoints"
        self.filename = ""
        self.label = str_action_wp
        self.wploader = mavwp.MAVWPLoader()
        self.wp_op = None
        self.loading_waypoints = False
        self.loading_waypoint_lasttime = time.time()
        self.last_waypoint = 0
        self.wp_period = mavutil.periodic_event(0.5)
        self.undo_wp = None
        self.undo_type = None
        self.undo_wp_idx = -1

    def begin(self):
        """
        Load the flight plan from the file and send a waypoint count
        """
        print("Action_WP.begin()")
        self.running = True
        self.wploader.load(self.filename)
        self.send_all_waypoints()

    def load_waypoints(self, filename):
        '''load waypoints from a file'''
        self.wploader.target_system = self.master.target_system
        self.wploader.target_component = self.master.target_component
        try:
            self.wploader.load(filename)
        except Exception as msg:
            print("Unable to load %s - %s" % (filename, msg))
            return
        print("Loaded %u waypoints from %s" % (self.wploader.count(), filename))
        self.send_all_waypoints()

    def send_all_waypoints(self):
        """
        This is the first step of the waypoint upload sequence. It begins by
        sending the MAV a waypoint count.
        """
        self.master.waypoint_clear_all_send()
        print(self.wploader.count())
        if self.wploader.count() == 0:
            return
        self.loading_waypoints = True
        self.loading_waypoint_lasttime = time.time()

        # Directly call the MAVLINK v1.0 function instead of the wrapper
        self.master.waypoint_count_send(self.wploader.count())
        #self.master.mav.mission_count_send(self.master.target_system, self.master.target_component, self.wploader.count())

    def process_waypoint_request(self, m, master):
        """
        Each time the MAV sends a request for a subsequent waypoint, this function processes
        the message and sends the waypoint.
        :param m: The message
        :param master: The master requesting the waypoint
        """
        print("process waypoint request")
        if (not self.loading_waypoints or
            time.time() > self.loading_waypoint_lasttime + 10.0):
            self.loading_waypoints = False
            self.console.error("not loading waypoints")
            return
        if m.seq >= self.wploader.count():
            self.console.error("Request for bad waypoint %u (max %u)" % (m.seq, self.wploader.count()))
            return
        wp = self.wploader.wp(m.seq)
        print("Sending waypoint: ",m.seq)
        wp.target_system = self.master.target_system
        wp.target_component = self.master.target_component
        self.master.mav.send(self.wploader.wp(m.seq))
        self.loading_waypoint_lasttime = time.time()
        #self.console.writeln("Sent waypoint %u : %s" % (m.seq, self.wploader.wp(m.seq)))
        if m.seq == self.wploader.count() - 1:
            self.loading_waypoints = False
            self.running = False
            console.log(1,"Waypoints successfully sent")
            self.finish(1)
            #self.console.writeln("Sent all %u waypoints" % self.wploader.count())


    def process_message(self,m):
        """
        Once the initial waypoint count is sent, the MAV will send a series of messages back.
        This function listens for those messages and handles each one appropriately.
        :param m:  The message
        """
        mtype = m.get_type()
        print("Action_WP.processing(): ", mtype)
        if mtype in ['WAYPOINT_COUNT','MISSION_COUNT']:
            if self.wp_op is None:
                self.console.error("No waypoint load started")
            else:
                self.wploader.clear()
                self.wploader.expected_count = m.count
                self.console.writeln("Requesting %u waypoints t=%s now=%s" % (m.count,
                                                                                 time.asctime(time.localtime(m._timestamp)),
                                                                                 time.asctime()))
                self.master.waypoint_request_send(0)

        elif mtype in ['WAYPOINT', 'MISSION_ITEM'] and self.wp_op != None:
            if m.seq > self.wploader.count():
                self.console.writeln("Unexpected waypoint number %u - expected %u" % (m.seq, self.wploader.count()))
            elif m.seq < self.wploader.count():
                # a duplicate
                pass
            else:
                self.wploader.add(m)
            if m.seq+1 < self.wploader.expected_count:
                self.master.waypoint_request_send(m.seq+1)
            else:
                if self.wp_op == 'list':
                    for i in range(self.wploader.count()):
                        w = self.wploader.wp(i)
                        print("%u %u %.10f %.10f %f p1=%.1f p2=%.1f p3=%.1f p4=%.1f cur=%u auto=%u" % (
                            w.command, w.frame, w.x, w.y, w.z,
                            w.param1, w.param2, w.param3, w.param4,
                            w.current, w.autocontinue))
                    if self.logdir != None:
                        waytxt = os.path.join(self.logdir, 'way.txt')
                        self.save_waypoints(waytxt)
                        print("Saved waypoints to %s" % waytxt)
                elif self.wp_op == "save":
                    self.save_waypoints(self.wp_save_filename)
                self.wp_op = None

        elif mtype in ["WAYPOINT_REQUEST", "MISSION_REQUEST"]:
            self.process_waypoint_request(m, self.master)

        elif mtype in ["WAYPOINT_CURRENT", "MISSION_CURRENT"]:
            if m.seq != self.last_waypoint:
                self.last_waypoint = m.seq
                if self.settings.wpupdates:
                    self.say("waypoint %u" % m.seq,priority='message')



class Action_Params(LoaderAction):
    """
    This action uploads a list of parameters from a file.

    Much of this code is taken directly from MAVProxy by Andrew Tridgell
    https://github.com/tridge/MAVProxy
    See mavproxy_param.py, mavutil.py, mavlink10.py

    Before use, initialize self.filename to a parameter file

    The action will consult a file called exclude_parameters.txt in the
    application, which is simply a list of parameters (one per line).
    These parameters will be skipped when parsing the parameter file.
    This ensures that parameters unique to each aircraft (such as
    compass offsets) won't be overwritten by master parameter files.

    """
    def __init__(self):
        super(Action_Params, self).__init__()
        self.name = "Parameters"
        self.label = str_action_param
        self.filename = ""
        self.params = []

        # Because floating point numbers sometimes get extra digits,
        # we check equality by ensuring the difference between
        # two numbers is less than this epsilon
        self.epsilon = 0.01


    def begin(self):
        print("Action_Params.begin()")

        # Load the exclusion list
        exclude_file = open(filename_exclusion, 'r')
        self.exclude = exclude_file.readlines()
        exclude_file.close()

        # Load the parameter file
        self.params = []
        param_file = open(self.filename,'r')
        for line in param_file:
            # Skip comment lines
            if line[0]=='#':
                continue
            stripped = line.strip()
            results = stripped.split(',')
            self.params.append((results[0],float(results[1])))
        param_file.close()

        # Send the first parameter
        self.current_param = 0
        #self.master.mav_param.mavset(self.master, self.params[0][0],self.params[0][1], retries=3)
        print("Sending Parameter: ",self.params[0][0],self.params[0][1])
        self.master.param_set_send(self.params[0][0], self.params[0][1])

    def process_message(self,msg):
        self.handle_mavlink_packet(self.master,msg)

    def handle_mavlink_packet(self, master, m):
        '''handle an incoming mavlink packet'''
        if m.get_type() == 'PARAM_VALUE':
            readback_id = "%.16s" % m.param_id
            readback_value = float(m.param_value)
            readback_text = m.param_value

            if self.params[self.current_param][0] == readback_id and abs(self.params[self.current_param][1] - readback_value) < self.epsilon:
                print("Good readback")
                self.current_param = self.current_param + 1

                if self.current_param == len(self.params):
                    print("All parameters uploaded")
                    self.finish(1)
                    return

                print("Sending Parameter: ",self.params[self.current_param][0],self.params[self.current_param][1])
                self.master.param_set_send(self.params[self.current_param][0], self.params[self.current_param][1])

            else:
                print("Bad readback",readback_id,readback_value,readback_text)
                self.finish(0)

class Action_Arm(LoaderAction):
    def __init__(self):
        super(Action_Arm, self).__init__()
        self.name = "Arm"
        self.label = str_action_arm

    def begin(self):
        print("Action_Arm.begin()")

    def process_message(self,msg):
        print(msg)
        self.finish(1)

class Action_Auto(LoaderAction):
    # See mavlink10.py class MAVLink_set_mode_message(MAVLink_message):

    def __init__(self):
        super(Action_Auto, self).__init__()
        self.name = "Auto"
        self.label = str_action_auto

    def begin(self):
        print("Action_Auto.begin()")

    def process_message(self,msg):
        print(msg)
        self.finish(1)

