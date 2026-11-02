# %%
# -*- coding: utf-8 -*-
"""Network rack documentation as PDF.

Creates a PDF containing the rack layout and port plans.

Installation: python -m pip install reportlab
Start: python network_rack_documentation.py
"""


from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
    TableStyle,
)

from data.rack_data import (
    RACK_COMPONENTS,
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


def validate_layout(layout, total_rack_units):
    """Validate rack unit ranges and conflicting occupancy.

    Components may share a rack unit row only if they have exactly the
    same top rack unit and the same number of rack units. This allows,
    for example, two devices to be mounted side by side in one rack
    unit. Overlapping but different ranges are rejected.

    Args:
        layout: Rack components in the format
            (top rack unit, number of rack units, name, subtitle, color).
        total_rack_units: Total number of rack units in the cabinet.

    Returns:
        The validated rack layout.

    Raises:
        ValueError: If a rack unit range is invalid or conflicts with
            another, non-identical component range.
    """
    if total_rack_units < 1:
        raise ValueError(
            "RACK_INFO['total_rack_units'] must be at least 1."
        )

    available_rack_units = set(range(1, total_rack_units + 1))
    known_ranges = set()

    for top, span, label, *_ in layout:
        if type(top) is not int or type(span) is not int:
            raise ValueError(
                f"{label}: rack unit and number of rack units "
                "must be integers."
            )

        if span < 1 or top > total_rack_units or top - span < 0:
            raise ValueError(f"{label}: invalid rack unit range.")

        occupied_rack_units = set(range(top - span + 1, top + 1))
        rack_unit_range = (top, span)

        # Identical ranges are allowed because multiple components can
        # be mounted side by side in the same rack unit row.
        if rack_unit_range not in known_ranges:
            if not occupied_rack_units <= available_rack_units:
                raise ValueError(
                    f"{label}: rack unit is occupied twice."
                )

            available_rack_units -= occupied_rack_units
            known_ranges.add(rack_unit_range)

    return layout


def add_reserve_units(layout, total_rack_units):
    """Add all unoccupied rack units as reserve space.

    Args:
        layout: Validated rack components.
        total_rack_units: Total number of rack units in the cabinet.

    Returns:
        Rack components and reserve units, sorted from the top of the
        cabinet to the bottom.
    """
    occupied_rack_units = set()

    for top, span, *_ in layout:
        occupied_rack_units.update(range(top - span + 1, top + 1))

    available_rack_units = (
        set(range(1, total_rack_units + 1))
        - occupied_rack_units
    )

    reserve_units = [
        (rack_unit, 1, "Reserve", "", RESERVE_COLOR)
        for rack_unit in available_rack_units
    ]

    return sorted(layout + reserve_units, reverse=True)


def group_components(layout):
    """Group components that occupy the same rack unit range.

    Components with an identical (top, span) range share one rack unit
    row. The drawing code divides such a row equally between all
    components in the group.

    Args:
        layout: Rack components and reserve units.

    Returns:
        A list of component groups, sorted from the top of the cabinet
        to the bottom.
    """
    groups = {}

    for component in layout:
        top, span = component[0], component[1]
        groups.setdefault((top, span), []).append(component)

    return sorted(
        groups.values(),
        key=lambda group: group[0][0],
        reverse=True,
    )


class RackLayout(Flowable):
    """Draw the network rack layout as a flowable for the PDF."""

    def __init__(self, layout, total_rack_units, width, height):
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

        # Draw the rack on the left side of the page. The remaining
        # width is intentionally unused to keep the layout readable.
        self.rack_width = width * 0.52

        # Small inset prevents component boxes from overlapping the
        # rack frame and rack unit boundaries.
        self.inset_x = 1.2 * mm
        self.inset_y = 0.6 * mm

        # Color used for component frames and dividers between
        # components sharing one rack unit row.
        self.frame_color = colors.HexColor("#555555")

    def wrap(self, available_width, available_height):
        """Return the fixed width and height of the rack layout.

        Args:
            available_width: Width available from the PDF layout engine.
            available_height: Height available from the PDF layout
                engine.

        Returns:
            Tuple containing the fixed width and height.
        """
        return self.width, self.height

    def rack_unit_y(self, rack_unit):
        """Return the PDF y-coordinate of the bottom edge of a rack unit.

        Rack units are numbered from top to bottom, while PDF
        coordinates increase from bottom to top.

        Args:
            rack_unit: Rack unit number, starting at 1 at the bottom.

        Returns:
            Y-coordinate of the lower boundary of the rack unit.
        """
        return self.rack_bottom + (
            (rack_unit - 1) * self.rack_unit_height
        )

    def draw_text(self, canvas, x, y, text, size=9, bold=False,
                  max_width=None):
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
        font = "Helvetica-Bold" if bold else "Helvetica"

        if max_width is not None:
            text_width = canvas.stringWidth(text, font, size)

            # Scale the font size down instead of allowing long labels
            # to overlap neighboring components.
            if text_width > max_width:
                size *= max_width / text_width

        canvas.setFillColor(colors.black)
        canvas.setFont(font, size)
        canvas.drawString(x, y, text)

    def draw_rack(self, canvas):
        """Draw the rack frame, rack unit boundaries and mounting holes."""
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(1.2)
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
                canvas.setLineWidth(0.3)
                canvas.line(
                    self.rack_x, y,
                    self.rack_x + self.rack_width, y,
                )

            # Draw mounting holes at every rack unit boundary.
            canvas.setLineWidth(0.5)
            for x in (
                self.rack_x + 3 * mm,
                self.rack_x + self.rack_width - 3 * mm,
            ):
                canvas.circle(x, y, 1.1 * mm)

    def draw_component(self, canvas, component, x, width):
        """Draw one component inside the specified horizontal area.

        Args:
            canvas: ReportLab canvas to draw on.
            component: Component in the format
                (top rack unit, number of rack units, name, subtitle,
                color).
            x: Left x-coordinate of the component box.
            width: Width of the component box.
        """
        top, span, label, subtitle, color = component
        y = self.rack_unit_y(top - span + 1)
        height = span * self.rack_unit_height

        canvas.setFillColor(colors.HexColor(color))
        canvas.setStrokeColor(self.frame_color)
        canvas.setLineWidth(1)
        canvas.rect(
            x,
            y + self.inset_y,
            width,
            height - 2 * self.inset_y,
            stroke=1,
            fill=1,
        )

        text_x = x + 3 * mm
        text_width = width - 6 * mm
        center_y = y + height / 2

        self.draw_text(
            canvas,
            text_x,
            center_y + (1.0 if subtitle else -0.8) * mm,
            label,
            size=7,
            bold=True,
            max_width=text_width,
        )

        if subtitle:
            self.draw_text(
                canvas,
                text_x,
                center_y - 2.5 * mm,
                subtitle,
                size=6,
                max_width=text_width,
            )

    def draw_rack_unit_numbers(self, canvas):
        """Draw the rack unit numbers on the right side of the rack."""
        canvas.setFillColor(colors.black)
        canvas.setFont("Helvetica-Bold", 7)

        for rack_unit in range(1, self.total_rack_units + 1):
            canvas.drawRightString(
                self.rack_x + self.rack_width - 4 * mm,
                self.rack_unit_y(rack_unit)
                + self.rack_unit_height
                - 3.8 * mm,
                f"{rack_unit} HE",
            )

    def draw(self):
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
                canvas.setLineWidth(1)

                top = group[0][0]
                span = group[0][1]
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


def create_pdf(portrait_orientation=True):
    """Create the rack layout and port plans in a single PDF.

    Args:
        portrait_orientation: Whether to create the PDF in A4 portrait
            format. If False, A4 landscape format is used.

    Returns:
        Path to the generated PDF file.
    """
    created_at = datetime.now().astimezone()
    created_at_text = created_at.strftime(
        "Stand: %d.%m.%Y – %H:%M Uhr"
    )

    total_rack_units = RACK_INFO["total_rack_units"]
    validated_layout = validate_layout(RACK_LAYOUT, total_rack_units)
    layout = add_reserve_units(validated_layout, total_rack_units)

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    if TIMESTAMP_IN_FILE_NAME:
        file_name = created_at.strftime(
            "network_rack_documentation_%Y-%m-%d_%H-%M-%S.pdf"
        )
    else:
        file_name = "network_rack_documentation.pdf"

    pdf_file = OUTPUT_FOLDER / file_name

    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=(
            portrait(A4)
            if portrait_orientation
            else landscape(A4)
        ),
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=DOCUMENT_TITLE,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PortplanTitel", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=16, leading=20,
        spaceAfter=6 * mm,
    )
    subtitle_style = ParagraphStyle(
        "PortplanUntertitel", parent=styles["Normal"],
        fontSize=9, leading=12, textColor=colors.HexColor("#666666"),
    )
    vlan_reference_style = ParagraphStyle(
        "VlanReferenz", parent=styles["Normal"],
        fontSize=9, leading=12,
    )
    cell_style = ParagraphStyle(
        "PortplanZelle", parent=styles["Normal"],
        fontSize=9, leading=12,
    )
    centered_style = ParagraphStyle(
        "PortplanZentriert", parent=cell_style, alignment=1,
    )
    header_style = ParagraphStyle(
        "PortplanKopf", parent=cell_style,
        fontName="Helvetica-Bold", textColor=colors.white,
    )

    def paragraph(value, style):
        """Convert a value into an escaped ReportLab paragraph.

        Args:
            value: Text, number, or None.
            style: ReportLab paragraph style.

        Returns:
            ReportLab paragraph with escaped text and support for
            manual line breaks.
        """
        text = "" if value is None else str(value)
        return Paragraph(
            escape(text).replace("\n", "<br/>"),
            style,
        )

    def vlan_reference_elements():
        """Create the VLAN reference list shown above each port table.

        Returns:
            List of PDF elements, or an empty list if no VLANs are
            configured.
        """
        if not VLAN_REFERENCES:
            return []

        vlan_text = "<br/>".join(
            f"<b>VLAN {vlan_id}</b> – {escape(name)}"
            for vlan_id, name in VLAN_REFERENCES
        )

        return [
            Paragraph(vlan_text, vlan_reference_style),
            Spacer(1, 6 * mm),
        ]

    def rack_page():
        """Create the PDF elements for the network rack layout page.

        Returns:
            List of PDF elements for the first page.
        """
        # Reserve vertical space for the page title, subtitle and
        # timestamp.
        title_height = 28 * mm
        spacing = 8 * mm

        available_width = doc.width
        available_height = (
            doc.height
            - title_height
            - spacing
        )

        return [
            paragraph(RACK_INFO["title"], title_style),
            paragraph(RACK_INFO["subtitle"], subtitle_style),
            paragraph(created_at_text, subtitle_style),
            Spacer(1, 5 * mm),
            RackLayout(
                layout=layout,
                total_rack_units=total_rack_units,
                width=available_width,
                height=available_height,
            ),
        ]

    def port_plan_page(component):
        """Create the PDF elements for one component port plan page.

        Args:
            component: Component configuration containing a title and a
                list of port entries.

        Returns:
            List of PDF elements for the component page.
        """
        elements = [
            paragraph(component["title"], title_style),
            paragraph(created_at_text, subtitle_style),
            Spacer(1, 5 * mm),
        ]

        elements.extend(vlan_reference_elements())

        data = [[
            paragraph(name, header_style)
            for name in ("Port", "Ziel", "VLAN", "PoE", "Bemerkung")
        ]]

        for port, destination, vlan, poe, remark in component["ports"]:
            data.append([
                paragraph(port, centered_style),
                paragraph(destination, cell_style),
                paragraph(vlan, centered_style),
                paragraph(poe, centered_style),
                paragraph(remark, cell_style),
            ])

        table = Table(
            data,
            colWidths=[
                doc.width * proportion
                for proportion in (0.09, 0.30, 0.09, 0.09, 0.43)
            ],
            repeatRows=1,
            hAlign="LEFT",
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b3bac3")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#f2f6fa")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        elements.append(table)
        return elements

    elements = rack_page()

    # Create one separate PDF page for every configured component.
    for component in RACK_COMPONENTS:
        elements.append(PageBreak())
        elements.extend(port_plan_page(component))

    def footer(canvas, document):
        """Draw the page number in the bottom-right corner.

        Args:
            canvas: ReportLab canvas to draw on.
            document: ReportLab document being rendered.
        """
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawRightString(
            document.pagesize[0] - document.rightMargin,
            9 * mm,
            f"Seite {document.page}",
        )
        canvas.restoreState()

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)

    print(f"PDF created: {pdf_file}")
    return pdf_file


if __name__ == "__main__":
    create_pdf(portrait_orientation=PORTRAIT_ORIENTATION)