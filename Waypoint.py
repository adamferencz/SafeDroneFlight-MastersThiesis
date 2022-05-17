"""
Waypoint class represents one control point of Path.
Storing, displaying, manipulation.

Adam Ferencz
VUT FIT 2022
"""

import pygame
import numpy as np
from utils import *

class Waypoint:
    """ """
    def __init__(self, transformer, lat, lon, metres_x, metres_y, metres_z, alt = None):

        self.latitude = lat
        self.longitude = lon
        self.altitude = alt

        self.metres_x = metres_x
        self.metres_y = metres_y
        self.metres_z = metres_z

        self.visual_x = 0
        self.visual_y = 0

        self.transformer = transformer

    def update_by_visual_xy(self, visual_xy):
        """
        Updates by mouse form GUI.

        :param visual_xy: list of two ints
        """
        cm_xy = self.transformer.pixels2cm(visual_xy)
        metres_x, metres_y = self.transformer.cm2metres(cm_xy)
        lat, lon = self.transformer.pixels2latlon(visual_xy)

        self.latitude = lat
        self.longitude = lon

        self.metres_x = metres_x
        self.metres_y = metres_y

        self.visual_x = visual_xy[0]
        self.visual_y = visual_xy[1]


    def position_metres(self):
        """ Returns position in metres for calculations."""
        return np.array([self.metres_x, self.metres_y, self.metres_z])

    def position_visual(self):
        """ Returns position in pixels for visualization. """
        cm_xy = self.transformer.metres2cm2D([self.metres_x, self.metres_y])
        self.visual_x, self.visual_y = self.transformer.cm2pixels(cm_xy)
        return self.visual_x, self.visual_y

    def display_wp_info(self, surface):
        """
        Displays Waypoint info.
        :param surface: display object

        """
        pos = self.position_visual()
        pygame.draw.rect(surface, (255, 255, 255), (pos[0] - 100, pos[1] - 100, 200, 75), width=0)
        text(surface, "Lat: " + "{:.5f}".format(self.latitude), 25, (pos[0] - 50, pos[1] - 100))
        text(surface, "Lon: " + "{:.5f}".format(self.longitude), 25, (pos[0] - 50, pos[1] - 75))
        text(surface, "Height: " + str(round(self.metres_z, 2)) + " m", 25, (pos[0] - 50, pos[1] - 50))

