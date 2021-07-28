import math
import cv2
from dataclasses import dataclass, astuple
from functools import cache
import imutils


@dataclass(unsafe_hash=True)
class Coord:
    x: int
    y: int

    @cache
    def tuple(self):
        return astuple(self)


@dataclass(frozen=True)
class EventInfo:
    frame_no: int
    position: Coord
    size: Coord

    @cache
    def center(self):
        x = self.position.x + (self.size.x / 2)
        y = self.position.y + (self.size.y / 2)
        return Coord(int(x), int(y))

    def is_simillar_to(self, event, treshold: float):
        # check the time between events
        if abs(self.frame_no - event.frame_no) > 5:
            return False
        # and how far apart they are
        if euc_distance(self.center(), event.center()) < treshold:
            return True
        return False


class Event:
    positions: [EventInfo]
    last_changed: int = 0

    def __init__(self, position: EventInfo):
        self.positions = []
        self.positions.append(position)
        self.last_changed = position.frame_no

    # TODO: This should be done using that
    #  https://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html
    @cache
    def bounding_rect(self) -> (int, int):
        min_x, min_y = self.positions[0].center()
        max_x, max_y = self.positions[0].center()
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
        minimal = math.floor(min_x), math.floor(min_y)
        maximal = math.floor(max_x), math.floor(max_y)
        return minimal, maximal

    def path(self) -> (Coord, Coord):
        start = self.positions[0].position
        end = self.positions[-1].position
        return start, end

    def add_if_similar(self, position: EventInfo) -> bool:
        for item in self.positions:
            if item.is_simillar_to(position, 15):
                self.positions.append(position)
                self.last_changed = position.frame_no
                return True
        return False


@cache
def euc_distance(pos1: Coord, pos2: Coord) -> float:
    return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)


def prepare_image(image, target_size):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = imutils.resize(image, width=target_size)
    x = y = 0
    h, w = image.shape
    # Cut out the description
    image = image[y:(h - 20), x:w]
    return image


# Adapted form:
# https://www.andrewnoske.com/wiki/Code_-_heatmaps_and_color_gradients
def heatmap_color(val, max_val):
    val = val / max_val
    NUM_COLORS = 2
    color = [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
    idx1 = None
    idx2 = None
    fractBetween = 0
    if val <= 0:
        idx1 = idx2 = 0  # ;} // accounts for an input <= 0
    elif val >= 1:
        idx1 = idx2 = NUM_COLORS  # accounts for an input >= 0
    else:
        val = val * NUM_COLORS
        idx1 = math.floor(val)
        fractBetween = val - float(idx1)
        idx2 = idx1 + 1

    red = (color[idx2][0] - color[idx1][0]) * fractBetween + color[idx1][0]
    green = (color[idx2][1] - color[idx1][1]) * fractBetween + color[idx1][1]
    blue = (color[idx2][2] - color[idx1][2]) * fractBetween + color[idx1][2]

    return blue * 255, green * 255, red * 255
