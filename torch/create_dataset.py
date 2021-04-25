"""
Simple loader for PBM and PPM encoded images
based on:
https://pytorch.org/tutorials/beginner/data_loading_tutorial.html
"""

from __future__ import print_function, division
import os
import torch
import pandas as pd
import numpy as np
import re
from torch.utils.data import Dataset

# Ignore warnings
import warnings


def load_pbm(path):
    file = open(path, "r")
    data = re.split(r'[ \n]', str(file.read()))  # remove all the \n and " "
    image_format = data[0]
    size_x = int(data[1])
    size_y = int(data[2])
    color_depth = int(data[1])
    data = list(filter(lambda val: val != '', data))  # filter all the empty strings
    data = np.array(data[4:], dtype=np.float32)
    data = np.reshape(data, (1080, 1920))
    return data


class ImageDataset(Dataset):
    def __init__(self, csv_file, root_dir, file_format="PBM", transform=None):
        self.data_frame = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

        # Chose the right loader
        if file_format == "PBM":
            self.image_parser = load_pbm
        elif file_format == "PPM":
            raise Exception("Not implemented yet")
        else:
            raise Exception("File format not supported")

    def __len__(self):
        return len(self.data_frame)

    def __repr__(self):
        return self.data_frame.__repr__()

    def __getitem__(self, idx):
        """ Get item at idx """
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_name = os.path.join(self.root_dir, self.data_frame.iloc[idx, 0])
        image = self.image_parser(img_name)
        landmarks = self.data_frame.iloc[idx, 1:]
        landmarks = np.array([landmarks])
        landmarks = landmarks.astype(np.float32).reshape(-1, 2)
        # landmarks = np.array(landmarks)
        sample = {'image': image, 'landmarks': landmarks}
        if self.transform:
            sample = self.transform(sample)

        return sample


class ToTensor(object):
    """ Converts the image(np.array) to torch.tensor """

    def __call__(self, sample):
        image, landmarks = sample['image'], sample['landmarks']

        # swap color axis because
        # numpy image: H x W x C
        # torch image: C X H X W
        # image = image.transpose((2, 0, 1))
        return {'image': torch.from_numpy(image),
                'landmarks': torch.from_numpy(landmarks)}


if __name__ == '__main__':
    image_set = ImageDataset(csv_file="./data.csv", root_dir="./images", file_format="PPM")
    print(image_set[2])
