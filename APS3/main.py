# File to make an interface for working with the applications
import tkinter as tk
import tkinter.filedialog as tkfd


#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
# serialName = "COM4"                  # Windows(variacao de)

import time
import os
import math
from helper import Helper
from server import Server
from client import Client
import stdMsgs
import traceback
import numpy as np

import datetime

today = datetime.datetime.today

class Application1:
    def __init__(self, master=None):
        self.master = master
        self.widget1 = tk.Frame(self.master)
        self.widget1.pack()
        self.game = tk.Label(self.widget1, text = 'Por favor, selecione um arquivo para ser enviado:')
        self.game["font"] = ("Verdana", "12", "bold")
        self.game.config(anchor=tk.CENTER)
        self.game.pack()
        self.button = tk.Button(self.widget1)
        self.button["text"] = "Escolher"
        self.button["font"] = ("Cambria", "16", "bold")
        self.button["width"] = 24
        self.button["command"] = self.get_image
        self.button.config(anchor=tk.CENTER)
        self.button.pack()
        self.got_img = False
    
    def get_image(self):
        file = tkfd.askopenfilename(title='Choose a file')
        if file != None:
            self.data = file
            self.master.destroy()

if __name__ == "__main__":
    try:
        
        helper = Helper()

        
        # Interface do Tkinter para pegar arquivo a ser enviado.
        ask_file = tk.Tk()
        ask_file.geometry("900x120")
        app_1 = Application1(ask_file)
        ask_file.mainloop()
        readFile, saveFile = helper.buildPaths(app_1.data)

        # Protocol start:
        # ===========================================

        
        messageDescriptor = {
            'type': 3,
            'sensorID': 69,
            'serverID': 1,
            'fileID': 2,
            'checkpointStep': 10,
        }
        

        with open(readFile, "rb") as File:
            message = File.read()
        
        if len(message) > 255*114:
            print(f"[APPLICATION] There's been a problem! Your selected file exceeds the maximum filesize of {255*114/1000}KB")
            Helper.log.append(f"[APPLICATION] There's been a problem! Your selected file exceeds the maximum filesize of {255*114/1000}KB")
        else:
            messageDict = helper.assembleDataPackets(message, messageDescriptor)

            server = Server("COM4")
            client = Client("COM5")
            client.buffer = messageDict
            server.beginRunning()

            Helper.log.append(f"\n[APPLICATION] | The code used to make this is in the following github repository: https://github.com/CEDipEngineering/DataTransmission\n")
            Helper.log.append(f"[APPLICATION] | The message that will be transmitted has {len(message)} bytes and will be sent over {len(messageDict.values())} data packets\n\n")
            Helper.log.append(f"\n[APPLICATION] | {today()} | Transmission is about to begin!\n")
            
            if client.beginRunning(1):


                print("==================================== \nBeginning communications: \n====================================\n")
                print(f"""
                Size of message (in packets):{len(messageDict.values())}
                Message filename: {readFile}\n
                """)
                startTime = time.perf_counter()
                client.sendMessage()
                endTime = time.perf_counter()


                sentData = np.array(server.messages[69])
                sentData = b"".join(sentData)

                with open(saveFile, "wb") as outFile:
                    outFile.write(sentData)











                # ===========================================
                # Protocol End.
                print("\n-------------------------")
                print("Transmission concluded in {:.02f}s".format(endTime - startTime))
                print(f"Approximated speed: {(len(message)*(1/1000))/(endTime - startTime):.05f}kbps")
                Helper.log.append(f"\n=====================================\n[APPLICATION] | {today()} | Transmission has ended!\n")
                Helper.log.append("[APPLICATION] | Transmission concluded in {:.02f}s\n".format(endTime - startTime))
                Helper.log.append(f"[APPLICATION] | Approximated speed: {(len(message)*(1/1000))/(endTime - startTime):.05f}kbps\n=====================================\n")

                # print("END")
                print("-------------------------")

    except Exception as e:
        print("Occoreu um erro!")
        print("")
        traceback.print_exc()
        print("")
    finally:
        server.killProcess()
        client.killProcess()
        # print(Helper.log)
        with open(f"APS3/logs/log{len(os.listdir(os.path.join(os.getcwd(), 'APS3/logs')))}.txt","w") as f:
            f.write("".join(Helper.log))
