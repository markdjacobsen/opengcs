'''
Class representing an ArduPilot mission
'''

# TODO: would like this class to recevie it's own messages as well as fire events - like mission received complete
#   This is a very rudimentary implementation.  Need to flesh this out with:
#       Mission file reading and writing
#       Mission editing
#       Mavlink mission command construction
#       Etc.


class Mission(list):

    def __init__(self, count):
        list.__init__(self, [None]*count)
        self.wp_count = count
        self.wp_received = 0
        self.received_complete = False

    def add_wp(self, m):        # m is a MISSION_ITEM mavlink message
        self[m.seq] = Waypoint(m)
        self.wp_received += 1
        if self.wp_received == self.wp_count:
            self.received_complete = True

class Waypoint:

    def __init__(self, m):  # TODO KW: can we have multiple initializers?  This is probably not the only one we want
        self.wp_msg = m
