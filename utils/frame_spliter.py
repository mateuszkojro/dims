#!/usr/bin/python
import cv2
import xml.etree.ElementTree as et
import logging as log
import sys
import argparse
import os
import sys


def get_video_info(filename):
    info_tree = et.parse(filename_base)
    root = info_tree.getroot()
    print(root.attrib['y'])


def split_frames(filename, output_dir):
    vidcap = cv2.VideoCapture(filename)
    success, image = vidcap.read()
    count = 0
    while success:
        image = draw_guides(image)
        # save frame as BMP file
        path = f"{output_dir}/{filename}.frame{count}.bmp"
        cv2.imwrite(path, image)
        success, image = vidcap.read()
        print(f'Reading frame and saving to {path}: {success}')
        count += 1


def draw_guides(img):

    deltay = deltax = 120
    for i in range(9):
        cv2.line(img, (0, i * deltay), (1920, i * deltay), (0, 0, 255))

    for i in range(16):
        cv2.line(img, (i * deltax, 0), (i * deltax, 1080), (0, 0, 255))

    return img


def init_argpasrse():
    parser = argparse.ArgumentParser(
        usage="Give input file as 1st arg and output path as 2nd",
        description="Split an video file into frames"
    )
    parser.add_argument("input_file", metavar="input_file",
                        type=str, help="Path to video file")
    parser.add_argument("output_directory", metavar="output_directory",
                        type=str, help="Output folder to save the files to")
    return parser


if __name__ == '__main__':
    args_parser = init_argpasrse()
    args = args_parser.parse_args()

    input_path = args.input_file
    output_dir = args.output_directory

    if not os.path.isfile(input_path):
        print('The specified file does not exsist')
        sys.exit()

    if not os.path.isdir(output_dir):
        print('Output direcotry does not exist')
        sys.exit()

    split_frames(input_path, output_dir)
