#! /usr/bin/python3

import cv2
import time
import imutils
import matplotlib.pyplot as plt
import numpy as np
import sys

from CustomAlgorithm import *

SHOW = False
INPUT_PATH = "./file.avi"
SHOW_RAW = True
SHOW_DELTA = True

DRAW_BOX = False
DRAW_PATH = True
DRAW_STATS = True
DRAW_CONFIDENCE = True
HEATMAP = True

TARGET_WIDTH = 1920

WITH_GAUSS = True
GAUSS_SIGMA = (3, 3)

TRIGER_AREA_TRESHOLD = 5
DROP_INACTIVE_TIME = 3

EVENT_TRESHOLD = 10


def analyze(path):
    triggers = []
    events: [Event] = []
    frame_number = 0
    video_capture = cv2.VideoCapture(path)
    reference_frame = None
    while True:

        status, frame = video_capture.read()

        if not status:
            on_destroy()
            break

        resized_frame = resize_frame(frame)

        preprocessed = preprocess_frame(resized_frame)

        # if the first frame is None, initialize it
        if reference_frame is None:
            reference_frame = preprocessed
            continue

        contours = get_contours(preprocessed, reference_frame)

        extract_events(contours, events, frame_number)

        new_triggers = update_events(events, frame_number)

        if new_triggers is not None:
            triggers.append(new_triggers)

        annotate_frame(resized_frame, events)
        cv2.imshow(path, resized_frame)

        frame_number += 1
        # Get the pressed key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            on_destroy()
            break

    return triggers


if __name__ == '__main__':
    from FileCrawler import crawl

    res = crawl("/run/media/mateusz/Seagate Expansion Drive/20190330Subset/N1", analyze)
    print(f"{res=}")
    res = np.array(res)
    res = np.concatenate(res, axis=0)
    np.save("out.npy", np.array(res), allow_pickle=True)
    plt.plot(res)
    plt.show()
