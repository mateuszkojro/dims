import numpy as np


class Simplex:

    iter = 0

    def __init__(self, A, b, c):
        self.A = np.array(A, dtype='float')
        self.b = np.array(b, dtype='float')
        self.c = np.array(c, dtype='float')

    def optimize(self):
        min_addr = np.argmin(self.c)
        size_x = self.A.shape[0]
        size_y = self.A.shape[1]
        min = (256, 0)  # max val, addr
        for i in range(size_y):
            a_val = self.A[i, min_addr]
            if a_val == 0:
                continue
            cur_ratio = self.b[i] / a_val
            if cur_ratio < min[0]:
                min = (cur_ratio, i)
        pivot_el = self.A[min[1], min_addr]

        # now we need to operate on the whole tablou so we need to create it
        r = min[1] + 1
        n = min_addr + 1

        tab = np.vstack((self.c, self.A))  # create_tableau()
        tab = np.hstack((tab, [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]))
        self.b = self.b.reshape((4, 1))
        tab = np.hstack((self.b, tab))

        print(tab)
        print()

        # normalize the values in pivot row
        tab[r, :] = tab[r, :] / tab[r, n]

        # pivot rows of A
        for i in range(4):
            if i != r:
                mult = tab[i, n] / tab[r, n]
                tab[i, :] = tab[i, :] - mult * tab[r, :]

        # print(tab)
        # print("Pivot col: ", n)
        # print("pivot row: ", r)
        # print(pivot_el)

        self.A = tab[1:, 1:]
        self.b = tab[:, 0]
        self.c = tab[0, 1:]

        print(self.A)
        print(self.b)
        print(self.c)

        return tab
