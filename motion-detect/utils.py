import cv2


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
