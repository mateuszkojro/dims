# Q: do they alwas go in the straight line

import time
import math
import matplotlib.pyplot as plt
import cv2
import imutils

show_raw = False


def calculate_center(position: (int, int), size: (int, int)) -> (float, float):
    x = position[0] + (size[0] / 2)
    y = position[1] + (size[1] / 2)
    return (x, y)


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


events: [Event] = []
frame_no = 0
time_sum = 0
times = []
if __name__ == '__main__':
    video_capture = cv2.VideoCapture("./file.avi")

    frame = None
    first_frame = None
    running = True

    while True:

        start_time = time.monotonic()

        status, frame = video_capture.read()

        # Loop to the begining when de file end
        if status is False:
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 1)
            # events = []
            # frame_no = 0
            continue

        frame_no += 1
        frame = imutils.resize(frame, width=1920)

        if show_raw:
            raw = frame.copy()

        x = 0
        y = 0
        w = frame.shape[1]
        h = frame.shape[0]

        # Cut out the description
        frame = frame[y:(h - 20), x:w]

        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grayscale = cv2.GaussianBlur(grayscale, (3, 3), 0)

        # if the first frame is None, initialize it
        if first_frame is None:
            first_frame = grayscale
            continue

        delta = cv2.absdiff(grayscale, first_frame)
        thresh = cv2.threshold(delta, 55, 255, cv2.THRESH_BINARY)[1]

        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # print("Cntrs", cnts)

        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 5:
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
            if abs(event.last_changed - frame_no) > 5:
                events.remove(event)
            idx += 1
            rect = event.path()
            cv2.line(frame, rect[0], rect[1], (0, 255, 0), 3)
            # rect = event.bounding_rect()
            # cv2.rectangle(frame, rect[0], rect[1], (0, 255, 0), 2)
            cv2.putText(frame, f"Detection confidence: {len(event.positions)}", rect[0], cv2.FONT_HERSHEY_SIMPLEX,
                        0.35, (0, 0, 255), 1)
        if idx > 0:
            # time.sleep(10)
            # print(f"Objects on the image:{idx}")
            pass

        end_time = time.monotonic()
        time_sum += end_time - start_time
        times.append(end_time - start_time)
        cv2.putText(frame,
                    f"Frame time: {(end_time - start_time):.3f}s ({math.floor(1 / (end_time - start_time))}fps), average {time_sum / frame_no:.3f}s per frame",
                    (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

        if show_raw:
            cv2.imshow("Raw", raw)
        cv2.imshow("Annotated", frame)
        # cv2.imshow("Treshhold", thresh)

        # Get the pressed key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            # plt.plot(times)
            # plt.imsave("./frame_time")
            break
        if key == ord('s'):
            time.sleep(0.1)
