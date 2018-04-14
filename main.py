import mcipc

def incomingPublishMessage(name,payload):
    print("Incoming publish")
    print("Name: " + name)
    print("Payload: " + str(payload))

m_ipc = mcipc.MCIPC("pymcipc")
m_ipc.setPublishCallback(incomingPublishMessage)
m_ipc.connectToHost("127.0.0.1",12345);
m_ipc.loop()


