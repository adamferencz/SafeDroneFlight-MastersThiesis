"""
Transformer between different coordinate systems.
GPD <--> UTM <--> NED <--> 2D pixels

Adam Ferencz
VUT FIT 2022
"""

import math
import numpy as np
import utm

class Transformer:
    """ """
    def __init__(self, width, height, zoom, center_latlon):
        self.width = width
        self.height = height
        self.zoom = zoom
        self.center_latlon = center_latlon

    def update(self, width, height, zoom):
        """
        Updates params of transformation.

        :param width: width of GUI
        :param height: height of GUI
        :param zoom: zoom

        """
        self.width = width
        self.height = height
        self.zoom = zoom

    def metres2pixels(self, vec3):
        """
        Transforms 3D vector of metres to 2D vector of pixels
        :param vec3: metres

        """
        vec2 = np.array([vec3[0], vec3[1]])
        z_pos = vec2 * self.zoom * 100
        i_pos = z_pos
        i_pos[1] = z_pos[1] * -1
        t_pos = i_pos + np.array([self.width / 2, self.height / 2])
        return t_pos

    def cm2pixels(self, vec3):
        """
        Transforms 3D vector of centimetres to 2D vector of pixels.
        :param vec3: 3D vector of centimetres

        """
        vec2 = np.array([vec3[0], vec3[1]])
        z_pos = vec2 * self.zoom
        i_pos = z_pos
        i_pos[1] = z_pos[1] * -1
        t_pos = i_pos + np.array([self.width / 2, self.height / 2])
        return t_pos

    def pixels2cm(self, vec2):
        """
        Transforms 2D vector of pixels to 2D vector of centimetres.
        :param vec2: 2D vector of pixels

        """
        vec2 = vec2 - np.array([self.width / 2, self.height / 2])
        vec2[1] = vec2[1] * -1
        vec2 = vec2 / self.zoom
        return vec2

    def pixels2metres(self, vec2):
        """
        Transforms 2D vector of pixels to 2D vector of metres.
        :param vec2: 

        """
        vec2 = vec2 - np.array([self.width / 2, self.height / 2])
        vec2[1] = vec2[1] * -1
        vec2 = vec2 / self.zoom
        return vec2/100

    def pixels2latlon(self, pixel_xy):
        """
        Transforms 2D vector of pixels (GUI coords) to GPS coords.
        :param pixel_xy: 2D vector of pixels

        """
        cm_xy = self.pixels2cm(pixel_xy)
        metres_xy = self.cm2metres(cm_xy)
        x, y, zone_number, zone_letter = utm.from_latlon(self.center_latlon[0], self.center_latlon[1])
        home_coords = np.array([x, y])

        utm_xy = home_coords + metres_xy

        loc = utm.to_latlon(utm_xy[0], utm_xy[1], zone_number, zone_letter)
        return loc

    def convert_latlon_visual_yx(self, loc, display_size, zoom):
        """
        Transforms GPS coords to 2D vector of pixels (GUI coords).
        :param loc: param display_size:
        :param zoom: float number
        :param display_size: size of window

        """
        x, y, _, _ = utm.from_latlon(self.center_latlon[0], self.center_latlon[1])
        home_coords = np.array([x, y])

        x, y, _, _ = utm.from_latlon(loc[0], loc[1])
        loc_coords = np.array([x, y])

        difference = (loc_coords - home_coords) * zoom

        return difference * np.array([1, -1]) + np.array([display_size[0] / 2, display_size[1] / 2])

    def convert_latlon_metres_yx(self, loc):
        """
        Transforms GPS coords to 2D vector of metres (relative word coords).
        :param loc: 

        """
        x, y, _, _ = utm.from_latlon(self.center_latlon[0], self.center_latlon[1])
        home_coords = np.array([x, y])

        x, y, _, _ = utm.from_latlon(loc[0], loc[1])
        loc_coords = np.array([x, y])

        difference = (loc_coords - home_coords)

        return difference

    def ned2utm(self, ned):
        """
        Transforms ned 3D vector of metres to UTM (relative word coords).
        :param ned: 

        """
        north = ned[0]
        east = ned[1]
        down = ned[2]

        y = north
        x = east
        z = -down
        return np.array([x, y, z])

    def utm2ned(self, utm):
        """
        Transforms UTM (relative word coords) to ned 3D vector of metres.
        :param utm: vector 2D

        """
        east = utm[0]
        north = utm[1]
        up = utm[2]

        x = north
        y = east
        z = -up
        return np.array([x, y, z])

    @staticmethod
    def cm2metres(cm):
        """
        Transforms cm to m in 2D.
        :param cm: 

        """
        return np.array([cm[0] / 100, cm[1] / 100])

    @staticmethod
    def metres2cm2D(metres):
        """
        Transforms m to cm in 2D.
        :param metres: 

        """
        return np.array([metres[0] * 100, metres[1] * 100])

