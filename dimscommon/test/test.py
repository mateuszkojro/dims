import unittest
import dimscommon.datacollection as dc


class TestDatacollection(unittest.TestCase):
    def test_simple_create_connection(self):
        conn = dc.DataCollection("Test collection", [], [], [])
        self.assertIsNotNone(conn.sql_connection)
        self.assertIsInstance(conn.data_collection_id, int)

    def test_create_connection_with_params(self):
        conn = dc.DataCollection("Test collection", ["sqr_size", "min_point"], ["100x100px", "4"], [])
        self.assertIsNotNone(conn.sql_connection)
        self.assertIsInstance(conn.data_collection_id, int)


class TestTrigger(unittest.TestCase):
    pass


if __name__ == '__main__':
    greating = "Running tests"
    print("=" * len(greating))
    print(greating)
    print("=" * len(greating))

    unittest.main()