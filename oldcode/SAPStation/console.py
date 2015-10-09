"""
console.py
Author: Mark Jacobsen
Last Update: 6 Dec 2014
Status: in progress

This replaces print() for use within SAP Station. It is customizable, so we can switch on/off different types of
logging at different types, and it can log to multiple outputs like a text console, files, or a GUI console.
Future plans include allowing subscribers, i.e. for GUI updating.
"""
__author__ = 'markjacobsen'
import config



class Console:

    def __init__(self,logfile,log_screen,log_file):
        self.logfile = logfile
        self.log_screen = log_screen
        self.log_file = log_file
        return

    def log(self,msg):

        if self.log_screen == True:
            print(msg)
        if self.log_file == True:
            f = open(self.logfile,'w')
            f.write(msg)
            f.write('\n')
            f.close()
            # TODO gui logging
        return

    def error(self,msg):
        if self.log_screen == True:
            print(msg)
        if self.log_file == True:
            f = open(self.logfile,'w')
            f.write(msg)
            f.write('\n')
            f.close()
        # TODO gui logging
        return

console = Console(config.logfile, config.log_screen, config.log_file)