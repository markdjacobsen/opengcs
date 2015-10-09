# Unit tests for database layer

import unittest
from db_layer import *


class TestMavCommanderDB(unittest.TestCase):

    def test_create_mav_type(self):
        db = MAVCommanderDB()
        # TODO rebuild database

        # Create a mavtype record
        mav_type_new = MAVTypeRecord("FX61", "Flying wing", "test.txt", "test.param" )
        db.create_mav_type(mav_type_new)


        # Readback the record
        mav_type_readback = db.get_mav_type(mav_type_new.uuid)

        # Ensure they are the same
        self.assertEqual(mav_type_readback.uuid, mav_type_new.uuid)
        self.assertEqual(mav_type_readback.name, mav_type_new.name)
        self.assertEqual(mav_type_readback.description, mav_type_new.description)
        self.assertEqual(mav_type_readback.checklistfile, mav_type_new.checklistfile)
        self.assertEqual(mav_type_readback.paramfile, mav_type_new.paramfile)

    def test_get_mav_types(self):
        db = MAVCommanderDB()

        mav_types = db.get_mav_types()

        self.assertEqual(mav_types[0].name, "FX61")
        self.assertEqual(mav_types[0].description, "Flying wing")
        self.assertEqual(mav_types[0].checklistfile, "test.txt")
        self.assertEqual(mav_types[0].paramfile, "test.param")

    def test_update_mav_types(self):
        db = MAVCommanderDB()
        #mav_type_old = db.v



if __name__ == '__main__':
    unittest.main()