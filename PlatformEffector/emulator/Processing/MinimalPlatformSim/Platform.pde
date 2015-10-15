static class PlatformDef {
  float baseAngles[]; 
  float platformAngles[]; 
  float beta[];
  float scale;
  // Dimensions
   float initialHeight;
   float baseRadius;
   float platformRadius;
   float legLength ;
   float hornLength;
   float maxTranslation;
   float maxRotation;
}

static final PlatformDef ServoPlatformDef = new  PlatformDef();
  static {
    ServoPlatformDef.platformAngles =  new float[] {325,335, 85,95,   205,215 };
    ServoPlatformDef.baseAngles = new float[]  {300, 0, 60,  120, 180, 240}; // {270, 330, 30,  90, 150, 210};
    ServoPlatformDef.beta = new float[] {-2.5, 1.5, -.25, -3, -4.5, -7}; // angle of servo shaft in radians
                                         
    // Dimensions
    ServoPlatformDef.scale = 1.5;
    ServoPlatformDef.initialHeight = 200;
    ServoPlatformDef.baseRadius = 70;
    ServoPlatformDef.platformRadius = 70;
    ServoPlatformDef.legLength = 200;    
    ServoPlatformDef.hornLength = 30;
    ServoPlatformDef.maxTranslation = 40;
    ServoPlatformDef.maxRotation = 25;
  } 


static final PlatformDef ChairPlatformDef = new  PlatformDef();
  static {
    ChairPlatformDef.platformAngles = new float[] {147, 154, 266, 274, 26, 33 };
    ChairPlatformDef.baseAngles =  new float[]  { 140, 207, 226, 314, 334, 40 };    
    // Dimensions
    ChairPlatformDef.scale = 0.4;
    ChairPlatformDef.initialHeight = 680;
    ChairPlatformDef.baseRadius = 440;
    ChairPlatformDef.platformRadius = 540;
    ChairPlatformDef.legLength = 700;    
    ChairPlatformDef.hornLength = 0;
    ChairPlatformDef.maxTranslation = 40;
    ChairPlatformDef.maxRotation = 25;
  } 

PlatformDef gPlatformDef;  // only needed for servo angles 

class Platform {
  private PVector translation, rotation, initialHeight;
  private PVector[] baseJoint, platformJoint, q, l, A;
  private float[] alpha;
  private float baseRadius, platformRadius, hornLength, legLength;
  private float scale;


  public Platform(PlatformDef def) {
    scale = def.scale;    
    gPlatformDef = def;
    translation = new PVector();
    initialHeight = new PVector(0, 0, scale*def.initialHeight);
    rotation = new PVector();
    baseJoint = new PVector[6];
    platformJoint = new PVector[6];
    alpha = new float[6];
    q = new PVector[6]; // line from base center to platform joint
    l = new PVector[6]; // line from base joint to platform joint (muscle length) 
    A = new PVector[6]; // angle of servo horn 
    baseRadius = scale*def.baseRadius;
    platformRadius = scale*def.platformRadius;
    hornLength = scale*def.hornLength;
    legLength = scale*def.legLength;

    for (int i=0; i<6; i++) {
      float mx = baseRadius*cos(radians(def.baseAngles[i]));
      float my = baseRadius*sin(radians(def.baseAngles[i]));
      baseJoint[i] = new PVector(mx, my, 0);
    }

    for (int i=0; i<6; i++) {
      float mx = platformRadius*cos(radians(def.platformAngles[i]));
      float my = platformRadius*sin(radians(def.platformAngles[i]));
      platformJoint[i] = new PVector(mx, my, 0);
      
      q[i] = new PVector(0, 0, 0);
      l[i] = new PVector(0, 0, 0);
      A[i] = new PVector(0, 0, 0);
    }
    calcQ();
  }

  public void applyTranslationAndRotation(PVector t, PVector r) {
    rotation.set(r);
    translation.set(t);
    calcQ();    
  }

  private void calcQ() {
    for (int i=0; i<6; i++) {
      // rotation
      q[i].x = cos(rotation.z)*cos(rotation.y)*platformJoint[i].x +
        (-sin(rotation.z)*cos(rotation.x)+cos(rotation.z)*sin(rotation.y)*sin(rotation.x))*platformJoint[i].y +
        (sin(rotation.z)*sin(rotation.x)+cos(rotation.z)*sin(rotation.y)*cos(rotation.x))*platformJoint[i].z;

      q[i].y = sin(rotation.z)*cos(rotation.y)*platformJoint[i].x +
        (cos(rotation.z)*cos(rotation.x)+sin(rotation.z)*sin(rotation.y)*sin(rotation.x))*platformJoint[i].y +
        (-cos(rotation.z)*sin(rotation.x)+sin(rotation.z)*sin(rotation.y)*cos(rotation.x))*platformJoint[i].z;

      q[i].z = -sin(rotation.y)*platformJoint[i].x +
        cos(rotation.y)*sin(rotation.x)*platformJoint[i].y +
        cos(rotation.y)*cos(rotation.x)*platformJoint[i].z;

      // translation
      q[i].add(PVector.add(translation, initialHeight));
      l[i] = PVector.sub(q[i], baseJoint[i]);
    }
  }
}

