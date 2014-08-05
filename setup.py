from setuptools import setup
import os

requirements = [
	"beautifulsoup4",
	"prettytable"
]

if os.name == "nt":
	requirements.append("WMI")
	requirements.append("PySide")
else:
	requirements.append("pygobject")

setup(name='lmtools',
	  version='0.1',
	  description='A python module to detect mbeds being connectedlm and disconnected, and identify them.',
	  url='http://github.com/mbedmicro/mbed',
	  author='Matthew Else',
	  author_email='matthew.else@arm.com',
	  packages=['lmtools', 'lmtools.lmtoolswin', 'lmtools.lmtoolslinux'],
	  install_requires=requirements,
	  scripts=['scripts/lm', 'scripts/lm.py', 'scripts/lmgui.pyw', 'scripts/lmgui'],
	  package_data = {
	  	'lmtools': ['data/*.png', 'data/*.json']
	  },
	  zip_safe=False)

print "In order to use lm as a cmd command, C:\Python27\Scripts or equivalent must be in PATH"