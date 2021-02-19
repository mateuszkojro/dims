import sys
import numpy as np
import matplotlib.pyplot as plt
import os


def read_file(path):
    with open(path, "rb") as f:
        data = f.read()
    return list(data)


def get_img(img):

    img = np.array(img[0::2])
    img = img.reshape((1080, 1920))
    return img


if __name__ == '__main__':

    img1 = get_img(read_file(sys.argv[1]))
    img2 = get_img(read_file(sys.argv[2]))

    img1 = np.square(img1)
    img2 = np.square(img2)

    result = img2 - img1
    result = np.absolute(result)
    # result = np.sqrt(result)
    # avg = np.average(result)

    home_dir = "HOOOME"
    if home_dir in os.environ:
        print(home_dir)
    else:
        print("Or not...")
    # plt.figure(figsize=(256, 256))
    f, grid = plt.subplots(2, 2)
    f.tight_layout(pad=-1)
    grid[0, 0].imshow(img1).set_cmap('hot')
    grid[0, 1].imshow(img2).set_cmap('hot')
    grid[1, 0].imshow(result).set_cmap('hot')

    grid[0, 0].axis('off')
    grid[0, 1].axis('off')
    grid[1, 0].axis('off')
    grid[1, 1].axis('off')

    plt.show()
