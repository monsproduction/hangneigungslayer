"""Packt die Teile jeder zerlegten Region in EIN ZIP (fuer den Knopf "Alle Teile als ZIP").

Ohne Argument passiert NICHTS auf der Platte: Das Skript zeigt nur, welche ZIPs
entstuenden, wie gross sie waeren und ob der Platz reicht.

  python3 -I build/make_zips_v1.py              Plan anzeigen (Trockenlauf)
  python3 -I build/make_zips_v1.py --erzeugen   ZIPs wirklich schreiben (ca. 4,6 GB)
  python3 -I build/make_zips_v1.py --erzeugen Tirol Kaernten   nur diese Regionen

Ablage: garmin_layers-5m/zip/Hangneigung_<Region>_alle_Teile.zip
Die ZIPs werden OHNE Kompression geschrieben (ZIP_STORED): Die .img sind schon
dicht, Packen braeuchte nur Rechenzeit. Dadurch ist die Groesse vorab bekannt, und
das Skript prueft nach dem Schreiben, dass sie auf das Byte stimmt.
Vorhandene ZIPs werden nicht ueberschrieben. Geschrieben wird erst in eine .part-
Datei, die erst nach erfolgreicher Pruefung ihren Namen bekommt.

Hochladen ins Release macht das Skript NICHT.
"""
import pathlib
import shutil
import sys
import zipfile

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import make_downloads_v2 as dl  # noqa: E402

ZIP_DIR = dl.LAYER_DIR / "zip"
SICHERHEIT = 1.1   # Platzbedarf-Zuschlag


def plan():
    """Je zerlegter Region: (Stamm, Liste der .img, erwartete ZIP-Groesse)."""
    teile = {}
    for pfad in sorted(dl.LAYER_DIR.glob("*.img")):
        m = dl.TEIL_RE.match(pfad.name)
        if m:
            teile.setdefault(m.group("stamm"), []).append(pfad)
    ergebnis = []
    for stamm, pfade in sorted(teile.items()):
        pfade.sort()
        groesse = dl.zip_groesse([(p.name, p.stat().st_size) for p in pfade])
        ergebnis.append((stamm, pfade, groesse))
    return ergebnis


def schreibe(stamm, pfade, erwartet):
    ziel = ZIP_DIR / dl.zip_name(stamm)
    teil = ziel.with_name(ziel.name + ".part")
    with zipfile.ZipFile(teil, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as z:
        for p in pfade:
            z.write(p, arcname=p.name)
    ist = teil.stat().st_size
    if ist != erwartet:
        teil.unlink()
        sys.exit(f"ABBRUCH {stamm}: ZIP hat {ist} Byte, erwartet {erwartet}")
    with zipfile.ZipFile(teil) as z:
        kaputt = z.testzip()
    if kaputt:
        teil.unlink()
        sys.exit(f"ABBRUCH {stamm}: Pruefsumme stimmt nicht bei {kaputt}")
    teil.rename(ziel)
    return ziel


def main():
    args = sys.argv[1:]
    erzeugen = "--erzeugen" in args
    filter_ = [a for a in args if not a.startswith("--")]
    alle = plan()
    if filter_:
        alle = [e for e in alle if any(f.lower() in e[0].lower() for f in filter_)]
        if not alle:
            sys.exit(f"ABBRUCH: keine Region passt zu {filter_}")

    offen = [e for e in alle if not (ZIP_DIR / dl.zip_name(e[0])).exists()]
    print(f"{'Region':<40}{'Teile':>6}{'ZIP-Groesse':>14}  Status")
    for stamm, pfade, g in alle:
        status = "liegt schon vor" if (ZIP_DIR / dl.zip_name(stamm)).exists() else "fehlt"
        grenze = " ZU GROSS (> 2 GB)" if g >= 2 * 1024 ** 3 else ""
        print(f"{stamm:<40}{len(pfade):>6}{dl.groesse_lesbar(g):>14}  {status}{grenze}")
    bedarf = sum(g for _, _, g in offen)
    dl.LAYER_DIR.mkdir(exist_ok=True)
    frei = shutil.disk_usage(dl.LAYER_DIR).free
    print(f"\nzu erzeugen: {len(offen)} ZIPs, {dl.groesse_lesbar(bedarf)}; "
          f"frei auf dem Laufwerk: {dl.groesse_lesbar(frei)}")

    if not erzeugen:
        print("Trockenlauf - nichts geschrieben. Mit --erzeugen wirklich packen.")
        return
    if any(g >= 2 * 1024 ** 3 for _, _, g in offen):
        sys.exit("ABBRUCH: Ein ZIP waere ueber 2 GB (GitHub-Grenze je Release-Datei).")
    if frei < bedarf * SICHERHEIT:
        sys.exit("ABBRUCH: zu wenig freier Platz.")
    ZIP_DIR.mkdir(exist_ok=True)
    for stamm, pfade, g in offen:
        print(f"packe {dl.zip_name(stamm)} ...", flush=True)
        schreibe(stamm, pfade, g)
    print("fertig. Danach make_downloads_v2.py und build.py erneut laufen lassen.")


if __name__ == "__main__":
    main()
