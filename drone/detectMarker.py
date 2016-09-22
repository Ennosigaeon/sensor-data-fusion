import argparse
import numpy as np
from cv2 import aruco

import cv2

import config


# noinspection PyMethodMayBeStatic,PyShadowingNames
class MarkerDetector:
    def __init__(self, config, filterFrames=10, dictionary=aruco.getPredefinedDictionary(aruco.DICT_4X4_50)):
        self.config = config
        self.filterFrames = filterFrames
        self.dictionary = dictionary
        self.distances = {}
        self.frameCount = {}
        self.missingFrames = {}

    def highlightCameraCenter(self, frame):
        """
        Highlights the center of the camera in the current frame.
        :param frame: The current frame as a numpy array
        """
        cv2.line(frame, (frame.shape[1] / 2, 0), (frame.shape[1] / 2, frame.shape[0]), (255, 0, 0), 1)
        cv2.line(frame, (0, frame.shape[0] / 2), (frame.shape[1], frame.shape[0] / 2), (255, 0, 0), 1)

    # noinspection PyShadowingNames
    def detect(self, frame):
        """
        Detects markers in the current frame. Detected markers are highlighted and their ids and smoothed distances are
        returned.
        :param frame: The current frame as a numpy array
        :return: A list of tupels containing detected marker id and distance in cm from camera center.
        """
        result = []
        corners, ids, rejectedPoints = aruco.detectMarkers(frame, self.dictionary, np.zeros(1), np.zeros(1),
                                                           self.config.detectorParams)
        if (ids is not None):
            ids = ids.flatten()
            aruco.drawDetectedMarkers(frame, corners, ids)

            rvecs, tvecs = aruco.estimatePoseSingleMarkers(corners, self.config.markerLength, self.config.camMatrix,
                                                           self.config.distCoeffs, np.zeros(1), np.zeros(1))
            for i in range(len(ids)):
                aruco.drawAxis(frame, self.config.camMatrix, self.config.distCoeffs, rvecs[i], tvecs[i],
                               self.config.markerLength / 2)
                res = self.__filterDistance(ids[i], rvecs[i], tvecs[i])
                if (res):
                    result.append(res)

        self.__cleanUp(ids)
        return result

    def __filterDistance(self, arucoId, rvec, tvec):
        if (arucoId not in self.distances):
            self.distances[arucoId] = np.zeros(3)
            self.frameCount[arucoId] = self.filterFrames
        self.missingFrames[arucoId] = self.filterFrames
        self.frameCount[arucoId] -= 1

        # distance in world coordinates
        rotM = cv2.Rodrigues(rvec)[0]
        cameraPosition = -rotM.dot(tvec.T).flatten()
        self.distances[arucoId] += cameraPosition.T

        if (self.frameCount[arucoId] == 0):
            res = [int(arucoId), (self.distances[arucoId] / self.filterFrames).tolist()]
            del self.distances[arucoId]
            del self.missingFrames[arucoId]
            del self.frameCount[arucoId]
            # append result in cm
            return res
        return None

    def __cleanUp(self, ids):
        """
        Removes old ids if not seen for longer time.
        """
        for key in self.missingFrames.keys():
            if (ids is not None and key in ids):
                continue
            self.missingFrames[key] -= 1
            if (self.missingFrames[key] == 0):
                del self.distances[key]
                del self.missingFrames[key]
                del self.frameCount[key]


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
    markerDetector = MarkerDetector(config)

    print "Press ESC to close video"
    while True:
        ret, frame = input.read()
        markerDetector.highlightCameraCenter(frame)
        markers = markerDetector.detect(frame)
        for marker in markers:
            print "Detected marker {} at {}".format(marker[0], marker[1])

        if (output is not None):
            output.write(frame)
        cv2.imshow('frame', frame)
        if (cv2.waitKey(1) & 0xFF == 27):
            break

    if (output is not None):
        output.release()
    input.release()
    cv2.destroyAllWindows()
