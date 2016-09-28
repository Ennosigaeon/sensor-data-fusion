import numpy as np


class KalmanFilter:
    def __init__(self):
        # noise terms v -> measurement cov, w -> process covariance
        self.v = np.matrix([[0.5, 0], [0, 0.5]])
        self.w = np.matrix([[0.09, 0], [0, 0.08]])

        # state and state covariance
        self.x = np.matrix([[0], [0], [0]])
        self.P = np.matrix([[1, 0], [0, 1]])

        # process matrix A and measurement matrix H
        self.A = np.matrix([[1, 0], [0, 1]])
        self.H = np.matrix([[1, 0], [0, 1]])

    # filter functions, altered to accept already calculated position
    def predict(self, position):
        x = np.array([position.x, position.y])
        self.x = np.matrix([x])
        self.P = self.A * self.P * self.A.T + self.w

        position.x = self.x[0, 0]
        position.y = self.x[0, 1]
        return (position, self.P)

    # standard Kalman filter update
    def update(self, position):
        y = np.matrix([position.x, position.y])

        K_gain = self.P * self.H.T * np.linalg.inv(self.H * self.P * self.H.T + self.v)
        self.x = (self.x.T + K_gain * (y.T - self.H * self.x.T)).T
        self.P = self.P - K_gain * (self.H * self.P)

        print "({}, {}) -> ({}, {})".format(position.x, position.y, self.x[0, 0], self.x[0, 1])
        position.x = self.x[0, 0]
        position.y = self.x[0, 1]
        return (position, self.P)
