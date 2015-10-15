import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;

// This thread takes care of a single watcher
public class SingleWatcher extends Thread {

    Socket clientSocket = null;    
    PrintWriter out = null;

    public SingleWatcher(Socket cs) {
        // We just set up the socket and the output stream
        // (we do not expect input from the client)
        this.clientSocket = cs;
        try {
            this.out = new PrintWriter(this.clientSocket.getOutputStream(), true);         
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }
    
    @Override
    public void run() {
        // nothing to do here... we just need to keep running
        // waiting for the other server to tell us that we need
        // to publish a message through the method announce below
    }
    public String getHostName() {
    	return clientSocket.getInetAddress().getHostName();	
    }
    
    public boolean announce(String s) {      
        this.out.println(s);
        if(out.checkError())
        {
             return false; // if error writing to socket
        }
        return true;
    }
}
