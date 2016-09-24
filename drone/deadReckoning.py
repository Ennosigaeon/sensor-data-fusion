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
        if (time is None):
            time = datetime.datetime.now()
        self.lastTimestamp = time
        self.phio = 0
        self.rtp = RealTimePlot()
        self.rtp.addPoint(self.pos.x, self.pos.y, "b")

    def setPhiToZero(self, drone):
        self.phio = drone.navData["demo"][2][2]

    def setPhioToValue(self, phi):
        print "Setting phio to {}".format(phi)
        self.phio = phi

    def updatePos(self, speed, phid, time=None):
        # adjusting angle (phid is in degree, phi is in radian)
        phi = (((phid - self.phio) % 360) / 180) * math.pi

        # measuring total time and time since last datapoint
        if (time is None):
            time = datetime.datetime.now()
        deltaTime = (time - self.lastTimestamp).total_seconds()
        self.lastTimestamp = time

        # calculating expected position
        self.pos = self.pos.updatePosition(speed[0], speed[1], phi, deltaTime)

        self.historyPos.append(self.pos)
        self.historyPosCor.append(self.pos)
        self.historyTime.append(time)

        self.rtp.addPoint(self.pos.x, self.pos.y, "b")
        self.rtp.plot()

    def updateConfPos(self, position, time=None):
        self.rtp.addPoint(position.x, position.y, "r")
        self.rtp.plot()
        if (time is None):
            time = datetime.datetime.now()

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
        for position in self.historyPosCor:
            self.rtp.addPoint(position.x, position.y, "g")
        self.rtp.plot()


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
