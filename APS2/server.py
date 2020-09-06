import threading
from enlace import enlace
import stdMsgs

class Server:
    def __init__(self, port):
        self.com = enlace(port)
        self.running = False
        self.thread = None
        self.messages = {}
        self.codes = {
            "FAIL":stdMsgs.FAILMSG,
            "PASS":stdMsgs.SUCCESSMSG,
            "INTERNALSERVERERROR":stdMsgs.SERVERERRORMSG
        }


    def threadJob(self):
        while self.running:

            # Get header for message;
            header, nRx = self.com.getData(10)
            if not self.running:
                break

            messageID = int.from_bytes(header[0],"little")
            sizeOfWholeMessage = int.from_bytes(header[1],"little") # Size of message in packets
            packetPosition = int.from_bytes(header[2],"little")
            messageSize = int.from_bytes(header[3],"little")
            commState = int.from_bytes(header[9],"little")
            # For now, the remaining bytes are 0
            
            # Before analysing, check if it's a handshake, or something else.
            if commState == 0:
                # Analyse Header to know whats going on;
                #   Check message ID, to know if it's a new message.
                #   Any message that is being received, should be of same size every time,
                #   And also be of index +1 over the last message of that ID
                infoIsValid = False

                # Info will be valid if either it's a new message's packet or if it's the next packet of a known message
                if messageID in self.messages.keys():
                    if len(self.messages[messageID]) == packetPosition:
                        infoIsValid = True
                elif messageID not in self.messages.keys() and packetPosition == 0:
                    infoIsValid = True
                    self.messages[messageID] = [[]*sizeOfWholeMessage]


                # Use header info to decide whether or not to continue
                if not infoIsValid:
                    self.com.rx.clearBuffer()
                    self.reply("FAIL")
                    continue
                # Empty buffer before going back to waiting
                

                # If message is valid, try to read it.
                content, nRx = self.com.getData(messageSize)

                # Store value;
                self.messages[messageID][packetPosition] = content



            # Could implement data verification here:

            # Read EOP, just cause (Should be the same everytime, but whatever);
            EOP, nRx = self.com.getData(4)

            # Make sure that the buffer is Empty before next message starts (?)
            if not self.com.rx.getIsEmpty():
                self.com.rx.clearBuffer()

            self.reply("PASS")


    def beginRunning(self):
        self.thread = threading.Thread(self.threadJob, args=())
        self.com.enable()
        self.running = True

    def reply(self, keyword):
        try:
            message = self.codes[keyword]
        except KeyError:
            message = self.codes["INTERNALSERVERERROR"]
        
        self.com.sendData(message)

    def killProcess(self):
        self.running = False
        self.com.disable()