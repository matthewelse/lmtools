from bs4 import BeautifulSoup
from json import loads
from os.path import isfile
from urlparse import urlparse
from platform import system


def identify_connected_mbed(drive, json_file="lookup.json"):
    with open("lookup.json" if json_file is None else json_file, "rt") as json_file_ref:
        lookup = loads(json_file_ref.read())

    # We're only targeting windows or linux so we may as well do it this way.
    if system() == "Windows":
        drive = drive + ":/"

    loc = "mbed.htm" if isfile("%smbed.htm" % drive) else "MBED.htm" if isfile(
        "%sMBED.htm" % drive) else None
    assert loc is not None, "mbed.htm does not exist!"

    with open("%s%s" % (drive, loc), "rt") as file_ref:
        content = BeautifulSoup(file_ref.read())

    meta = content.meta['content']
    if "url=" not in meta:
        return None
    else:
        chunks = meta.split(';')
        chunks = [x.strip() for x in chunks]
        chunks = [x[4:] for x in chunks if x.startswith("url=")]

        assert len(chunks) == 1, "Invalid HTML File"

        url = urlparse(chunks[0])

        query = url.query.split("&")
        query = {x.split('=')[0]: x.split("=")[1] for x in query}

        if url.path == "/start":
            if query['auth'][:4] not in lookup:
                return None
            return lookup[query['auth'][:4]]
        elif url.path == "/device/":
            if query['code'][:4] not in lookup:
                return None
            return lookup[query['code'][:4]]
        else:
            return None
