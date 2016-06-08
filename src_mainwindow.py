from ui_mainwindow import Ui_MainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from socket import *
import time
import threading
import sys


class ChatONLAN(QMainWindow, Ui_MainWindow):
    PORT = 8000
    MEMBERS = {}
    ONLINE = QTreeWidgetItem()
    FAV = QTreeWidgetItem()

    def __init__(self):
        super(ChatONLAN, self).__init__()
        self.setupUi(self)

        self.ONLINE.setText(0, 'Online')
        self.FAV.setText(0, 'Favorites')
        self.treeMember.insertTopLevelItem(0, self.ONLINE)
        self.treeMember.insertTopLevelItem(1, self.FAV)

        # signal and slots
        self.treeMember.currentItemChanged.connect(self.tree_selection)

        self.action_About.triggered.connect(self.about)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit ?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def about(self):
        QMessageBox.information(self, 'About',
                                "This is <b>ChatONLAN</b> ver 1.", QMessageBox.Ok,
                                QMessageBox.Ok)

    def tree_selection(self, current, previous):
        self.statusbar.showMessage(current.text(1))

    def broadcast(self):
        msg = "name=user&host="+gethostname()
        broadc = socket(AF_INET, SOCK_DGRAM)
        broadc.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        broadc.settimeout(15)
        broadc.sendto(bytes(msg, "utf-8"), ('<broadcast>', 8000))
        broadc.close()

    def beacon(self):
        while 1:
            self.broadcast()
            time.sleep(2)

    def start_beacon(self):
        beacon = threading.Thread(target=self.beacon)
        beacon.setDaemon(True)
        beacon.start()

    def member_lookup(self):
        self.MEMBERS = {}
        while 1:
            s = socket(AF_INET, SOCK_DGRAM)
            s.bind(('<broadcast>', 8000))
            m = s.recvfrom(4096)

            '''

                the beacon sends 'name=xyz&host=abc'
                so the variables variable needs to be split to get the name and the host

            '''

            variables = (str(m[0])).split('&')
            tmp, name = variables[0].split('=')      # feature not yet implemented
            tmp, host = variables[1].split('=')
            host = host[:-1]
            if host != gethostname():
                self.MEMBERS[host] = m[1][0]                # store the found member info into the dict
            self.setup_member_table()

    def start_member_lookup(self):
        lookup = threading.Thread(target=self.member_lookup)
        lookup.setDaemon(True)
        lookup.start()

    def setup_member_table(self):
        row = 0
        child_count = self.ONLINE.childCount()
        # child_count += 1
        print('Child count: ' + str(child_count))
        print(self.MEMBERS)
        print('Length of member dict: ' + str(len(self.MEMBERS)))
        exist = False
        for host, ip in self.MEMBERS.items():
            for i in range(child_count):
                # exist = False
                print('checking at: ' + str(i) + ': ' + host)
                temp_item = self.ONLINE.child(i)
                if temp_item.text(0) == host:
                    print('found: ' + host)
                    exist = True
                i += 1
            if exist:
                exist = False
                pass
            else:
                exist = False
                host_item = QTreeWidgetItem()
                host_item.setText(0, host)
                host_item.setText(1, ip)
                self.ONLINE.addChild(host_item)
                print('inserting: ' + host)
                row += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QMainWindow()
    w = ChatONLAN()

    w.start_beacon()
    w.start_member_lookup()

    w.show()
    sys.exit(app.exec_())
