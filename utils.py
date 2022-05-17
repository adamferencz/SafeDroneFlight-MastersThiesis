"""
Helper functions.

Adam Ferencz
VUT FIT 2022
"""

import math

import numpy as np
import pygame
import utm
import matplotlib.pyplot as plt
from Transformer import *

# color constants

BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
WHITE = (255, 255, 255)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

def get_input_arrows():
    """ For keyboard input. """
    # https://github.com/sshell/pythongame/blob/359294fb52070a3623d50accf256aacc34cb5159/input.py
    left = pygame.key.get_pressed()[pygame.K_LEFT]
    up = pygame.key.get_pressed()[pygame.K_UP]
    down = pygame.key.get_pressed()[pygame.K_DOWN]
    right = pygame.key.get_pressed()[pygame.K_RIGHT]
    return pygame.math.Vector2(right - left, down - up)


def get_input_wasd():
    """ For wasd input. """
    # https://github.com/sshell/pythongame/blob/359294fb52070a3623d50accf256aacc34cb5159/input.py
    left = pygame.key.get_pressed()[pygame.K_a]
    up = pygame.key.get_pressed()[pygame.K_w]
    down = pygame.key.get_pressed()[pygame.K_s]
    right = pygame.key.get_pressed()[pygame.K_d]
    return pygame.math.Vector2(right - left, down - up)


def get_input_space():
    """ Space input. """
    space = pygame.key.get_pressed()[pygame.K_SPACE]
    return


def visualise_joystick(screen, pos, size, joystick):
    """
    Visualization of stictk.

    :param screen: reference to screen
    :param pos: coords in GUI
    :param size: size
    :param joystick: joystick

    """
    pygame.draw.circle(screen, (0, 255, 0), (pos[0], pos[1]), 5, width=0)
    pygame.draw.circle(screen, (0, 255, 0), (pos[0], pos[1]), size, width=2)
    pygame.draw.circle(screen, (0, 255, 100), (pos[0] + joystick[0] * size, pos[1] + joystick[1] * size), 8, width=0)
    pos[0] += 100
    pygame.draw.circle(screen, (0, 255, 0), (pos[0], pos[1]), 5, width=0)
    pygame.draw.circle(screen, (0, 255, 0), (pos[0], pos[1]), size, width=2)
    pygame.draw.circle(screen, (0, 255, 100), (pos[0] + joystick[2] * size, pos[1] + joystick[3] * size), 8, width=0)


def map_joystick_to_speed(joystick, speed):
    """
    Maps joystick  to command.

    :param joystick: state of joystick list of floats
    :param speed: mapping constant

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


def text(display, text, size, xy):
    """ Displays text.

    :param display: object
    :param text: string
    :param size: int
    :param xy: list of two ints

    """
    font = pygame.font.Font(None, size)
    text = font.render(str(text), 1, (255, 10, 10))
    display.blit(text, xy)


def rotate(origin, point, angle):
    """Rotate a point counterclockwise by a given angle around a given origin.
    
    The angle should be given in radians.

    :param origin: center of rotation
    :param point: point which rotates
    :param angle: ankle radiants

    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def rotate_vector(vec, angle_deg):
    """ Rotates vector.

    :param vec:
    :param angle_deg: 

    """
    theta = np.deg2rad(-angle_deg)
    rot = np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]])
    return np.dot(rot, vec)


def visualise_metrics(surface, width, height, zoom):
    """
    Draws squares to the canvas according to the zoom.

    :param surface: canvas reference
    :param width: integer
    :param height: integer
    :param zoom: float

    """
    start = [0, 0]
    end = [0, height]
    spacing_m = 1000 * zoom
    while True:
        start = [start[0] + spacing_m, 0]
        end = [end[0] + spacing_m, height]
        pygame.draw.line(surface, (100, 255, 200), start, end, width=1)
        if start[0] > height:
            break

    start = [0, 0]
    end = [width, 0]
    while True:
        start = [0, start[1] + spacing_m]
        end = [width, end[1] + spacing_m]

        pygame.draw.line(surface, (0, 255, 0), start, end)
        if start[1] > width:
            break

def unit_vector(vector):
    """Returns the unit vector of the vector.

    :param vector: 

    """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """
    Computes angle between to lines.
    :param v1: vector
    :param v2: vector

    """
    # https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            # >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            # >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            # >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def distance_np(a, b):
    """
    Distance for np array.

    :param a: np array
    :param b: np array

    """
    return mag(a - b)

def set_mag(force, mag):
    """
    Set magnitude to 2D vector.
    :param force: force as np array
    :param mag: float

    """
    if np.linalg.norm(force) == 0:
        return np.array([0, 0])
    force = force / np.linalg.norm(force) * mag
    return force


def set_mag_vec3(force, mag):
    """
    Set magnitude to 3D vector.
    :param force: param mag:
    :param mag: 

    """
    if np.linalg.norm(force) == 0:
        return np.array([0, 0, 0])
    force = force / np.linalg.norm(force) * mag
    return force


