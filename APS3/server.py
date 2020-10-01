import threading
from enlace import enlace
import stdMsgs
import time
from helper import Helper
import datetime

today = datetime.datetime.today


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
        self.counter = 0
        self.timeResend = 3
        self.timeOut = 20


    def threadJob(self):
        while self.running:
            if self.threadActive:
                # Get header for message;
                logMsg = f"[SERVER] | {today()} | "

                self.com.rx.clearBuffer()
                # print("Server is receiving next header")
                header, nRx = self.com.getData(10)
                if not self.running:
                    break
                # print(f"Server received header: {header}")
                # print(f"Server is idle: {self.idle}")
                sensorID = header[1]
                serverID = header[2]
                sizeOfWholeMessage = header[3] # Size of message in packets
                packetPosition = header[4]
                commState = header[0]
                if self.idle:    
                # For now, the remaining bytes are 0
                    Helper.log.append("[SERVER] Server received idle message\n")
                    logMsg += f"incoming | {commState} | 14 | {header[8:10]}\n"
                    Helper.log.append(logMsg)
                    logMsg = f"[SERVER] | {today()} | "

                    if commState == 1 and serverID != self.id:

                        # Message is not for me :(
                        print(f"Server {self.id} has received a message meant for server {serverID}")
                        self.com.rx.clearBuffer()
                        
                    elif commState == 1:

                        self.com.sendData(stdMsgs.SERVERALIVEMSG)
                        logMsg += f"sending  | {stdMsgs.SERVERALIVEMSG[0]} | {len(stdMsgs.SERVERALIVEMSG)} | {stdMsgs.SERVERALIVEMSG[8:10]}\n"
                        Helper.log.append(logMsg)
                        self.com.rx.clearBuffer()
                        self.idle = False
                        Helper.log.append("[SERVER] Server is no longer idle!\n")
                        self.counter = 0
                        self.timeOutTimer = time.perf_counter()
                        self.timeResendTimer = time.perf_counter()

                    time.sleep(0.5)
                    continue

                else:
                    if time.perf_counter() - self.timeOutTimer <= self.timeOut:
                        if time.perf_counter() - self.timeResendTimer <= self.timeResend:
                            if commState == 3:
                                
                                # print(f"""timerStates: 
                                #         timerTimeout: {time.perf_counter()-self.timeOutTimer}
                                #         timerResend: {time.perf_counter()-self.timeResendTimer}""")
                                # Analyse Header to know whats going on;
                                #   Check message ID, to know if it's a new message.
                                #   Any message that is being received, should be of same size every time,
                                #   And also be of index +1 over the last message of that ID
                                messageSize = header[5]
                                
                                logMsg += f"incoming | {commState} | {10+messageSize+4} | {packetPosition} | {self.counter}/{sizeOfWholeMessage} | {header[8:10]}\n"
                                Helper.log.append(logMsg)
                                logMsg = f"[SERVER] | {today()} | "

                                infoIsValid = False
                                if packetPosition > sizeOfWholeMessage:
                                    print(f"The server has found an error!")
                                    print(f"The indicated packet position {packetPosition} is outside the bounds of the message (length {sizeOfWholeMessage})")
                                    self.com.rx.clearBuffer()
                                    mess = self.helper.constructParcel(head=bytes([6,0,0,0,0,0,self.counter,0,0,0]), data=bytes([]))
                                    self.com.sendData(mess)
                                    logMsg += f"sending  | 6 | 14 | {mess[8:10]}\n"
                                    Helper.log.append(logMsg)
                                    continue

                                # Info will be valid if either it's a new message's packet or if it's the next packet of a known message
                                if sensorID in self.messages.keys():
                                    if self.counter == packetPosition:
                                        infoIsValid = True
                                elif sensorID not in self.messages.keys() and packetPosition == 0:
                                    infoIsValid = True
                                    self.messages[sensorID] = [[] for i in range(sizeOfWholeMessage)]

                                

                                # Use header info to decide whether or not to continue
                                if not infoIsValid:
                                    print(f"An error has ocurred with this data packet!")                        
                                    print(f"The server has responded and is now expecting a repeat of the message.")
                                    self.com.rx.clearBuffer()
                                    mess = self.helper.constructParcel(head=bytes([6,0,0,0,0,0,self.counter,0,0,0]), data=bytes([]))
                                    self.com.sendData(mess)
                                    logMsg += f"sending  | 6 | 14 | {mess[8:10]}\n"
                                    Helper.log.append(logMsg)
                                    continue
                                # Empty buffer before going back to waiting
                                
                                # Could implement data verification here:

                                # If message is valid, try to read it.
                                content, nRx = self.com.getData(messageSize)
                            



                                # Read EOP, just cause (Should be the same everytime, but whatever);
                                EOP, nRx = self.com.getData(4)
                                # print(f"Is the EOP right?: {EOP == bytes([255,176,255,176])}")
                                # Make sure that the buffer is Empty before next message starts (?)
                                if not self.com.rx.getIsEmpty():
                                    self.com.rx.clearBuffer()

                                expectedCRC = self.helper.CRC(header[:8] + bytes([0,0]) + content + EOP)
                                # print(f"\nCRC: {expectedCRC}\nheaderCRC: {header[8:10]}\n")
                                if expectedCRC != header[8:10]:
                                    # print(f"CRC checked successfuly")
                                    print(f"An error has ocurred with this data packet!")                        
                                    print(f"The server has responded and is now expecting a repeat of the message.")
                                    self.com.rx.clearBuffer()
                                    mess = self.helper.constructParcel(head=bytes([6,0,0,0,0,0,self.counter,0,0,0]), data=bytes([]))
                                    self.com.sendData(mess)
                                    logMsg += f"sending  | 6 | 14 | {mess[8:10]}\n"
                                    Helper.log.append(logMsg)
                                    continue

                                # Store value;
                                self.messages[sensorID][self.counter] = content
                                self.counter += 1

                                # print(f"Current message buffer on server:{[x for x in self.messages[sensorID]]}")
                                print(f"Message transmission in progress: {100*self.counter/sizeOfWholeMessage:.02f}% ({self.counter}/{sizeOfWholeMessage} packets)")


                                # Enviar mensagem de sucesso
                                succ = self.helper.constructParcel(head=bytes([4,0,0,0,0,0,0,self.counter,0,0]), data=bytes([]))
                                self.com.sendData(succ)
                                logMsg += f"sending  | 4 | 14 | {succ[8:10]}\n"
                                Helper.log.append(logMsg)
                                self.timeOutTimer = time.perf_counter()
                                self.timeResendTimer = time.perf_counter()
                            else:
                                time.sleep(1)
                                continue
                        else:
                            succ = self.helper.constructParcel(head=bytes([4,0,0,0,0,0,0,self.counter,0,0]), data=bytes([]))
                            self.com.sendData(succ)
                            logMsg += f"sending  | 4 | 14 | {succ[8:10]}\n"
                            Helper.log.append(logMsg)                            
                            self.timeResendTimer = time.perf_counter()
                            continue
                    else:
                        self.idle = True
                        self.com.sendData(stdMsgs.TIMEOUTMSG)
                        logMsg += f"sending  | 5 | 14 | {stdMsgs.TIMEOUTMSG[8:10]}\n"
                        Helper.log.append(logMsg)  
                        continue



    def beginRunning(self):
        self.com.enable()
        self.idle = True
        self.threadActive = True
        self.running = True
        self.thread = threading.Thread(target = self.threadJob, args=())
        self.thread.start()

    def killProcess(self):
        self.running = False
        self.threadActive = False
        self.com.disable()
    