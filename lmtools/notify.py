import os

if os.name == "nt":
	# Windows
	from .lmtoolswin.notify import Listener
else:
	from .lmtoolslinux.notify import Listener

