from robsim.primitives.point import Point
from robsim.primitives.pose import Pose

from math import sqrt, ceil, pow, pi

from threading import Timer
import time
import sys
import msvcrt

import numpy as np

def timed_input(input_string, timeout_string: str = '', timeout: float = 5, timestep: float = 0.01, timer=time.monotonic):
    sys.stdout.write(input_string)
    sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if msvcrt.kbhit():
            result.append(msvcrt.getwche()) #XXX can it block on multibyte characters?
            if result[-1] == '\r':
                print('')
                return ''.join(result[:-1])
        time.sleep(timestep) # just to yield to other processes/threads
    sys.stdout.write(timeout_string)
    print('')
    return None

def minimize_angular_difference(a, b):
    while (b - a) > pi:  b -= 2 * pi
    while (b - a) < -pi: b += 2 * pi 

    return b

def dist_l1(a: Point, b: Point) -> float:
    s = 0
    for ai, bi in zip(a, b):
        s += abs(ai - bi)
    return s

def dist_l2(a: Point, b: Point) -> float:
    s = 0
    for ai, bi in zip(a, b):
        s += (ai - bi) * (ai - bi)
    return sqrt(s)

def dist_max(a: Point, b: Point) -> float:
    s = 0
    for ai, bi in zip(a, b):
        s = max(s, abs(ai - bi))
    return s

dist_names = {'l1': dist_l1, 'l2': dist_l2, 'max': dist_max}

def closest_point(a: Point, b: list, dist='l2') -> Point:
    dist = dist_names[dist]

    return min(b, key= lambda pt: dist(a, pt))

def interpolate(a: Point, b: Point, d: int = None, N: int = None):
    if N == None:
        dist = dist_l2(a, b)
        N = ceil(dist / d)

    K = [(n) / (N - 1) for n in range(N)]
    pts = [(a * (1 - k) + b * k) for k in K]

    return pts

def rom_spline(P, d: float = None, N: int = None, alpha: float = 0, t: tuple = (0.0, 0.333, 0.667, 1.0)):
    if N == None:
        dist = dist_l2(P[1], P[2])
        N = ceil(dist / d)

    x = [pt.x for pt in P]
    y = [pt.y for pt in P]
    v = [pt.theta for pt in P]

    t0 = 0
    t1 = pow(sqrt((x[1] - x[0])**2 + (y[1] - y[0])**2 + (v[1] - v[0])**2), alpha) + t0
    t2 = pow(sqrt((x[2] - x[1])**2 + (y[2] - y[1])**2 + (v[2] - v[1])**2), alpha) + t1
    t3 = pow(sqrt((x[3] - x[2])**2 + (y[3] - y[2])**2 + (v[3] - v[2])**2), alpha) + t2

    T = [(t2 - t1) * n / (N - 1) + t1 for n in range(N)]

    pts = []
    for t in T:
        A1 = P[0] * (t1 - t) / (t1 - t0) + P[1] * (t - t0) / (t1 - t0)
        A2 = P[1] * (t2 - t) / (t2 - t1) + P[2] * (t - t1) / (t2 - t1)
        A3 = P[2] * (t3 - t) / (t3 - t2) + P[3] * (t - t2) / (t3 - t2) 

        B1 = A1 * (t2 - t) / (t2 - t0) + A2 * (t - t0) / (t2 - t0)
        B2 = A2 * (t3 - t) / (t3 - t1) + A3 * (t - t1) / (t3 - t1) 
        
        pt = B1 * (t2 - t) / (t2 - t1) + B2 * (t - t1) / (t2 - t1)

        pts.append(pt)

    return pts

def reduce_list(l, reduction):
    result = []

    for i in range(len(l)):
        if len(result) < i * reduction:
            result.append(l[i])

    return result

def check_ipython():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False

# std_d and std_a are relative to 1m and 2pi respectively, depending on the distance moved.
# a std_d value of 0.1 means that you would expect the error to be 1m if the robot moves 10m.
# a std_a value of 0.1 means that you would expect the error to be 2pi if the robot turns 20pi.
def add_radial_noise_pose(pose, std_d: float = 0.5, std_a1: float = 0.3, std_a2: float = 0.3):
    e_d = np.random.normal(1, std_d)
    e_a1 = np.random.normal(1, std_a1)
    e_a2 = np.random.normal(1, std_a2)

    a1, d = Point(pose.x, pose.y).as_polar()
    x, y = Point.from_polar(a1 * e_a1, d * e_d)
    theta = pose.theta * e_a2

    return Pose(x, y, theta)

# std_d and std_a are relative to 1m and 2pi respectively, depending on the distance moved.
# a std_d value of 0.1 means that you would expect the error to be 1m if the robot moves 10m.
# a std_a value of 0.1 means that you would expect the error to be 2pi if the robot turns 20pi.
def add_radial_noise_point(point, std_d: float = 0.01, std_a: float = 0.005):
    e_d = np.random.normal(1, std_d)
    e_a = np.random.normal(1, std_a)

    a, d = Point(point.x, point.y).as_polar()

    return Point.from_polar(a * e_a, d * e_d)