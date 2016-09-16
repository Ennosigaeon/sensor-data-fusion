import time

import ps_drone


class Drone(ps_drone.Drone):
    """
    This class extends ps_drone.Drone and adds some convenience methods.
    """

    def __init__(self):
        super(Drone, self).__init__()
        self.groundCamEnabled = True
        self.lastIMC = self.VideoImageCount

    def reset(self):
        """
        Calls ps_drone.Drone.reset() and waits for reset to complete.
        """
        super(Drone, self).reset()
        while self.getBattery()[0] == -1:
            time.sleep(0.1)
        print "Battery: " + str(self.getBattery()[0]) + "% " + str(self.getBattery()[1])

    def getNextVideoFrame(self):
        """
        Waits for the next video frame. If no camera is activated, None will be returned.
        :return: The next video frame as a numpy array
        """
        # TODO check if VideoReady really means that one camera is active
        if (not self.VideoReady):
            return None
        # Wait for next video frame
        while self.lastIMC == self.VideoImageCount:
            time.sleep(0.01)
        return self.VideoImage

    def frontCam(self, *args):
        """
        Calls ps_drone.Drone.frontCam(). Also sets data for toggleCam().
        :param args: Arguments for frontCam()
        """
        super(Drone, self).frontCam(args)
        self.groundCamEnabled = False

    def groundCam(self, *args):
        """
        Calls ps_drone.Drone.groundCam(). Also sets data for toggleCam().
        :param args: Arguments for groundCam()
        """
        super(Drone, self).groundCam(args)
        self.groundCamEnabled = True

    def toggleCamera(self):
        """
        Toggles the enabled camera.
        """
        self.groundCamEnabled = not self.groundCamEnabled
        self.groundCam(self.groundCamEnabled)
