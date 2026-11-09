# %%
# -*- coding: utf-8 -*-
"""Network rack documentation as PDF.

Creates a PDF containing the rack layout and port plans.

Installation: python -m pip install reportlab
Start: python network_rack_documentation.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence, Union
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Flowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
    TableStyle,
)

from data.models import PortPlan, RackComponent, RackInfo
from data.rack_data import (
    PORT_PLANS,
    RACK_INFO,
    RACK_LAYOUT,
    RESERVE_COLOR,
    VLAN_REFERENCES,
)


# =============================================================
# SETTINGS – adjust manually here
# =============================================================

# Title shown in the PDF document properties.
DOCUMENT_TITLE = "Netzwerkschrank – Dokumentation"

# True: A4 portrait / False: A4 landscape
PORTRAIT_ORIENTATION = True

# True: save every PDF with a timestamp in its file name.
# False: overwrite network_rack_documentation.pdf on every run.
TIMESTAMP_IN_FILE_NAME = True

# Output folder next to this Python file.
OUTPUT_FOLDER = Path(__file__).resolve().parent / "output"


# =============================================================
# CONSTANTS – file names and visible (German) texts
# =============================================================

# File name used when TIMESTAMP_IN_FILE_NAME is False.
PLAIN_FILE_NAME = "network_rack_documentation.pdf"

# strftime pattern used when TIMESTAMP_IN_FILE_NAME is True.
TIMESTAMPED_FILE_NAME_FORMAT = (
    "network_rack_documentation_%Y-%m-%d_%H-%M-%S.pdf"
)

# strftime pattern of the "last updated" line on every page.
CREATED_AT_FORMAT = "Stand: %d.%m.%Y – %H:%M Uhr"

# Label of automatically added unoccupied rack units.
RESERVE_LABEL = "Reserve"

# Suffix of the rack unit numbers ("HE" = Höheneinheit).
RACK_UNIT_SUFFIX = "HE"

# Column headings of the port plan tables.
PORT_TABLE_HEADERS = ("Port", "Ziel", "VLAN", "PoE", "Bemerkung")

# Page number text; the page number is appended.
PAGE_NUMBER_PREFIX = "Seite"


# =============================================================
# CONSTANTS – fonts and colors
# =============================================================

FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

TEXT_MUTED_COLOR = colors.HexColor("#666666")
RACK_FRAME_COLOR = colors.HexColor("#555555")

TABLE_HEADER_BACKGROUND = colors.HexColor("#1f4e79")
TABLE_GRID_COLOR = colors.HexColor("#b3bac3")
TABLE_ROW_COLORS = [colors.white, colors.HexColor("#f2f6fa")]


# =============================================================
# CONSTANTS – page layout
# =============================================================

PAGE_MARGIN = 15 * mm

# Vertical space reserved on the rack page for title, subtitle and
# timestamp, plus the gap below them.
RACK_PAGE_TITLE_BLOCK_HEIGHT = 28 * mm
RACK_PAGE_CONTENT_SPACING = 8 * mm

# Gap between the page header and the page content.
HEADER_SPACING = 5 * mm

# Gap between the VLAN reference list and the port table.
VLAN_REFERENCE_SPACING = 6 * mm

FOOTER_FONT_SIZE = 8
FOOTER_BASELINE_Y = 9 * mm


# =============================================================
# CONSTANTS – paragraph styles
# =============================================================

TITLE_FONT_SIZE = 16
TITLE_LEADING = 20
TITLE_SPACE_AFTER = 6 * mm

BODY_FONT_SIZE = 9
BODY_LEADING = 12


# =============================================================
# CONSTANTS – port table
# =============================================================

# Column widths as a fraction of the document width:
# Port, Ziel, VLAN, PoE, Bemerkung.
PORT_TABLE_COLUMN_RATIOS = (0.09, 0.30, 0.09, 0.09, 0.43)

PORT_TABLE_GRID_LINE_WIDTH = 0.5
PORT_TABLE_PADDING_X = 6
PORT_TABLE_PADDING_Y = 5


# =============================================================
# CONSTANTS – rack drawing
# =============================================================

# Share of the available width taken by the rack. The remaining width
# is intentionally unused to keep the layout readable.
RACK_WIDTH_RATIO = 0.52

# Small inset that keeps component boxes from overlapping the rack
# frame and the rack unit boundaries.
COMPONENT_INSET_X = 1.2 * mm
COMPONENT_INSET_Y = 0.6 * mm

RACK_FRAME_LINE_WIDTH = 1.2
RACK_UNIT_BOUNDARY_LINE_WIDTH = 0.3
COMPONENT_LINE_WIDTH = 1
COMPONENT_DIVIDER_LINE_WIDTH = 1

MOUNTING_HOLE_LINE_WIDTH = 0.5
MOUNTING_HOLE_INSET_X = 3 * mm
MOUNTING_HOLE_RADIUS = 1.1 * mm

DEFAULT_TEXT_SIZE = 9
COMPONENT_LABEL_FONT_SIZE = 7
COMPONENT_SUBTITLE_FONT_SIZE = 6
COMPONENT_TEXT_PADDING_X = 3 * mm

# Vertical text offsets relative to the vertical center of a component.
LABEL_OFFSET_WITH_SUBTITLE = 1.0 * mm
LABEL_OFFSET_WITHOUT_SUBTITLE = -0.8 * mm
SUBTITLE_OFFSET_BELOW_CENTER = 2.5 * mm

RACK_UNIT_NUMBER_FONT_SIZE = 7
RACK_UNIT_NUMBER_RIGHT_PADDING = 4 * mm
RACK_UNIT_NUMBER_TOP_OFFSET = 3.8 * mm


def validate_layout(
    layout: Sequence[RackComponent],
    total_rack_units: int,
) -> Sequence[RackComponent]:
    """Validate rack unit ranges and conflicting occupancy.

    Components may share a rack unit row only if they have exactly the
    same top rack unit and the same number of rack units. This allows,
    for example, two devices to be mounted side by side in one rack
    unit. Overlapping but different ranges are rejected.

    Components sharing a rack unit row must use distinct column values.
    A column value of 0 refers to the leftmost position, 1 to the
    position to its right, and so on.

    Args:
        layout: Rack components to validate.
        total_rack_units: Total number of rack units in the cabinet.

    Returns:
        The validated rack layout.

    Raises:
        ValueError: If a rack unit range is invalid, conflicts with
            another, non-identical component range, or uses a duplicate
            column within the same rack unit row.
    """
    if total_rack_units < 1:
        raise ValueError(
            "RACK_INFO['total_rack_units'] must be at least 1."
        )

    available_rack_units = set(range(1, total_rack_units + 1))
    known_ranges = set()
    used_columns: dict[tuple[int, int], set[int]] = {}

    for component in layout:
        top = component.top_unit
        span = component.unit_count
        label = component.name

        if type(top) is not int or type(span) is not int:
            raise ValueError(
                f"{label}: rack unit and number of rack units "
                "must be integers."
            )

        if span < 1 or top > total_rack_units or top - span < 0:
            raise ValueError(f"{label}: invalid rack unit range.")

        if type(component.column) is not int or component.column < 0:
            raise ValueError(
                f"{label}: column must be a non-negative integer."
            )

        occupied_rack_units = set(component.occupied_units)
        rack_unit_range = component.row_key

        # Identical ranges are allowed because multiple components can
        # be mounted side by side in the same rack unit row. However,
        # each component needs a unique horizontal position.
        columns = used_columns.setdefault(rack_unit_range, set())

        if component.column in columns:
            raise ValueError(
                f"{label}: column {component.column} is already used "
                f"in rack unit row {rack_unit_range}."
            )

        columns.add(component.column)

        if rack_unit_range not in known_ranges:
            if not occupied_rack_units <= available_rack_units:
                raise ValueError(
                    f"{label}: rack unit is occupied twice."
                )

            available_rack_units -= occupied_rack_units
            known_ranges.add(rack_unit_range)

    return layout


def add_reserve_units(
    layout: Sequence[RackComponent],
    total_rack_units: int,
) -> list[RackComponent]:
    """Add all unoccupied rack units as reserve space.

    Args:
        layout: Validated rack components.
        total_rack_units: Total number of rack units in the cabinet.

    Returns:
        Rack components and reserve units, sorted from the top of the
        cabinet to the bottom.
    """
    occupied_rack_units: set[int] = set()

    for component in layout:
        occupied_rack_units.update(component.occupied_units)

    available_rack_units = (
        set(range(1, total_rack_units + 1))
        - occupied_rack_units
    )

    reserve_units = [
        RackComponent(
            top_unit=rack_unit,
            unit_count=1,
            name=RESERVE_LABEL,
            color=RESERVE_COLOR,
        )
        for rack_unit in available_rack_units
    ]

    return sorted(
        list(layout) + reserve_units,
        key=lambda component: component.sort_key,
        reverse=True,
    )


def group_components(
    layout: Sequence[RackComponent],
) -> list[list[RackComponent]]:
    """Group components that occupy the same rack unit range.

    Components with an identical top and span range share one rack unit
    row. The drawing code divides such a row equally between all
    components in the group.

    Args:
        layout: Rack components and reserve units.

    Returns:
        A list of component groups, sorted from the top of the cabinet
        to the bottom. Components within one group are ordered from left
        to right by their column value.
    """
    groups: dict[tuple[int, int], list[RackComponent]] = {}

    for component in layout:
        groups.setdefault(component.row_key, []).append(component)

    return sorted(
        (
            sorted(group, key=lambda component: component.column)
            for group in groups.values()
        ),
        key=lambda group: group[0].top_unit,
        reverse=True,
    )


class RackLayout(Flowable):
    """Draw the network rack layout as a flowable for the PDF."""

    def __init__(
        self,
        layout: Sequence[RackComponent],
        total_rack_units: int,
        width: float,
        height: float,
    ) -> None:
        """Initialize the rack layout drawing.

        Args:
            layout: Rack components and automatically added reserve
                units.
            total_rack_units: Total number of rack units in the cabinet.
            width: Available width for the rack drawing.
            height: Available height for the rack drawing.
        """
        super().__init__()
        self.layout = layout
        self.total_rack_units = total_rack_units
        self.width = width
        self.height = height

        self.rack_x = 0
        self.rack_bottom = 0
        self.rack_top = height
        self.rack_unit_height = height / total_rack_units

        # Draw the rack on the left side of the page.
        self.rack_width = width * RACK_WIDTH_RATIO

        self.inset_x = COMPONENT_INSET_X
        self.inset_y = COMPONENT_INSET_Y

        # Color used for component frames and dividers between
        # components sharing one rack unit row.
        self.frame_color = RACK_FRAME_COLOR

    def wrap(
        self,
        available_width: float,
        available_height: float,
    ) -> tuple[float, float]:
        """Return the fixed width and height of the rack layout.

        Args:
            available_width: Width available from the PDF layout engine.
            available_height: Height available from the PDF layout
                engine.

        Returns:
            Tuple containing the fixed width and height.
        """
        return self.width, self.height

    def rack_unit_y(self, rack_unit: int) -> float:
        """Return the PDF y-coordinate of the bottom edge of a rack unit.

        Rack units are numbered from the bottom (1) to the top, which
        matches the PDF coordinate system, where y increases upwards.

        Args:
            rack_unit: Rack unit number, starting at 1 at the bottom.

        Returns:
            Y-coordinate of the lower boundary of the rack unit.
        """
        return self.rack_bottom + (
            (rack_unit - 1) * self.rack_unit_height
        )

    def draw_text(
        self,
        canvas: Canvas,
        x: float,
        y: float,
        text: str,
        size: float = DEFAULT_TEXT_SIZE,
        bold: bool = False,
        max_width: Optional[float] = None,
    ) -> None:
        """Draw text and reduce its font size if it exceeds max_width.

        Args:
            canvas: ReportLab canvas to draw on.
            x: X-coordinate of the text.
            y: Y-coordinate of the text.
            text: Text to draw.
            size: Initial font size in points.
            bold: Whether to use a bold font.
            max_width: Maximum available text width in points.
        """
        font = FONT_BOLD if bold else FONT_REGULAR

        if max_width is not None:
            text_width = canvas.stringWidth(text, font, size)

            # Scale the font size down instead of allowing long labels
            # to overlap neighboring components.
            if text_width > max_width:
                size *= max_width / text_width

        canvas.setFillColor(colors.black)
        canvas.setFont(font, size)
        canvas.drawString(x, y, text)

    def draw_rack(self, canvas: Canvas) -> None:
        """Draw the rack frame, rack unit boundaries and mounting holes.

        Args:
            canvas: ReportLab canvas to draw on.
        """
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(RACK_FRAME_LINE_WIDTH)
        canvas.rect(
            self.rack_x,
            self.rack_bottom,
            self.rack_width,
            self.rack_top - self.rack_bottom,
        )

        for boundary in range(self.total_rack_units + 1):
            y = self.rack_unit_y(boundary + 1)

            # Draw internal rack unit boundaries, but not the outer
            # frame boundaries.
            if 0 < boundary < self.total_rack_units:
                canvas.setLineWidth(RACK_UNIT_BOUNDARY_LINE_WIDTH)
                canvas.line(
                    self.rack_x, y,
                    self.rack_x + self.rack_width, y,
                )

            # Draw mounting holes at every rack unit boundary.
            canvas.setLineWidth(MOUNTING_HOLE_LINE_WIDTH)
            for x in (
                self.rack_x + MOUNTING_HOLE_INSET_X,
                self.rack_x + self.rack_width - MOUNTING_HOLE_INSET_X,
            ):
                canvas.circle(x, y, MOUNTING_HOLE_RADIUS)

    def draw_component(
        self,
        canvas: Canvas,
        component: RackComponent,
        x: float,
        width: float,
    ) -> None:
        """Draw one component inside the specified horizontal area.

        Args:
            canvas: ReportLab canvas to draw on.
            component: Component or reserve unit to draw.
            x: Left x-coordinate of the component box.
            width: Width of the component box.
        """
        top = component.top_unit
        span = component.unit_count
        label = component.name
        subtitle = component.subtitle
        color = component.color

        y = self.rack_unit_y(top - span + 1)
        height = span * self.rack_unit_height

        canvas.setFillColor(colors.HexColor(color))
        canvas.setStrokeColor(self.frame_color)
        canvas.setLineWidth(COMPONENT_LINE_WIDTH)
        canvas.rect(
            x,
            y + self.inset_y,
            width,
            height - 2 * self.inset_y,
            stroke=1,
            fill=1,
        )

        text_x = x + COMPONENT_TEXT_PADDING_X
        text_width = width - 2 * COMPONENT_TEXT_PADDING_X
        center_y = y + height / 2

        label_offset = (
            LABEL_OFFSET_WITH_SUBTITLE
            if subtitle
            else LABEL_OFFSET_WITHOUT_SUBTITLE
        )

        self.draw_text(
            canvas,
            text_x,
            center_y + label_offset,
            label,
            size=COMPONENT_LABEL_FONT_SIZE,
            bold=True,
            max_width=text_width,
        )

        if subtitle:
            self.draw_text(
                canvas,
                text_x,
                center_y - SUBTITLE_OFFSET_BELOW_CENTER,
                subtitle,
                size=COMPONENT_SUBTITLE_FONT_SIZE,
                max_width=text_width,
            )

    def draw_rack_unit_numbers(self, canvas: Canvas) -> None:
        """Draw the rack unit numbers on the right side of the rack.

        Args:
            canvas: ReportLab canvas to draw on.
        """
        canvas.setFillColor(colors.black)
        canvas.setFont(FONT_BOLD, RACK_UNIT_NUMBER_FONT_SIZE)

        for rack_unit in range(1, self.total_rack_units + 1):
            canvas.drawRightString(
                self.rack_x
                + self.rack_width
                - RACK_UNIT_NUMBER_RIGHT_PADDING,
                self.rack_unit_y(rack_unit)
                + self.rack_unit_height
                - RACK_UNIT_NUMBER_TOP_OFFSET,
                f"{rack_unit} {RACK_UNIT_SUFFIX}",
            )

    def draw(self) -> None:
        """Draw the complete rack layout, including shared rack unit rows."""
        canvas = self.canv
        self.draw_rack(canvas)

        box_x = self.rack_x + self.inset_x
        total_box_width = self.rack_width - 2 * self.inset_x

        for group in group_components(self.layout):
            component_count = len(group)

            # Divide a shared rack unit row equally between its
            # components.
            group_width = total_box_width / component_count

            for index, component in enumerate(group):
                x = box_x + index * group_width
                self.draw_component(
                    canvas,
                    component,
                    x,
                    group_width,
                )

            if component_count > 1:
                canvas.setStrokeColor(self.frame_color)
                canvas.setLineWidth(COMPONENT_DIVIDER_LINE_WIDTH)

                top = group[0].top_unit
                span = group[0].unit_count
                y = self.rack_unit_y(top - span + 1) + self.inset_y
                height = (
                    span * self.rack_unit_height
                    - 2 * self.inset_y
                )

                # Draw vertical dividers between components sharing the
                # same rack unit row.
                for index in range(1, component_count):
                    divider_x = box_x + index * group_width

                    canvas.line(
                        divider_x,
                        y,
                        divider_x,
                        y + height,
                    )

        self.draw_rack_unit_numbers(canvas)


@dataclass(frozen=True)
class PdfStyles:
    """Paragraph styles used throughout the PDF.

    Attributes:
        title: Page heading style.
        subtitle: Muted style for subtitles and timestamps.
        vlan_reference: Style of the VLAN reference list.
        cell: Left-aligned table cell style.
        centered: Centered table cell style.
        header: Table header style (bold, white text).
    """

    title: ParagraphStyle
    subtitle: ParagraphStyle
    vlan_reference: ParagraphStyle
    cell: ParagraphStyle
    centered: ParagraphStyle
    header: ParagraphStyle


def build_styles() -> PdfStyles:
    """Create the paragraph styles used in the PDF.

    Returns:
        The collection of paragraph styles.
    """
    base_styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PortPlanTitle",
        parent=base_styles["Title"],
        fontName=FONT_BOLD,
        fontSize=TITLE_FONT_SIZE,
        leading=TITLE_LEADING,
        spaceAfter=TITLE_SPACE_AFTER,
    )
    subtitle_style = ParagraphStyle(
        "PortPlanSubtitle",
        parent=base_styles["Normal"],
        fontSize=BODY_FONT_SIZE,
        leading=BODY_LEADING,
        textColor=TEXT_MUTED_COLOR,
    )
    vlan_reference_style = ParagraphStyle(
        "VlanReference",
        parent=base_styles["Normal"],
        fontSize=BODY_FONT_SIZE,
        leading=BODY_LEADING,
    )
    cell_style = ParagraphStyle(
        "PortPlanCell",
        parent=base_styles["Normal"],
        fontSize=BODY_FONT_SIZE,
        leading=BODY_LEADING,
    )
    centered_style = ParagraphStyle(
        "PortPlanCentered",
        parent=cell_style,
        alignment=TA_CENTER,
    )
    header_style = ParagraphStyle(
        "PortPlanHeader",
        parent=cell_style,
        fontName=FONT_BOLD,
        textColor=colors.white,
    )

    return PdfStyles(
        title=title_style,
        subtitle=subtitle_style,
        vlan_reference=vlan_reference_style,
        cell=cell_style,
        centered=centered_style,
        header=header_style,
    )


def make_paragraph(
    value: Union[str, int, None],
    style: ParagraphStyle,
) -> Paragraph:
    """Convert a value into an escaped ReportLab paragraph.

    Args:
        value: Text, number, or None.
        style: ReportLab paragraph style.

    Returns:
        ReportLab paragraph with escaped text and support for manual
        line breaks.
    """
    text = "" if value is None else str(value)
    return Paragraph(
        escape(text).replace("\n", "<br/>"),
        style,
    )


def build_vlan_reference_elements(styles: PdfStyles) -> list[Flowable]:
    """Create the VLAN reference list shown above each port table.

    Args:
        styles: Paragraph styles of the PDF.

    Returns:
        List of PDF elements, or an empty list if no VLANs are
        configured.
    """
    if not VLAN_REFERENCES:
        return []

    vlan_text = "<br/>".join(
        f"<b>VLAN {reference.vlan_id}</b> – {escape(reference.name)}"
        for reference in VLAN_REFERENCES
    )

    return [
        Paragraph(vlan_text, styles.vlan_reference),
        Spacer(1, VLAN_REFERENCE_SPACING),
    ]


def build_rack_page(
    doc: SimpleDocTemplate,
    rack_info: RackInfo,
    layout: Sequence[RackComponent],
    styles: PdfStyles,
    created_at_text: str,
) -> list[Flowable]:
    """Create the PDF elements for the network rack layout page.

    Args:
        doc: Document that provides the available page area.
        rack_info: General information about the rack.
        layout: Rack components including reserve units.
        styles: Paragraph styles of the PDF.
        created_at_text: Timestamp line shown below the subtitle.

    Returns:
        List of PDF elements for the first page.
    """
    available_width = doc.width
    available_height = (
        doc.height
        - RACK_PAGE_TITLE_BLOCK_HEIGHT
        - RACK_PAGE_CONTENT_SPACING
    )

    return [
        make_paragraph(rack_info.title, styles.title),
        make_paragraph(rack_info.subtitle, styles.subtitle),
        make_paragraph(created_at_text, styles.subtitle),
        Spacer(1, HEADER_SPACING),
        RackLayout(
            layout=layout,
            total_rack_units=rack_info.total_rack_units,
            width=available_width,
            height=available_height,
        ),
    ]


def build_port_plan_page(
    doc: SimpleDocTemplate,
    plan: PortPlan,
    styles: PdfStyles,
    created_at_text: str,
) -> list[Flowable]:
    """Create the PDF elements for one component port plan page.

    Args:
        doc: Document that provides the available page width.
        plan: Port plan containing a title and its port entries.
        styles: Paragraph styles of the PDF.
        created_at_text: Timestamp line shown below the title.

    Returns:
        List of PDF elements for the port plan page.
    """
    elements: list[Flowable] = [
        make_paragraph(plan.title, styles.title),
        make_paragraph(created_at_text, styles.subtitle),
        Spacer(1, HEADER_SPACING),
    ]

    elements.extend(build_vlan_reference_elements(styles))

    data = [[
        make_paragraph(name, styles.header)
        for name in PORT_TABLE_HEADERS
    ]]

    for entry in plan.ports:
        data.append([
            make_paragraph(entry.port, styles.centered),
            make_paragraph(entry.destination, styles.cell),
            make_paragraph(entry.vlan, styles.centered),
            make_paragraph(entry.poe, styles.centered),
            make_paragraph(entry.remark, styles.cell),
        ])

    table = Table(
        data,
        colWidths=[
            doc.width * proportion
            for proportion in PORT_TABLE_COLUMN_RATIOS
        ],
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BACKGROUND),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), PORT_TABLE_GRID_LINE_WIDTH,
         TABLE_GRID_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), TABLE_ROW_COLORS),
        ("LEFTPADDING", (0, 0), (-1, -1), PORT_TABLE_PADDING_X),
        ("RIGHTPADDING", (0, 0), (-1, -1), PORT_TABLE_PADDING_X),
        ("TOPPADDING", (0, 0), (-1, -1), PORT_TABLE_PADDING_Y),
        ("BOTTOMPADDING", (0, 0), (-1, -1), PORT_TABLE_PADDING_Y),
    ]))

    elements.append(table)
    return elements


def draw_footer(canvas: Canvas, document: SimpleDocTemplate) -> None:
    """Draw the page number in the bottom-right corner.

    Args:
        canvas: ReportLab canvas to draw on.
        document: ReportLab document being rendered.
    """
    canvas.saveState()
    canvas.setFont(FONT_REGULAR, FOOTER_FONT_SIZE)
    canvas.setFillColor(TEXT_MUTED_COLOR)
    canvas.drawRightString(
        document.pagesize[0] - document.rightMargin,
        FOOTER_BASELINE_Y,
        f"{PAGE_NUMBER_PREFIX} {document.page}",
    )
    canvas.restoreState()


def create_pdf(portrait_orientation: bool = True) -> Path:
    """Create the rack layout and port plans in a single PDF.

    Args:
        portrait_orientation: Whether to create the PDF in A4 portrait
            format. If False, A4 landscape format is used.

    Returns:
        Path to the generated PDF file.
    """
    created_at = datetime.now().astimezone()
    created_at_text = created_at.strftime(CREATED_AT_FORMAT)

    total_rack_units = RACK_INFO.total_rack_units
    validated_layout = validate_layout(RACK_LAYOUT, total_rack_units)
    layout = add_reserve_units(validated_layout, total_rack_units)

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    if TIMESTAMP_IN_FILE_NAME:
        file_name = created_at.strftime(TIMESTAMPED_FILE_NAME_FORMAT)
    else:
        file_name = PLAIN_FILE_NAME

    pdf_file = OUTPUT_FOLDER / file_name

    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=(
            portrait(A4)
            if portrait_orientation
            else landscape(A4)
        ),
        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,
        topMargin=PAGE_MARGIN,
        bottomMargin=PAGE_MARGIN,
        title=DOCUMENT_TITLE,
    )

    styles = build_styles()

    elements = build_rack_page(
        doc, RACK_INFO, layout, styles, created_at_text,
    )

    # Create one separate PDF page for every configured port plan.
    for plan in PORT_PLANS:
        elements.append(PageBreak())
        elements.extend(
            build_port_plan_page(doc, plan, styles, created_at_text)
        )

    doc.build(elements, onFirstPage=draw_footer, onLaterPages=draw_footer)

    print(f"PDF created: {pdf_file}")
    return pdf_file


if __name__ == "__main__":
    create_pdf(portrait_orientation=PORTRAIT_ORIENTATION)