def limit_vec3(force, limit):
    """
    Limits magnitude of 3D vector.

    :param force: 3D vector
    :param limit: float, maximum

    """
    if mag(force) > limit:
        return set_mag_vec3(force, limit)
    else:
        return force


def mag(force):
    """
    Gets magnitude of vector represented by np array.

    :param force: vector represented by np array
    """
    return np.linalg.norm(force)

def map_value(value, leftMin, leftMax, rightMin, rightMax):
    """Maps value from one range to another.
    #Source: https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another

    :param value:
    :param leftMax:
    :param rightMax: 
    :param leftMin: 
    :param rightMin: 

    """
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def map_value_vec3(vec3, leftMin, leftMax, rightMin, rightMax):
    """
    Maps 3D vector from one range to another.

    :param vec3: param leftMin:
    :param leftMax: param rightMin:
    :param rightMax: 
    :param leftMin: 
    :param rightMin:
    """
    value = mag(vec3)
    new_mag = map_value(value, leftMin, leftMax, rightMin, rightMax)
    return set_mag_vec3(vec3, new_mag)


def map_vec3_to_int_list(vec3):
    """
    Converts 3D vector to list of ints.

    :param vec3: 3D vector

    """
    return [int(vec3[0]), int(vec3[1]), int(vec3[2])]

def map_vec3_to_float_list(vec3):
    """
    Converts 3D vector to list of floats.

    :param vec3: 3D vector

    """
    return [float(vec3[0]), float(vec3[1]), float(vec3[2])]


def trunc(values, decs=2):
    """
    Rounds np array of values.

    :param values: np array of floats
    :param decs: int (Default value = 2) number of decimals

    """
    return np.trunc(values * 10 ** decs) / (10 ** decs)


def display_info(surface, x, y, info, title):
    """

    :param surface: param x:
    :param y: param info:
    :param title: 
    :param x: 
    :param info: 

    """
    for i, t in zip(info, title):
        text(surface, t + ": " + str(i), 20, (x, y))
        y = y + 20


def tune(v):
    """

    :param v: 

    """
    if abs(v) <= 10:
        v = 0
    elif abs(v) > 10 and abs(v) < 20:
        v = v/abs(v)*20
    else:
        v = v
    return v

def show_graph3(a, b, c):
    """

    :param a: param b:
    :param c: 
    :param b: 

    """
    y0 = np.array(a)
    y1 = np.array(b)
    y2 = np.array(c)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    fig.subplots_adjust(hspace=0.5)

    time_seconds_list = np.arange(0, len(y0), 1)
    ax1.plot(time_seconds_list, y0, color='b', label='model')
    ax1.set_xlabel('time')
    ax1.set_ylabel('xspeed')
    ax1.grid(True)
    ax1.legend()

    time_seconds_list = np.arange(0, len(y1), 1)
    ax2.plot(time_seconds_list, y1, color='b', label='model')
    ax2.set_xlabel('time')
    ax2.set_ylabel('yspeed')
    ax2.grid(True)
    ax2.legend()

    time_seconds_list = np.arange(0, len(y2), 1)
    ax3.plot(time_seconds_list, y2, color='r', label='gyro')
    ax3.set_xlabel('time')
    ax3.set_ylabel('zspeed')
    ax3.grid(True)
    ax3.legend()

    plt.show()

def print_graphs(vec1, vec2):
    """

    :param vec1: param vec2:
    :param vec2: 

    """

    v1 = np.array(vec1)
    v2 = np.array(vec2)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    fig.subplots_adjust(hspace=0.5)

    sl = v1[:, 0]
    rsl = v2[:, 0]
    time_seconds_list = np.arange(0, len(sl), 1)
    ax1.plot(time_seconds_list, sl,color='b', label='model')
    ax1.plot(time_seconds_list, rsl, color='r' , label='gyro')
    ax1.set_xlabel('time')
    ax1.set_ylabel('x')
    ax1.grid(True)
    ax1.legend()

    sl = v1[:, 1]
    rsl = v2[:, 1]
    time_seconds_list = np.arange(0, len(sl), 1)
    ax2.plot(time_seconds_list, sl,color='b', label='model')
    ax2.plot(time_seconds_list, rsl, color='r' , label='gyro')
    ax2.set_xlabel('time')
    ax2.set_ylabel('y')
    ax2.grid(True)
    ax2.legend()

    sl = v1[:, 2]
    rsl = v2[:, 2]
    time_seconds_list = np.arange(0, len(sl), 1)
    ax3.plot(time_seconds_list, sl,color='b', label='model')
    ax3.plot(time_seconds_list, rsl, color='r' , label='gyro')
    ax3.set_xlabel('time')
    ax3.set_ylabel('z')
    ax3.grid(True)
    ax3.legend()
    plt.show()



