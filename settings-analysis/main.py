import cv2
import numpy as np
import matplotlib.pyplot as plt
import imutils
import time
import random


# ls -1a

def load_video(path):
    pass


def cut_region(cvmat, position):
    # x = 0
    # y = 0
    # w = cvmat.shape[1]
    # h = cvmat.shape[0]
    x, y, w, h = position

    # Cut out the description
    return cvmat[y:(y + h), x:(x + w)]


def calc_avg(cvmat):
    return sum(cvmat) / len(cvmat)


def plot(data, errx, erry):
    assert len(errx) == len(data) == len(erry)
    plt.errorbar(np.linspace(0, len(data)), data, yerr=erry, fmt='d', color='black',
                 ecolor='lightgray', elinewidth=1, capsize=4)
    plt.plot(data)
    plt.show()


def analyze_file(path):
    PATH = path
    TARGET_WIDTH = 900
    x, y, w, h = 1800, 985, 100, 100

    data = [[], []]

    capture = cv2.VideoCapture(PATH)
    i = 0
    while True:
        status, frame = capture.read()

        if status is False:
            print("End of file")
            break
            # capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            # continue

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        cv2.rectangle(frame, (x - 2, y - 2), (x + w + 2, y + h + 2,), (0, 0, 255), 2)
        close_up = cut_region(frame, (x, y, w, h))

        close_up = imutils.resize(close_up, width=TARGET_WIDTH)
        frame = imutils.resize(frame, width=TARGET_WIDTH)
        frame = np.array(frame)

        avg = calc_avg(close_up.flatten())

        data[0].append(capture.get(cv2.CAP_PROP_POS_FRAMES))
        data[1].append(avg)

        cv2.imshow("close up", close_up)
        cv2.imshow("frame", frame)

    # plt.style.use('seaborn-whitegrid')
    plt.plot(data[1])
    # upper = []
    # lower = []
    # maximum = max(data[1])
    # minimum = min(data[1])
    # for i in range(len(data[0])):
    #     upper.append(maximum)
    #     lower.append(minimum)
    # plt.errorbar(data[0], data[1], yerr=[lower, upper], fmt='^', color='black',
    #              ecolor='lightgray', elinewidth=1, capsize=4)
    plt.title(PATH)
    plt.savefig(f"{PATH}.plot.png")
    plt.show()
    return calc_avg(data[1]), (max(data[0]), min(data[0])), path


if __name__ == '__main__':
    with open('videos.txt') as f:
        all = []
        paths = []
        errorsL = []
        errorsU = []
        for file in f:
            if file != "\n":
                file = file.strip("\n")
                print(f"Analyzing file:\t{file}")
                data, err, path = analyze_file(file)
                all.append(data)
                paths.append(path)
                errorsL.append(err[0])
                errorsU.append(err[1])

        plt.errorbar([x for x in range(len(all))], all, yerr=[errorsU, errorsL], fmt='x', color='black', elinewidth=1,
                     capsize=4)
        plt.xlabel("analyzed files")
        plt.xticks(rotation='vertical')
        plt.bar([x for x in range(len(all))],all,tick_label=paths)
        plt.title("out")
        plt.tight_layout()
        plt.savefig(f"out.plot.png")
        plt.show()
