# Website-Text

Alle Texte, die aktuell auf der Website erscheinen — sortiert nach Seite und Abschnitt,
in der Reihenfolge, in der sie auf der Seite vorkommen. Jeder Textblock trägt in eckigen
Klammern eine kurze Markierung, was für ein Element es ist (Überschrift, Absatz, Button,
Tabellenzelle, ...), damit die Zuordnung beim Wiedereinsetzen eindeutig bleibt.

Nicht enthalten: reiner Code, CSS-Kommentare, IDs/Klassennamen, Zahlenwerte in
Platzhalter-Statistiken (die sind zufällig generiert, kein echter Text).

---

## Seite 1: Startseite (index.html)

### Browser-Tab / Meta
- [Title] Hangneigungslayer für Garmin Uhren
- [Meta-Description] Hangneigungskarte für Skitouren als Kartendatei für Garmin Uhren mit Kartennavigation. Potenzielles Lawinengelände ab 30 Grad, offline am Handgelenk.

### Navigation
- [Markenname] Hangneigungslayer für Garmin Uhren
- [Nav-Link] Vorteile
- [Nav-Link] Hangneigungsklassen
- [Nav-Link] Download
- [Nav-Link] Einrichtung
- [Nav-Link] Kompatibilität
- [Nav-Link, Menü] Feedback senden
- [Button] Feedback senden  → mailto:hangneigungslayer@proton.me

### Hero (Kopfbereich)
- [Eyebrow] Skitouren · Freeride · Skibergsteigen
- [H1] Der Hangneigungslayer: Direkt an deinem Handgelenk.
- [Lede/Absatz] Der Hangneigungslayer färbt jeden Hang ab 30 Grad ein. Bisher gab es ihn nur in Karten-Apps am Handy. Jetzt liegt er als Kartendatei auf deiner Garmin Uhr, offline und schnell verfügbar.
- [Button, primär] Download
- [Button, sekundär] Passt meine Uhr?
- [Eyebrow, Legende] Hangneigungsklassen im Layer
- [Legenden-Label] 30°
- [Legenden-Label] 35°
- [Legenden-Label] 40°
- [Legenden-Label] 45°
- [Legenden-Label] 50°+

### Abschnitt „Vorteile" (#handgelenk)
- [Eyebrow] Vorteile
- [H2] Im Gelände zählt, wie schnell du nachsehen kannst.
- [Absatz] Viele Skitourengeher navigieren heute schon mit ihrer Sportuhr oder tracken die Aktivität. Die Uhr ist dann eh schon am Handgelenk. Ein schneller Blick genügt nun, um die Steilheit der näheren Umgebung zu checken und seine Route evtl. anzupassen.

**Vergleichstabelle:**

| | Am Handy | An der Uhr |
|---|---|---|
| Zugriff | Aus der Tasche holen, entsperren | Ärmel hochschieben |
| Handschuhe | Ausziehen | Bleiben an |
| Kälte und Nässe | Akku bricht ein, Gerät wird nass | Bleibt geschützt am Arm |

### Abschnitt „Was der Layer zeigt" (#klassen)
- [Eyebrow] Was der Layer zeigt
- [H2] Fünf Farben, fünf Neigungsbereiche.
- [Absatz] Flächen unter 30 Grad bleiben transparent, damit die darunterliegende Karte lesbar bleibt. Ab 30 Grad beginnt die Einfärbung. Ein geladener Track und die eigene Position werden immer über dem Hangneigungslayer dargestellt.

**Klassentabelle:**

| Farbe | Hangneigung |
|---|---|
| Gelb | 30 bis 35° |
| Orange | 35 bis 40° |
| Pink | 40 bis 45° |
| Lila | 45 bis 50° |
| Grau | ab 50° |

### Abschnitt „Grenzen" (#grenzen)
- [Eyebrow] Grenzen
- [H2] Was der Layer nicht leistet.
- [H3] Er ist ein Hilfsmittel, keine Entscheidung.
- [Absatz] Der Layer zeigt die Neigung des Geländes. Alles Weitere bleibt deine Beurteilung und die deiner Ausbildung.
- [H3] Er ist so genau wie das Geländemodell.
- [Absatz] Gerechnet auf einem 10-Meter-Raster. Schmale Rinnen und kurze Steilstufen fallen durch dieses Raster und erscheinen nicht.
- [H3] Aktualität der Daten.
- [Absatz] Es wurden nach Möglichkeit die aktuellsten Daten verarbeitet, aber gerade im vergletscherten Gebirge können sich die Gegebenheiten schnell ändern.
- [H3] Er ist kein Ersatz für die Planung.
- [Absatz] Die Tourenplanung gehört an den großen Bildschirm. Auf der Uhr geht es um die Kontrolle im Gelände.

