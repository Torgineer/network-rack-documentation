# Network Rack Documentation

Python script for creating network rack documentation as a PDF. The input data is stored in `data/rack_data.py`. The data structures (dataclasses) are defined in `data/models.py`. The PDF generation is located in `network_rack_documentation.py`.

The PDF contains the network rack layout as well as separate pages for the patch panel, switch, and UCG-Ultra. Each component receives its own heading and port table. New components are added exclusively in the data file.

The PDF file name and console output are in English. The visible content of the generated PDF remains in German.

## Features

- Network rack layout as the first page of the PDF.
- Rack size is configured using `RACK_INFO.total_rack_units`.
- Multiple components can share one rack unit row.
- A shared rack unit row is automatically divided equally between its components.
- Unoccupied rack units are automatically displayed as reserve space.
- Separate port plans for the patch panel, switch, and UCG-Ultra in one PDF.
- Automatic creation of one PDF page per port plan from `PORT_PLANS`.
- VLAN reference list above each port table.
- Table with the columns **Port**, **Ziel**, **VLAN**, **PoE**, and **Bemerkung**.
- A4 portrait format by default, with optional A4 landscape format.
- Current local date and time in the PDF.
- Optional timestamp in the file name.
- Column widths adapted to the page format.
- Automatic line breaks for longer entries.
- Repeated table header on subsequent pages.
- Page numbers in the footer.
- Alternating row colors for better readability.
- Typed dataclasses for rack information, rack components, VLANs, and port entries.
- All layout values (sizes, margins, colors, line widths) are named constants.

## Requirements

- Python 3
- Python package `reportlab`

## Installation

Open a terminal in the project folder and install the dependency:

```bash
python -m pip install reportlab
```

On Windows, you can alternatively use the Python launcher:

```powershell
py -m pip install reportlab
```

## Usage

1. Open `data/rack_data.py`.
2. Adjust `RACK_INFO`, `RACK_LAYOUT`, `VLAN_REFERENCES`, and `PORT_PLANS`.
3. Adjust the settings in `network_rack_documentation.py` if necessary.
4. Save the files and run the script from the project root directory:

```bash
python network_rack_documentation.py
```

On Windows, alternatively:

```powershell
py network_rack_documentation.py
```

The PDF is saved in the `output` folder next to the Python file. The folder is created automatically if necessary. After successful creation, the script prints the full path to the PDF in the terminal.

## Data model

The data classes are defined in `data/models.py` and are used in `data/rack_data.py`. All of them are immutable (`frozen=True`).

| Class | Purpose |
| --- | --- |
| `RackInfo` | General information about the cabinet |
| `RackComponent` | A component mounted in the rack (also used internally for reserve units) |
| `VlanReference` | One entry of the VLAN reference list |
| `PortEntry` | One row of a port plan table |
| `PortPlan` | A port plan page: title and list of `PortEntry` objects |

## Configuring the network rack

The general information about the network rack is stored in `RACK_INFO` in `data/rack_data.py`:

```python
RACK_INFO = RackInfo(
    title="Netzwerkschrank-Aufteilung",
    total_rack_units=16,
    subtitle=(
        '19" Wandschrank, 16 HE, 450 mm Tiefe, Glastür – '
        "Digitus Digital Basic"
    ),
)
```

| Field | Meaning |
| --- | --- |
| `title` | Heading of the rack layout page |
| `total_rack_units` | Total number of rack units in the cabinet |
| `subtitle` | Description of the cabinet |

The rack size is defined by `total_rack_units`. It is not calculated from the highest occupied rack unit. This allows unoccupied rack units to be displayed correctly as reserve space.

## Configuring the rack layout

The `RACK_LAYOUT` list in `data/rack_data.py` defines the components installed in the cabinet. Each entry is a `RackComponent`:

```python
RACK_LAYOUT = [
    RackComponent(
        top_unit=15, unit_count=1,
        name="FRITZ!Box 5690 Fiber",
        color="#FFE0B2",
    ),
    RackComponent(
        top_unit=13, unit_count=1,
        name="UniFi Cloud Gateway Ultra",
        color="#C8E6C9",
    ),
    RackComponent(
        top_unit=13, unit_count=1,
        name="UniFi Switch Lite 8 PoE",
        color="#C8E6C9",
    ),
    RackComponent(
        top_unit=12, unit_count=1,
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
```

| Field | Meaning | Example |
| --- | --- | --- |
| `top_unit` | Highest occupied rack unit of the component | `15` |
| `unit_count` | Number of occupied rack units | `2` |
| `name` | Name of the component | `"UniFi UNVR Instant"` |
| `color` | Background color in the rack layout | `"#F8BBD0"` |
| `subtitle` | Optional additional mounting or connection information (default: empty) | `"2HE"` |

