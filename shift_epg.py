import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import gzip
import os

EPG_URL = "https://xmltvfr.fr/xmltv/xmltv.xml"

PARIS = ZoneInfo("Europe/Paris")
UTC = ZoneInfo("UTC")

INPUT = "original.xml"

# Téléchargement
req = urllib.request.Request(
    EPG_URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

with urllib.request.urlopen(req) as response:
    with open(INPUT, "wb") as f:
        f.write(response.read())


tree = ET.parse(INPUT)
root = tree.getroot()


now = datetime.now()
start_limit = now - timedelta(days=2)
end_limit = now + timedelta(days=2)


def apply_shift(dt):
    utc_dt = dt.replace(tzinfo=UTC)
    offset = utc_dt.astimezone(PARIS).utcoffset()
    return dt + offset


for programme in list(root.findall("programme")):

    start = programme.attrib.get("start")

    if start:

        dt = datetime.strptime(
            start[:14],
            "%Y%m%d%H%M%S"
        )

        dt = apply_shift(dt)

        if dt < start_limit or dt > end_limit:
            root.remove(programme)
            continue

        programme.attrib["start"] = (
            dt.strftime("%Y%m%d%H%M%S")
            + start[14:]
        )


        stop = programme.attrib.get("stop")

        if stop:

            stop_dt = datetime.strptime(
                stop[:14],
                "%Y%m%d%H%M%S"
            )

            stop_dt = apply_shift(stop_dt)

            programme.attrib["stop"] = (
                stop_dt.strftime("%Y%m%d%H%M%S")
                + stop[14:]
            )


xml_data = ET.tostring(
    root,
    encoding="utf-8"
)

with gzip.open(
    "epg.xml.gz",
    "wb"
) as f:

    f.write(
        b'<?xml version="1.0" encoding="utf-8"?>\n'
    )
    f.write(xml_data)


os.remove(INPUT)

print("EPG corrigé généré avec gestion automatique été/hiver")
