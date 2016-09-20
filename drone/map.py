import math


class Position:
    """
    Represents a three dimensional position of an object.
    """

    def __init__(self, x=None, y=None, z=0, phi=0):
        self.x = x
        self.y = y
        self.z = z
        self.phi = phi

    def updatePosition(self, vx, vy, phi, deltaTime):
        x = self.x + (math.cos(phi) * vx - math.sin(phi) * vy) * deltaTime / 1000000
        y = self.y - (math.cos(phi) * vy + math.sin(phi) * vx) * deltaTime / 1000000
        return Position(x, y, 0, phi)


class Landmark:
    """
    Represents a landmark in the world. A landmark has a position and an aruco marker id.
    """

    def __init__(self, arucoId=None, position=None):
        self.arucoId = arucoId
        self.position = position


class Map:
    """
    Represents a map of the world.
    """

    def __init__(self):
        self.landmarks = {}

    def addLandmark(self, landmark):
        """
        Adds the given landmark to this map. If a landmark with the same id already exists it is replaced.
        :param landmark: The landmark to be stored.
        """
        self.landmarks[landmark.arucoId] = landmark

    def getAllLandmarks(self):
        """
        Returns a list of all landmarks.
        :return: A list of all landmarks
        """
        return self.landmarks.values()
