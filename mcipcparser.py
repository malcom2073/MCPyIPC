
import json

class MCIPCParser():
    def __init__(self):
        self.m_publishCallback = None

    def parsePacket(self,buffer):
        type = int.from_bytes(buffer[0:4], byteorder='big', signed=False)
        if type == 1:
            #Auth message
            print("Got auth")
        elif type == 3:
            #Subscribe message
            print("Subscibe Message")
        elif type == 7:
            #Publish message
            print("Publish Message")
            if self.m_publishCallback != None:
                jsonbytes = json.loads(buffer[4:])
                self.m_publishCallback(jsonbytes['name'],jsonbytes['payload'])
        else:
            print("Unknown type: " + str(type))

    def setPublishCallback(self,callback):
        self.m_publishCallback = callback
