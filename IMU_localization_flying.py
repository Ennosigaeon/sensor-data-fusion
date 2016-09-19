#!/usr/bin/env python

#TODO: test this code

import time, sys, math
import extDrone
import datetime
import matplotlib.pyplot as plt
import os

def createFolder(path):
  try: 
    os.makedirs(path)
  except OSError:
    if not os.path.isdir(path):
      raise

class DeadReckoning:
  def __init__(self, drone):
    self.x = 0
    self.y = 0
    self.z = 0
    self.lastX = 0
    self.lastY = 0
    self.timeStart = datetime.datetime.now()
    self.lastTimestamp = datetime.datetime.now()
    self.phio = drone.NavData["demo"][2][2]
    
  def updatePos(self, navData):
    #adjusting expected speed
    vx=drone.NavData["demo"][4][0]
    vy=drone.NavData["demo"][4][1]
    vz=drone.NavData["demo"][4][2]
    
    #adjusting angle (phid is in degree, phi is in radian)
    phid=drone.NavData["demo"][2][2]
    phi=((phid-self.phio)/180)*math.pi
  
    z=drone.NavData["demo"][3]
    
    #measuring total time and time since last datapoint
    time = datetime.datetime.now()
    diff = (time-self.lastTimestamp).microseconds
    total = (time-self.timeStart).microseconds
    self.lastTimestamp = time
    
    #calculating expected position
    self.x+=(math.cos(phi)*vx-math.sin(phi)*vy)*diff/1000000
    self.y-=(math.cos(phi)*vy+math.sin(phi)*vx)*diff/1000000
    
    #plot new datapoint
    #TODO better plotting algorithm
    plt.plot([self.lastX, self.x],[self.lastY, self.y])
    plt.pause(0.05)
    self.lastX = self.x
    self.lastY = self.y
    
    
  def initOutputFiles(self):
    createFolder("./data")
    
    #plot_file is an executable file plotting the calculated x and y values
    #raw_file stores all gathered data from the drone as well as the corresponding timestamps
    minfree=1;
    while os.path.lexists("./data/plotdata"+str(minfree)+".py"): minfree+=1
    while os.path.lexists("./data/rawdata"+str(minfree)+".txt"): minfree+=1
    plot_file = open("./data/plotdata"+str(minfree)+".py", "w")
    raw_file = open("./data/rawdata"+str(minfree)+".txt", "w")
    
    print "Create output file: ./data/plotdata"+str(minfree)+".py"
    print "Create output file: ./data/rawdata"+str(minfree)+".txt"
    
    plot_file.write("#!/usr/bin/env python\n\n")
    plot_file.write("import matplotlib.pyplot as plt\n")
    plot_file.write("x=[];y=[];")
    return (plot_file, raw_file)
    
  def initRTPlot(self):
    plt.axis([-4000,4000,-4000,4000])
    plt.ion()
    
    

def extendedStart():
  #drone start routine
  drone = extDrone.Drone()
  drone.startup()
  drone.reset()
  drone.useDemoMode(True)
  drone.getNDpackage(["demo"])
  time.sleep(0.5) 
  drone.trim()
  time.sleep(1) 
  speed = 0.05
  drone.setSpeed(speed)
  return drone
  
if (__name__ == "__main__"):
  drone = extendedStart()
  DR = DeadReckoning(drone)
  plot_file, raw_file = DR.initOutputFiles()
  DR.initRTPlot()
   

  landed = True
  speed = 0.05

  while(1):
    navData = drone.getNextDataSet()
    
    DR.updatePos(navData)

    key = drone.getKey()
    if key:
      if key == ' ':
        if landed:
          drone.takeoff()
          while drone.NavData["demo"][0][2]: time.sleep(0.1)
          print " drone is now in air"
          landed = False
        else:
          drone.stop()
          drone.land()
          time.sleep(3)
          print " drone has landed"
          landed = True
      elif key == 'q':
        drone.turnLeft()
        print " drone turns left"
      elif key == 'w':
        drone.moveForward()
        print " drone flies forwards"
      elif key == 'e':
        drone.turnRight()
        print " drone turns right"
      elif key == 'a':
        drone.moveLeft()
        print " drone flies to the left"
      elif key == 's':
        drone.moveBackward()
        print " drone flies backwards"
      elif key == 'd':
        drone.moveRight()
        print " drone flies to the right"
      elif key == '0':
        print " end program"
        drone.stop()
        drone.land()
        time.sleep(3)
        print "  drone has landed"
        plot_file.write("plt.plot(x,y);\n")
        plot_file.write("plt.show();")
        plot_file.close()
        raw_file.close()
        plt.pause(5)
        sys.exit()
      elif key == '+':
        if speed<=0.99: speed+=0.01
        drone.setSpeed(speed)
        print " drone speed is now "+str(speed)
      elif key == '-':
        if speed>0.01: speed-=0.01
        drone.setSpeed(speed)
        print " drone speed is now "+str(speed)
      elif key == 'u':
        drone.moveUp(speed)
        print " drone moves up"
      elif key == 'j':
        drone.moveDown(speed)
        print " drone moves down"
      else:
        drone.stop()
        print " drone stopped"
    else:
      time.sleep(0.01)
  
  
  

  





