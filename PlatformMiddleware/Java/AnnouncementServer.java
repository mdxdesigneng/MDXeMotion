import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.LinkedList;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

// This TCP server sends the same message to all connected clients.
public class AnnouncementServer extends Thread {
	
	// The actual server
	ServerSocket ss = null;
    private final Lock lock = new ReentrantLock();
	
	// The list of clients currently connected to this server
	LinkedList <SingleWatcher> listOfClients = new LinkedList <SingleWatcher>();
	
	public AnnouncementServer(int port) {
	    try {
	        ss = new ServerSocket(port);
	    } catch (IOException e) {
            System.err.println("Could not listen on Watcher port: " + Integer.toString(port));
            System.err.println("Notification to watching clients is disabled");
	        System.exit(1);
	    }
	}

	@Override
	public void run() {
		while (true) {
			try {
				// We wait here for connections
				Socket clientSocket = ss.accept();
                System.out.println(String.format("Connection from watcher on %s",clientSocket.getInetAddress() ));               
                // When we receive a connection, we create a new thread and we add it to the list of clients
				SingleWatcher watcher = new SingleWatcher(clientSocket);
				watcher.start();
                this.lock.lock();
				listOfClients.add(watcher);
                this.lock.unlock();
			} catch (IOException e) {
                System.err.println("Failed to add watcher to list.");                
			}
		}
	}
	
	public void announce(String s) {
		// We call the method announce for each client that is not null
		//System.out.println("We currently have "+listOfClients.size()+" clients connected");
		for (SingleWatcher watcher: listOfClients) {
			if ( watcher != null ) {
				 if(!watcher.announce(s) ) {                    
                     // error writing to client, assume disconnect so remove from list
                     // TODO more exception handling needed here 
                   	 System.out.println(String.format("Error sending to watcher %s, removing from list", watcher.getHostName()) );				
                     this.lock.lock();
                     listOfClients.remove(watcher);
                     this.lock.unlock();                     
                 }
			}
            else {
                // null watcher, remove from list
            	 // TODO exception handling needed here 
              	System.out.println("Null watcher, removing from list "); 
                this.lock.lock();
                listOfClients.remove(watcher);
                this.lock.unlock(); 
            }
		}
	}
	
}
