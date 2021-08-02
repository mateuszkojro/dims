import os
import random


def get_ext(path):
    return os.path.splitext(path)[-1]


def crawl(path, function, extension=".avi", debug=False):
    result = []
    size = len([file for file in os.listdir(path) if get_ext(file) == ".avi"])
    i = 0
    file_list = os.listdir(path)
    if debug:
        random.shuffle(file_list)
    for obj in file_list:
        abs_path = os.path.abspath(path + "/" + obj)
        if os.path.isdir(abs_path):
            print("Hello there")
            result += crawl(abs_path, function)
        else:
            # ext = os.path.splitext(abs_path)[-1]
            if get_ext(abs_path) == extension:
                print(f"Analyzing file {i}/{size} ({i / size * 100:2}%)")
                result += function(abs_path, debug=debug)
                i += 1
        if debug and i ==6:
            break
    return result


if __name__ == '__main__':
    f = lambda file: print(file)
    crawl(".", f)
