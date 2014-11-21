UDPServer
=========

This block provides a UDP server that runs inside nio. 


Properties
----------

-  **host**: The host IP for the UDP server. Defaults to '127.0.0.1'.
-  **port**: The desired port for the server. If left unset, the block will obtain an available port from nio's PortManager.
-  **threaded**: Dispatch a thread to handle every datagram received
-  **packet_size**: Packet size used for reading udp socket. Defaults to 8192 

Dependencies
------------


Commands
--------


Input
-----


Output
------

  Signals with data attribute containing udp raw data received