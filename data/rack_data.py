# -*- coding: utf-8 -*-
"""Configuration data for the network rack documentation.

This module contains all user-editable input data used to generate the
network rack documentation PDF. It separates the rack configuration
from the PDF generation logic in ``network_rack_documentation.py``.

The visible PDF content remains in German.
"""

from __future__ import annotations

from data.models import (
    PortEntry,
    PortPlan,
    RackComponent,
    RackInfo,
    VlanReference,
)


# General information about the network rack.
#
# "title" is displayed as the heading of the rack layout page.
# "total_rack_units" defines the physical size of the cabinet and is
# not calculated from the highest occupied rack unit. This allows
# unoccupied rack units to be displayed correctly as reserve space.
# "subtitle" describes the cabinet and is displayed below the title.
RACK_INFO: RackInfo = RackInfo(
    title="Netzwerkschrank-Aufteilung",
    total_rack_units=16,
    subtitle=(
        '19" Wandschrank, 16 HE, 450 mm Tiefe, Glastür – '
        "Digitus Digital Basic"
    ),
)


# Layout of the network rack.
#
# Each entry describes one component installed in the cabinet.
#
# "top_unit" is the highest occupied rack unit.
# "unit_count" is the height of the component in rack units.
# "name" is the label shown in the rack layout.
# "color" is the background color of the component in the rack layout.
# "subtitle" can be omitted and is displayed below the component name.
#
# Components with an identical top unit and an identical unit count
# share one rack unit row. The PDF generator divides such a row equally
# between all components in the group. For example, two entries with
# top_unit=13 and unit_count=1 are displayed side by side in rack
# unit 13.

# Background color for rack units that are not occupied by a component.
RESERVE_COLOR: str = "#F5F5F5"

RACK_LAYOUT: list[RackComponent] = [
    RackComponent(
        top_unit=15, unit_count=1,
        name="FRITZ!Box 5690 Fiber",
        color="#FFE0B2",
    ),
    RackComponent(
        top_unit=13,
        unit_count=1,
        name="UniFi Switch Lite 8 PoE",
        color="#C8E6C9",
        column=0,
    ),
    RackComponent(
        top_unit=13,
        unit_count=1,
        name="UniFi Cloud Gateway Ultra",
        color="#C8E6C9",
        column=1,
    ),
    RackComponent(
        top_unit=12, unit_count=1,
        name="Rangierpanel",
        subtitle="",
        color=RESERVE_COLOR,
    ),
    RackComponent(
        top_unit=11, unit_count=1,
        name="Patchfeld 24 Port",
        subtitle="Keystone",
        color="#BBDEFB",
    ),
    RackComponent(
        top_unit=9, unit_count=2,
        name="UniFi UNVR Instant",
        subtitle="2HE",
        color="#F8BBD0",
    ),
    RackComponent(
        top_unit=7, unit_count=1,
        name="Tiny PC Lenovo M720q",
        color="#D1C4E9",
    ),
    RackComponent(
        top_unit=1, unit_count=1,
        name="Steckdosenleiste",
        color="#FFCC80",
    ),
]



# VLAN reference list displayed above every port table.
#
# The order of the entries determines the order in the PDF. The list
# can be empty, in which case no VLAN reference is displayed.
VLAN_REFERENCES: list[VlanReference] = [
    VlanReference(1, "Default"),
    VlanReference(10, "Home"),
    VlanReference(20, "IoT"),
    VlanReference(30, "Guest"),
    VlanReference(40, "Camera"),
]


# Port plans of the components in the network rack.
#
# Each port plan receives its own page in the generated PDF. The order
# of the entries determines the order of the PDF pages.
#
# Each port plan requires:
#   title: Heading of the port plan page.
#   ports: List of PortEntry objects for the component.
#
# Each PortEntry has the following fields:
#   port: Port number of the component.
#   destination: Connected room, device, or connection.
#   vlan: VLAN ID as text. Can be omitted for an unassigned VLAN.
#   poe: Manually maintained PoE information.
#   remark: Free text for additional information.
#
# Only "port" is required; omitted text fields are empty.
#
# Use "\n" inside "destination" or "remark" to create a manual line
# break in the PDF table.
PORT_PLANS: list[PortPlan] = [
    PortPlan(
        title="Patchpanel-Portplan",
        ports=[
            PortEntry(1, "Flur 1", remark="WAN"),
            PortEntry(
                2, "Büro", vlan="1", poe="Ja",
                remark="Access Point - U7 In-Wall",
            ),
            PortEntry(
                3, "Wohnzimmer", vlan="1", poe="Ja",
                remark="Access Point - U6+",
            ),
            PortEntry(
                4, "Flur 2", vlan="1", poe="Ja",
                remark="Access Point - U7-Pro-XG",
            ),
            PortEntry(5, "Schlafzimmer"),
            PortEntry(6),
            PortEntry(7),
            PortEntry(8),
            PortEntry(9),
            PortEntry(10),
            PortEntry(11),
            PortEntry(12),
            PortEntry(13),
            PortEntry(14),
            PortEntry(15),
            PortEntry(16),
            PortEntry(17),
            PortEntry(18),
            PortEntry(19),
            PortEntry(20),
            PortEntry(21),
            PortEntry(22),
            PortEntry(23),
            PortEntry(24),
        ],
    ),
    PortPlan(
        title="Switch-Portplan Lite-8-PoE",
        ports=[
            PortEntry(
                1,
                "Patchpanel Port 2\nBüro: Access Point - U7 In-Wall",
                vlan="1", poe="Ja",
            ),
            PortEntry(
                2,
                "Patchpanel Port 3\nWohnzimmer: Access Point - U6+",
                vlan="1", poe="Ja",
            ),
            PortEntry(
                3,
                "Patchpanel Port 4\nFlur: Access Point - U7-Pro-XG",
                vlan="1", poe="Ja",
            ),
            PortEntry(4, poe="Ja"),
            PortEntry(5, "Proxmox Host M720q", vlan="1", poe="Nein"),
            PortEntry(6, poe="Nein"),
            PortEntry(7, poe="Nein"),
            PortEntry(8, "UCG-Ultra LAN out", poe="Nein"),
        ],
    ),
    PortPlan(
        title="UCG-Ultra-Portplan",
        ports=[
            PortEntry(1, "Switch Lite-8-PoE", vlan="1", poe="Nein"),
            PortEntry(2),
            PortEntry(3),
            PortEntry(4),
            PortEntry(5, "WAN", poe="Nein", remark="Uplink"),
        ],
    ),
]