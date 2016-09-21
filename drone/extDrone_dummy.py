import time

#TODO: resolve: "No module named cv2"
#import cv2

import ps_drone


class Drone(ps_drone.Drone):
    """
    This class extends ps_drone.Drone and adds some convenience methods.
    """

    def __init__(self):
        super(Drone, self).__init__()
        self.groundCamEnabled = True
        self.lastIMC = self.VideoImageCount
        self.lastNDC = self.NavDataCount
        self.landed = True
        self.cap = None

    def defaultInit(self):
        """
        Extended startup procedure.
        """
        print "use Demo mode"
        print "get demo package"
        print "wait half a second"
        time.sleep(0.5)
        print "calibrate sensors"
        print "wait one second"
        time.sleep(1)
        print "set speed to 0.05"

    def reset(self):
        """
        Calls ps_drone.Drone.reset() and waits for reset to complete.
        """
        super(Drone, self).reset()
        while self.getBattery()[0] == -1:
            time.sleep(0.1)
        print "Battery: " + str(self.getBattery()[0]) + "% " + str(self.getBattery()[1])

    def getNextDataSet(self):
        print "get next Data set (None)"
        return None

    # noinspection PyArgumentList
    def startCamera(self, fps):
        print "startCamera"

    def getNextVideoFrame(self):
        """
        Waits for the next video frame. If no camera is activated, None will be returned.
        :return: The next video frame as a numpy array
        """
        print "getNextVideoFrame"
        return None

    def frontCam(self, *args):
        """
        Calls ps_drone.Drone.frontCam(). Also sets data for toggleCam().
        :param args: Arguments for frontCam()
        """
        print "frontCam"

    def groundCam(self, *args):
        """
        Calls ps_drone.Drone.groundCam(). Also sets data for toggleCam().
        :param args: Arguments for groundCam()
        """
        print "groundCam"

    def toggleCamera(self):
        """
        Toggles the enabled camera.
        """
        print "toggleCamera"

    def failSafeStopDrone(self):
        print "failSafeStopDrone"

    def simplePiloting(self, key):
        if (key is None):
            return

        if key == ' ':
            if self.landed:
                print " drone is now in air"
                self.landed = False
            else:
                self.failSafeStopDrone()
                print " drone has landed"
        elif key == 'q':
            print " drone turns left"
        elif key == 'w':
            print " drone flies forwards"
        elif key == 'e':
            print " drone turns right"
        elif key == 'a':
            print " drone flies to the left"
        elif key == 's':
            print " drone flies backwards"
        elif key == 'd':
            print " drone flies to the right"
        elif key == '+':
            self.__speed = min(1, self.__speed + 0.01)
            self.setSpeed(self.__speed)
            print " drone speed is now " + str(self.__speed)
        elif key == '-':
            self.__speed = max(0, self.__speed - 0.01)
            self.setSpeed(self.__speed)
            print " drone speed is now " + str(self.__speed)
        elif key == 'u':
            print " drone moves up"
        elif key == 'j':
            print " drone moves down"
        else:
            print " drone stopped"

    def getSpeed(self, navData = None):
        """
        Returns the current velocity of the drone.
        :return: Array with three values for velocity in three directions.
        """
        if navData == None:
            print "return speed vector from drone navData"
            vx = float(raw_input('vx: '))
            vy = float(raw_input('vy: '))
            vz = float(raw_input('vz: '))
            return (vx, vy, vz)
        else:
            print "return speed vector from passed navData"
            return navData["demo"][4]

    def getOrientation(self, navData = None):
        """
        Returns the current orientation of the drone.
        :return: Current orientation
        """
        # Add 180 to make 0 degree == north
        if navData == None:
            print "return orientation from drone navData"
            phi = float(raw_input('phi: '))
            return phi + 180
        else:
            print "return orientation from passed navData"
            return navData["demo"][2][2] + 180
