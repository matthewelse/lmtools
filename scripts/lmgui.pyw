from PySide import QtCore, QtGui
from lmtools import get_connected_mbeds, Listener
import os, sys

class DeviceWidget(QtGui.QWidget):
    def __init__(self, device="Unknown", comport="COM N", driveLetter="F"):
        super(DeviceWidget, self).__init__()

        print device, comport, driveLetter

        mainLayout = QtGui.QHBoxLayout()
        deviceLabel = QtGui.QLabel(device)
        namelabel = QtGui.QLabel(comport)
        driveLabel = QtGui.QLabel(driveLetter)

        mainLayout.addWidget(deviceLabel)
        mainLayout.addWidget(namelabel)
        mainLayout.addWidget(driveLabel)
        self.setLayout(mainLayout)

class USBListener(QtCore.QThread, Listener):
    __errorHappened = False

    def __init__(self, parent=None):
        Listener.__init__(self)
        QtCore.QThread.__init__(self, parent)
        self.exiting = False

    def run(self):
        self.start_listening()

    def serial_device_connected(self):
        self.emit(QtCore.SIGNAL("update()"))


class Window(QtGui.QDialog):
    def __init__(self):
        super(Window, self).__init__()

        # Setup tray icon
        self.createTrayIcon()
        self.trayIcon.show()

        # Set currently connected to an empty set
        self.currentlyConnected = set([])

        # Set up the layout of the widget
            
        self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.WindowStaysOnTopHint)
        self.move(QtCore.QPoint(0, 100))

        self.layout = QtGui.QVBoxLayout()

        self.infoLabel = QtGui.QLabel()
        self.infoLabel.setTextFormat(QtCore.Qt.RichText)
        self.infoLabel.setStyleSheet("font-family: Consolas, Ubuntu Mono, monospace; font-size: 14px;")
        self.infoLabel.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum);
        self.layout.addWidget(self.infoLabel)
        self.setupConnectedBoards()
        self.layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.setLayout(self.layout)

        # Setup and start the listening thread
        self.processThread = USBListener()
        QtCore.QObject.connect(self.processThread, QtCore.SIGNAL("update()"), self, QtCore.SLOT("refreshConnectedBoards()"), QtCore.Qt.QueuedConnection)
        self.processThread.start()

        

    def setupConnectedBoards(self):
        boards = set(get_connected_mbeds())

        if len(boards) == 0:
            self.infoLabel.setText("No Devices Connected")
            return

        max_boardname_length = max([len(board[3]) for board in boards])
        max_comport_length = max([len(board[1]) for board in boards])

        content = ""
        
        for board in boards:
            content += "%s%s%s%s%s<br />" % (board[3], "&nbsp;" * (1 + max_boardname_length - len(board[3])), board[1], "&nbsp;" * (1 + max_comport_length - len(board[1])), board[2])

        content = content[:-6]
        self.infoLabel.setText(content)

    def refreshConnectedBoards(self, maxnew=1):
        newboards = set(get_connected_mbeds())
        print newboards

        if newboards == self.currentlyConnected:
            return

        if len(newboards) == 0:
            self.infoLabel.setParent(None)
            newInfoLabel = QtGui.QLabel("No Devices Connected")
            newInfoLabel.setTextFormat(QtCore.Qt.RichText)
            newInfoLabel.setStyleSheet("font-family: Consolas, Ubuntu Mono, monospace; font-size: 14px;")
            self.infoLabel = newInfoLabel
            self.layout.addWidget(self.infoLabel)
        else:
            max_boardname_length = max([len(board[2]) for board in newboards])
            max_comport_length = max([len(board[0]) for board in newboards])

            content = ""
            
            for board in newboards:
                content += "%s%s%s%s%s<br />" % (board[3], "&nbsp;" * (1 + max_boardname_length - len(board[3])), board[1], "&nbsp;" * (1 + max_comport_length - len(board[1])), board[2])

            content = content[:-6]
            
            self.infoLabel.setText(content)
            self.infoLabel.show()

        insertedboards = newboards - self.currentlyConnected
        removedboards = self.currentlyConnected - newboards
        self.currentlyConnected = newboards

        if len(insertedboards) == 1:
            board = insertedboards.pop()

            if self.messagesEnabled.isChecked():
                icon = QtGui.QSystemTrayIcon.MessageIcon(QtGui.QSystemTrayIcon.Information)
                self.trayIcon.showMessage("%s connected" % (board[3] if board[3] is not None else "Unknown board"), "On %s, connected to drive letter %s" % (board[1], board[2]), icon, 200)
        elif len(removedboards) == 1:
            board = removedboards.pop()

            if self.messagesEnabled.isChecked():
                icon = QtGui.QSystemTrayIcon.MessageIcon(QtGui.QSystemTrayIcon.Information)
                self.trayIcon.showMessage("%s disconnected" % (board[3] if board[3] is not None else "Unknown board"), "It was on %s, connected to drive letter %s" % (board[1], board[2]), icon, 200)


    def refreshAction(self):
        self.refreshConnectedBoards()

    def end(self):
        # End everything gracefully
        self.processThread.exit()
        sys.exit()
        

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)

        widgetAction = QtGui.QWidgetAction(self.trayIconMenu)
        widgetAction.setDefaultWidget(DeviceWidget())
        self.trayIconMenu.addAction(widgetAction)
        self.trayIconMenu.addSeparator()
        self.messagesEnabled = QtGui.QAction("Enable Notifications", self, checkable=True)
        self.trayIconMenu.addAction(self.messagesEnabled)
        self.trayIconMenu.addSeparator()        
        self.trayIconMenu.addAction(QtGui.QAction("Refresh", self, triggered=self.refreshAction))
        self.trayIconMenu.addAction(QtGui.QAction("Quit", self, triggered=self.end))

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)

        mbed_icon_location = os.path.join(os.path.dirname(sys.modules["lmtools"].__file__), "data/mbed-logo-blue.png")

        self.trayIcon.setIcon(QtGui.QIcon(mbed_icon_location))

if __name__ == '__main__':
 
    import sys
 
    app = QtGui.QApplication(sys.argv)
 
    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        QtGui.QMessageBox.critical(None, "Systray",
                "I couldn't detect any system tray on this system.")
        sys.exit(1)
 
    QtGui.QApplication.setQuitOnLastWindowClosed(False)
 
    window = Window()
    window.show()

    sys.exit(app.exec_())
