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
		   msg = PlatformApi.shapeData(msg); // apply gain and washout		      
		   transform.applyTranslationAndRotation(new PVector(msg.x, msg.y, msg.z), 
				                                 new PVector(msg.pitch, msg.roll, msg.yaw));
		   // todo - code needed to use transform to create raw muscle length messages
		   //  for testing form xyzpry message 
		   chairItf.sendXyzrpy(msg);
	 
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
