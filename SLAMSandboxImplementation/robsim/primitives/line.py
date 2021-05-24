from robsim.primitives.point import Point
from robsim.utility import dist_l2

from math import pi, atan2, tan, sin, cos

import numpy as np

import matplotlib.pyplot as plt

class Line:
    @staticmethod
    def from_points(pts):
        assert len(pts) > 1
        pts = np.array([[pt.x, pt.y] for pt in pts]).transpose()

        covariance_matrix = np.cov(pts)
        weights, axes = np.linalg.eig(covariance_matrix)

        axis = axes[np.argmax(weights)]

        mean = np.average(pts, axis=1)

        line = Line(Point(mean[0], mean[1]), Point(mean[0] + axis[0], mean[1] + axis[1]))

        return line

    @staticmethod
    def from_points_fast(pts):
        assert len(pts) > 1
        return Line(pts[0], pts[-1])

    def __init__(self, a: Point, b: Point):
        assert (a != b), 'Points cannot be the same.'
        
        self.a = a
        self.b = b

    def get_intersection(self, line):
        x1, x2, x3, x4 = self.a.x, self.b.x, line.a.x, line.b.x 
        y1, y2, y3, y4 = self.a.y, self.b.y, line.a.y, line.b.y

        b = ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))

        if b == 0:
            return None

        t =  ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / b

        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / b

        p = self.eval_at(t)

        return p, t, u

    def get_distance(self, point):
        if point in [self.a, self.b]:
            return 0, point

        a = atan2(self.b.y - self.a.y, self.b.x - self.a.x) + pi/2

        x = point.x + cos(a)
        y = point.y + sin(a)

        line = Line(point, Point(x, y))

        p, t, u = self.get_intersection(line)

        return dist_l2(point, p), p

    def get_x(self, y):
        if self.a.y == self.b.y:
            return np.nan
            raise Exception('')

        if self.a.x == self.b.x:
            return self.a.x

        dx = self.b.x - self.a.x
        dy = self.b.y - self.a.y

        return (y - self.a.y) * dx / dy + self.a.x

    def get_y(self, x):
        if self.a.x == self.b.x:
            return np.nan
            raise Exception('')

        if self.a.y == self.b.y:
            return self.a.y

        dx = self.b.x - self.a.x
        dy = self.b.y - self.a.y

        return (x - self.a.x) * dy / dx + self.a.y

    def eval_at(self, t) -> Point:
        return Point(self.a.x + t * (self.b.x - self.a.x), self.a.y + t * (self.b.y - self.a.y))

    def get_scale(self, x: float = None, y: float = None) -> float:
        if y != None:
            if y == self.a.y:
                return 0

            return (y - self.a.y) / (self.b.y - self.a.y)

        if x == self.a.x:
            return 0

        return (x - self.a.x) / (self.b.x - self.a.x)

    def plot(self, label_line: str = None, label_points: str = None, color_line: tuple = None, color_points: tuple = None):
        if color_line == None:
            color_line = color_points

        if color_points == None:
            color_points = color_line

        plt.plot([self.a.x, self.b.x], [self.a.y, self.b.y], 'o', color=color_points, label=label_points)
        plt.axline([self.a.x, self.a.y], [self.b.x, self.b.y], color=color_line, label=label_line)