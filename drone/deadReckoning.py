#!/usr/bin/env python
import datetime
import math
import os
import sys
from time import sleep

import matplotlib.pyplot as plt

from drone.kalman import KalmanFilter
from extDrone import Drone
from map import Position
from plot import RealTimePlot


def createFolder(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


class DeadReckoning:
    def __init__(self, position, time=None):
        self.pos = position
        self.rawPos = position
        self.historyRaw = [position]
        self.historyPos = [position]
        self.historyTime = [datetime.datetime.now()]
        self.historyConfirmed = []
        self.timeStart = datetime.datetime.now()
        if (time is None):
            time = datetime.datetime.now()
        self.lastTimestamp = time
        self.phio = 0
        self.rtp = RealTimePlot()
        self.rtp.addPoint(self.pos.x, self.pos.y, "b")

        self.kalmanFilter = KalmanFilter()
        self.kalmanFilter.predict(self.pos)

        self.rawKalmanFilter = KalmanFilter()
        self.rawKalmanFilter.predict(self.rawPos)

    def setPhiToZero(self, drone):
        self.phio = drone.navData["demo"][2][2]

    def setPhioToValue(self, phi):
        print "Setting phio to {}".format(phi)
        self.phio = phi

    def updatePos(self, speed, phid, time=None):
        if (not time):
            print "{} {} {} {}".format(phid, (phid - self.phio) % 360, speed[0], speed[1])

        # adjusting angle (phid is in degree, phi is in radian)
        phi = (((phid - self.phio) % 360) / 180) * math.pi

        # measuring total time and time since last datapoint
        if (time is None):
            time = datetime.datetime.now()
        deltaTime = (time - self.lastTimestamp).total_seconds()
        self.lastTimestamp = time

        # calculating expected position
        currentPos = self.pos.updatePosition(speed[0], speed[1], phi, deltaTime)
        self.pos, cov = self.kalmanFilter.predict(currentPos)

        self.historyPos.append(self.pos)
        self.historyTime.append(time)

        currentRawPos = self.rawPos.updatePosition(speed[0], speed[1], phi, deltaTime)
        self.rawPos, cov = self.rawKalmanFilter.predict(currentRawPos)
        self.historyRaw.append(self.rawPos)

        self.rtp.addPoint(self.pos.x, self.pos.y, "b")
        self.rtp.plot()

    def updateConfPos(self, position, time=None):
        position, cov = self.kalmanFilter.update(position)

        self.rtp.addPoint(position.x, position.y, "r")
        self.rtp.plot()
        if (time is None):
            time = datetime.datetime.now()

        self.pos = position
        self.historyPos.append(position)
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
                self.historyPos[i].x += fracTime * deltaPosX
                self.historyPos[i].y += fracTime * deltaPosY
        else:
            deltaPosX = self.historyPos[self.historyConfirmed[-1]].x - self.historyPos[self.historyConfirmed[-1] - 1].x
            deltaPosY = self.historyPos[self.historyConfirmed[-1]].y - self.historyPos[self.historyConfirmed[-1] - 1].y

            for i in range(0, self.historyConfirmed[-1]):
                self.historyPos[i].x += deltaPosX
                self.historyPos[i].y += deltaPosY

    def drawCorrectedPath(self):
        rtp = RealTimePlot()
        for position in self.historyRaw:
            rtp.addPoint(position.x, position.y, "b")
        for position in self.historyPos:
            rtp.addPoint(position.x, position.y, "g")
        rtp.plot(labelB="Dead Reckoning", labelG="Corrected path")
        return rtp


if (__name__ == "__main__"):
    drone = Drone()
    drone.startup()
    drone.reset()
    drone.defaultInit()

    DR = DeadReckoning(Position(0, 0))
    DR.setPhiToZero(drone.getOrientation())

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
