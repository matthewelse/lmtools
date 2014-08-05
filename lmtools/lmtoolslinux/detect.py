import pyudev
import subprocess
import os.path
from ..common import vendor_ids

# Linux supports STM as well :)
vendor_ids = ['0d28', '0483']


def parse_ls_row(row):
    halves = row.split('->')
    chunks = halves[0].strip().split(' ')
    return chunks[-1]


def parse_lss_row(row):
    halves = row.split('->')
    chunks = halves[1].strip().split(' ')
    return chunks[-1]


def parse_lsblk_row(row):
    chunks = row.strip().split(' ')
    return chunks[-1]


def find_connected_mbeds():
    ctx = pyudev.Context()
    mbeds = []

    for dev in ctx.list_devices(subsystem='usb'):
        d = {k: dev[k] for k in dev}

        if "ID_VENDOR_ID" not in d:
            continue

        if d['ID_VENDOR_ID'] not in vendor_ids:
            continue

        # print d

        ls = subprocess.Popen(
            ('ls', '-oA', '/sys/block'), stdout=subprocess.PIPE)
        output = subprocess.check_output(
            ('grep', dev.device_path), stdin=ls.stdout)
        ls.wait()

        drivename = parse_ls_row(output)

        lsblk = subprocess.Popen(('lsblk',), stdout=subprocess.PIPE)
        goutput = subprocess.check_output(
            ('grep', drivename), stdin=lsblk.stdout)
        lsblk.wait()

        ls = subprocess.Popen(
            ('ls', '-oA', '/dev/serial/by-id'), stdout=subprocess.PIPE)
        output = subprocess.check_output(
            ('grep', d['ID_SERIAL']), stdin=ls.stdout)
        ls.wait()

        serial_port = os.path.normpath(
            os.path.join('/dev/serial/by-id', parse_lss_row(output)))
        mount_point = parse_lsblk_row(goutput)

        # return none if it hasn't been mounted yet.
        if mount_point == "disk":
            mount_point = None

        mbeds.append((d['ID_SERIAL_SHORT'], serial_port, mount_point))

    return mbeds

if __name__ == "__main__":
    print find_connected_mbeds()
