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
        minimal = Coord(math.floor(min_x), math.floor(min_y))
        maximal = Coord(math.floor(max_x), math.floor(max_y))
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

    def magnitude(self):
        return len(self.positions)


@cache
def euc_distance(pos1: Coord, pos2: Coord) -> float:
    return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)


# Adapted form:
# https://www.andrewnoske.com/wiki/Code_-_heatmaps_and_color_gradients
def heatmap_color(val, max_val):
    val = val / max_val
    NUM_COLORS = 2
    color = [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
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


def save_event(event: Event):
    return event.magnitude()


def resize_frame(image, width=1920):
    # Scale image
    image = imutils.resize(image, width=width)
    x = y = 0
    h = image.shape[0]
    w = image.shape[1]

    # Cut out the description
    image = image[y:(h - 20), x:w]
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

    contours = cv2.findContours(thresh.copy(),
                                cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    return contours


def extract_events(contours, event_list, frame_number, triger_treshold_area=5):
    for contour in contours:
        # if the contour is too small, ignore it
        if cv2.contourArea(contour) < triger_treshold_area:
            return
        # compute the bounding box for the contour
        (x, y, w, h) = cv2.boundingRect(contour)
        position = Coord(x, y)
        size = Coord(w, h)
        was_added = False
        new_event = EventInfo(frame_number, position, size)
        for event in event_list:
            if event.add_if_similar(new_event):
                was_added = True
        if not was_added:
            event_list.append(Event(new_event))


def update_events(event_list, frame_number, drop_inactive_time=3, triger_treshold=20):
    triggers = []
    for event in event_list:
        # remove events not active for more than 5 frames
        if abs(event.last_changed - frame_number) > drop_inactive_time:
            # Here we should save info if event is good enough
            if event.magnitude() < triger_treshold:
                return []

            start, end = event.path()
            if euc_distance(start, end) < 20:
                triggers.append(save_event(event))

            event_list.remove(event)
    return triggers


def annotate_frame(frame, event_list, draw_path=True, draw_box=False, draw_confidence=True, heatmap=(0, 20)):
    for event in event_list:
        if draw_path:
            rect = event.path()
            color = heatmap_color(len(event.positions), heatmap[1]) if heatmap else (0, 255, 0)
            cv2.line(frame, rect[0].tuple(), rect[1].tuple(), color, 3)

        if draw_box:
            rect = event.bounding_rect()
            cv2.rectangle(frame, rect[0].tuple(), rect[1].tuple(), (0, 255, 0), 2)

        if draw_confidence:
            cv2.putText(frame, f"Trigger count: {len(event.positions)}", rect[0].tuple(),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.35, (0, 0, 255), 1)
