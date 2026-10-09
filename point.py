import math
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return '(' + str(self.x) + '; ' + str(self.y) + ')'

    def get_distance_to_other(self, other_point):
        return math.dist((self.x, self.y), (other_point.x, other_point.y))