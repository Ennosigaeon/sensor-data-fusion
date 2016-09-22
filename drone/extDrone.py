import time

import cv2

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
        self.useDemoMode(True)
        self.getNDpackage(["demo"])
        self.trim()
        self.setSpeed(0.05)

    def reset(self):
        """
        Calls ps_drone.Drone.reset() and waits for reset to complete.
        """
        super(Drone, self).reset()
        while self.getBattery()[0] == -1:
            time.sleep(0.1)
        print "Battery: " + str(self.getBattery()[0]) + "% " + str(self.getBattery()[1])

    def getNextDataSet(self):
        while self.NavDataCount == self.lastNDC: time.sleep(0.001)  # waiting for new datapoint
        self.lastNDC = self.NavDataCount
        return self.NavData

    # noinspection PyArgumentList
    def startCamera(self, fps):
        self.setConfigAllID()
        self.sdVideo()
        self.groundCam()
        self.videoFPS(fps)
        self.cap = cv2.VideoCapture('tcp://192.168.1.1:5555')

    def getNextVideoFrame(self):
        """
        Waits for the next video frame. If no camera is activated, None will be returned.
        :return: The next video frame as a numpy array
        """
        # Wait for next video frame
        if (self.cap is None):
            raise ValueError("Video stream not started yet")
        ret, frame = self.cap.read()
        return frame

    def frontCam(self, *args):
        """
        Calls ps_drone.Drone.frontCam(). Also sets data for toggleCam().
        :param args: Arguments for frontCam()
        """
        super(Drone, self).frontCam(*args)
        self.groundCamEnabled = False

    def groundCam(self, *args):
        """
        Calls ps_drone.Drone.groundCam(). Also sets data for toggleCam().
        :param args: Arguments for groundCam()
        """
        super(Drone, self).groundCam(*args)
        self.groundCamEnabled = True

    def toggleCamera(self):
        """
        Toggles the enabled camera.
        """
        self.groundCamEnabled = not self.groundCamEnabled
        if (self.groundCamEnabled):
            self.groundCam()
        else:
            self.frontCam()

    def failSafeStopDrone(self):
        self.stop()
        self.land()
        time.sleep(3)
        self.landed = True

    def simplePiloting(self, key):
        if (key is None):
            return

        if key == ' ':
            if self.landed:
                self.takeoff()
                while self.NavData["demo"][0][2]: time.sleep(0.1)
                print " drone is now in air"
                self.landed = False
            else:
                self.failSafeStopDrone()
                print " drone has landed"
        elif key == 'q':
            self.turnLeft()
            print " drone turns left"
        elif key == 'w':
            self.moveForward()
            print " drone flies forwards"
        elif key == 'e':
            self.turnRight()
            print " drone turns right"
        elif key == 'a':
            self.moveLeft()
            print " drone flies to the left"
        elif key == 's':
            self.moveBackward()
            print " drone flies backwards"
        elif key == 'd':
            self.moveRight()
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
            self.moveUp()
            print " drone moves up"
        elif key == 'j':
            self.moveDown()
            print " drone moves down"
        else:
            self.stop()
            print " drone stopped"

    def getSpeed(self, navData=None):
        """
        Returns the current velocity of the drone.
        :return: Array with three values for velocity in three directions.
        """
        if navData is None:
            return self.NavData["demo"][4]
        else:
            return navData["demo"][4]

    def getOrientation(self, navData=None):
        """
        Returns the current orientation of the drone.
        :return: Current orientation
        """
        # Add 180 to make 0 degree == north
        if navData is None:
            return self.NavData["demo"][2][2] + 180
        else:
            return navData["demo"][2][2] + 180
