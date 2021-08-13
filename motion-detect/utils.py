import cv2
import os
import numpy as np
import imutils
import pandas as pd
import cython

from log import *

from collections import namedtuple

# @cython.cclass
# class Vec2:
#     x = cython.declare(cython.int, visibility='public')
#     y = cython.declare(cython.int, visibility='public')

#     def __init__(self, x, y):
#         self.x: cython.int = x
#         self.y: cython.int = y

#     @cache
#     def tuple(self) -> Tuple[int, int]:
#         # return astuple(self)
#         return self.x, self.y

Vec2 = namedtuple('Vec2', ['x', 'y'])


def combine_frames(frame_list):
    if len(frame_list) > 50:
        print("ERR: to many frames")
        frame_list = frame_list[:50]
    return np.amax(frame_list, axis=0)


def get_frames(path, start, stop):
    capture = cv2.VideoCapture(path)
    capture.set(cv2.CAP_PROP_POS_FRAMES, start)
    frames = []
    if stop is None:
        stop = capture.get(cv2.CAP_PROP_FRAME_COUNT - 1)
        status = True
        while status:
            status, frame = capture.read()
            frames.append(frame)
        return frames

    for _ in range(stop - start + 1):
        status, frame = capture.read()
        frames.append(frame)

    return frames


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)  # Deactivate negative indexing.
@cython.ccall
def resize_frame(image, width=1920):
    # Scale image
    image = imutils.resize(image, width=width)
    x = y = 0
    h = image.shape[0]
    w = image.shape[1]

    # Cut out the description
    image = image[y:(h - 30), x:w]
    return image


def show_coresponding_image(path):
    image = cv2.imread(path[:-4] + "M.bmp")
    image = imutils.resize(image, width=600)
    cv2.imshow("Ufo capture", image)


def draw_grid(frame, res=Vec2(16, 9)):
    h = frame.shape[0]
    w = frame.shape[1]

    for x in range(16):
        cv2.line(frame, (x * w / res.x, 0), (x * w / res.x, h), (0, 0, 100), 1)
    for y in range(9):
        cv2.line(frame, (0, y * h / res.y), (w, y * h / res.y), (0, 0, 100), 1)


def get_setting(setting, default, var_type=int):
    result = default
    if setting in os.environ:
        result = var_type(os.environ[setting])
        info(f"{setting}:{result}")

    return result


def save(all_triggers, out_name="out"):
    numpy_array = np.array(all_triggers, dtype=object)
    np.save(out_name + ".npy", numpy_array, allow_pickle=True)

    rows = []

    for clip in all_triggers:
        for trigger in clip:
            start, end = trigger.bounding_box
            rows.append([
                trigger.filename, trigger.start_frame, trigger.end_frame,
                start.x, start.y, end.x, end.y, trigger.length,
                trigger.event_count,
                trigger.get_section(), trigger.line_fit
            ])

    df = pd.DataFrame(data=rows,
                      columns=[
                          "file", "start_frame", "end_frame", "box_up_left_x",
                          "box_up_left_y", "box_down_right_x",
                          "box_down_right_y", "length", "count", "section",
                          "line_fir"
                      ])

    df.to_csv(out_name + ".csv")
