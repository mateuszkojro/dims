'''
Module to leran more about simplex method
'''
import logging as log
import numpy as np


class Simplex:
    '''
    Eaasiest possible simplex impl based on:
    https://mattmolter.medium.com/creating-a-linear-program-solver-by-implementing-the-simplex-method-in-python-with-numpy-22f4cbb9b6db
    '''

    def __init__(self, A, b, c):
        self.A = np.array(A, dtype='float64')
        self.size = self.A.shape[0]
        self.A = np.hstack((self.A, np.identity(self.size)))
        self.b = np.array(b, dtype='float64')
        self.c = np.array(c, dtype='float64')
        self.c = np.hstack(
            (self.c, np.zeros(self.size)))
        self.result = None

    def optimize(self):
        """
        run one iteration of the simplex algorithm -
        find a pivot element and pivot around it
        """
        # find the pivot column
        min_addr = np.argmin(self.c)

        # findint the pivot row
        size_y = self.A.shape[0]
        min_ratio = (256, 0)  # max val, addr
        for i in range(size_y):
            a_val = self.A[i, min_addr]
            if a_val > 0:
                cur_ratio = self.b[i + 1] / a_val
                if cur_ratio < min_ratio[0]:
                    min_ratio = (cur_ratio, i)

        # now we need to operate on the whole tablou so we need to create it
        tab = self.create_tab()

        row = min_ratio[1] + 1
        col = min_addr + 1
        _ = tab[row, col]  # pivot el

        # normalize the values in pivot row
        tab[row, :] = tab[row, :] / tab[row, col]

        # pivot other rows of A
        # i am not sure tego self.size tutaj
        for i in range(self.size + 1):
            if i != row:
                mult = tab[i, col] / tab[row, col]
                tab[i, :] = tab[i, :] - mult * tab[row, :]

        # Destructure the tableau back to difrent parts
        self.A, self.b, self.c = self.load_tab(tab)

        log.info("\n Iteration complete\n Table: \n %s", tab)

        return tab

    def create_tab(self):
        """
        Creates simplex "tablou" from current state
        """
        tab = np.vstack((self.c, self.A))
        self.b = self.b.reshape((self.size + 1, 1))
        tab = np.hstack((self.b, tab))
        return tab

    def load_tab(self, tab):
        """
        Destructures tablou into matricies
        """
        self.A = tab[1:, 1:]
        self.b = tab[:, 0]
        self.c = tab[0, 1:]
        return self.A, self.b, self.c

    def simplex(self, depth):
        """
        Do n=depth iterations of the simplex algorithm
        """
        while depth:
            self.result = self.optimize()[1:, 0].T
            depth -= 1
        return self.result

    def apply_func(self, arr):
        """
        Use results to calculate value
        """
        func = self.result.flatten()
        arr = arr.flatten()
        result = 0
        # @TODO thats definetly to be fixed
        for i in range(4):
            result += func[i] * arr[i]
        return abs(result)
