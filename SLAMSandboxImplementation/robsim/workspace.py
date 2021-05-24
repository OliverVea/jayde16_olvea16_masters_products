import robsim.obstacles as obstacles
from robsim.primitives.point import Point
from robsim.primitives.line import Line
from robsim.utility import dist_l2

import json
import matplotlib.pyplot as plt
from random import random
from math import pi, sin, cos, floor, ceil, radians

import numpy as np

import cv2

class Workspace:
    def __init__(self, config_file: str, background_file: str):
        # Read background image
        im = cv2.imread(background_file, cv2.IMREAD_GRAYSCALE)
        self.background = cv2.threshold(im, 127, 1, cv2.THRESH_BINARY)[1]
        self.dimensions = tuple(reversed(self.background.shape))

        #im = cv2.resize(im, (600, 300), interpolation=cv2.INTER_NEAREST )
        #cv2.imshow('img', im)
        #cv2.waitKey()

        # Read config file
        with open(config_file, 'r') as f:
            ws = json.load(f)

        self.solid_edge = ws.setdefault('solid_edge', False)

        self.obstacles = ws.setdefault('obstacles', [])
        self.obstacles = [obstacles.obstacle_from_dict(obstacle) for obstacle in self.obstacles]

        self.landmarks = ws.setdefault('landmarks', [])

    def set_landmarks(self, landmarks):
        self.landmarks = landmarks

    def is_free(self, pt: Point) -> bool:
        # Bounds check
        if self.solid_edge:
            if pt.x < 0 or pt.x >= self.dimensions[0] or pt.y < 0 or pt.y >= self.dimensions[1]:
                return False

        # Static collision check
        if not self.background[int(pt.x), int(pt.y)]:
            return False

        # Obstacle collision check
        for obstacle in self.obstacles:
            if obstacle.check(pt):
                return False
        return True

    def plot(self, border: int = 1, border_color = 'black', show = False, figname: str = None, grid_size: float = None, figsize: tuple = (12,12), dpi: int = 200):
        fig = plt.figure(figname, figsize=figsize, dpi=dpi)
        ax = plt.gca()
        ax.set_aspect(1)

        # Draw background
        for y, row in enumerate(self.background):
            for x, cell in enumerate(row):
                if not cell:
                    origin = Point(x, y)
                    rect = obstacles.RectangleObstacle(origin=origin, dimensions=(1, 1), color='black')
                    ax.add_patch(rect.get_patch())
        
        if grid_size != None:
            ax.set_xticks(np.arange(0, self.dimensions[0], 5 * grid_size))
            ax.set_xticks(np.arange(0, self.dimensions[0], grid_size), minor=True)
            ax.set_yticks(np.arange(0, self.dimensions[1], 5 * grid_size))
            ax.set_yticks(np.arange(0, self.dimensions[1], grid_size), minor=True)

            plt.grid(True, which='both', color='black', linestyle='-', linewidth=1, alpha=0.2)

        x_min = 0
        x_max = self.dimensions[0]

        y_min = 0
        y_max = self.dimensions[1]

        ax.set(xlim=(x_min - border, x_max + border), ylim=(y_min - border, y_max + border))

        # Draw map edge
        if self.solid_edge:
            plt.plot([x_min, x_min,x_max, x_max, x_min], [y_min, y_max, y_max, y_min, y_min], '-', color=border_color)

        # Draw obstacles
        for obstacle in self.obstacles:
            ax.add_patch(obstacle.get_patch())

        # Draw landmarks
        x = [landmark[0] for landmark in self.landmarks]
        y = [landmark[1] for landmark in self.landmarks]

        plt.plot(x, y, 's', color='red', markersize=3)

        ax.invert_yaxis()
        if show:
            plt.show()

        return fig

    def get_intersections(self, line: Line, backwards: bool = False, only_first: bool = True):
        intersections = []

        # Static map intersections
        ys = list(range(self.dimensions[1]))
        map_intersections = [(line.get_x(y), y) for y in ys]

        for i in map_intersections:
           if 0 <= i[0] <= self.dimensions[0]:
               x = int(i[0])
               y = int(i[1])
               cell_values = self.background[y, x] \
                   + self.background[y - 1, x]
               if cell_values == 1:
                   intersections.append(Point(*i))
                   #plt.plot((x + 0.5, x + 0.5), (y + 0.5, y - 1 + 0.5), 'o', color='green')

        xs = list(range(self.dimensions[0]))
        map_intersections = [(x, line.get_y(x)) for x in xs]

        for i in map_intersections:
           if 0 <= i[1] <= self.dimensions[1]:
               x = int(i[0])
               y = int(i[1])
               cell_values = self.background[y, x] \
                   + self.background[y, x - 1]
               if cell_values == 1:
                   intersections.append(Point(*i))

        # Obstacle intersections
        for i, obstacle in enumerate(self.obstacles):
            intersections.extend(obstacle.get_intersections(line))
        
        # Edge intersections
        if self.solid_edge:
            corners = [Point(0,0), Point(self.dimensions[0], 0), Point(self.dimensions[0], self.dimensions[1]), Point(0, self.dimensions[1]), Point(0, 0)]
            edges = [Line(corners[i], corners[i + 1]) for i in range(4)]
            edge_intersections = [edge.get_intersection(line) for edge in edges if edge.get_intersection(line) != None]
            edge_intersections = [i[0] for i in edge_intersections if 0 <= i[1] <= 1]
            intersections.extend(edge_intersections)

        if not backwards:
            intersections = [i for i in intersections if not np.isnan(i.y) and line.get_scale(x=i.x) >= 0]

        if only_first and len(intersections) > 1:
            intersections = [min(intersections, key= lambda i: dist_l2(line.a, i))]

        return intersections

    def lidar_scan(self, origin, fov: float = 270, da: float = 1.25, max_range: float = None):
        N = ceil(fov / da)
        da = radians(da)
        fov = da * N

        a0 = origin.theta - fov/2

        rads = [a0 + da*i for i in range(N + 1)]

        pts = [Point(cos(rad) + origin.x, sin(rad) + origin.y) for rad in rads]
        lines = [Line(origin, pt) for pt in pts]
        intersections = [self.get_intersections(line, backwards=False, only_first=True) for line in lines]
        intersections = [intersection[0] for intersection in intersections if len(intersection) != 0]

        if max_range != None:
            intersections = [pt for pt in intersections if dist_l2(origin, pt) <= max_range]

        return intersections

    def sample_free(self):
        pt = None
        while pt == None or not self.is_free(pt):
            pt = Point(random() * self.dimensions[0], random() * self.dimensions[1])
        return pt

if __name__ == '__main__':
    print('a')

    print('v')