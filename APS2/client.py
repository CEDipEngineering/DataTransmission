import threading
from enlace import enlace
import stdMsgs
import time

class Client:
    def __init__(self, port):
        self.com = enlace(port)
        time.sleep(3e-3)
        self.running = False
        self.threadActive = False
        self.thread = None
        self.buffer = {}
        self.codes = {
            "FAIL":stdMsgs.FAILMSG,
            "PASS":stdMsgs.SUCCESSMSG,
            "INTERNALCLIENTERROR":stdMsgs.CLIENTERRORMSG
        }


    def threadJob(self):
        while self.running:
            if self.threadActive:
                # Get header for message;
                header, nRx = self.com.getData(10)
                if not self.running:
                    break

                messageID = header[0]
                sizeOfWholeMessage = int.from_bytes(header[1:3],"little") # Size of message in packets
                packetPosition = int.from_bytes(header[3:5], "little")
                messageSize = header[5]
                commState = header[9]
                # For now, the remaining bytes are 0
                
                # Before analysing, the client only needs to know if it's a comms message.
                # The client never receives data

                # Could implement data verification here:

                # Read EOP, just cause (Should be the same everytime, but whatever);
                EOP, nRx = self.com.getData(4)

                # Make sure that the buffer is Empty before next message starts (?)
                if not self.com.rx.getIsEmpty():
                    self.com.rx.clearBuffer()

                self.reply("PASS")


    def beginRunning(self):
        self.com.enable()        
        serverAlive = False
        while not serverAlive:
            self.com.sendData(stdMsgs.HANDSHAKEMSG)
            print("Sending handshake")
            time.sleep(5)
            print("Checking for response")

            buff = self.com.rx.getBuffer(14)
            if len(buff) != 14:    
                print("O server ainda não respondeu, tentar de novo?")
                j = input("Tentar contato com o servidor? (y/n): ")
                if(j.lower() in [" ", "y", ""]):
                    continue
                else:
                    serverAlive = False
                    break
            if buff == stdMsgs.SUCCESSMSG:
                print("Handshake Success!")
                serverAlive = True
            
            self.com.rx.clearBuffer()
        if not serverAlive:
            self.killProcess()
            return
        self.threadActive = True
        self.running = True
        self.thread = threading.Thread(target = self.threadJob, args=())
        self.thread.start()

    def reply(self, keyword):
        try:
            message = self.codes[keyword]
        except KeyError:
            message = self.codes["INTERNALCLIENTERROR"]
        
        self.com.sendData(message)

    def killProcess(self):
        self.running = False
        self.threadActive = False
        self.com.disable()

    def sendDatagram(self, datagram):
        success = False
        counter = 0
        while not success:
            self.com.sendData(datagram)
            resp, nRx = self.com.getData(14)
            success = resp == stdMsgs.SUCCESSMSG
            if resp[9] == 4:
                return -1
            counter += 1
            if counter >= 100:
                return 0
        return 1

    def sendMessage(self, message):
        for i in message:
            verif = self.sendDatagram(i)
            if verif == 0 or verif == -1:
                return verif
            else:
                continue