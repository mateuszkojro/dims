# Q: do they alwas go in the straight line

import time
import math
import cv2
import imutils

show_raw = True


def calculate_center(position: (int, int), size: (int, int)) -> (float, float):
    x = position[0] + (size[0] / 2)
    y = position[1] + (size[1] / 2)
    return (x, y)


def euc_distance(pos1: (float, float), pos2: (float, float)):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[0] - pos2[0]) ** 2)


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
    if euc_distance(pos1.center, pos2.center) < treshold:
        return True
    return False


class Event:
    positions: [EventInfo]

    def __init__(self, position: EventInfo):
        self.positions.append(position)

    def add_if_similar(self, position: EventInfo) -> bool:
        for item in self.positions:
            if are_similar(item, position, 5):
                self.positions.append(position)
                return True
        return False


if __name__ == '__main__':
    video_capture = cv2.VideoCapture("./file.avi")

    frame = None
    first_frame = None
    running = True
    while True:
        status, frame = video_capture.read()

        # Loop to the begining when de file end
        if status is False:
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 1)
            continue

        frame = imutils.resize(frame, width=850)

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
        thresh = cv2.threshold(delta, 75, 255, cv2.THRESH_BINARY)[1]

        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        print("Cntrs", cnts)

        # loop over the contours
        idx = 0
        for c in cnts:
            idx += 1
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 5:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"obj{idx}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        if idx > 0:
            time.sleep(10)
            print(f"Objects on the image:{idx}")

        cv2.imshow("Annotated", frame)
        cv2.imshow("Treshhold", thresh)

        if show_raw:
            cv2.imshow("Raw", raw)

        # Get the pressed key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('s'):
            time.sleep(0.1)
