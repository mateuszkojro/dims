# I: Make a convec hull (https://docs.opencv.org/master/dd/d49/tutorial_py_contour_features.html)

# Q: do they alwas go in the straight line

import argparse
import math
import time

import cv2
import imutils

SHOW_RAW = False
SHOW_DELTA = True

DRAW_BOX = False
DRAW_PATH = True
DRAW_STATS = True
DRAW_CONFIDENCE = True

TARGET_WIDTH = 900

WITH_GAUSS = True
GAUSS_SIGMA = (3, 3)

TRIGER_AREA_TRESHOLD = 5
DROP_INACTIVE_TIME = 5


def calculate_center(position: (int, int), size: (int, int)) -> (float, float):
    x = position[0] + (size[0] / 2)
    y = position[1] + (size[1] / 2)
    return x, y


def euc_distance(pos1: (float, float), pos2: (float, float)) -> float:
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


class EventInfo:
    frame_no: int
    position: (int, int)
    size: (int, int)
    center: (float, float)

    def __init__(self, frame_number: int, event_position: (int, int), event_size: (int, int)):
        self.frame_no = frame_number
        self.position = event_position
        self.size = event_size
        self.center = calculate_center(event_position, event_size)


def are_similar(pos1: EventInfo, pos2: EventInfo, treshold: float) -> bool:
    # check the time between events
    if abs(pos1.frame_no - pos2.frame_no) > 5:
        return False
    # and how far apart they are
    if euc_distance(pos1.center, pos2.center) < treshold:
        return True
    return False


class Event:
    positions: [EventInfo]
    last_changed: int = 0

    def __init__(self, position: EventInfo):
        self.positions = []
        self.positions.append(position)
        self.last_changed = position.frame_no

    def bounding_rect(self) -> (int, int):
        min_x, min_y = self.positions[0].center
        max_x, max_y = self.positions[0].center
        for item in self.positions:
            event = item.center
            if event[0] < min_x:
                min_x = event[0]
            if event[1] < min_y:
                min_y = event[1]
            if event[0] > max_x:
                max_x = event[0]
            if event[1] > max_y:
                max_y = event[1]
        minimal = math.floor(min_x), math.floor(min_y)
        maximal = math.floor(max_x), math.floor(max_y)
        return minimal, maximal

    def path(self) -> (int, int):
        start = self.positions[0].position
        end = self.positions[-1].position
        return start, end

    def add_if_similar(self, position: EventInfo) -> bool:
        for item in self.positions:
            if are_similar(item, position, 15):
                self.positions.append(position)
                self.last_changed = position.frame_no
                return True
        return False


def init_argparse():
    parser = argparse.ArgumentParser(
        usage="Give the input file to be analyzed",
        description="Program detects events on the video recordings of the night sky"
    )
    # parser.add_argument("input_file", metavar="input_file",
    #                     type=str, help="File to be analyzed")
    # parser.add_argument("draw_path", metavar="draw_path", type=bool, help="Should draw a path of the event",
    #                     default=DRAW_PATH, required=False)
    # parser.add_argument("draw_stats", metavar="draw_stats", type=bool, help="Should display performance statistics",
    #                     default=DRAW_STATS, required=False)
    # parser.add_argument("draw_confidence", metavar="draw_confidence", type=bool,
    #                     help="Should display a confidenece of an event", default=DRAW_CONFIDENCE, required=False)
    #
    # parser.add_argument("show_raw", metavar="show_raw", type=bool,
    #                     help="Show raw input frames", default=SHOW_RAW, required=False)
    #
    # parser.add_argument("show_delta", metavar="show_delta", type=bool,
    #                     help="Show the diference between frames and status quo", default=DRAW_CONFIDENCE, required=False)
    # parser.add_argument("--draw_path", action="store_true", help="Should the path of the event be drawn")
    return parser


if __name__ == '__main__':
    arg_parser = init_argparse()
    input_path = "./file.avi"
    # args = arg_parser.parse_args()
    #
    # input_path = args.input_file
    #
    # SHOW_RAW = args.show_raw
    # SHOW_DELTA = args.show_delta
    #
    # DRAW_BOX = args.draw_box
    # DRAW_PATH = args.draw_path
    # DRAW_STATS = args.draw_stats
    # DRAW_CONFIDENCE = args.draw_confidence

    events: [Event] = []
    frame_no = 0
    time_sum = 0
    times = []
    video_capture = cv2.VideoCapture(input_path)

    frame = None
    first_frame = None
    running = True
    wait_time = 0

    while True:
        time.sleep(wait_time)
        start_time = time.monotonic()

        status, frame = video_capture.read()

        # Loop to the beginning when de file end
        if status is False:
            print("Rolling back to the beginning")
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 1)
            # events = []
            # frame_no = 0
            continue

        frame_no += 1
        frame = imutils.resize(frame, width=TARGET_WIDTH)

        if SHOW_RAW:
            raw = frame.copy()

        x = 0
        y = 0
        w = frame.shape[1]
        h = frame.shape[0]

        # Cut out the description
        frame = frame[y:(h - 20), x:w]

        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if WITH_GAUSS:
            grayscale = cv2.GaussianBlur(grayscale, GAUSS_SIGMA, 0)

        # if the first frame is None, initialize it
        if first_frame is None:
            first_frame = grayscale
            continue

        delta = cv2.absdiff(grayscale, first_frame)
        thresh = cv2.threshold(delta, 55, 255, cv2.THRESH_BINARY)[1]

        # on threshold image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < TRIGER_AREA_TRESHOLD:
                continue
            # compute the bounding box for the contour
            (x, y, w, h) = cv2.boundingRect(c)
            position = (x, y)
            size = (w, h)
            was_added = False
            new_event = EventInfo(frame_no, position, size)
            for event in events:
                if event.add_if_similar(new_event):
                    was_added = True
            if not was_added:
                events.append(Event(new_event))

        # loop over the contours
        idx = 0
        for event in events:
            # remove events not active for more than 5 frames
            if abs(event.last_changed - frame_no) > DROP_INACTIVE_TIME:
                events.remove(event)

            idx += 1
            if DRAW_PATH:
                rect = event.path()
                cv2.line(frame, rect[0], rect[1], (0, 255, 0), 3)

            if DRAW_BOX:
                rect = event.bounding_rect()
                cv2.rectangle(frame, rect[0], rect[1], (0, 255, 0), 2)

            if DRAW_CONFIDENCE:
                cv2.putText(frame, f"Trigger count: {len(event.positions)}", rect[0], cv2.FONT_HERSHEY_SIMPLEX,
                            0.35, (0, 0, 255), 1)

        end_time = time.monotonic()
        time_sum += end_time - start_time
        times.append(end_time - start_time)
        if DRAW_STATS:
            cv2.putText(frame,
                        f"Frame time: {(end_time - start_time):.3f}s ({math.floor(1 / (end_time - start_time))}fps), average {time_sum / frame_no:.3f}s per frame",
                        (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)

        if SHOW_RAW:
            cv2.imshow("Raw", raw)

        if SHOW_DELTA:
            cv2.imshow("Threshold", thresh)

        cv2.imshow("Annotated", frame)

        # Get the pressed key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            # plt.plot(times)
            # plt.imsave("./frame_time")
            break

        if key == ord('s'):
            time.sleep(0.1)
        if key == ord('+'):
            wait_time = wait_time + .02 if wait_time > 0.2 else 0
        if key == ord('-'):
            wait_time = wait_time + .02 if wait_time < 10 else 10
        if key == ord('r'):
            wait_time = 0
