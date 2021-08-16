import pyximport
import cython
import time
import cv2
import imutils
import sys
import multiprocessing as mp
import random
import numpy as np

import utils
from FileCrawler import StopCrawl, recursive_file_list
from log import *

import CustomAlgorithm as ca

# pyximport.install(pyimport=True)


@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)  # Deactivate negative indexing.
def analyze(path, debug=False):
    try:
        info(f"Analyzing: {path}")
        # triggers = np.array([])
        # events = np.array([])
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
                    info("Saved image")

            frame_number += 1

            now = time.monotonic()
            # if file takes more than 5 minutes stop
            if now - start_time > 5 * 60:
                err(f"Analyzing file took too long - stopping ({path})")
                new_triggers = ca.on_destroy(events)
                if new_triggers is not None:
                    triggers += new_triggers
                break
        video_capture.release()
        cv2.destroyAllWindows()
    except Exception as error:
        critical(f"analysys failed for file: {path} with: {error}")
        video_capture.release()
        cv2.destroyAllWindows()
        return triggers
    return triggers


if __name__ == '__main__':


    debug = utils.get_setting("DEBUG", False)
    threads = utils.get_setting("TH", mp.cpu_count() - 1)
    multithreading = utils.get_setting("MULTITHREADING", True)
    cv_threads = utils.get_setting("CV_TH", 2)

    # TODO: Lets check that on the other computer
    cv2.setNumThreads(cv_threads)

    path = sys.argv[1] \
        if len(sys.argv) > 1 \
        else "/media/mateusz/Seagate Expansion Drive/all"

    out_path = sys.argv[2] \
        if len(sys.argv) > 2 \
        else "out"

    file_list = recursive_file_list(path)

    if debug:
        # random.shuffle(file_list)
        file_list = file_list[700:710]

    info(f"Found {len(file_list)} avi files")

    def apply_analyze(file):
        return analyze(file, debug=debug)

    all_triggers = []
    if multithreading:
        with mp.Pool(threads) as p:
            all_triggers = p.map(apply_analyze, file_list)
    else:
        for file in file_list:
            all_triggers += analyze(file)

    utils.save(all_triggers, out_path)

    print()
    print("-" * 30)
    print("\t" + "Complete!")
    print("-" * 30)
    print()
    print("\a")
