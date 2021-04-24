"""
based on:
https://pytorch.org/tutorials/beginner/data_loading_tutorial.html
"""

from __future__ import print_function, division
import pandas as pd

import os
import torch
import pandas as pd
from skimage import io, transform
import numpy as np
import re
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils

# Ignore warnings
import warnings


def load_ppm(path):
    file = open(path, "r")
    data = re.split(r'[ \n]', str(file.read()))
    image_format = data[0]
    size_x = int(data[1])
    size_y = int(data[2])
    color_depth = int(data[1])
    data = list(filter(lambda val: val != '', data))
    data = np.array(data[4:], dtype=np.float32)
    data = np.reshape(data, (1080, 1920))
    return data


class ImageDataset(Dataset):
    def __init__(self, csv_file, root_dir, transform=None):
        self.data_frame = pd.read_csv(csv_file)
        # self.data_frame = self.data_frame.drop("Unnamed: 3", 1)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.data_frame)

    def __repr__(self):
        return self.data_frame.__repr__()

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_name = os.path.join(self.root_dir, self.data_frame.iloc[idx, 0])
        image = load_ppm(img_name)
        landmarks = self.data_frame.iloc[idx, 1:]
        landmarks = np.array([landmarks])
        landmarks = landmarks.astype(np.float32).reshape(-1, 2)
        # landmarks = np.array(landmarks)
        sample = {'image': image, 'landmarks': landmarks}
        if self.transform:
            sample = self.transform(sample)

        return sample


class ToTensor(object):
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, sample):
        image, landmarks = sample['image'], sample['landmarks']

        # swap color axis because
        # numpy image: H x W x C
        # torch image: C X H X W
        # image = image.transpose((2, 0, 1))
        return {'image': torch.from_numpy(image),
                'landmarks': torch.from_numpy(landmarks)}


if __name__ == '__main__':
    imset = ImageDataset(csv_file="./data.csv", root_dir="./images")
    print(imset[2])
