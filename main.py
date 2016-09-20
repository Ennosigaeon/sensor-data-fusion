#!/usr/bin/env python

# TODO: test this code

import argparse
import os
import sys
import time

import cv2
import matplotlib.pyplot as plt

from drone import deadReckoning, detectMarker, extDrone
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

# Initialize drone and deadReckoning
drone = extDrone.Drone()
drone.startup()
DR = deadReckoning.DeadReckoning(Position(0, 0))
DR.setPhiToZero(drone.getOrientation())
DR.initRTPlot()
markerDetector = detectMarker.MarkerDetector(config)

# Start camera
drone.setConfigAllID()
drone.sdVideo()
drone.groundCam()
drone.videoFPS(config.fps)

CDC = drone.ConfigDataCount
while CDC == drone.ConfigDataCount:
    time.sleep(0.001)

# Show video
drone.startVideo()
drone.showVideo()

map = Map()
map.addLandmark(Landmark(0, Position(0, 0)))
map.addLandmark(Landmark(1, Position(1, 0)))
map.addLandmark(Landmark(2, Position(1, 2)))
map.addLandmark(Landmark(3, Position(0, 2)))
map.addLandmark(Landmark(4, Position(0.5, 1)))

# Drone execution loop
while (1):
    # Wait for new NavData and update deadReckoning
    navData = drone.getNextDataSet()

    DR.updatePos(drone.getSpeed(), drone.getOrientation())

    # Marker detection
    image = drone.getNextVideoFrame()
    markers = markerDetector.detect(image)
    output.write(image)

    if (len(markers) > 0):
        print "Detected marker/s {}".format(markers)
        position = map.determinePosition(markers)
        DR.updateConfPos(position)

    # TODO: Implement autonomous flying (fly to marker or random walk)

    # Control input
    key = drone.getKey()
    if key:
        drone.simplePiloting(key)
        if (key == '0'):
            break
    else:
        time.sleep(0.01)

# Stop drone
print "Program stopped"
drone.failSafeStopDrone()

# Release output
output.release()

# Store raw data
minFree = 1
while os.path.lexists("./data/rawdata" + str(minFree) + ".txt"): minFree += 1
with open("./data/rawdata" + str(minFree) + ".txt", "w") as raw_file:
    DR.storeRaw(raw_file)

plt.pause(5)
sys.exit()
