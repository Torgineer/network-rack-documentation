# -*- coding: utf-8 -*-
"""Konfigurationsdaten für die Netzwerkschrank-Dokumentation."""


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