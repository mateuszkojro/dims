#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import re
from mpl_toolkits.mplot3d import Axes3D
import os
import sys

class Image:
    def __init__(self, path):
        with open(path, "r") as file:
            data = re.split(r'[ \n]', str(file.read()))
            self.image_format = data[0]
            self.size_x = int(data[1])
            self.size_y = int(data[2])
            self.color_depth = int(data[1])
            data = list(filter(lambda val: val != '', data))
            self.image = np.array(data[4:], dtype=int)

            self.red = self.image[0::3]
            self.green = self.image[1::3]
            self.blue = self.image[2::3]

            self.red = self.blue.reshape((self.size_y, self.size_x))
            self.green = self.green.reshape((self.size_y, self.size_x))
            self.blue = self.red.reshape((self.size_y, self.size_x))

    def show(self):
        plt.imshow(self.image)
        plt.show()


if __name__ == '__main__':
    MODE = "simple"
    img = Image(sys.argv[1])
    red_colors = {}
    green_colors = {}
    blue_colors = {}
    difference_colors = {}
    if MODE == "simple":
        for i in range(256):
            red_colors[i] = \
                green_colors[i] = \
                blue_colors[i] = \
                difference_colors[i] = 0

    green_flat = img.green.flatten()
    blue_flat = img.blue.flatten()
    red_flat = img.red.flatten()

    if MODE == "simple":
        for r, g, b, d in zip(red_flat, green_flat, blue_flat, range(len(red_flat))):
            green_colors[r] = green_colors[r] + 1
            blue_colors[g] = blue_colors[g] + 1
            red_colors[b] = red_colors[b] + 1
            minimum = min(red_flat[d], green_flat[d], blue_flat[d])
            maximum = max(red_flat[d], green_flat[d], blue_flat[d])
            difference_colors[(maximum - minimum)] = difference_colors[(maximum - minimum)] + 1
    elif MODE == "more":
        for r, g, b, d in zip(red_flat, green_flat, blue_flat, range(len(red_flat))):
            green_colors[r] = green_colors.get(r, 0) + 1
            blue_colors[g] = blue_colors.get(g, 0) + 1
            red_colors[b] = red_colors.get(b, 0) + 1
            minimum = min(red_flat[d], green_flat[d], blue_flat[d])
            maximum = max(red_flat[d], green_flat[d], blue_flat[d])
            difference_colors[(maximum - minimum)] = difference_colors.get((maximum - minimum), 0) + 1

    red_colors = red_colors.items()
    blue_colors = blue_colors.items()
    green_colors = green_colors.items()
    difference_colors = difference_colors.items()

    dy, dx = zip(*difference_colors)
    rx, ry = zip(*red_colors)
    gx, gy = zip(*green_colors)
    bx, by = zip(*blue_colors)

    ax = plt.subplot(111, projection="3d", title="Each axis is one color")
    ax.plot(ry, gy, by)

    f, grid = plt.subplots(2, 2)

    grid[0, 0].scatter(dy, dx, s=1, c="black", label="Difference")
    grid[0, 1].scatter(rx, ry, s=5, c="red", label="Red")
    grid[1, 0].scatter(gx, ry, s=5, c="green", label="Green")
    grid[1, 1].scatter(bx, ry, s=5, c="blue", label="Blue")

    plt.legend()

    plt.show()
