# MessengerProject
server-client messenger, basic encryption, room based design

To run this code on another computer, the only part that matters is if the server is going to be run on a different network. 
If the servers network address is unchanged the clients will all function immediately after download.

But, if the server is going to be run on a different network, then the server address inside of client code needs to be changed.
It needs to be set to the public IP address of wherever the server will be running, which can be found through various sites, like whatismyip.com.
however, it must be noted whenever a router is restarted your public IP will change and it will need to be re-adjusted in the code. 
This can be bypassed with a static IP domain, which will never change, but it is not necessary. 

After that the server, still may not function properly depending on your router’s settings.
you may need to go into your network settings and enable port forwarding for port 20020(the port I chose, you could change it if you want).
something like 20020-20050 all forwarded to 20020. The number of slots you forward to port 20020 will be how many users you can have at once.
 
Once the setup is complete, run one instance of the server in any python shell.
Now anyone who runs the client program, will connect to that instance of the server.

client users will be prompted to give a name and press login,
then a new screen will ask them to enter a room number (just the number, and currently its only setup for 1-5) and press join or they can leave the box blank, and press create new room.
After that the client will be sitting in the corresponding room where they can click the lower box, type a message, and press the button to send it out to the room.
