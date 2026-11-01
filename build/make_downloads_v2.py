"""Liest die fertigen .img-Dateien und schreibt build/downloads.json (Fassung 2, mit Teilen).

Gegenueber make_downloads.py (Fassung 1):
  - liest den 5-m-Export aus garmin_layers-5m
  - erkennt Regionen, die in Teile zerlegt sind (Hangneigung_Tirol_Teil_01.img ...)
    und legt sie als Liste ab, damit die Karte jeden Teil einzeln anbieten kann
  - gleicht die Teile mit build/map_parts.json ab: Eine Region darf nur dann als
    zerlegt auf der Karte stehen, wenn ALLE ihre Teile als Datei vorliegen, und
    umgekehrt. Sonst bricht das Skript ab, statt einen toten Download anzuzeigen.

Aufbau je Eintrag, Schluessel "ISO|Regionsname":
  ganze Region    {vorhanden, geteilt: false, datei, groesse, bytes, datenstand, raster, url}
  zerlegt         {vorhanden, geteilt: true, anzahl, groesse, bytes, datenstand, raster,
                   teile: [{nr, datei, groesse, bytes, url}, ...],
                   zip: {datei, groesse, bytes, url}}
  ohne Datei      {vorhanden: false}

Zu "zip": Zerlegte Regionen werden zusaetzlich als EIN ZIP mit allen Teilen
angeboten (Hangneigung_Tirol_alle_Teile.zip). Das ZIP wird ohne Kompression
geschrieben - die .img sind ohnehin dicht gepackt -, dadurch ist seine Groesse
vorab auf das Byte genau berechenbar (zip_groesse, an echten Dateien gegen die
Wirklichkeit geprueft: Differenz 0). Es muss nicht schon existieren, damit die Seite
gebaut werden kann; erzeugt wird es mit make_zips_v1.py. Liegt es schon unter
garmin_layers-5m/zip/, zaehlt dessen echte Groesse.

Der Unterordner Old im Export wird ignoriert: Er enthaelt Testdateien, keine Layer.
"""
import json
import pathlib
import re
import sys
import unicodedata

HERE = pathlib.Path(__file__).parent
PROJEKT = HERE.parent.parent
LAYER_DIR = PROJEKT / "garmin_layers-5m"

NAME_PREFIX = "Hangneigung"

# Datenstand je Land. LEER, und das mit Absicht: Die frueheren Angaben (AUT 2024,
# CHE 2021, DEU 2025) gehoerten zu den alten Hoehenmodellen. Die 5-m-Layer stammen
# aus einer anderen Quelle, deren Jahrgang je Land hier niemand belegt hat. Fehlt
# der Eintrag, laesst die Karte die Kachel weg, statt eine Zahl zu erfinden.
DATENSTAND = {}

# Rasterweite der neuen Layer. Laut Angabe des Projektinhabers 5 x 5 m.
RASTERWEITE = "5 m"

TEIL_RE = re.compile(r"^(?P<stamm>.+)_Teil_(?P<nr>\d\d)\.img$")


def dateistamm(region_name):
    """Dieselbe Regel wie im Export (mbtiles_to_garmin_v11.py): Umlaute umschreiben, Rest ASCII."""
    text = f"{NAME_PREFIX} {region_name}"
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"),
                 ("Ä", "Ae"), ("Ö", "Oe"), ("Ü", "Ue")):
        text = text.replace(a, b)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")


def zip_name(stamm):
    """Dateiname des ZIP mit allen Teilen einer Region."""
    return f"{stamm}_alle_Teile.zip"


def zip_groesse(paare):
    """Groesse eines ZIP ohne Kompression, aus (Name, Groesse)-Paaren der Dateien darin.

    Je Datei ein lokaler Kopf (30 Byte + Name), die Daten und ein Eintrag im
    Verzeichnis (46 Byte + Name); dazu 22 Byte Abschluss. Gilt fuer Dateien unter 4 GB.
    """
    return sum(30 + len(n.encode()) + g + 46 + len(n.encode()) for n, g in paare) + 22


def groesse_lesbar(bytes_):
    """Nur so genau, wie es dem Leser nuetzt: unter 1 MB in KB, darueber in MB, ab 1 GB in GB."""
    mb = bytes_ / 1024 ** 2
    if mb < 1:
        return f"{bytes_ / 1024:.0f} KB"
    if mb < 10:
        return f"{mb:.1f} MB"
    if mb < 1000:
        return f"{mb:.0f} MB"
    return f"{mb / 1024:.1f} GB".replace(".", ",")


