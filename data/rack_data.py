# -*- coding: utf-8 -*-
"""Konfigurationsdaten für die Netzwerkschrank-Dokumentation."""

# Allgemeine Informationen zum Netzwerkschrank.
RACK_INFO = {
    "titel": "Netzwerkschrank-Aufteilung",
    "gesamt_he": 16,
    "untertitel": (
        '19" Wandschrank, 16 HE, 450 mm Tiefe, Glastür – '
        "Digitus Digital Basic"
    ),
}

# Aufbau des Netzwerkschranks.
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

# Farbe für nicht belegte Höheneinheiten.
RESERVE_COLOR = "#F5F5F5"

# VLAN-Referenzliste: (VLAN-ID, Name)
VLAN_REFERENZ = [
    (1, "Default"),
    (10, "Home"),
    (20, "IoT"),
    (30, "Guest"),
    (40, "Camera"),
]

# Komponenten im Netzwerkschrank.
# Jede Komponente erhält eine eigene Seite in der PDF.
# "ports" enthält Einträge im Format:
# (Port, Ziel, VLAN, PoE, Bemerkung)
RACK_COMPONENTS = [
    {
        "titel": "Patchpanel-Portplan",
        "ports": [
            (1, "Flur 1", "", "", "WAN"),
            (2, "Büro", "1", "Ja", "Access Point - U7 In-Wall"),
            (3, "Wohnzimmer", "1", "Ja", "Access Point - U6+"),
            (4, "Flur 2", "1", "Ja", "Access Point - U7-Pro-XG"),
            (5, "Schlafzimmer", "", "", ""),
            (6, "", "", "", ""),
            (7, "", "", "", ""),
            (8, "", "", "", ""),
            (9, "", "", "", ""),
            (10, "", "", "", ""),
            (11, "", "", "", ""),
            (12, "", "", "", ""),
            (13, "", "", "", ""),
            (14, "", "", "", ""),
            (15, "", "", "", ""),
            (16, "", "", "", ""),
            (17, "", "", "", ""),
            (18, "", "", "", ""),
            (19, "", "", "", ""),
            (20, "", "", "", ""),
            (21, "", "", "", ""),
            (22, "", "", "", ""),
            (23, "", "", "", ""),
            (24, "", "", "", ""),
        ],
    },
    {
        "titel": "Switch-Portplan Lite-8-PoE",
        "ports": [
            (1, "Patchpanel Port 2\nBüro: Access Point - U7 In-Wall", "1", "Ja", ""),
            (2, "Patchpanel Port 3\nWohnzimmer: Access Point - U6+", "1", "Ja", ""),
            (3, "Patchpanel Port 4\nFlur: Access Point - U7-Pro-XG", "1", "Ja", ""),
            (4, "", "", "Ja", ""),
            (5, "Proxmox Host M720q", "1", "Nein", ""),
            (6, "", "", "Nein", ""),
            (7, "", "", "Nein", ""),
            (8, "UCG-Ultra LAN out", "", "Nein", ""),
        ],
    },
    {
        "titel": "UCG-Ultra-Portplan",
        "ports": [
            (1, "Switch Lite-8-PoE", "1", "Nein", ""),
            (2, "", "", "", ""),
            (3, "", "", "", ""),
            (4, "", "", "", ""),
            (5, "WAN", "", "Nein", "Uplink"),
        ],
    },
]