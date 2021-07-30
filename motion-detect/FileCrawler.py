import os

def get_ext(path):
    return os.path.splitext(path)[-1]

def crawl(path, function, extension=".avi"):
    result = []
    size = len([file for file in os.listdir(path) if get_ext(file) == ".avi"])
    for i, obj in enumerate(os.listdir(path)):

        abs_path = os.path.abspath(path + "/" + obj)
        if os.path.isdir(abs_path):
            print("Hello there")
            result += crawl(abs_path, function)
        else:
            print(f"Analyzing file {i}/{size} ({i/size * 100}%)")
            # ext = os.path.splitext(abs_path)[-1]
            if get_ext(abs_path) == extension:
                result += function(abs_path)
        if i == 20:
            break
    return result


if __name__ == '__main__':
    f = lambda file: print(file)
    crawl(".", f)
