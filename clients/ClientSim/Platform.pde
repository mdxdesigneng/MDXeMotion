public class Platform  {
  private PVector translation, rotation, initialHeight; 
  private float baseRadius, platformRadius;

  // REAL ANGLES
  private final float platformAngles[] = {
//   50, 117, 136, 224, 244, 310 };
  140, 207, 226, 314, 334, 40 };

  private final float baseAngles[]  = {
 //  57, 64, 176,  184, 296, 303};
 147, 154, 266, 274, 26, 33 };


  // REAL MEASUREMENTS
  private final float SCALE_INITIAL_HEIGHT = 700;
  private final float SCALE_PLATFORM_RADIUS = 400;

  public Platform(float s) {
    translation = new PVector();
    initialHeight = new PVector(0, 0, s*SCALE_INITIAL_HEIGHT);
    rotation = new PVector();

     platformRadius = s*SCALE_PLATFORM_RADIUS;

    for (int i=0; i<6; i++) {
     float mx = platformRadius*cos(radians(platformAngles[i]));
     float my = platformRadius*sin(radians(platformAngles[i]));
    }
  }

  public void applyTranslationAndRotation(PVector t, PVector r) {
    rotation.set(r);
    translation.set(t);   
  }


  public void draw() {
    // draw Base
    noStroke();
    noFill();
    //fill(128);
    ellipse(0, 0, 2*baseRadius, 2*baseRadius);


    // sanity check
    pushMatrix();
    translate(initialHeight.x, initialHeight.y, initialHeight.z);
    translate(translation.x, translation.y, translation.z);
    rotateZ(rotation.z);
    rotateY(rotation.y);
    rotateX(rotation.x);
    stroke(245);
    //noFill();
    fill(128);
    ellipse(0, 0, 2*platformRadius, 2*platformRadius);
    fill(255,0,0);
    box(150); 
    popMatrix();
  }
}
