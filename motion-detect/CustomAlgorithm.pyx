from os import EX_CANTCREAT
import cython
from numpy.core.fromnumeric import size
from numpy.lib.function_base import cov
import pyximport

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.animation as animation

pyximport.install()
import math

import cv2
from typing import NoReturn, Tuple, List, Union
import matplotlib.pyplot as plt
from dataclasses import dataclass, astuple
from functools import cache
import imutils
import numpy as np

from collections import namedtuple
from math import sqrt
import scipy.optimize as optim
import scipy.stats as stats

Line = namedtuple('Line', ['a', 'b', 'r'])


# Vec2 = namedtuple('Vec2', ['x','y'])
@cython.cfunc
def linear_func(x, a, b):
    return a * x + b


all_events = []


# # @dataclass(unsafe_hash=True)
@cython.cclass
class Vec2:
    x = cython.declare(cython.int, visibility='public')
    y = cython.declare(cython.int, visibility='public')

    def __init__(self, x, y):
        self.x: cython.int = x
        self.y: cython.int = y

    @cache
    def tuple(self) -> Tuple[int, int]:
        # return astuple(self)
        return self.x, self.y


# @dataclass(frozen=True)
@cython.cclass
class EventInfo:
    frame_no = cython.declare(cython.int, visibility='public')
    position = cython.declare(Vec2, visibility='public')
    size = cython.declare(Vec2, visibility='public')

    def __init__(self, frame_no: int, position: Vec2, size: int):
        self.size: cython.int = size
        self.position: cython.int = position
        self.frame_no: cython.int = frame_no

    @cache
    # TODO: Test that Is that correct tho?
    def center(self) -> Vec2:
        x: cython.int = self.position.x + int(self.size.x / 2)
        y: cython.int = self.position.y + int(self.size.y / 2)
        return Vec2(int(x), int(y))

    @cython.ccall
    def is_simillar_to(self, event, treshold: float):
        # check the time between events
        if abs(self.frame_no - event.frame_no) > 5:
            return False
        # and how far apart they are
        if euc_distance(self.center(), event.center()) < treshold:
            return True
        return False


class Event:
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

    # TODO: This should be done using that
    #  https://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html
    @cache
    @cython.boundscheck(False)  # Deactivate bounds checking
    @cython.wraparound(False)  # Deactivate negative indexing.
    def bounding_rect(self) -> Tuple[Vec2]:
        min_x, min_y = self.positions[0].center().tuple()
        max_x, max_y = self.positions[0].center().tuple()
        for item in self.positions:
            event = item.center()
            if event.x < min_x:
                min_x = event.x
            if event.y < min_y:
                min_y = event.y
            if event.x > max_x:
                max_x = event.x
            if event.y > max_y:
                max_y = event.y
        minimal = Vec2(math.floor(min_x), math.floor(min_y))
        maximal = Vec2(math.floor(max_x), math.floor(max_y))
        return minimal, maximal

    @cython.boundscheck(False)  # Deactivate bounds checking
    def path(self) -> Tuple[Vec2]:
        start = self.positions[0].position
        end = self.positions[-1].position
        return start, end

    @cython.boundscheck(False)  # Deactivate bounds checking
    @cython.wraparound(False)  # Deactivate negative indexing.
    def add_if_similar(self, position: EventInfo) -> bool:
        # FIXME: How long should it be
        if len(self.positions) > 3 and self.point_to_line_distance(
                position.position) > 5:
            return False
        for item in self.positions:
            if item.is_simillar_to(position, 15):
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

    @cython.boundscheck(False)  # Deactivate bounds checking
    @cython.wraparound(False)  # Deactivate negative indexing.
    def lenght(self):
        start, stop = self.path()
        return euc_distance(start, stop)

    # TODO: Odleglosc od odcinka
    def line_segment_to_point_distance(self):
        raise Exception("Not implemented")

    def point_to_line_distance(self, point: Vec2):
        a, b, r = self.fit_line()
        a = abs(a * point.x + (-1) * point.y + b)
        denominator = a**2 + (-1)**2
        return a / denominator

    def pearsons_coef(self):
        N = len(self.positions)
        xs = np.zeros(N)
        ys = np.zeros(N)
        for i, point in enumerate(self.positions):
            xs[i] = point.position.x
            ys[i] = point.position.y
        return stats.pearsonr(xs, ys)

    # TODO: I think mine was much faster
    @cython.boundscheck(False)  # Deactivate bounds checking
    @cython.wraparound(False)  # Deactivate negative indexing.
    def fit_line(self):

        N = len(self.positions)
        xs = np.zeros(N)
        ys = np.zeros(N)
        for i, point in enumerate(self.positions):
            xs[i] = point.position.x
            ys[i] = point.position.y

        (a, b), covariance_matrix = optim.curve_fit(linear_func, xs, ys)

        r_sqr, _ = stats.pearsonr(xs, ys)

        return Line(a, b,
                    r_sqr)  #, covariance_matrix[0, 0], covariance_matrix[1,1])

        # points = [p.position for p in self.positions]
        # s = float(len(points))
        # s_x = sum(float(p.x) for p in points)
        # s_y = sum(float(p.y) for p in points)
        # s_xx = sum(float(p.x)**2.0 for p in points)
        # s_yy = sum(float(p.y)**2.0 for p in points)
        # s_xy = sum(float(p.x) * float(p.y) for p in points)
        # delta = s * s_xx - (s_x**2.0)

        # if s == 0 or delta == 0 or s - 2 == 0:
        #     print(f"ERR\tDivide by 0 while fitting the line: \n"
        #           f"s: {s}\n"
        #           f"s_x: {s_x}, s_xx: {s_xx}\n"
        #           f"s_y: {s_y}, s_yy: {s_yy}\n"
        #           f"s_xy: {s_xy}, delta: {delta}\n"
        #           f"points: {points}")
        #     return Line(0, 0, 0, 0, 0)

        # a = (s * s_xy - s_x * s_y) / delta
        # b = (s_xx * s_y - s_x * s_xy) / delta

        # chi_sqr = s_yy - a * s_xy - b * s_y

        # delta_a = chi_sqr / (s - 2) * s / delta
        # delta_b = delta_a * s_xx / s

        # denominator = sqrt((s * s_xx - (s_x**2)) * (s * s_yy - (s_y**2)))

        # if denominator == 0:
        #     print(f"ERR\tDivide by 0 while fitting the line: \n"
        #           f"s: {s}\n"
        #           f"s_x: {s_x}, s_xx: {s_xx}\n"
        #           f"s_y: {s_y}, s_yy: {s_yy}\n"
        #           f"s_xy: {s_xy}, delta: {delta}, denominator: {denominator}\n"
        #           f"points: {points}\n")
        #     return Line(0, 0, 0, 0, 0)

        # r = (s * s_xy - s_x * s_y) / denominator
        # r = abs(r)

        # return Line(a, b, r, delta_a, delta_b)


