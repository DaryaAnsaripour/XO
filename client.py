import socket
import sys
import threading


class Client:
    # initialize clients socket and generate 2 threads for concurrent send and recv procedures.
    def __init__(self, port: int = 9999):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect(("localhost", port))
        self.mutex = threading.Lock()
        self.exited = False
        self.recv_thread = None
        self.send_thread = None

    # handle printing with a lock. (avoid possible race conditions between send and recv threads.)   
    def printt(self, msg):
        self.mutex.acquire()
        print(msg)
        self.mutex.release()
    
    # start recv and send threads to communicate with server
    def run(self):
        self.login()
        self.send_thread = threading.Thread(target= self.send_handler, args=())
        self.recv_thread = threading.Thread(target= self.recv_handler, args=())
        self.send_thread.start()
        self.recv_thread.start()

        self.send_thread.join()
        self.send_thread.join()

    # login procedure
    def login(self):
        response = self._sock.recv(2048).decode("utf-8")
        self.printt(response)
        response = "INVALID COMMAND"
        while response == "INVALID COMMAND" :
            login_info = input().strip()
            self._sock.send(login_info.encode("utf-8"))
            response = self._sock.recv(2048).decode("utf-8")
            self.printt(response)
        response = self._sock.recv(2048).decode("utf-8")
        self.printt(response)

    # send method to send client's msgs to server.
    def send_handler(self):
        while True:
            command = input().strip()
            if command == "exit":
                self.exited = True
                self.recv_thread.join()
                self._sock.close()
                return
            self._sock.send(command.encode("utf-8"))
    
    # recv method for receiving messages from server
    def recv_handler(self):
        while not self.exited:
            response = self._sock.recv(2048).decode("utf-8")
            print(response)

if __name__ == "__main__":
    client = Client()
    client.run()