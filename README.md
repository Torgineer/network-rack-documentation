# Netzwerkschrank-Dokumentation

Python-Skript zum Erstellen einer Netzwerkschrank-Dokumentation als PDF. Die Eingabedaten liegen in `data/rack_data.py`. Die PDF-Erstellung befindet sich in `network_rack_documentation.py`.

Die PDF enthält standardmäßig die Aufteilung des Netzwerkschranks sowie separate Seiten für Patchpanel, Switch und UCG-Ultra. Jede Komponente erhält eine eigene Überschrift und eine eigene Porttabelle. Neue Komponenten werden ausschließlich in der Datendatei ergänzt.

## Funktionen

- Rack-Aufteilung als erste Seite der PDF.
- Automatische Berechnung der Rack-Größe anhand von `RACK_INFO["gesamt_he"]`.
- Automatische Darstellung nicht belegter Höheneinheiten als Reserve.
- Separate Portpläne für Patchpanel, Switch und UCG-Ultra in einer PDF.
- Automatische Erzeugung einer PDF-Seite pro Komponente aus `RACK_COMPONENTS`.
- VLAN-Referenzliste über jeder Porttabelle.
- Tabelle mit den Spalten **Port**, **Ziel**, **VLAN**, **PoE** und **Bemerkung**.
- A4-Hochformat als Standard, optional A4-Querformat.
- Aktuelles lokales Datum und Uhrzeit in der PDF.
- Optionaler Zeitstempel im Dateinamen.
- An das Seitenformat angepasste Spaltenbreiten.
- Automatischer Zeilenumbruch für längere Einträge.
- Wiederholung des Tabellenkopfs auf Folgeseiten.
- Seitenzahlen in der Fußzeile.
- Abwechselnde Zeilenfarben zur besseren Lesbarkeit.

## Voraussetzungen

- Python 3
- Python-Paket `reportlab`

## Installation

Öffne ein Terminal im Projektordner und installiere die Abhängigkeit:

```bash
python -m pip install reportlab
```

Unter Windows kannst du alternativ den Python-Launcher verwenden:

```powershell
py -m pip install reportlab
```

## Verwendung

1. Öffne `data/rack_data.py`.
2. Passe `RACK_INFO`, `RACK_LAYOUT`, die VLAN-Referenzliste und `RACK_COMPONENTS` an.
3. Passe bei Bedarf die Einstellungen in `network_rack_documentation.py` an.
4. Speichere die Dateien und starte das Skript aus dem Projektstammverzeichnis:

```bash
python network_rack_documentation.py
```

Unter Windows alternativ:

```powershell
py network_rack_documentation.py
```

Die PDF wird im Unterordner `output` neben der Python-Datei gespeichert. Der Ordner wird bei Bedarf automatisch angelegt. Nach erfolgreicher Erstellung gibt das Skript den vollständigen Pfad zur PDF im Terminal aus.

## Netzwerkschrank konfigurieren

Die allgemeinen Angaben zum Netzwerkschrank befinden sich in `RACK_INFO` in `data/rack_data.py`:

```python
RACK_INFO = {
    "titel": "Netzwerkschrank-Aufteilung",
    "gesamt_he": 16,
    "untertitel": (
        '19" Wandschrank, 16 HE, 450 mm Tiefe, Glastür – '
        "Digitus Digital Basic"
    ),
}
```

| Feld | Bedeutung |
| --- | --- |
| `titel` | Überschrift der Rack-Aufteilungsseite |
| `gesamt_he` | Gesamtanzahl der Höheneinheiten des Schranks |
| `untertitel` | Beschreibung des Schranks |

Die Rack-Größe wird über `gesamt_he` festgelegt. Sie wird nicht aus der höchsten belegten Höheneinheit berechnet. Dadurch können freie Höheneinheiten korrekt als Reserve dargestellt werden.

## Rack-Aufteilung konfigurieren

Die Liste `RACK_LAYOUT` in `data/rack_data.py` definiert die im Schrank verbauten Komponenten:

```python
# Format: (oberste HE, Anzahl HE, Name, Untertitel, Farbe)
RACK_LAYOUT = [
    (15, 1, "FRITZ!Box 5690",
     "auf Fachboden, WAN von hinten", "#FFE0B2"),
    (13, 1, "UniFi Cloud Gateway Ultra",
     "1U-Rackmount, direkt unter FRITZ!Box", "#C8E6C9"),
    (12, 1, "Patchfeld 24 Port",
     "CAT7 von oben, Anschluss von hinten", "#BBDEFB"),
    (11, 1, "UniFi Switch Lite 8 PoE",
     '19"-Rackmount, direkt unter Patchfeld', "#C8E6C9"),
    (9, 2, "UniFi UNVR Instant",
     "2U-Rackmount – belegt HE 8 und 9", "#F8BBD0"),
    (7, 1, "Tiny PC Lenovo M720q",
     "auf Fachboden", "#D1C4E9"),
    (1, 1, "Steckdosenleiste",
     "Netzkabel getrennt von Datenkabeln", "#FFCC80"),
]
```