### Abschnitt „Regionsauswahl / Karte" (#karte)
- [Eyebrow] Regionsauswahl
- [H2] Bundesland, Kanton, Region.
- [Absatz] 44 Verwaltungseinheiten aus fünf Alpenländern. Jede Region ist eine eigene Kartendatei, damit auf der Uhr nur liegt, was du brauchst. Klicke eine Region an.
- [Hinweistext über der Karte] Demo-Umrisse, vereinfacht aus echten Verwaltungsgrenzen
- [Leerzustand-Text im Seitenpanel] Wähle eine Region aus, um Datenstand und Download zu sehen.
- [Panel, nach Regionsauswahl — Statistik-Label] Dateigröße
- [Panel, nach Regionsauswahl — Statistik-Label] Datenstand
- [Panel, nach Regionsauswahl — Statistik-Label] Rasterweite
- [Panel-Button] .img herunterladen
- [Panel, Hinweistext] Platzhalter-Werte. In der echten Version verweist der Button auf die erzeugte Kartendatei für {Regionsname}.

### Abschnitt „Einrichtung" (#einrichtung)
- [Eyebrow] Einrichtung
- [H2] Einmal einrichten, dann liegt der Layer dauerhaft auf der Uhr.
- [Absatz] Rechne mit etwa fünf Minuten. Die Menübezeichnungen unterscheiden sich je nach Modell und Software-Stand geringfügig.
- [Voraussetzungs-Chip] Garmin Uhr mit Kartennavigation
- [Voraussetzungs-Chip] USB-Datenkabel
- [Voraussetzungs-Chip] ca. 200 MB freier Speicher je Region

**Schritt 1**
- [H3] Region herunterladen
- [Absatz] Oben in der Karte die gewünschte Region wählen und die `.img`-Datei herunterladen.

