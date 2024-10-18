import re
import socket
import threading
import time

players = []
games = []
unique_id = 0
lock = threading.Lock()

port = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(('localhost', port))
sock.listen(5)
print(f"listening on port {port}")

# players are shown as player objects. each player has a unique socket for sending msgs.
class player:
    def __init__(self, username, playerSocket: socket.socket):
        self.username = username
        self.playerSocket = playerSocket
        self.state = "loggedin"
    def send(self, msg):
        self.playerSocket.send(msg)
    def setRequest(self, dim):
        self.dim = dim
        self.state = "waiting"
    def setBusy(self):
        self.state = "busy"

# each game is represented by a game object, including its board and related methods. for more info check the report :)
class game:
    cmnd_pat = re.compile(r"MARK ([0-9]),([0-9])")
    def __init__(self, player1: player, player2: player, dimension, gameID):
        self.player1 = player1
        self.player2 = player2
        self.turn = player1
        self.wait = player2
        self.dim = dimension
        self.ID = gameID
        self.end = False
        self.board = [[ '_' for _ in range(self.dim)] for _ in range(self.dim)]

    def display(self):
        s = ""
        for i in range(self.dim):
            for j in range(self.dim):
                s+=self.board[i][j]
                s+=" "
            s+="\n"
        return s

    def checkWin(self, char):
        if self.dim == 3:
            if((self.board[0][0] == self.board[0][1] == self.board[0][2] == char) 
                or (self.board[1][0] == self.board[1][1] == self.board[1][2] == char)
                or (self.board[2][0] == self.board[2][1] == self.board[2][2] == char)
                or (self.board[0][0] == self.board[1][0] == self.board[2][0] == char)
                or (self.board[0][1] == self.board[1][1] == self.board[2][1] == char)
                or (self.board[0][2] == self.board[1][2] == self.board[2][2] == char)
                or (self.board[0][0] == self.board[1][1] == self.board[2][2] == char)
                or (self.board[0][2] == self.board[1][1] == self.board[2][0] == char)):
                return True
        elif self.dim == 4:
            if((self.board[0][0] == self.board[0][1] == self.board[0][2] == char) 
                or (self.board[1][0] == self.board[1][1] == self.board[1][2] == char)
                or (self.board[2][0] == self.board[2][1] == self.board[2][2] == char)
                or (self.board[0][0] == self.board[1][0] == self.board[2][0] == char)
                or (self.board[0][1] == self.board[1][1] == self.board[2][1] == char)
                or (self.board[0][2] == self.board[1][2] == self.board[2][2] == char)
                or (self.board[0][0] == self.board[1][1] == self.board[2][2] == char)
                or (self.board[0][2] == self.board[1][1] == self.board[2][0] == char)
                or (self.board[0][2] == self.board[0][2] == self.board[0][3] == char) 
                or (self.board[1][1] == self.board[1][2] == self.board[1][3] == char)
                or (self.board[2][1] == self.board[2][2] == self.board[2][3] == char)
                or (self.board[0][1] == self.board[1][1] == self.board[2][1] == char)
                or (self.board[0][2] == self.board[1][2] == self.board[2][2] == char)
                or (self.board[0][3] == self.board[1][3] == self.board[2][3] == char)
                or (self.board[0][1] == self.board[1][2] == self.board[2][3] == char)
                or (self.board[0][3] == self.board[1][2] == self.board[2][1] == char)
                or (self.board[1][0] == self.board[1][1] == self.board[1][2] == char) 
                or (self.board[2][0] == self.board[2][1] == self.board[2][2] == char)
                or (self.board[3][0] == self.board[3][1] == self.board[3][2] == char)
                or (self.board[1][0] == self.board[2][0] == self.board[3][0] == char)
                or (self.board[1][1] == self.board[2][1] == self.board[3][1] == char)
                or (self.board[1][2] == self.board[2][2] == self.board[3][2] == char)
                or (self.board[1][0] == self.board[2][1] == self.board[3][2] == char)
                or (self.board[1][2] == self.board[2][1] == self.board[3][0] == char)
                or (self.board[1][1] == self.board[1][2] == self.board[1][3] == char) 
                or (self.board[2][1] == self.board[2][2] == self.board[2][3] == char)
                or (self.board[3][1] == self.board[3][2] == self.board[3][3] == char)
                or (self.board[1][1] == self.board[2][1] == self.board[3][1] == char)
                or (self.board[1][2] == self.board[2][2] == self.board[3][2] == char)
                or (self.board[1][3] == self.board[2][3] == self.board[3][3] == char)
                or (self.board[1][1] == self.board[2][2] == self.board[3][3] == char)
                or (self.board[1][3] == self.board[2][2] == self.board[3][1] == char)):
                return True
        elif self.dim == 5:
            if((self.board[0][0] == self.board[0][1] == self.board[0][2] == self.board[0][3] == char) 
                or (self.board[1][0] == self.board[1][1] == self.board[1][2] == self.board[1][3] == char)
                or (self.board[2][0] == self.board[2][1] == self.board[2][2] == self.board[2][3] == char)
                or (self.board[3][0] == self.board[3][1] == self.board[3][2] == self.board[3][3] == char)
                or (self.board[0][0] == self.board[1][0] == self.board[2][0] == self.board[3][0] == char)
                or (self.board[0][1] == self.board[1][1] == self.board[2][1] == self.board[3][1] == char)
                or (self.board[0][2] == self.board[1][2] == self.board[2][2] == self.board[3][2] == char)
                or (self.board[0][3] == self.board[1][3] == self.board[2][3] == self.board[3][3] == char)
                or (self.board[0][0] == self.board[1][1] == self.board[2][2] == self.board[3][3] == char)
                or (self.board[0][3] == self.board[1][2] == self.board[2][1] == self.board[3][0] == char)
                
                or (self.board[0][1] == self.board[0][2] == self.board[0][3] == self.board[0][4] == char) 
                or (self.board[1][1] == self.board[1][2] == self.board[1][3] == self.board[1][4] == char)
                or (self.board[2][1] == self.board[2][2] == self.board[2][3] == self.board[2][4] == char)
                or (self.board[3][1] == self.board[3][2] == self.board[3][3] == self.board[3][4] == char)
                or (self.board[0][1] == self.board[1][1] == self.board[2][1] == self.board[3][1] == char)
                or (self.board[0][2] == self.board[1][2] == self.board[2][2] == self.board[3][2] == char)
                or (self.board[0][3] == self.board[1][3] == self.board[2][3] == self.board[3][3] == char)
                or (self.board[0][4] == self.board[1][4] == self.board[2][4] == self.board[3][4] == char)
                or (self.board[0][1] == self.board[1][2] == self.board[2][3] == self.board[3][4] == char)
                or (self.board[0][4] == self.board[1][3] == self.board[2][2] == self.board[3][1] == char)
                
                or (self.board[1][0] == self.board[1][1] == self.board[1][2] == self.board[1][3] == char) 
                or (self.board[2][0] == self.board[2][1] == self.board[2][2] == self.board[2][3] == char)
                or (self.board[3][0] == self.board[3][1] == self.board[3][2] == self.board[3][3] == char)
                or (self.board[4][0] == self.board[4][1] == self.board[4][2] == self.board[4][3] == char)
                or (self.board[1][0] == self.board[2][0] == self.board[3][0] == self.board[4][0] == char)
                or (self.board[1][1] == self.board[2][1] == self.board[3][1] == self.board[4][1] == char)
                or (self.board[1][2] == self.board[2][2] == self.board[3][2] == self.board[4][2] == char)
                or (self.board[1][3] == self.board[2][3] == self.board[3][3] == self.board[4][3] == char)
                or (self.board[1][0] == self.board[2][1] == self.board[3][2] == self.board[4][3] == char)
                or (self.board[1][3] == self.board[2][2] == self.board[3][1] == self.board[4][0] == char)
                
                or (self.board[1][1] == self.board[1][2] == self.board[1][3] == self.board[1][4] == char) 
                or (self.board[2][1] == self.board[2][2] == self.board[2][3] == self.board[2][4] == char)
                or (self.board[3][1] == self.board[3][2] == self.board[3][3] == self.board[3][4] == char)
                or (self.board[4][1] == self.board[4][2] == self.board[4][3] == self.board[4][4] == char)
                or (self.board[1][1] == self.board[2][1] == self.board[3][1] == self.board[4][1] == char)
                or (self.board[1][2] == self.board[2][2] == self.board[3][2] == self.board[4][2] == char)
                or (self.board[1][3] == self.board[2][3] == self.board[3][3] == self.board[4][3] == char)
                or (self.board[1][4] == self.board[2][4] == self.board[3][4] == self.board[4][4] == char)
                or (self.board[1][1] == self.board[2][2] == self.board[3][3] == self.board[4][4] == char)
                or (self.board[1][4] == self.board[2][3] == self.board[3][2] == self.board[4][1] == char)):
                return True

        return False

    def changeTurn(self):
        if self.turn == self.player1 :
            self.turn = self.player2
            self.wait = self.player1
        elif self.turn == self.player2 :
            self.turn = self.player1
            self.wait = self.player2
    
    def Move(self, cmnd):
        matches = list(self.cmnd_pat.finditer(cmnd))
        char = ''
        if self.turn == self.player1 :
            char = 'X'
        elif self.turn == self.player2 :
            char = 'O'
        if matches:
            if ((0<=int(matches[0].group(1))) and (int(matches[0].group(1))<self.dim) and (0<=int(matches[0].group(2))) and (int(matches[0].group(2))<self.dim) and (self.board[int(matches[0].group(1))][int(matches[0].group(2))] == '_')):
                self.board[int(matches[0].group(1))][int(matches[0].group(2))] = char
                flag = True
                for i in range(self.dim):
                    for j in range(self.dim):
                        if self.board[i][j] == '_' :
                            flag = False
                
                if self.checkWin(char):
                    self.end = True
                    return ("WIN")
                
                if flag :
                    self.end = True
                    return ("equal")
                # self.changeTurn()
                return ("next")
            else:
                return("THIS CELL CANNOT BE USED")
        else:
            return("INVALID COMMAND")
        
