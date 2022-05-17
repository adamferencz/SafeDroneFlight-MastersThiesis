"""
Drone model that represents AirSim dron.

Adam Ferencz
VUT FIT 2022
"""

import airsim
from airsim import *

from AbstractDroneModel import AbstractDroneModel
from utils import *
import cv2
import numpy as np
from datetime import datetime


class AirSimDroneModel(AbstractDroneModel):
    """Drone model that represents AirSim dron.
    
    Implement functions for communication with AirSim API.
    Contains drone state.
    Contains Additions function specific for AirSim.


    """

    def __init__(self, surface, transformer):
        AbstractDroneModel.__init__(self, surface, transformer)

        self.joystick_mapping = 5
        self.getTicksLastFrame = 0
        self.home = None

    def connect(self):
        """Connect to the external simulator program or real drone."""
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)

        lat = self.client.getHomeGeoPoint().latitude
        lon = self.client.getHomeGeoPoint().longitude
        self.home = [lat, lon]
        self.transform.center_latlon = [lat, lon]

    def takeoff(self):
        """Sends command to move drone in the air."""
        self.client.takeoffAsync().join()
        self.in_air = True

    def land(self):
        """Sends command to land the drone."""
        self.client.landAsync(timeout_sec=5).join()

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

        left_right = int(left_right * self.joystick_mapping)
        fwd_back = int(fwd_back * self.joystick_mapping)
        up_down = int(up_down * self.joystick_mapping)
        yaw = int(yaw * self.joystick_mapping)

        return left_right, fwd_back, up_down, yaw * 10

    def display_video(self):
        """Displays video from the drone camera to the GUI."""
        result = self.client.simGetImage("0", airsim.ImageType.Scene)
        rawImage = np.fromstring(result, np.int8)
        frame = cv2.imdecode(rawImage, cv2.IMREAD_UNCHANGED)

        # Source: https://gist.github.com/radames/1e7c794842755683162b
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = frame.swapaxes(0, 1)
        frame = pygame.surfarray.make_surface(frame)
        self.surface.blit(frame, (10, 350))

    def take_photo(self):
        """Saves actual frame from drone camera as png image file to ``self.log_folder`` path."""
        result = self.client.simGetImage("0", airsim.ImageType.Scene)
        rawImage = np.fromstring(result, np.int8)
        png = cv2.imdecode(rawImage, cv2.IMREAD_UNCHANGED)

        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
        print("date and time =", dt_string)

        path = self.log_folder + "/photos/" + dt_string + ".png"
        print("path =", path)
        cv2.imwrite(path, png)

    def update(self):
        """Get info about drone. Update it.
        
        Update here:
        
        ``self.yaw``, ``self.speed``, ``self.acceleration``,
        ``self.position``, ``self.GPS``


        """
        state = self.client.getMultirotorState()
        q = state.kinematics_estimated.orientation
        r, p, y = to_eularian_angles(q)
        self.yaw = np.rad2deg(y)
        self.pitch = np.rad2deg(p)
        self.roll = np.rad2deg(r)

        vel = state.kinematics_estimated.linear_velocity
        self.speed = self.transform.ned2utm(np.array([vel.x_val, vel.y_val, vel.z_val]))

        lat = state.gps_location.latitude
        lon = state.gps_location.longitude
        x, y = self.transform.convert_latlon_metres_yx((lat, lon))
        z = state.gps_location.altitude - self.client.getHomeGeoPoint().altitude
        self.position = np.array([x, y, z])

        self.GPS = self.client.getMultirotorState().gps_location

    def move(self, command, delta_time):
        """

        :param command: param delta_time:
        :param delta_time: 

        """
        if self.in_air:
            left_right, fwd_back, up_down, yaw = command
            command_ned = self.transform.utm2ned([left_right, fwd_back, up_down])
            vx, vy, vz = map_vec3_to_float_list(command_ned)
            duration = delta_time * 2
            self.client.moveByVelocityAsync(vx, vy, vz, duration, yaw_mode={'is_rate': True, 'yaw_or_rate': yaw})

    def plot_to_airsim(self, path, mouse):
        """Visualises path and mouse position to the world in AirSim simulator.

        :param path: object of Path class
        :param mouse: list of 2 float [x, y]

        """

        path.redraw_timer = 60
        segments = path.get_segments()
        duration = 0.2
        if len(segments) > 0:
            points_up_vector3r = []
            points_down_vector3r = []
            height_vector3r = []
            path_vector3r = []

            # Draw save path in AirSIm word.
            for seg in segments:

                # Get points.
                seg1_ned = self.transform.utm2ned(seg[0])
                seg2_ned = self.transform.utm2ned(seg[1])

                # Build lines.
                path_vector3r.append(Vector3r(seg1_ned[0], seg1_ned[1], seg1_ned[2]))
                path_vector3r.append(Vector3r(seg2_ned[0], seg2_ned[1], seg2_ned[2]))
                height_vector3r.append(Vector3r(seg1_ned[0], seg1_ned[1], 0))
                points_down_vector3r.append(Vector3r(seg1_ned[0], seg1_ned[1], 0))
                height_vector3r.append(Vector3r(seg1_ned[0], seg1_ned[1], seg1_ned[2]))
                points_up_vector3r.append(Vector3r(seg1_ned[0], seg1_ned[1], seg1_ned[2]))

            # Last line.
            seg = segments[-1]
            seg2_ned = self.transform.utm2ned(seg[1])
            height_vector3r.append(Vector3r(seg2_ned[0], seg2_ned[1], 0))
            points_down_vector3r.append(Vector3r(seg2_ned[0], seg2_ned[1], 0))
            height_vector3r.append(Vector3r(seg2_ned[0], seg2_ned[1], seg2_ned[2]))
            points_up_vector3r.append(Vector3r(seg2_ned[0], seg2_ned[1], seg2_ned[2]))

            # Plot to the AirSim.
            self.client.simPlotLineList(points=path_vector3r, color_rgba=[1.0, 0.0, 0.0, 0.01], thickness=8,
                                        duration=duration)
            self.client.simPlotLineList(points=height_vector3r, color_rgba=[0.0, 0.0, 1.0, 1.0], thickness=5,
                                        duration=duration)
            self.client.simPlotPoints(points=points_down_vector3r, color_rgba=[1.0, 0.0, 1.0, 1.0], size=15,
                                      duration=duration, is_persistent=False)
            self.client.simPlotPoints(points=points_up_vector3r, color_rgba=[0.0, 1.0, 1.0, 1.0], size=15,
                                      duration=duration, is_persistent=False)
        # Plot mouse position.
        mouse_utm = self.transform.pixels2metres([mouse[0], mouse[1]])
        mouse_ned = self.transform.utm2ned([mouse_utm[0], mouse_utm[1], path.actual_height])
        mouse_up = Vector3r(mouse_ned[0], mouse_ned[1], mouse_ned[2])
        mouse_down = Vector3r(mouse_ned[0], mouse_ned[1], 0)
        self.client.simPlotLineList(points=[mouse_down, mouse_up], color_rgba=[0.0, 0.0, 1.0, 1.0], thickness=5,
                                    duration=duration)
        self.client.simPlotPoints(points=[mouse_down], color_rgba=[1.0, 0.0, 1.0, 1.0], size=15, duration=duration,
                                  is_persistent=False)
        self.client.simPlotPoints(points=[mouse_up], color_rgba=[0.0, 1.0, 1.0, 1.0], size=15, duration=duration,
                                  is_persistent=False)
