#!/usr/bin/python
import time
import os
import subprocess

nl2 = os.path.normpath('"C:/Program Files/NoLimits 2/64bit/nolimits2app.exe" --telemetry')
print "starting NL2", nl2
subprocess.Popen(nl2)
print("Select coaster then position the ride control panel for reset (press F4)")
print("Pressing Reset on remote controller will show the mouse cursor reset location")
raw_input("Press any key to continue when ready")

effector = 'chairServer.py'
print "starting chair server:", effector
os.startfile(effector)
time.sleep(2)

middleware = 'java -jar middleware.jar'
subprocess.Popen(middleware)
print "starting middleware", middleware

nl2Client = 'CoasterClient.py'
print "starting client:", nl2Client
os.startfile(nl2Client)

# if remote runs on this machine, start remote controller
remoteController = 'RemoteController.py'
print "starting remote controller", remoteController
os.startfile(remoteController)

