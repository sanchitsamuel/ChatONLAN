from socket import *
from PyQt5.QtCore import QThread, QSettings, pyqtSignal


class MemberLookup(QThread):
    settings = QSettings('chatonlan', 'config')
    MEMBERS = {}
    IP2HOST = {}
    TEMP = {}
    ADD = {}
    REMOVE = {}
    x = 0

    lookup = pyqtSignal(dict, dict, dict, dict, name='lookup')

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
        username = self.settings.value('username', type=str)
        if name != username:
            self.TEMP[name] = m[1][0]  # store the found member info into the dict
            self.IP2HOST[m[1][0]] = host

    def compare(self):
        self.ADD = {k: self.TEMP[k] for k in self.TEMP if k not in self.MEMBERS}  # temp - members (new online)
        self.REMOVE = {k: self.MEMBERS[k] for k in self.MEMBERS if k not in self.TEMP}  # members - temp (new offline)
        self.MEMBERS = {k: self.MEMBERS.get(k, k in self.MEMBERS or self.ADD[k]) for k in
                        set(self.MEMBERS) | set(self.ADD)}
        self.MEMBERS = {k: self.MEMBERS[k] for k in self.MEMBERS if k not in self.REMOVE}

        self.lookup.emit(self.MEMBERS, self.ADD, self.REMOVE, self.IP2HOST)
        self.x = 0
        self.TEMP = {}

    def run(self):
        while True:
            self.member_lookup()
            if self.x == 4:
                self.compare()
            self.x += 1