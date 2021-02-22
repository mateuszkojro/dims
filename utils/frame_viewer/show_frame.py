import sys
import numpy as np
import matplotlib.pyplot as plt


def read_file(path):
    with open(path, "rb") as f:
        data = f.read()
    return list(data)


def get_img(img):

    img = np.array(img[0::2])
    img = img.reshape((1080, 1920))
    return img


def show_img(path):
    img = get_img(read_file(path))

    plt.tight_layout(pad=-1)
    plt.imshow(img)
    plt.show()


def show_diff(path1, path2):
    img1 = get_img(read_file(path2))
    img2 = get_img(read_file(path2))

    result = img2 - img1
    result = np.absolute(result)

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


if __name__ == '__main__':

    if len(sys.argv) == 2:
        show_img(sys.argv[1])
    elif len(sys.argv) == 3:
        show_diff(sys.argv[1], sys.argv[2])
    else:
        print("If you want to look at a single frame give path to it \n"
              "if you want compare 2 images give to paths ")

    # result = np.sqrt(result)
    # avg = np.average(result)

    # plt.figure(figsize=(256, 256))
