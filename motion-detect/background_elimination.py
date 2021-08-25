def remove_bg(frame, deviation=2, div_sqr=(50, 50)):
    """
    Removes background from the frame based on splitting the frame into smaller
    squares and the eliminating pixels based on std deviation

    :param      frame:      Frame to be processed
    :type       frame:      np.array
    :param      deviation:  Multiple of standard deviations to remove
    :type       deviation:  int
    :param      div_sqr:    Size of subdivided square
    :type       div_sqr:    Rect

    :returns:   Frame with the background removed
    :rtype:     np.array
    """
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    h_original, w_original = frame.shape
    parts = frame.reshape((-1, div_sqr.y.int(), div_sqr.x.int()))

    n, h, w = parts.shape

    for idx, part in enumerate(parts):
        colors = part.flatten()

        std_dev = np.std(colors)
        counts = np.bincount(colors)
        most_freq = np.argmax(counts)

        def filter(color):
            return color if color > most_freq + std_dev * deviation else 0

        parts[idx] = np.fromiter((filter(c) for c in colors),
                                 dtype=int).reshape(part.shape)

    return parts.reshape((h_original, w_original))


def apply_median_filtter(frame, kernel_size=3):
    """
    Applays a median filter on given frame

    :param      frame:        The frame
    :param      kernel_size:  The kernel size

    :returns:   Filtered frame
    """
    return cv2.medianBlur(frame, 3)
