# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI/MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(558, 316)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setObjectName("tabWidget")
        self.tabMembers = QtWidgets.QWidget()
        self.tabMembers.setObjectName("tabMembers")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tabMembers)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.treeMember = QtWidgets.QTreeWidget(self.tabMembers)
        self.treeMember.setHeaderHidden(True)
        self.treeMember.setObjectName("treeMember")
        self.treeMember.headerItem().setText(0, "1")
        self.treeMember.header().setVisible(False)
        self.horizontalLayout_2.addWidget(self.treeMember)
        self.tabWidget.addTab(self.tabMembers, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 558, 30))
        self.menubar.setObjectName("menubar")
        self.menuOption = QtWidgets.QMenu(self.menubar)
        self.menuOption.setObjectName("menuOption")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionBroadcast = QtWidgets.QAction(MainWindow)
        self.actionBroadcast.setCheckable(True)
        self.actionBroadcast.setChecked(True)
        self.actionBroadcast.setObjectName("actionBroadcast")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.action_About = QtWidgets.QAction(MainWindow)
        self.action_About.setObjectName("action_About")
        self.actionUsername = QtWidgets.QAction(MainWindow)
        self.actionUsername.setObjectName("actionUsername")
        self.menuOption.addAction(self.actionBroadcast)
        self.menuOption.addAction(self.actionUsername)
        self.menuOption.addSeparator()
        self.menuOption.addAction(self.actionQuit)
        self.menuHelp.addAction(self.action_About)
        self.menubar.addAction(self.menuOption.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ChatONLAN"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMembers), _translate("MainWindow", "Members"))
        self.menuOption.setTitle(_translate("MainWindow", "Optio&n"))
        self.menuHelp.setTitle(_translate("MainWindow", "He&lp"))
        self.actionBroadcast.setText(_translate("MainWindow", "&Broadcast"))
        self.actionQuit.setText(_translate("MainWindow", "&Quit"))
        self.action_About.setText(_translate("MainWindow", "&About"))
        self.actionUsername.setText(_translate("MainWindow", "Username"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

