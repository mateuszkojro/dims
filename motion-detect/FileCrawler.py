import os
import random


class StopCrawl(Exception):
    pass


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
        if debug and i == 10:
            break
    return result


def recursive_file_list(path, extension=".avi", debug=False):
    initial_path = path
    print(initial_path)
    nodes = os.listdir(path)

    collected_files = []

    for node in nodes:
        abs_path = initial_path + "/" + node

        if os.path.isdir(abs_path):
            print(f"INFO: Found subdirectory: {abs_path}")
            collected_files += recursive_file_list(abs_path)
            continue

        if get_ext(node) == ".avi":
            collected_files.append(abs_path)

    return collected_files


if __name__ == '__main__':
    print(recursive_file_list("."))
