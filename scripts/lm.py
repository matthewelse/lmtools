#!/usr/bin/python
import argparse
from prettytable import PrettyTable
from lmtools import get_connected_mbeds

if __name__ == "__main__":
	# Output list of currently connected microcontrollers.

	parser = argparse.ArgumentParser(description='List all connected mbed-compatible microcontrollers')
	parser.add_argument('-j', dest='json', type=argparse.FileType('r'), help='Location of JSON file containing mapping between codes and devices.')
	parser.add_argument('-i', dest='micro', help='Find a specific microcontroller by name.')
	parser.add_argument('-p', dest='port', help='Find a specific microcontroller by serial port.')
	parser.add_argument('-m', dest='mount_point', help='Find a specific microcontroller by mount point.')
	parser.add_argument('-n', dest='code', help='Find a specific microcontroller by serial number.')

	args = parser.parse_args()
	
	json_file = args.json
	devices = get_connected_mbeds(json_file)

	if args.micro is not None:
		devices = {k: v for k, v in devices.items() if v['name'] == args.micro}

	if args.port is not None:
		devices = {k: v for k, v in devices.items() if v['port'] == args.port}

	if args.mount_point is not None:
		devices = {k: v for k, v in devices.items() if v['mount_point'] == args.mount_point}

	if args.code is not None:
		devices = {k: v for k, v in devices.items() if k == args.code}

	if len(devices) > 0:
		x = PrettyTable(["Name", "Port", "Drive", "Serial Number"])
		x.align["Name"] = 'l'
		x.align["Serial Number"] = 'l'

		for k, v in devices.items():
			x.add_row([v["name"], v["port"], v["mount_point"], k])

		print x
	else:
		print "No devices connected"