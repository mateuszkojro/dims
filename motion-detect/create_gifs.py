
"""
Creatre gifs from triggers
"""

import numpy as np
import pandas as pd
import multiprocessing as mp
import hashlib
import sys
import os

import base64

import log
from Trigger import *

import FileCrawler
import os
import numpy as np
import sys

h = hashlib.new('md5')


def gen_gif(trigger, out_filename, size=None):
    b_box = trigger.bounding_rect
    frames = get_frames(trigger)
    c_rect = center_rect(trigger, Vec2(100, 100))
    frames = [cut_rect_from_frame(
        mark_rect(frame, b_box, thickness=1), c_rect) for frame in frames]
    animate(frames, interactive=False, file=out_filename, size=size)


def aplyer(trigger):

    t_id = get_id(trigger)
    # h.update(t_id.encode('ascii'))
    # code = h.hexdigest()
    code = t_id

    out_filename = output_folder + "/" + str(code)

    if os.path.isfile(out_filename + ".gif") and os.path.isfile(out_filename + ".npy"):
        log.err("skiping" + code)
        return

    log.info(str(trigger.file))

    gen_gif(trigger, out_filename + ".gif")

    np.save(out_filename + ".npy", np.array(trigger))
    # with open(out_filename + ".txt", "w+") as f:
    #     f.write(t_id)


if __name__ == '__main__':
    dataset_file = sys.argv[1]
    output_folder = sys.argv[2]

    df = pd.read_csv(dataset_file)
    triggers = read_df(df)

    with mp.Pool(32) as p:
        p.map(aplyer, triggers)
