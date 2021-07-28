#! /usr/bin/python3

import cv2
import time
import imutils

from CustomAlgorithm import *

INPUT_PATH = "./file.avi"
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
DROP_INACTIVE_TIME = 5

EVENT_TRESHOLD = 10


def main():
    events: [Event] = []
    frame_no = 0
    time_sum = 0
    times = []
    video_capture = cv2.VideoCapture(INPUT_PATH)

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

        frame = prepare_image(frame, TARGET_WIDTH)

        if WITH_GAUSS:
            frame = cv2.GaussianBlur(frame, GAUSS_SIGMA, 0)

        # if the first frame is None, initialize it
        if first_frame is None:
            first_frame = frame
            continue

        delta = cv2.absdiff(frame, first_frame)
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
            position = Coord(x, y)
            size = Coord(w, h)
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
                color = heatmap_color(len(event.positions), EVENT_TRESHOLD) if HEATMAP else (0, 255, 0)
                cv2.line(frame, rect[0].tuple(), rect[1].tuple(), color, 3)

            if DRAW_BOX:
                rect = event.bounding_rect()
                cv2.rectangle(frame, rect[0].tuple(), rect[1].tuple(), (0, 255, 0), 2)

            if DRAW_CONFIDENCE:
                cv2.putText(frame, f"Trigger count: {len(event.positions)}", rect[0].tuple(), cv2.FONT_HERSHEY_SIMPLEX,
                            0.35, (0, 0, 255), 1)

        end_time = time.monotonic()
        time_sum += end_time - start_time
        times.append(end_time - start_time)
        if DRAW_STATS:
            cv2.putText(frame,
                        f"Frame time: {(end_time - start_time):.3f}s ({math.floor(1 / (end_time - start_time))}fps), average {time_sum / frame_no:.3f}s per frame",
                        (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)

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


if __name__ == '__main__':
    main()
