import argparse
import time

import cv2

from drone import detectMarker, extDrone
from drone.config import Config

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--calibration", action="store", type=str, required=True, help="Path to calibration file")
parser.add_argument("-o", "--output", action="store", type=str, required=True,
                    help="Path to a file to store processed video")
args = parser.parse_args()

config = Config(args.calibration)
config.fps = 15.0

output = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'XVID'), config.fps,
                         (config.imageWidth, config.imageHeight))

markerDetector = detectMarker.MarkerDetector(config)

drone = extDrone.Drone()
drone.startup()
drone.reset()
drone.defaultInit()

drone.startCamera(config.fps)

print "Press ESC to stop recording"
print "Press space to switch cameras"

while True:
    image = drone.getNextVideoFrame()
    markerDetector.detect(image)
    output.write(image)
    cv2.imshow("Image", image)

    key = cv2.waitKey(1) & 0xFF
    if (key == ord(" ")):
        drone.toggleCamera()
    elif (key == 27):
        break

output.release()
