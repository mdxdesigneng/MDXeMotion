import java.awt.EventQueue;

import javax.swing.JFrame;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JSlider;
import javax.swing.SwingConstants;
import java.lang.reflect.Field;
import javax.swing.JPanel;

import java.awt.Color;
import java.awt.Dimension;

import javax.swing.border.BevelBorder;
import javax.swing.border.TitledBorder;
import javax.swing.UIManager;
import javax.swing.event.ChangeListener;
import javax.swing.event.ChangeEvent;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import javax.swing.JCheckBox;
import java.awt.Toolkit;

public class Gui {
	
	
	private JFrame frame;
	private JSlider[] outputSliders;
	private JSlider[] cfgSliders;
	private JLabel[]  cfgLabels;
	private JLabel lblOutput;
	private boolean isDirty = false;
	// static objects accessed by PlatformMiddlware class
	private static Gui window;
	private static PlatformApi.config cfgObj;



	public static void guiBegin(PlatformApi.config cfg) {
		cfgObj = cfg;
		// launch the Gui
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					//System.out.println("Opening GUI Window"); 
					window = new Gui();
					window.frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});		
	}	

	/**
	 * Create the application.
	 */
	public Gui() {
		initialize();	
	}

	public static void updateActuators(final float[] vals) {		
		EventQueue.invokeLater(new Runnable() {
		    public void run() {
        		for(int i=0; i < 6; i++) {
        		   int sliderVal = 50+ (int) (vals[i]*50);
        		   if( window != null){        			
        			  if(  window.outputSliders[i] != null)
	                     window.outputSliders[i].setValue(sliderVal);
	                 
        		   }
		        }
		    }
		});
	}
	
	public static void updateLabels(final String label, final String text) {		
		EventQueue.invokeLater(new Runnable() {
		    public void run() {        		
        	     if( window != null){
        	    	 updateSliderValues();
        	    	 if( label.equals("in")){
        	    		 window.frame.setTitle(text);        	    		
        	    	 }
        	    	 else if ( label.equals("out")){
       	    		  window.lblOutput.setText( text);  		 
       	    	    }
        		}
		        
		    }
		});
	}
	
    private void handleGainChange(String name,  int value) {
    	// System.out.format("%s, %d", name, value);		 
		try {
			if( cfgObj != null) {   
		        Field f = cfgObj.getClass().getDeclaredField(name);
			    try {
				  f.set(cfgObj, (float)(value*.02));				 
				
		    	} catch (IllegalArgumentException | IllegalAccessException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			    }
			 
			}			 
		} catch (NoSuchFieldException | SecurityException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
    }
    
    private void handleWashoutChange(String name,  int value) {
    	// System.out.format("%s, %d", name, value);		 
		try {
			if( cfgObj != null) {   
		        Field f = cfgObj.getClass().getDeclaredField(name);
			    try {			 
			       value =100- value; // invert so 100 is max washout	
				  f.set(cfgObj, (float)(((float)value/12500) + 0.992));	
				 // System.out.format("setting washout for %s to %f (%d)\n",name, (float) (((float)value/12500) + 0.992), value); 	
				
		    	} catch (IllegalArgumentException | IllegalAccessException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			    }
			 
			}			 
		} catch (NoSuchFieldException | SecurityException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
    }
    
    private static void updateSliderValues() {
    	 if( cfgObj != null) {            	 
			  Field[] fields = cfgObj.getClass().getDeclaredFields();
			  int len = fields.length;	
			  if( len != 13)
				  System.out.println("did not get 13 fields"); // error	
		      for (int i=0; i < len; i++ ) {
		    	    float val;
					try {
						val = fields[i].getFloat(cfgObj);
					  	if(i < 7){					
					    	window.cfgSliders[i].setValue((int)(val*50));						
			    	    }
			    	    else {   
			    	    	 int v = (int)((val-0.992)*12500);
			    	    	 v = 100-v;
			    	    	 window.cfgSliders[i].setValue(v);
			    	    	// System.out.format("washout : %d , fp=%f, val = %d\n",i, val,v); 	
    			       	  }
					} catch (IllegalArgumentException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					} catch (IllegalAccessException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}		    	  
		      }
    	 }
    }
    
	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frame = new JFrame();
		frame.setIconImage(Toolkit.getDefaultToolkit().getImage(Gui.class.getResource("/res/Platform24.png")));
		frame.setBounds(100, 100, 765, 497);
		frame.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
		frame.getContentPane().setLayout(null);
		frame.setTitle("Input Source not Connected");
		
		frame.addWindowListener(new WindowAdapter() {
			public void windowClosing(WindowEvent e) {
			int confirmed = JOptionPane.showConfirmDialog(null,
			"Are you sure you want to exit?", "User Confirmation",
			JOptionPane.YES_NO_OPTION);
			if (confirmed == JOptionPane.YES_OPTION)
				  System.exit(-1); // todo - set flag in middleware to exit while loop
			
			}
			});
				
		JButton btnSave = new JButton("Save");
		btnSave.setEnabled(false);
		btnSave.setBounds(413, 419, 89, 23);
		frame.getContentPane().add(btnSave);
		btnSave.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e)	{			
			    PlatformApi.saveConfig();
	            btnSave.setEnabled(false); 
            }	
		});	
		
		lblOutput = new JLabel("Output Not Connected");
		lblOutput.setHorizontalAlignment(SwingConstants.CENTER);
		lblOutput.setBounds(10, 24, 180, 12);
		frame.getContentPane().add(lblOutput);
		
		JPanel pnlActuators = new JPanel();
		pnlActuators.setBorder(new BevelBorder(BevelBorder.LOWERED, null, null, null, null));
		pnlActuators.setForeground(Color.GRAY);
		pnlActuators.setBounds(36, 47, 130, 336);
		frame.getContentPane().add(pnlActuators);
		
		outputSliders = new JSlider[6];	
		for( int i=0; i < 6; i++ ) {
			outputSliders[i] = new JSlider();
			outputSliders[i].setOrientation(SwingConstants.VERTICAL);
			outputSliders[i].setEnabled(true);
			outputSliders[i].setName("out" + Integer.toString(i) );
			Dimension d = outputSliders[i].getPreferredSize();
			d.height = pnlActuators.getHeight() - 10 ;
			outputSliders[i].setPreferredSize(d);
			//outputSliders[i].setMaximumSize(new Dimension(Short.MAX_VALUE, 225));
			pnlActuators.add(outputSliders[i]);		
		}
		
		JLabel lblNewLabel_2 = new JLabel("Actuators");
		lblNewLabel_2.setBounds(79, 394, 61, 14);
		frame.getContentPane().add(lblNewLabel_2);
		
		JPanel pnlGain = new JPanel();
		pnlGain.setBorder(new TitledBorder(null, "Gain", TitledBorder.LEADING, TitledBorder.TOP, null, null));
		pnlGain.setBounds(188, 23, 268, 385);
		frame.getContentPane().add(pnlGain);
		
		JPanel pnlWashout = new JPanel();
		pnlWashout.setBorder(new TitledBorder(UIManager.getBorder("TitledBorder.border"), "Washout", TitledBorder.LEADING, TitledBorder.TOP, null, new Color(0, 0, 0)));
		pnlWashout.setBounds(464, 23, 268, 385);
		frame.getContentPane().add(pnlWashout);
		
		try{
			
            if( cfgObj != null) {            	 
				  Field[] fields = cfgObj.getClass().getDeclaredFields();
				  int len = fields.length;	
				  if( len != 13)
					  System.out.println("did not get 13 fields"); // error
				  cfgSliders = new JSlider[len];	
				  cfgLabels = new JLabel[len];
			      for (int i=0; i < len; i++ ) {
			    	    cfgSliders[i]= new JSlider();
			    	    String name = fields[i].getName();
			    	    String lbl = null;
			    	    int index = name.indexOf("gain");
			    	    if( index > -1 ) {
			    	    	lbl = name.substring(index + "gain".length());
			    	    	cfgSliders[i].addChangeListener(new ChangeListener() {
								public void stateChanged(ChangeEvent e) {
									 JSlider source = (JSlider)e.getSource();
								        if (!source.getValueIsAdjusting()) {
								            int val = (int)source.getValue();
								            handleGainChange(source.getName(), source.getValue());
								            isDirty = true;
								            btnSave.setEnabled(true);							           
								        }    
								}
							});
			    	    }
			    	    else if( (index = name.indexOf("washout")) > -1) { 
			    	    	lbl = name.substring(index+ "washout".length());
			    	    	cfgSliders[i].addChangeListener(new ChangeListener() {
								public void stateChanged(ChangeEvent e) {
									 JSlider source = (JSlider)e.getSource();
								        if (!source.getValueIsAdjusting()) {
								            int val = (int)source.getValue();
								            handleWashoutChange(source.getName(), source.getValue());
								            isDirty = true;
								            btnSave.setEnabled(true);							           
								        }    
								}
							});
			    	    }
			    	    if(lbl != null)
			    	       lbl = ("      " + lbl).substring(lbl.length()); // pad left
			    	    else
			    	    	lbl = "     unk";
			    	    //System.out.format("%s, index = %d\n", name, index);			    	
			    	    cfgSliders[i].setName(name);
						cfgSliders[i].setPaintLabels(true);
						cfgSliders[i].setPaintTicks(true);
						cfgSliders[i].setMajorTickSpacing(10);
						cfgSliders[i].setBorder(null);						
						cfgLabels[i] = new JLabel(lbl);					    
					    //System.out.format("%s = %f\n", fields[i].getName().toString(),cfgArray[i]);
						if( i < 7) {
					       pnlGain.add(cfgLabels[i]);
						   pnlGain.add(cfgSliders[i], fields[i].getName().toString());
				
						}
						else {
							pnlWashout.add(cfgLabels[i]);
							pnlWashout.add(cfgSliders[i], fields[i].getName().toString());					
						}
			          }
						
			         }	
		    	} catch( Exception e) {
	    	 	System.out.println(e);
		  	}	
	}
}
