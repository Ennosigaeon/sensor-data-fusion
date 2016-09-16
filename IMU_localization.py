#!/usr/bin/env python

#TODO: test this code

import time, sys, math
import ps_drone
import datetime
import matplotlib.pyplot as plt

#Drone start
drone = ps_drone.Drone()
drone.startup()

drone.reset()                                      # Sets drone's status to good
while (drone.getBattery()[0]==-1): time.sleep(0.1) # Wait until drone has done its reset
print "Battery: "+str(drone.getBattery()[0])+"% "+str(drone.getBattery()[1]) # Battery-status
drone.useDemoMode(True)                            # Set 15 basic dataset/sec (default anyway)
drone.getNDpackage(["demo"])                       # Packets, which shall be decoded
time.sleep(0.5) 

drone.trim()

#current position of the drone
#TODO implement z
x = 0
y = 0
z = 0

#former positions used for plotting
old_x = 0
old_y = 0

#starttime used for raw-data
time_start = datetime.datetime.now()

#variable for measuring the time between two datapoints
time_old = datetime.datetime.now()

#plot_file is an executable file plotting the calculated x and y values
#raw_file stores all gathered data from the drone as well as the corresponding timestamps
plot_file = open("plotdata.py", "w")
plot_file.write("#!/usr/bin/env python\n\n")
plot_file.write("import matplotlib.pyplot as plt\n")
plot_file.write("x=[];y=[];")
raw_file = open("rawdata.txt", "w")

#set phi-offset
print "phi:"+str(drone.NavData["demo"][2][2])
phio = float(raw_input('offset: '))

NDC = drone.NavDataCount

#for real-time tracking
plt.axis([-2000,2000,-2000,2000])
plt.ion()

while (1):
  while drone.NavDataCount==NDC: time.sleep(0.001) #waiting for new datapoint
  
  #adjusting expected speed
  vx=drone.NavData["demo"][4][0]
  vy=drone.NavData["demo"][4][1]
  vz=drone.NavData["demo"][4][2]
  #adjusting angle (phid is in degree, phi is in radian)
  phid=drone.NavData["demo"][2][2]
  phi=((phid-phio)/180)*math.pi
  
  #measuring total time and time since last datapoint
  time_new = datetime.datetime.now()
  time_diff = (time_new-time_old).microseconds
  time_total = (time_new-time_start).microseconds
  time_old = time_new
  
  raw_file.write("(time:{0};vx:{1};vy:{2};vz:{3};phi:{4})\n".format(time_total, vx, vy, vz, phid))
  
  #TODO check geometry
  #x+=(math.cos(phi)*vx+math.sin(phi)*vy)*time_diff/1000000
  #y+=(math.cos(phi)*vy-math.sin(phi)*vx)*time_diff/1000000
  
  #calculating expected position
  x+=(vx)*time_diff/1000000
  y+=(vy)*time_diff/1000000
  
  plot_file.write("x+=[{0}];y+=[{0}];\n".format(x, y))
  
  #plot new datapoint
  #TODO better plotting algorithm
  plt.plot([old_x, x],[old_y, y])
  plt.pause(0.05)
  old_x = x
  old_y = y
  
  #end if key is pressed
  if drone.getKey():
    plot_file.write("plt.plot(x,y);\n")
    plot_file.write("plt.show();")
    plot_file.close()
    plt.pause(5)
    sys.exit()
  NDC = drone.NavDataCount
