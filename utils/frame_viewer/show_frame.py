import sys
import numpy as np
import matplotlib.pyplot as plt


def read_file(path):
    with open(path, "rb") as f:
        data = f.read()
    return list(data)


def get_img(img, resolution):

    img = np.array(img[0::2])
    try:
        img = img.reshape(resolution)
    except:
        print(f"Could not convert image to set resolution {resolution}")
        exit(1)
    # (1080, 1920)
    return img


def show_img(path, resolution):
    img = get_img(read_file(path), resolution)

    plt.tight_layout(pad=-1)
    plt.imshow(img)
    plt.show()


def show_diff(path1, path2, resolution):
    img1 = get_img(read_file(path1), resolution)
    img2 = get_img(read_file(path2), resolution)

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

    args = sys.argv

    resolution = (1080, 1920)
    if len(args) == 2:
        show_img(args[1], resolution)
    elif len(args) == 4:
        show_img(sys.argv[1], (int(args[2]), int(args[3])))
    elif len(args) == 3:
        show_diff(args[1], args[2], resolution)
    elif len(args) == 5:
        show_diff(args[1], args[2], (int(args[3]), int(args[4])))
    else:
        print("If you want to look at a single frame give path to it \n"
              "if you want compare 2 images give to paths ")

    # result = np.sqrt(result)
    # avg = np.average(result)

    # plt.figure(figsize=(256, 256))