| Feld | Bedeutung | Beispiel |
| --- | --- | --- |
| Oberste HE | Höchste belegte Höheneinheit der Komponente | `15` |
| Anzahl HE | Anzahl der belegten Höheneinheiten | `2` |
| Name | Bezeichnung der Komponente | `"UniFi UNVR Instant"` |
| Untertitel | Zusätzliche Montage- oder Anschlussinformation | `"2U-Rackmount"` |
| Farbe | Hintergrundfarbe in der Rack-Darstellung | `"#F8BBD0"` |

Eine Komponente mit `top = 9` und `span = 2` belegt beispielsweise die Höheneinheiten 8 und 9. Die Reihenfolge der Einträge in `RACK_LAYOUT` hat keinen Einfluss auf die Darstellung; die Komponenten werden nach ihrer Position im Rack sortiert.

Nicht belegte Höheneinheiten werden automatisch als Reserve ergänzt und mit `RESERVE_COLOR` dargestellt:

```python
RESERVE_COLOR = "#F5F5F5"
```

Das Skript prüft, ob Höheneinheiten außerhalb des Schranks liegen oder doppelt belegt sind. Bei einem ungültigen Layout wird die PDF-Erstellung mit einer Fehlermeldung abgebrochen.

## VLAN-Referenzliste konfigurieren

Die Liste `VLAN_REFERENZ` in `data/rack_data.py` definiert die VLANs, die über jeder Porttabelle in der PDF angezeigt werden. Jeder Eintrag besteht aus der VLAN-ID und einem frei wählbaren Namen:

```python
# VLAN-Referenzliste: (VLAN-ID, Name)
VLAN_REFERENZ = [
    (1, "Default"),
    (10, "Home"),
    (20, "IoT"),
    (30, "Guest"),
    (40, "Camera"),
]
```

In der PDF erscheint die Liste beispielsweise so:

```text
VLAN 1 – Default
VLAN 10 – Home
VLAN 20 – IoT
VLAN 30 – Guest
VLAN 40 – Camera
```

Die Reihenfolge in `VLAN_REFERENZ` bestimmt die Reihenfolge in der PDF. Wenn die Liste leer ist, wird keine VLAN-Referenzliste ausgegeben.

## Komponenten konfigurieren

Die Liste `RACK_COMPONENTS` in `data/rack_data.py` definiert alle Komponenten, für die eine eigene PDF-Seite erzeugt wird. Jede Komponente benötigt einen Titel und eine Portliste:

```python
RACK_COMPONENTS = [
    {
        "titel": "Patchpanel-Portplan",
        "ports": [
            (1, "Flur 1", "", "", "WAN"),
            (2, "Büro", "1", "Ja", "Access Point - U7 In-Wall"),
            (3, "Wohnzimmer", "1", "Ja", "Access Point - U6+"),
            (4, "Flur 2", "1", "Ja", "Access Point - U7-Pro-XG"),
            (5, "Schlafzimmer", "", "", ""),
        ],
    },
    {
        "titel": "Switch-Portplan Lite-8-PoE",
        "ports": [
            (1, "Patchpanel Port 2\nBüro: Access Point - U7 In-Wall", "1", "Ja", ""),
            (2, "Patchpanel Port 3\nWohnzimmer: Access Point - U6+", "1", "Ja", ""),
            (3, "Patchpanel Port 4\nFlur: Access Point - U7-Pro-XG", "1", "Ja", ""),
            (5, "Proxmox Host M720q", "1", "Nein", ""),
            (8, "UCG-Ultra LAN out", "", "Nein", ""),
        ],
    },
    {
        "titel": "UCG-Ultra-Portplan",
        "ports": [
            (1, "Switch Lite-8-PoE", "1", "Nein", ""),
            (5, "WAN", "", "Nein", "Uplink"),
        ],
    },
]
```

| Feld | Bedeutung |
| --- | --- |
| `titel` | Überschrift der PDF-Seite |
| `ports` | Liste der Port-Einträge dieser Komponente |

Jeder Port-Eintrag enthält fünf Werte:

```python
# (Port, Ziel, VLAN, PoE, Bemerkung)
(1, "Flur 1", "", "", "WAN"),
```