A component with `top_unit=9` and `unit_count=2`, for example, occupies rack units 8 and 9. The order of entries in `RACK_LAYOUT` does not affect the layout; components are grouped and sorted by their position in the rack.

### Sharing a rack unit row

Multiple components can share the same rack unit row if they have exactly the same `top_unit` and the same `unit_count`.

For example, these two components share rack unit 13:

```python
RackComponent(
    top_unit=13, unit_count=1,
    name="UniFi Cloud Gateway Ultra",
    color="#C8E6C9",
),
RackComponent(
    top_unit=13, unit_count=1,
    name="UniFi Switch Lite 8 PoE",
    color="#C8E6C9",
),
```

The rack layout automatically divides this row into two equally sized fields:

```text
┌──────────────────────┬──────────────────────┐
│ UniFi Switch Lite    │ UniFi Cloud Gateway  │
│ 8 PoE                │ Ultra                │
└──────────────────────┴──────────────────────┘
```

Components within a shared row are ordered by the same sort key as the rest of the layout (top unit, unit count, name, subtitle, color, in descending order), so the order of entries in `RACK_LAYOUT` does not change which component appears on the left.

If three components use the same rack unit range, the row is divided into three equally sized fields. The vertical divider lines use the same gray color as the component frames.

Only components with an identical `(top_unit, unit_count)` combination can share a row. Overlapping but different ranges, such as `(13, 1)` and `(12, 1)` combined with a two-unit component spanning both, are rejected as conflicting occupancy.

Unoccupied rack units are automatically added as reserve space (labelled "Reserve") and displayed using `RESERVE_COLOR`:

```python
RESERVE_COLOR = "#F5F5F5"
```

The script checks whether rack units are outside the cabinet or occupied by conflicting component ranges. If the layout is invalid, PDF creation is aborted with an error message.

## Configuring the VLAN reference list

The `VLAN_REFERENCES` list in `data/rack_data.py` defines the VLANs displayed above each port table in the PDF. Each entry is a `VlanReference` consisting of a VLAN ID and a freely selectable name:

```python
VLAN_REFERENCES = [
    VlanReference(1, "Default"),
    VlanReference(10, "Home"),
    VlanReference(20, "IoT"),
    VlanReference(30, "Guest"),
    VlanReference(40, "Camera"),
]
```

The list appears in the PDF as follows:

```text
VLAN 1 – Default
VLAN 10 – Home
VLAN 20 – IoT
VLAN 30 – Guest
VLAN 40 – Camera
```

The order in `VLAN_REFERENCES` determines the order in the PDF. If the list is empty, no VLAN reference list is displayed.

## Configuring port plans

The `PORT_PLANS` list in `data/rack_data.py` defines all port plans for which a separate PDF page is created. Each entry is a `PortPlan` with a title and a list of `PortEntry` objects:

```python
PORT_PLANS = [
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
            PortEntry(5, "Proxmox Host M720q", vlan="1", poe="Nein"),
            PortEntry(8, "UCG-Ultra LAN out", poe="Nein"),
        ],
    ),
    PortPlan(
        title="UCG-Ultra-Portplan",
        ports=[
            PortEntry(1, "Switch Lite-8-PoE", vlan="1", poe="Nein"),
            PortEntry(5, "WAN", poe="Nein", remark="Uplink"),
        ],
    ),
]
```

| Field of `PortPlan` | Meaning |
| --- | --- |
| `title` | Heading of the PDF page |
| `ports` | List of `PortEntry` objects for this component |

Each `PortEntry` has the following fields:

| Field | Meaning | Example |
| --- | --- | --- |
| `port` | Port number of the respective component (required) | `1` |
| `destination` | Room, connection, or connected device | `"Wohnzimmer"` |
| `vlan` | VLAN ID of the connection as text | `"1"`, `"10"`, or `""` |
| `poe` | Manually entered PoE information | `"Ja"`, `"Nein"`, or `""` |
| `remark` | Free text for additional information | `"Uplink"` |

Only `port` is required. All other fields default to an empty string, so an unused port can be written as `PortEntry(6)`. The `vlan` field is text, for example `"10"`, and can remain empty for unassigned VLANs.

The order of entries in `PORT_PLANS` determines the order of the PDF pages. The order of port entries determines the order in the respective table.

The supplied assignments are examples. The script uses the information unchanged; it does not detect or validate network connections, VLAN assignments, or PoE supply.

