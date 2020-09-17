import os

class Helper:
    def __init__(self):
        self.storage = {}

    def getStorage(self):
        return self.storage
    
    def retrieveFromStorage(self, key):
        try:
            return self.storage
        except KeyError as e:
            print("Key not found", e)
            return

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
        
        message = head + data + bytes([255,176,255,176])
        
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
                i,
                messagedescriptor['fileID'],
                (i//chkStp)*chkStp])
            if(i==0):
                head += bytes([i])
            else:
                head += bytes([i-1])
            head += bytes([len(e), 255])
            if e is bytes:
                out[str(i)] = self.constructParcel(head = head,data = e)
            else:
                out[str(i)] = self.constructParcel(head = head,data = bytes(e))
        
        return out
    


