"""
Class for storing and manipulation with safe path.

Adam Ferencz
VUT FIT 2022
"""

import json
import os
from datetime import datetime

from Waypoint import *
from utils import *


class Path:
    """
    Represents save and ideal trajectory.

    Implements manipulation with path.
    Implements visualization with path.
    """
    def __init__(self, transformer):
        self.waypoints = []
        self.saved = True
        self.mission_folder = "missions"
        self.selected_wp = None
        self.selected_wp_locked = False
        self.transformer = transformer

        self.redraw_timer = 60
        self.actual_height = 2

    def add_waypoint_by_pixel(self, pixel_xy):
        """
        Adds new waypoint by clicking in GUI.

        :param pixel_xy: position in GUI

        """
        metres_z = self.actual_height
        cm_xy = self.transformer.pixels2cm(pixel_xy)
        metres_x, metres_y = self.transformer.cm2metres(cm_xy)
        lat, lon = self.transformer.pixels2latlon(pixel_xy)
        wp = Waypoint(self.transformer, lat, lon, metres_x, metres_y, metres_z)
        self.waypoints.append(wp)
        self.saved = False
        self.redraw_timer = 0

    def display(self, surface):
        """
        Displays path.

        :param surface: Screen reference.

        """
        if len(self.waypoints) > 0:
            prev = self.waypoints[0].position_visual()
            for wp in self.waypoints:
                p = wp.position_visual()
                pygame.draw.line(surface, (0, 0, 255), (p[0], p[1]), (prev[0], prev[1]))
                pygame.draw.circle(surface, (0, 0, 255), (p[0], p[1]), 5)
                pygame.draw.circle(surface, (0, 0, 255), (prev[0], prev[1]), 5)
                prev = p

        if self.selected_wp is not None:
            pygame.draw.circle(surface, (0, 255, 0), self.selected_wp.position_visual(), 10, width=2)
            self.selected_wp.display_wp_info(surface)

    def save_path_json(self):
        """  Saves path as JSON. """

        wp_list = []
        for wp in self.waypoints:
            wp_list.append({
                'latitude': wp.latitude,
                'longitude': wp.longitude,
                'altitude': wp.altitude,

                'metres_x': wp.metres_x,
                'metres_y': wp.metres_y,
                'metres_z': wp.metres_z,

                'visual_x': wp.visual_x,
                'visual_y': wp.visual_y,
                'transformer.width': wp.transformer.width,
                'transformer.height': wp.transformer.height,
                'transformer.zoom': wp.transformer.zoom,
                'transformer.center_latlon': wp.transformer.center_latlon,

            })
        print(wp_list)
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
        print("date and time =", dt_string)

        path = self.mission_folder + "/" + dt_string + ".json"
        data = wp_list
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def delete_path(self):
        """ Resets current path. """
        self.waypoints = []
        self.saved = True

    def load_path_json(self, json_file):
        """
        Loads path from the json file.

        :param json_file: path

        """

        width = json_file[0]["transformer.width"]
        height = json_file[0]["transformer.height"]
        zoom = json_file[0]["transformer.zoom"]
        center_latlon = json_file[0]["transformer.center_latlon"]
        self.transformer = Transformer(width, height, zoom, center_latlon)

        for wp in json_file:
            lat = wp["latitude"]
            lon = wp["longitude"]
            metres_x = wp["metres_x"]
            metres_y = wp["metres_y"]
            metres_z = wp["metres_z"]

            self.waypoints.append(Waypoint(self.transformer, lat, lon, metres_x, metres_y, metres_z))


    def update(self, mouse):
        """
        Implements update of the path while manipulating with the control points.
        :param mouse: mouse position in GUI

        """
        mouseX, mouseY = mouse
        if not self.selected_wp_locked:
            self.selected_wp = None
        for wp in self.waypoints:
            mouse = np.array(mouse)
            wp_coords = wp.position_visual()
            dist = distance_np(mouse, wp_coords)
            if dist < 5:
                self.selected_wp = wp

        if self.selected_wp_locked:
            self.selected_wp.update_by_visual_xy(mouse)
            self.redraw_timer = 0


    def get_segments(self):
        """ Transforms path to list of segments. """
        result = []
        for i in range(len(self.waypoints) - 1):
            result.append([self.waypoints[i].position_metres(), self.waypoints[i + 1].position_metres()])
        return result