## Adding a new component

To add a second patch panel, for example, add another entry to `PORT_PLANS` in `data/rack_data.py`:

```python
PortPlan(
    title="Patchpanel 2 – Portplan",
    ports=[
        PortEntry(1, "Keller"),
        PortEntry(2, "Terrasse"),
    ],
),
```

The main script does not need to be adjusted. The new component automatically receives its own page in the same PDF.

## Line breaks in cells

Use `\n` for a manual line break within a cell:

```python
PortEntry(
    1,
    "Patchpanel Port 1\nFlur: Access Point - U7-Pro-XG",
    vlan="1", poe="Ja",
)
```

This becomes the following in the PDF:

```text
Patchpanel Port 1
Flur: Access Point - U7-Pro-XG
```

This works in all text fields of a port entry, i.e. in `destination` and `remark`.

## Settings

The settings for the document title, page orientation, file name, and output folder are located at the top of `network_rack_documentation.py`.

### Document title

```python
DOCUMENT_TITLE = "Netzwerkschrank – Dokumentation"
```

### Page orientation

```python
PORTRAIT_ORIENTATION = True
```

- `True`: A4 portrait format.
- `False`: A4 landscape format.

During a regular script start, this value is passed to the function:

```python
if __name__ == "__main__":
    create_pdf(portrait_orientation=PORTRAIT_ORIENTATION)
```

For a direct function call, portrait format is the default:

```python
create_pdf()                                  # A4 portrait format
create_pdf(portrait_orientation=False)        # A4 landscape format
```

### Date and time

The timestamp is created anew on every function call. The visible date line uses the following format:

```text
Stand: 26.10.2026 – 17:25 Uhr
```

The format is defined by the constant `CREATED_AT_FORMAT`:

```python
CREATED_AT_FORMAT = "Stand: %d.%m.%Y – %H:%M Uhr"
```

### File name

```python
TIMESTAMP_IN_FILE_NAME = True
```

With `True`, the file name contains the date and time including seconds:

```text
network_rack_documentation_2026-10-26_17-25-00.pdf
```

With `False`, the same file name is always used:

```text
network_rack_documentation.pdf
```

The two file name patterns are defined by the constants `TIMESTAMPED_FILE_NAME_FORMAT` and `PLAIN_FILE_NAME`.

An existing file with the same name is overwritten. Even with an enabled timestamp, two calls within the same second can produce the same file name.

### Output folder

```python
OUTPUT_FOLDER = Path(__file__).resolve().parent / "output"
```

By default, the output folder is located next to the main script. To use a different folder, adjust this variable.

## Layout constants

Below the settings, `network_rack_documentation.py` contains named constants instead of hard-coded values. They are grouped by purpose:

| Group | Examples |
| --- | --- |
| File names and visible texts | `PLAIN_FILE_NAME`, `CREATED_AT_FORMAT`, `RESERVE_LABEL`, `RACK_UNIT_SUFFIX`, `PORT_TABLE_HEADERS`, `PAGE_NUMBER_PREFIX` |
| Fonts and colors | `FONT_REGULAR`, `FONT_BOLD`, `TEXT_MUTED_COLOR`, `RACK_FRAME_COLOR`, `TABLE_HEADER_BACKGROUND` |
| Page layout | `PAGE_MARGIN`, `RACK_PAGE_TITLE_BLOCK_HEIGHT`, `HEADER_SPACING`, `FOOTER_BASELINE_Y` |
| Paragraph styles | `TITLE_FONT_SIZE`, `TITLE_LEADING`, `BODY_FONT_SIZE`, `BODY_LEADING` |
| Port table | `PORT_TABLE_COLUMN_RATIOS`, `PORT_TABLE_PADDING_X`, `PORT_TABLE_PADDING_Y` |
| Rack drawing | `RACK_WIDTH_RATIO`, `COMPONENT_INSET_X`, `MOUNTING_HOLE_RADIUS`, `COMPONENT_LABEL_FONT_SIZE` |

Visible PDF texts stay in German, even though the constants and code are in English.

## Project structure

```text
network-rack-documentation/
├── data/
│   ├── .gitignore
│   ├── models.py
│   └── rack_data.py
├── .gitignore
├── network_rack_documentation.py
├── README.md
└── output/
    └── .gitignore
```

| File | Purpose |
| --- | --- |
| `data/models.py` | Dataclasses for rack information, components, VLANs, and port plans |
| `data/rack_data.py` | User-editable input data |
| `network_rack_documentation.py` | Validation, layout drawing, and PDF generation |