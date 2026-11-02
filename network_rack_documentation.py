# %%
# -*- coding: utf-8 -*-
"""Netzwerkschrank-Dokumentation als PDF.

Erzeugt eine PDF mit Rack-Aufteilung und Portplänen.

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
    VLAN_REFERENZ,
)

# =============================================================
# EINSTELLUNGEN – hier manuell anpassen
# =============================================================
TITEL = "Netzwerkschrank – Dokumentation"

# True: A4-Hochformat / False: A4-Querformat
HOCHFORMAT = True

# True: jede PDF mit Zeitstempel im Dateinamen speichern.
# False: netzwerkschrank_dokumentation.pdf bei jedem Lauf überschreiben.
ZEITSTEMPEL_IM_DATEINAMEN = True

# Ausgabeordner neben dieser Python-Datei.
AUSGABEORDNER = Path(__file__).resolve().parent / "output"


def pruefe_layout(layout, gesamt_he):
    """Prüft HE-Bereiche und doppelte Belegungen."""
    if gesamt_he < 1:
        raise ValueError("RACK_INFO['gesamt_he'] muss mindestens 1 sein.")

    freie_he = set(range(1, gesamt_he + 1))

    for top, span, label, *_ in layout:
        if type(top) is not int or type(span) is not int:
            raise ValueError(
                f"{label}: HE und Anzahl HE müssen ganze Zahlen sein."
            )

        if span < 1 or top > gesamt_he or top - span < 0:
            raise ValueError(f"{label}: ungültiger HE-Bereich.")

        belegte_he = set(range(top - span + 1, top + 1))

        if not belegte_he <= freie_he:
            raise ValueError(f"{label}: HE doppelt belegt.")

        freie_he -= belegte_he

    return layout


def ergaenze_reserven(layout, gesamt_he):
    """Ergänzt alle freien HE als Reserve."""
    belegte_he = set()

    for top, span, *_ in layout:
        belegte_he.update(range(top - span + 1, top + 1))

    freie_he = set(range(1, gesamt_he + 1)) - belegte_he

    reserven = [
        (he, 1, "Reserve", "", RESERVE_COLOR)
        for he in freie_he
    ]

    return sorted(layout + reserven, reverse=True)


class RackAufteilung(Flowable):
    """Zeichnet die Rack-Aufteilung als Flowable für die PDF."""

    def __init__(self, layout, gesamt_he, breite, hoehe):
        super().__init__()
        self.layout = layout
        self.gesamt_he = gesamt_he
        self.breite = breite
        self.hoehe = hoehe

        self.rack_x = 0
        self.rack_w = breite * 0.52
        self.rack_bottom = 0
        self.rack_top = hoehe
        self.he_hoehe = hoehe / gesamt_he

        self.inset_x = 1.2 * mm
        self.inset_y = 0.6 * mm
        self.frame_color = colors.HexColor("#555555")

    def wrap(self, available_width, available_height):
        return self.breite, self.hoehe

    def he_y(self, he):
        return self.rack_bottom + (he - 1) * self.he_hoehe

    def draw_text(self, canvas, x, y, text, size=9, bold=False,
                  max_width=None):
        font = "Helvetica-Bold" if bold else "Helvetica"

        if max_width is not None:
            width = canvas.stringWidth(text, font, size)
            if width > max_width:
                size *= max_width / width

        canvas.setFillColor(colors.black)
        canvas.setFont(font, size)
        canvas.drawString(x, y, text)

    def draw_rack(self, canvas):
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(1.2)
        canvas.rect(
            self.rack_x,
            self.rack_bottom,
            self.rack_w,
            self.rack_top - self.rack_bottom,
        )

        for boundary in range(self.gesamt_he + 1):
            y = self.he_y(boundary + 1)

            if 0 < boundary < self.gesamt_he:
                canvas.setLineWidth(0.3)
                canvas.line(
                    self.rack_x, y,
                    self.rack_x + self.rack_w, y,
                )

            canvas.setLineWidth(0.5)
            for x in (
                self.rack_x + 3 * mm,
                self.rack_x + self.rack_w - 3 * mm,
            ):
                canvas.circle(x, y, 1.1 * mm)

    def draw_component(self, canvas, top, span, label, subtitle, color):
        y = self.he_y(top - span + 1)
        height = span * self.he_hoehe
        box_x = self.rack_x + self.inset_x
        box_w = self.rack_w - 2 * self.inset_x

        canvas.setFillColor(colors.HexColor(color))
        canvas.setStrokeColor(self.frame_color)
        canvas.setLineWidth(1)
        canvas.rect(
            box_x,
            y + self.inset_y,
            box_w,
            height - 2 * self.inset_y,
            stroke=1,
            fill=1,
        )

        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(0.3)
        for offset in range(1, span):
            line_y = y + offset * self.he_hoehe
            canvas.line(box_x, line_y, box_x + box_w, line_y)

        text_x = self.rack_x + 5 * mm
        text_width = self.rack_w - 23 * mm
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

    def draw_he_numbers(self, canvas):
        canvas.setFillColor(colors.black)
        canvas.setFont("Helvetica-Bold", 7)

        for he in range(1, self.gesamt_he + 1):
            canvas.drawRightString(
                self.rack_x + self.rack_w - 4 * mm,
                self.he_y(he) + self.he_hoehe - 3.8 * mm,
                f"{he} HE",
            )

    def draw(self):
        canvas = self.canv
        self.draw_rack(canvas)

        for component in self.layout:
            self.draw_component(canvas, *component)

        self.draw_he_numbers(canvas)


def erstelle_pdf(hochformat=True):
    """Erstellt Rack-Aufteilung und Portpläne in einer PDF."""
    erstellt_am = datetime.now().astimezone()
    unterzeile = erstellt_am.strftime("Stand: %d.%m.%Y – %H:%M Uhr")

    gesamt_he = RACK_INFO["gesamt_he"]
    geprueftes_layout = pruefe_layout(RACK_LAYOUT, gesamt_he)
    layout = ergaenze_reserven(geprueftes_layout, gesamt_he)

    AUSGABEORDNER.mkdir(parents=True, exist_ok=True)

    if ZEITSTEMPEL_IM_DATEINAMEN:
        dateiname = erstellt_am.strftime(
            "netzwerkschrank_dokumentation_%Y-%m-%d_%H-%M-%S.pdf"
        )
    else:
        dateiname = "netzwerkschrank_dokumentation.pdf"

    pdf_datei = AUSGABEORDNER / dateiname

    doc = SimpleDocTemplate(
        str(pdf_datei),
        pagesize=portrait(A4) if hochformat else landscape(A4),
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=TITEL,
    )

    styles = getSampleStyleSheet()

    titel_stil = ParagraphStyle(
        "PortplanTitel", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=16, leading=20,
        spaceAfter=6 * mm,
    )
    untertitel_stil = ParagraphStyle(
        "PortplanUntertitel", parent=styles["Normal"],
        fontSize=9, leading=12, textColor=colors.HexColor("#666666"),
    )
    vlan_referenz_stil = ParagraphStyle(
        "VlanReferenz", parent=styles["Normal"],
        fontSize=9, leading=12,
    )
    zellen_stil = ParagraphStyle(
        "PortplanZelle", parent=styles["Normal"],
        fontSize=9, leading=12,
    )
    zentriert_stil = ParagraphStyle(
        "PortplanZentriert", parent=zellen_stil, alignment=1,
    )
    kopf_stil = ParagraphStyle(
        "PortplanKopf", parent=zellen_stil,
        fontName="Helvetica-Bold", textColor=colors.white,
    )

    def absatz(wert, stil):
        text = "" if wert is None else str(wert)
        return Paragraph(escape(text).replace("\n", "<br/>"), stil)

    def vlan_referenz_elemente():
        if not VLAN_REFERENZ:
            return []

        vlan_text = "<br/>".join(
            f"<b>VLAN {vlan_id}</b> – {escape(name)}"
            for vlan_id, name in VLAN_REFERENZ
        )

        return [
            Paragraph(vlan_text, vlan_referenz_stil),
            Spacer(1, 6 * mm),
        ]

    def rack_seite():
        titel_hoehe = 28 * mm
        abstand = 8 * mm

        verfuegbare_breite = doc.width
        verfuegbare_hoehe = (
            doc.height
            - titel_hoehe
            - abstand
        )

        elemente = [
            absatz(RACK_INFO["titel"], titel_stil),
            absatz(RACK_INFO["untertitel"], untertitel_stil),
            absatz(unterzeile, untertitel_stil),
            Spacer(1, 5 * mm),
            RackAufteilung(
                layout=layout,
                gesamt_he=gesamt_he,
                breite=verfuegbare_breite,
                hoehe=verfuegbare_hoehe,
            ),
        ]

        return elemente

    def portplan_seite(komponente):
        elemente = [
            absatz(komponente["titel"], titel_stil),
            absatz(unterzeile, untertitel_stil),
            Spacer(1, 5 * mm),
        ]

        elemente.extend(vlan_referenz_elemente())

        daten = [[
            absatz(name, kopf_stil)
            for name in ("Port", "Ziel", "VLAN", "PoE", "Bemerkung")
        ]]

        for port, ziel, vlan, poe, bemerkung in komponente["ports"]:
            daten.append([
                absatz(port, zentriert_stil),
                absatz(ziel, zellen_stil),
                absatz(vlan, zentriert_stil),
                absatz(poe, zentriert_stil),
                absatz(bemerkung, zellen_stil),
            ])

        tabelle = Table(
            daten,
            colWidths=[
                doc.width * anteil
                for anteil in (0.09, 0.30, 0.09, 0.09, 0.43)
            ],
            repeatRows=1,
            hAlign="LEFT",
        )

        tabelle.setStyle(TableStyle([
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

        elemente.append(tabelle)
        return elemente

    elemente = rack_seite()

    for komponente in RACK_COMPONENTS:
        elemente.append(PageBreak())
        elemente.extend(portplan_seite(komponente))

    def fusszeile(canvas, dokument):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawRightString(
            dokument.pagesize[0] - dokument.rightMargin,
            9 * mm,
            f"Seite {dokument.page}",
        )
        canvas.restoreState()

    doc.build(elemente, onFirstPage=fusszeile, onLaterPages=fusszeile)

    print(f"PDF erstellt: {pdf_datei}")
    return pdf_datei


if __name__ == "__main__":
    erstelle_pdf(hochformat=HOCHFORMAT)