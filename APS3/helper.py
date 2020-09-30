import os
import crcmod


class Helper:
    def __init__(self):
        Helper.log = ["=======================\nThis is the log!\nMessages will be formatted according to the logs.pdf file\nand will be preceeded by the name of the instance who saved the message.\n=======================\n"]
        self.EOP = bytes([255,176,255,176])

    def constructParcel(self, head, data):
        
        if len(head) != 10:
            print("Head was not of length 10!")
            return
        if (len(data)>114 and len(data)<0):
            print("Data was of incorrect size! Must be between 0 and 114")
            return 
        # if not (head is bytes):
        #     head = bytes([head])
        # if not (data is bytes):
        #     data = bytes([data])
        
        # Implement CRC here:
        
        message = head + data + self.EOP
        extra = self.CRC(message)

        message = head[:8] + extra + data + self.EOP 


        return message

    def buildPaths(self, data):
        "data == filepath"
        selectedFile = data
        selectedFileExtension = os.path.splitext(selectedFile)[1]
        saveFileLocation = os.path.splitext(selectedFile)[0] + "Received" + selectedFileExtension
        return selectedFile, saveFileLocation

    def breakData(self, data):
        packetAmount = len(data)//114 + 1

        allData = [[] for i in range(packetAmount)]
        content = data[:]
        for i in range(packetAmount):
            if i<packetAmount-1:
                allData[i] = content[0:114]
                content = content[114:]
            else:
                allData[i] = content[:]            


        # print(f"PacketAmount: {packetAmount}")
        # print(f"Alldata: {allData}")
        # print(f"len(Alldata): {[len(a) for a in allData]}")


        return allData

    def assembleDataPackets(self, data, messagedescriptor):
        """
        messageDescriptor = {
            'type': 1-6,
            'sensorID': 0-255,
            'serverID': 0-255,
            'fileID': 0-255,
            'checkpointStep': 0-255,
        }
        """
        out = {}
        content = self.breakData(data)
        chkStp = messagedescriptor['checkpointStep']
        for i, e in enumerate(content):
            head = bytes([
                messagedescriptor['type'],
                messagedescriptor['sensorID'],
                messagedescriptor['serverID'],
                len(content),
                i])
            if messagedescriptor['type'] == 1:
                head += bytes([messagedescriptor['fileID']])
            else:
                head+= bytes([len(e)])
            head += bytes([(i//chkStp)*chkStp])
            if(i==0):
                head += bytes([i])
            else:
                head += bytes([i-1])
            head += bytes([0, 0])
            if e is bytes:
                out[str(i)] = self.constructParcel(head = head,data = e)
            else:
                out[str(i)] = self.constructParcel(head = head,data = bytes(e))
        
        return out
    
    def CRC(self, message):
        return crcmod.mkCrcFun(0x11021, initCrc=0, xorOut=0xFFFFFFFF)((message)).to_bytes(2,'big')



