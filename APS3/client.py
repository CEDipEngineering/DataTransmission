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
        self.timeResend = 5
        self.timeOut = 25
        
    def beginRunning(self, serverID = 1):
        self.com.enable()        
        serverAlive = False
        timeoutTimer = time.perf_counter()
        print("==================================== \nBeginning client handshake: \n====================================\n")
        while not serverAlive and time.perf_counter()-timeoutTimer<=self.timeOut:
            self.com.sendData(self.helper.constructParcel(head=bytes([1,0,serverID,len(self.buffer),0,0,0,0,0,0]), data=bytes([])))
            print("Sending handshake (Now waiting for 5 seconds)")
            header, nRx = self.com.getData(10,5)
            
            if header == b'':
                self.com.rx.clearBuffer()
                print(f'Server failed to respond!')
                continue
            
            else:
                # print(f"Client received header: {header}")
                EOP, nRx = self.com.getData(4)
                # print(f"EOP Client Handshake is right?: {EOP == bytes([255,176,255,176])}")
                mess = header + EOP
                # print(f"Expected SERVERALIVEMSG: {stdMsgs.SERVERALIVEMSG}")
                # print(f"Received SERVERALIVEMSG: {mess}")
                if mess == stdMsgs.SERVERALIVEMSG:
                    print("Handshake Success!\n")
                    serverAlive = True

        if not serverAlive:    
            self.com.rx.clearBuffer()    
            print("The server hasn't responded yet...")
            j = input("Try again? (y/n): ")
            if(j.lower() in [" ", "y", ""]):
                self.beginRunning(serverID)
        else:
            print("==================================== \nClient handshake finished. \n====================================\n")
            return

    def killProcess(self):
        self.com.disable()

    def sendMessage(self):
        timeoutTimer = time.perf_counter()
        counter = 0
        while counter < len(self.buffer.values()) and time.perf_counter()-timeoutTimer<self.timeOut:
            datagram = list(self.buffer.values())[counter]
            
            # Send current packet
            success = False
            resendTimer = time.perf_counter()
            while not success and time.perf_counter() - resendTimer < self.timeResend:
                
                # Noise generator for testing
                mess = datagram[:]
                if self.makeNoise:
                    # This is to introduce noise for testing. Ignore.
                    if random.randint(0,100) < 25:
                        mess = mess[0:3] + bytes([random.randint(0,255), random.randint(0,255)]) + mess[5:]
                        print("\nRandom error has been introduced!\n")
                
                self.com.sendData(mess)
                resp, nRx = self.com.getData(14)
                if resp[0] != 4:
                    if resp[0] == 6:
                        counter = resp[6]
                        timeoutTimer = time.perf_counter()
                        resendTimer = time.perf_counter()
                else:
                    success = True
            
            
            if success:
                timeoutTimer = time.perf_counter()
                counter += 1

        if counter == len(self.buffer.values()):
            print(f"Message transmission has finished.")
        else:
            self.com.sendData(stdMsgs.TIMEOUTMSG)
            self.killProcess()
            print(f"Communication has failed!")
