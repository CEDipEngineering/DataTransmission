import threading
from enlace import enlace
import stdMsgs
import time
from helper import Helper

# https://pypi.org/project/timeout-decorator/

class Server:
    def __init__(self, port):
        self.com = enlace(port)
        time.sleep(3e-3)
        self.running = False
        self.threadActive = False
        self.thread = None
        self.messages = {}
        self.id = 1
        self.helper = Helper()


    def threadJob(self):
        while self.running:
            if self.threadActive:    
                # Get header for message;
                header, nRx = self.com.getData(10)
                if not self.running:
                    break
                
                sensorID = header[1]
                serverID = header[2]
                sizeOfWholeMessage = header[3] # Size of message in packets
                packetPosition = header[4]
                messageID = header[5]
                messageSize = header[8]
                commState = header[1]
                # For now, the remaining bytes are 0

                if serverID != self.id:
                    # Message is not for me :(
                    self.com.rx.clearBuffer()
                    continue

                
                # Before analysing, check if it's a handshake, or something else.
                if commState == 3:
                    # Analyse Header to know whats going on;
                    #   Check message ID, to know if it's a new message.
                    #   Any message that is being received, should be of same size every time,
                    #   And also be of index +1 over the last message of that ID
                    # print(f"packetPos {packetPosition, header[3:5]}; sizeOfWhole {sizeOfWholeMessage, header[1:3]}")

                    infoIsValid = False


                    if packetPosition > sizeOfWholeMessage:
                        print(f"The server has found an error!")
                        print(f"The indicated packet position {packetPosition} is outside the bounds of the message (length {sizeOfWholeMessage})")
                        self.com.sendData(self.helper.constructParcel(head=bytes([6,0,0,0,0,0,self.countMessages(messageID),0,0,0]), data=bytes([])))
                        self.com.rx.clearBuffer()
                        continue

                    # Info will be valid if either it's a new message's packet or if it's the next packet of a known message
                    if messageID in self.messages.keys():
                        if self.countMessages(messageID) == packetPosition:
                            infoIsValid = True
                    elif messageID not in self.messages.keys() and packetPosition == 0:
                        infoIsValid = True
                        self.messages[messageID] = [[] for i in range(sizeOfWholeMessage)]


                    # Use header info to decide whether or not to continue
                    if not infoIsValid:
                        print(f"An error has ocurred with this data packet!")                        
                        print(f"The server has responded and is now expecting a repeat of the message.")
                        self.com.rx.clearBuffer()
                        self.com.sendData(self.helper.constructParcel(head=bytes([6,0,0,0,0,0,self.countMessages(messageID),0,0,0]), data=bytes([])))
                        continue
                    # Empty buffer before going back to waiting
                    

                    # If message is valid, try to read it.
                    content, nRx = self.com.getData(messageSize)

                    # Store value;
                    self.messages[messageID][packetPosition] = content

                # Could implement data verification here:

                # Read EOP, just cause (Should be the same everytime, but whatever);
                EOP, nRx = self.com.getData(4)
                EOP == bytes([255,176,255,176])
                # Make sure that the buffer is Empty before next message starts (?)
                if not self.com.rx.getIsEmpty():
                    self.com.rx.clearBuffer()

                # Enviar mensagem de sucesso
                self.com.sendData(self.helper.constructParcel(head=bytes([4,0,0,0,0,0,0,self.countMessages(messageID),0,0]), data=bytes([])))

                try:
                    print(f"Message transmission in progress: {100*packetPosition/sizeOfWholeMessage:.02f}% ({packetPosition+1}/{sizeOfWholeMessage} packets)")
                finally: 
                    continue



    def beginRunning(self):
        self.com.enable()
        self.threadActive = True
        self.running = True
        self.thread = threading.Thread(target = self.threadJob, args=())
        self.thread.start()

    def killProcess(self):
        self.running = False
        self.threadActive = False
        self.com.disable()
    
    def countMessages(self, id):
        start = self.messages[id]
        j = 0
        for i in start:
            if len(i) != 0:
                j+=1
        return j