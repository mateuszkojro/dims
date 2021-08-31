
"""
Creatre gifs from triggers
"""

import numpy as np
import pandas as pd
import multiprocessing as mp
import sys

import log
from Trigger import *


def gen_gif(trigger, out_filename, size=None):
    b_box = trigger.bounding_rect
    frames = get_frames(trigger)
    c_rect = center_rect(trigger, Vec2(100, 100))
    frames = [cut_rect_from_frame(
        mark_rect(frame, b_box, thickness=1), c_rect) for frame in frames]
    animate(frames, interactive=False, file=out_filename, size=size)


def aplyer(trigger):
    log.info(str(trigger.file))
    out_filename = output_folder + '/' + \
        str(trigger.file).replace('/', '_')
    gen_gif(trigger, out_filename + ".gif")


if __name__ == '__main__':
    dataset_file = sys.argv[1]
    output_folder = sys.argv[2]

    df = pd.read_csv(dataset_file)
    triggers = read_df(df)

    with mp.Pool(16) as p:
        p.map(aplyer, triggers)