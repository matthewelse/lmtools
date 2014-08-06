from wmi import WMI
from ..common import vendor_ids
import pythoncom

vendor_ids = ['0D28']


def find_connected_mbeds():
    pythoncom.CoInitialize()
    c = WMI()

    devices = {}

    for usb in c.Win32_PnPEntity():
        # Device ID is standardised, apparently

        id_chunks = usb.DeviceID.split('\\')

        if id_chunks[0] != "USB":
            continue

        if usb.Caption.find("COM") != -1:
            comport = usb.Caption[
                usb.Caption.find("(") + 1:usb.Caption.rfind(")")]

            if id_chunks[1].split("&")[0].split('_')[1].upper() not in vendor_ids:
                continue

            uid = id_chunks[2]

            if uid not in devices:
                devices[uid] = [comport]
            else:
                devices[uid].append(comport)

    for usb in c.Win32_DiskDrive(InterfaceType="USB"):
        uid = usb.PNPDeviceID.split('\\')[2][:-2]
        drive_letters = []

        for partition in usb.associators("Win32_DiskDriveToDiskPartition"):
            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                drive_letters.append(logical_disk.Caption)

        try:
            driveletter = drive_letters[0][0]
        except:
            driveletter = None

        if uid in devices:
            devices[uid].append(driveletter)

    output = [(k, str(v[0]), str(v[1])) for k, v in devices.items()]
    return output

if __name__ == "__main__":
    print find_connected_mbeds()
