'''
Class representing an ArduPilot mission
'''

# TODO: would like this class to recevie it's own messages as well as fire events - like mission received complete
#   This is a very rudimentary implementation.  Need to flesh this out with:
#       Mission file reading and writing
#       Mission editing
#       Mavlink mission command construction
#       Etc.


# Mission commands.  Adapted from ardupilotmega.h
# Note: not all commands apply to all aircraft types
mission_commands = {
    16		: "NAV_WAYPOINT",
    17		: "NAV_LOITER_UNLIM",
    18		: "NAV_LOITER_TURNS",
    19		: "NAV_LOITER_TIME",
    20		: "NAV_RETURN_TO_LAUNCH",
    21		: "NAV_LAND",
    22		: "NAV_TAKEOFF",
    30		: "NAV_CONTINUE_AND_CHANGE_ALT",
    31		: "NAV_LOITER_TO_ALT",
    80		: "NAV_ROI",
    81		: "NAV_PATHPLANNING",
    82		: "NAV_SPLINE_WAYPOINT",
    83		: "NAV_ALTITUDE_WAIT",
    92		: "NAV_GUIDED_ENABLE",
    95		: "NAV_LAST",
    112		: "CONDITION_DELAY",
    113		: "CONDITION_CHANGE_ALT",
    114		: "CONDITION_DISTANCE",
    115		: "CONDITION_YAW",
    159		: "CONDITION_LAST",
    176		: "DO_SET_MODE",
    177		: "DO_JUMP",
    178		: "DO_CHANGE_SPEED",
    179		: "DO_SET_HOME",
    180		: "DO_SET_PARAMETER",
    181		: "DO_SET_RELAY",
    182		: "DO_REPEAT_RELAY",
    183		: "DO_SET_SERVO",
    184		: "DO_REPEAT_SERVO",
    185		: "DO_FLIGHTTERMINATION",
    189		: "DO_LAND_START",
    190		: "DO_RALLY_LAND",
    191		: "DO_GO_AROUND",
    200		: "DO_CONTROL_VIDEO",
    201		: "DO_SET_ROI",
    202		: "DO_DIGICAM_CONFIGURE",
    203		: "DO_DIGICAM_CONTROL",
    204		: "DO_MOUNT_CONFIGURE",
    205		: "DO_MOUNT_CONTROL",
    206		: "DO_SET_CAM_TRIGG_DIST",
    207		: "DO_FENCE_ENABLE",
    208		: "DO_PARACHUTE",
    209		: "DO_MOTOR_TEST",
    210		: "DO_INVERTED_FLIGHT",
    211		: "DO_GRIPPER",
    212		: "DO_AUTOTUNE_ENABLE",
    220		: "DO_MOUNT_CONTROL_QUAT",
    221		: "DO_GUIDED_MASTER",
    222		: "DO_GUIDED_LIMITS",
    240		: "DO_LAST",
    241		: "PREFLIGHT_CALIBRATION",
    242		: "PREFLIGHT_SET_SENSOR_OFFSETS",
    245		: "PREFLIGHT_STORAGE",
    246		: "PREFLIGHT_REBOOT_SHUTDOWN",
    252		: "OVERRIDE_GOTO",
    300		: "MISSION_START",
    400		: "COMPONENT_ARM_DISARM",
    500		: "START_RX_PAIR",
    520		: "REQUEST_AUTOPILOT_CAPABILITIES",
    2000	: "IMAGE_START_CAPTURE",
    2001	: "IMAGE_STOP_CAPTURE",
    2500	: "VIDEO_START_CAPTURE",
    2501	: "VIDEO_STOP_CAPTURE",
    2800	: "PANORAMA_CREATE",
    30001	: "PAYLOAD_PREPARE_DEPLOY",
    30002	: "PAYLOAD_CONTROL_DEPLOY",
    42424	: "DO_START_MAG_CAL",
    42425	: "DO_ACCEPT_MAG_CAL",
    42426	: "DO_CANCEL_MAG_CAL",
    42427	: "ENUM_END"
}

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
