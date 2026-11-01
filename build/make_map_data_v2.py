"""Erzeugt build/map_data.json neu, jetzt mit Liechtenstein als sechstem Land.

Ersetzt website_prototype/build/make_map_svg.py fuer die Arbeitskopie. Dieselbe
Rechnung (Auswahl, Vereinfachung 0,01 Grad, Projektion, Pfadformat), nur dass
Liechtenstein dazukommt. Der Code steckt in make_map_parts_v1.py, damit beide
Skripte garantiert dieselbe Projektion benutzen.

Wichtig ist, dass sich fuer die 44 bisherigen Regionen NICHTS aendert:
  - Liechtenstein liegt mitten im Kartenausschnitt, die Projektion bleibt gleich
    (Skala, Hoehe), das wird geprueft;
  - jeder bisherige Eintrag muss bitgenau erhalten bleiben, sonst bricht das
    Skript ab, bevor es etwas schreibt;
  - keine Region darf wegfallen.

Neu ist nur der Eintrag LIE|Liechtenstein am Ende der Liste.

Danach: make_country_outlines_v2.py (Laenderumrisse neu), make_map_parts_v1.py.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
# Mit "python3 -I" gehoert das Skriptverzeichnis nicht zum Suchpfad.
sys.path.insert(0, str(HERE))
import make_map_parts_v1 as grund  # noqa: E402

ZIEL = HERE / "map_data.json"


def main():
    regionen = grund.lade_regionen()
    proj = grund.Projektion(regionen)

    neu = []
    for r in regionen:
        cx, cy = r["geom"].centroid.x, r["geom"].centroid.y
        lx, ly = proj.svg(cx, cy)
        neu.append({"iso": r["iso"], "country": r["country"], "name": r["name"],
                    "d": proj.pfad(r["geom"]), "labelX": round(lx, 1), "labelY": round(ly, 1)})
    ergebnis = {"viewW": round(grund.VIEW_W, 1), "viewH": round(proj.view_h, 1), "regions": neu}

    if ZIEL.exists():
        alt = json.loads(ZIEL.read_text())
        if (alt["viewW"], alt["viewH"]) != (ergebnis["viewW"], ergebnis["viewH"]):
            sys.exit(f"ABBRUCH: Kartengroesse aendert sich {alt['viewW']}x{alt['viewH']} -> "
                     f"{ergebnis['viewW']}x{ergebnis['viewH']}. Dann stimmen alle Pfade nicht mehr.")
        alt_nach = {(e["iso"], e["name"]): e for e in alt["regions"]}
        neu_nach = {(e["iso"], e["name"]): e for e in neu}
        weg = [k for k in alt_nach if k not in neu_nach]
        if weg:
            sys.exit(f"ABBRUCH: Regionen waeren weggefallen: {weg}")
        geaendert = [k for k, e in alt_nach.items() if neu_nach[k] != e]
        if geaendert:
            sys.exit(f"ABBRUCH: {len(geaendert)} bisherige Regionen wuerden sich aendern: {geaendert[:5]}")
        dazu = [k for k in neu_nach if k not in alt_nach]
        print(f"bisherige Regionen unveraendert: {len(alt_nach)} von {len(alt_nach)}")
    else:
        dazu = [(e["iso"], e["name"]) for e in neu]

    ZIEL.write_text(json.dumps(ergebnis))
    print(f"map_data.json: {len(neu)} Regionen, neu dazugekommen: "
          f"{', '.join('|'.join(k) for k in dazu) or 'nichts'}")


if __name__ == "__main__":
    main()
