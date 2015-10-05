
import java.lang.Math;

/*
 *  Modules for rotation and translation transforms
 */

public class PlatfromTransforms {
	// REAL ANGLES of attachment points
	private final float platformAngles[] = { 140, 207, 226, 314, 334, 40 };
	private final float baseAngles[] = { 147, 154, 266, 274, 26, 33 };

	// REAL MEASUREMENTS
	private final float SCALE_INITIAL_HEIGHT = 700;
	private final float SCALE_BASE_RADIUS = 400;
	private final float SCALE_PLATFORM_RADIUS = 400;
	private final float SCALE_LEG_LENGTH = 800;

	private PVector translation, rotation, initialHeight;
	private PVector[] baseJoint, platformJoint, q, l, A;
	private float baseRadius, platformRadius, legLength;

	public PlatfromTransforms() {	
		//System.out.println(" in transform constructor");
		translation = new PVector();
		initialHeight = new PVector(0, 0, SCALE_INITIAL_HEIGHT);
		rotation = new PVector();
		baseJoint = new PVector[6];
		platformJoint = new PVector[6];

		q = new PVector[6];
		l = new PVector[6];
		A = new PVector[6];
		baseRadius = SCALE_BASE_RADIUS;
		platformRadius = SCALE_PLATFORM_RADIUS;
		legLength = SCALE_LEG_LENGTH;

		for (int i = 0; i < 6; i++) {
			float mx = (float) (baseRadius * Math.cos(Math.toRadians(baseAngles[i])));
			float my = (float) (baseRadius * Math.sin(Math.toRadians(baseAngles[i])));
			baseJoint[i] = new PVector(mx, my, 0);
			q[i] = new PVector();
			l[i] = new PVector();
			A[i] = new PVector();
			platformJoint[i] = new PVector();
		}
	}

	public void applyTranslationAndRotation(PVector t, PVector r) {
		rotation.set(r);
		translation.set(t);
		calcQ();
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
