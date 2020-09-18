import threading
from enlace import enlace
import stdMsgs
import time
import random
from helper import Helper

class Client:
    def __init__(self, port):
        self.com = enlace(port)
        time.sleep(3e-3)
        self.running = False
        self.threadActive = False
        self.thread = None
        self.buffer = {}
        self.helper = Helper()
        self.makeNoise = False
        
    def beginRunning(self, serverID = 1):
        self.com.enable()        
        serverAlive = False
        while not serverAlive:
            print("==================================== \nBeginning client handshake: \n====================================\n")
            self.com.sendData(self.helper.constructParcel(head=bytes([1,0,serverID,len(self.buffer),0,0,0,0,0,0]), data=bytes([])))
            print("Sending handshake (Now waiting for 5 seconds)")

            header, nRx = self.com.getData(10,5)
            # print(f"Client received header: {header}")
            if len(header) != 10:    
                print("The server hasn't responded yet...")
                j = input("Try again? (y/n): ")
                if(j.lower() in [" ", "y", ""]):
                    continue
                else:
                    serverAlive = False
                    break
            else:
                EOP, nRx = self.com.getData(4)
                mess = header + EOP
                # print(f"Expected SERVERALIVEMSG: {stdMsgs.SERVERALIVEMSG}")
                # print(f"Received SERVERALIVEMSG: {mess}")
            if mess == stdMsgs.SERVERALIVEMSG:
                print("Handshake Success!\n")
                serverAlive = True
            
            self.com.rx.clearBuffer()
        if not serverAlive:
            self.killProcess()
            return
        print("==================================== \nClient handshake finished. \n====================================\n")

    def killProcess(self):
        self.com.disable()

    def sendDatagram(self, datagram):
        success = False
        while not success:
            mess = datagram[:]
            if self.makeNoise:
                # This is to introduce noise for testing. Ignore.
                if random.randint(0,100) < 15:
                    mess = mess[0:3] + bytes([255, 255]) + mess[5:]
                    print("\nRandom error has been introduced!\n")
            self.com.sendData(mess)
            resp, nRx = self.com.getData(14)
            success = resp[0] == 4
        return 1

    def sendMessage(self):
        for i in self.buffer.values():
            verif = self.sendDatagram(i)
            if verif == 0 or verif == -1:
                return verif
            else:
                continue