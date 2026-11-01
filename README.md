# Hangneigungslayer für Garmin Uhren

Hangneigungskarte für Skitouren als Kartendatei für Garmin Uhren mit
Kartennavigation. Färbt jeden Hang ab 30 Grad ein, liegt offline auf der Uhr.

**Website:** https://monsproduction.github.io/hangneigungslayer/
**Downloads:** unter [Releases](https://github.com/monsproduction/hangneigungslayer/releases)

Derzeit verfügbar: Österreich (9 Bundesländer), Schweiz (26 Kantone) und
Bayern. Frankreich und Italien folgen.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `index.html`, `info.html`, `beispiele.html` | die gebaute Website |
| `screenshots/` | Bilder der Beispielseite |
| `build/` | Vorlagen, Kartendaten und Bauskripte |

Die HTML-Dateien werden **nicht von Hand bearbeitet**, sondern aus den
Vorlagen in `build/` erzeugt:

```
cd build && python3 build.py
```

### Skripte in `build/`

| Skript | Zweck |
|---|---|
| `build.py` | setzt die Vorlagen zu den fertigen Seiten zusammen |
| `make_downloads.py` | Fassung 1: liest die 10-m-`.img`, erzeugt `downloads.json` (nicht mehr benutzt) |
| `make_downloads_v2.py` | liest den 5-m-Export aus `garmin_layers-5m`, erkennt zerlegte Regionen (`_Teil_NN`), gleicht sie mit `map_parts.json` ab |
| `make_zips_v1.py` | packt je zerlegter Region alle Teile in ein ZIP (`garmin_layers-5m/zip/`); ohne Argument nur Trockenlauf, `--erzeugen` schreibt wirklich |
| `make_map_parts_v1.py` | schneidet zerlegte Regionen in ihre Teile zu, erzeugt `map_parts.json` |
| `make_map_data_v2.py` | erzeugt `map_data.json` mit Liechtenstein als sechstem Land; bricht ab, wenn sich eine der 44 bisherigen Regionen aendern wuerde |
| `make_country_outlines_v2.py` | berechnet die Länderflächen der Karte |
| `make_contours.py`, `make_topo_bg.py` | Höhenlinien-Hintergrund der Seiten |

### Zerlegte Regionen

Grosse Regionen (Tirol, Steiermark, Piemont u. a., 11 Stueck) sind im Export in je
zehn Teile zerlegt, jeder Teil ist eine eigene `.img`. Die Karte zeichnet dort die
Teile statt der ganzen Region.

- `teile_plan.json` enthaelt die Rechtecke der Teile. Herkunft und Pruefung stehen
  in der Datei: Alle 110 Kachelzahlen stimmen mit dem Protokoll des Exports ueberein.
- `make_map_parts_v1.py` baut vorher die Projektion nach und bricht ab, wenn sie
  nicht alle 44 vorhandenen Regionspfade bitgenau trifft. Danach prueft es je
  Region: keine Luecke, keine Ueberlappung, kein leerer oder winziger Teil.
- Reihenfolge der Skripte: `make_map_data_v2.py`, `make_country_outlines_v2.py`,
  `make_map_parts_v1.py`, `make_downloads_v2.py`, dann `build.py`. Jedes bricht ab, wenn
  seine Eingabe nicht zur vorherigen Stufe passt.

### ZIP mit allen Teilen

Im Panel einer zerlegten Region gibt es neben den Einzel-Downloads den Knopf
"Alle 10 Teile als ZIP". Das ZIP heisst `Hangneigung_<Region>_alle_Teile.zip` und
enthaelt die zehn `.img` unveraendert (ohne Kompression, die `.img` sind schon dicht).

- `make_downloads_v2.py` traegt das ZIP mit URL und Groesse in `downloads.json` ein. Die
  Groesse wird vorab auf das Byte genau berechnet, die ZIPs muessen zum Bauen der Seite
  also noch nicht existieren. Liegt eins unter `garmin_layers-5m/zip/`, zaehlt dessen echte Groesse.
- Erzeugen: `python3 -I build/make_zips_v1.py --erzeugen` (11 ZIPs, zusammen ca. 4,6 GB;
  groesstes ca. 675 MB, GitHub erlaubt 2 GB je Release-Datei).
- Die ZIPs muessen wie die `.img` ins Release hochgeladen werden, sonst ist der Link tot.

### Liechtenstein

Liechtenstein ist ein eigenes Land mit einer Region (ADM0-Grenze, Farbe Schieferblau).
Es ist auf der Karte klein, rund 12 x 22 Kartenpunkte, und mit derselben Vereinfachung
(0,01 Grad) wie alle Regionen gezeichnet, also nur 14 Ecken. Bis Fassung 2 der Seite
war seine Flaeche den Umrissen der Schweiz zugeschlagen; die Schweiz verliert dadurch
rund 100 Karteneinheiten2.

Die Teile am Rand einer Region reichen bis an deren Rand, auch ueber die letzte
Kachel hinaus (Flachland ohne Daten), damit jede Stelle der Karte zu genau einem
Teil gehoert.

Zentrale Einstellungen: `urls.json` (Seitenlinks), `release.json` (Repository
und Release-Tag für die Downloadlinks), `MAIL_ADRESSE` in `build.py`.

## Daten und Lizenzen

Die Geländemodelle sind offene Verwaltungsdaten unter CC BY 4.0. Die
vollständige Namensnennung steht auf der Seite „Kompatibilität und Herkunft
der Daten", in der `LIESMICH.txt` jedes Releases und in jeder `.img`-Datei
selbst.

Der Layer ist ein Hilfsmittel zur Geländebeurteilung und ersetzt weder den
Lawinenlagebericht noch eine Ausbildung in Lawinenkunde.
