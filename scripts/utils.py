import os

import pygame


BASE_IMG_PATH = 'data/images/'


def load_image(path):
    # make rendering more efficient
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))  # Make pure black transparent
    return img


def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images
