#!/usr/bin/python
import json
import lmtools
from flask import Flask, Response, abort

# REST API for lmtools

app = Flask(__name__)

@app.route('/devices/')
def enumerate_devices():
	devices = lmtools.get_connected_mbeds()

	if len(devices) > 0:
		return Response(json.dumps(devices), mimetype='text/json')
	else:
		abort(404)

@app.route('/devices/<devicename>')
def enumerate_devices_named(devicename):
	devices = [x for x in lmtools.get_connected_mbeds() if x["name"] == devicename]

	if len(devices) > 0:
		return Response(json.dumps(devices), mimetype='text/json')
	else:
		abort(404)

@app.route('/device/<serialnumber>')
def find_device_with_serial_number(serialnumber):
	devices = lmtools.get_connected_mbeds()

	if serialnumber not in devices:
		abort(404)
	else:
		return Response(json.dumps(devices[serialnumber]), mimetype='text/json')

if __name__ == "__main__":
	app.run(debug=True, port=5555)