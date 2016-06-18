from ui_mainwindow import Ui_MainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from socket import *
import sys
import threading
import time
from src_beacon import Beacon
from src_member_lookup import MemberLookup
from src_receive_message import ReceiveMessage


class ChatONLAN(QMainWindow, Ui_MainWindow):
    PORT = 8000
    MEMBERS = {}
    IP2HOST = {}
    SIGNAL = []
    ONLINE = QTreeWidgetItem()
    FAV = QTreeWidgetItem()
    settings = QSettings('chatonlan', 'config')
    open_chat_list = {}
    notify_offline = {}
    open_socket = {}
    beacon = Beacon()
    member_lookup = MemberLookup()
    receive_message = ReceiveMessage()

    def __init__(self):
        super(ChatONLAN, self).__init__()
        self.setupUi(self)

        QCoreApplication.setOrganizationName('tSibyonixo')
        QCoreApplication.setOrganizationDomain('tSibyonixo.com')
        QCoreApplication.setApplicationName('ChatONLAN')

        self.beacon.start()
        self.member_lookup.lookup.connect(self.setup_member_table)
        self.member_lookup.start()
        self.receive_message.receive.connect(self.display_message)
        self.receive_message.start()

        self.ONLINE.setText(0, 'Online')
        self.FAV.setText(0, 'Favorites')
        self.treeMember.insertTopLevelItem(0, self.ONLINE)
        self.treeMember.insertTopLevelItem(1, self.FAV)

        # signal and slots
        # self.treeMember.currentItemChanged.connect(self.tree_selection)
        self.treeMember.itemDoubleClicked.connect(self.tree_double_clicked)
        self.tabWidget.tabCloseRequested.connect(self.tab_close)
        self.tabWidget.currentChanged.connect(self.tab_changed)

        self.action_About.triggered.connect(self.action_about)
        self.actionUsername.triggered.connect(self.action_change_username)
        self.actionQuit.triggered.connect(self.action_quit)
        self.actionBroadcast.triggered.connect(self.action_broadcast_toggle)

    def closeEvent(self, event):
        for name, sock in self.open_socket.items():
            sock.close()
        self.beacon.terminate()
        self.member_lookup.terminate()
        self.receive_message.terminate()
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

    def action_broadcast_toggle(self, status):
        if status:
            self.beacon.start()
        else:
            self.beacon.terminate()
            self.statusbar.showMessage('Stopping broadcast')

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
            self.SIGNAL.remove(index)
            self.tabWidget.removeTab(index)
            text = text.replace('&', '')
            if text in self.notify_offline:
                self.notify_offline.pop(text)
            self.open_chat_list.pop(text)

    def tab_changed(self, index):
        send = self.tabWidget.widget(index).findChildren(QPushButton, "send")
        if index != 0:
            self.start_notify(index)
            if index not in self.SIGNAL:
                send[0].clicked.connect(self.send_button_pressed)
                send[0].setEnabled(True)
                send_default = self.tabWidget.widget(index).findChildren(QCheckBox, "send_default")
                send_default[0].stateChanged.connect(self.checkbox_state_changed)
                self.SIGNAL.append(index)

    def start_notify(self, index):
        start_notify = threading.Thread(target=self.loop_notify, args=(index,))
        start_notify.setDaemon(True)
        start_notify.start()

    def loop_notify(self, index):
        if index >= 1:
            while True:
                self.notify(index)
                time.sleep(2)
        else:
            pass

    def notify(self, index):
        chat_box = self.tabWidget.widget(index).findChildren(QTextEdit, "chat_box")
        send = self.tabWidget.widget(index).findChildren(QPushButton, "send")
        if index != 0:
            name = self.tabWidget.tabText(index)
            name = name.replace('&', '')
            if name not in self.MEMBERS:
                if name not in self.notify_offline:
                    to_display = '<font color="grey"><b>' + name + ' appears to be offline</b></font>'
                    chat_box[0].append(to_display)
                    send[0].setEnabled(False)
                    self.notify_offline[name] = 'notified'
                else:
                    pass
            if name in self.notify_offline:
                if name in self.MEMBERS:
                    to_display = '<font color="green"><b>' + name + ' has appeared back online</b></font>'
                    chat_box[0].append(to_display)
                    send[0].setEnabled(True)
                    self.notify_offline.pop(name)

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
                # self.tab_changed(index)
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
                # self.tab_changed(index)
                # self.create_socket(name)
            if get_tab_number:
                return index

                # self.create_socket(name)

    def create_socket(self, name):
        run = True
        s_msg = socket(AF_INET, SOCK_STREAM)
        s_msg.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        print('ip: ' + self.MEMBERS[name])
        while run:
            try:
                s_msg.connect((self.MEMBERS[name], 9000))
                self.open_socket[name] = s_msg
                run = False

            except ConnectionRefusedError:
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
                    send.setEnabled(False)
                    break

    def get_name_from_address(self, address):
        print(self.MEMBERS)
        return list(self.MEMBERS.keys())[list(self.MEMBERS.values()).index(address)]

    def display_message(self, address, data, connection):
        # maybe not be used later
        name = self.get_name_from_address(address)
        self.open_socket[name] = connection
        index = self.create_tab(name, False, True)
        chat_box = self.tabWidget.widget(index).findChildren(QTextEdit, "chat_box")
        data = data[:-1]
        data = data[2:]
        to_display = '<font color="red"><b>' + name + '</b>: ' + data + '</font>'
        chat_box[0].append(to_display)

    def checkbox_state_changed(self, state):
        send = self.tabWidget.widget(self.tabWidget.currentIndex()).findChildren(QPushButton, "send")
        if state == 1:
            send[0].setDefault(True)
        else:
            send[0].setDefault(False)

    def send_button_pressed(self):
        self.statusbar.showMessage('Send button pressed')
        # get tab label and from that the IP and send it to the function
        print('sending message')
        address = self.tabWidget.tabText(self.tabWidget.currentIndex())
        address = address.replace('&', '')
        self.create_socket(address)
        find_widget = self.tabWidget.widget(self.tabWidget.currentIndex()).findChildren(QLineEdit, "chat_msg")
        chat_msg = find_widget[0]
        if chat_msg.isModified():
            print('calling send_message')
            self.send_message(chat_msg.text(), address)
            chat_msg.clear()
        else:
            self.statusbar.showMessage('Type a message to send.')

    def send_message(self, msg, to):
        to = to.replace('&', '')
        print(to)
        # self.create_socket(to)
        sock = self.open_socket[to]
        find_widget = self.tabWidget.widget(self.tabWidget.currentIndex()).findChildren(QTextEdit, "chat_box")
        chat_box = find_widget[0]
        to_display = '<font color="blue"><b>' + username + '</b>: ' + msg + '</font>'
        chat_box.append(to_display)
        print('socket.send')
        sock.send(bytes(msg, 'utf-8'))
        sock.close()
        self.open_socket.pop(to)

    def setup_member_table(self, members, add, remove, ip2host):
        self.IP2HOST = ip2host
        self.MEMBERS = members
        row = 0
        child_count = self.ONLINE.childCount()
        exist = False
        for name, ip in add.items():
            host_item = QTreeWidgetItem()
            host_item.setText(0, name)
            host_item.setText(1, ip)
            self.ONLINE.addChild(host_item)

        for name, ip in remove.items():
            for i in range(child_count):
                temp_item = self.ONLINE.child(i)
                if temp_item.text(0) == name:
                    self.ONLINE.takeChild(i)
                i += 1


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
            # w.start_notify()
            w.show()
            sys.exit(app.exec_())
    else:
        # w.start_notify()
        w.show()
        sys.exit(app.exec_())