# @dataclass(frozen=True)
class TriggerInfo:
    event: Union[Event, None]
    length: cython.int
    filename: str
    start_frame: cython.int
    end_frame: cython.int
    event_count: cython.int
    bounding_box: Tuple[Vec2]
    line_fit: float

    def __init__(self,
                 event,
                 length,
                 filename,
                 start_frame,
                 end_frame,
                 event_count,
                 bounding_box,
                 line_fit=None):

        self.event = event
        self.length = length
        self.filename = filename
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.event_count = event_count
        self.bounding_box = bounding_box
        self.line_fit = line_fit

    # TODO: Test that to be sure
    def get_section(self):
        start, end = self.bounding_box
        x = start.x + abs(end.x - start.x) / 2
        y = start.y + abs(end.y - start.y) / 2

        x = x // 120
        y = y // 120

        return int(y * (1920 / 120)) + int(x)

    # TODO: Test that to be sure
    def get_center(self):
        start, end = self.bounding_box
        x = start.x + abs(end.x - start.x) / 2
        y = start.y + abs(end.y - start.y) / 2
        return Vec2(x, y)

    def get_uid(self):
        filename = self.filename.replace('/', '@')
        return f"{filename}_{self.get_section()}_{self.start_frame}_{self.end_frame}"

    def cutout(self):
        frames = get_frames(self.filename, self.start_frame, self.end_frame)
        start, stop = self.bounding_box
        frames = [frame[start.x:stop.x, start.y:stop.y] for frame in frames]
        return frames

    def region(self):
        raise Exception("Not implemented")

    def animate(self):
        imgs = self.cutout()
        frames = []  # for storing the generated images

        fig = plt.figure()
        for img in imgs:
            # frames.append([plt.imshow(img[i], cmap=cm.Greys_r, animated=True)])
            frames.append([plt.imshow(img, animated=True)])

        ani = animation.ArtistAnimation(fig,
                                        frames,
                                        interval=100,
                                        blit=True,
                                        repeat_delay=10)
        plt.show()

    def calculate_moment(self):
        frames = []
        capture = cv2.VideoCapture(self.filename)
        capture.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        for i in range(self.end_frame - self.start_frame):
            status, frame = capture.read()
            frames.append(frame)

        combined = self.combine_frames(frames)

        raise Exception("Onl partialy implemented")

    def get_frame_chunk(self):
        raise Exception("Not implemented")

    @staticmethod
    def from_csv_row(row):
        row = row[1:]
        return TriggerInfo(filename=row[0],
                           start_frame=int(row[1]),
                           end_frame=int(row[2]),
                           bounding_box=(Vec2(row[3],
                                              row[4]), Vec2(row[5], row[6])),
                           length=row[7],
                           event_count=row[8],
                           line_fit=[0],
                           event=None)

    @staticmethod
    def combine_frames(frames):
        if len(frames) == 0:
            return None

        # print(f"{np.ndim(frames)}")
        if len(frames) > 50:
            print("ERR: to many frames")
            frames = frames[:50]
        result = np.amax(frames, axis=1)

        return result

    def show(self) -> None:
        frames = []
        capture = cv2.VideoCapture(self.filename)
        capture.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        for i in range(self.end_frame - self.start_frame):
            status, frame = capture.read()
            frames.append(frame)

        combined = self.combine_frames(frames)

        if combined is None:
            print("Empty frame")
            return

        # frame = combined

        for point in self.event.positions:
            frame = cv2.circle(frame,
                               point.center().tuple(), 1, (0, 255, 0), 1)

        frame = resize_frame(frame)
        left_top, right_bottom = self.bounding_box

        plt.imshow(frame)
        plt.show()


