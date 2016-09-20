#!/usr/bin/env python

# TODO: test this code

import datetime
import math
import os
import sys
import time
import argparse

import cv2
import matplotlib.pyplot as plt

import extDrone
import deadReckoning
import detectMarker
from config import Config


#Get calibration data for configuration and output path for video
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--calibration", action="store", type=str, required=True, help="Path to calibration file")
parser.add_argument("-o", "--output", action="store", type=str, required=True,
                    help="Path to a file to store processed video")
args = parser.parse_args()

config = Config(args.calibration)
config.fps = 15.0

output = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'XVID'), config.fps,
                         (config.imageWidth, config.imageHeight))


#Initialize drone and deadReckoning
drone = extDrone.Drone()
drone.startup()
# TODO: Initialize deadReckoning with y-axis pointing north
DR = DeadReckoning(drone)
DR.initRTPlot()


#Start camera
drone.setConfigAllID()
drone.sdVideo()
drone.groundCam()
drone.videoFPS(config.fps)

CDC = drone.ConfigDataCount
while CDC == drone.ConfigDataCount:
    time.sleep(0.001)


#Show video
drone.startVideo()
drone.showVideo()


# TODO: Implement map


#Drone execution loop
while (1):
	#Wait for new NavData and update deadReckoning
    navData = drone.getNextDataSet()

    DR.updatePos(navData)
    DR.updateRTPlot()

	#Marker detection
	image = drone.getNextVideoFrame()
    detectMarker.detectMarkers(image, config)
    output.write(image)

	# TODO: Determine position on map

	# TODO: Implement autonomous flying (fly to marker or random walk)

	#Control input
    key = drone.getKey()
    if key:
        drone.simplePiloting(key)
        if (key == '0'):
			#Stop drone
            print "Program stopped"
            drone.failSafeStopDrone()

			#Release output
			output.release()

			#Store raw data
            minFree = 1
            while os.path.lexists("./data/rawdata" + str(minFree) + ".txt"): minFree += 1
            with open("./data/rawdata" + str(minFree) + ".txt", "w") as raw_file:
                DR.storeRaw(raw_file)

            plt.pause(5)
            sys.exit()
    else:
        time.sleep(0.01)