# talk method is called for each thread to serve the corresponding client.
def talk(sock_obj: socket.socket):
    sock_obj.send("TIC TAC TOE \nenter login and your username to login".encode("utf-8"))
    
    while True:
        cmnd = sock_obj.recv(2048)
        cmnd = cmnd.decode("utf-8").split(' ')
        if cmnd[0] == "login":
            flag = False
            p =  None
            for currp in players:
                if currp.username == cmnd[1]:
                    currp.state == "loggedin"
                    currp.send("logged in successfuly.".encode("utf-8"))
                    p = currp
                    flag = True
                    break
            
            if (not flag):
                lock.acquire()
                p = player(cmnd[1], sock_obj)
                players.append(p)
                p.send("account created successfuly".encode("utf-8"))
                lock.release()
            handleCommand(p)
            break
        else:
            sock_obj.send("INVALID COMMAND".encode("utf-8"))

# this method is designed to handle client's requests.
def handleCommand(p : player):
    global unique_id
    sock_obj.send("TIC TAC TOE \nenter play and dimension to start a game. \nenter exit to exit.".encode("utf-8"))

    while True:
        cmnd = sock_obj.recv(2048)
        cmnd = cmnd.decode("utf-8").split(' ')
        if cmnd[0] == "play" :
            dim = int(cmnd[1])
            p.setRequest(dim)
            opp = None
            g = None
            while opp == None :
                for curplayer in players :
                    if curplayer.state == "waiting" and curplayer.username!=p.username and curplayer.dim == p.dim :
                        opp = curplayer
                        break
                if opp != None :
                    g = game(p, opp, p.dim, unique_id)
                    lock.acquire()
                    unique_id+=1
                    lock.release()
                    handleGame(g)

                else :
                    # p.send("there is no other player, please wait".encode("utf-8"))
                    time.sleep(1)

        elif cmnd[0] == "exit" :
            sock_obj.send("disconnect".encode("utf-8"))
            sock_obj.close()
            break
        
        else:
            sock_obj.send("INVALID COMMAND".encode("utf-8"))

