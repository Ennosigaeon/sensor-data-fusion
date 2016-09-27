import math


class Position:
    """
    Represents a three dimensional position of an object.
    """

    def __init__(self, x, y, z=0, phi=0):
        self.x = x
        self.y = y
        self.z = z
        self.phi = phi

    def updatePosition(self, vx, vy, phi, deltaTime):
        x = self.x + (math.cos(phi) * vx - math.sin(phi) * vy) * deltaTime / 1000
        y = self.y - (math.sin(phi) * vx + math.cos(phi) * vy) * deltaTime / 1000
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

    def determinePosition(self, markers):
        """
        Determines position based on detected markers
        :return: Estimated position
        """
        x = 0.0
        y = 0.0
        for marker in markers:
            arucoId = marker[0]
            distance = marker[1]
            if (arucoId not in self.landmarks):
                raise ValueError("Invalid marker id {}".format(arucoId))
            x += self.landmarks[arucoId].position.x - distance[0]
            y += self.landmarks[arucoId].position.y - distance[1]
            # TODO: angle update based on marker yaw
        x /= len(markers)
        y /= len(markers)
        return Position(x, y)
        
def defaultMap():
    map = Map()
    map.addLandmark(Landmark(0, Position(2, 0)))
    map.addLandmark(Landmark(1, Position(2, 1)))
    map.addLandmark(Landmark(2, Position(0, 1)))
    map.addLandmark(Landmark(3, Position(0, 0)))
    map.addLandmark(Landmark(4, Position(1, 0.5)))
    map.addLandmark(Landmark(5, Position(0, 0.5)))
    map.addLandmark(Landmark(6, Position(1, 0)))
    map.addLandmark(Landmark(7, Position(1, 1)))
    map.addLandmark(Landmark(8, Position(0.5, 0.5)))
    map.addLandmark(Landmark(9, Position(1.5, 0.5)))
    map.addLandmark(Landmark(10, Position(2, 0.5)))
    map.addLandmark(Landmark(11, Position(2, -0.5)))
    map.addLandmark(Landmark(12, Position(0, -0.5)))
    map.addLandmark(Landmark(13, Position(0.5, -0.5)))
    map.addLandmark(Landmark(14, Position(1, -0.5)))
    map.addLandmark(Landmark(15, Position(1.5, -0.5)))
    map.addLandmark(Landmark(16, Position(0, -1)))
    map.addLandmark(Landmark(17, Position(0.5, 0)))
    map.addLandmark(Landmark(18, Position(1, -1)))
    map.addLandmark(Landmark(19, Position(1.5, 0)))
    map.addLandmark(Landmark(20, Position(2, -1)))
    map.addLandmark(Landmark(21, Position(1.5, 1)))
    map.addLandmark(Landmark(22, Position(0.5, 1)))
    map.addLandmark(Landmark(23, Position(0.5, -1)))
    map.addLandmark(Landmark(24, Position(1.5, -1)))
    map.addLandmark(Landmark(25, Position(-0.5, 1)))
    map.addLandmark(Landmark(26, Position(-0.5, 0.5)))
    map.addLandmark(Landmark(27, Position(-0.5, 0)))
    map.addLandmark(Landmark(28, Position(-0.5, -0.5)))
    map.addLandmark(Landmark(29, Position(-0.5, -1)))
    return map

def simpleMap():
    map = Map()
    map.addLandmark(Landmark(0, Position(2, 0)))
    map.addLandmark(Landmark(1, Position(2, 1)))
    map.addLandmark(Landmark(2, Position(0, 1)))
    map.addLandmark(Landmark(3, Position(0, 0)))
    map.addLandmark(Landmark(4, Position(1, 0.5)))
    return map
