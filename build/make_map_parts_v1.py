"""Zerlegt grosse Regionen der Karte in die Teile, die als eigene .img exportiert wurden.

Zum Beispiel ist Tirol in zehn Teile geschnitten (Hangneigung_Tirol_Teil_01.img
bis _10.img). Damit die Karte zu diesen Dateien passt, braucht jeder Teil einen
eigenen Pfad, den man anklicken kann.

Eingang
  build/teile_plan.json     die Rechtecke der Teile (Herkunft steht in der Datei)
  website_prototype/data/boundaries/*.geojson   die Verwaltungsgrenzen
  build/map_data.json       die bisherigen Regionspfade (nur zum Gegenpruefen)
Ausgang
  build/map_parts.json      je zerlegter Region die Teilpfade

map_data.json bleibt UNVERAENDERT: Die Laenderumrisse (country_outlines.json)
sind aus den ganzen Regionen berechnet und stimmen weiter, weil die Teile
zusammen genau die Region ergeben.

Reihenfolge der Skripte: make_map_data_v2.py, make_country_outlines_v2.py,
make_map_parts_v1.py, make_downloads_v2.py, build.py.

Ablauf
  1. Projektion nachbauen und PRUEFEN, dass dabei fuer alle 44 Regionen genau
     dieselben Pfade herauskommen wie in map_data.json. Sonst wuerden die Teile
     neben den Regionen liegen statt darauf.
  2. Je Region die Regionsflaeche (Laenge/Breite) mit den Teilrechtecken
     zuschneiden und mit derselben Projektion in Kartenpfade umrechnen.
  3. Pruefen: Die Teile ergeben zusammen die Region, ueberlappen sich nicht und
     keiner ist leer oder winzig.

Aussenkanten: Die Teile sind Rechtecke ueber die KACHELN, die es gibt. Eine
Region reicht aber oft ueber diese Kacheln hinaus, meist ins flache Vorland, wo
es keine Haenge ueber 30 Grad und damit keine Kacheln gibt (Beispiel: die
Nordspitze von Salzburg endet 0,06 Grad hinter der letzten Kachel). Damit auf
der Karte trotzdem jeder Punkt einer Region genau EINEM Teil gehoert und
anklickbar ist, werden Kanten, die auf dem Rand des Gesamtrechtecks liegen,
bis ueber den Regionsrand hinaus verlaengert. Dieser Randstreifen enthaelt keine
Daten; am Export aendert das nichts. Innenkanten zwischen zwei Teilen bleiben
exakt, beide Nachbarn nutzen denselben gerundeten Wert.

Aufruf:  python3 build/make_map_parts_v1.py
"""
import json
import math
import pathlib
import sys

from shapely.geometry import box, shape
from shapely.ops import unary_union

HERE = pathlib.Path(__file__).parent
PROJEKT = HERE.parent.parent
BOUNDARIES = PROJEKT / "website_prototype" / "data" / "boundaries"

# Identisch zu website_prototype/build/make_map_svg.py. Aenderungen hier muessen
# dort mitgemacht werden, sonst stimmt die Projektion nicht mehr.
SELECTION = {
    "AUT": None,
    "CHE": None,
    "DEU": ["Bayern"],
    "FRA": ["Auvergne-Rhône-Alpes", "Provence-Alpes-Côte d'Azur"],
    "ITA": ["Valle d'Aosta", "Piemonte", "Lombardia", "Trentino-Alto Adige", "Veneto",
            "Friuli Venezia Giulia"],
    "LIE": None,
}
COUNTRY_NAMES = {"AUT": "Österreich", "CHE": "Schweiz", "DEU": "Deutschland",
                 "FRA": "Frankreich", "ITA": "Italien", "LIE": "Liechtenstein"}

# Verwaltungsebene je Land. Vorgabe ADM1 (Bundeslaender, Kantone, Regionen).
# Liechtenstein ist mit 160 km2 kleiner als jede dieser Einheiten; seine ADM1-Ebene
# waeren die elf Gemeinden. Es wird wie im Export als EIN Gebiet gefuehrt.
ADM_EBENE = {"LIE": "ADM0"}
VIEW_W = 1000
MARGIN = 20
SIMPLIFY = 0.01

