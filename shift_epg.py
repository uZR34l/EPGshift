import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

EPG_URL = "https://xmltvfr.fr/xmltv/xmltv.xml"
SHIFT_HOURS = 2
DAYS_TO_KEEP = 3

INPUT = "original.xml"
OUTPUT = "epg.xml"

# Téléchargement avec identification navigateur
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
start_limit = now - timedelta(hours=2)
end_limit = now + timedelta(days=DAYS_TO_KEEP)

for programme in list(root.findall("programme")):

    start = programme.attrib.get("start")

    if start:
        date_part = start[:14]
        tz_part = start[14:]

        dt = datetime.strptime(date_part, "%Y%m%d%H%M%S")
        dt = dt + timedelta(hours=SHIFT_HOURS)

        # Garde uniquement maintenant + 3 jours
        if dt < start_limit or dt > end_limit:
            root.remove(programme)
            continue

        programme.attrib["start"] = (
            dt.strftime("%Y%m%d%H%M%S") + tz_part
        )

        stop = programme.attrib.get("stop")

        if stop:
            stop_dt = datetime.strptime(stop[:14], "%Y%m%d%H%M%S")
            stop_dt = stop_dt + timedelta(hours=SHIFT_HOURS)

            programme.attrib["stop"] = (
                stop_dt.strftime("%Y%m%d%H%M%S") + stop[14:]
            )

import gzip

# Création du XML temporaire puis compression directe
xml_data = ET.tostring(root, encoding="utf-8")

with gzip.open("epg.xml.gz", "wb") as f:
    f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
    f.write(xml_data)

print("EPG corrigé généré en GZIP uniquement")
