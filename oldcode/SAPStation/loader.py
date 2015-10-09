"""
This contains all the backend logic for the SAP Loader. The application creates
a single SAPLoader object, then adds loader_action objects such as waypoints, parameters, etc.
This class ensures that each loader_action can communicate with the MAV and runs
sequentially through the actions, returning results.
"""

__author__ = 'markjacobsen'

from loader_actions import *

import MAVDispatch

import loader_actions

class SAPLoader:
    def __init__(self):
        # The one and only message dispatcher in SAPStation is owned by this object
        self.dispatch = MAVDispatch.MAVDispatch()

        # These are the actions that the loader will execute
        self.action_wp = loader_actions.Action_WP()
        self.action_params = loader_actions.Action_Params()
        self.action_auto = loader_actions.Action_Auto()
        self.action_arm = loader_actions.Action_Arm()

        self.actions = []
        self.actions.append(self.action_wp)
        self.actions.append(self.action_params)
        self.actions.append(self.action_auto)
        self.actions.append(self.action_arm)


    def connect(self,port,baud):
        """
        Initializes the MAV link using the dispatch object, then gives
        each action a reference to master.

        :param port: COM port
        :param baud: baud rate (115200 USB, 57600 3D Radio)
        """
        self.dispatch.connect(port,baud)

        for action in self.actions:
            action.connect(self.dispatch.master)

    def start_actions(self):
        """
        Start running the loader by executing the first action in the queue.
        """
        self.current_action = 0
        self.do_action(self.current_action)

    def do_action(self,action_number):
        """
        Execute a single action. Configures that message to receive incoming
        MAV messages, and configures the loader to monitor for when the
        action is complete.

        :param action_number:
        :return:
        """
        action = self.actions[action_number]

        #
        self.dispatch.add_observer(action.process_message)
        action.add_observer(self.on_action_finished)

        action.begin()

    def on_action_finished(self,status):
        old_action = self.actions[self.current_action]
        console.log(0,"Action " + str(self.current_action) + " finished with status: " + str(status))

        # Disconnect the old action
        self.dispatch.remove_observer(old_action.process_message)
        old_action.remove_observer(self.on_action_finished)

        # If this was the last action, then we're done
        if self.current_action == len(self.actions) - 1:
            print("All actions completed")
            return

        # Otherwise, run the next action
        self.current_action = self.current_action + 1
        self.do_action(self.current_action)

        return