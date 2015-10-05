Platform API

Methods comprise :
    Config Method: (each of the following arguments is optional)
       "blocking"       true/false – defaults to false (current version only supports false)                           

       "gainX"      float multiplier for x values
       "gainY"      float multiplier for y values
       "gainZ"      float multiplier for z values
       "gainRoll"   float multiplier for roll values
       "gainPitch"  float multiplier for pitch values
       "gainYaw"    float multiplier for yaw values
       "gain"       float multiplier for all values
         - all above gain factors default to 1.0

       "washoutX"      washout factor for x values
       "washoutY"      washout factor for y values
       "washoutZ"      washout factor for z values
       "washoutRoll"   washout factor for roll values
       "washoutPitch"  washout factor for pitch values
       "washoutYaw"    washout factor for yaw values
        - all above washout factors default to 1.0, lower numbers increase washout

        (configuration of movement rate control is not supported in initial release)

    Movement methods:
      Method identifier:
        "raw"  - array of raw values for each of six arms
        "xyzrpy" – array of six values for xyz translations and rotations
            x translation is forward/backward movement (surge)
            y translation is side to side movement (sway)
            z translation is up/down movement (heave)
            x rotation is tilting on front/back axis (roll)
            y rotation is tilting on lateral axis (pitch)
            z rotation is tilting on vertical axis (yaw)
                
         Units identifier:
        "real"  use real world mm values for translation, degrees for rotation
         (not implemented in initial release ?)       
        Default is range of normalized movement expressed as values from -1 to 1

              args:
            An array of six floating point values

      JSON RPC message id is optional and ignored in the initial release     

Translation/Rotation example:
{"jsonrpc":"2.0","method":"xyzrpy","args":[0, 0, 0, 0, 0, 0]}
 
Raw Interface Example:
{"jsonrpc":"2.0","method":"raw","units":"real","args":[0, 0, 0, 0, 0, 0],"id":null} 

