#!/usr/bin/python
import json
import lmtools
import pythoncom
from flask import Flask, Response, abort

# REST API for lmtools

app = Flask(__name__)

@app.route('/devices/')
def enumerate_devices():
	pythoncom.CoInitialize()
	devices = lmtools.get_connected_mbeds()

	return Response(json.dumps(devices), mimetype='text/json')

@app.route('/devices/<devicename>')
def enumerate_devices_named(devicename):
	pythoncom.CoInitialize()
	devices = [x for x in lmtools.get_connected_mbeds() if x["name"] == devicename]

	return Response(json.dumps(devices), mimetype='text/json')

@app.route('/device/<serialnumber>')
def find_device_with_serial_number(serialnumber):
	pythoncom.CoInitialize()
	devices = lmtools.get_connected_mbeds()

	if serialnumber not in devices:
		abort(404)
	else:
		return Response(json.dumps(devices[serialnumber]), mimetype='text/json')

if __name__ == "__main__":
	app.run(debug=True, port=5555)