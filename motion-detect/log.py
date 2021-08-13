from sys import stderr


def color(color):
    return lambda string: color + string + "\u001b[0m"


def err(msg):
    yellow = color("\u001b[33m")
    print(yellow("ERR:\t") + msg, file=stderr)


def critical(msg):
    red = color("\u001b[31m")
    print(red("CRITICAL:\t") + msg, file=stderr)


def info(msg):
    blue = color("\u001b[34;1m")
    print(blue("INFO:\t") + msg, file=stderr)