**Schritt 2**
- [H3] Datei auf die Uhr kopieren
- [Absatz] Uhr per USB anschließen. Die Datei unverändert in den Ordner `\GARMIN\` kopieren, dann das Laufwerk auswerfen und die Uhr abstecken. Bei einem Mac muss evtl. die Software OpenMTP installiert werden.
- [Absatz, "Warum"-Hinweis] Du kannst mehrere Layer auf die Uhr kopieren. Die werden dann nebeneinander dargestellt und du kannst einzelne Layer auch in der Uhr ausblenden.

**Schritt 3**
- [H3] Layer aktivieren und gegenprüfen
- [Absatz] Auf der Kartendatenseite in einer Aktivität `MENU` gedrückt halten, dann `Aktivitätseinstellungen` → `Karte` → `Karten konfigurieren`.
- [Absatz, "Warum"-Hinweis] Hier können die einzelnen Layer aktiviert und deaktiviert werden.


### Footer
- [H3] Rückmeldung
- [Absatz] Der Hangneigungslayer bleibt kostenlos und werbefrei. Fehler, fehlende Regionen oder Erfahrungen von der Uhr sind willkommen.
- [Button] Feedback senden  → mailto:hangneigungslayer@proton.me
- [Adresse im Klartext] hangneigungslayer@proton.me
- [Spaltentitel] Seite
- [Link] Vorteile
- [Link] Hangneigungsklassen
- [Link] Download
- [Link] Einrichtung
- [Spaltentitel] Technik
- [Link] Kompatible Modelle
- [Link] So entsteht der Layer
- [Link] Datenquellen
- [Spaltentitel] Kontakt
- [Link] Fehler melden  → mailto, Betreff „Fehler melden: "
- [Link] Region vorschlagen  → mailto, Betreff „Regionsvorschlag: "
- [Fußzeile links] Hangneigungslayer für Garmin Uhren · Konzeptentwurf
- [Fußzeile rechts] 44 Regionen · 5 Länder

### Schwebende Hinweise (immer sichtbar / bei Klick)
- [Konzept-Badge, unten rechts] Konzeptentwurf · ohne echte Funktionen
- [Toast bei Klick auf Download-Button] Noch keine Funktion. Der Download kommt in der echten Version.
- [Toast bei Klick auf sonstige Platzhalter-Links] Konzeptentwurf. Diese Funktion ist noch nicht angebunden.

---

## Seite 2: Kompatibilität und Herkunft der Daten (info.html)

### Browser-Tab / Meta
- [Title] Kompatibilität und Herkunft der Daten
- [Meta-Description] Welche Garmin Uhren den Hangneigungslayer darstellen, wie der Layer aus offenen Geländemodellen entsteht und welche Datenquellen und Lizenzen dahinterstehen.

### Navigation
- [Markenname] Hangneigungslayer für Garmin Uhren
- [Nav-Link] Kompatibilität
- [Nav-Link] So entsteht der Layer
- [Nav-Link] Quellen & Rechte
- [Nav-Link, Menü] Zur Karte
- [Button] Zur Karte

### Kopfbereich
- [Eyebrow] Technische Grundlagen
- [H1] Kompatibilität und Herkunft der Daten.
- [Lede/Absatz] Welche Uhren den Layer darstellen, wie er aus offenen Geländemodellen der Alpenländer entsteht und unter welchen Lizenzen die zugrunde liegenden Daten stehen.

### Abschnitt „Geräte" (#kompatibilitaet)
- [Eyebrow] Geräte
- [H2] Zeigt deine Uhr eine Karte, funktioniert der Layer.
- [Absatz] Der Layer ist eine gewöhnliche Garmin-Kartendatei. Prüfen kannst du das in zehn Sekunden: `MENU` gedrückt halten, dann `Karte` öffnen. Gibt es dort `Kartendesign` oder eine Liste installierter Karten, passt deine Uhr.

**Gerätetabelle:**

| Serie | Modelle mit Kartendarstellung |
|---|---|
| fēnix | 5X · 5 Plus · 5X Plus · 6 Pro · 6S Pro · 6X Pro · 7S · 7 · 7X · 7 Pro · 8 · 8 Pro · E · 9 · 9 Pro |
| epix | epix (Gen 2) · epix Pro (Gen 2) |
| Enduro | 2 · 3 |
| Forerunner | 945 · 955 · 965 · 970 |
| MARQ | Gen 1 und Gen 2, alle Editionen |
| Descent | Mk2 · Mk2i · Mk2S · Mk3 · Mk3i |
| tactix | Delta · 7 · 8 |
| quatix | 6 · 6X · 7 · 8 |
| D2 | Delta PX · Mach 1 |

- [Hinweis] Zu den Namen: S und X sind Gehäusegrößen, Pro und Sapphire bezeichnen die Ausstattung, Solar hat mit der Kartenfunktion nichts zu tun. Varianten der oben genannten Modelle sind also mit eingeschlossen. Einzige wichtige Ausnahme: bei der fēnix 6 entscheidet der Pro-Zusatz über die Karten.
- [Hinweis] Ohne Kartendarstellung: Instinct, Venu, vívoactive, Lily, vívomove, Forerunner unterhalb der 945 sowie die fēnix 6 und 6S ohne Pro. Die Übersicht ist nach bestem Wissen erstellt und altert mit jeder Modellgeneration. Verbindlich ist der Test an deiner Uhr.

### Abschnitt „Herkunft / So entsteht der Layer" (#dokumentation)
- [Eyebrow] Herkunft
- [H2] So entsteht der Layer.
- [Absatz] Grundlage sind digitale Geländemodelle, die die Vermessungsverwaltungen der Alpenländer als offene Daten bereitstellen. Aus der Höhe wird die Neigung gerechnet, aus der Neigung werden Flächen, aus den Flächen wird eine Garmin-Kartendatei.

**Ablaufschritte (Pipeline):**
1. [H3] Geländemodell beziehen — [Absatz] Je Region das amtliche digitale Geländemodell laden, meist als GeoTIFF-Kacheln mit 1 bis 10 Metern Rasterweite. Quellen und Lizenzen stehen weiter unten.
2. [H3] In QGIS zusammenführen — [Absatz] Die Kacheln werden über `gdalbuildvrt` zu einem virtuellen Raster verbunden, auf ein gemeinsames Koordinatensystem reprojiziert und einheitlich auf 10 Meter resampelt. Erst dadurch passen die Regionen an ihren Grenzen zusammen.
3. [H3] Neigung berechnen — [Absatz] Aus dem Höhenraster entsteht mit `gdaldem slope`, in QGIS unter Raster / Analyse / Steigung, je Rasterzelle die Hangneigung in Grad.
4. [H3] In fünf Klassen einteilen — [Absatz] Der Raster-Rechner teilt die Grad-Werte in die Klassen ab 30, 35, 40, 45 und 50 Grad. Alles unter 30 Grad wird auf NoData gesetzt und fällt damit heraus.
5. [H3] Vektorisieren und ausdünnen — [Absatz] `gdal_polygonize` macht aus den klassifizierten Zellen zusammenhängende Polygone. Anschließend werden Kleinstflächen verworfen und die Umrisse nach Douglas-Peucker vereinfacht, weil sie auf einem Uhrendisplay ohnehin nicht auflösen und die Datei sonst unnötig wächst.
6. [H3] Zur Garmin-Karte kompilieren — [Absatz] Die Polygone gehen als OSM-XML an `mkgmap`, zusammen mit einer eigenen Style-Datei und einer TYP-Datei. Die Style-Datei ordnet jeder Klasse einen eigenen Flächentyp zu, die TYP-Datei legt fest, in welcher Farbe die Uhr diesen Typ zeichnet. Ergebnis ist eine einzelne `.img`-Datei je Region.

**Vier kurze Erläuterungen:**
- [H4] Warum keine Transparenz? — [Absatz] Das Kartenformat der Uhren unterstützt echte Flächentransparenz nicht zuverlässig. Deshalb kommen kräftige Volltonfarben zum Einsatz. Auf einem kleinen Display sind sie besser lesbar als ein durchscheinender Effekt, der bei diesen Größen kaum sichtbar wäre. Der Track und der aktuelle Standort sind aber immer über dem Layer.
- [H4] Warum je Region eine Datei? — [Absatz] Der Speicher auf der Uhr ist begrenzt und große Kartendateien verlangsamen den Kartenaufbau spürbar. Eine Datei je Verwaltungseinheit hält die Dateien klein und lässt sich sauber wieder entfernen.
- [H4] Warum 10 Meter Rasterweite? — [Absatz] Feinere Raster erzeugen deutlich mehr Polygone, ohne auf dem Display sichtbaren Gewinn. 10 Meter ist der Kompromiss zwischen Dateigröße, Zeichengeschwindigkeit und ausreichender Geländetreue (gleiche Auflösung wie bei swisstopo).
- [H4] Wie aktuell sind die Daten? — [Absatz] Der Datenstand richtet sich nach der jeweiligen Vermessungsverwaltung und ist je Region in der Kartenauswahl angegeben. Das Gelände ändert sich langsam, ein älterer Stand ist für die Neigung unkritisch (außer bei vergletschertem Gelände).

### Abschnitt „Quellen und Rechte" (#rechte)
- [Eyebrow] Quellen und Rechte
- [H2] Offene Daten, mit Namensnennung.
- [Absatz] Alle verwendeten Geländemodelle sind offene Verwaltungsdaten. Die jeweilige Lizenz verlangt eine Nennung der Quelle, die hier erfolgt und in der echten Version zusätzlich jeder Kartendatei beiliegt.

**Quellentabelle:**

| Gebiet | Quelle | Lizenz |
|---|---|---|
| Österreich | Geoland.at, Digitales 10m – Geländemodell aus Airborne Laserscan Daten | CC BY 4.0 |
| Schweiz | DTM Switzerland 10m v2 by Sonny (sonny.4lima.de), Grunddaten swisstopo (OGD) | CC BY 4.0 |
| Bayern | Bayerische Vermessungsverwaltung, DGM5, www.geodaten.bayern.de | CC BY 4.0 |
| Verwaltungsgrenzen | geoBoundaries.org, ADM1 | CC BY 4.0 |

- [Hinweis] Aufgeführt sind nur Quellen, aus denen tatsächlich Layer erzeugt wurden. Für Frankreich und Italien folgen die Angaben, sobald die Daten dort beschafft sind. Der bayerische Layer deckt nur den Alpenraum ab, nicht das gesamte Bundesland.
- [Hinweis] Der Layer selbst ist ein abgeleitetes Werk dieser Daten. Aus dem Höhenmodell wurde die Hangneigung berechnet, in fünf Klassen eingeteilt, vektorisiert und in das Garmin-Kartenformat überführt. Er wird kostenlos weitergegeben und ist ein Hilfsmittel zur Geländebeurteilung, das weder den Lawinenlagebericht noch eine Ausbildung in Lawinenkunde ersetzt.

### Footer
- [Fußzeile links] Hangneigungslayer für Garmin Uhren · Konzeptentwurf
- [Fußzeile rechts, Link] Zurück zur Karte

### Schwebende Hinweise
- [Konzept-Badge, unten rechts] Konzeptentwurf · ohne echte Funktionen
- [Toast bei Klick auf Platzhalter-Links] Konzeptentwurf. Diese Funktion ist noch nicht angebunden.

---

## Hinweis zum Wiedereinsetzen

Beim Zurückspielen der überarbeiteten Texte am besten die Markierungen `[...]` als
Anker nutzen und die Reihenfolge beibehalten — dann lässt sich jeder Block eindeutig
der passenden Stelle in `build/index_template.html` bzw. `build/info_template.html`
zuordnen. Tabellenüberschriften, feste Fachbegriffe in Code-Formatierung (z. B.
`MENU`, `\GARMIN\`, `Kartendesign`) und die Gerätenamen in der Kompatibilitätstabelle
sind technische Angaben, keine freien Texte — die sollten beim Umschreiben unverändert
bleiben, sofern sich an der Sache nichts ändert.
