UDPServer
=========
Create a UDP server that runs in nio to receive data.

Properties
----------
- **host**: The host address for the udp server.
- **packet_size**: Packet size used for reading udp socket.
- **port**: The port for the udp server.
- **threaded**: Dispatch a thread to handle every datagram received.

Inputs
------
None

Outputs
-------
- **default**: A signal with attribute `data` for each received data packet.

Commands
--------
None

