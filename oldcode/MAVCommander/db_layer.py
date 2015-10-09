# TODO why is create_mav_type not persisting?

# This contains the database layer for MAVCommander. The application creates a single instance of this
# class, which opens a DB connection and creates the DB if necessary.

import sqlite3, os
from uuid import uuid4

# References code from: https://pymotw.com/2/sqlite3/

db_filename = 'mavcommander.db'
schema_filename = 'mavcommander_schema.sql'

class MAVCommanderDB:
    def __init__(self):
        db_is_new = not os.path.exists(db_filename)

        with sqlite3.connect(db_filename) as conn:
            if db_is_new:
                print 'Creating schema'
                with open(schema_filename, 'rt') as f:
                    schema = f.read()
                    conn.executescript(schema)

            else:
                print("db exists")


    def test_db(self):

        # Create a mavtype record
        mav_type_record = MAVTypeRecord("FX61", "Flying wing", "test.txt", "test.param" )
        self.create_mav_type(mav_type_record)
        mav_type_readback = self.get_mav(mav_type_record.uuid)


        # Readback
        mav_type_record.name = "FX61_revised"
        self.update_mav_type(mav_type_record)
        records = self.get_mav_types()
        for record in records:
            print record.name, record.description
        self.delete_mav_type(mav_type_record)

        #records = self.get_mav_types()
        #for record in records:
        #    print record.name

    def get_mav_types(self):
        """
        Returns a list of mav_type records

        :return A list of MAVTypeRecord objects
        """
        with sqlite3.connect(db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT uuid, name, description, checklistfile, paramfile FROM mav_type")
            records = []
            for row in cursor.fetchall():
                uuid, name, description, checklistfile, paramfile = row
                mavrecord = MAVTypeRecord(name, description, checklistfile, paramfile, uuid)
                records.append(mavrecord)
        return records

    def get_mav_type(self, uuid):
        str = 'SELECT name, description, checklistfile, paramfile FROM mav_type WHERE uuid="' + uuid + '"'
        with sqlite3.connect(db_filename) as conn:
            cursor = self.conn.cursor()
            cursor.execute(str)
            row = cursor.fetchone()
            name, description, checklistfile, paramfile = row
            mavrecord = MAVTypeRecord(name, description, checklistfile, paramfile, uuid)
        return mavrecord

    def create_mav_type(self, record):
        """
        Add a mav_type record

        :param record - A MavTypeRecord object
        """
        str = 'INSERT INTO mav_type (uuid, name, description, checklistfile, paramfile) VALUES ("' + \
            record.uuid + '","' + \
            record.name + '","' + \
            record.description + '","' + \
            record.checklistfile + '","' + \
            record.paramfile + '")'
        #print(str)
        with sqlite3.connect(db_filename) as self.conn:
            self.conn.execute(str)

    def delete_mav_type(self, record):
        """
        Delete a mav_type record

        :param record - The MAVType Record to delete
        """

        str = 'DELETE FROM mav_type WHERE uuid = "' + record.uuid + '"'
        with sqlite3.connect(db_filename) as self.conn:
            self.conn.execute(str)

    def update_mav_type(self, record):
         str = 'UPDATE mav_type SET name = "' + record.name + '", ' + \
             'description = "' + record.description + '", ' + \
             'checklistfile = "' + record.checklistfile + '", ' + \
             'paramfile = "' + record.paramfile + '"' + \
             'WHERE uuid = "' + record.uuid + '"'
         with sqlite3.connect(db_filename) as self.conn:
            self.conn.execute(str)


    def get_mavs(self):
        with sqlite3.connect(db_filename) as conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT uuid, name, mav_type, sys_id, notes FROM mav")
            records = []
            for row in cursor.fetchall():
                uuid, name, mav_type, sys_id, notes = row
                mavrecord = MAVRecord(name, mav_type, sys_id, notes, uuid)
                records.append(mavrecord)
        return records

    def get_mav(self, id):
        # TODO
        return

    def create_mav(self, record):
        """
        Add a mav record

        :param record - A Mav object
        """
        str = 'INSERT INTO mav (uuid, name, mav_type, sys_id, notes) VALUES ("' + \
            record.uuid + '","' + \
            record.name + '","' + \
            record.mav_type + '","' + \
            record.sys_id + '","' + \
            record.notes + '")'
        #print(str)
        with sqlite3.connect(db_filename) as self.conn:
            self.conn.execute(str)


    def close(self):
        return

class MAVTypeRecord:
    """
    This class wraps up a 'mav_type' record in the database
    """
    def __init__(self):
        self.uuid = str(uuid4())
        self.name = ""
        self.description = ""
        self.checklistfile = ""
        self.paramfile = ""

    def __init__(self, name, description, checklistfile, paramfile, uuid=None):
        if uuid is None:
            self.uuid = str(uuid4())
        else:
            self.uuid = uuid
        self.name = name
        self.description = description
        self.checklistfile = checklistfile
        self.paramfile = paramfile

class MAVRecord:
    """
    This class wraps up a 'mav' record in the database
    """
    def __init__(self):
        self.uuid = str(uuid4())
        self.name = ""
        self.description = ""
        self.mav_type = ""
        self.sys_id = -1
        self.notes = ""

    def __init__(self, name, mav_type, sys_id, notes, uuid=None):
        if uuid is None:
            self.uuid = str(uuid4())
        else:
            self.uuid = uuid
        self.name = name
        self.mav_type = mav_type
        self.sys_id = sys_id
        self.notes = notes

class LogRecord:
    """
    This class wraps up a 'log' record in the database
    """

    def __init__(self):
        self.uuid = uuid4()
        self.mav_id = ""
        self.weight = ""
        self.cg = ""
        self.notes = ""
        self.file = ""