# this method runs the game till a win or a tie occurs.
def handleGame(game: game):
    game.player1.setBusy()
    game.player2.setBusy()
    game.player1.send(str("game started! mark cells using MARK i,j command.\n" + game.display()).encode("utf-8"))
    game.player2.send(str("game started! mark cells using MARK i,j command.\n" + game.display()).encode("utf-8"))
    while (game.end == False):
        game.turn.send("Enter move".encode("utf-8"))
        game.wait.send("Please wait".encode("utf-8"))
        cmnd = game.turn.playerSocket.recv(2048).decode("utf-8")
        res = game.Move(cmnd)

        if res == "WIN":
            game.turn.send(str(game.display() + "\n YOU WON :)").encode("utf-8"))
            game.wait.send(str(game.display() + "\n YOU LOST :(").encode("utf-8"))
        elif res == "equal":
            game.turn.send("GAME ENDED, NO WINNER.".encode("utf-8"))
            game.wait.send("GAME ENDED, NO WINNER.".encode("utf-8"))
        elif res == "next":
            game.changeTurn()
            game.turn.send(str("\n" + game.display()).encode("utf-8"))
            game.wait.send(str("\n" + game.display()).encode("utf-8"))
        else:
            game.turn.send("INVALID COMMAND, TRY AGAIN.".encode("utf-8"))
    game.player1.state = "loggedin"
    game.player2.state = "loggedin"

# main loop; connecting each client to the server concurrently.
while True:
    sock_obj, address_info = sock.accept()
    print(f"connected to a client: IP: {address_info}")
    t1 = threading.Thread(target= talk , args= (sock_obj,))
    t1.start()
