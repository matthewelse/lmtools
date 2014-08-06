from pyudev import Context, Monitor
from pyudev import MonitorObserver
from time import sleep
from ..common import vendor_ids


class Listener(object):

    def __init__(self):
        self.context = Context()
        self.monitor = Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='usb')
        self.observer = MonitorObserver(
            self.monitor, callback=self.event_handler, name="blahblah")
        self.observer.daemon = True

    def start_listening(self):
        self.observer.start()

    def event_handler(self, device):
        d = {k: device[k] for k in device}

        if 'ID_VENDOR_ID' not in d or 'ACTION' not in d:
            return

        if d['ID_VENDOR_ID'] not in vendor_ids:
            return

        sleep(2) # Give the drive time to mount
        self.device_state_changed(d['ACTION'])

    def device_state_changed(self, action):
        raise NotImplementedError
