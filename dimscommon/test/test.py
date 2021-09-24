import unittest
import dimscommon.datacollection as dc
from dimscommon.trigger import Trigger, create_trigger_flat


class TestDatacollection(unittest.TestCase):
    def test_simple_create_connection(self):
        conn = dc.DataCollection("Test collection", [], [], [])
        self.assertIsNotNone(conn.sql_connection)
        self.assertIsInstance(conn.data_collection_id, int)

    def test_create_connection_with_params(self):
        conn = dc.DataCollection("Test collection", ["sqr_size", "min_point"],
                                 ["100x100px", "4"], [])
        self.assertIsNotNone(conn.sql_connection)
        self.assertIsInstance(conn.data_collection_id, int)

    def test_add_triggers_without_additional_props(self):
        conn = dc.DataCollection("Test collection", [], [], [])
        conn.upload_trigger(
            create_trigger_flat(file="filename",
                                start_frame=1,
                                end_frame=2,
                                box_min_x=1,
                                box_min_y=2,
                                box_max_x=3,
                                box_max_y=4,
                                additional_data=None))

    def test_add_trigger_with_props(self):
        conn = dc.DataCollection("Test collection", [], [],
                                 ["speed", "linearity"])
        conn.upload_trigger(
            create_trigger_flat(file="filename",
                                start_frame=1,
                                end_frame=2,
                                box_min_x=1,
                                box_min_y=2,
                                box_max_x=3,
                                box_max_y=4,
                                additional_data={
                                    "speed": 12,
                                    "linearity": 0.9
                                }))


class TestTrigger(unittest.TestCase):
    pass


if __name__ == '__main__':
    greating = "Running tests"
    print("=" * len(greating))
    print(greating)
    print("=" * len(greating))

    unittest.main()