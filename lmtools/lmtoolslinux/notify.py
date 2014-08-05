import gudev
import glib
#from ..common import vendor_ids

vendor_ids = ['0d28', '0483']


class Listener(object):

    def __init__(self):
        self.client = gudev.Client(["usb/usb_device"])
        self.client.connect("uevent", self.callback, None)

        self.loop = glib.MainLoop()

    def start_listening(self):
        self.loop.run()

    def device_state_changed(self, connected=True):
        #raise NotImplementedError
        pass

    def callback(self, client, action, device, user_data):
        if device.get_property("ID_VENDOR_ID") in vendor_ids:
            self.device_state_changed(action == "add")

if __name__ == "__main__":
    l = Listener()
    l.start_listening()
