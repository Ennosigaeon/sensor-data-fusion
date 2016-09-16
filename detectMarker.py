import argparse
import numpy as np
from cv2 import aruco

import cv2

import config


# noinspection PyShadowingNames
def detectMarkers(frame, config, dictionary=aruco.getPredefinedDictionary(aruco.DICT_4X4_50)):
    """
    Detects markers in the current frame. Detected markers are highlighted and their ids are returned
    :param frame: The current frame as a numpy array
    :param config: A Config object
    :param dictionary: The optional dictionary to be used
    :return: A array with all detected markers
    """
    corners, ids, rejectedPoints = aruco.detectMarkers(frame, dictionary, np.zeros(1), np.zeros(1),
                                                       config.detectorParams)
    if (ids is not None):
        ids = ids.flatten()
        aruco.drawDetectedMarkers(frame, corners, ids)

        if (config.isPoseDetectionEnabled()):
            rvecs, tvecs = aruco.estimatePoseSingleMarkers(corners, config.markerLength, config.camMatrix,
                                                           config.distCoeffs, np.zeros(1), np.zeros(1))
            for i in range(len(ids)):
                aruco.drawAxis(frame, config.camMatrix, config.distCoeffs, rvecs[i], tvecs[i], config.markerLength / 2)
    return ids if ids is not None else np.array([])


if (__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video", action="store", type=str, default="0", help="Load video and process it")
    parser.add_argument("-c", "--calibration", action="store", type=str, required=True, help="Path to calibration file")
    parser.add_argument("-o", "--output", action="store", type=str, help="Path to a file to store processed video")
    parser.add_argument("-l", "--length", action="store", type=float, required=True, help="Edge length of marker in m")
    args = parser.parse_args()

    config = config.Config(args.calibration)
    config.markerLength = args.length

    try:
        # try to use capute device
        input = cv2.VideoCapture(int(args.video))
    except ValueError:
        # fallback to load video
        input = cv2.VideoCapture(args.video)

    output = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'XVID'), config.fps,
                             (config.imageWidth, config.imageHeight)) if args.output else None

    print "Press ESC to close video"
    while True:
        ret, frame = input.read()
        detectMarkers(frame, config)
        if (output is not None):
            output.write(frame)
        cv2.imshow('frame', frame)
        if (cv2.waitKey(1) & 0xFF == 27):
            break

    if (output is not None):
        output.release()
    input.release()
    cv2.destroyAllWindows()
