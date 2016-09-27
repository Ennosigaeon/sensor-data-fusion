#!/usr/bin/env python

import argparse

import cv2

from drone import deadReckoning, detectMarker, extDrone
from drone.capture import Capture
from drone.config import Config
from drone.map import Map, Landmark, Position

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--calibration", action="store", type=str, required=True, help="Path to calibration file")
parser.add_argument("-o", "--output", action="store", type=str, required=True,
                    help="Path to a file to store processed video")
args = parser.parse_args()

config = Config(args.calibration)
config.fps = 15.0

output = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'XVID'), config.fps,
                         (config.imageWidth, config.imageHeight))

map = Map()
map.addLandmark(Landmark(0, Position(2, 0)))
map.addLandmark(Landmark(1, Position(2, 1)))
map.addLandmark(Landmark(2, Position(0, 1)))
map.addLandmark(Landmark(3, Position(0, 0)))
map.addLandmark(Landmark(4, Position(1, 0.5)))
# Initialize drone and deadReckoning
drone = extDrone.Drone()
drone.startup()
drone.reset()
drone.defaultInit()
drone.startCamera(config.fps)

DR = deadReckoning.DeadReckoning(Position(0, 0))
markerDetector = detectMarker.MarkerDetector(config)
capture = Capture()

captureData = False
# Drone execution loop
while (1):
    # Wait for new NavData and update deadReckoning
    if (captureData):
        navData = drone.getNextDataSet()
        if (navData):
            DR.updatePos(drone.getSpeed(navData), drone.getOrientation(navData))
            capture.addRawSensorData(drone.getSpeed(navData), drone.getOrientation(navData))

    # Marker detection
    image = drone.getNextVideoFrame()
    markers = markerDetector.detect(image)
    output.write(image)
    cv2.imshow("Image", image)
    capture.addMarker(markers)

    if (len(markers) > 0):
        print "Detected marker/s {} {}".format(markers[0][0], markers[0][1])
        position = map.determinePosition(markers)
        # DR.updateConfPos(position)

    # TODO: Implement autonomous flying (fly to marker or random walk)

    # Control input
    key = cv2.waitKey(1) & 0xFF
    key = None if key > 127 else chr(key)
    if key:
        drone.simplePiloting(key)
        if (key == 'r'):
            captureData = not captureData
            if (captureData):
                navData = drone.getNextDataSet(force=True)
                DR.setPhioToValue(drone.getOrientation(navData))
                capture.addPhiO(drone.getOrientation(navData))
        if (key == '0'):
            break

# Stop drone
print "Program stopped"
drone.failSafeStopDrone()
capture.store("test_flight.json")

# Release output
output.release()
