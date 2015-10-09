__author__ = 'markjacobsen'

import os
import config

def get_all_aircraft():
    # This returns subdirectories in the aircraft directory in the format Aircraft/Bixler
    all_aircraft = [x[0] for x in os.walk(config.aircraft_directory)]
    all_aircraft.remove(all_aircraft[0])

    # This only keeps the portion after the slash
    clean_aircraft = []
    for x in all_aircraft:
        clean_aircraft.append(x.split('/')[1])

    return clean_aircraft