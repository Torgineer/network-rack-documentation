# -*- coding: utf-8 -*-
"""Configuration data for the network rack documentation.

This module contains all user-editable input data used to generate the
network rack documentation PDF. It separates the rack configuration
from the PDF generation logic in ``network_rack_documentation.py``.

The visible PDF content remains in German.
"""


# General information about the network rack.
#
# "title" is displayed as the heading of the rack layout page.
# "total_rack_units" defines the physical size of the cabinet and is
# not calculated from the highest occupied rack unit. This allows
# unoccupied rack units to be displayed correctly as reserve space.
# "subtitle" describes the cabinet and is displayed below the title.
RACK_INFO = {
    "title": "Netzwerkschrank-Aufteilung",
    "total_rack_units": 16,
    "subtitle": (
        '19" Wandschrank, 16 HE, 450 mm Tiefe, Glastür – '
        "Digitus Digital Basic"
    ),
}


# Layout of the network rack.
#
# Each entry describes one component installed in the cabinet.
# Format:
#   (top rack unit, number of rack units, name, subtitle, color)
#
# "top rack unit" is the highest occupied rack unit.
# "number of rack units" is the height of the component in rack units.
# "subtitle" can be empty and is displayed below the component name.
# "color" is the background color of the component in the rack layout.
#
# Components with an identical top rack unit and an identical number of
# rack units share one rack unit row. The PDF generator divides such a
# row equally between all components in the group. For example, two
# entries with (13, 1) are displayed side by side in rack unit 13.
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


# Background color for rack units that are not occupied by a component.
RESERVE_COLOR = "#F5F5F5"


# VLAN reference list displayed above every port table.
#
# Format:
#   (VLAN ID, name)
#
# The order of the entries determines the order in the PDF. The list
# can be empty, in which case no VLAN reference is displayed.
VLAN_REFERENCES = [
    (1, "Default"),
    (10, "Home"),
    (20, "IoT"),
    (30, "Guest"),
    (40, "Camera"),
]


# Components in the network rack.
#
# Each component receives its own page in the generated PDF. The order
# of the entries determines the order of the PDF pages.
#
# Each component requires:
#   "title": Heading of the component page.
#   "ports": List of port entries for the component.
#
# Each port entry uses the following format:
#   (port, destination, VLAN, PoE, remark)
#
# "port" is the port number of the component.
# "destination" is the connected room, device, or connection.
# "VLAN" is the VLAN ID and can be empty for an unassigned VLAN.
# "PoE" contains manually maintained PoE information.
# "remark" is free text for additional information.
#
# Use "\n" inside "destination" or "remark" to create a manual line
# break in the PDF table.
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