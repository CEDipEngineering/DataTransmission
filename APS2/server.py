import threading
from enlace import enlace

class Server:
    def __init__(self, port):
        self.com = enlace(port)
        self.running = False
        self.thread = None
        self.messages = {}
        self.codes = {
            "FAIL":bytes([0]),
            "PASS":bytes([1]),
            "INTERNALSERVERERROR":bytes([2])
        }


    def threadJob(self):
        while self.running:

            # Get header for message;
            header, nRx = self.com.getData(10)
            if not self.running:
                break
            # Analyse Header to know whats going on;
            #   Check message ID, to know if it's a new message.
            #   Any message that is being received, should be of same size every time,
            #   And also be of index +1 over the last message of that ID


            # Use header info to decide whether or not to continue
            # if not infoIsValid:
            #    self.rx.clearBuffer()
            #    continue
            # Empty buffer before going back to waiting
            

            # If message is valid, try to read it.
            messageSize = header[3]
            content, nRx = self.com.getData(messageSize)

            # Store value;


            # Could implement data verification here:

            # Read EOP, just cause;
            EOP, nRx = self.com.getData(4)

            # Should be the same everytime, but whatever
            if not self.com.rx.getIsEmpty():
                self.com.rx.clearBuffer()


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