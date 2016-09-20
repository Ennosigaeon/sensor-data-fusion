#!/usr/bin/env python

# TODO: test this code

import datetime
import math
import os
import sys
import time

import matplotlib.pyplot as plt

import extDrone
from map import Position


def createFolder(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


class DeadReckoning:
    def __init__(self, position):
        self.pos = position
        self.historyPos = [position]
        self.historyPosCor = [position]
        self.historyTime = [datetime.datetime.now()]
        
        self.historyConfirmed = []
        
        self.timeStart = datetime.datetime.now()
        self.lastTimestamp = datetime.datetime.now()
        self.phio = -180
        
    def setPhiToZero(self, drone):
        self.phio = drone.NavData["demo"][2][2]

    def updatePos(self, vx, vy, vz, phid):
        # adjusting expected speed
        # vx = navData["demo"][4][0]
        # vy = navData["demo"][4][1]
        # vz = navData["demo"][4][2]

        # adjusting angle (phid is in degree, phi is in radian)
        # phid = navData["demo"][2][2]
        phi = ((phid - self.phio) / 180) * math.pi

        # z = navData["demo"][3]

        # measuring total time and time since last datapoint
        time = datetime.datetime.now()
        deltaTime = (time - self.lastTimestamp).microseconds+1000000*(time - self.lastTimestamp).seconds
        self.lastTimestamp = time

        # calculating expected position
        self.pos = self.pos.updatePosition(vx, vy, phi, deltaTime)

        self.historyPos.append(self.pos)
        self.historyPosCor.append(self.pos)
        self.historyTime.append(time)
        
    def updateConfPos(self, x, y):
        time=datetime.datetime.now()
        self.pos = Position(x,y)
        self.historyPos.append(Position(x,y))
        self.historyPosCor.append(Position(x,y))
        self.historyTime.append(time)
        self.historyConfirmed.append(len(self.historyPos)-1)
        
        self.correctPos()
    
    def correctPos(self):
        if len(self.historyConfirmed)>1:
            deltaTimestamp = self.historyTime[self.historyConfirmed[-1]]-self.historyTime[self.historyConfirmed[-2]]
            deltaTotal = deltaTimestamp.microseconds + 1000000*deltaTimestamp.seconds
            deltaPosX = self.historyPos[self.historyConfirmed[-1]].x-self.historyPos[self.historyConfirmed[-1]-1].x
            deltaPosY = self.historyPos[self.historyConfirmed[-1]].y-self.historyPos[self.historyConfirmed[-1]-1].y
            
            for i in range(self.historyConfirmed[-2], self.historyConfirmed[-1]):
                deltaTimestamp = self.historyTime[i]-self.historyTime[self.historyConfirmed[-2]]
                deltaTime = deltaTimestamp.microseconds + 1000000*deltaTimestamp.seconds
                fracTime = 1.0 * deltaTime / deltaTotal
                self.historyPosCor[i].x = self.historyPos[i].x+fracTime*deltaPosX
                self.historyPosCor[i].y = self.historyPos[i].y+fracTime*deltaPosY
        else:
            deltaPosX = self.historyPos[self.historyConfirmed[-1]].x-self.historyPos[self.historyConfirmed[-1]-1].x
            deltaPosY = self.historyPos[self.historyConfirmed[-1]].y-self.historyPos[self.historyConfirmed[-1]-1].y
            
            for i in range(0, self.historyConfirmed[-1]):
                self.historyPosCor[i].x = self.historyPos[i].x+deltaPosX
                self.historyPosCor[i].y = self.historyPos[i].y+deltaPosY
        

    # TODO implement
    def storeRaw(self, file):
        pass

    def loadRaw(self):
        pass

    # noinspection PyMethodMayBeStatic
    def initRTPlot(self):
        plt.axis([-4, 4, -4, 4])
        plt.ion()
        plt.pause(0.05)

    def updateRTPlot(self):
        # plot new datapoint
        # TODO better plotting algorithm
        plt.plot([self.historyPos[-2].x, self.pos.x], [self.historyPos[-2].y, self.pos.y])
        plt.pause(0.05)


if (__name__ == "__main__"):
    drone = extDrone.Drone()
    drone.startup()
    DR = DeadReckoning()
    DR.setPhiToZero(drone)
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
            if (key == '1'):
                pass
        else:
            time.sleep(0.01)
