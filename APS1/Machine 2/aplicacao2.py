#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import os
import math

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
#serialName = "COM5"                  # Windows(variacao de)

def main(serialName):
    try:

        # Essa main tenta receber uma imagem de tamanhho desconhecido, 


        
        # Sempre salvo a imagem recebida no mesmo diretório que a imagem enviada.
        saveImage = os.getcwd() + "//imgs//received.png"

        print("Estabelecendo enlace:")
        com = enlace(serialName)
        print("Enlace estabelecido com sucesso!")

        print("Habilitando comunicação:")
        com.enable()
        print("Comunicação habilitada!")

        
        print("Starting wait")
        time.sleep(25)
        print("Wait done!")


        allData, nRx = com.getData(-1)
        print(allData)
        print("")


        sizeOfSize = allData[-1]
        print("Size of Size:" + str(sizeOfSize))
        sizeOfImage = allData[-sizeOfSize-1:-1]
        print("sizeOfImage:" + str(sizeOfImage))
        sizeOfImage = int.from_bytes(sizeOfImage, "little")
        print("sizeOfImage:" + str(sizeOfImage))
        imageData = allData[0:sizeOfImage]
        print(imageData)


        with open(saveImage, "wb") as file2:
            file2.write(imageData)

    
        
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
    except Exception as e:
        print("Occoreu um erro!")
        print("")
        print(e)
        print("")
        com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main(serialName = "COM5")
    

