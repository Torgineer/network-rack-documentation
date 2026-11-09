# -*- coding: utf-8 -*-
"""Data models for the network rack documentation.

This module defines the dataclasses used by ``rack_data.py`` to describe
the cabinet, its components, the VLAN reference list and the port plans.
They contain no PDF logic and are consumed by
``network_rack_documentation.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class RackInfo:
    """General information about the network rack.

    Attributes:
        title: Heading of the rack layout page.
        total_rack_units: Physical size of the cabinet in rack units.
            It is not derived from the highest occupied rack unit, so
            unoccupied units can be shown as reserve space.
        subtitle: Description of the cabinet, shown below the title.
    """

    title: str
    total_rack_units: int
    subtitle: str


@dataclass(frozen=True)
class RackComponent:
    """A component mounted in the rack, or a reserve rack unit.

    Rack units are numbered from the bottom (1) to the top. Components
    with an identical ``top_unit`` and ``unit_count`` share one rack
    unit row and are drawn side by side.

    Attributes:
        top_unit: Highest rack unit occupied by the component.
        unit_count: Height of the component in rack units.
        name: Name shown in bold in the rack layout.
        color: Background color as a hex string, for example "#FFE0B2".
        subtitle: Optional text shown below the name.
    """

    top_unit: int
    unit_count: int
    name: str
    color: str
    subtitle: str | None = None
    column: int = 0

    @property
    def bottom_unit(self) -> int:
        """Return the lowest rack unit occupied by the component."""
        return self.top_unit - self.unit_count + 1

    @property
    def occupied_units(self) -> range:
        """Return all rack units occupied by the component."""
        return range(self.bottom_unit, self.top_unit + 1)

    @property
    def row_key(self) -> Tuple[int, int]:
        """Return the key that identifies a shared rack unit row."""
        return self.top_unit, self.unit_count

    @property
    def sort_key(self) -> tuple[int, int, int, str, str, str]:
        """Return the key used to order components in the rack layout.

        The order of the values matches the tuple format:
        top rack unit, number of rack units, column, name, subtitle, color.
        """
        return (
            self.top_unit,
            self.unit_count,
            self.column,
            self.name,
            self.subtitle,
            self.color,
        )


@dataclass(frozen=True)
class VlanReference:
    """An entry of the VLAN reference list.

    Attributes:
        vlan_id: Numeric VLAN ID.
        name: Display name of the VLAN.
    """

    vlan_id: int
    name: str


@dataclass(frozen=True)
class PortEntry:
    """One row of a port plan table.

    Attributes:
        port: Port number of the component.
        destination: Connected room, device or connection. Use "\\n"
            for a manual line break in the PDF table.
        vlan: VLAN ID as text. Empty for an unassigned VLAN.
        poe: Manually maintained PoE information.
        remark: Free text with additional information. Use "\\n" for a
            manual line break in the PDF table.
    """

    port: int
    destination: str = ""
    vlan: str = ""
    poe: str = ""
    remark: str = ""


@dataclass(frozen=True)
class PortPlan:
    """The port plan of one component, shown on its own PDF page.

    Attributes:
        title: Heading of the port plan page.
        ports: Port entries in the order they appear in the table.
    """

    title: str
    ports: list[PortEntry] = field(default_factory=list)