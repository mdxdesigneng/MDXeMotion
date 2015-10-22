Platform Middleware (a component of the Middlesex 6DOF platform)

This module receives API positional commands that are processed for sending to a stewart platform such as the Middlesex Chair

The middleware consists of the following elements:
   PlatformMiddleware.java - initializes and finalized all other modules. Dispatches incoming commands from PlatformAPI
   to the PlatformTransform module and sends the transformed output data to the effectorInterface.   

   PlatformApi.java - receives json positional commands and optional commands to configure gain and washout.
   
   PlatformTransform.java - converts between rotation/translation requests and raw actuator distances
   
   EffectorInterface.jave - forms json output messages sent to the platform 
   
   SingleWatcher.java - thread run in the effectorInterface class to support passive listeners to the output data
   
  


