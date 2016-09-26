import datetime
import math

import numpy as np
from numpy.linalg import inv

# After testing the normal Kalman filter, I think, that we don't want a Kalman filter for the fusion of the deadReckoning and the marker detection.
# Issue 1:
# marker detection is not normal distributed. If the library only detects markers on the screen, the error is limited by some small number and therefore not normal distributed.
# In the other case there is a nonzero probability to detect a wrong marker, which is not dependent on the distance to the marker.
# Issue 2 using the notation of https://en.wikipedia.org/wiki/Kalman_filter#Overview_of_the_calculation:
# The predictions of the Kalman filter are not dependent on the accuracy of the prior prediction, but just on the number of prior predictions and updates (and time of the predictions since F is time-dependent)
# We want for our used filter, that atleast F is adjusted if our predictions are wrong.
# Issue 3:
# In most cases we have a long time between the updates. This means that the Kalman Filter ignores the predicted position almost completely and just uses the marker detection. The current code does exactly the same thing.

# The part where a Kalman filter is actual useful (getting vx,vy from gyroscope and accelerometer) is probably already implemented using a kalman filter. Another filter probably won't make the results better.


# if the filter does not work as predicted change self.R
# (use smaller values for R if marker detection should be weighted heigher)

class KalmanFilter:
    def __init__(self):
        #[x, y, vx, vy] vx, vy in m/s
        self.x = np.matrix([[1.0], [2.0], [3.0], [4.0]])
        #initialized with high values
        #converges to right values
        self.P = 1000000*np.identity(4)
        #only the position is measured
        self.H = np.matrix([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]])
        self.R = np.matrix([[1.0, 0.0], [0.0, 1.0]])
        
    
    #INPUT vx, vy in mm/s; phi in radian; deltaTime in seconds (float)
    def predict(self, vx, vy, phi, deltaTime):
        #create state transition model based on time
        F = np.matrix([[1.0,0.0,math.cos(phi)*deltaTime,-math.sin(phi)*deltaTime],
            [0.0,1.0,math.sin(phi)*deltaTime,math.cos(phi)*deltaTime],
            [0.0,0.0,1.0,0.0],
            [0.0,0.0,0.0,1.0]])
        #create covariance matrix of the process noise based on time
        #see: http://www.cbcity.de/das-kalman-filter-einfach-erklaert-teil-2
        G = np.matrix([0.5*deltaTime*deltaTime, 0.5*deltaTime*deltaTime, deltaTime, deltaTime]).transpose()
        self.Q = G.dot(G.transpose())*8
        #adjust speed
        self.x[2] = vx/1000
        self.x[3] = vy/1000
        #predict state
        self.x = F.dot(self.x)
        #predict covariance matrix
        self.P = F.dot(self.P.dot(F.transpose())) + self.Q
        
    def update(self, px, py):
        #innovation
        y = np.matrix([[px], [py]]) - self.H.dot(self.x)
        #residual covariance
        S = self.H.dot(self.P.dot(self.H.transpose()))+self.R
        #Kalman gain
        K = self.P.dot(self.H.transpose().dot(inv(S)))
        #update position
        self.x = self.x + K.dot(y)
        #update covariance matrix
        self.P = (np.identity(4)-K.dot(self.H)).dot(self.P)
        
        

        
        
        
        
if (__name__ == "__main__"):
    pass:
