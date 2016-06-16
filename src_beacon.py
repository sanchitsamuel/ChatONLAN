from socket import *
from PyQt5.QtCore import QThread, QSettings


class Beacon(QThread):
    settings = QSettings('chatonlan', 'config')

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def broadcast(self):
        username = self.settings.value('username', type=str)
        msg = "name=" + username + "&host=" + gethostname()
        broadc = socket(AF_INET, SOCK_DGRAM)
        broadc.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        broadc.settimeout(15)
        broadc.sendto(bytes(msg, "utf-8"), ('<broadcast>', 8000))
        broadc.close()
        self.sleep(2)

    def run(self):
        while True:
            self.broadcast()