# @cache
@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)  # Deactivate negative indexing.
@cython.ccall
def euc_distance(pos1: Vec2, pos2: Vec2) -> cython.float:
    return math.sqrt((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2)


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


def save_event(event: Event) -> TriggerInfo:
    return TriggerInfo(filename=event.filename,
                       length=event.lenght(),
                       start_frame=event.first_point,
                       end_frame=event.last_changed,
                       event_count=event.event_count(),
                       bounding_box=event.bounding_rect(),
                       line_fit=event.fit_line()[2],
                       event=event)


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


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)  # Deactivate negative indexing.
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

    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

    contours = imutils.grab_contours(contours)

    return contours


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)  # Deactivate negative indexing.
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
            event_list.append(Event(new_event, filename=filename))


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)  # Deactivate negative indexing.
@cython.ccall
def update_events(event_list, frame_number, drop_inactive_time=3):
    triggers = []
    for event in event_list:
        # remove events not active for more than 5 frames
        if abs(event.last_changed - frame_number) > drop_inactive_time:

            # If event is not good enough we delete it
            if is_good_trigger(event):
                triggers.append(save_event(event))

            event_list.remove(event)

    return triggers if len(triggers) > 0 else None


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)  # Deactivate negative indexing.
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
        print(f"INFO:\tBad line fit {r}")
        return False

    #
    # if event.too_slow():
    #     return False

    # TODO: Check how close to a line is it
    return True


def annotate_frame(frame,
                   event_list,
                   draw_path=True,
                   draw_box=False,
                   draw_confidence=True,
                   heatmap=(0, 20)):
    for event in event_list:
        rect = event.path()
        if draw_path:
            color = heatmap_color(event.lenght(),
                                  heatmap[1]) if heatmap else (0, 255, 0)
            cv2.line(frame, rect[0].tuple(), rect[1].tuple(), color, 3)

        if draw_box:
            rect = event.bounding_rect()
            cv2.rectangle(frame, rect[0].tuple(), rect[1].tuple(), (0, 255, 0),
                          2)

        if draw_confidence:
            cv2.putText(frame, f"{event.lenght():1f}q", rect[0].tuple(),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 0, 0), 1)


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)  # Deactivate negative indexing.
@cython.ccall
def on_destroy(event_list):
    triggers = []
    for event in event_list.copy():
        if is_good_trigger(event):
            triggers.append(save_event(event))

    return triggers if len(triggers) > 0 else None


def combine_frames(frame_list):
    if len(frame_list) > 50:
        print("ERR: to many frames")
        frame_list = frame_list[:50]
    return np.amax(frame_list, axis=0)


def get_frames(path, start, stop):
    print(f"path= {path}")
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
        print(status, frame)
        frames.append(frame)

    return frames


def add_marker(frame, trigger):
    rect = trigger.bounding_box
    cv2.rectangle(frame, rect[0].tuple(), rect[1].tuple(), (0, 255, 0), 2)
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
    result = prepare_trigger_frame(trigger)
    plt.imshow(result)
    plt.show()
    # return plt
    # return result


# TODO: Test that to be sure
def show_raw(filename,
             start_frame,
             end_frame,
             rect_start,
             rect_stop,
             size=(1920 // 120, 1080 // 120)):
    # plt.Figure(figsize=size)
    frames = get_frames(filename, start_frame, end_frame)
    result = combine_frames(frames)
    cv2.rectangle(result, rect_stop, rect_start, (255, 0, 0), 2)
    # plt.imshow(result)
    # plt.show()
    return result


class Analyzer:
    def __init__(self):
        pass
