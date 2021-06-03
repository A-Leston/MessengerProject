# by Ariel Leston
# this is the client-side of an instant messenger program

# importing all necessary libraries
import socket
import threading
from tkinter import *

# setting up the server IP/Port info
PORT = 20020
SERVER = "32.210.204.155"  # must be set to the public IP/domain name of the network where server-side code is running
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

# connecting to the server
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect(ADDRESS)


# the first GUI screen, for entering users name
class loginScreen:
    def __init__(self):
        self.Window = Tk()
        self.Window.withdraw()
        self.login = Toplevel()
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(bg='#C4C8E1', width=400, height=300)
        self.pls = Label(self.login, text="Enter a name to login with", justify=CENTER, bg='#C4C8E1', font="Helvetica 14 bold")
        self.pls.place(relheight=0.15, relx=0.3, rely=0.1)
        self.labelName = Label(self.login, text="Name: ", bg='#C4C8E1', fg='black', font="Helvetica 12", pady=0.05)
        self.labelName.place(relheight=0.2, relx=0.1, rely=0.39)
        self.entryName = Entry(self.login, font="Helvetica 14")
        self.entryName.place(relwidth=0.5, relheight=0.12, relx=0.35, rely=0.40)
        self.entryName.focus()
        self.next = Button(self.login, text="Login", bg='#7082F9', font="Helvetica 14 bold", command=lambda: self.nextScreen(self.entryName.get()))
        self.next.place(relx=0.50, rely=0.70)
        self.Window.mainloop()

    # function for the login button to get next screen, and pass the name
    def nextScreen(self, name):
        self.login.destroy()
        self.Window.destroy()
        roomChoiceScreen(name)


# the second screen, asks what room the client wants to go into
# (enter just the number of a room and press join or leave blank and press create)
class roomChoiceScreen:
    def __init__(self, name):
        self.Window = Tk()
        self.Window.withdraw()
        self.roomChoice = Toplevel()
        self.roomChoice.title("Flex-Chat")
        self.roomChoice.resizable(width=False, height=False)
        self.roomChoice.configure(bg='#C4C8E1', width=400, height=300)
        self.text = Label(self.roomChoice, bg='#C4C8E1', fg='black', text="join by room number or create a new room", justify=CENTER, font="Helvetica 12 bold")
        self.text.place(relheight=0.15, relx=0.05, rely=0.08)
        self.roomInfo = Entry(self.roomChoice, font="Helvetica 14")
        self.roomInfo.place(relwidth=0.5, relheight=0.12, relx=0.25, rely=0.25)
        self.roomInfo.focus()
        self.joinButton = Button(self.roomChoice, bg='#7082F9', text="Join room", font="Helvetica 14 bold", command=lambda: self.joinRoom(name, self.roomInfo.get()))
        self.joinButton.place(relx=0.25, rely=0.55)
        self.newButton = Button(self.roomChoice, bg='#7082F9', text="Create room", font="Helvetica 14 bold", command=lambda: self.newRoom(name))
        self.newButton.place(relx=0.55, rely=0.55)
        self.Window.mainloop()

    # the function for new room button, just calls chat with a room number of 0
    # which isnt a room, so it knows to get next free one
    def newRoom(self, name):
        roomInfo = 0
        self.roomChoice.destroy()
        self.Window.destroy()
        chatRoom(name, roomInfo)

    # function for the join room, calls chat with the given room number
    def joinRoom(self, name, roomInfo):
        self.roomChoice.destroy()
        self.Window.destroy()
        chatRoom(name, roomInfo)


# function for the chat room screen
class chatRoom:
    def __init__(self, name, roomInfo):
        self.name = name
        self.roomInfo = roomInfo
        self.Window = Tk()
        self.Window.title("Flex-chat")
        self.Window.resizable(width=True, height=True)
        self.Window.configure(width=470, height=550, bg="#C4C8E1")
        self.labelHead = Label(self.Window, bg="#C4C8E1", fg="black", text=self.name, font="Helvetica 13 bold", pady=5)
        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window, width=450, bg="#7082F9")
        self.line.place(relwidth=1, rely=0.07, relheight=0.012)
        self.textCons = Text(self.Window, width=20, height=2, bg="#C4C8E1", fg="black", font="Helvetica 14", padx=5, pady=5)
        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08)
        self.labelBottom = Label(self.Window, bg="#7082F9", height=80)
        self.labelBottom.place(relwidth=1, rely=0.825)
        self.entryMsg = Entry(self.labelBottom, bg="#C4C8E1", fg="black", font="Helvetica 13")
        self.entryMsg.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.entryMsg.focus()
        self.buttonMsg = Button(self.labelBottom, text="Send", font="Helvetica 10 bold", width=20, bg="#C4C8E1", fg="black", command=lambda: self.sendButton(self.entryMsg.get()))
        self.buttonMsg.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
        self.textCons.config(cursor="arrow")
        scrollbar = Scrollbar(self.textCons)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.config(command=self.textCons.yview)
        self.textCons.config(state=DISABLED)
        receiveThread = threading.Thread(target=self.receive)
        receiveThread.start()
        self.Window.mainloop()

    # function for the send button in chat room, starts a thread that sends the message currently in input box.
    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)
        sendThread = threading.Thread(target=self.sendMessage)
        sendThread.start()

    # receive thread is started when chat room opens, and will receive messages from the server
    def receive(self):
        while True:
            try:
                # the data is encrypted in the format of message>key
                # so it splits at > and uses the key to decode message
                data = clientSocket.recv(1024).decode(FORMAT)
                data = data.split('>')
                key = data[1]
                message = vegenereDecrypt(data[0], key)
                myKey = str(self.name)

                # then checks the message
                if message == "NAME/ROOM":
                    # upon first connection server asks for name/room so it can place the user accordingly
                    # so client will respond with "name/room>key" with "name/room" encrypted
                    text = vegenereEncrypt(str(self.name) + '/' + str(self.roomInfo), myKey)
                    text += '>' + myKey
                    clientSocket.send(text.encode(FORMAT))
                else:
                    # if not a first connection message it puts it on the screen
                    self.textCons.config(state=NORMAL)
                    self.textCons.insert(END, message + "\n\n")
                    self.textCons.config(state=DISABLED)
                    self.textCons.see(END)

            except:
                print("An error occurred in receive thread")
                clientSocket.close()
                break

    # function to send a message with the send button, which runs in a thread
    def sendMessage(self):
        self.textCons.config(state=DISABLED)
        while True:
            message = f"{self.name} : {self.msg}"
            myKey = str(self.name)
            # encodes the message with a vegenere cipher before sending
            text = vegenereEncrypt(message, myKey) + '>' + myKey
            clientSocket.send(text.encode(FORMAT))
            break


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


g = loginScreen()
