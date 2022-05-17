# Source: https://www.fundza.com/vectors/point2line/index.html
# CG References & Tutorials
# Author: 2002- Malcolm Kesson
import math


def dot(v, w):
    """

    :param v: param w:
    :param w: 

    """
    x, y, z = v
    X, Y, Z = w
    return x * X + y * Y + z * Z


def length(v):
    """

    :param v: 

    """
    x, y, z = v
    return math.sqrt(x * x + y * y + z * z)


def vector(b, e):
    """

    :param b: param e:
    :param e: 

    """
    x, y, z = b
    X, Y, Z = e
    return (X - x, Y - y, Z - z)


def unit(v):
    """

    :param v: 

    """
    x, y, z = v
    mag = length(v)
    return (x / mag, y / mag, z / mag)


def distance(p0, p1):
    """

    :param p0: param p1:
    :param p1: 

    """
    return length(vector(p0, p1))


def scale(v, sc):
    """

    :param v: param sc:
    :param sc: 

    """
    x, y, z = v
    return (x * sc, y * sc, z * sc)


def add(v, w):
    """

    :param v: param w:
    :param w: 

    """
    x, y, z = v
    X, Y, Z = w
    return (x + X, y + Y, z + Z)