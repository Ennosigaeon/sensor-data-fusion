import argparse
import numpy as np
from curses import ascii
from cv2 import aruco

import cv2

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--target", action="store", type=str, required=True, choices=["board", "marker"],
                    help="Method to create sequence.")
parser.add_argument("-o", "--output", action="store", type=str, required=True,
                    help="Either filename for checkerboard or folder to store markers in")
parser.add_argument("-r", "--rows", action="store", type=int, default=5, help="Number of rows in checker board")
parser.add_argument("-c", "--columns", action="store", type=int, default=8, help="Number of columns in checker board")
parser.add_argument("-p", "--pixel", action="store", type=int, default=200, help="Size of one marker in pixel")
parser.add_argument("-n", "--number", action="store", type=int, default=200, help="Number of markers to be created")
args = parser.parse_args()

if args.target == "board":
    image = np.ones((args.pixel * args.rows, args.pixel * args.columns), dtype=np.uint8) * 255

    for row in range(args.rows):
        for column in range(args.columns):
            if (row % 2 + column % 2 == 1):
                continue
            markerId = (row * args.columns) + column

            marker = aruco.drawMarker(dictionary, markerId, args.pixel, image)
            image[row * args.pixel:(row + 1) * args.pixel, column * args.pixel:(column + 1) * args.pixel] = marker

    cv2.imwrite(args.output, image)
    cv2.imshow('Image', image)
    while (True):
        if (cv2.waitKey(1) & 0xFF == ord(ascii.ESC)):
            break

if args.target == "marker":
    for i in range(args.number):
        image = np.ones((1, 1), dtype=np.uint8)
        marker = aruco.drawMarker(dictionary, i, args.pixel, image)
        cv2.imwrite("{}-{}.png".format(args.output, i), marker)