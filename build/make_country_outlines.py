"""Berechnet je Land die Aussenlinie aus der Vereinigung aller seiner Regionen.

Eine dickere Version der bestehenden Regionsraender waere KEIN Laenderumriss -
sie wuerde weiterhin jede einzelne Kanton-/Bundeslandgrenze zeigen, nur fetter.
Gebraucht wird stattdessen die echte Aussenkontur: alle Regionspfade eines
Landes geometrisch vereinigen, gemeinsame Innengrenzen verschwinden dabei von
selbst, uebrig bleibt nur die Silhouette des gesamten Landes (plus echte
Enklaven/Exklaven als eigene Teilflaechen, falls vorhanden).

Liest build/map_data.json (SVG-Pfade bereits in Karten-Pixelkoordinaten,
kein Bezug mehr zu EPSG-CRS), schreibt build/country_outlines.json.
"""
import json
import pathlib
import re

from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
from shapely.validation import make_valid

HERE = pathlib.Path(__file__).parent

COORD_RE = re.compile(r"[ML]\s*(-?[\d.]+),(-?[\d.]+)")


def parse_d(d: str):
    """Zerlegt ein 'M x,y L x,y ... Z M x,y ... Z'-Pfad in Ringe (Punktlisten).

    Die Regionspfade wurden per make_map_svg.py selbst erzeugt und enthalten
    garantiert nur M/L/Z, keine Kurven - ein regulaerer Ausdruck reicht.
    """
    ringe = []
    for teil in d.split("M")[1:]:
        pts = COORD_RE.findall("M" + teil)
        if len(pts) >= 3:
            ringe.append([(float(x), float(y)) for x, y in pts])
    return ringe


def ring_zu_d(coords) -> str:
    pts = [f"{x:.1f},{y:.1f}" for x, y in coords]
    return "M" + "L".join(pts) + "Z"


def geometrie_zu_d(geom) -> str:
    """Polygon oder MultiPolygon -> ein d-String, ein Teilpfad je Aussenring.

    Absichtlich nur die Aussenringe (exterior), keine Loecher: ein Laendersee
    mitten im Land soll die Umrisslinie nicht durchbrechen, hier geht es um
    Kontrast an der Aussenkante, nicht um geografische Vollstaendigkeit.
    """
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    return "".join(ring_zu_d(p.exterior.coords) for p in polys if not p.is_empty)


def main():
    daten = json.loads((HERE / "map_data.json").read_text())

    nach_land = {}
    for region in daten["regions"]:
        ringe = parse_d(region["d"])
        polys = [Polygon(r) for r in ringe if len(r) >= 3]
        polys = [p if p.is_valid else make_valid(p) for p in polys]
        nach_land.setdefault(region["iso"], []).extend(polys)

    # Jede Region wurde beim Kartenbau UNABHAENGIG vereinfacht (shapely
    # .simplify je Region). Dadurch liegen gemeinsame Grenzen zweier
    # Nachbarregionen danach nicht mehr pixelgenau aufeinander - unary_union
    # haelt sie faelschlich fuer getrennt und die "Laendersilhouette" zerfaellt
    # in viele Splitter statt einer Kontur. Fix: vor der Vereinigung um einen
    # winzigen Betrag aufblasen (schliesst die Haarrisse), danach wieder um
    # denselben Betrag verkleinern, um die Originalgroesse zurückzubekommen.
    SPALT_SCHLUSS = 3.0  # Karten-Pixel, bei ~1000 Einheiten Kartenbreite sehr klein
    MINDESTFLAECHE = 8.0  # verbleibende Mini-Splitter als Rauschen verwerfen

    ergebnis = {}
    for iso, polys in nach_land.items():
        aufgeblasen = [p.buffer(SPALT_SCHLUSS, join_style="mitre") for p in polys]
        vereinigt = unary_union(aufgeblasen).buffer(-SPALT_SCHLUSS, join_style="mitre")
        vereinigt = vereinigt if vereinigt.is_valid else make_valid(vereinigt)
        if vereinigt.geom_type not in ("Polygon", "MultiPolygon"):
            flaechen = [g for g in getattr(vereinigt, "geoms", [vereinigt])
                        if g.geom_type in ("Polygon", "MultiPolygon")]
            vereinigt = unary_union(flaechen)

        if vereinigt.geom_type == "MultiPolygon":
            teile_liste = [p for p in vereinigt.geoms if p.area >= MINDESTFLAECHE]
            vereinigt = unary_union(teile_liste) if teile_liste else vereinigt

        ergebnis[iso] = geometrie_zu_d(vereinigt)
        teile = len(vereinigt.geoms) if vereinigt.geom_type == "MultiPolygon" else 1
        print(f"{iso}: {len(polys)} Einzelpolygone -> {teile} Aussenring(e)")

    (HERE / "country_outlines.json").write_text(json.dumps(ergebnis, ensure_ascii=False))
    print(f"\ngeschrieben: country_outlines.json ({len(ergebnis)} Laender)")


if __name__ == "__main__":
    main()
