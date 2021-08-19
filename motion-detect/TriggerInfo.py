import cython
import numpy as np
import matplotlib.pyplot as plt
import cv2
from typing import Tuple

import skimage.measure

from utils import Vec2, get_frames, combine_frames, resize_frame

from Trigger import Trigger, get_section

from log import err


# @dataclass(frozen=True)
class TriggerInfo:
    event: Event
    length: cython.int
    filename: str
    start_frame: cython.int
    end_frame: cython.int
    event_count: cython.int
    bounding_box: Tuple[Vec2]
    line_fit: float

    def __init__(self,
                 event,
                 length,
                 filename,
                 start_frame,
                 end_frame,
                 event_count,
                 bounding_box,
                 line_fit=None):

        self.event = event
        self.length = length
        self.filename = filename
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.event_count = event_count
        self.bounding_box = bounding_box
        self.line_fit = line_fit

    # TODO: Test that to be sure
    def get_section(self):
        x, y = self.get_center()

        x = x // 120
        y = y // 120

        return int(y * (1920 // 120)) + int(x)

    # TODO: Test that to be sure
    def get_center(self):
        min_x, min_y, max_x, max_y = self.bounding_box
        x = min_x + abs(max_x - min_x) / 2
        y = min_y + abs(max_y - min_y) / 2

        return Vec2(x, y)

    def get_uid(self):
        filename = self.filename.replace('/', '@')
        return f"{filename}_{self.get_section()}_{self.start_frame}_{self.end_frame}"

    def section_cutout(self):
        """ 
        Go through all frames on which event was detected than cutout the section of the image 
        """

        frames = get_frames(self.filename, self.start_frame, self.end_frame)
        section = self.get_section()
        min_x = (((section % (1920 // 120))) * 120) - 1
        min_y = (((section // (1920 // 120))) * 120) - 1
        max_x = (min_x + 120) - 1
        max_y = (min_y + 120) - 1

        frames = [[frame[min_y:max_y, min_x:max_x]] for frame in frames]
        return frames

    def center_rect(self):
        pass

    def region_props(self):
        frames = self.section_cutout()
        frames = combine_frames(frames)
        props = skimage.measure.regionprops(frames)
        return props

    def animate(self):
        import matplotlib.animation as animation
        from IPython.core.display import HTML, display

        imgs = self.cutout()  # some array of images
        # imgs = [[frame[min_y:max_y, min_x:max_x]] for frame in frames]
        animation_frames = []  # for storing the generated images

        fig = plt.figure()
        for img in imgs:
            # frames.append([plt.imshow(img[i], cmap=cm.Greys_r, animated=True)])
            animation_frames.append([plt.imshow(img[0], animated=True)])

        ani = animation.ArtistAnimation(fig,
                                        animation_frames,
                                        interval=100,
                                        blit=True,
                                        repeat_delay=10)
        # ani.save('movie.mp4')
        display(HTML(ani.to_jshtml()))

    def calculate_moment(self):
        frames = []
        capture = cv2.VideoCapture(self.filename)
        capture.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        for _ in range(self.end_frame - self.start_frame):
            status, frame = capture.read()
            if not status:
                raise Exception("Cv read frame failed")

            frames.append(frame)

        combined = self.combine_frames(frames)

        raise Exception("Onl partialy implemented")

    def  get_frame_chunk(self):
        raise Exception("Not implemented")

    @staticmethod
    def from_csv_row(row):
        row = row[1:]
        return TriggerInfo(filename=row[0],
                           start_frame=int(row[1]),
                           end_frame=int(row[2]),
                           bounding_box=(row[3], row[4], row[5], row[6]),
                           length=row[7],
                           event_count=row[8],
                           line_fit=[0],
                           event=None)

    def show(self) -> None:
        frames = []
        capture = cv2.VideoCapture(self.filename)
        capture.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        for i in range(self.end_frame - self.start_frame):
            status, frame = capture.read()
            frames.append(frame)

        combined = self.combine_frames(frames)

        if combined is None:
            print("Empty frame")
            return

        # frame = combined

        for point in self.event.positions:
            frame = cv2.circle(frame, point.center(), 1, (0, 255, 0), 1)

        frame = resize_frame(frame)
        left_top, right_bottom = self.bounding_box

        plt.imshow(frame)
        plt.show()


    def to_common_trigger(self):

        return Trigger(
            filename=self.filename,
            start_frame=self.start_frame,
            end_frame=self.end_frame,
            bounding_rect=self.bounding_box,
            section=self.get_section(),
            line_fit=self.line_fit,
            length=None,
            time_block=self.start_frame % 10
        )