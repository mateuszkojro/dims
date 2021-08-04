import cython
import pyximport;

pyximport.install()
import math

import cv2
from typing import NoReturn, Tuple, List, Union
import matplotlib.pyplot as plt
from dataclasses import dataclass, astuple
from functools import cache
import imutils
import numpy as np


# @dataclass(unsafe_hash=True)
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

    def __init__(self, frame_no: int, position : Vec2, size : int):
        self.size: cython.int = size
        self.position: cython.int = position
        self.frame_no: cython.int = frame_no

    @cache
    # TODO: Is that correct tho?
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
        self.positions = []
        self.positions.append(position)
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
        for item in self.positions:
            if item.is_simillar_to(position, 10):
                self.positions.append(position)
                self.last_changed = position.frame_no
                return True
        return False

    def magnitude(self):
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

    def lenght(self):
        start, stop = self.path()
        return euc_distance(start, stop)


# @dataclass(frozen=True)
class TriggerInfo:
    event: Union[Event, None]
    length: cython.int
    filename: str
    start_frame: cython.int
    end_frame: cython.int
    magnitude: cython.int
    bounding_box: Tuple[Vec2]

    def __init__(self, event, length, filename, start_frame, end_frame, magnitude, bounding_box):
        self.event = event
        self.length = length
        self.filename = filename
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.magnitude = magnitude
        self.bounding_box = bounding_box

    def get_section(self):
        start, end = self.bounding_box
        x = start.x + (end.x - start.x) / 2
        y = start.y + (end.y - start.y) / 2

        x = x // 120
        y = y // 120

        return int(y * (1920 / 120)) + int(x)

    def cutout(self):
        pass

    def calculate_moment(self):
        frames = []
        capture = cv2.VideoCapture(self.filename)
        capture.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        for i in range(self.end_frame - self.start_frame):
            status, frame = capture.read()
            frames.append(frame)

        combined = self.combine_frames(frames)

        cutout =


    def get_frame_chunk(self):
        raise Exception("Not implemented")

    @staticmethod
    def from_csv_row(row):
        row = row[1:]
        return TriggerInfo(
            filename=row[0],
            start_frame=int(row[1]),
            end_frame=int(row[2]),
            bounding_box=(Vec2(row[3], row[4]), Vec2(row[5], row[6])),
            length=row[7],
            magnitude=row[8],
            event=None
        )

    @staticmethod
    def combine_frames(frames):
        if len(frames) == 0:
            return None

        # print(f"{np.ndim(frames)}")
        if len(fames) > 50:
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
    return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)

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
                       magnitude=event.magnitude(),
                       bounding_box=event.bounding_rect(),
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

def preprocess_frame(frame, sigma=(3, 3)):
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grayscale = cv2.GaussianBlur(grayscale, sigma, 0)
    return grayscale

def get_contours(frame, reference_frame):
    delta = cv2.absdiff(frame, reference_frame)
    thresh = cv2.threshold(delta, 55, 255, cv2.THRESH_BINARY)[1]

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
def update_events(event_list,
                  frame_number,
                  drop_inactive_time=3):
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
    # if event.magnitude() < trigger_treshold:
    #     return False

    # FIXME: That needs to be some dynamic value
    if event.lenght() < 20:
        return False

    # real event will be on more than one frame
    # FIXME: That needs to be some dynamic value
    if event.last_changed - event.first_point < 3:
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
    if len(fames) > 50:
        print("ERR: to many frames")
        frames = frames[:50]
    return np.amax(frame_list, axis=0)

def get_frames(path, start, stop):
    capture = cv2.VideoCapture(path)
    capture.set(cv2.CAP_PROP_POS_FRAMES, start)
    frames = []
    for i in range(stop - start + 1):
        status, frame = capture.read()
        frames.append(frame)
    return frames

def add_marker(frame, trigger):
    rect = trigger.bounding_box
    cv2.rectangle(frame, rect[0].tuple(), rect[1].tuple(), (0, 255, 0), 2)
    return frame

def show_trigger(trigger):
    frames = get_frames(trigger.filename, trigger.start_frame, trigger.end_frame)
    result = combine_frames(frames)
    result = add_marker(result, trigger)
    plt.imshow(result)
    plt.show()


class Analyzer:

    def __init__(self):
        pass
