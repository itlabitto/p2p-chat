# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chat.ui'
#
# Created: Mon Apr 10 16:19:55 2017
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Chat(object):
    def setupUi(self, Chat):
        Chat.setObjectName(_fromUtf8("Chat"))
        Chat.resize(801, 650)
        self.centralwidget = QtGui.QWidget(Chat)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.frame_connection = QtGui.QFrame(self.centralwidget)
        self.frame_connection.setGeometry(QtCore.QRect(10, 20, 771, 91))
        self.frame_connection.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_connection.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_connection.setObjectName(_fromUtf8("frame_connection"))
        self.label_ip = QtGui.QLabel(self.frame_connection)
        self.label_ip.setGeometry(QtCore.QRect(0, 10, 16, 20))
        self.label_ip.setObjectName(_fromUtf8("label_ip"))
        self.label_nickname = QtGui.QLabel(self.frame_connection)
        self.label_nickname.setGeometry(QtCore.QRect(410, 10, 61, 16))
        self.label_nickname.setObjectName(_fromUtf8("label_nickname"))
        self.label_port = QtGui.QLabel(self.frame_connection)
        self.label_port.setGeometry(QtCore.QRect(190, 10, 31, 16))
        self.label_port.setObjectName(_fromUtf8("label_port"))
        self.connect_button = QtGui.QPushButton(self.frame_connection)
        self.connect_button.setGeometry(QtCore.QRect(660, 10, 83, 24))
        self.connect_button.setObjectName(_fromUtf8("connect_button"))
        self.label_listen = QtGui.QLabel(self.frame_connection)
        self.label_listen.setEnabled(False)
        self.label_listen.setGeometry(QtCore.QRect(290, 10, 41, 16))
        self.label_listen.setObjectName(_fromUtf8("label_listen"))
        self.line_ip = QtGui.QLineEdit(self.frame_connection)
        self.line_ip.setGeometry(QtCore.QRect(20, 10, 161, 20))
        self.line_ip.setInputMask(_fromUtf8(""))
        self.line_ip.setObjectName(_fromUtf8("line_ip"))
        self.line_port = QtGui.QLineEdit(self.frame_connection)
        self.line_port.setGeometry(QtCore.QRect(220, 10, 61, 20))
        self.line_port.setObjectName(_fromUtf8("line_port"))
        self.line_port_listen = QtGui.QLineEdit(self.frame_connection)
        self.line_port_listen.setEnabled(False)
        self.line_port_listen.setGeometry(QtCore.QRect(340, 10, 61, 20))
        self.line_port_listen.setObjectName(_fromUtf8("line_port_listen"))
        self.line_nickname = QtGui.QLineEdit(self.frame_connection)
        self.line_nickname.setGeometry(QtCore.QRect(480, 10, 161, 20))
        self.line_nickname.setObjectName(_fromUtf8("line_nickname"))
        self.disconnect_button = QtGui.QPushButton(self.frame_connection)
        self.disconnect_button.setGeometry(QtCore.QRect(670, 60, 83, 24))
        self.disconnect_button.setObjectName(_fromUtf8("disconnect_button"))
        self.sysinfo_button = QtGui.QPushButton(self.frame_connection)
        self.sysinfo_button.setEnabled(False)
        self.sysinfo_button.setGeometry(QtCore.QRect(570, 60, 83, 24))
        self.sysinfo_button.setObjectName(_fromUtf8("sysinfo_button"))
        self.frame_chat = QtGui.QFrame(self.centralwidget)
        self.frame_chat.setGeometry(QtCore.QRect(9, 129, 511, 411))
        self.frame_chat.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_chat.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_chat.setObjectName(_fromUtf8("frame_chat"))
        self.list_chat = QtGui.QListWidget(self.frame_chat)
        self.list_chat.setGeometry(QtCore.QRect(10, 10, 491, 381))
        self.list_chat.setObjectName(_fromUtf8("list_chat"))
        self.frame_users = QtGui.QFrame(self.centralwidget)
        self.frame_users.setGeometry(QtCore.QRect(530, 130, 241, 411))
        self.frame_users.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_users.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_users.setObjectName(_fromUtf8("frame_users"))
        self.list_users = QtGui.QListWidget(self.frame_users)
        self.list_users.setGeometry(QtCore.QRect(10, 10, 221, 381))
        self.list_users.setObjectName(_fromUtf8("list_users"))
        self.frame_send = QtGui.QFrame(self.centralwidget)
        self.frame_send.setGeometry(QtCore.QRect(10, 549, 731, 71))
        self.frame_send.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_send.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_send.setObjectName(_fromUtf8("frame_send"))
        self.send_button = QtGui.QPushButton(self.frame_send)
        self.send_button.setGeometry(QtCore.QRect(490, 10, 83, 24))
        self.send_button.setObjectName(_fromUtf8("send_button"))
        self.help_button = QtGui.QPushButton(self.frame_send)
        self.help_button.setEnabled(False)
        self.help_button.setGeometry(QtCore.QRect(640, 10, 83, 24))
        self.help_button.setObjectName(_fromUtf8("help_button"))
        self.msg_text = QtGui.QLineEdit(self.frame_send)
        self.msg_text.setGeometry(QtCore.QRect(10, 10, 461, 31))
        self.msg_text.setObjectName(_fromUtf8("msg_text"))
        Chat.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(Chat)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 801, 19))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        Chat.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(Chat)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        Chat.setStatusBar(self.statusbar)

        self.retranslateUi(Chat)
        QtCore.QObject.connect(self.msg_text, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.send_button.click)
        QtCore.QObject.connect(self.line_nickname, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.connect_button.click)
        QtCore.QObject.connect(self.msg_text, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.msg_text.clear)
        QtCore.QMetaObject.connectSlotsByName(Chat)

    def retranslateUi(self, Chat):
        Chat.setWindowTitle(_translate("Chat", "Peer-to-Peer Chat", None))
        self.label_ip.setText(_translate("Chat", "IP", None))
        self.label_nickname.setText(_translate("Chat", "Nickname", None))
        self.label_port.setText(_translate("Chat", "Port", None))
        self.connect_button.setText(_translate("Chat", "Connect", None))
        self.label_listen.setText(_translate("Chat", "Listen", None))
        self.line_ip.setText(_translate("Chat", "localhost", None))
        self.line_port.setText(_translate("Chat", "9876", None))
        self.disconnect_button.setText(_translate("Chat", "Disconnect", None))
        self.sysinfo_button.setText(_translate("Chat", "SysInfo", None))
        self.send_button.setText(_translate("Chat", "Send", None))
        self.help_button.setText(_translate("Chat", "Help", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Chat = QtGui.QMainWindow()
    ui = Ui_Chat()
    ui.setupUi(Chat)
    Chat.show()
    sys.exit(app.exec_())

