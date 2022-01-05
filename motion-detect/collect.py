import FileCrawler
import os
import numpy as np
import sys


def collect(path, extension):
    nodes = os.listdir(path)
    array = np.array([])
    for node in nodes:
        filename = output_folder + "/" + node
        if FileCrawler.get_ext(node) == extension:
            try:
                np.append(array, np.load(filename, allow_pickle=True)[0])
            except Exception:
                print(filename)
    return array


if __name__ == "__main__":
    output_folder = sys.argv[1]
    np.save("db",
            collect(output_folder + "/", ".npy"))
