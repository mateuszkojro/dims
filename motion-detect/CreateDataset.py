import pyximport
import cython
import time
import cv2
import imutils
import sys
import multiprocessing as mp
import random

import utils
from FileCrawler import StopCrawl, recursive_file_list
import CustomAlgorithm as ca

pyximport.install()


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)  # Deactivate negative indexing.
def analyze(path, debug=False):
    print(f"Analyzing: {path}")
    triggers = []
    events = []
    frame_number = 0
    video_capture = cv2.VideoCapture(path)
    reference_frame = None
    start_time = time.monotonic()
    while True:

        status, frame = video_capture.read()

        if not status:
            new_triggers = ca.on_destroy(events)
            if new_triggers is not None:
                triggers += new_triggers
            break

        resized_frame = ca.resize_frame(frame)

        preprocessed = ca.preprocess_frame(resized_frame)

        # if the first frame is None, initialize it
        if reference_frame is None:
            reference_frame = preprocessed
            continue

        contours = ca.get_contours(preprocessed, reference_frame)

        ca.extract_events(contours, events, frame_number, filename=path)

        new_triggers = ca.update_events(events, frame_number)

        if new_triggers is not None:
            triggers += new_triggers

        if debug:
            ca.annotate_frame(resized_frame, events)

            utils.draw_grid(resized_frame)

            preview = imutils.resize(resized_frame, width=1500)
            cv2.imshow("Preview", preview)
            # Get the pressed key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                new_events = ca.on_destroy(events)
                if new_events is not None:
                    triggers = new_events
                break
            if key == ord('s'):
                with open("interesting", "a") as f:
                    f.write(path + frame_number + "\n")
                print("INFO: Saved image")

        frame_number += 1

        now = time.monotonic()
        # if file takes more than 5 minutes stop
        if now - start_time > 5 * 60:
            print(f"ERR: Analyzing file took too long - stopping ({path})")
            new_triggers = ca.on_destroy(events)
            if new_triggers is not None:
                triggers += new_triggers
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return triggers


if __name__ == '__main__':

    debug = utils.get_setting("DEBUG", False)
    threads = utils.get_setting("THREADS", mp.cpu_count() - 1)
    multithreading = utils.get_setting("MULTITHREADING", True)

    path = sys.argv[1] \
        if len(sys.argv) > 1 \
        else "/run/media/mateusz/Seagate Expansion Drive/all"

    file_list = recursive_file_list(path)

    if debug:
        random.shuffle(file_list)
        file_list = file_list[:10]

    def apply_analyze(file):
        return analyze(file, debug=debug)

    all_triggers = []
    if multithreading:
        with mp.Pool(threads) as p:
            all_triggers = p.map(apply_analyze, file_list)
    else:
        for file in file_list:
            all_triggers += analyze(file)

    utils.save(all_triggers)
