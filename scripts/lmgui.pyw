from PySide import QtCore, QtGui
from lmtools import get_connected_mbeds, Listener
import os
import sys


class USBListener(QtCore.QThread, Listener):
    def __init__(self, parent=None):
        Listener.__init__(self)
        QtCore.QThread.__init__(self, parent)

        self.connection_event = None

    def run(self):
        self.start_listening()

    def device_state_changed(self, connected="add"):
        print "Hello!"
        self.connection_event = connected
        self.emit(QtCore.SIGNAL("updateBoards()"))

    def get_event(self):
        return self.connection_event


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
        self.updateInfoLabel()
        self.layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.setLayout(self.layout)

        self.notification_thread = USBListener()
        QtCore.QObject.connect(self.notification_thread, QtCore.SIGNAL(
            "updateBoards()"), self, QtCore.SLOT("refreshBoards()"), QtCore.Qt.QueuedConnection)
        self.notification_thread.start()

    def refreshBoards(self):
        # Show notification if enabled

        newboards = get_connected_mbeds()
        event_type = self.notification_thread.get_event()

        added_mbeds = set(newboards) - set(self.boards)
        removed_mbeds = set(self.boards) - set(newboards)

        changed_mbeds = added_mbeds | removed_mbeds

        print changed_mbeds
        print self.messagesEnabled.isChecked()

        if self.messagesEnabled.isChecked() and len(changed_mbeds) == 1:
            # Show a message :)
            serial_number = changed_mbeds.pop()
            if event_type == "add":
                self.trayIcon.showMessage("%s connected" % newboards[serial_number]['name'],
                    "Connected to %s\r\nMounted at %s" % (newboards[serial_number]['port'], newboards[serial_number]['mount_point']))
                print "%s connected" % newboards[serial_number]['name']
                print "Connected to %s\r\nMounted at %s" % (newboards[serial_number]['port'], newboards[serial_number]['mount_point'])

        if len(newboards) == 0:
            self.infoLabel.setText("No Devices Connected")
            self.boards = newboards
            return

        max_boardname_length = max([len(v["name"]) for v in newboards.values()])
        max_comport_length = max([len(v["port"]) for v in newboards.values()])

        content = ""

        for k, v in newboards.items():
            content += "%s%s%s%s%s<br />" % (v["name"], "&nbsp;" * (1 + max_boardname_length - len(
                v["name"])), v["port"], "&nbsp;" * (1 + max_comport_length - len(v["port"])), v["mount_point"])

        content = content[:-6]
        self.infoLabel.setText(content)
        self.boards = newboards

    def updateInfoLabel(self, boards=None):
        if boards is None:
            boards = get_connected_mbeds()

        self.boards = boards

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

    def end(self):
        # End everything gracefully
        self.notification_thread.exit()
        sys.exit()

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)

        self.messagesEnabled = QtGui.QAction(
            "Enable Notifications", self, checkable=True)
        self.trayIconMenu.addAction(self.messagesEnabled)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(
            QtGui.QAction("Refresh", self, triggered=self.refreshBoards))
        self.trayIconMenu.addAction(
            QtGui.QAction("Quit", self, triggered=self.end))

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)

        mbed_icon_location = os.path.join(
            os.path.dirname(sys.modules["lmtools"].__file__), "data/mbed-logo-blue.png")

        self.trayIcon.setIcon(QtGui.QIcon(mbed_icon_location))

    def mousePressEvent(self, event):
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
