import win32con
import win32api
import win32gui
import ctypes
import ctypes.wintypes


class HARDWARESTRUCT(ctypes.Structure):
    _fields_ = [
        ('dbch_size', ctypes.wintypes.DWORD),
        ('dbch_devicetype', ctypes.wintypes.DWORD),
        ('dbch_reserved', ctypes.wintypes.DWORD)
    ]

PHARDWARESTRUCT = ctypes.POINTER(HARDWARESTRUCT)


class Listener(object):

    def __init__(self):
        mapping = {
            win32con.WM_DEVICECHANGE: self.on_device_change
        }
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = mapping
        wc.lpszClassName = 'MyWindowClass'
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        classAtom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(
            classAtom,
            "",
            0,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            hinst,
            None
        )

    def device_state_changed(self, connected=True):
        raise NotImplementedError

    def start_listening(self):
        win32gui.PumpMessages()

    def on_device_change(self, hwnd, uMsg, wParam, lParam):
        if wParam == 0x8000 or wParam == 0x8004:
            data = ctypes.cast(lParam, PHARDWARESTRUCT)
            devicetype = data.contents.dbch_devicetype

            if devicetype == 0x2:
                self.device_state_changed(wParam == 0x8000)
