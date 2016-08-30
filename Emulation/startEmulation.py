#!/usr/bin/python
import time
import os
import subprocess

chairEmulator = 'festoEmulator.py'
print "starting chair emulator:", chairEmulator
os.startfile(chairEmulator)
time.sleep(2)

effector = 'chairServer.py'
print "starting chair server:", effector
os.startfile(effector)
time.sleep(2)

middleware = 'java -jar middleware.jar'
subprocess.Popen(middleware)
print "starting middleware", middleware

client = os.path.normpath('TestClient.py')
print "starting client: ", client
os.startfile(client)

