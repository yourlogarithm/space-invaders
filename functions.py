import pygame
import os


def rescale(image, scale):
    try:
        image = pygame.transform.scale(image, (scale, scale))
    except TypeError:
        image = pygame.transform.scale(image, scale)
    return image


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
