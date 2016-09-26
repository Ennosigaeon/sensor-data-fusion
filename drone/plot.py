import matplotlib.pyplot as plt


class RealTimePlot:
    def __init__(self):
        self.maxBorders = [2] * 2
        self.minBorders = [-2] * 2
        self.x = {'b': [], 'r': [], 'g': []}
        self.y = {'b': [], 'r': [], 'g': []}
        self.plt = plt.figure()
        self.ax = self.plt.add_subplot(111)

        self.ax.axis([self.minBorders[0], self.maxBorders[0], self.minBorders[1], self.maxBorders[1]])
        self.ax.hold(True)
        plt.show(False)
        plt.draw()

        self.background = self.plt.canvas.copy_from_bbox(self.ax.bbox)

    def addPoint(self, x, y, color="b"):
        if (color == 'r'):
            self.x[color].append([self.x['b'][-1], x])
            self.y[color].append([self.y['b'][-1], y])
            self.x['b'].append(x)
            self.y['b'].append(y)
        else:
            self.x[color].append(x)
            self.y[color].append(y)
        self._updateBorders(x, y)

    def plot(self):
        self.plt.canvas.restore_region(self.background)
        self.ax.draw_artist(self.ax.plot(self.x['b'], self.y['b'], 'b')[0])
        for i in range(len(self.x['r'])):
            self.ax.draw_artist(self.ax.plot(self.x['r'][i], self.y['r'][i], 'r')[0])
        self.ax.draw_artist(self.ax.plot(self.x['g'], self.y['g'], 'g')[0])
        self.plt.canvas.blit(self.ax.bbox)

    def _updateBorders(self, x, y):
        if ((self.minBorders[0] <= x <= self.maxBorders[0]) and
                (self.minBorders[1] <= y <= self.maxBorders[1])):
            return

        self.minBorders[0] = min(x, self.minBorders[0])
        self.minBorders[1] = min(y, self.minBorders[1])
        self.maxBorders[0] = max(x, self.maxBorders[0])
        self.maxBorders[1] = max(y, self.maxBorders[1])
        if (self.minBorders[0] == self.maxBorders[0]):
            self.maxBorders[0] += 1
        if (self.minBorders[1] == self.maxBorders[1]):
            self.maxBorders[1] += 1

        self.ax.set_xlim([self.minBorders[0] - 0.1, self.maxBorders[0] + 0.1])
        self.ax.set_ylim([self.minBorders[1] - 0.1, self.maxBorders[1] + 0.1])
