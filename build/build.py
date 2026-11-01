"""Baut die beiden Seiten aus den Templates.

Ersetzt die __PLATZHALTER__ durch den Höhenlinien-Hintergrund, die
Kartendaten und die gegenseitigen Artifact-Links. Bricht ab, wenn ein
Platzhalter übrig bleibt, damit nie eine halb gebaute Seite rausgeht.
"""
import json
import pathlib
import re
import sys
import urllib.parse

from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

COORD_RE = re.compile(r"[ML]\s*(-?[\d.]+),(-?[\d.]+)")

# Wie weit jede Region aufgeblasen wird, damit sie ihre Nachbarn beruehrt.
#
# Bewusst klein gehalten. Ein grosser Wert (getestet: 3.0) schliesst zwar auch
# die breitesten Luecken zwischen zwei Regionen, laesst die Regionen dabei aber
# so stark ueberlappen, dass die jeweils spaeter gezeichnete die fruehere
# ueberdeckt - kleine Kantone wie Appenzell oder Basel-Stadt waren danach nicht
# mehr anklickbar. Da farblose Stellen inzwischen ohnehin ausgeschlossen sind
# (Grundflaeche je Land plus abgedunkelte statt sandfarbener Regionsgrenzen),
# reicht hier ein Wert, der nur die haeufigen Haarrisse schliesst.
REGION_AUFBLASEN = 0.0


def _region_ringe(d):
    ringe = []
    for teil in d.split("M")[1:]:
        pts = COORD_RE.findall("M" + teil)
        if len(pts) >= 3:
            ringe.append([(float(x), float(y)) for x, y in pts])
    return ringe


def aufgeblasene_region(d):
    if REGION_AUFBLASEN <= 0:
        return d
    polys = [Polygon(r) for r in _region_ringe(d)]
    polys = [p if p.is_valid else make_valid(p) for p in polys]
    polys = [p for p in polys if not p.is_empty]
    if not polys:
        return d
    vereinigt = unary_union([p.buffer(REGION_AUFBLASEN, join_style="mitre") for p in polys])
    if vereinigt.geom_type not in ("Polygon", "MultiPolygon"):
        teile = [g for g in getattr(vereinigt, "geoms", [vereinigt])
                 if g.geom_type in ("Polygon", "MultiPolygon")]
        vereinigt = unary_union(teile)
    teile = vereinigt.geoms if vereinigt.geom_type == "MultiPolygon" else [vereinigt]
    return "".join(
        "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in p.exterior.coords) + "Z"
        for p in teile if not p.is_empty
    )

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent

# Artifact-URLs der veröffentlichten Seiten. Beim allerersten Build sind
# sie noch unbekannt: dann zeigt der Link auf die jeweils andere Datei,
# und nach dem ersten Veröffentlichen werden die echten URLs eingetragen.
HOME_URL = "__PENDING_HOME__"
INFO_URL = "__PENDING_INFO__"
BEISPIELE_URL = "__PENDING_BEISPIELE__"
IMPRESSUM_URL = "impressum.html"

URLS = HERE / "urls.json"
if URLS.exists():
    _u = json.loads(URLS.read_text())
    HOME_URL = _u.get("home", HOME_URL)
    INFO_URL = _u.get("info", INFO_URL)
    BEISPIELE_URL = _u.get("beispiele", BEISPIELE_URL)
    IMPRESSUM_URL = _u.get("impressum", IMPRESSUM_URL)

# Kontaktadresse. Steht bewusst nur hier, damit ein spaeterer Wechsel (etwa auf
# eine eigene Domain) eine einzige Aenderung ist und nicht sechs im Template.
MAIL_ADRESSE = "hangneigungslayer@proton.me"

# Vorausgefuellte Betreffzeilen, damit eingehende Post sich von selbst sortiert.
# urllib.parse.quote statt Handarbeit, damit Umlaute und Leerzeichen korrekt
# prozentkodiert werden - ein roher Betreff mit Leerzeichen bricht den Link.
def _mailto(betreff):
    return f"mailto:{MAIL_ADRESSE}?subject={urllib.parse.quote(betreff)}"


MAILTO = {
    "__MAIL_ADRESSE__": MAIL_ADRESSE,
    "__PAYPAL_URL__": "https://www.paypal.com/paypalme/AlexanderTombrink",
    "__MAILTO_ALLGEMEIN__": _mailto("Feedback zum Hangneigungslayer"),
    "__MAILTO_FEHLER__": _mailto("Fehler melden: "),
    "__MAILTO_REGION__": _mailto("Regionsvorschlag: "),
}


def build(template_name, out_name, extra=None):
    tpl = (HERE / template_name).read_text()
    topo = (HERE / "topo_bg_sand.txt").read_text().strip()

    out = tpl.replace("__TOPO_BG_SAND__", topo)
    out = out.replace("__HOME_URL__", HOME_URL)
    out = out.replace("__INFO_URL__", INFO_URL)
    out = out.replace("__BEISPIELE_URL__", BEISPIELE_URL)
    out = out.replace("__IMPRESSUM_URL__", IMPRESSUM_URL)
    for key, value in MAILTO.items():
        out = out.replace(key, value)
    for key, value in (extra or {}).items():
        out = out.replace(key, value)

    leftover = sorted(set(re.findall(r"__[A-Z0-9_]+__", out)))
    if leftover:
        sys.exit(f"FEHLER {out_name}: Platzhalter übrig: {leftover}")

    target = OUT / out_name
    target.write_text(out)
    print(f"{out_name}: {len(out):,} Bytes")


def main():
    map_data = json.loads((HERE / "map_data.json").read_text())
    for region in map_data["regions"]:
        region["d"] = aufgeblasene_region(region["d"])
    country_outlines = json.loads((HERE / "country_outlines.json").read_text())
    downloads = json.loads((HERE / "downloads.json").read_text())

    # Zerlegte Regionen (siehe make_map_parts_v1.py): Die Karte zeichnet dort die
    # Teile statt der ganzen Region. Der ganze Pfad wird deshalb nicht mehr
    # gebraucht und aus der Seite genommen; Name, Land und ISO bleiben fuer die Suche.
    parts_pfad = HERE / "map_parts.json"
    map_parts = json.loads(parts_pfad.read_text())["regionen"] if parts_pfad.exists() else {}
    for region in map_data["regions"]:
        if f"{region['iso']}|{region['name']}" in map_parts:
            region["d"] = ""
    build(
        "index_template.html",
        "index.html",
        {
            "__MAP_DATA_JSON__": json.dumps(map_data, ensure_ascii=False),
            "__COUNTRY_OUTLINES_JSON__": json.dumps(country_outlines, ensure_ascii=False),
            "__DOWNLOADS_JSON__": json.dumps(downloads, ensure_ascii=False),
            "__MAP_PARTS_JSON__": json.dumps(map_parts, ensure_ascii=False),
        },
    )
    build("info_template.html", "info.html")
    build("beispiele_template.html", "beispiele.html")
    build("impressum_template.html", "impressum.html")


if __name__ == "__main__":
    main()
