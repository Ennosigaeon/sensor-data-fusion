import json
from datetime import datetime
from time import sleep

import matplotlib.pyplot as plt
import pytz

from drone.deadReckoning import DeadReckoning
from drone.map import Position, Map, Landmark

epoch = datetime.utcfromtimestamp(0)


def unix_time_millis(dt):
    return (dt - epoch).total_seconds()


class Capture:
    def __init__(self):
        self.phio = []
        self.rawSensorData = []
        self.markers = []
        self.sensorIndex = -1
        self.markerIndex = -1

    def addRawSensorData(self, speed, orientation):
        self.rawSensorData.append(
            {"speed": speed, "orientation": orientation, "time": unix_time_millis(datetime.now())}
        )

    def addMarker(self, markers):
        if (markers is None or len(markers) == 0):
            return
        self.markers.append({"markers": markers, "time": unix_time_millis(datetime.now())})

    def addPhiO(self, orientation):
        self.phio.append(orientation)

    def store(self, filename):
        self.rawSensorData = sorted(self.rawSensorData, key=lambda d: d["time"])
        self.markers = sorted(self.markers, key=lambda m: m["time"], reverse=True)

        with open(filename, "w") as f:
            s = json.dumps({"rawSensorData": self.rawSensorData, "markers": self.markers, "phio": self.phio})
            f.write(s)

    def load(self, filename):
        with open(filename, "r") as f:
            lines = f.readline()
            data = json.loads(lines)
            self.phio = data["phio"]
            self.markers = data["markers"]
            self.rawSensorData = data["rawSensorData"]

    def playbackSensor(self):
        self.sensorIndex += 1
        if (self.sensorIndex >= len(self.rawSensorData)):
            return None

        dp = self.rawSensorData[self.sensorIndex]
        return (dp["speed"], dp["orientation"], datetime.fromtimestamp(dp["time"], pytz.utc))

    def playbackMarker(self):
        if (self.sensorIndex + 1 >= len(self.rawSensorData) or len(self.markers) <= 0):
            return (None, None)

        if (self.rawSensorData[self.sensorIndex + 1]["time"] > self.markers[-1]["time"]):
            m = self.markers.pop()
            return (m["markers"], datetime.fromtimestamp(m["time"] / 1000, pytz.utc))
        return (None, None)


if (__name__ == "__main__"):
    map = Map()
    map.addLandmark(Landmark(0, Position(2, 0)))
    map.addLandmark(Landmark(1, Position(2, 1)))
    map.addLandmark(Landmark(2, Position(0, 1)))
    map.addLandmark(Landmark(3, Position(0, 0)))
    map.addLandmark(Landmark(4, Position(1, 0.5)))

    capture = Capture()
    capture.load("../test_flight_hourglass.json")
    DR = DeadReckoning(Position(0, 0), datetime.fromtimestamp(capture.rawSensorData[0]["time"], pytz.utc))
    DR.setPhioToValue(capture.phio[0])

    while (True):
        sensor = capture.playbackSensor()
        if (not sensor):
            break
        DR.updatePos(sensor[0], sensor[1], sensor[2])

        markers, time = capture.playbackMarker()
        if (markers):
            position = map.determinePosition(markers)
            DR.updateConfPos(position, time)
        sleep(0.01)
    # DR.drawCorrectedPath()
    plt.pause(10)
