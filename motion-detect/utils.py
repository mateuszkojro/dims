import cv2
import os


def show_coresponding_image(path):
    image = cv2.imread(path[:-4] + "M.bmp")
    image = imutils.resize(image, width=600)
    cv2.imshow("Ufo capture", image)


def draw_grid(frame):
    h = frame.shape[0]
    w = frame.shape[1]

    for x in range(16):
        cv2.line(frame, (x * 120, 0), (x * 120, h), (0, 0, 100), 1)
    for y in range(9):
        cv2.line(frame, (0, y * 120), (w, y * 120), (0, 0, 100), 1)


def get_setting(setting, default):
    result = default
    if setting in os.environ:
        result = int(os.environ[setting])
        print(f"{setting}:{result}")

    return result


def save(all_triggers):
    numpy_array = np.array(all_triggers, dtype=object)
    np.save("out.npy", all_triggers, allow_pickle=True)

    rows = []

    for clip in all_triggers:
        for trigger in clip:
            start, end = trigger.bounding_box
            rows.append(
                [trigger.filename, trigger.start_frame, trigger.end_frame,
                 start.x, start.y, end.x, end.y, trigger.length, trigger.magnitude
                 ])

    df = pd.DataFrame(
        data=rows,
        columns=["file", "start_frame", "end_frame", "box_up_left_x",
                 "box_up_left_y", "box_down_right_x",
                 "box_down_right_y", "length", "count"])

    df.to_csv("out.csv")
