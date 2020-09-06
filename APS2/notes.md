# Notes for data packet

The following structure is to be adopted for a data packet:

- It's size is to be no more than 128 bytes
- The first 10 bytes are to be it's header
- The next 0 to 114 bytes are it's message
- The final 4 bytes are the EOP (end of packet), which can be any value.

In the 10 bytes that constitute the header, one must specify all required information for the server to process and store the information sent.
 
1. Message ID
2. Size of Whole Message 
3. Position of Packet in Message (PacketPosition starts at 0)
4. Bytes of Data in this packet
5. 0
6. 0
7. 0
8. 0
9. 0
10. Comms Feedback (0 = Ignore; 1 = Handshake; 2 = Transmission failed, repeat; 3 = Transmission success, continue; 4 = Internal server error, end comms;)
