#!/usr/bin/python


import sys,signal,os
import time
import math

import IMU
import datetime


def handle_ctrl_c(signal, frame):
    print(" ")
    print("magXmin = %i"%  (magXmin))
    print("magYmin = %i"%  (magYmin))
    print("magZmin = %i"%  (magZmin))
    print("magXmax = %i"%  (magXmax))
    print("magYmax = %i"%  (magYmax))
    print("magZmax = %i"%  (magZmax))
    sys.exit(130) # 130 is standard exit code for ctrl-c



IMU.detectIMU()
IMU.initIMU()

#This will capture exit when using Ctrl-C
signal.signal(signal.SIGINT, handle_ctrl_c)


a = datetime.datetime.now()


#Preload the variables used to keep track of the minimum and maximum values
magXmin = 32767
magYmin = 32767
magZmin = 32767
magXmax = -32767
magYmax = -32767
magZmax = -32767



while True:

    #Read magnetometer values
    MAGx = IMU.readMAGx()
    MAGy = IMU.readMAGy()
    MAGz = IMU.readMAGz()

    if MAGx > magXmax:
        magXmax = MAGx
    if MAGy > magYmax:
        magYmax = MAGy
    if MAGz > magZmax:
        magZmax = MAGz

    if MAGx < magXmin:
        magXmin = MAGx
    if MAGy < magYmin:
        magYmin = MAGy
    if MAGz < magZmin:
        magZmin = MAGz

    print((" magXmin  %i  magYmin  %i  magZmin  %i  ## magXmax  %i  magYmax  %i  magZmax %i  " %(magXmin,magYmin,magZmin,magXmax,magYmax,magZmax)))



    #slow program down a bit, makes the output more readable
    time.sleep(0.03)


