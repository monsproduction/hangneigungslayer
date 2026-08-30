"""Berechnet je Land eine Flaeche, die den Alpenbogen LUECKENLOS aufteilt.

Warum v2:
v1 hat jedes Land unabhaengig aus seinen eigenen Regionen vereinigt. Weil die
Regionsumrisse beim Kartenbau einzeln vereinfacht wurden, liegen die Grenzen
zweier BENACHBARTER LAENDER danach nicht deckungsgleich aufeinander - zwischen
Schweiz und Oesterreich, Oesterreich und Bayern usw. blieb ein bis zu 5,8
Karteneinheiten breiter Spalt, der auf der Website als farbloser Streifen
erschien. Innerhalb eines Landes war das durch die Grundflaeche abgedeckt,
zwischen zwei Laendern nicht.

Vorgehen hier:
1. je Land die Silhouette seiner Regionen bilden (wie v1, mit Spaltschluss),
2. daraus den gemeinsamen Alpenbogen bilden und dabei die Spalten ZWISCHEN den
   Laendern schliessen,
3. die dabei entstandene Restflaeche (die Spalten) demjenigen Land zuschlagen,
   das die laengere gemeinsame Kante damit hat.

Ergebnis: Die fuenf Flaechen ueberlappen sich nicht und lassen keinen Rest -
sie kacheln den Bogen. Da die Website dieselben Pfaddaten fuer die Fuellung
UND fuer die schwarze Aussenlinie verwendet, schliessen Farbe und Rand damit
weiterhin exakt ab.

Liest build/map_data.json, schreibt build/country_outlines.json.
"""
import json
import pathlib
import re

from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

HERE = pathlib.Path(__file__).parent

COORD_RE = re.compile(r"[ML]\s*(-?[\d.]+),(-?[\d.]+)")

# Schliesst Haarrisse zwischen Regionen DESSELBEN Landes.
SPALT_INTERN = 3.0
# Schliesst die breiteren Spalten ZWISCHEN zwei Laendern. Gemessen wurde ein
# Maximum von 5,83 Einheiten; ein Radius r schliesst Spalten bis 2*r, daher
# reicht 4.0 mit Reserve.
SPALT_LAENDER = 4.0
# Splitter unterhalb dieser Flaeche sind Vereinfachungsrauschen, kein Gebiet.
MINDESTFLAECHE = 8.0


def parse_d(d: str):
    ringe = []
    for teil in d.split("M")[1:]:
        pts = COORD_RE.findall("M" + teil)
        if len(pts) >= 3:
            ringe.append([(float(x), float(y)) for x, y in pts])
    return ringe


def ring_zu_d(coords) -> str:
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in coords) + "Z"


def geometrie_zu_d(geom) -> str:
    """Nur Aussenringe: ein See mitten im Land soll die Umrisslinie nicht
    durchbrechen, hier geht es um die Aussenkante."""
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    return "".join(ring_zu_d(p.exterior.coords) for p in polys if not p.is_empty)


def ohne_loecher(geom):
    """Baut die Geometrie nur aus ihren Aussenringen neu auf."""
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    return unary_union([Polygon(p.exterior.coords) for p in polys if not p.is_empty])


def gueltig(geom):
    return geom if geom.is_valid else make_valid(geom)


def nur_flaechen(geom):
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    teile = [g for g in getattr(geom, "geoms", [geom])
             if g.geom_type in ("Polygon", "MultiPolygon")]
    return unary_union(teile) if teile else Polygon()


def schliessen(geom, r):
    """Morphologisches Schliessen: aufblasen, dann wieder schrumpfen.
    Schliesst Spalten bis zur Breite 2*r, ohne die Aussenkontur zu vergroessern."""
    return nur_flaechen(gueltig(geom.buffer(r, join_style="mitre").buffer(-r, join_style="mitre")))


def entrausche(geom):
    if geom.geom_type != "MultiPolygon":
        return geom
    teile = [p for p in geom.geoms if p.area >= MINDESTFLAECHE]
    return unary_union(teile) if teile else geom


