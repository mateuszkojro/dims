import cython
import pyximport

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import math

import cv2
from typing import Tuple, List, Union
import matplotlib.pyplot as plt
# from functools import cache
import imutils
import numpy as np

from TriggerInfo import TriggerInfo
from utils import Vec2, Rect, get_frames, combine_frames, resize_frame

from collections import namedtuple
import scipy.optimize as optim
import scipy.stats as stats
from math import dist

from log import *

pyximport.install()

Line = namedtuple('Line', ['a', 'b', 'r'])


# Vec2 = namedtuple('Vec2', ['x','y'])
@cython.cfunc
def linear_func(x, a, b):
    return a * x + b


all_events = []


# @dataclass(frozen=True)
# @cython.cclass
class EventInfo:
    # frame_no = cython.declare(cython.int, visibility='public')
    # position = cython.declare(Tuple, visibility='public')
    # size = cython.declare(Tuple, visibility='public')

    def __init__(self, frame_no: int, position: Vec2, size: int):
        self.size: cython.int = size
        self.position: cython.int = position
        self.frame_no: cython.int = frame_no

    # TODO: Test that Is that correct tho?
    def center(self) -> Vec2:
        x: cython.int = self.position.x + int(self.size.x / 2)
        y: cython.int = self.position.y + int(self.size.y / 2)
        return Vec2(int(x), int(y))

    def is_simillar_to(self, event, treshold: float):
        # check the time between events
        if abs(self.frame_no - event.frame_no) > 5:
            return False
        # and how far apart they are
        if euc_distance(self.center(), event.center()) < treshold:
            return True
        return False


class Cluster:
    """ Class containing a cluster of events """
    positions: List[EventInfo]
    last_changed: cython.int = 0
    filename: str

    def __init__(self, position: EventInfo, filename):
        self.positions = np.array([position])
        # self.positions = np.append(self.positions,)
        self.first_point = position.frame_no
        self.last_changed = position.frame_no
        self.filename = filename

    # TODO: This could be useful
    # https://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html
    @cython.boundscheck(False)
    @cython.wraparound(False)
    def bounding_rect(self):
        N = len(self.positions)

        xs = np.empty(N)
        ys = np.empty(N)

        for i, position in enumerate(self.positions):
            xs[i] = position.center().x
            ys[i] = position.center().y

        rect = Rect(
            min_x=np.min(xs),
            min_y=np.min(ys),
            max_x=np.max(xs),
            max_y=np.max(ys),
        )

        return rect

    @cython.wraparound(False)
    @cython.boundscheck(False)
    def path(self) -> Tuple[Vec2]:
        start = self.positions[0].position
        end = self.positions[len(self.positions) - 1].position
        return start, end

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def add_if_similar(self, position: EventInfo) -> bool:
        # FIXME: How long should it be
        if len(self.positions) > 3 and self.point_to_line_distance(
                position.position) > 5:
            return False
        for item in self.positions:
            if item.is_simillar_to(position, 20):
                self.positions = np.append(self.positions, position)
                self.last_changed = position.frame_no
                return True
        return False

    def event_count(self):
        return len(self.positions)

    def too_slow(self, min_speed: cython.int = 10):
        if len(self.positions) < 5:
            return False

        time = (self.last_changed - self.first_point)
        if time == 0:
            return False

        start, stop = self.path()
        speed = euc_distance(start, stop) / time
        if speed < min_speed:
            return True

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def lenght(self):
        start, stop = self.path()
        return euc_distance(start, stop)

    # TODO: Odleglosc od odcinka
    def line_segment_to_point_distance(self):
        raise Exception("Not implemented")

    def point_to_line_distance(self, point: Vec2):
        a, b, _ = self.fit_line()
        a = abs(a * point.x + (-1) * point.y + b)
        denominator = a**2 + (-1)**2
        return a / denominator

    def pearsons_coef(self):
        N = len(self.positions)
        xs = np.empty(N)
        ys = np.empty(N)
        for i, point in enumerate(self.positions):
            xs[i] = point.position.x
            ys[i] = point.position.y
        return stats.pearsonr(xs, ys)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def fit_line(self):

        N = len(self.positions)
        xs = np.zeros(N)
        ys = np.zeros(N)
        for i, point in enumerate(self.positions):
            xs[i] = point.position.x
            ys[i] = point.position.y

        (a, b), covariance_matrix = optim.curve_fit(linear_func, xs, ys)

        # r_sqr = stats.pearsonr(xs, ys) # if we want to calculte the fit
        r_sqr = None

        return Line(a, b, r_sqr)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.ccall
def euc_distance(pos1: Vec2, pos2: Vec2) -> cython.float:
    return dist(pos1,
                pos2)  # math.sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2)


