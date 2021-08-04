import pyximport

import utils
import time
import cv2
import imutils
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from FileCrawler import StopCrawl, crawl, recursive_file_list
import CustomAlgorithm as ca

import multiprocessing as mp
from typing import List

import os
import sys

pyximport.install()


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
                raise StopCrawl
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

    path = sys.argv[1] if len(
        sys.argv) > 1 else "/run/media/mateusz/Seagate Expansion Drive/20190330Subset/N1"

    file_list = recursive_file_list(path)

    if debug:
        import random

        file_list = file_list[:5]

    all_triggers = []

    def apply_analyze(file):
        return analyze(file, debug=debug)

    if multithreading:
        with mp.Pool(threads) as p:
            all_triggers = p.map(apply_analyze, file_list)
    else:
        for file in file_list:
            all_triggers += analyze(file)

    uttils.save(all_triggers)
