from socket import *
from PyQt5.QtCore import QThread, pyqtSignal


class ReceiveMessage (QThread):
    receive = pyqtSignal(str, str, socket, name='receive')

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def receive_message(self):
        r_msg = socket(AF_INET, SOCK_STREAM)
        r_msg.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        r_msg.bind(('', 9000))
        r_msg.listen(20)
        print('Receiving...')
        connection, address = r_msg.accept()
        if address:
                # self.open_socket[name] = connection
            data = connection.recvfrom(4096)
            print(address[0])
            print(str(data[0]))
                # self.display_message(data, name)
            self.receive.emit(address[0], str(data[0]), connection)
            print('Received.')

    def run(self):
        while True:
            self.receive_message()
