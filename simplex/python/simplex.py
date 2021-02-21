import numpy as np


class Simplex:

    def __init__(self, A, b, c):
        self.A = np.array(A, dtype='float64')
        # we could append an identity matrix there
        self.size = self.A.shape[0]
        self.A = np.hstack((self.A, np.identity(self.size)))
        self.b = np.array(b, dtype='float64')
        self.c = np.array(c, dtype='float64')
        self.c = np.hstack(
            (self.c, np.zeros(self.size)))
        self.result = None

    def optimize(self):
        min_addr = np.argmin(self.c)

        size_y = self.A.shape[0]
        min = (256, 0)  # max val, addr
        for i in range(size_y):
            a_val = self.A[i, min_addr]
            if a_val <= 0:
                continue
            cur_ratio = self.b[i + 1] / a_val
            # print("i", i, "col", min_addr, "b[i]", self.b[i + 1],
            #     "a_val", a_val, "row", i, "ratio", cur_ratio)
            if cur_ratio < min[0]:
                min = (cur_ratio, i)

        # now we need to operate on the whole tablou so we need to create it
        tab = self.create_tab()

        row = min[1] + 1
        col = min_addr + 1
        # pivot_el = tab[row, col]

        # normalize the values in pivot row
        tab[row, :] = tab[row, :] / tab[row, col]

        # pivot rows of A
        # i am not sure tego self.size tutaj
        for i in range(self.size + 1):
            if i != row:
                mult = tab[i, col] / tab[row, col]
                tab[i, :] = tab[i, :] - mult * tab[row, :]

        # print(tab)
        # print("Pivot col: ", col)
        # print("pivot row: ", row)
        # print(pivot_el)

        # Destructure the tableau back to difrent parts
        self.A, self.b, self.c = self.load_tab(tab)

        return tab

    def create_tab(self):
        tab = np.vstack((self.c, self.A))
        self.b = self.b.reshape((self.size + 1, 1))
        tab = np.hstack((self.b, tab))
        return tab

    def load_tab(self, tab):
        self.A = tab[1:, 1:]
        self.b = tab[:, 0]
        self.c = tab[0, 1:]
        return self.A, self.b, self.c

    def simplex(self, depth):
        while(depth):
            self.result = self.optimize()[1:, 0].T
            depth -= 1
        return (self.result)

    def apply_func(self, arr):
        func = self.result.flatten()
        arr = arr.flatten()
        print(self.result)
        sum = 0
        for i in range(4):
            print(func[i], arr[i])
            sum += func[i] * arr[i]
        return abs(sum)
