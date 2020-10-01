import threading
from enlace import enlace
import stdMsgs
import time
import random
from helper import Helper

import datetime

today = datetime.datetime.today

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
        self.timeResend = 3
        self.timeOut = 20
        
    def beginRunning(self, serverID = 1):
        self.com.enable()        
        serverAlive = False
        timeoutTimer = time.perf_counter()
        print("==================================== \nBeginning client handshake: \n====================================\n")
        while not serverAlive and time.perf_counter()-timeoutTimer<=self.timeOut:
            logMsg = f"[CLIENT] | {today()} | "
            
            handshake = self.helper.constructParcel(head=bytes([1,0,serverID,len(self.buffer),0,0,0,0,0,0]), data=bytes([]))
            
            logMsg += f"sending  | {handshake[0]} | 14 | {handshake[8:10]}\n"
            Helper.log.append(logMsg)
            logMsg = f"[CLIENT] | {today()} | "

            self.com.sendData(handshake)
            print("Sending handshake (Now waiting for 3 seconds)")
            header, nRx = self.com.getData(10,3)
            
            if header == b'':
                self.com.rx.clearBuffer()
                print(f'Server failed to respond!')
                continue
            
            else:
                logMsg += f"incoming | {header[0]} | 14 | {header[8:10]}\n"
                Helper.log.append(logMsg)
                logMsg = f"[CLIENT] | {today()} | "
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
                logMsg = f"[CLIENT] | {today()} | "
                logMsg += f"sending  | 5 | 14 | {stdMsgs.TIMEOUTMSG[8:10]}\n"
                Helper.log.append(logMsg)
                return False  
        else:
            print("==================================== \nClient handshake finished. \n====================================\n")
            return True

    def killProcess(self):
        self.com.disable()

    def sendMessage(self):
        timeoutTimer = time.perf_counter()
        counter = 0
        # print("Client started sending message")
        while counter < len(self.buffer.values()) and time.perf_counter()-timeoutTimer<self.timeOut:
            datagram = list(self.buffer.values())[counter]

            logMsg = f"[CLIENT] | {today()} | "
            
            # Send current packet
            success = False
            resendTimer = time.perf_counter()
            # print(f"Client is starting to send packet {counter}\n")
            while not success and time.perf_counter() - resendTimer < self.timeResend:
                
                # Noise generator for testing
                mess = datagram[:]
                if self.makeNoise:
                    # This is to introduce noise for testing. Ignore.
                    if random.randint(0,100) < 25:
                        mess = mess[0:4] + bytes([random.randint(0,255)]) + mess[5:]
                        print("\nRandom error has been introduced!\n")
                
                self.com.sendData(mess)
                logMsg += f"sending  | {mess[0]} | {10+mess[5]+4} | {mess[4]} | {mess[4]}/{mess[3]} | {mess[8:10]}\n"
                Helper.log.append(logMsg)
                logMsg = f"[CLIENT] | {today()} | "
                # print("Client is expecting server response  (t4 or t6)")
                resp, nRx = self.com.getData(14, self.timeResend)
                if resp == b'':
                    continue
                logMsg += f"incoming | {resp[0]} | 14 | {resp[8:10]}\n"
                Helper.log.append(logMsg)
                logMsg = f"[CLIENT] | {today()} | "
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
            logMsg += f"sending  | 5 | 14 | {stdMsgs.TIMEOUTMSG[8:10]}\n"
            Helper.log.append(logMsg)  
            self.killProcess()
            print(f"Communication has failed!")