| Feld | Bedeutung | Beispiel |
| --- | --- | --- |
| Port | Portnummer der jeweiligen Komponente | `1` |
| Ziel | Raum, Anschluss oder angeschlossenes Gerät | `"Wohnzimmer"` |
| VLAN | VLAN-ID des Anschlusses | `"1"`, `"10"` oder `""` |
| PoE | Manuell eingetragene PoE-Angabe | `"Ja"`, `"Nein"` oder `""` |
| Bemerkung | Freitext für zusätzliche Informationen | `"Uplink"` |

Die VLAN-Angabe kann als Text, etwa `"10"`, oder als Zahl, etwa `10`, eingetragen werden. Für nicht zugewiesene VLANs kann das Feld leer bleiben.

Die Reihenfolge der Einträge in `RACK_COMPONENTS` bestimmt die Reihenfolge der PDF-Seiten. Die Reihenfolge der Port-Einträge bestimmt die Reihenfolge in der jeweiligen Tabelle. Jeder Port-Eintrag muss genau fünf Werte enthalten.

Die mitgelieferten Belegungen sind Beispiele. Das Skript übernimmt die Angaben unverändert; es erkennt oder prüft keine Netzwerkverbindungen, VLAN-Zuordnungen oder PoE-Versorgung.

## Neue Komponente hinzufügen

Um beispielsweise ein zweites Patchpanel hinzuzufügen, ergänze in `data/rack_data.py` einen weiteren Eintrag in `RACK_COMPONENTS`:

```python
{
    "titel": "Patchpanel 2 – Portplan",
    "ports": [
        (1, "Keller", "", "", ""),
        (2, "Terrasse", "", "", ""),
    ],
},
```

Das Hauptskript muss dafür nicht angepasst werden. Die neue Komponente erhält automatisch eine eigene Seite in derselben PDF.

## Zeilenumbrüche in Zellen

Für einen manuellen Zeilenumbruch innerhalb einer Zelle verwende `\n`:

```python
(1, "Patchpanel Port 1\nFlur: Access Point - U7-Pro-XG", "1", "Ja", ""),
```

In der PDF wird daraus:

```text
Patchpanel Port 1
Flur: Access Point - U7-Pro-XG
```

Das funktioniert in allen Textfeldern eines Port-Eintrags, also in **Ziel** und **Bemerkung**.

## Einstellungen

Die Einstellungen für Titel, Seitenformat, Dateiname und Ausgabeordner befinden sich oben in `network_rack_documentation.py`.

### Titel

```python
TITEL = "Netzwerkschrank – Dokumentation"
```

### Seitenformat

```python
HOCHFORMAT = True
```

- `True`: A4-Hochformat.
- `False`: A4-Querformat.

Beim regulären Skriptstart wird dieser Wert an die Funktion übergeben:

```python
if __name__ == "__main__":
    erstelle_pdf(hochformat=HOCHFORMAT)
```

Bei einem direkten Funktionsaufruf ist Hochformat der Standard:

```python
erstelle_pdf()                  # A4-Hochformat
erstelle_pdf(hochformat=False)  # A4-Querformat
```

### Datum und Uhrzeit

Der Zeitstempel wird bei jedem Funktionsaufruf neu erzeugt. Die sichtbare Datumszeile verwendet folgendes Format:

```text
Stand: 26.10.2026 – 17:25 Uhr
```

Das Format wird innerhalb von `erstelle_pdf()` festgelegt:

```python
unterzeile = erstellt_am.strftime("Stand: %d.%m.%Y – %H:%M Uhr")
```

### Dateiname

```python
ZEITSTEMPEL_IM_DATEINAMEN = True
```

Mit `True` enthält der Dateiname Datum und Uhrzeit einschließlich Sekunden:

```text
netzwerkschrank_dokumentation_2026-10-26_17-25-00.pdf
```

Mit `False` wird immer derselbe Dateiname verwendet:

```text
netzwerkschrank_dokumentation.pdf
```

Eine vorhandene Datei gleichen Namens wird überschrieben. Auch mit aktiviertem Zeitstempel können zwei Aufrufe innerhalb derselben Sekunde denselben Dateinamen erzeugen.

### Ausgabeordner

```python
AUSGABEORDNER = Path(__file__).resolve().parent / "output"
```

Standardmäßig liegt der Ausgabeordner neben dem Hauptskript. Für einen anderen Ordner passe diese Variable an.

## Projektstruktur

```text
network-rack-documentation/
├── data/
│   ├── .gitignore
│   └── rack_data.py
├── .gitignore
├── network_rack_documentation.py
├── README.md
└── output/
    └── .gitignore
```