import poplib
from email.parser import Parser

import sys

from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QMessageBox, QListWidgetItem
from PyQt5.QtCore import Qt

uiMainWindow, QMainWindow = uic.loadUiType("ui/mainWindow.ui")

class MainWindow(QMainWindow, uiMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setFixedSize(763, 381)
        self.passwd_edit.setEchoMode(QLineEdit.Password)
        self.setWindowIcon(QtGui.QIcon('YoumuAava.ico'))

        self.deleted = []

        self.pageSize = 5
        self.currentPage = 1

        self.numMessages = 0

        self.pop_conn = None
        self.connectStatus = False

        #Кнопки
        self.connectButton.clicked.connect(self.connectButton_clicked)

        self.updateList.clicked.connect(self.updateList_clicked)
        self.nextPage.clicked.connect(self.nextPage_clicked)
        self.prevPage.clicked.connect(self.prevPage_clicked)

        self.dell.clicked.connect(self.dell_clicked)
        self.rset.clicked.connect(self.rset_clicked)

        self.listWidget.itemClicked.connect(self.listItemSelected)


    def rset_clicked(self):
        try:
            self.pop_conn.rset()
            for item in self.deleted:
                item.setForeground(Qt.black)
                print("Пометки сняты")

                self.deleted.clear()
        except Exception as e:
            print(f"Не удалось снять пометки на удаление: {e}")


    def dell_clicked(self):
        selectedItems = self.listWidget.selectedItems()

        if selectedItems:
            for item in selectedItems:
                currItemId = item.text().split(":")[0]
                self.deleted.append(item)

                try:
                    self.pop_conn.dele(int(currItemId))

                except Exception as e:
                    print(f"Ошибка при удалении письма: {e}")

                item.setForeground(Qt.red)
                print("Помечено")


    def listItemSelected(self):
        self.dell.setEnabled(True)
        self.rset.setEnabled(True)


    def closeEvent(self, event):
        close = QMessageBox(self)
        close.setWindowTitle("Выход")
        close.setIcon(QMessageBox.Warning)
        close.setText("Выйти ?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            event.accept()

            if self.pop_conn and self.pop_conn.noop():
                print("pop quit")
                self.pop_conn.quit()
        else:
            event.ignore()


    def nextPage_clicked(self):

        nextP = self.currentPage + self.pageSize
        if nextP <= self.numMessages:

            self.listWidget.clear()
            print("next")

            self.currentPage = nextP

            for i in range(self.currentPage, self.currentPage + self.pageSize - 1):
                #print(i)
                try:
                    response, msgData, octets = self.pop_conn.retr(i)
                    messageText = b'\n'.join(msgData).decode('utf-8')
                    emailMessage = Parser().parsestr(messageText)
                    body = f'{i}: '
                    for part in emailMessage.walk():
                        if part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode('utf-8')

                    item = QListWidgetItem(body)
                    self.listWidget.addItem(item)
                except Exception as e:
                    pass
        else:
            print("next err")


    def prevPage_clicked(self):
        nextP = self.currentPage - self.pageSize
        if nextP >= 1:

            self.listWidget.clear()
            print("prev")

            self.currentPage = nextP

            for i in range(self.currentPage, self.currentPage + self.pageSize):
                #print(i)
                response, msgData, octets = self.pop_conn.retr(i)
                messageText = b'\n'.join(msgData).decode('utf-8')
                emailMessage = Parser().parsestr(messageText)
                body = f'{i}: '
                for part in emailMessage.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode('utf-8')

                item = QListWidgetItem(body)
                self.listWidget.addItem(item)
        else:
            print("prev err")


    def connectButton_clicked(self):
        popSrv = self.srvCombo.currentText()
        login = self.login_edit.text()
        passwd = self.passwd_edit.text()

        try:
            self.pop_conn = poplib.POP3_SSL(popSrv, 995)
            self.pop_conn.user(login)
            self.pop_conn.pass_(passwd)

            #print(self.pop_conn.retr(53))

            self.statusLabel.setText("OK")
            self.statusLabel.setStyleSheet('color: green')

            messageBox = QMessageBox(self)
            messageBox.setWindowTitle("Успех")
            messageBox.setIcon(QMessageBox.Information)
            messageBox.setText("Соединение установлено!")
            messageBox.setDefaultButton(QMessageBox.Ok)
            messageBox.exec_()

            self.connectStatus = True

        except Exception as e:

            self.statusLabel.setText("ERR")
            self.statusLabel.setStyleSheet('color: red')

            messageBox = QMessageBox(self)
            messageBox.setWindowTitle("Неудача")
            messageBox.setIcon(QMessageBox.Warning)
            messageBox.setText("Не удалось установить соединение")
            messageBox.setDefaultButton(QMessageBox.Ok)
            messageBox.exec_()

            self.connectStatus = False

            print(f"Ошибка при подключении к серверу: {e}")

    def updateList_clicked(self):
        if not self.connectStatus:
            print("xui")
        else:
            self.listWidget.clear()

            self.numMessages = len(self.pop_conn.list()[1])
            print(f"Всего писем в почтовом ящике: {self.numMessages}\n")

            if self.numMessages < self.pageSize:
                itemsNum = self.numMessages
            else:
                itemsNum = self.pageSize

            for i in range(self.currentPage, itemsNum + 1):
                #print(i)
                response, msgData, octets = self.pop_conn.retr(i)
                messageText = b'\n'.join(msgData).decode('utf-8')
                emailMessage = Parser().parsestr(messageText)
                body = f'{i}: '
                for part in emailMessage.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode('utf-8')

                item = QListWidgetItem(body)
                print(f"VOT-{body}")
                self.listWidget.addItem(item)

                #print(f"Письмо {i}:\n{body}\n{'-' * 50}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


    #pyinstaller.exe --onefile --windowed --icon=app.ico app.py