import cython
import numpy as np
import matplotlib.pyplot as plt
import cv2

from log import err

from typing import Tuple
from utils import Vec2, get_frames, combine_frames, resize_frame


# @dataclass(frozen=True)
class TriggerInfo:
    event:Event
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
        start, end = self.bounding_box
        x = start.x + abs(end.x - start.x) / 2
        y = start.y + abs(end.y - start.y) / 2

        x = x // 120
        y = y // 120

        return int(y * (1920 // 120)) + int(x)

    # TODO: Test that to be sure
    def get_center(self):
        start, end = self.bounding_box
        x = start.x + abs(end.x - start.x) / 2
        y = start.y + abs(end.y - start.y) / 2
        return Vec2(x, y)

    def get_uid(self):
        filename = self.filename.replace('/', '@')
        return f"{filename}_{self.get_section()}_{self.start_frame}_{self.end_frame}"

    def section_cutout(self):
        frames = get_frames(self.filename, self.start_frame, self.end_frame)
        section = self.get_section()
        min_x = (((section % (1920 // 120))) * 120) - 1
        min_y = (((section // (1920 // 120))) * 120) - 1
        max_x = (min_x + 120) - 1
        max_y = (min_y + 120) - 1
        print(min_y)

        frames = [[frame[min_y:max_y, min_x:max_x]] for frame in frames]
        return frames

    def region(self):
        raise Exception("Not implemented")

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
        for i in range(self.end_frame - self.start_frame):
            status, frame = capture.read()
            frames.append(frame)

        combined = self.combine_frames(frames)

        raise Exception("Onl partialy implemented")

    def get_frame_chunk(self):
        raise Exception("Not implemented")

    @staticmethod
    def from_csv_row(row):
        row = row[1:]
        return TriggerInfo(filename=row[0],
                           start_frame=int(row[1]),
                           end_frame=int(row[2]),
                           bounding_box=(Vec2(row[3],
                                              row[4]), Vec2(row[5], row[6])),
                           length=row[7],
                           event_count=row[8],
                           line_fit=[0],
                           event=None)

    @staticmethod
    def combine_frames(frames):
        if len(frames) == 0:
            return None

        # print(f"{np.ndim(frames)}")
        if len(frames) > 50:
            err("to many frames")

            frames = frames[:50]
        result = np.amax(frames, axis=1)

        return result

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
            frame = cv2.circle(frame,
                               point.center(), 1, (0, 255, 0), 1)

        frame = resize_frame(frame)
        left_top, right_bottom = self.bounding_box

        plt.imshow(frame)
        plt.show()
