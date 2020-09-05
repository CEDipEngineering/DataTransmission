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
        
        if len(head != 10):
            print("Head was not of length 10!")
            return
        if (len(data)>114 and len(data)<0):
            print("Data was of incorrect size! Must be between 0 and 114")
            return 
        if not head is bytes:
            head = bytes([head])
        if not data is bytes:
            data = bytes([data])
        
        message = head + data + bytes([2,1,7,1])
        
    def buildPaths(self, data):
        "data == filepath"
        selectedFile = data
        selectedFileExtension = os.path.splitext(selectedFile)[1]
        saveFileLocation = os.path.splitext(selectedFile)[0] + "Received" + selectedFileExtension
        return selectedFile, saveFileLocation