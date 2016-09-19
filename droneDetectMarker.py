import argparse
import time

import cv2

import detectMarker
import extDrone
from config import Config

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--calibration", action="store", type=str, required=True, help="Path to calibration file")
parser.add_argument("-o", "--output", action="store", type=str, required=True,
                    help="Path to a file to store processed video")
args = parser.parse_args()

config = Config(args.calibration)
config.fps = 15.0

output = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'XVID'), config.fps,
                         (config.imageWidth, config.imageHeight))

drone = extDrone.Drone()
drone.startup()

drone.setConfigAllID()
drone.sdVideo()
drone.groundCam()
drone.videoFPS(config.fps)

CDC = drone.ConfigDataCount
while CDC == drone.ConfigDataCount:
    time.sleep(0.001)

drone.startVideo()
drone.showVideo()

print "Press ESC to stop recording"
print "Press space to switch cameras"

while True:
    image = drone.getNextVideoFrame()
    detectMarker.detectMarkers(image, config)
    output.write(image)

    key = drone.getKey()
    if (key == " "):
        drone.toggleCamera()
    elif (key and ord(key) == 27):
        break

output.release()