# Wie weit Kanten auf dem Rand des Gesamtrechtecks nach aussen verlaengert werden.
# Bewusst gross: Es soll bis ueber den Regionsrand reichen, nicht nur die
# Rundung auf 0,01 Grad ausgleichen. Keine Region ist 5 Grad breiter als ihre Kacheln.
AUSSEN_PUFFER = 5.0   # Grad

# Ein Teil, der auf der Karte kleiner ist als das, gilt als Fehler.
MIN_TEIL_PX2 = 40.0


def lade_regionen():
    regionen = []
    for iso, behalten in SELECTION.items():
        data = json.loads((BOUNDARIES / f"{iso}_{ADM_EBENE.get(iso, 'ADM1')}.geojson").read_text())
        for feat in data["features"]:
            name = feat["properties"].get("shapeName")
            if behalten is not None and name not in behalten:
                continue
            regionen.append({"iso": iso, "country": COUNTRY_NAMES[iso], "name": name,
                             "geom": shape(feat["geometry"])})
    for r in regionen:
        r["geom"] = r["geom"].simplify(SIMPLIFY, preserve_topology=True)
    return regionen


class Projektion:
    """Dieselbe Rechnung wie make_map_svg.py, damit Teile und Regionen deckungsgleich sind."""

    def __init__(self, regionen):
        self.minx = min(r["geom"].bounds[0] for r in regionen)
        self.miny = min(r["geom"].bounds[1] for r in regionen)
        self.maxx = max(r["geom"].bounds[2] for r in regionen)
        self.maxy = max(r["geom"].bounds[3] for r in regionen)
        lat0 = (self.miny + self.maxy) / 2
        self.cos_lat0 = math.cos(math.radians(lat0))
        proj_w = (self.maxx - self.minx) * self.cos_lat0
        proj_h = self.maxy - self.miny
        self.scale = (VIEW_W - 2 * MARGIN) / proj_w
        self.view_h = proj_h * self.scale + 2 * MARGIN

    def svg(self, lon, lat):
        x = (lon - self.minx) * self.cos_lat0
        y = self.maxy - lat
        return (x * self.scale + MARGIN, y * self.scale + MARGIN)

    def ring(self, coords):
        pts = [self.svg(lon, lat) for lon, lat in coords]
        return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"

    def pfad(self, geom):
        if geom.geom_type == "Polygon":
            polys = [geom]
        elif geom.geom_type == "MultiPolygon":
            polys = list(geom.geoms)
        else:
            return ""
        teile = []
        for poly in polys:
            teile.append(self.ring(list(poly.exterior.coords)))
            for innen in poly.interiors:
                teile.append(self.ring(list(innen.coords)))
        return " ".join(teile)

    def px2(self, geom):
        """Flaeche auf der Karte in Bildpunkten zum Quadrat."""
        return geom.area * self.cos_lat0 * self.scale ** 2


def nur_flaechen(geom):
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    teile = [g for g in getattr(geom, "geoms", []) if g.geom_type in ("Polygon", "MultiPolygon")]
    return unary_union(teile) if teile else geom


