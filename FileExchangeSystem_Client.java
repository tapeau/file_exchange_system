// Machine Project Group 10
// TAPIA, John Lorenzo N.
// ARGAMOSA, Daniel Cedric S.
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.InetSocketAddress;
import java.net.SocketTimeoutException;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class FileExchangeSystem_Client {
    // Function to display Help page - accessed with '/?' command
    public static void displayHelp() {
        System.out.println(""
                + "/?\t\t\t\t\t\t\tDisplay information about all valid commands\n"
                + "/dir\t\t\t\t\t\tDisplay a directory of the files in the File Exchange server\n"
                + "/exit\t\t\t\t\t\tExit the program - disconnects from any connected File Exchange server\n"
                + "/get [filename]\t\t\t\tDownload a file of name [filename] from the File Exchange server\n"
                + "/join [ip_address] [port]\tConnect to the File Exchange server of IP address [ip_address] and port number [port]\n"
                + "/leave\t\t\t\t\t\tDisconnect from the connected File Exchange server\n"
                + "/register [alias]\t\t\tRegister to the connected File Exchange server using the handle [alias]\n"
                + "/store [filename]\t\t\tUpload a file of name [filename] to the File Exchange server - [filename] must exist inside the client's directory\n");
    }
    
    // Function to check whether a string is a valid IPv4 address
    public static boolean isValidIPAddress(String ipAddress) {
        // Define the regex pattern for a valid IPv4 address
        String ipPattern = "^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\\."
                        + "(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\\."
                        + "(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\\."
                        + "(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$";

        // Compile the pattern
        Pattern pattern = Pattern.compile(ipPattern);

        // Match the given IP address with the pattern
        Matcher matcher = pattern.matcher(ipAddress);

        // Return true if it matches or if the string is "localhost", false otherwise
        return ipAddress.equals("localhost") || matcher.matches();
    }
    
    // Main function
    public static void main(String[] args) {
        // Initial interface
        System.out.println("------------------------------");
        System.out.println("FILE EXCHANGE SYSTEM");
        System.out.println("------------------------------\n");
        System.out.println("Welcome!");
        System.out.println("Please connect to a server to start...\n");
        System.out.println("To get a list of all recognized commands, enter \'/?\'");
        
        // Declare variables
        Socket socEndpoint = new Socket();
        boolean bContinue = true;
        
        // Main program loop
        do {
            // Scan for input
            Scanner sInput = new Scanner(System.in);
            sInput.useDelimiter(" ");

            // Evaluate input
            String sCommand = sInput.next();
            switch (sCommand) {
                
                // '/?' command
                case "/?" -> displayHelp();
                
                // '/join' command
                case "/join" -> {
                    String sServerAdd = "";
                    int nServerPort = -1;

                    // Get server IPv4 address
                    if (sInput.hasNext() == false) {
                        System.out.println("ERROR: You have not entered any IP address\n"
                                + "Command format:\t/join [ip_address] [port]");
                    } else {
                        sServerAdd = sInput.next();

                        // Additional check if address is valid
                        if (isValidIPAddress(sServerAdd) == false) {
                            System.out.println("ERROR: You entered an invalid IPv4 address.");
                            sServerAdd = "";
                        }
                    }
                    if (sServerAdd.isEmpty()) break;

                    // Get server port
                    if (sInput.hasNext() == false) {
                        System.out.println("ERROR: You have not entered any port number\n"
                                + "Command format:\t/join [ip_address] [port]");
                    } else {
                        // Try-catch system for port number validation
                        try {
                            // Attempt to parse the string as an integer
                            nServerPort = Integer.parseInt(sInput.next());
                        } catch (NumberFormatException e1) {
                            nServerPort = -1;
                        }
                    }
                    if (nServerPort == -1) break;

                    // Connect to the server
                    try {
                        System.out.println("Connecting to server at " + socEndpoint.getRemoteSocketAddress());
                        socEndpoint.connect(new InetSocketAddress(sServerAdd, nServerPort), 6000); // Timeout after 6000 ms (6 seconds)
                        System.out.println("Connected to server at " + socEndpoint.getRemoteSocketAddress());
                    } catch (SocketTimeoutException e) {
                        System.err.println("ERROR: Connection timed out. Check server availability and try again.");
                    } catch (IOException e) {
                        if (e instanceof java.net.ConnectException) {
                            System.err.println("ERROR: Could not connect to the server. Make sure the server is running and try again.");
                        } else {
                            System.err.println("I/O ERROR: " + e.getMessage());
                        }
                    }
                }
                
                // TODO: Switch case for other commands
                
                // '/exit' command
                case "/exit" -> {
                    // Close the connection
                    try {
                        // TODO: Disconnect from connected server, if any
                        socEndpoint.close();
                    } catch (IOException e) {
                        System.err.println("I/O ERROR: " + e.getMessage());
                    }
                    
                    // Halt continuation of program
                    System.out.println("Program terminated.");
                    bContinue = false;
                }
                
                // For invalid commands
                default -> System.out.println("ERROR: \'" + sCommand + "\' is not recognized as a valid command.");
            }
        } while (bContinue);
    }
}