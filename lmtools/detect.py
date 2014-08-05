import os
import sys

if os.name == "nt":
    # Windows
    from .lmtoolswin.detect import find_connected_mbeds
else:
    from .lmtoolslinux.detect import find_connected_mbeds
from .identify import identify_connected_mbed


def get_connected_mbeds(json_file=None):
    if json_file is None:
        json_file = os.path.join(
            os.path.dirname(sys.modules["lmtools"].__file__), "data/default.json")

    return {k[0]: {"name": identify_connected_mbed(k[2], json_file), "mount_point": k[2], "port": k[1]} for k in find_connected_mbeds()}
