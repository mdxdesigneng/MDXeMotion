# MDXeMotion emulation #
The files in this folder are the minimum required to create a working runtime of a simulated client and effector.  

Copy the files to a windows machine with python 2.7 and  the Java Runtime Environment (JRE) installed. 

Python is used for the emulators and as a script to get everything running.

JRE is required for the middleware.

To run the emulation execute startEmulation.py from the directory with the files copied above.

The startup script creates command windows for the following:
 * chair hardware emulator( named  festoEmulator.py)
 * chair server (named chairServer.py)
 * middleware (named middleware.jar)
 * client (named TestClient.py)

If everything starts up ok you will see values change in all the windows indicating the the chair is moving up a down repeatedly.

The middleware has a GUI that shows the commanded position of the six actuators. It also has sliders to control the gain.

The easiest way to create a new client is to replace TestClient.py with new client code that generates the six x,y,z, roll pitch and yaw values.  MdxPlatformItf.py handles the connections and creates the TCP messages that interact with the middleware. You can also create a client by generating the TCP messages directly.
Middleware.pdf in the docs folder describes the content of all the middleware messages. 
