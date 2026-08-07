import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

EPG_URL = "https://xmltvfr.fr/xmltv/xmltv.xml"
SHIFT_HOURS = 2

INPUT = "original.xml"
OUTPUT = "epg.xml"

# Téléchargement
urllib.request.urlretrieve(EPG_URL, INPUT)

tree = ET.parse(INPUT)
root = tree.getroot()

for programme in root.findall("programme"):
    for key in ["start", "stop"]:
        value = programme.attrib.get(key)

        if value:
            date_part = value[:14]
            tz_part = value[14:]

            dt = datetime.strptime(date_part, "%Y%m%d%H%M%S")
            dt = dt + timedelta(hours=SHIFT_HOURS)

            programme.attrib[key] = (
                dt.strftime("%Y%m%d%H%M%S") + tz_part
            )

tree.write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True
)

print("EPG corrigé généré")