# Adapted form:
# https://www.andrewnoske.com/wiki/Code_-_heatmaps_and_color_gradients
def heatmap_color(val, max_val) -> Tuple[int]:
    val = val / max_val
    NUM_COLORS = 2
    color = [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
    frac_between = 0
    if val <= 0:
        idx1 = idx2 = 0  # accounts for an input <= 0
    elif val >= 1:
        idx1 = idx2 = NUM_COLORS  # accounts for an input >= 0
    else:
        val = val * NUM_COLORS
        idx1 = math.floor(val)
        frac_between = val - float(idx1)
        idx2 = idx1 + 1

    red = (color[idx2][0] - color[idx1][0]) * frac_between + color[idx1][0]
    green = (color[idx2][1] - color[idx1][1]) * frac_between + color[idx1][1]
    blue = (color[idx2][2] - color[idx1][2]) * frac_between + color[idx1][2]

    return blue * 255, green * 255, red * 255


def save_event(event: Cluster) -> TriggerInfo:
    return TriggerInfo(filename=event.filename,
                       length=event.lenght(),
                       start_frame=event.first_point,
                       end_frame=event.last_changed,
                       event_count=event.event_count(),
                       bounding_box=event.bounding_rect(),
                       line_fit=event.fit_line()[2],
                       event=event)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.ccall
def preprocess_frame(frame, sigma=(3, 3)):
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grayscale = cv2.GaussianBlur(grayscale, sigma, 0)
    return grayscale


def get_contours(frame, reference_frame):
    delta = cv2.absdiff(frame, reference_frame)

    thresh = cv2.threshold(delta, 50, 255, cv2.THRESH_BINARY)[1]

    # on threshold image
    thresh = cv2.dilate(thresh, None, iterations=2)

    contours = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL,  # Here was tresh.copy()
        cv2.CHAIN_APPROX_SIMPLE)

    contours = imutils.grab_contours(contours)

    return contours


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.ccall
def extract_events(contours,
                   event_list,
                   frame_number,
                   filename,
                   trigger_treshold_area=5):
    for contour in contours:
        # if the contour is too small, ignore it
        if cv2.contourArea(contour) < trigger_treshold_area:
            return
        # compute the bounding box for the contour
        (x, y, w, h) = cv2.boundingRect(contour)
        position = Vec2(x, y)
        size = Vec2(w, h)
        was_added = False
        new_event = EventInfo(frame_number, position, size)

        for event in event_list:
            if event.add_if_similar(new_event):
                was_added = True
        if not was_added:
            event_list.append(Cluster(new_event, filename=filename))


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.ccall
def update_events(event_list, frame_number, drop_inactive_time=3):
    triggers = []
    for event in event_list:
        # remove events not active for more than 5 frames
        if abs(event.last_changed - frame_number) > drop_inactive_time:

            # If event is ok we save it to the list of triggers
            if is_good_trigger(event):
                triggers.append(save_event(event))

            event_list.remove(event)

    return triggers if len(triggers) > 0 else None


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.ccall
def is_good_trigger(event, trigger_treshold=5):
    #
    # if event.event_count() < trigger_treshold:
    #     return False

    # FIXME: That needs to be some dynamic value
    if event.lenght() < 20:
        return False

    # real event will be on more than one frame
    # FIXME: That needs to be some dynamic value
    if event.last_changed - event.first_point < 3:
        return False

    # FIXME: That needs to be some dynamic value
    r = event.pearsons_coef()[0]
    if abs(r) < 0.8:
        info(f"Bad line fit {r}")
        return False

    # TODO: We should check for speed (too slow events are bad)
    # if event.too_slow():
    #     return False

    return True


def annotate_frame(frame,
                   event_list,
                   draw_path=False,
                   draw_box=True,
                   draw_confidence=True,
                   heatmap=(0, 20)):

    for event in event_list:
        (start_x, start_y), (end_x, end_y) = event.path()
        if draw_path:
            color = heatmap_color(event.lenght(),
                                  heatmap[1]) if heatmap else (0, 255, 0)
            # cv2.line(frame,
            #          (int(start_x), int(start_y)),
            #          (int(end_x), int(end_y)),
            #          end, color, 3)

        if draw_box:
            min_x, min_y, max_x, max_y = event.bounding_rect()
            cv2.rectangle(frame,
                          (int(min_x), int(min_y)),
                          (int(max_x), int(max_y)),
                          (0, 255, 0), 2)

        if draw_confidence:
            pass
            # cv2.putText(frame, f"{event.lenght():1f}q",
            #             (int(start_x), int(start_y)),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 0, 0), 1)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.ccall
def on_destroy(event_list):
    triggers = []
    for event in event_list.copy():
        if is_good_trigger(event):
            triggers.append(save_event(event))

    return triggers if len(triggers) > 0 else None


def add_marker(frame, trigger):
    print(type(frame))
    (min_x, min_y), (max_x, max_y) = trigger.bounding_box
    cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
    return frame


# TODO: Test that to be sure
def prepare_trigger_frame(trigger, size=(1920 // 120, 1080 // 120)):
    frames = get_frames(trigger.filename, trigger.start_frame,
                        trigger.end_frame)
    result = combine_frames(frames)
    result = add_marker(result, trigger)
    return result


def show_trigger(trigger, size=(1920 // 120, 1080 // 120)):
    # plt.Figure(figsize=size)
    from matplotlib.pyplot import figure
    figure(figsize=size, dpi=80)
    result = prepare_trigger_frame(trigger)
    plt.imshow(result)
    plt.show()
    # return plt
    # return result


class Analyzer:
    def __init__(self):
        pass
