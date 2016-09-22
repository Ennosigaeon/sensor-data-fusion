#!/usr/bin/env python

# TODO: test this code

import datetime
import math
import os
import sys

from time import sleep

import matplotlib.pyplot as plt

from extDrone import Drone
from plot import RealTimePlot
from map import Position


def createFolder(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


class DeadReckoning:
    def __init__(self, position, time=None):
        self.pos = position
        self.historyPos = [position]
        self.historyPosCor = [position]
        self.historyTime = [datetime.datetime.now()]
        self.historyConfirmed = []
        self.timeStart = datetime.datetime.now()
        if (time):
            self.lastTimestamp = time
        else:
            self.lastTimestamp = datetime.datetime.now()
        self.phio = 0
        self.rtp = RealTimePlot()

    def setPhiToZero(self, drone):
        self.phio = drone.navData["demo"][2][2]

    def setPhioToValue(self, phi):
        self.phio = phi

    def updatePos(self, speed, phid, timestamp=None):
        # adjusting angle (phid is in degree, phi is in radian)
        phi = (((phid - self.phio) % 360) / 180) * math.pi

        # measuring total time and time since last datapoint
        if (timestamp):
            time = timestamp
        else:
            time = datetime.datetime.now()
        deltaTime = (time - self.lastTimestamp).total_seconds()
        self.lastTimestamp = time

        # calculating expected position
        self.pos = self.pos.updatePosition(speed[0], speed[1], phi, deltaTime)

        self.historyPos.append(self.pos)
        self.historyPosCor.append(self.pos)
        self.historyTime.append(time)

        histPos = self.historyPos[-2]
        self.rtp.drawLine([histPos.x, histPos.y], [self.pos.x, self.pos.y], "b")

    def updateConfPos(self, position):
        time = datetime.datetime.now()
        # self.rtp.drawLine([position.x, position.y], [self.pos.x, self.pos.y], "r")

        # TODO use Kalman filter
        self.pos = position
        self.historyPos.append(position)
        self.historyPosCor.append(position)
        self.historyTime.append(time)
        self.historyConfirmed.append(len(self.historyPos) - 1)

        self.correctPos()

    def correctPos(self):
        if len(self.historyConfirmed) > 1:
            deltaTotal = (self.historyTime[self.historyConfirmed[-1]] -
                          self.historyTime[self.historyConfirmed[-2]]).total_seconds()
            deltaPosX = self.historyPos[self.historyConfirmed[-1]].x - self.historyPos[self.historyConfirmed[-1] - 1].x
            deltaPosY = self.historyPos[self.historyConfirmed[-1]].y - self.historyPos[self.historyConfirmed[-1] - 1].y

            for i in range(self.historyConfirmed[-2], self.historyConfirmed[-1]):
                deltaTime = (self.historyTime[i] - self.historyTime[self.historyConfirmed[-2]]).total_seconds()
                fracTime = 1.0 * deltaTime / deltaTotal
                self.historyPosCor[i].x = self.historyPos[i].x + fracTime * deltaPosX
                self.historyPosCor[i].y = self.historyPos[i].y + fracTime * deltaPosY
        else:
            deltaPosX = self.historyPos[self.historyConfirmed[-1]].x - self.historyPos[self.historyConfirmed[-1] - 1].x
            deltaPosY = self.historyPos[self.historyConfirmed[-1]].y - self.historyPos[self.historyConfirmed[-1] - 1].y

            for i in range(0, self.historyConfirmed[-1]):
                self.historyPosCor[i].x = self.historyPos[i].x + deltaPosX
                self.historyPosCor[i].y = self.historyPos[i].y + deltaPosY

    def drawCorrectedPath(self):
        for i in range(len(self.historyPosCor) - 1):
            self.rtp.drawLine([self.historyPosCor[i].x, self.historyPosCor[i].y],
                              [self.historyPosCor[i + 1].x, self.historyPosCor[i + 1].y], "r")


if (__name__ == "__main__"):
    drone = Drone()
    drone.startup()
    drone.reset()
    drone.defaultInit()

    DR = DeadReckoning(Position(0, 0))

    # Change if yaw is wrong
    # DR.setPhiToZero(drone.getOrientation())

    while (1):
        navData = drone.getNextDataSet()

        DR.updatePos(drone.getSpeed(navData), drone.getOrientation(navData))

        sleep(1)
        key = drone.getKey()
        if key:
            drone.simplePiloting(key)
            if (key == '0'):
                print "Program stopped"
                drone.failSafeStopDrone()

                plt.pause(5)
                sys.exit()
            if (key == '1'):
                pass
        else:
            sleep(0.01)
