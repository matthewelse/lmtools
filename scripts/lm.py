#!/usr/bin/python
import argparse
from prettytable import PrettyTable
from lmtools import get_connected_mbeds

if __name__ == "__main__":
	# Output list of currently connected microcontrollers.

	parser = argparse.ArgumentParser(description='List all connected mbed-compatible microcontrollers')
	parser.add_argument('--json', dest='json', type=argparse.FileType('r'), help='Location of JSON file containing mapping between codes and devices.')
	parser.add_argument('--micro', dest='micro', help='Find a specific microcontroller.')

	args = parser.parse_args()
	
	json_file = args.json
	devices = get_connected_mbeds(json_file)

	if args.micro is not None:
		devices = [y for y in devices if y[2] == args.micro]

	x = PrettyTable(["Name", "Port", "Drive", "Serial Number"])
	x.align["Name"] = 'l'
	x.align["Serial Number"] = 'l'

	for device in devices:
		x.add_row([device[3], device[1], device[2], device[0]])

	print x
