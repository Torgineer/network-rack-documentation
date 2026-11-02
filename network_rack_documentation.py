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
DOCUMENT_TITLE = "Netzwerkschrank – Dokumentation"

# True: A4 portrait / False: A4 landscape
PORTRAIT_ORIENTATION = True

# True: save every PDF with a timestamp in its file name.
# False: overwrite netzwerkschrank_dokumentation.pdf on every run.
TIMESTAMP_IN_FILE_NAME = True

# Output folder next to this Python file.
OUTPUT_FOLDER = Path(__file__).resolve().parent / "output"


def validate_layout(layout, total_rack_units):
    """Validate rack unit ranges and duplicate occupancy."""
    if total_rack_units < 1:
        raise ValueError(
            "RACK_INFO['total_rack_units'] must be at least 1."
        )

    available_rack_units = set(range(1, total_rack_units + 1))

    for top, span, label, *_ in layout:
        if type(top) is not int or type(span) is not int:
            raise ValueError(
                f"{label}: rack unit and number of rack units "
                "must be integers."
            )

        if span < 1 or top > total_rack_units or top - span < 0:
            raise ValueError(f"{label}: invalid rack unit range.")

        occupied_rack_units = set(range(top - span + 1, top + 1))

        if not occupied_rack_units <= available_rack_units:
            raise ValueError(f"{label}: rack unit is occupied twice.")

        available_rack_units -= occupied_rack_units

    return layout


def add_reserve_units(layout, total_rack_units):
    """Add all unoccupied rack units as reserve space."""
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


class RackLayout(Flowable):
    """Draw the network rack layout as a flowable for the PDF."""

    def __init__(self, layout, total_rack_units, width, height):
        super().__init__()
        self.layout = layout
        self.total_rack_units = total_rack_units
        self.width = width
        self.height = height

        self.rack_x = 0
        self.rack_width = width * 0.52
        self.rack_bottom = 0
        self.rack_top = height
        self.rack_unit_height = height / total_rack_units

        self.inset_x = 1.2 * mm
        self.inset_y = 0.6 * mm
        self.frame_color = colors.HexColor("#555555")

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def rack_unit_y(self, rack_unit):
        return self.rack_bottom + (
            (rack_unit - 1) * self.rack_unit_height
        )

    def draw_text(self, canvas, x, y, text, size=9, bold=False,
                  max_width=None):
        font = "Helvetica-Bold" if bold else "Helvetica"

        if max_width is not None:
            text_width = canvas.stringWidth(text, font, size)
            if text_width > max_width:
                size *= max_width / text_width

        canvas.setFillColor(colors.black)
        canvas.setFont(font, size)
        canvas.drawString(x, y, text)

    def draw_rack(self, canvas):
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

            if 0 < boundary < self.total_rack_units:
                canvas.setLineWidth(0.3)
                canvas.line(
                    self.rack_x, y,
                    self.rack_x + self.rack_width, y,
                )

            canvas.setLineWidth(0.5)
            for x in (
                self.rack_x + 3 * mm,
                self.rack_x + self.rack_width - 3 * mm,
            ):
                canvas.circle(x, y, 1.1 * mm)

    def draw_component(self, canvas, top, span, label, subtitle, color):
        y = self.rack_unit_y(top - span + 1)
        height = span * self.rack_unit_height
        box_x = self.rack_x + self.inset_x
        box_width = self.rack_width - 2 * self.inset_x

        canvas.setFillColor(colors.HexColor(color))
        canvas.setStrokeColor(self.frame_color)
        canvas.setLineWidth(1)
        canvas.rect(
            box_x,
            y + self.inset_y,
            box_width,
            height - 2 * self.inset_y,
            stroke=1,
            fill=1,
        )

        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(0.3)
        for offset in range(1, span):
            line_y = y + offset * self.rack_unit_height
            canvas.line(box_x, line_y, box_x + box_width, line_y)

        text_x = self.rack_x + 5 * mm
        text_width = self.rack_width - 23 * mm
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
        canvas = self.canv
        self.draw_rack(canvas)

        for component in self.layout:
            self.draw_component(canvas, *component)

        self.draw_rack_unit_numbers(canvas)


def create_pdf(portrait_orientation=True):
    """Create the rack layout and port plans in a single PDF."""
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
        text = "" if value is None else str(value)
        return Paragraph(
            escape(text).replace("\n", "<br/>"),
            style,
        )

    def vlan_reference_elements():
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

    for component in RACK_COMPONENTS:
        elements.append(PageBreak())
        elements.extend(port_plan_page(component))

    def footer(canvas, document):
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