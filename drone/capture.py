import json
import time
from datetime import datetime

import pytz

from drone.deadReckoning import DeadReckoning
from drone.map import Position

epoch = datetime.utcfromtimestamp(0)


def unix_time_millis(dt):
    return (dt - epoch).total_seconds()


class Capture:
    def __init__(self):
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

    def store(self, filename):
        self.rawSensorData = sorted(self.rawSensorData, key=lambda d: d["time"])
        self.markers = sorted(self.markers, key=lambda m: m["time"], reverse=True)

        with open(filename, "w") as f:
            s = json.dumps({"rawSensorData": self.rawSensorData, "markers": self.markers})
            f.write(s)

    def load(self, filename):
        with open(filename, "r") as f:
            lines = f.readline()
            data = json.loads(lines)
            self.markers = data["markers"]
            self.rawSensorData = data["rawSensorData"]

    def playbackSensor(self):
        self.sensorIndex += 1
        if (self.sensorIndex >= len(self.rawSensorData)):
            return None

        dp = self.rawSensorData[self.sensorIndex]
        # TODO remove / 1000. Only correct for first record.
        return (dp["speed"], dp["orientation"], datetime.fromtimestamp(dp["time"] / 1000, pytz.utc))

    def playbackMarker(self):
        if (self.sensorIndex + 1 >= len(self.rawSensorData) or len(self.markers) <= 0):
            return None

        if (self.rawSensorData[self.sensorIndex + 1]["time"] > self.markers[-1]["time"]):
            return self.markers.pop()["markers"]
        return None


if (__name__ == "__main__"):
    capture = Capture()
    capture.load("../test_flight.json")
    # TODO remove / 1000. Only correct for first record.
    DR = DeadReckoning(Position(0, 0), datetime.fromtimestamp(capture.rawSensorData[0]["time"] / 1000, pytz.utc))

    while (True):
        sensor = capture.playbackSensor()
        if (sensor):
            DR.updatePos(sensor[0], sensor[1], sensor[2])
            print sensor

            markers = capture.playbackMarker()
            if (markers):
                print markers
        else:
            break
    time.sleep(10)
