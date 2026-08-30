"""Liest die fertigen .img-Dateien und schreibt build/downloads.json.

Damit zeigt die Karte echte Dateigroessen statt der frueheren Platzhalter und
der Download-Button verweist auf die tatsaechliche Datei im GitHub-Release.

Die Dateinamen entstehen nach derselben Regel wie in garmin_slope_batch_v1.py
(Funktion dateistamm): Umlaute werden umschrieben, alles Uebrige auf ASCII
reduziert. Der auf der Uhr angezeigte Kartenname behaelt seine Umlaute, nur
der Dateiname wird vereinfacht - der Speicher der Uhr ist FAT32.

Regionen ohne Layer landen mit "vorhanden": false in der Datei. Die Website
zeigt fuer sie einen Hinweis statt eines Downloads.
"""
import json
import pathlib
import re
import unicodedata

HERE = pathlib.Path(__file__).parent
PROJEKT = HERE.parent.parent
LAYER_DIR = PROJEKT / "garmin_layers"

NAME_PREFIX = "Hangneigung"

# Datenstand je Land, vom Betreiber angegeben. Steht None, laesst die
# Website die Kachel weg, statt eine Zahl zu erfinden.
DATENSTAND = {
    "AUT": "2024",
    "CHE": "2021",
    "DEU": "2025",
}

# Alle Layer werden in der Verarbeitung einheitlich auf 10 m resampelt.
RASTERWEITE = "10 m"


def dateistamm(region_name):
    text = f"{NAME_PREFIX} {region_name}"
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"),
                 ("Ä", "Ae"), ("Ö", "Oe"), ("Ü", "Ue")):
        text = text.replace(a, b)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")


def groesse_lesbar(bytes_):
    """Nur so genau, wie es dem Leser nuetzt: unter 1 MB in KB, darueber in MB."""
    mb = bytes_ / 1024 ** 2
    if mb < 1:
        return f"{bytes_ / 1024:.0f} KB"
    if mb < 10:
        return f"{mb:.1f} MB"
    return f"{mb:.0f} MB"


def main():
    map_data = json.loads((HERE / "map_data.json").read_text())
    release = json.loads((HERE / "release.json").read_text())
    basis = f"https://github.com/{release['repo']}/releases/download/{release['tag']}"

    eintraege = {}
    vorhanden = fehlend = 0
    for region in map_data["regions"]:
        stamm = dateistamm(region["name"])
        pfad = LAYER_DIR / f"{stamm}.img"
        schluessel = f"{region['iso']}|{region['name']}"
        if pfad.exists():
            vorhanden += 1
            eintraege[schluessel] = {
                "vorhanden": True,
                "datei": pfad.name,
                "groesse": groesse_lesbar(pfad.stat().st_size),
                "bytes": pfad.stat().st_size,
                "datenstand": DATENSTAND.get(region["iso"]),
                "raster": RASTERWEITE,
                "url": f"{basis}/{pfad.name}",
            }
        else:
            fehlend += 1
            eintraege[schluessel] = {"vorhanden": False}

    (HERE / "downloads.json").write_text(json.dumps(eintraege, ensure_ascii=False))
    gesamt = sum(e.get("bytes", 0) for e in eintraege.values())
    print(f"downloads.json: {vorhanden} mit Layer, {fehlend} ohne, "
          f"{gesamt / 1024 ** 3:.2f} GB gesamt")
    print(f"Release-Basis: {basis}")


if __name__ == "__main__":
    main()