def main():
    plan = json.loads((HERE / "teile_plan.json").read_text())["regionen"]
    map_data = json.loads((HERE / "map_data.json").read_text())

    regionen = lade_regionen()
    proj = Projektion(regionen)
    print(f"Projektion: Skala {proj.scale:.4f}, Hoehe {proj.view_h:.1f} "
          f"(map_data.json: {map_data['viewW']} x {map_data['viewH']})")
    if round(proj.view_h, 1) != map_data["viewH"]:
        sys.exit("ABBRUCH: Kartenhoehe weicht ab - Auswahl oder Vereinfachung nicht identisch.")

    # 1. Gegenpruefung: ALLE Regionen muessen bitgenau reproduziert werden.
    vorhanden = {(r["iso"], r["name"]): r for r in map_data["regions"]}
    abweichend = []
    for r in regionen:
        ref = vorhanden.get((r["iso"], r["name"]))
        if ref is None or proj.pfad(r["geom"]) != ref["d"]:
            abweichend.append(f"{r['iso']}|{r['name']}")
    print(f"Gegenpruefung: {len(regionen) - len(abweichend)} von {len(regionen)} Regionspfaden "
          f"identisch zu map_data.json")
    if abweichend or len(regionen) != len(map_data["regions"]):
        sys.exit(f"ABBRUCH: Pfade weichen ab: {abweichend[:5]}")

    # 2. Teile zuschneiden
    nach_name = {f"{r['iso']}|{r['name']}": r for r in regionen}
    ergebnis = {}
    for schluessel, teile in plan.items():
        region = nach_name[schluessel]
        geom = region["geom"]
        west0 = min(t["west"] for t in teile)
        ost0 = max(t["ost"] for t in teile)
        sued0 = min(t["sued"] for t in teile)
        nord0 = max(t["nord"] for t in teile)

        stuecke = []
        for t in sorted(teile, key=lambda x: x["nr"]):
            w, o, s, n = t["west"], t["ost"], t["sued"], t["nord"]
            if w == west0: w -= AUSSEN_PUFFER
            if o == ost0:  o += AUSSEN_PUFFER
            if s == sued0: s -= AUSSEN_PUFFER
            if n == nord0: n += AUSSEN_PUFFER
            teil_geom = nur_flaechen(geom.intersection(box(w, s, o, n)))
            stuecke.append((t, teil_geom))

        # 3. Pruefungen
        gesamt = geom.area
        vereinigt = unary_union([g for _, g in stuecke])
        luecke = geom.difference(vereinigt).area
        ueberlapp = 0.0
        for i in range(len(stuecke)):
            for j in range(i + 1, len(stuecke)):
                ueberlapp += stuecke[i][1].intersection(stuecke[j][1]).area
        leer = [t["nr"] for t, g in stuecke if g.is_empty]
        klein = [(t["nr"], round(proj.px2(g), 1)) for t, g in stuecke
                 if not g.is_empty and proj.px2(g) < MIN_TEIL_PX2]
        ohne_kacheln = geom.difference(box(west0, sued0, ost0, nord0)).area / gesamt
        print(f"{schluessel:<34} {len(stuecke):>2} Teile  Luecke {luecke / gesamt:.2e}  "
              f"Ueberlappung {ueberlapp / gesamt:.2e}  kleinster Teil "
              f"{min(proj.px2(g) for _, g in stuecke):6.0f} px2  "
              f"ausserhalb der Kacheln {100 * ohne_kacheln:4.1f} %")
        if luecke / gesamt > 1e-6 or ueberlapp / gesamt > 1e-6 or leer or klein:
            sys.exit(f"ABBRUCH {schluessel}: Luecke {luecke / gesamt:.2e}, Ueberlappung "
                     f"{ueberlapp / gesamt:.2e}, leer {leer}, zu klein {klein}")

        eintraege = []
        for t, g in stuecke:
            groesster = max(g.geoms, key=lambda p: p.area) if g.geom_type == "MultiPolygon" else g
            lx, ly = proj.svg(*groesster.representative_point().coords[0])
            eintraege.append({"nr": t["nr"], "d": proj.pfad(g), "labelX": round(lx, 1),
                              "labelY": round(ly, 1), "kacheln": t["kacheln"]})
        ergebnis[schluessel] = {"anzahl": len(eintraege), "teile": eintraege}

    out = {"hinweis": "Erzeugt von make_map_parts_v1.py - nicht von Hand aendern.",
           "regionen": ergebnis}
    (HERE / "map_parts.json").write_text(json.dumps(out, ensure_ascii=False))
    groesse = (HERE / "map_parts.json").stat().st_size
    print(f"\nmap_parts.json: {len(ergebnis)} Regionen, {sum(v['anzahl'] for v in ergebnis.values())} Teile, "
          f"{groesse / 1024:.0f} KB")


if __name__ == "__main__":
    main()
