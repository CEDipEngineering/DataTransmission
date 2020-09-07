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
        
        helper = Helper()

        with open(readFile, "rb") as File:
            message = File.read()

        messageDict = helper.assembleDataPackets(message, 69)

        server = Server("COM4")
        client = Client("COM5")
        server.beginRunning()
        client.beginRunning()














        # ===========================================
        # Protocol End.
        print("-------------------------")
        #print("Comunicação encerrada com tempo de {}s".format(endTime - startTime))
        print("END")
        print("-------------------------")
        server.killProcess()
        client.killProcess()
    except Exception as e:
        print("Occoreu um erro!")
        print("")
        traceback.print_exc()
        print("")
        server.killProcess()
        client.killProcess()
