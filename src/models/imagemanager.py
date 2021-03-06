import sys
import skimage
import skimage.transform
from skimage.color import rgb2gray
import imageio
from pathlib import Path
import numpy as np
import random

sys.path.insert(0, '..')
from filemanager import get_images


class Manager:
    def __init__(self):
        self.test_offset = 0
        self.train_offset = 0

    def imread(self, path):
        return imageio.imread(path)

    def get_resize_gray_img(self, path):
        return rgb2gray(self.get_resize_img(path))

    def get_resize_img(self, path, dim=28, channel=3):
        img = self.imread(path)
        return skimage.transform.resize(img, [dim, dim, channel], mode="reflect")

    def get_flatten_img(self, path, dim=28, invert_gray=False):
        if invert_gray:
            img = 255 - self.imread(path)
        else:
            img = self.imread(path)
        return rgb2gray(skimage.transform.resize(img, [dim, dim], mode="reflect"))

    def load_data(self, path, ratio=0.1):
        p = Path(path)
        labels_path = p / "labels" / "labels.csv"
        self.labels = self.create_label_obj(labels_path)
        image_dir = p / "images"
        images = get_images(image_dir)
        random.shuffle(images)
        n_images = len(images)

        print("# of images: ", len(images))
        print("test/train: ", ratio)

        n_test = int(n_images * ratio)

        self.test_images = images[:n_test]
        self.train_images = images[n_test:]


        self.n_test = len(self.test_images)
        self.n_train = len(self.train_images)

        print("test/train: {}/{} = {:.4}".format(
            self.n_test, self.n_train, self.n_test/self.n_train))

    def create_label_obj(self, path):
        labels = {}
        mapping_dic = {}

        with open(path, "r") as f:
            for line in f:
                filename = line.split(",")[0]
                label = line.split(",")[1][:-1]
                if label in mapping_dic.keys():
                    mapped_label = mapping_dic[label]
                else:
                    length = len(mapping_dic)
                    mapping_dic[label] = length
                    mapped_label = length
                labels[filename] = mapped_label
        self.mapping_dic = mapping_dic
        print(self.mapping_dic)
        return labels

    def next_batch(self, kind, num, one_hot=True):
        if kind == "test":
            end = self.test_offset + num
            if end > self.n_test:
                self.test_offset = 0
                end = num
                random.shuffle(self.test_images)
            images = self.test_images
            offset = self.test_offset
        elif kind == "train":
            end = self.train_offset + num
            if end > self.n_train:
                self.train_offset = 0
                end = num
                random.shuffle(self.train_images)
            images = self.train_images
            offset = self.train_offset

        else:
            raise Exception("kind is 'test' or 'train'")

        image_paths = images[offset: end]
        label_batch = [np.identity(10)[self.labels[p.name]] for p in image_paths]
        image_batch = [self.imread(str(p)) for p in image_paths]

        if kind == "test":
            self.test_offset = end
        elif kind == "train":
            self.train_offset = end
        return label_batch, image_batch
