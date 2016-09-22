import matplotlib.pyplot as plt


class RealTimePlot:
    def __init__(self):
        self.maxBorders = [4] * 2
        self.minBorders = [-4] * 2
        self.plt = plt.figure()
        self.ax = self.plt.add_subplot(111)

        self.ax.axis([self.minBorders[0], self.maxBorders[0], self.minBorders[1], self.maxBorders[1]])
        self.ax.hold(True)
        plt.show(False)
        plt.draw()

    def drawLine(self, point1, point2, color="b"):
        self.ax.plot([point1[0], point2[0]], [point1[1], point2[1]], color=color)
        self.updateBorders(point1, point2)
        self.plt.canvas.draw()

    def updateBorders(self, point1, point2):
        if (all((self.minBorders[0] <= point1[0], point2[0] <= self.maxBorders[0])) and
                all((self.minBorders[1] <= point1[1], point2[1] <= self.maxBorders[1]))):
            return

        self.minBorders[0] = min(point1[0], point2[0], self.minBorders[0])
        self.minBorders[1] = min(point1[1], point2[1], self.minBorders[1])
        self.maxBorders[0] = max(point1[0], point2[0], self.maxBorders[0])
        self.maxBorders[1] = max(point1[1], point2[1], self.maxBorders[1])
        if (self.minBorders[0] == self.maxBorders[0]):
            self.maxBorders[0] += 1
        if (self.minBorders[1] == self.maxBorders[1]):
            self.maxBorders[1] += 1

        self.ax.set_xlim([self.minBorders[0] - 0.1, self.maxBorders[0] + 0.1])
        self.ax.set_ylim([self.minBorders[1] - 0.1, self.maxBorders[1] + 0.1])
