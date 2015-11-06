#!/usr/bin/python
import time
import os
import subprocess

# start chair server if running on this computer
# otherwise, wait until chair server is running
#os.startfile("C:/Program Files/NoLimits 2/64bit/nolimits2app.exe --telemetry")
#os.startfile(os.path.normpath("C:/Program Files/NoLimits 2/64bit/nolimits2app.exe"))

effector = 'chairServer.py'
print "starting chair server:", effector
os.startfile(effector)
time.sleep(2)

middleware = 'java -jar middleware.jar'
subprocess.Popen(middleware)
print "starting middleware", middleware

nl2 = os.path.normpath('"C:/Program Files/NoLimits 2/64bit/nolimits2app.exe" --telemetry')
subprocess.Popen(nl2)
print "starting NL2", nl2
time.sleep(2)

nl2Client = 'CoasterClient.py'
print "starting client:", nl2Client
os.startfile(nl2Client)

# if remote runs on this machine, start remote controller
remoteController = 'RemoteController.py'
print "starting remote controller", remoteController
os.startfile(remoteController)

