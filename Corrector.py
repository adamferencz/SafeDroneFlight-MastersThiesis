"""
Class for computing correction algorithm on pilot commands.
Implements the novel method described in the thesis.

Adam Ferencz
VUT FIT 2022
"""

from distances import *
from utils import *


class Corrector:
    """ Control algorithm for correction pilot commands."""

    def __init__(self, display, transformer):
        self.display = display

        # Current nearest point.
        self.nearest_point = None
        self.nearest_point_dist = 0
        self.nearest_segment = None

        # Predicted nearest point.
        self.future_nearest_point = None
        self.future_nearest_point_dist = 0
        self.future_nearest_segment = None

        # For transformation between systems.
        self.transform = transformer

        # Weighting constants.
        self.gain_command, self.gain_lc, self.gain_fc = 1, 1, 5

        # Weighted powers for computing result.
        self.gain_command_power, self.gain_present_correction_power, self.gain_future_correction_power = 0, 0, 0

        # In free_range correction power is zero.
        self.free_range = 1

        # Edge of the safe zone.
        self.warning_range = 2

        # Sets time for the predictive correction.
        self.future_time = 2

        self.command = np.array([0, 0, 0])
        self.safe_command = np.array([0, 0, 0])

    def draw_circle(self, color, metres_xy, size):
        """
        Draw circle in 2D canvas described by 3D coordinates in metres.

        :param color:
        :param size: 
        :param metres_xy: coordinates in metres [x, y]

        """
        cm_xy = self.transform.metres2cm2D(metres_xy)
        pixel_xy = self.transform.cm2pixels(cm_xy)
        pygame.draw.circle(self.display, color, pixel_xy, size)

    def get_correction_power(self, dist, free_range=1, attack=50):
        """

        :param dist: param free_range:  (Default value = 1)
        :param attack: Default value = 50)
        :param free_range:  (Default value = 1)

        """
        free_range = self.free_range
        if dist < free_range:
            power = 0
        else:
            x = dist
            power = pow((x - 2), 3) / 10 + 0.5
        return power

    def adjust_command(self, location, velocity, command_speed, path):
        """
        Computes state of the system and transforms input command to safe command.

        :param location: position as vector [x, y, z]
        :param velocity: velocity as vector [x, y, z]
        :param command_speed: command from pilot as vector [x, y, z]
        :param path: path object

        """

        self.command = command_speed

        """ Get nearest points """
        # Current nearest point.
        self.nearest_point, self.nearest_point_dist, self.nearest_segment = self.get_nearest_point(location, path)

        # Predicted nearest point.
        future_location = location + self.future_time * np.array(velocity)
        p, d, s = self.get_nearest_point(future_location, path)
        self.future_nearest_point, self.future_nearest_point_dist, self.future_nearest_segment = p, d, s

        """ Estimate correction powers. """
        # Direction.
        local_correction_power = self.nearest_point - location
        future_correction_power = self.future_nearest_point - future_location

        # Magnitude.
        local_correction_mag = self.get_correction_power(self.nearest_point_dist)
        future_correction_mag = self.get_correction_power(self.future_nearest_point_dist)

        # Result.
        local_correction_power = set_mag_vec3(local_correction_power, local_correction_mag)
        future_correction_power = set_mag_vec3(future_correction_power, future_correction_mag)

        """ Main calculation """
        # self.gain_command = self.get_command_gain(local_correction_power) # Experimental.

        self.gain_command_power = self.gain_command * np.array(command_speed)
        self.gain_present_correction_power = self.gain_lc * local_correction_power
        self.gain_future_correction_power = self.gain_fc * future_correction_power

        save_command_speed = self.gain_command_power + self.gain_present_correction_power + self.gain_future_correction_power

        """ Draw visualisation. """

        # Visualise top-down view 2D.
        vectors = save_command_speed, command_speed, future_correction_power, local_correction_power, velocity
        self.visualise_top_down_view(vectors)

        # Visualise vertical difference.
        self.visualise_vertical_difference(location, velocity, path, vectors)

        # Draw points.
        self.draw_circle(GRAY, (self.nearest_point[0], self.nearest_point[1]), 3)
        location_pixel_xy = self.transform.metres2pixels(location)
        nearest_point_pix = self.transform.metres2pixels(self.nearest_point)
        pygame.draw.line(self.display, GRAY, location_pixel_xy, nearest_point_pix, 1)

        self.draw_circle(GRAY, (future_location[0], future_location[1]), 5)
        f_location_pixel_xy = self.transform.metres2pixels(future_location)
        future_nearest_point_pix = self.transform.metres2pixels(self.future_nearest_point)
        pygame.draw.line(self.display, GRAY, f_location_pixel_xy, future_nearest_point_pix, 1)
        self.draw_circle((255, 100, 255), (self.future_nearest_point[0], self.future_nearest_point[1]), 3)

        self.safe_command = np.array([save_command_speed[0], save_command_speed[1], save_command_speed[2]])
        return self.safe_command

    def get_nearest_point(self, location, path):
        """ Gets the nearest point to the whole path.

        :param location: vector 3D [x, y, z] of location of drone
        :param path: object of ``Path``

        """

        segments = path.get_segments()
        nearest_segment = None
        min_mag = None
        min_vec = None
        for seg in segments:

            # Get distance and vector from point to line segment.
            mag, vec = pnt2line(location, seg[0], seg[1])

            if min_mag is None or mag < min_mag:
                min_mag = mag
                min_vec = vec
                nearest_segment = seg

        # Draw the nearest point.
        if min_vec is not None:
            location_t = self.transform.cm2pixels(location)
            min_vec_t = self.transform.cm2pixels(min_vec)
            pygame.draw.line(self.display, (0, 0, 255), (location_t[0], location_t[1]), (min_vec_t[0], min_vec_t[1]))
            pygame.draw.circle(self.display, (0, 0, 255), (min_vec_t[0], min_vec_t[1]), 5)

        return min_vec, min_mag, nearest_segment

    def visualise_top_down_view(self, vectors):
        """
        Draws visualization of 2D part of correction vectors.

        :param vectors: list of vectors

        """
        save_command_speed, command_speed, future_correction, correction_vector, velocity = vectors
        starting_point = (650, 500)
        pygame.draw.circle(self.display, (0, 0, 255), starting_point, 5)
        pygame.draw.circle(self.display, (0, 0, 255), starting_point, 100, width=2)
        self.visualise_vector_2D(starting_point, save_command_speed, (0, 0, 255), "save_command_speed", scale=5)
        self.visualise_vector_2D(starting_point, command_speed, (255, 0, 255), "command_speed", scale=5)
        self.visualise_vector_2D(starting_point, future_correction, (255, 200, 0), "FC", scale=5)
        self.visualise_vector_2D(starting_point, correction_vector, (0, 255, 255), "correction_vector", scale=5)
        self.visualise_vector_2D(starting_point, velocity, (255, 0, 0), "velocity", scale=50)

    def visualise_vertical_difference(self, location, velocity, path, vectors):
        """
        Draws "side view". Displays drone height i comparison to path.

        :param location: drone location vec3
        :param path: object ``Path``
        :param velocity: drone speed vec3
        :param vectors: list of vectors vec3

        """

        # Get all vectors to visualize.
        save_command_speed, command_speed, future_correction, correction_vector, velocity = vectors

        # Origin of the "side view" element.
        sp = (50, 700)  # lower left corner

        # Get extremes of height for current path to set the scale.
        max_height = 0
        min_height = 100000000000
        for wp in path.waypoints:
            if wp.metres_z > max_height:
                max_height = wp.metres_z
            if wp.metres_z < min_height:
                min_height = wp.metres_z

        # Constants.
        visual_max_height = 200
        visual_max_power = 100
        visual_max_width = 200
        real_max_height = max_height + 10

        # Create pins for waypoints of the segment.
        left_x = sp[0]
        right_x = sp[0] + visual_max_width
        pygame.draw.rect(self.display, (0, 255, 0),
                         (left_x, sp[1] - visual_max_height, visual_max_width, visual_max_height), width=1),

        left_height = self.nearest_segment[0][2]
        right_height = self.nearest_segment[1][2]

        left_y = sp[1] - map_value(left_height, 0, real_max_height, 0, visual_max_height)
        right_y = sp[1] - map_value(right_height, 0, real_max_height, 0, visual_max_height)

        pygame.draw.circle(self.display, (255, 150, 0), (left_x, left_y), 4)
        pygame.draw.circle(self.display, (255, 150, 0), (right_x, right_y), 4)

        # Display height info.
        text(self.display, "{:.2f}".format(left_height), 20,
             (left_x + 5, left_y + 5))
        text(self.display, "{:.2f}".format(right_height), 20,
             (right_x - 30, right_y + 5))

        # Compute position on of nearest point on the segment.
        # Get distance from left and right, then compute the ratio.
        dist_from_left = distance(self.nearest_segment[0], self.nearest_point)
        dist_from_right = distance(self.nearest_segment[1], self.nearest_point)

        # Get visual distance from the left.
        visual_length = 1
        visual_dist_from_left = visual_length / (dist_from_left + dist_from_right) * dist_from_left

        # Get exact position of the point on the visualisation of segment.
        left = np.array([left_x, left_y])
        right = np.array([right_x, right_y])
        visual_vertical_vector = right - left
        visual_vertical_location = left + visual_vertical_vector * visual_dist_from_left

        # Draw segment line and location of the nearest point placed on the segment.
        color = (255, 0, 0)
        pygame.draw.line(self.display, color, (left_x, left_y), (right_x, right_y), 5)
        pygame.draw.circle(self.display, (255, 0, 255), visual_vertical_location, 7)

        # Get visual location of the drone relative to the segment.
        visual_vertical_location2 = sp[1] - map_value(location[2], 0, real_max_height, 0, visual_max_height)  # *100

        # Draw the drone and connection to the nearest point.
        pygame.draw.line(self.display, color, visual_vertical_location,
                         (visual_vertical_location[0], visual_vertical_location2), 5)
        pygame.draw.circle(self.display, (255, 100, 100), (visual_vertical_location[0], visual_vertical_location2), 7)

        # Display height info.
        text(self.display, "{:.2f}".format(location[2]), 20,
             (visual_vertical_location[0] + 5, visual_vertical_location2))

        # Visualise vertical part of vectors used in the method.
        starting_point = np.array([right_x + 10, visual_vertical_location2])
        pygame.draw.circle(self.display, (0, 0, 255), starting_point, 5)
        self.visualise_vector_vertical(starting_point + np.array([10, 0]), save_command_speed, (0, 0, 255),
                                       "sc")
        self.visualise_vector_vertical(starting_point + np.array([60, 0]), command_speed, (255, 0, 255),
                                       "oc")
        self.visualise_vector_vertical(starting_point + np.array([90, 0]), future_correction, (255, 200, 0), "fc")
        self.visualise_vector_vertical(starting_point + np.array([120, 0]), correction_vector, (0, 255, 255),
                                       "pc")
        self.visualise_vector_vertical(starting_point + np.array([150, 0]), velocity, (255, 0, 0), "v")

    def visualise_vector_2D(self, start, vector, color, text, scale=10):
        """ Visualises 3D vector ad 2D vector just by [x, y].

        :param start: origin of the vector [x, y, z]
        :param color: color
        :param scale: Default value = 1.0) float scale factor
        :param vector: input vector in metres [x, y, z]
        :param text: text used for displaying info

        """
        vector = [vector[0] * scale, vector[1] * scale]
        end = (start[0] + vector[0], start[1] + vector[1])
        pygame.draw.line(self.display, color, start, end, 5)
        pygame.draw.circle(self.display, color, (600, 600), 3)

    def visualise_vector_vertical(self, start, vector_in, color, text):
        """ Visualises vertical component of 3D vector.

        :param start: origin of the vector [x, y, z]
        :param color: color
        :param vector_in: input vector in metres [x, y, z]
        :param text: text used for displaying info

        """
        vector = [0, -vector_in[2] * 10]
        end = (start[0] + vector[0], start[1] + vector[1])
        end_plus = (start[0] + vector[0] - 20, start[1] + vector[1] * 1.3)
        pygame.draw.line(self.display, color, start, end, 20)
        pygame.draw.circle(self.display, color, (600, 600), 3)
        font = pygame.font.Font(None, 20)
        text = font.render(str(text) + " " + str(round(-vector_in[2], 1)), 1, color)
        self.display.blit(text, end_plus)
