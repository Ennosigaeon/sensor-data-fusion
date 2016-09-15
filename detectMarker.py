import argparse
import numpy as np
import re
from curses import ascii
from cv2 import aruco

import cv2
import yaml


def readCalibrationFile(fileName):
    with open(fileName) as f:
        # skip header line
        f.readline()
        ymlContent = f.read()
        # remove !!opencv-matrix
        regex = re.compile(r"!!.*")
        return yaml.load(regex.sub(r'', ymlContent))


def parseNumpyMatrix(data):
    cols = data["cols"]
    rows = data["rows"]
    return np.array(data["data"]).reshape((cols, rows))


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--video", action="store", type=str, default="0", help="Load video and process it")
parser.add_argument("-c", "--calibration", action="store", type=str, required=True, help="Path to calibration file")
parser.add_argument("-o", "--output", action="store", type=str, help="Path to a file to store processed video")
parser.add_argument("-l", "--length", action="store", type=float, required=True, help="Edge length of marker in m")
args = parser.parse_args()

markerLength = args.length
config = readCalibrationFile(args.calibration)
camMatrix = parseNumpyMatrix(config["camera_matrix"])
distCoeffs = parseNumpyMatrix(config["distortion_coefficients"])

try:
    # try to use capute device
    input = cv2.VideoCapture(int(args.video))
except ValueError:
    # fallback to load video
    input = cv2.VideoCapture(args.video)

if (args.output):
    output = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'XVID'), 20.0,
                             (config["image_width"], config["image_height"]))

detectorParams = aruco.DetectorParameters_create()
detectorParams.doCornerRefinement = True
dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

while True:
    ret, frame = input.read()

    corners, ids, rejectedPoints = aruco.detectMarkers(frame, dictionary, np.zeros(1), np.zeros(1), detectorParams)
    if (ids is not None):
        ids = ids.flatten()
        print "Detected marker {}".format(ids)
        rvecs, tvecs = aruco.estimatePoseSingleMarkers(corners, markerLength, camMatrix, distCoeffs, np.zeros(1),
                                                       np.zeros(1))
        aruco.drawDetectedMarkers(frame, corners, ids)
        for i in range(len(ids)):
            aruco.drawAxis(frame, camMatrix, distCoeffs, rvecs[i], tvecs[i], markerLength / 2)

    if ('output' in locals()):
        output.write(frame)
    cv2.imshow('frame', frame)
    if (cv2.waitKey(1) & 0xFF == ord(ascii.ESC)):
        break

if ('output' in locals()):
    output.release()
input.release()
cv2.destroyAllWindows()
