from socket import *
from PyQt5.QtCore import QThread, pyqtSignal


class ReceiveMessage (QThread):
    receive_message_signal = pyqtSignal(str, bytes, name='receive_message_signal')
    receive_file_signal = pyqtSignal(str, bytes, name='receive_file_signal')

    def __init__(self):
        self.r_msg = socket(AF_INET, SOCK_STREAM)
        self.r_msg.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.r_msg.bind(('', 9000))
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def receive_message(self):
        self.r_msg.listen(20)
        print('Receiving...')
        connection, address = self.r_msg.accept()
        if address:
            # self.open_socket[name] = connection
            data = connection.recvfrom(4096)
            print(address[0])
            print(str(data[0]))
            rcv = str(data[0])
            rcv = rcv[:-1]
            rcv = rcv[2:]
            if rcv.startswith('#FILE'):
                self.receive_file_signal.emit(address[0], data[0])
            # send a byte instead and convert it to str lin the function.
            else:
                self.receive_message_signal.emit(address[0], data[0])
            print('Received.')
            connection.close()

    def run(self):
        while True:
            self.receive_message()
