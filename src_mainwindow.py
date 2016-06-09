from ui_mainwindow import Ui_MainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from socket import *
import time
import threading
import sys


class ChatONLAN(QMainWindow, Ui_MainWindow):
    PORT = 8000
    MEMBERS = {}
    ONLINE = QTreeWidgetItem()
    FAV = QTreeWidgetItem()
    settings = QSettings('chatonlan', 'config')

    def __init__(self):
        super(ChatONLAN, self).__init__()
        self.setupUi(self)

        QCoreApplication.setOrganizationName('tSibyonixo')
        QCoreApplication.setOrganizationDomain('tSibyonixo.com')
        QCoreApplication.setApplicationName('ChatONLAN')

        self.ONLINE.setText(0, 'Online')
        self.FAV.setText(0, 'Favorites')
        self.treeMember.insertTopLevelItem(0, self.ONLINE)
        self.treeMember.insertTopLevelItem(1, self.FAV)

        # signal and slots
        self.treeMember.currentItemChanged.connect(self.tree_selection)

        self.action_About.triggered.connect(self.action_about)
        self.actionUsername.triggered.connect(self.action_change_username)
        self.actionQuit.triggered.connect(self.action_quit)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit ?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def action_about(self):
        QMessageBox.information(self, 'About',
                                "This is <b>ChatONLAN</b> ver 1.", QMessageBox.Ok,
                                QMessageBox.Ok)

    def tree_selection(self, current, previous):
        self.statusbar.showMessage(current.text(1))

    def action_change_username(self, line=None):
        old = self.settings.value('username', type=str)
        if not line:
            line = 'Enter your username (current= ' + old + '):'
        text, ok = QInputDialog.getText(self, 'Username', line)

        if ok:
            # self.le1.setText(str(text))
            print(text)
            self.settings.setValue('username', text)

    def action_quit(self):
        self.close()

    def broadcast(self):
        username = self.settings.value('username', type=str)
        msg = "name="+username+"&host=" + gethostname()
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
        username = self.settings.value('username', type=str)
        while 1:
            s = socket(AF_INET, SOCK_DGRAM)
            s.bind(('<broadcast>', 8000))
            m = s.recvfrom(4096)

            '''

                the beacon sends 'name=xyz&host=abc'
                so the variables variable needs to be split to get the name and the host

            '''

            variables = (str(m[0])).split('&')
            tmp, name = variables[0].split('=')  # feature not yet implemented
            tmp, host = variables[1].split('=')
            print(name)
            # host = host[:-1]
            if name != username:
                self.MEMBERS[name] = m[1][0]  # store the found member info into the dict
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
        for name, ip in self.MEMBERS.items():
            for i in range(child_count):
                # exist = False
                print('checking at: ' + str(i) + ': ' + name)
                temp_item = self.ONLINE.child(i)
                if temp_item.text(0) == name:
                    print('found: ' + name)
                    exist = True
                i += 1
            if exist:
                exist = False
                pass
            else:
                exist = False
                host_item = QTreeWidgetItem()
                host_item.setText(0, name)
                host_item.setText(1, ip)
                self.ONLINE.addChild(host_item)
                print('inserting: ' + name)
                row += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QMainWindow()
    w = ChatONLAN()

    username = w.settings.value('username', type=str)
    if not username:
        w.action_change_username('Create new username:')
        username = w.settings.value('username', type=str)
        if not username:
            sys.exit(app.exit(0))
        else:
            w.start_beacon()
            w.start_member_lookup()

            w.show()
            sys.exit(app.exec_())
    else:
        w.start_beacon()
        w.start_member_lookup()

        w.show()
        sys.exit(app.exec_())
