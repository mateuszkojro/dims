from collections import namedtuple
import pathlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2

Vec2 = namedtuple('Vec2', ['x', 'y'])

Rect = namedtuple('Rect', ['min_x', 'min_y', 'max_x', 'max_y'])

Trigger = namedtuple('Trigger', [
    'filename', 'length', 'start_frame', 'end_frame', 'bounding_rect',
    'section', 'line_fit'
])


def _assert(condition: bool, msg: str):
    """
    Assertion that survives cython compilation
    """
    if not condition:
        print("Assertion failed: ")
        raise Exception(msg)


def _get_frames(path, start=None, stop=None) -> np.array:
    """
    Read frames from given file you can pass start and end frame
    """
    capture = cv2.VideoCapture(path)

    start = start if start is not None else 0
    stop = stop if stop is not None else capture.get(cv2.CAP_PROP_FRAME_COUNT -
                                                     1)

    N = stop - start + 1

    capture.set(cv2.CAP_PROP_POS_FRAMES, start)
    frames = np.empty(N)

    for i in range(N):
        status, frame = capture.read()
        _assert(status, "Error reading frame")
        frames[i] = frame

    return frames


def read_row(row, base_path="./") -> Trigger:
    """ Convert row of a df to Trigger obj """
    # FIXME: Path conversion
    base_path = pathlib.Path(base_path)
    file = pathlib.Path(row["file"])
    # file = base_path / file

    return Trigger(filename=file,
                   length=row["length"],
                   start_frame=row["start_frame"],
                   end_frame=row["end_frame"],
                   bounding_rect=row["bounding_rect"],
                   section=row["section"],
                   line_fit=row["line_fit"])


def read_df(df: pd.DataFrame, base_path="./") -> np.array:
    """ Convert df int numpy arry containing triggers """
    N = df.shape[0]
    all_triggers = np.empty(dtype=object)

    for idx, row in df.iterrows():
        all_triggers[idx] = read_row(row, base_path)

    return all_triggers


def combine_frames(frame_list: np.array):
    """ 
    Get the arr of frames and combine them into one (by getting max pixel value) 
    """
    return np.amax(frame_list, axis=0)


def cut_rect_from_frame(frame: np.array, r: Rect) -> np.array:
    """ Cuts out the rect from given frame """
    return frame[r.min_y:r.max_y + 1, r.min_x:r.max_x + 1]


def get_center(trigger: Trigger):
    """ Calculate center of a @Trigger """
    min_x, min_y, max_x, max_y = trigger.bounding_rect
    x = min_x + abs(max_x - min_x) / 2
    y = min_y + abs(max_y - min_y) / 2

    return Vec2(x, y)


def get_section(trigger: Trigger) -> int:
    """ Calculate number of a section containing center of the @Trigger """
    x, y = get_center(trigger)

    x = x // 120
    y = y // 120

    return int(y * (1920 // 120)) + int(x)


def section_rect(trigger: Trigger) -> Rect:
    """ Cutout section Rect """
    section = trigger.section
    min_x = (((section % (1920 // 120))) * 120) - 1
    min_y = (((section // (1920 // 120))) * 120) - 1
    max_x = (min_x + 120) - 1
    max_y = (min_y + 120) - 1
    return Rect(min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)


def center_rect(trigger: Trigger, size: Vec2) -> Rect:
    """ Creates Rect with some offeset from the center """
    center = get_center(trigger)
    min_x = center.x - size.x
    max_x = center.x + size.x
    min_y = center.y - size.y
    max_y = center.y + size.y
    return Rect(min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)


def get_frames(trigger: Trigger) -> np.array:
    """ Get frames from Trigger """
    return _get_frames(trigger.filename, trigger.start_frame,
                       trigger.end_frame)


def animate(frame_list: np.array, interactive=True, filename="out.mp4"):
    """ Given an array of frames creates and animation """
    import matplotlib.animation as animation
    animation_frames = []  # for storing the generated images
    fig = plt.figure()
    for frame in frame_list:
        animation_frames.append([plt.imshow(frame[0], animated=True)])

    ani = animation.ArtistAnimation(fig,
                                    animation_frames,
                                    interval=100,
                                    blit=True,
                                    repeat_delay=10)

    if interactive:
        from IPython.core.display import HTML, display
        return HTML(ani.to_jshtml())

    else:
        ani.save(filename)
        return None


def mark_rect(frame: np.array, rect: Rect):
    """ Draw a rectangle on a bigger image """
    raise NotImplementedError


def get_id(trigger: Trigger):
    """ Unique id of an event """
    raise NotImplementedError