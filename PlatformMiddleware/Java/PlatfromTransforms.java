
import java.lang.Math;

/*
 *  Modules for rotation and translation transforms
 */

public class PlatfromTransforms {
	private PVector translation, rotation, initialHeight;
	private PVector[] baseJoint, platformJoint, q, l, A;
	private float baseRadius, platformRadius;
	private float maxTranslation, maxRotationRadians;
	private float minLen; 
	private float maxLen;

	public PlatfromTransforms() {	
	}

	public void begin(EffectorInterface.effectorDef def) {	
		minLen = def.minActuatorLen;
		maxLen = def.maxActuatorLen;
		translation = new PVector();
		initialHeight = new PVector(0, 0, def.initialHeight );
		rotation = new PVector();
		baseJoint = new PVector[6];
		platformJoint = new PVector[6];

		q = new PVector[6];
		l = new PVector[6];
		A = new PVector[6];
		baseRadius = def.baseRadius;
		platformRadius = def.platformRadius;
		maxTranslation = def.maxTranslation;
		maxRotationRadians = (float)Math.toRadians(def.maxRotation);
		
		for (int i = 0; i < 6; i++) {
			float mx = (float) (baseRadius * Math.cos(Math.toRadians(def.baseAngles[i])));
			float my = (float) (baseRadius * Math.sin(Math.toRadians(def.baseAngles[i])));
			baseJoint[i] = new PVector(mx, my, 0);
		}	
		for (int i=0; i<6; i++) {
		    float mx = (float)(platformRadius * Math.cos(Math.toRadians(def.platformAngles[i])));
		    float my = (float)(platformRadius * Math.sin(Math.toRadians(def.platformAngles[i])));
		    platformJoint[i] = new PVector(mx, my, 0);		
		    q[i] = new PVector(0,0,0);
			l[i] = new PVector(0,0,0);
			A[i] = new PVector(0,0,0);			
		}
		calcQ();
	}
	
	public void showAll() {	
		System.out.print("rotation="); 	System.out.print(rotation);
		System.out.print(", translation="); 	System.out.println(translation);
		/*
		System.out.print("q= ");
		for(int i=0; i < 6; i++ ) {
		  	System.out.print(q[i]);   System.out.print(" ");  
		}
		System.out.println(); 
		*/
		System.out.print("l= ");
		for(int i=0; i < 6; i++ ) {
		  	System.out.print(l[i].mag());   System.out.print(" ");  
		}
		System.out.println(); 
 
	}
	
	public void applyTranslationAndRotation(PVector t, PVector r) {	  
		rotation.set(PVector.mult(r, maxRotationRadians));
		translation.set(PVector.mult(t,maxTranslation));		
		calcQ();
		//showAll();
	}	
	
	public float getRawLength(int index) {
		 float v = l[index].mag();
		 float vnormalized = -1 + ((v - minLen) * 2 / (maxLen - minLen));
		 //System.out.format("%d  %f %f\n", index, v, vnormalized  );  	
	   return (vnormalized) ; 
	}

	private void calcQ() {		   
	        for (int i=0; i<6; i++) {
	          // rotation	        		        	
	          q[i].x = (float) (Math.cos(rotation.z)*Math.cos(rotation.y)*platformJoint[i].x +
	            (-Math.sin(rotation.z)*Math.cos(rotation.x)+Math.cos(rotation.z)*Math.sin(rotation.y)*Math.sin(rotation.x))*platformJoint[i].y +
	            (Math.sin(rotation.z)*Math.sin(rotation.x)+Math.cos(rotation.z)*Math.sin(rotation.y)*Math.cos(rotation.x))*platformJoint[i].z);

	          q[i].y = (float) (Math.sin(rotation.z)*Math.cos(rotation.y)*platformJoint[i].x +
	            (Math.cos(rotation.z)*Math.cos(rotation.x)+Math.sin(rotation.z)*Math.sin(rotation.y)*Math.sin(rotation.x))*platformJoint[i].y +
	            (-Math.cos(rotation.z)*Math.sin(rotation.x)+Math.sin(rotation.z)*Math.sin(rotation.y)*Math.cos(rotation.x))*platformJoint[i].z);

	          q[i].z = (float) (-Math.sin(rotation.y)*platformJoint[i].x +
	        		  Math.cos(rotation.y)*Math.sin(rotation.x)*platformJoint[i].y +
	        		  Math.cos(rotation.y)*Math.cos(rotation.x)*platformJoint[i].z);

	          // translation
	          q[i].add(PVector.add(translation, initialHeight));
	          l[i] = PVector.sub(q[i], baseJoint[i]);	        
	        }
	   }
      
}