def main():
    if not LAYER_DIR.is_dir():
        sys.exit(f"ABBRUCH: Exportordner fehlt: {LAYER_DIR}")

    map_data = json.loads((HERE / "map_data.json").read_text())
    release = json.loads((HERE / "release.json").read_text())
    parts_file = HERE / "map_parts.json"
    karte_teile = json.loads(parts_file.read_text())["regionen"] if parts_file.exists() else {}
    basis = f"https://github.com/{release['repo']}/releases/download/{release['tag']}"

    # Dateien einlesen: ganze Regionen und Teile getrennt
    ganz, teile = {}, {}
    for pfad in sorted(LAYER_DIR.glob("*.img")):
        m = TEIL_RE.match(pfad.name)
        if m:
            teile.setdefault(m.group("stamm"), {})[int(m.group("nr"))] = pfad
        else:
            ganz[pfad.stem] = pfad

    eintraege, verwendet = {}, set()
    for region in map_data["regions"]:
        schluessel = f"{region['iso']}|{region['name']}"
        stamm = dateistamm(region["name"])
        if stamm in teile:
            nummern = sorted(teile[stamm])
            erwartet = list(range(1, len(nummern) + 1))
            if nummern != erwartet:
                sys.exit(f"ABBRUCH {schluessel}: Teile {nummern} - erwartet lueckenlos {erwartet}")
            if schluessel not in karte_teile or karte_teile[schluessel]["anzahl"] != len(nummern):
                sys.exit(f"ABBRUCH {schluessel}: {len(nummern)} Dateien, aber map_parts.json kennt "
                         f"{karte_teile.get(schluessel, {}).get('anzahl', 'keine Teile')}")
            if stamm in ganz:
                sys.exit(f"ABBRUCH {schluessel}: Es gibt die ganze Region UND ihre Teile als Datei")
            liste = []
            for nr in nummern:
                p = teile[stamm][nr]
                liste.append({"nr": nr, "datei": p.name, "bytes": p.stat().st_size,
                              "groesse": groesse_lesbar(p.stat().st_size), "url": f"{basis}/{p.name}"})
            summe = sum(t["bytes"] for t in liste)
            zname = zip_name(stamm)
            vorhanden_zip = LAYER_DIR / "zip" / zname
            zbytes = (vorhanden_zip.stat().st_size if vorhanden_zip.exists()
                      else zip_groesse([(t["datei"], t["bytes"]) for t in liste]))
            if zbytes >= 2 * 1024 ** 3:
                sys.exit(f"ABBRUCH {schluessel}: ZIP waere {groesse_lesbar(zbytes)}, GitHub erlaubt "
                         f"hoechstens 2 GB je Release-Datei")
            eintraege[schluessel] = {
                "vorhanden": True, "geteilt": True, "anzahl": len(liste),
                "bytes": summe, "groesse": groesse_lesbar(summe),
                "datenstand": DATENSTAND.get(region["iso"]), "raster": RASTERWEITE, "teile": liste,
                "zip": {"datei": zname, "bytes": zbytes, "groesse": groesse_lesbar(zbytes),
                        "url": f"{basis}/{zname}", "liegt_vor": vorhanden_zip.exists()}}
            verwendet.add(stamm)
        elif stamm in ganz:
            if schluessel in karte_teile:
                sys.exit(f"ABBRUCH {schluessel}: Karte kennt Teile, aber es liegt nur die ganze Datei vor")
            p = ganz[stamm]
            eintraege[schluessel] = {
                "vorhanden": True, "geteilt": False, "datei": p.name, "bytes": p.stat().st_size,
                "groesse": groesse_lesbar(p.stat().st_size),
                "datenstand": DATENSTAND.get(region["iso"]), "raster": RASTERWEITE,
                "url": f"{basis}/{p.name}"}
            verwendet.add(stamm)
        else:
            if schluessel in karte_teile:
                sys.exit(f"ABBRUCH {schluessel}: Karte kennt Teile, es liegt aber keine Datei vor")
            eintraege[schluessel] = {"vorhanden": False}

    # Dateien, die zu keiner Region der Karte gehoeren, sind kein Fehler, aber sichtbar.
    ohne_region = sorted((set(ganz) | set(teile)) - verwendet)
    (HERE / "downloads.json").write_text(json.dumps(eintraege, ensure_ascii=False))

    vorh = [e for e in eintraege.values() if e["vorhanden"]]
    n_dateien = sum(e["anzahl"] if e.get("geteilt") else 1 for e in vorh)
    gesamt = sum(e["bytes"] for e in vorh)
    print(f"downloads.json: {len(vorh)} Regionen mit Layer ({sum(1 for e in vorh if e['geteilt'])} davon in Teilen), "
          f"{len(eintraege) - len(vorh)} ohne, {n_dateien} Dateien, {groesse_lesbar(gesamt)} gesamt")
    ohne = [k for k, e in eintraege.items() if not e["vorhanden"]]
    print("ohne Layer:", ", ".join(ohne))
    zips = [e["zip"] for e in vorh if e.get("geteilt")]
    print(f"ZIPs mit allen Teilen: {len(zips)} vorgesehen, davon {sum(z['liegt_vor'] for z in zips)} schon "
          f"erzeugt, zusammen {groesse_lesbar(sum(z['bytes'] for z in zips))}")
    if ohne_region:
        print("Dateien ohne Region auf der Karte (z. B. Liechtenstein):", ", ".join(ohne_region))
    print(f"Release-Basis: {basis}")


if __name__ == "__main__":
    main()
