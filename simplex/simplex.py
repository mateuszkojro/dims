import numpy as np


class Simplex:

    def __init__(self, A, b, c):
        self.A = np.array(A, dtype='float64')
        # we could append an identity matrix there
        self.A = np.hstack((self.A, [[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
        self.b = np.array(b, dtype='float64')
        self.c = np.array(c, dtype='float64')
        self.c = np.hstack((self.c, [[0, 0, 0]]))

    def optimize(self):
        min_addr = np.argmin(self.c)

        size_y = self.A.shape[0]
        min = (256, 0)  # max val, addr
        for i in range(size_y):
            a_val = self.A[i, min_addr]
            if a_val <= 0:
                print("helllo")
                continue
            cur_ratio = self.b[i + 1] / a_val
            print("i", i, "col", min_addr, "b[i]", self.b[i + 1],
                  "a_val", a_val, "row", i, "ratio", cur_ratio)
            if cur_ratio < min[0]:
                min = (cur_ratio, i)

        # now we need to operate on the whole tablou so we need to create it

        tab = np.vstack((self.c, self.A))  # create_tableau()
        self.b = self.b.reshape((4, 1))
        tab = np.hstack((self.b, tab))

        row = min[1] + 1
        col = min_addr + 1
        pivot_el = tab[row, col]

        print(tab)
        print()

        # normalize the values in pivot row
        tab[row, :] = tab[row, :] / tab[row, col]

        # pivot rows of A
        for i in range(4):
            if i != row:
                mult = tab[i, col] / tab[row, col]
                tab[i, :] = tab[i, :] - mult * tab[row, :]

        print(tab)
        print("Pivot col: ", col)
        print("pivot row: ", row)
        print(pivot_el)

        self.A = tab[1:, 1:]
        self.b = tab[:, 0]
        self.c = tab[0, 1:]

        return tab

    def simplex(self, depth):
        result = []
        while(depth):
            result = self.optimize()
            depth -= 1
        return (result[1:, 0].T)
