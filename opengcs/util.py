"""
Contains various utility functions
"""

import sys, serial, glob

def serial_ports():
    """Lists all available serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """

    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            #s = serial.Serial(port)
            #s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def import_package(name):
    """Given a package name like 'foo.bar.quux', imports the package
    and returns the desired module.
    """
    # Code taken directly from MAVProxy by Andrew Tridgell
    #import zipimport
    try:
        mod = __import__(name)
    except ImportError:
        print("ImportError: " + name)
        #clear_zipimport_cache()
        #mod = __import__(name)

    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
