import java.util.*;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;


/*
 *  Main module for middleware test harness
 *  Handles messages from clients queued in PlatformItf thread.
 *  After data is processed for gain and washout, raw muscle lengths
 *  are calculated from rotational data and sent to the MDX platform 
 */

public class PlatformMiddleware {
	public static LinkedList<PlatformApi.msgFields> msgQueue;
	private final Lock lock = new ReentrantLock();
	private PlatformApi api;
	private PlatfromTransforms transform;
	private ChairInterface chairItf;

	
	public PlatformMiddleware()	{		
		this.transform = new PlatfromTransforms();
		this.api = new PlatformApi(lock);
		this.chairItf = new ChairInterface();
	}
	 
	private boolean begin(){
	   if(!chairItf.begin())
		  return false; // terminate  
	   api.begin();
	   return true;
	}
	
	private void end(){
	   api.end();
	   chairItf.end();
	  
	}
	
	private void processMsg(PlatformApi.msgFields msg) {
      //System.out.format("pre shape: %f,%f,%f, %f,%f,%f\n",msg.x, msg.y, msg.z, msg.pitch, msg.roll, msg.yaw);	
		   if( msg.isRaw ) {
			   chairItf.sendRaw(msg);
		   }
		   else {
		       msg = PlatformApi.shapeData((PlatformApi.xyzMsg)msg); // apply gain and washout only if xyzMsg		   
		       transform.applyTranslationAndRotation(new PVector(msg.v[0], msg.v[1], msg.v[2]),
				                                     new PVector(msg.v[3], msg.v[4], msg.v[5]));
		       // todo - transform method call above should use xyzGet methods as args
		       // todo - code needed to use transform to get raw muscle length messages
		       //  for testing form xyzpry message 
		       chairItf.sendXyzrpy((PlatformApi.xyzMsg)msg);
		   }	 
	}	
	
	public static void main(String[] args) {
		System.out.println("Platform Middleware Prototype");	
		PlatformMiddleware pm = new PlatformMiddleware();
		if(!pm.begin()){			
			System.exit(0); 
			return; // exit if cannot connect to chair
		}
		try {
			msgQueue = new LinkedList<PlatformApi.msgFields>();				

			while (true) {
				PlatformApi.msgFields msg = null;
				pm.lock.lock();
				if (PlatformMiddleware.msgQueue.size() > 0) {
					msg = (PlatformApi.msgFields) PlatformMiddleware.msgQueue.getFirst();
					PlatformMiddleware.msgQueue.removeFirst();
				}
				pm.lock.unlock();
				if (msg != null) {				
					pm.processMsg(msg);
				}
				try {
					Thread.sleep(10);
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
		} finally {
			pm.end();
			System.out.println("Finished");

		}
	}

}
