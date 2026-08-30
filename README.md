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
| `make_downloads.py` | liest die `.img`-Dateien, erzeugt `downloads.json` |
| `make_country_outlines_v2.py` | berechnet die Länderflächen der Karte |
| `make_contours.py`, `make_topo_bg.py` | Höhenlinien-Hintergrund der Seiten |

Zentrale Einstellungen: `urls.json` (Seitenlinks), `release.json` (Repository
und Release-Tag für die Downloadlinks), `MAIL_ADRESSE` in `build.py`.

## Daten und Lizenzen

Die Geländemodelle sind offene Verwaltungsdaten unter CC BY 4.0. Die
vollständige Namensnennung steht auf der Seite „Kompatibilität und Herkunft
der Daten", in der `LIESMICH.txt` jedes Releases und in jeder `.img`-Datei
selbst.

Der Layer ist ein Hilfsmittel zur Geländebeurteilung und ersetzt weder den
Lawinenlagebericht noch eine Ausbildung in Lawinenkunde.
