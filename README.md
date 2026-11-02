# Network Rack Documentation

Python script for creating network rack documentation as a PDF. The input data is stored in `data/rack_data.py`. The PDF generation is located in `network_rack_documentation.py`.

The PDF contains the network rack layout as well as separate pages for the patch panel, switch, and UCG-Ultra. Each component receives its own heading and port table. New components are added exclusively in the data file.

The PDF file name and console output are in English. The visible content of the generated PDF remains in German.

## Features

- Network rack layout as the first page of the PDF.
- Rack size is configured using `RACK_INFO["total_rack_units"]`.
- Unoccupied rack units are automatically displayed as reserve space.
- Separate port plans for the patch panel, switch, and UCG-Ultra in one PDF.
- Automatic creation of one PDF page per component from `RACK_COMPONENTS`.
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
2. Adjust `RACK_INFO`, `RACK_LAYOUT`, the VLAN reference list, and `RACK_COMPONENTS`.
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

## Configuring the network rack

The general information about the network rack is stored in `RACK_INFO` in `data/rack_data.py`:

```python
RACK_INFO = {
    "title": "Netzwerkschrank-Aufteilung",
    "total_rack_units": 16,
    "subtitle": (
        '19" Wandschrank, 16 HE, 450 mm Tiefe, Glastür – '
        "Digitus Digital Basic"
    ),
}
```

| Field | Meaning |
| --- | --- |
| `title` | Heading of the rack layout page |
| `total_rack_units` | Total number of rack units in the cabinet |
| `subtitle` | Description of the cabinet |

The rack size is defined by `total_rack_units`. It is not calculated from the highest occupied rack unit. This allows unoccupied rack units to be displayed correctly as reserve space.

## Configuring the rack layout

The `RACK_LAYOUT` list in `data/rack_data.py` defines the components installed in the cabinet:

```python
# Format: (top rack unit, number of rack units, name, subtitle, color)
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

| Field | Meaning | Example |
| --- | --- | --- |
| Top rack unit | Highest occupied rack unit of the component | `15` |
| Number of rack units | Number of occupied rack units | `2` |
| Name | Name of the component | `"UniFi UNVR Instant"` |
| Subtitle | Additional mounting or connection information | `"2U-Rackmount"` |
| Color | Background color in the rack layout | `"#F8BBD0"` |

A component with `top = 9` and `span = 2`, for example, occupies rack units 8 and 9. The order of entries in `RACK_LAYOUT` does not affect the layout; components are sorted by their position in the rack.

Unoccupied rack units are automatically added as reserve space and displayed using `RESERVE_COLOR`:

```python
RESERVE_COLOR = "#F5F5F5"
```

The script checks whether rack units are outside the cabinet or occupied more than once. If the layout is invalid, PDF creation is aborted with an error message.

## Configuring the VLAN reference list

The `VLAN_REFERENCES` list in `data/rack_data.py` defines the VLANs displayed above each port table in the PDF. Each entry consists of a VLAN ID and a freely selectable name:

```python
# VLAN reference list: (VLAN ID, name)
VLAN_REFERENCES = [
    (1, "Default"),
    (10, "Home"),
    (20, "IoT"),
    (30, "Guest"),
    (40, "Camera"),
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

## Configuring components

The `RACK_COMPONENTS` list in `data/rack_data.py` defines all components for which a separate PDF page is created. Each component requires a title and a port list:

```python
RACK_COMPONENTS = [
    {
        "title": "Patchpanel-Portplan",
        "ports": [
            (1, "Flur 1", "", "", "WAN"),
            (2, "Büro", "1", "Ja", "Access Point - U7 In-Wall"),
            (3, "Wohnzimmer", "1", "Ja", "Access Point - U6+"),
            (4, "Flur 2", "1", "Ja", "Access Point - U7-Pro-XG"),
            (5, "Schlafzimmer", "", "", ""),
        ],
    },
    {
        "title": "Switch-Portplan Lite-8-PoE",
        "ports": [
            (1, "Patchpanel Port 2\nBüro: Access Point - U7 In-Wall", "1", "Ja", ""),
            (2, "Patchpanel Port 3\nWohnzimmer: Access Point - U6+", "1", "Ja", ""),
            (3, "Patchpanel Port 4\nFlur: Access Point - U7-Pro-XG", "1", "Ja", ""),
            (5, "Proxmox Host M720q", "1", "Nein", ""),
            (8, "UCG-Ultra LAN out", "", "Nein", ""),
        ],
    },
    {
        "title": "UCG-Ultra-Portplan",
        "ports": [
            (1, "Switch Lite-8-PoE", "1", "Nein", ""),
            (5, "WAN", "", "Nein", "Uplink"),
        ],
    },
]
```

| Field | Meaning |
| --- | --- |
| `title` | Heading of the PDF page |
| `ports` | List of port entries for this component |

Each port entry contains five values:

```python
# (port, destination, VLAN, PoE, remark)
(1, "Flur 1", "", "", "WAN"),
```

| Field | Meaning | Example |
| --- | --- | --- |
| Port | Port number of the respective component | `1` |
| Destination | Room, connection, or connected device | `"Wohnzimmer"` |
| VLAN | VLAN ID of the connection | `"1"`, `"10"`, or `""` |
| PoE | Manually entered PoE information | `"Ja"`, `"Nein"`, or `""` |
| Remark | Free text for additional information | `"Uplink"` |

The VLAN value can be entered as text, for example `"10"`, or as a number, for example `10`. The field can remain empty for unassigned VLANs.

The order of entries in `RACK_COMPONENTS` determines the order of the PDF pages. The order of port entries determines the order in the respective table. Each port entry must contain exactly five values.

The supplied assignments are examples. The script uses the information unchanged; it does not detect or validate network connections, VLAN assignments, or PoE supply.

## Adding a new component

To add a second patch panel, for example, add another entry to `RACK_COMPONENTS` in `data/rack_data.py`:

```python
{
    "title": "Patchpanel 2 – Portplan",
    "ports": [
        (1, "Keller", "", "", ""),
        (2, "Terrasse", "", "", ""),
    ],
},
```

The main script does not need to be adjusted. The new component automatically receives its own page in the same PDF.

## Line breaks in cells

Use `\n` for a manual line break within a cell:

```python
(1, "Patchpanel Port 1\nFlur: Access Point - U7-Pro-XG", "1", "Ja", ""),
```

This becomes the following in the PDF:

```text
Patchpanel Port 1
Flur: Access Point - U7-Pro-XG
```

This works in all text fields of a port entry, i.e. in **destination** and **remark**.

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

The format is defined within `create_pdf()`:

```python
created_at_text = created_at.strftime(
    "Stand: %d.%m.%Y – %H:%M Uhr"
)
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

An existing file with the same name is overwritten. Even with an enabled timestamp, two calls within the same second can produce the same file name.

### Output folder

```python
OUTPUT_FOLDER = Path(__file__).resolve().parent / "output"
```

By default, the output folder is located next to the main script. To use a different folder, adjust this variable.

## Project structure

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