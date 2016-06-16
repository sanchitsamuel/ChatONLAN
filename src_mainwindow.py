from ui_mainwindow import Ui_MainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from socket import *
import time
import threading
import sys
from src_beacon import Beacon
from src_member_lookup import MemberLookup


class ChatONLAN(QMainWindow, Ui_MainWindow):
    PORT = 8000
    MEMBERS = {}
    IP2HOST = {}
    running = True
    ONLINE = QTreeWidgetItem()
    FAV = QTreeWidgetItem()
    settings = QSettings('chatonlan', 'config')
    open_chat_list = {}
    open_socket = {}
    beacon = Beacon()
    member_lookup = MemberLookup()

    def __init__(self):
        super(ChatONLAN, self).__init__()
        self.setupUi(self)

        QCoreApplication.setOrganizationName('tSibyonixo')
        QCoreApplication.setOrganizationDomain('tSibyonixo.com')
        QCoreApplication.setApplicationName('ChatONLAN')

        self.beacon.start()
        self.member_lookup.lookup.connect(self.setup_member_table)
        self.member_lookup.start()

        self.ONLINE.setText(0, 'Online')
        self.FAV.setText(0, 'Favorites')
        self.treeMember.insertTopLevelItem(0, self.ONLINE)
        self.treeMember.insertTopLevelItem(1, self.FAV)

        # signal and slots
        self.treeMember.currentItemChanged.connect(self.tree_selection)
        self.treeMember.itemDoubleClicked.connect(self.tree_double_clicked)
        self.tabWidget.tabCloseRequested.connect(self.tab_close)
        # self.tabWidget.currentChanged.connect(self.tab_changed)

        self.action_About.triggered.connect(self.action_about)
        self.actionUsername.triggered.connect(self.action_change_username)
        self.actionQuit.triggered.connect(self.action_quit)

    def closeEvent(self, event):
        for name, sock in self.open_socket.items():
            sock.close()
        self.beacon.terminate()
        self.member_lookup.terminate()
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
            self.settings.setValue('username', text)

    def action_quit(self):
        self.close()

    def tab_close(self, index):
        text = self.tabWidget.tabText(index)
        if index != 0:
            self.tabWidget.removeTab(index)
            text = text.replace('&', '')
            self.open_chat_list.pop(text)

    def tab_changed(self, index):
        if index != 0:
            send = self.tabWidget.widget(index).findChildren(QPushButton, "send")
            send[0].clicked.connect(self.send_button_pressed)
            send_default = self.tabWidget.widget(index).findChildren(QCheckBox, "send_default")
            send_default[0].stateChanged.connect(self.checkbox_state_changed)

    def tree_double_clicked(self, item, column):
        text = item.text(0)
        if text != 'Online':
            if text != 'Favorites':
                self.create_tab(text, True)

    def create_tab(self, name, switch=False, get_tab_number=False):
        if name in self.open_chat_list:
            index = self.open_chat_list[name]
            if switch:
                self.tabWidget.setCurrentIndex(index)
                self.tab_changed(index)
            if get_tab_number:
                return index
        else:
            chat_box = QTextEdit()
            chat_box.setObjectName('chat_box')
            chat_box.setReadOnly(True)
            chat_msg = QLineEdit()
            chat_msg.setObjectName('chat_msg')
            msg_send = QPushButton('Send')
            msg_send.setObjectName('send')
            send_default = QCheckBox('Enter to send message')
            send_default.setObjectName('send_default')

            chat_widget = QWidget()

            hBox_layout = QHBoxLayout()
            chat_tab_layout = QVBoxLayout()
            hBox_layout.addWidget(chat_msg)
            hBox_layout.addWidget(msg_send)
            chat_tab_layout.addWidget(chat_box)
            chat_tab_layout.addLayout(hBox_layout)
            chat_tab_layout.addWidget(send_default)

            chat_widget.setLayout(chat_tab_layout)
            chat_widget.setTabOrder(chat_box, chat_msg)
            chat_widget.setTabOrder(chat_msg, msg_send)

            index = self.tabWidget.addTab(chat_widget, name)
            self.open_chat_list[name] = index
            if switch:
                self.tabWidget.setCurrentIndex(index)
                self.tab_changed(index)
                # self.create_socket(name)
            if get_tab_number:
                return index

                # self.create_socket(name)

    def create_socket(self, name):
        run = True
        s_msg = socket(AF_INET, SOCK_STREAM)
        while run:
            try:
                s_msg.connect((self.MEMBERS[name], 9000))
                self.open_socket[name] = s_msg
                run = False

            except:
                reply = QMessageBox.information(self, 'Socket Error',
                                                "Would you like to retry?", QMessageBox.Yes |
                                                QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    continue
                else:
                    find_widget = self.tabWidget.widget(self.tabWidget.currentIndex()).findChildren(QTextEdit,
                                                                                                    "chat_box")
                    chat_box = find_widget[0]
                    to_display = '<font color="red">' + \
                                 'Unable to connect to the user, please close the tab and retry' + '</font>'
                    chat_box.append(to_display)
                    send = self.tabWidget.widget(self.tabWidget.currentIndex()).findChildren(QPushButton,
                                                                                             "send")
                    # send.setDisabled(True)
                    break

    def get_name_from_address(self, address):
        return list(self.MEMBERS.keys())[list(self.MEMBERS.values()).index(address)]

    def start_receive(self):
        recv = threading.Thread(target=self.receive_message)
        # recv.setDaemon(True)
        recv.start()

    def receive_message(self):
        r_msg = socket(AF_INET, SOCK_STREAM)
        r_msg.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        r_msg.bind(('', 9000))
        r_msg.listen(20)
        while True:
            connection, address = r_msg.accept()
            if address:
                name = self.get_name_from_address(address[0])
                print(name)
                if name:
                    self.open_socket[name] = connection
                    data, address = connection.recvfrom(4096)
                    self.display_message(data, name)

    def display_message(self, data, name):
        # maybe not be used later
        index = self.create_tab(name, False, True)
        chat_box = self.tabWidget.widget(index).findChildren(QTextEdit, "chat_box")
        chat_box[0].append(str(data))

    def checkbox_state_changed(self, state):
        send = self.tabWidget.widget(self.tabWidget.currentIndex()).findChildren(QPushButton, "send")
        if state == 1:
            send[0].setDefault(True)
        else:
            send[0].setDefault(False)

    def send_button_pressed(self):
        # get tab label and from that the IP and send it to the function
        address = self.tabWidget.tabText(self.tabWidget.currentIndex())
        find_widget = self.tabWidget.widget(self.tabWidget.currentIndex()).findChildren(QLineEdit, "chat_msg")
        chat_msg = find_widget[0]
        if chat_msg.isModified():
            self.send_message(chat_msg.text(), address)
            chat_msg.clear()
        else:
            self.statusbar.showMessage('Type a message to send.')

    def send_message(self, msg, to):
        to = to.replace('&', '')
        sock = self.open_socket[to]
        find_widget = self.tabWidget.widget(self.tabWidget.currentIndex()).findChildren(QTextEdit, "chat_box")
        chat_box = find_widget[0]
        to_display = '<font color="blue"><b>' + username + '</b>: ' + msg + '</font>'
        chat_box.append(to_display)
        sock.send(bytes(msg, 'utf-8'))

    '''

    def member_lookup(self):
        username = self.settings.value('username', type=str)
        while 1:
            s = socket(AF_INET, SOCK_DGRAM)
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.bind(('<broadcast>', 8000))
            m = s.recvfrom(4096)

            '

                the beacon sends 'name=xyz&host=abc'
                so the variables variable needs to be split to get the name and the host

            '

            variables = (str(m[0])).split('&')
            tmp, name = variables[0].split('=')
            tmp, host = variables[1].split('=')
            host = host[:-1]
            username = self.settings.value('username', type=str)
            if name != username:
                self.MEMBERS[name] = m[1][0]  # store the found member info into the dict
                self.IP2HOST[m[1][0]] = host
            self.setup_member_table()

    def start_member_lookup(self):
        lookup = threading.Thread(target=self.member_lookup)
        lookup.setDaemon(True)
        lookup.start()

    '''

    def setup_member_table(self, members, ip2host):
        self.IP2HOST = ip2host
        row = 0
        child_count = self.ONLINE.childCount()
        # child_count += 1
        exist = False
        for name, ip in members.items():
            for i in range(child_count):
                # exist = False
                temp_item = self.ONLINE.child(i)
                if temp_item.text(0) == name:
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
            w.start_receive()

            w.show()
            sys.exit(app.exec_())
    else:
        w.start_receive()

        w.show()
        sys.exit(app.exec_())
