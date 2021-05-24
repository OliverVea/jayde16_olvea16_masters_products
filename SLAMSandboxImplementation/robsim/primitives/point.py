from math import sqrt, cos, sin, atan2

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __eq__(self, pt):
        if pt == None: return False
        return (self.x == pt.x) and (self.y == pt.y)

    def __ne__(self, pt):
        if pt == None: return True
        return (not isinstance(pt, Point)) or (self.x != pt.x) or (self.y != pt.y)

    def __iter__(self):
        return iter([self.x, self.y])

    def norm(self):
        return sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        n = self.norm()
        return Point(self.x / n, self.y / n)

    def __add__(self, pt):
        return Point(self.x + pt.x, self.y + pt.y)

    def __sub__(self, pt):
        return Point(self.x - pt.x, self.y - pt.y)

    def __mul__(self, k):
        return Point(self.x * k, self.y * k)

    def __truediv__(self, k):
        return Point(self.x / k, self.y / k)

    def as_polar(self):
        d = sqrt(self.x**2 + self.y**2)
        a = atan2(self.y, self.x)

        return a, d

    @staticmethod
    def from_polar(a, d):
        x = cos(a) * d
        y = sin(a) * d

        return Point(x, y)

    # Returns a relative point in respect to another pose.
    def relative(self, pose):
        x = self.x - pose.x
        y = self.y - pose.y

        x, y = x * cos(-pose.theta) - y * sin(-pose.theta), \
               x * sin(-pose.theta) + y * cos(-pose.theta)

        return Point(x, y)

    # Returns the global coordinate in respect to another coordinate.
    def absolute(self, pose):
        x, y = self.x * cos(pose.theta) - self.y * sin(pose.theta) + pose.x, \
               self.x * sin(pose.theta) + self.y * cos(pose.theta) + pose.y

        return Point(x, y)