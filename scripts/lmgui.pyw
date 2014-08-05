from PySide import QtCore, QtGui
from lmtools import get_connected_mbeds, Listener
import os
import sys


class USBListener(QtCore.QThread, Listener):
    __errorHappened = False

    def __init__(self, parent=None):
        Listener.__init__(self)
        QtCore.QThread.__init__(self, parent)
        self.exiting = False

    def run(self):
        self.start_listening()

    def device_state_changed(self, connected=True):
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

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.move(QtCore.QPoint(0, 100))

        self.layout = QtGui.QVBoxLayout()

        self.infoLabel = QtGui.QLabel()
        self.infoLabel.setTextFormat(QtCore.Qt.RichText)
        self.infoLabel.setStyleSheet(
            "font-family: Consolas, Ubuntu Mono, monospace; font-size: 14px;")
        self.infoLabel.setSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        self.infoLabel.mousePressEvent = self.mousePressEvent
        self.layout.mousePressEvent = self.mousePressEvent
        self.infoLabel.mouseMoveEvent = self.mouseMoveEvent

        self.mouseDown = False

        self.layout.addWidget(self.infoLabel)
        self.update_info_label()
        self.layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.setLayout(self.layout)

        # Setup and start the listening thread
        self.processThread = USBListener()
        QtCore.QObject.connect(self.processThread, QtCore.SIGNAL(
            "update()"), self, QtCore.SLOT("refreshConnectedBoards()"), QtCore.Qt.QueuedConnection)
        self.processThread.start()

    def update_info_label(self, boards=None):
        if boards is None:
            boards = get_connected_mbeds()

        if len(boards) == 0:
            self.infoLabel.setText("No Devices Connected")
            return

        max_boardname_length = max([len(v["name"]) for v in boards.values()])
        max_comport_length = max([len(v["port"]) for v in boards.values()])

        content = ""

        for k, v in boards.items():
            content += "%s%s%s%s%s<br />" % (v["name"], "&nbsp;" * (1 + max_boardname_length - len(
                v["name"])), v["port"], "&nbsp;" * (1 + max_comport_length - len(v["port"])), v["mount_point"])

        content = content[:-6]
        self.infoLabel.setText(content)

    def refreshConnectedBoards(self, maxnew=1):
        newboards = get_connected_mbeds()

        if newboards == self.currentlyConnected:
            return

        self.update_info_label()

        newset = set(newboards)
        currentset = set(self.currentlyConnected)

        insertedboards = newset - currentset
        removedboards = currentset - newset

        if len(insertedboards) == 1:
            board = insertedboards.pop()

            if self.messagesEnabled.isChecked():
                icon = QtGui.QSystemTrayIcon.MessageIcon(
                    QtGui.QSystemTrayIcon.Information)
                connected_board = newboards[board]
                self.trayIcon.showMessage("%s disconnected" % (connected_board["name"] if connected_board[
                                          "name"] is not None else "Unknown board"), "It was on %s, connected to drive letter %s" % (connected_board["port"], connected_board["mount_point"]), icon, 200)
        elif len(removedboards) == 1:
            board = removedboards.pop()

            if self.messagesEnabled.isChecked():
                icon = QtGui.QSystemTrayIcon.MessageIcon(
                    QtGui.QSystemTrayIcon.Information)
                disconnected_board = self.currentlyConnected[board]
                self.trayIcon.showMessage("%s connected" % (disconnected_board["name"] if disconnected_board[
                                          "name"] is not None else "Unknown board"), "On %s, connected to drive letter %s" % (disconnected_board["port"], disconnected_board["mount_point"]), icon, 200)

        self.currentlyConnected = newboards

    def refreshAction(self):
        self.refreshConnectedBoards()

    def end(self):
        # End everything gracefully
        self.processThread.exit()
        sys.exit()

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)

        self.messagesEnabled = QtGui.QAction(
            "Enable Notifications", self, checkable=True)
        self.trayIconMenu.addAction(self.messagesEnabled)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(
            QtGui.QAction("Refresh", self, triggered=self.refreshAction))
        self.trayIconMenu.addAction(
            QtGui.QAction("Quit", self, triggered=self.end))

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)

        mbed_icon_location = os.path.join(
            os.path.dirname(sys.modules["lmtools"].__file__), "data/mbed-logo-blue.png")

        self.trayIcon.setIcon(QtGui.QIcon(mbed_icon_location))

    def mousePressEvent(self, event):
        print "mouse down!"
        self.mouseDown = True
        self.offset = event.pos()

    def mouseReleaseEvent(self, event):
        self.mouseDown = False

    def mouseMoveEvent(self, event):
        if self.mouseDown:
            self.move(0, event.globalY() - self.offset.y())


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
