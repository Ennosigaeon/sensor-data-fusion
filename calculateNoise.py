import numpy as np


def readValues(filename, column):
    res = []
    with open(filename) as file:
        lines = file.readlines()
        for line in lines:
            tokens = line.split(" ")
            res.append(float(tokens[column]))
    return np.array(res)


values = readValues("../Contrib/sensor_noise", 0)
high = np.where(values > 180)
values[high] -= 360
print values
print "N({}, {})".format(values.mean(), values.var())

values = readValues("../Contrib/sensor_noise", 1)
print "N({}, {})".format(values.mean(), values.var())

values = readValues("../Contrib/sensor_noise", 2)
print "N({}, {})".format(values.mean(), values.var())
