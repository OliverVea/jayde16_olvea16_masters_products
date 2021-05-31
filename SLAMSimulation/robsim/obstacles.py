from robsim.primitives.point import Point
from robsim.primitives.line import Line
from robsim.utility import dist_l2

from matplotlib.patches import Rectangle, Circle
from math import sqrt, pi, sin, cos, ceil

class Obstacle:
    pass

class RectangleObstacle(Obstacle):
    def __init__(self, origin: Point, dimensions: tuple, angle: float = 0.0, color=None):
        self.origin = origin
        self.dimensions = dimensions
        self.angle = angle
        self.color = None

    def check(self, point: Point) -> bool:
        return self.origin.x <= point.x <= self.origin.x + self.dimensions[0] and \
            self.origin.y <= point.y <= self.origin.y + self.dimensions[1]
        
    def get_patch(self) -> Rectangle:
        return Rectangle((self.origin.x, self.origin.y), self.dimensions[0], self.dimensions[1], self.angle, color=self.color)

    def get_corners(self, repeat_first: bool = True) -> list:
        corners = [self.origin,
            Point(self.origin.x + self.dimensions[0], self.origin.y),
            Point(self.origin.x + self.dimensions[0], self.origin.y + self.dimensions[1]),
            Point(self.origin.x, self.origin.y + self.dimensions[1])]

        if repeat_first:
            corners.append(self.origin)

        return corners

    def get_points(self, density: float) -> list:
        corners = self.get_corners()

        pts = []
        for i in range(4):
            dist = dist_l2(corners[i], corners[i + 1])
            N = ceil(dist * density)
            pts.extend([Point(corners[i].x + j/N * (corners[i + 1].x - corners[i].x), corners[i].y + j/N * (corners[i + 1].y - corners[i].y)) for j in range(N)])
        
        return pts

    def get_intersections(self, line: Line, behind: bool = False) -> list:
        pts = self.get_corners()

        edges = [Line(pts[i], pts[i + 1]) for i in range(4)]

        intersections = [edge.get_intersection(line) for edge in edges]
        intersections = [i for i in intersections if i != None]

        intersections = list(filter(lambda intersection: 0 <= intersection[1] <= 1, intersections))

        if not behind:
            intersections = list(filter(lambda intersection: intersection[2] > 0, intersections))
        
        intersections = [i[0] for i in intersections]

        return intersections

class CircleObstacle(Obstacle):
    def __init__(self, origin: Point, radius: float):
        self.origin = origin
        self.radius = radius

    def check(self, point: Point) -> bool:
        return dist_l2(self.origin, point) < self.radius

    def get_patch(self) -> Circle:
        return Circle((self.origin.x, self.origin.y), self.radius)

    def get_points(self, density) -> list:
        N = ceil(2 * pi * self.radius * density)
        points = [2 * pi * i / N for i in range(N + 1)]
        points = [Point(self.radius * cos(angle) + self.origin.x, self.radius * sin(angle) + self.origin.y) for angle in points]
        return points

    def get_intersections(self, line: Line) -> list:
        ax, bx, ay, by, x0, y0 = line.a.x, line.b.x, line.a.y, line.b.y, self.origin.x, self.origin.y
        swapped = ax == bx

        if swapped:
            ax, bx, ay, by, x0, y0 = ay, by, ax, bx, y0, x0

        k1 = (by - ay) / (bx - ax)
        k2 = ay - k1 * ax - y0

        a = 1 + k1 * k1
        b = 2 * k1 * k2 - 2 * x0
        c = k2 * k2 - self.radius * self.radius + x0 * x0

        d = b * b - 4 * a * c

        if d < 0:
            return []
        
        elif d == 0:
            x_vec = [-b/(2*a)]
        
        else:
            x_vec = [(-b + sqrt(d))/(2*a), (-b - sqrt(d))/(2*a)]

        if swapped:
            intersections = [Point(ay + (x - ax) / (bx - ax)*(by - ay), x) for x in x_vec]
        else:
            intersections = [Point(x, ay + (x - ax) / (bx - ax)*(by - ay)) for x in x_vec]

        return intersections

def obstacle_from_dict(d: dict) -> Obstacle:
    obstacle_type = d['type']

    if obstacle_type == 'rectangle':
        return RectangleObstacle(Point(d['origin'][0], d['origin'][1]), tuple(d['dimensions']), d['angle'], d['color'])
    
    if obstacle_type == 'circle':
        return CircleObstacle(Point(d['origin'][0], d['origin'][1]), d['radius'])
