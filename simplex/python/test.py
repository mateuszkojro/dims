import unittest
import simplex as my
import numpy as np
import time


class TestTableau(unittest.TestCase):

    def test_join(self):
        """
        A = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 1]])
        b = np.array([0, 20, 20, 20])
        c = np.array([-10, -12, -12])
        s = my.Simplex(A, b, c)
        tab = s.create_tab()
        tab_test = []
        self.assertTrue(np.array_equiv(tab, tab_test))
        """
        pass

    def test_split(self):
        pass

    def test_all(self):
        pass


class TestSimplexExmpl1(unittest.TestCase):

    def test_iter1(self):
        A = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 1]])
        b = np.array([0, 20, 20, 20])
        c = np.array([-10, -12, -12])
        test_itr_1 = np.array([
            [120.0,	-4.0,	0.0,	0.0,	6.0,	0.0,	0.0	],
            [10.0,	0.5,	1.0,	1.0,	0.5,	0.0,	0.0	],
            [10.0,	1.5,	0.0,	1.0,	-0.5,	1.0,	0.0	],
            [0.0,	1.0,	0.0,	-1.0,	-1.0,	0.0,	1.0	]
        ])
        s = my.Simplex(A, b, c, "MIN")
        pass1 = s.optimize()
        self.assertTrue(np.array_equiv(pass1, test_itr_1))

    def test_iter2(self):
        A = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 1]])
        b = np.array([0, 20, 20, 20])
        c = np.array([-10, -12, -12])

        test_itr_2 = np.array([
            [120.0, 0.0, 0.0, -4.0, 2.0, 0.0, 4.0],
            [10.0, 0.0, 1.0, 1.5, 1.0, 0.0, -0.5],
            [10.0, 0.0, 0.0, 2.5, 1.0, 1.0, -1.5],
            [0.0, 1.0, 0.0, -1.0, -1.0,	0.0, 1.0],
        ])
        s = my.Simplex(A, b, c, "MIN")
        s.optimize()
        pass2 = s.optimize()
        self.assertTrue(np.array_equiv(pass2, test_itr_2))

    def test_result(self):
        A = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 1]])
        b = np.array([0, 20, 20, 20])
        c = np.array([-10, -12, -12])
        s = my.Simplex(A, b, c, "MIN")
        result = s.simplex(4)
        self.assertTrue(np.array_equiv(result, np.array([4., 4., 4.])))

    def test_time(self):
        A = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 1]])
        b = np.array([0, 20, 20, 20])
        c = np.array([-10, -12, -12])
        s = my.Simplex(A, b, c, "MIN")
        start = time.perf_counter()
        _ = s.simplex(4)
        stop = time.perf_counter()
        self.assertGreater(0.005, stop - start)


if __name__ == '__main__':
    unittest.main()
