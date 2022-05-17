"""
Abstract model of drone class. Used as a drone interface.

Adam Ferencz
VUT FIT 2022
"""

import cv2
from utils import *
from abc import ABC, abstractmethod


class AbstractDroneModel(ABC):
    """Abstract model of drone class. Used as a drone interface.
    
    The word drone in this class context can mean drone in the simulator or real drone.


    """

    def __init__(self, surface, transformer):
        self.GPS = None
        self.position = np.array([0, 0, 0])  # metres from center
        self.speed = np.array([0, 0, 0])  # metres/s
        self.acceleration = np.array([0, 0, 0])  # metres/s*s
        self.yaw = 0  # -180 -> 180 degrees
        self.pitch = 0
        self.roll = 0
        self.position_history = []

        self.surface = surface

        self.transform = transformer

        self.sl = []

        self.client = None

        self.in_air = False
        self.on_target = True
        self.target = np.array([0, 0, 0])

        self.joystick_mapping = 5

        self.log_folder = "logs/general_log"

    @abstractmethod
    def connect(self):
        """Connect to the external simulator program or real drone."""
        pass

    @abstractmethod
    def takeoff(self):
        """Sends command to move drone in the air."""
        pass

    @abstractmethod
    def land(self):
        """Sends command to land the drone."""
        pass

    def map_joystick_to_speed(self, joystick):
        """Maps input vector from the joystick controller to the command vector.

        :param joystick: list of 4 floats

        """
        joystick = list(map(lambda x: 0 if abs(x) < 0.1 else x, joystick))
        joystick = [joystick[0], -1 * joystick[1], joystick[2], -1 * joystick[3]]
        left_right = joystick[2]
        fwd_back = joystick[3]
        up_down = joystick[1]
        yaw = joystick[0]

        left_right = int(left_right * speed)
        fwd_back = int(fwd_back * speed)
        up_down = int(up_down * speed)
        yaw = int(yaw * speed)

        return left_right, fwd_back, up_down, yaw

    @abstractmethod
    def display_video(self):
        """Displays video from the drone camera to the GUI."""
        pass

    @abstractmethod
    def take_photo(self):
        """Saves actual frame from drone camera as png image file to ``self.log_folder`` path."""

    @abstractmethod
    def update(self):
        """Get info about drone. Update it.
        
        Update here:
        
        ``self.yaw``, ``self.speed``, ``self.acceleration``,
        ``self.position``, ``self.GPS``


        """
        pass

    @abstractmethod
    def move(self, command, delta_time):
        """Send move command to the drone.

        :param command: list of 4 floats [x_speed, y_speed, z_speed, yaw]
        :param delta_time: time from previous update (used just for basic mode)

        """

    def rotate_command_by_yaw(self, command):
        """Rotates command vector by yaw ankle in positive direction.

        :param command: list of 4 floats [x_speed, y_speed, z_speed, yaw]

        """
        rotated = rotate_vector(np.array([command[0], command[1]]), self.yaw)
        return rotated

    def rotate_back_command_by_yaw(self, command):
        """Rotates command vector by yaw ankle in negative direction.

        :param command: list of 4 floats

        """
        rotated = rotate_vector(np.array([command[0], command[1]]), -self.yaw)
        return rotated

    def visualise_vector_2d_scale(self, start, vector, color, text_info, scale=1.0):
        """ Visualises 3D vector ad 2D vector just by [x, y].

        :param start: origin of the vector [x, y, z]
        :param color: color
        :param scale: Default value = 1.0) float scale factor
        :param vector: input vector in metres [x, y, z]
        :param text_info: text used for displaying info

        """
        vector = [vector[0] * scale, vector[1] * scale]
        end = (start[0] + vector[0], start[1] + vector[1])

        start = self.transform.metres2pixels(start)
        end = self.transform.metres2pixels(end)
        pygame.draw.line(self.surface, color, start, end, 5)

    def display(self):
        """Draws drone position, heading, speed vector and path history to the GUI."""
        self.position_history.append(self.position)
        t_pos = self.transform.metres2pixels(self.position)

        # Draw position history.
        for p in self.position_history:
            t_pos = self.transform.metres2pixels(p)
            pygame.draw.circle(self.surface, GRAY, (t_pos[0], t_pos[1]), 1)

        # Draw drone.
        pygame.draw.circle(self.surface, RED, (t_pos[0], t_pos[1]), 5)

        # Draw speed vector.
        self.visualise_vector_2d_scale(self.position, self.speed, (0, 255, 0), self.speed, scale=5)

        # Draw heading.
        t_pos = self.transform.metres2pixels(self.position)
        heading = rotate(t_pos, t_pos + np.array([0, -20]), math.radians(self.yaw))
        pygame.draw.line(self.surface, (255, 0, 0), t_pos, heading, 5)

        text(self.surface, "position :" + str(trunc(self.position)), 25, (450, 100))
        text(self.surface, "speed :" + str(trunc(self.speed)), 25, (450, 125))
        text(self.surface, "acceleration :" + str(trunc(self.acceleration)), 25, (450, 150))
