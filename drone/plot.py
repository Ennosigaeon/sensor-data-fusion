import matplotlib.pyplot as plt


class RealTimePlot:
    def __init__(self):
        self.maxBorders = [4] * 2
        self.minBorders = [-4] * 2
        self.x = []
        self.y = []
        self.plt = plt.figure()
        self.ax = self.plt.add_subplot(111)

        self.ax.axis([self.minBorders[0], self.maxBorders[0], self.minBorders[1], self.maxBorders[1]])
        self.ax.hold(True)
        plt.show(False)
        plt.draw()

        self.background = self.plt.canvas.copy_from_bbox(self.ax.bbox)

    def drawPoint(self, x, y, color="b"):
        self.x.append(x)
        self.y.append(y)

        points = self.ax.plot(self.x, self.y, color)[0]
        self.plt.canvas.restore_region(self.background)
        self.ax.draw_artist(points)
        self.plt.canvas.blit(self.ax.bbox)

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
