# by Ariel Leston
# this is the server-side of an instant messenger program

# importing all necessary libraries
import socket
import threading

# setting up server port and IP which will just be the hosts public IP
PORT = 20020
SERVER = "0.0.0.0"
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

# creating a multi-dimensional array of rooms, this is how it will filter people into specific rooms
# ideally this would be done dynamically as the program needs more rooms, allowing it to make as many as it needs
# but due to time limitations, I just pre-made some rooms to show proof of concept
names, room1, room2, room3, room4, room5 = [], [], [], [], [], []
rooms = [room1, room2, room3, room4, room5]

# creating the server socket for clients to connect to
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(ADDRESS)


# starting the chat loop, where server accepts connections and starts handling messages from them
def startChat():
    print("server is working on " + str(socket.gethostbyname(socket.gethostname())))
    serverSocket.listen()
    running = True

    # any message sent by server and not from a client will be encrypted with this key instead, as it has no originator
    myKey = "server"

    # this keeps track of the next empty room, every time someone presses create room it increments by 1
    nextRoomSlot = 0

    while running:
        # accepts a connection
        clientSocket, address = serverSocket.accept()
        try:
            # send initial message to get the clients name and room number
            # also encrypting it in name/room>key format with vegenere cipher
            text = vegenereEncrypt("NAME/ROOM", myKey)
            text += ">" + myKey
            clientSocket.send(text.encode(FORMAT))

            # it receives a response in the same format so it splits by / and >
            data = clientSocket.recv(1024).decode(FORMAT)
            print(data)
            data = data.split('>')
            info = data[0].split('/')
            key = data[1]

            # then adds all the info to its variables for that client
            name = vegenereDecrypt(info[0], key)
            roomNumb = int(info[1])
            names.append(name)

            # it checks if the client wants an emtpy room or a specific room, and places them accordingly
            if roomNumb == 0:
                print("new room")
                nextRoomSlot += 1
                print("making room " + str(nextRoomSlot))
                roomNumb = nextRoomSlot
            else:
                print("joining room " + str(roomNumb))
            rooms[roomNumb - 1].append(clientSocket)

            # then sends a confirmation message to the room showing they joined and confirming what room number
            print(f"{name} has connected to server")
            text = vegenereEncrypt(f"{name} has joined room {roomNumb}", myKey)
            text += '>' + myKey
            broadcastMessage(clientSocket, text.encode(FORMAT))
            text = vegenereEncrypt("Connection established", myKey)
            text += '>' + myKey
            clientSocket.send(text.encode(FORMAT))

            # then starts a thread to handle that client
            thread = threading.Thread(target=handle, args=(clientSocket, address))
            thread.start()
        except:
            broadcastMessage(clientSocket, f" {address} has left the room".encode(FORMAT))
            clientSocket.close()

        print(f"active connections = {threading.activeCount() - 1}")


# when a client sends something, the server will receive using this function and then send that message to broadcast
def handle(clientSocket, address):
    print(f"now handling connection with {address}")
    connected = True
    try:
        while connected:
            message = clientSocket.recv(1024)
            sender = clientSocket
            broadcastMessage(sender, message)
    except:
        pass
    print(f"connection with {address} closed")
    clientSocket.close()


# this will send the given message to every user in the same room of the message sender
def broadcastMessage(sender, message):
    senderRoom = -1
    for currentRoom in rooms:
        for currentSocket in currentRoom:
            if currentSocket == sender:
                senderRoom = currentRoom

    if senderRoom is not -1:
        for userSocket in senderRoom:
            userSocket.send(message)


# slightly modified vegenere cipher for encryption, works by ascii numbers and indexes
def vegenereEncrypt(text, key):
    loopedKey = ""
    while len(loopedKey) < len(text):
        for element in key:
            loopedKey += element
    loopedKeyList = list(loopedKey)
    textList = list(text)
    newText = ""

    for i in range(len(textList)):
        if 65 <= ord(textList[i]) <= 122:
            letterIndex = ord(textList[i]) - 65
            keyIndex = ord(loopedKeyList[i]) - 65
            newIndex = letterIndex + keyIndex
            if newIndex > 57:
                newIndex -= 58
            newLetter = chr(newIndex + 65)
            newText += newLetter
        else:
            newText += str(textList[i])

    return newText


# the inverse of encrypt function to allow decyrption
def vegenereDecrypt(text, key):
    loopedKey = ""
    while len(loopedKey) < len(text):
        for element in key:
            loopedKey += element
    loopedKeyList = list(loopedKey)
    textList = list(text)
    newText = ""

    for i in range(len(textList)):
        if 65 <= ord(textList[i]) <= 122:
            letterIndex = ord(textList[i]) - 65
            keyIndex = ord(loopedKeyList[i]) - 65
            newIndex = letterIndex - keyIndex
            if newIndex < 0:
                newIndex += 58
            newLetter = chr(newIndex + 65)
            newText += newLetter
        else:
            newText += textList[i]

    return newText

# starts
startChat()
