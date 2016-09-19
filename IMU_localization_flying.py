#!/usr/bin/env python

# TODO: test this code

import datetime
import math
import os
import sys
import time

import matplotlib.pyplot as plt

import extDrone


def createFolder(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


class DeadReckoning:
    def __init__(self, drone):
        self.x = 0
        self.y = 0
        self.z = 0
        self.historyX = [0]
        self.historyY = [0]
        self.timeStart = datetime.datetime.now()
        self.lastTimestamp = datetime.datetime.now()
        self.phio = drone.NavData["demo"][2][2]

    def updatePos(self, navData):
        # adjusting expected speed
        vx = navData["demo"][4][0]
        vy = navData["demo"][4][1]
        vz = navData["demo"][4][2]

        # adjusting angle (phid is in degree, phi is in radian)
        phid = navData["demo"][2][2]
        phi = ((phid - self.phio) / 180) * math.pi

        z = navData["demo"][3]

        # measuring total time and time since last datapoint
        time = datetime.datetime.now()
        diff = (time - self.lastTimestamp).microseconds
        total = (time - self.timeStart).microseconds
        self.lastTimestamp = time

        # calculating expected position
        self.x += (math.cos(phi) * vx - math.sin(phi) * vy) * diff / 1000000
        self.y -= (math.cos(phi) * vy + math.sin(phi) * vx) * diff / 1000000

        self.historyX.append(self.x)
        self.historyY.append(self.y)

    # TODO implement
    def storeRaw(self, file):
        pass

    def loadRaw(self):
        pass

    # noinspection PyMethodMayBeStatic
    def initRTPlot(self):
        plt.axis([-4000, 4000, -4000, 4000])
        plt.ion()
        plt.pause(0.05)

    def updateRTPlot(self):
        # plot new datapoint
        # TODO better plotting algorithm
        plt.plot([self.historyX[-1], self.x], [self.historyY[-1], self.y], facecolor="b")
        plt.pause(0.05)


if (__name__ == "__main__"):
    drone = extDrone.Drone()
    drone.startup()
    DR = DeadReckoning(drone)
    DR.initRTPlot()

    while (1):
        navData = drone.getNextDataSet()

        DR.updatePos(navData)
        DR.updateRTPlot()

        key = drone.getKey()
        if key:
            drone.simplePiloting(key)
            if (key == '0'):
                print "Program stopped"
                drone.failSafeStopDrone()

                minFree = 1
                while os.path.lexists("./data/rawdata" + str(minFree) + ".txt"): minFree += 1
                with open("./data/rawdata" + str(minFree) + ".txt", "w") as raw_file:
                    DR.storeRaw(raw_file)

                plt.pause(5)
                sys.exit()
        else:
            time.sleep(0.01)
