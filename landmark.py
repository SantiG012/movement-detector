import math

class Landmark():
    x = 0
    y = 0
    z = 0

    def __init__(self, x, y, z):
        self.x = math.floor(x)
        self.y = math.floor(y)
        self.z = math.floor(z)