def main():
    daten = json.loads((HERE / "map_data.json").read_text())

    nach_land = {}
    for region in daten["regions"]:
        polys = [gueltig(Polygon(r)) for r in parse_d(region["d"]) if len(r) >= 3]
        nach_land.setdefault(region["iso"], []).extend(polys)

    # 1. Silhouette je Land
    silhouette = {}
    for iso, polys in nach_land.items():
        s = schliessen(unary_union([p.buffer(SPALT_INTERN, join_style="mitre") for p in polys]).buffer(
            -SPALT_INTERN, join_style="mitre"), 0.01)
        s = ohne_loecher(entrausche(nur_flaechen(gueltig(s))))
        silhouette[iso] = s
        teile = len(s.geoms) if s.geom_type == "MultiPolygon" else 1
        print(f"{iso}: {len(polys)} Einzelpolygone -> Silhouette mit {teile} Teil(en)")

    # 2. Gemeinsamer Alpenbogen, Spalten zwischen den Laendern geschlossen
    belegt = unary_union(list(silhouette.values()))
    bogen = ohne_loecher(schliessen(belegt, SPALT_LAENDER))
    rest = nur_flaechen(gueltig(bogen.difference(belegt)))
    stuecke = list(rest.geoms) if rest.geom_type == "MultiPolygon" else ([rest] if not rest.is_empty else [])
    print(f"\nSpaltflaeche zwischen den Laendern: {rest.area:.0f} Einheiten^2 in {len(stuecke)} Stueck(en)")

    # 3. Jedes Spaltstueck dem Land mit der laengeren gemeinsamen Kante zuschlagen.
    #    (Ein Spalt liegt zwischen zwei Laendern; der reine Mittelpunktabstand
    #     waere dort fast gleich und die Zuordnung damit zufaellig.)
    ergebnis_geom = {iso: s for iso, s in silhouette.items()}
    for stueck in stuecke:
        beste, bester_wert = None, -1.0
        for iso, s in silhouette.items():
            wert = stueck.buffer(0.6).intersection(s).area
            if wert > bester_wert:
                beste, bester_wert = iso, wert
        if beste is not None:
            ergebnis_geom[beste] = nur_flaechen(gueltig(unary_union([ergebnis_geom[beste], stueck])))

    # 4. Ueberschneidungsfrei machen. Die Silhouetten koennen sich durch den
    #    Spaltschluss geringfuegig ueberlappen; blieben sie so, wuerde in diesem
    #    Streifen die schwarze Grenzlinie doppelt gezeichnet. Feste Reihenfolge,
    #    damit das Ergebnis bei jedem Lauf identisch ist.
    vergeben = None
    for iso in sorted(ergebnis_geom):
        g = ergebnis_geom[iso]
        if vergeben is not None:
            g = nur_flaechen(gueltig(g.difference(vergeben)))
        g = entrausche(g)
        ergebnis_geom[iso] = g
        vergeben = g if vergeben is None else unary_union([vergeben, g])

    # 5. Kontrolle: bleibt noch Flaeche uebrig, ueberlappen sich Laender?
    zusammen = unary_union(list(ergebnis_geom.values()))
    luecke = bogen.difference(zusammen).area
    isos = list(ergebnis_geom)
    ueberlapp = sum(ergebnis_geom[a].intersection(ergebnis_geom[b]).area
                    for i, a in enumerate(isos) for b in isos[i + 1:])
    print(f"Restluecke nach Zuordnung: {luecke:.2f} Einheiten^2")
    print(f"Ueberlappung zwischen Laendern: {ueberlapp:.2f} Einheiten^2")

    ergebnis = {iso: geometrie_zu_d(ohne_loecher(g)) for iso, g in ergebnis_geom.items()}
    (HERE / "country_outlines.json").write_text(json.dumps(ergebnis, ensure_ascii=False))
    print(f"\ngeschrieben: country_outlines.json ({len(ergebnis)} Laender)")


if __name__ == "__main__":
    main()
