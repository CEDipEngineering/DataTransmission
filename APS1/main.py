# File to make an interface for working with the applications
import tkinter as tk
import tkinter.filedialog as tkfd


#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
# serialName = "COM4"                  # Windows(variacao de)

from enlace import *
import time
import os
import math

class Application1:
    def __init__(self, master=None):
        self.master = master
        self.widget1 = tk.Frame(self.master)
        self.widget1.pack()
        self.game = tk.Label(self.widget1, text = 'Por favor, selecione uma imagem para ser enviada:')
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

        # Interface do Tkinter
        ask_file = tk.Tk()
        ask_file.geometry("900x120")
        app_1 = Application1(ask_file)
        ask_file.mainloop()

        saveImage = os.getcwd() + "//APS1//imgs//received.png"


        print("Estabelecendo enlace client:")
        comClient = enlace("COM5")
        comClient.enable()
        print("Enlace e comunicação client habilitada!")

        print("Estabelecendo enlace server:")
        comServer = enlace("COM4")
        comServer.enable()
        print("Enlace e comunicação server habilitada!")

        with open(app_1.data, "rb") as file1:
            clientBuffer = file1.read()
            savedLen = len(clientBuffer)

        n_bytes = math.floor((math.log2(len(clientBuffer))/8)) + 1
        len_bytes = (len(clientBuffer).to_bytes(n_bytes,'little'))
        clientBuffer = bytes([n_bytes]) + len_bytes + clientBuffer

        #print("clientBuffer:" + str(clientBuffer)[0:100] + "...")

        print("Tamanho da imagem:" + str(len(clientBuffer)))

        startTime = time.perf_counter()
        comClient.sendData(clientBuffer)
        sizeOfSize, nRx = comServer.getData(1)
        sizeOfSize = int.from_bytes(sizeOfSize,"little")
        sizeOfImage, nRx = comServer.getData(sizeOfSize)
        sizeOfImage = int.from_bytes(sizeOfImage,"little")
        imageData, nRx = comServer.getData(sizeOfImage)
        #print(str(imageData[0:100]) + "...")

        feedback = sizeOfSize.to_bytes(1,"little") + sizeOfImage.to_bytes(sizeOfSize,"little")
        comServer.sendData(feedback)

        receivedSizeofSize, nRx = comClient.getData(1)
        receivedSizeofImage, nRx = comClient.getData(int.from_bytes(receivedSizeofSize, "little"))
        receivedSizeofImage = (int.from_bytes(receivedSizeofImage, "little"))
        print("A imagem enviada tinha " + str(savedLen) + " bytes")
        print("A mensagem de feedback disse que tinha " + str(receivedSizeofImage) + " bytes")

        if receivedSizeofImage == savedLen:
            print("A transmissão foi bem sucedida!")
        else:
            print("Fracasso na transmissão!")
        endTime = time.perf_counter()


        with open(saveImage, "wb") as file2:
            file2.write(imageData)


        

        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada com tempo de {}s".format(endTime - startTime))
        print("-------------------------")
        comServer.disable()
        comClient.disable()
    except Exception as e:
        print("Occoreu um erro!")
        print("")
        print(e)
        print("")
        comServer.disable()
        comClient.disable()
