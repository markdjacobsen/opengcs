# This contains implementations for each type of preflight check.
# Each check is a separate class inheriting from ChecklistItemPanel, which is defined in checklists.py.
# ChecklistItemPanel, in turn, inherits from ChecklistItemPanelBase in baseforms.py, which is auto-generated
# by wxFormBuilder.
#
# To use, follow the example of ChecklistItem_ZeroizeAirspeed. Be sure to call the super constructor,
# then add whatever controls you want to self.sizerRow2 (a horizontal sizer containing the second row of
# the checklist panel. Call self.parent.add_subscriber() to subscribe to any mavlink message types that you
# need. Call self.set_green(), set_red(), or set_yellow() to determine the check's status.

from forms.checklists import *
from pymavlink import mavutil
import wx, os

class AverageValue:
    """
    This class keeps the running average of a variable, with a specified memory length.
    For example, tracking the average airspeed over the last 10 samples.
    """
    def __init__(self, memory_length):
        self.memory_length = memory_length
        self.values = []

    def add_value(self, value):
        self.values.append(value)
        if len(self.values) >= self.memory_length:
            self.values.remove(0)

    def average(self):
        return sum(self.values)/len(self.values)

class ChecklistItem_ZeroizeAirspeed  (ChecklistItemPanel):
    """
    This check verifies that the user has run an airspeed sensor calibration, and that the resting airspeed
    # does not exceed some threshold (i.e. 2 m/s).
    """
    def __init__(self, parent):
        super(ChecklistItem_ZeroizeAirspeed, self).__init__(parent)

        # Override attributes of ChecklistItem
        self.staticStepName.SetLabel("Calibrate/Zeroize Airspeed Sensor")

        # Build row 2
        self.staticAirspeed = wx.StaticText( self, wx.ID_ANY, u"Airspeed: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.buttonZeroize = wx.Button(self, wx.ID_ANY, u"Calibrate", wx.DefaultPosition, wx.DefaultSize, 0 )


        self.sizerRow2.Add( self.buttonZeroize, 0, wx.ALL, 5 )
        self.sizerRow2.Add( self.staticAirspeed, 0, wx.ALL, 5 )
        self.buttonZeroize.Bind( wx.EVT_BUTTON, self.on_click_zeroize)

        # Listen for messages
        self.parent.add_subscriber("VFR_HUD", self.on_vfrhud)
        return

    def on_click_zeroize(self, evt):
        # TODO implement airspeed sensor calibration
        return

    def on_vfrhud(self, msg):
        self.staticAirspeed.SetLabel("Airspeed: " + str(round(msg.airspeed,1)))

class ChecklistItem_Arm (ChecklistItemPanel):
    """
    Require the user to arm the motor to go green
    """
    # TODO defaults to showing that the motor is disarmed. I need to check during __init__() if the motor
    # TODO is actually disarmed.
    def __init__(self, parent):
        super(ChecklistItem_Arm, self).__init__(parent)

        self.armed = False

        # Override attributes of ChecklistItem
        self.staticStepName.SetLabel("Arm motor")

        # Build row 2
        self.buttonArm = wx.Button(self, wx.ID_ANY, u"Arm", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.staticArmStatus = wx.StaticText( self, wx.ID_ANY, u"Motor is currently DISARMED", wx.DefaultPosition, wx.DefaultSize, 0 )

        self.sizerRow2.Add( self.staticArmStatus, 0, wx.ALL, 5 )
        self.sizerRow2.Add( self.buttonArm, 0, wx.ALL, 5 )

        self.buttonArm.Bind( wx.EVT_BUTTON, self.on_click_arm)

        # Listen for messages
        self.parent.add_subscriber("STATUSTEXT", self.on_statustext)
        return

    def on_click_arm(self, evt):
        if self.armed == False:
            self.parent.master.arducopter_arm()
        # TODO Else, send disarm command
        return

    def on_statustext(self, msg):
        # DEBUG
        print(msg)

        if "Throttle armed" in msg.text:
            self.staticArmStatus.SetLabel("Motor is currently ARMED")
            self.buttonArm.SetLabel("DISARM")
            self.set_green()
        # TODO error handling if motor won't arm
        # TODO acknowledge motor disarming

class ChecklistItem_Voltage (ChecklistItemPanel):
    """
    This check verifies that the user has run an airspeed sensor calibration, and that the resting airspeed
    # does not exceed some threshold (i.e. 2 m/s).
    """
    def __init__(self, parent, args):
        super(ChecklistItem_Voltage, self).__init__(parent)

        # Override attributes of ChecklistItem
        self.staticStepName.SetLabel("Battery charged to acceptable voltage")

        self.green_voltage = args[0]
        self.yellow_voltage = args[1]

        # Build row 2
        self.staticVoltage = wx.StaticText( self, wx.ID_ANY, u"Voltage:       ", wx.DefaultPosition, wx.DefaultSize, 0 )
        voltagestr = u"Green > " + str(args[0]) + "V, Yellow > " + str(args[1]) + "V"
        self.staticVoltageLims = wx.StaticText( self, wx.ID_ANY, voltagestr, wx.DefaultPosition, wx.DefaultSize, 0 )

        self.sizerRow2.Add( self.staticVoltage, 0, wx.ALL, 5 )
        self.sizerRow2.Add( self.staticVoltageLims, 0, wx.ALL, 5 )

        # Listen for messages
        self.parent.add_subscriber("SYS_STATUS", self.on_sys_status)

        return


    def on_sys_status(self, msg):
        volts = round(msg.voltage_battery/1000,1)
        self.staticVoltage.SetLabel("Voltage: " + str(volts))
        if volts > self.green_voltage:
            self.set_green()
        elif volts > self.yellow_voltage:
            self.set_yellow()
        else:
            self.set_red()


class ChecklistItem_TrimCentered (ChecklistItemPanel):
    """
    Verifies that trim is within limits
    """
    def __init__(self, parent, args):
        super(ChecklistItem_TrimCentered, self).__init__(parent)

        # Override attributes of ChecklistItem
        self.staticStepName.SetLabel("Trim centered")

        self.roll_max_percent = args[0]
        self.pitch_max_percent = args[1]
        self.yaw_max_percent = args[2]

        # Build row 2
        trimstr = "Roll: " + "Pitch: " + "Yaw: "
        self.staticTrim = wx.StaticText( self, wx.ID_ANY, trimstr, wx.DefaultPosition, wx.DefaultSize, 0 )

        self.sizerRow2.Add( self.staticTrim, 0, wx.ALL, 5 )

        # Listen for messages
        self.parent.add_subscriber("RC_CHANNELS_RAW", self.on_sys_status)

        return


    def on_sys_status(self, msg):
        # TODO These should not be hard-coded, but should reflect the min/max
        # for that channel in the parameters
        chan1_percent = (msg.chan1_raw - 1000.0)/1000.0 * 100.0 - 50.0
        chan2_percent = (msg.chan2_raw - 1000.0)/1000.0 * 100.0 - 50.0
        chan4_percent = (msg.chan4_raw - 1000.0)/1000.0 * 100.0 - 50.0

        trimstr = "Roll: " + str(chan1_percent) + "%, Pitch: " + str(chan2_percent) + "%, Yaw: " + str(chan4_percent) + "%"
        self.staticTrim.SetLabelText(trimstr)

        self.set_green()
        if abs(chan1_percent) > self.roll_max_percent:
            self.set_red()
        if abs(chan2_percent) > self.pitch_max_percent:
            self.set_red()
        if abs(chan4_percent) > self.yaw_max_percent:
            self.set_red()

class ChecklistItem_ThrottleDown(ChecklistItemPanel):
    """
    Verifies the throttle is down at zero.
    """
    def __init__(self, parent, args):
        super(ChecklistItem_ThrottleDown, self).__init__(parent)

        # Override attributes of ChecklistItem
        self.staticStepName.SetLabel("Throttle down")

        self.throttle_max_percent = args[0]

        # Build row 2
        self.staticThrottle = wx.StaticText( self, wx.ID_ANY, "Throttle percent: ", wx.DefaultPosition, wx.DefaultSize, 0 )

        self.sizerRow2.Add( self.staticThrottle, 0, wx.ALL, 5 )

        # Listen for messages
        self.parent.add_subscriber("RC_CHANNELS_RAW", self.on_sys_status)

        return


    def on_sys_status(self, msg):
        chan3_percent = (msg.chan3_raw - 1000.0)/1000.0 * 100.0
        chan3_percent = max(0.0,chan3_percent)

        throttlestr = "Throttle: " + str(chan3_percent) + "%"
        self.staticThrottle.SetLabelText(throttlestr)

        self.set_green()
        if chan3_percent > self.throttle_max_percent:
            self.set_red()

#class ChecklistItem_FCManual (ChecklistItemPanel):

#class ChecklistItem_FCFBWA (ChecklistItemPanel):

class ChecklistItem_PositiveAirspeed (ChecklistItemPanel):
    """
    This check verifies that the user has blown in the pitot tube and registered
    a speed > arg0 m/s
    """
    def __init__(self, parent):
        super(ChecklistItem_PositiveAirspeed, self).__init__(parent)

        # Override attributes of ChecklistItem
        self.staticStepName.SetLabel("Blow in the pitot tube")

        # Build row 2
        self.staticAirspeed = wx.StaticText( self, wx.ID_ANY, u"Airspeed: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.buttonBegin = wx.Button(self, wx.ID_ANY, u"Begin", wx.DefaultPosition, wx.DefaultSize, 0 )


        self.sizerRow2.Add( self.buttonBegin, 0, wx.ALL, 5 )
        self.sizerRow2.Add( self.staticAirspeed, 0, wx.ALL, 5 )
        self.buttonBegin.Bind( wx.EVT_BUTTON, self.on_click_begin)

        # Listen for messages
        self.parent.add_subscriber("VFR_HUD", self.on_vfrhud)

        self.timing = False
        return

    def on_click_begin(self, evt):
        self.set_red()
        if self.timing == False:
            self.timing = True
            self.timer = wx.Timer(self, wx.ID_ANY)
            self.timer.Start(5000)
            self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
            self.buttonBegin.SetLabelText("Stop")
        else:
            self.timer.Stop()
            self.timing = False
            self.buttonBegin.SetLabelText("Begin")
        return

    def on_timer(self, evt):
        self.timer.Stop()
        self.timing = False
        self.buttonBegin.SetLabelText("Begin")

    def on_vfrhud(self, msg):
        airspeed = round(msg.airspeed,1)
        self.staticAirspeed.SetLabel("Airspeed: " + str(airspeed))
        if airspeed > 10.0 and self.timing == True:
            self.set_green()

class ChecklistItem_DemoServos(ChecklistItemPanel):
    """
    This demonstrates the servos in a pattern specified by the calling function.
    """
    def __init__(self, parent, args):
        super(ChecklistItem_DemoServos, self).__init__(parent)

        self.servo_steps = args

        # Override attributes of ChecklistItem
        self.staticStepName.SetLabel("Demo servos")

        # Build row 2
        self.buttonBegin = wx.Button(self, wx.ID_ANY, u"Begin", wx.DefaultPosition, wx.DefaultSize, 0 )


        self.sizerRow2.Add( self.buttonBegin, 0, wx.ALL, 5 )
        self.buttonBegin.Bind( wx.EVT_BUTTON, self.on_click_begin)

        self.timing = False

        return

    def on_click_begin(self, evt):

        self.set_red()
        if self.timing == False:
            self.servo_step = 0
            self.timing = True
            self.timer = wx.Timer(self, wx.ID_ANY)
            self.timer.Start(2000)
            self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
            self.buttonBegin.SetLabelText("Stop")
        else:
            self.timer.Stop()
            self.timing = False
            # TODO center servos
            self.buttonBegin.SetLabelText("Begin")
        return

    def on_timer(self, evt):

        # Advance to the next servo step
        self.servo_step = self.servo_step + 1

        # Check if we are at the end
        if self.servo_step >= len(self.servo_steps):
            self.timer.Stop()
            self.timing = False
            self.buttonBegin.SetLabelText("Begin")
            return

        # Get the instructions for this step
        current_step = self.servo_steps[self.servo_step]
        print("Demo servo: " + current_step)
        self.parent.master.mav.command_long_send(self.parent.master.target_system,
                                                   self.parent.master.target_component,
                                                   mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
                                                   current_step[0], current_step[1],
                                                   0, 0, 0, 0, 0)





class ChecklistItem_ParameterDiff (ChecklistItemPanel):
    """
    This demonstrates the servos in a pattern specified by the calling function.
    """
    def __init__(self, parent):
        super(ChecklistItem_ParameterDiff, self).__init__(parent)

        # Override attributes of ChecklistItem
        self.staticStepName.SetLabel("Validate Parameters")

        # Build row 2
        self.buttonBegin = wx.Button(self, wx.ID_ANY, u"Begin", wx.DefaultPosition, wx.DefaultSize, 0 )


        self.sizerRow2.Add( self.buttonBegin, 0, wx.ALL, 5 )
        self.buttonBegin.Bind( wx.EVT_BUTTON, self.on_click_begin)

        self.mav_param = {}
        self.mav_param_set = set()

        return

    def on_click_begin(self, evt):

        print("Starting")
        self.set_red()
        self.parent.master.param_fetch_all()

        self.parent.add_subscriber("PARAM_VALUE", self.on_param)

        return

    def on_param(self, m):
        # This code taken from mavproxy_param.py handle_mavlink_packet()
        param_id = "%.16s" % m.param_id
        # Note: the xml specifies param_index is a uint16, so -1 in that field will show as 65535
        # We accept both -1 and 65535 as 'unknown index' to future proof us against someday having that
        # xml fixed.
        if m.param_index != -1 and m.param_index != 65535 and m.param_index not in self.mav_param_set:
            added_new_parameter = True
            self.mav_param_set.add(m.param_index)
        else:
            added_new_parameter = False
        if m.param_count != -1:
            self.mav_param_count = m.param_count
        self.mav_param[str(param_id)] = m.param_value
        if self.fetch_one > 0:
            self.fetch_one -= 1
            print("%s = %f" % (param_id, m.param_value))
        if added_new_parameter and len(self.mav_param_set) == m.param_count:
            print("Received %u parameters" % m.param_count)
            if self.logdir != None:
                self.mav_param.save(os.path.join(self.logdir, self.parm_file), '*', verbose=True)

#class ChecklistItem_ParameterBounds (ChecklistItemPanel):

#class ChecklistItem_FlightPlanDiff (ChecklistItemPanel):

#class ChecklistItem_ParameterValidate (ChecklistItemPanel):

#class ChecklistItem_Endurance (ChecklistItemPanel):

class ChecklistItem_GPSHealth (ChecklistItemPanel):
    """
    This check verifies that the GPS is healthy
    """
    # TODO Check to see what Mission Planner checks
    def __init__(self, parent):
        super(ChecklistItem_GPSHealth, self).__init__(parent)

        # Override attributes of ChecklistItem
        self.staticStepName.SetLabel("GPS Healthy")


        # Build row 2

        # Listen for messages
        self.parent.add_subscriber("GPS_RAW_INT", self.on_sys_status)

        return


    def on_sys_status(self, msg):
        status = STATUS_GREEN

        # Satellite count
        if msg.satellites_visible < 4:
            status = STATUS_RED

        # Horizontal hdop
        # TODO I have no idea what this value should be
        if msg.eph < 100:
            status = STATUS_RED

        # Vertical hdop
        # TODO Check value
        if msg.epv < 100:
            status = STATUS_RED

        # Fix type
        if msg.fix_type < 3:
            status = STATUS_RED

        if status == STATUS_RED:
            self.set_red()
        elif status == STATUS_GREEN:
            self.set_green()


#class ChecklistItem_BaroHealth (ChecklistItemPanel):

#class ChecklistItem_CompassHealth (ChecklistItemPanel):
