# -*- coding: utf-8 -*-
"""Configuration data for the network rack documentation."""

# General information about the network rack.
RACK_INFO = {
    "title": "Netzwerkschrank-Aufteilung",
    "total_rack_units": 16,
    "subtitle": (
        '19" Wandschrank, 16 HE, 450 mm Tiefe, Glastür – '
        "Digitus Digital Basic"
    ),
}

# Layout of the network rack.
# Format: (top rack unit, number of rack units, name, subtitle, color)
RACK_LAYOUT = [
    (15, 1, "FRITZ!Box 5690 Fiber",
     "", "#FFE0B2"),
    (13, 1, "UniFi Cloud Gateway Ultra",
     "", "#C8E6C9"),
    (13, 1, "UniFi Switch Lite 8 PoE",
     '', "#C8E6C9"),
    (12, 1, "Patchfeld 24 Port",
     "Keystone", "#BBDEFB"),
    (9, 2, "UniFi UNVR Instant",
     "2HE", "#F8BBD0"),
    (7, 1, "Tiny PC Lenovo M720q",
     "", "#D1C4E9"),
    (1, 1, "Steckdosenleiste",
     "", "#FFCC80"),
]

# Color for unoccupied rack units.
RESERVE_COLOR = "#F5F5F5"

# VLAN reference list: (VLAN ID, name)
VLAN_REFERENCES = [
    (1, "Default"),
    (10, "Home"),
    (20, "IoT"),
    (30, "Guest"),
    (40, "Camera"),
]

# Components in the network rack.
# Each component receives its own page in the PDF.
# "ports" contains entries in the format:
# (port, destination, VLAN, PoE, remark)
RACK_COMPONENTS = [
    {
        "title": "Patchpanel-Portplan",
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
        "title": "Switch-Portplan Lite-8-PoE",
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
        "title": "UCG-Ultra-Portplan",
        "ports": [
            (1, "Switch Lite-8-PoE", "1", "Nein", ""),
            (2, "", "", "", ""),
            (3, "", "", "", ""),
            (4, "", "", "", ""),
            (5, "WAN", "", "Nein", "Uplink"),
        ],
    },
]