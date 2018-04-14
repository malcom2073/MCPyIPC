import socket
import asyncore
import mcipcparser


class MCIPC(asyncore.dispatcher):
    def __init__(self, name):
        asyncore.dispatcher.__init__(self)
        self.m_name = name
        self.write_buffer = bytearray()
        self.m_socketBuffer = bytearray()
        self.m_packetBuffer = list()
        self.m_publishCallback = None
        self.m_ipcParser = mcipcparser.MCIPCParser()

    def connectToHost(self,address,port):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting to: " + address + ":" + str(port))
        self.connect((address,port))
        self.sendWelcome()
        self.subscribeMessage("core/status")

    def handle_connect(self):
        print("handle_connect()")

    def handle_close(self):
        print("handle_close()")
        self.close()

    def writable(self):
        return (len(self.write_buffer) > 0)

    def sendWelcome(self):
        key = bytearray()
        key.append(0x01)
        key.append(0x02)
        key.append(0x03)
        authstring = '{"type":"auth","key":"' + 'pythontest' + '"}'
        key.extend((len(authstring) + 4).to_bytes(4, byteorder='big', signed=False))
        key.append(0x0)
        key.append(0x0)
        key.append(0x0)
        key.append(0x1)
        key.extend(authstring.encode('latin-1'))
        key.append(0x0)
        key.append(0x0)
        key.append(0x0)
        key.append(0x0)
        self.send(key)

    def readable(self):
        return True

    def handle_write(self):
        sent = self.send(self.write_buffer)
        self.write_buffer = self.write_buffer[sent:]

    def handle_read(self):
        self.m_socketBuffer.extend(self.recv(1024))
        self.checkBuffer()

    def subscribeMessage(self,messageName):
        message = self.generateSubscribeMessage(messageName)
        packet = self.generateCorePacket(message)
        self.write_buffer.extend(packet)

    def generateSubscribeMessage(self,messageName):
        authstring = '{"name":"' + messageName + '"}'
        key = bytearray()
        key.append(0x0)
        key.append(0x0)
        key.append(0x0)
        key.append(0x3)
        key.extend(authstring.encode('latin-1'))
        return key

    def setPublishCallback(self,callback):
        self.m_publishCallback = callback
        self.m_ipcParser.setPublishCallback(callback)

    def generateCorePacket(self,message):
        key = bytearray()
        key.append(0x1)
        key.append(0x2)
        key.append(0x3)
        key.extend(len(message).to_bytes(4, byteorder='big', signed=False))
        key.extend(message)
        key.append(0x0)
        key.append(0x0)
        key.append(0x0)
        key.append(0x0)
        return key

    def checkBuffer(self):
        if len(self.m_packetBuffer) > 0:
            self.m_ipcParser.parsePacket(self.m_packetBuffer[0])
            self.m_packetBuffer.remove(self.m_packetBuffer[0])
        if (len(self.m_socketBuffer) <= 11):
            print("Not enough for auth: " + str(len(self.m_socketBuffer)))
            return False
        if self.m_socketBuffer[0] == 0x1 and self.m_socketBuffer[1] == 0x2 and self.m_socketBuffer[2] == 0x3:
            length = int.from_bytes(self.m_socketBuffer[3:7], byteorder='big', signed=False)
            print("Length: " + str(length))
            if len(self.m_socketBuffer) >= length+11:
                #full packet
                print("Buffer size before: " + str(len(self.m_socketBuffer)))
                packet = self.m_socketBuffer[7:length+7]
                self.m_socketBuffer[0:length+11] = []
                self.m_packetBuffer.append(packet)
                print("JSON: " + str(packet))
                print("Buffer size after: " + str(len(self.m_socketBuffer)))
                self.checkBuffer()

    def loop(self):
        print("Entering loop...")
        asyncore.loop()
        print("Done loop")
