#!/usr/bin/python
import time
import os
import subprocess

# start chair server if running on this computer
# otherwise, wait until chair server is running
#os.startfile("C:/Program Files/NoLimits 2/64bit/nolimits2app.exe --telemetry")
#os.startfile(os.path.normpath("C:/Program Files/NoLimits 2/64bit/nolimits2app.exe"))
effector = os.path.normpath("PlatformSim.exe")
print "starting chair server:", effector
#####os.startfile(effector)
#####time.sleep(6)

middleware = "java -jar PlatformMiddleware/Java/export/middleware.jar"
subprocess.Popen(middleware)
print "starting moddleware", middleware

localController = os.path.normpath("clients/RemoteController/LocalController.py")
print "starting local controller", localController
os.startfile(localController)

nl2 = os.path.normpath('"C:/Program Files/NoLimits 2/64bit/nolimits2app.exe" --telemetry')
#os.startfile(nl2 )
subprocess.Popen(nl2)
print "starting NL2", nl2
time.sleep(4)

nl2Client = os.path.normpath("clients/CoasterClient/CoasterClient.py")
#nl2Client = os.path.normpath('python "clients/CoasterClient/CoasterClient.py"')
print "starting client:", nl2Client
os.startfile(nl2Client)
#subprocess.Popen(nl2Client)

# if remote runs on this machine, start remote controller
remoteController = os.path.normpath("clients/RemoteController/RemoteController.py")
print "starting remote controller", remoteController
os.startfile(remoteController)

