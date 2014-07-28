import win32con, win32api, win32gui, ctypes, ctypes.wintypes

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
            win32con.WM_DEVICECHANGE: self.onDeviceChange
            }
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = mapping
        wc.lpszClassName = 'MyWindowClass'
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        classAtom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow (
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

    def serial_device_connected(self):
        raise NotImplementedError

    def start_listening(self):
        win32gui.PumpMessages()

    def onDeviceChange(self, hwnd, uMsg, wParam, lParam):
        if wParam == 0x8000 or wParam == 0x8004:
            data = ctypes.cast(lParam, PHARDWARESTRUCT)
            devicetype = data.contents.dbch_devicetype

            if devicetype == 0x2:
                self.serial_device_connected()
