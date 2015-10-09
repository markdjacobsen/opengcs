"""
This receives incoming messages from the MAV on a separate thread and notifies observers
of new messages.
"""

import sys
from pymavlink import mavutil
import threading


__author__ = 'markjacobsen'

class MAVDispatch:
    def __init__(self):
        self._observers = []
        return

    def connect(self,port,baud):
        print("Connecting to " + port + " at " + str(baud) + "baud")
        self.master = mavutil.mavlink_connection(port, baud=baud)
        self.wait_heartbeat()
        thread = threading.Thread(target=self.process_messages)
        thread.setDaemon(True)
        thread.start()
        return self.master

    def wait_heartbeat(self):
        '''wait for a heartbeat so we know the target system IDs'''
        print("Waiting for APM heartbeat")
        msg = self.master.recv_match(type='HEARTBEAT', blocking=True)
        print("Heartbeat from APM (system %u component %u)" % (self.master.target_system, self.master.target_system))

    def process_messages(self):
         while True:
            msg = self.master.recv_match(blocking=True)
            if not msg:
                return
            if msg.get_type() == "BAD_DATA":
                if mavutil.all_printable(msg.data):
                    sys.stdout.write(msg.data)
                    sys.stdout.flush()
            else:
                for observer in self._observers:
                    observer(msg)

    def add_observer(self,observer):
        self._observers.append(observer)

    def remove_observer(self,observer):
        self._observers.remove(observer)