import numpy as np
import re
from cv2 import aruco

import yaml


# noinspection PyMethodMayBeStatic
class Config:
    def __init__(self, filename=None):
        """
        This class stores the configuration of the marker detection
        :param filename: An optional path to a calibration file
        """
        self.camMatrix = None
        self.distCoeffs = None
        self.imageWidth = 0
        self.imageHeight = 0

        self.detectorParams = aruco.DetectorParameters_create()
        self.detectorParams.doCornerRefinement = True

        self.markerLength = 0.11
        self.fps = 20.0

        if (filename is not None):
            self.parseConfig(filename)

    def parseConfig(self, filename):
        """
        Parse the given calibration file
        :param filename: The calibration file to be parsed
        :return: None
        """
        with open(filename) as f:
            # skip header line
            f.readline()
            ymlContent = f.read()
            # remove !!opencv-matrix
            regex = re.compile(r"!!.*")
            conf = yaml.load(regex.sub(r'', ymlContent))

            self.camMatrix = self.__parseNumpyMatrix(conf["camera_matrix"])
            self.distCoeffs = self.__parseNumpyMatrix(conf["distortion_coefficients"])
            self.imageWidth = conf["image_width"]
            self.imageHeight = conf["image_height"]

    def isPoseDetectionEnabled(self):
        """
        Pose detection is enabled if a calibration file was parsed.
        :return: bool
        """
        return self.camMatrix is not None and self.distCoeffs is not None

    def __parseNumpyMatrix(self, data):
        cols = data["cols"]
        rows = data["rows"]
        return np.array(data["data"]).reshape((cols, rows))
