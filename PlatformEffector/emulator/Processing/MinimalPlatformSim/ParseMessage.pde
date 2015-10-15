   public static class msgFields
   {
      float x;
      float y;
      float z;
      float roll;
      float pitch;
      float yaw;
   }



public class ParseMessage 
{

  public class config 
  {
    float gainX  = 1.0;      //  factor for x values
    float gainY  = 1.0;      //  factor for y values
    float gainZ  = 1.0;      //  factor for z values
    float gainRoll  = 1.0;   //  factor for roll values
    float gainPitch  = 1.0;  //  factor for pitch values
    float gainYaw  = 1.0;    //  factor for yaw values
    float gain  = 1.0;       //  factor for all values


    float washoutX  = 1.0;     // washout factor for x values
    float washoutY  = 1.0;     // washout factor for y values
    float washoutZ  = 1.0;     // washout factor for z values
    float washoutRoll  = 1.0;  // washout factor for roll values
    float washoutPitch  = 1.0; // washout factor for pitch values
    float washoutYaw  = 1.0;   // washout factor for yaw values
  }
  
  private msgFields parseXyzrph(boolean isRealUnits, JSONArray values) 
  {
    //print(" parseXyzrph "); println( values);
    if (isRealUnits == false) {  // for now, only add if normalized - todo
      msgFields msg = new msgFields();
      msg.x     = (float)values.getDouble(0);
      msg.y     = (float)values.getDouble(1);
      msg.z     = (float)values.getDouble(2);
      msg.roll  = (float)values.getDouble(3);
      msg.pitch = (float)values.getDouble(4);
      msg.yaw   = (float)values.getDouble(5);
      return msg;     
     // msgQueue.add(msg);   
   
    } 
    return null;  
  } 
  
  private float [] parseRaw( JSONArray values) 
  {  
      float [] msg = new float[6];
      for(int i=0; i < 6; i++)
          msg[i] = (float)values.getDouble(i);
      println( msg);
      return msg; 
      
  } 


  public boolean isGeometryRequest(String msg)
  {    
    JSONObject json1 = JSONObject.parse(msg);   
    return json1.getString("method").equals("geometry") ; 
  }

  public float [] parseMsg(String msg)  
  {  
    JSONObject json1 = JSONObject.parse(msg);   
    if ( json1.getString("method").equals("moveEvent"))
    {  
      //print(json1);     
      JSONArray values = json1.getJSONArray("rawArgs"); 
      return parseRaw(values) ;
    }   
    return null;
  } 
}  
