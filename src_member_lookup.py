from socket import *
from PyQt5.QtCore import QThread, QSettings, pyqtSignal


class MemberLookup (QThread):
    settings = QSettings('chatonlan', 'config')
    MEMBERS = {}
    IP2HOST = {}

    lookup = pyqtSignal(dict, dict, name='lookup')

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def member_lookup(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind(('<broadcast>', 8000))
        m = s.recvfrom(4096)

        '''

                the beacon sends 'name=xyz&host=abc'
                so the variables variable needs to be split to get the name and the host

        '''

        variables = (str(m[0])).split('&')
        tmp, name = variables[0].split('=')
        tmp, host = variables[1].split('=')
        host = host[:-1]
        print(self.MEMBERS)
        username = self.settings.value('username', type=str)
        if name != username:
            self.MEMBERS[name] = m[1][0]  # store the found member info into the dict
            self.IP2HOST[m[1][0]] = host
        print(len(self.MEMBERS))
        if len(self.MEMBERS) != 0:
            self.lookup.emit(self.MEMBERS, self.IP2HOST)

    def run(self):
        while True:
            self.member_lookup()
