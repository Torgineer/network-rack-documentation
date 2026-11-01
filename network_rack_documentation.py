# %%
# -*- coding: utf-8 -*-
"""Network rack documentation as PDF.

Creates port plans and other rack documentation pages.

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
    PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


# =============================================================
# EINSTELLUNGEN – hier manuell anpassen
# =============================================================
TITEL = "Netzwerkschrank – Portplan"


# True: A4-Hochformat / False: A4-Querformat
HOCHFORMAT = True


# True: jede PDF mit Zeitstempel im Dateinamen speichern.
# False: patchpanel_portplan.pdf bei jedem Lauf überschreiben.
ZEITSTEMPEL_IM_DATEINAMEN = True


# Ausgabeordner neben dieser Python-Datei.
AUSGABEORDNER = Path(__file__).resolve().parent / "output"


# VLAN-Referenzliste: (VLAN-ID, Name)
VLAN_REFERENZ = [
    (1, "Default"),
    (10, "Home"),
    (20, "IoT"),
    (30, "Guest"),
    (40, "Camera"),
]


# Format je Eintrag: (Port, Ziel, VLAN, PoE, Bemerkung)
# Die folgenden Belegungen sind Beispiele – bitte anpassen.
PORTS_PATCHFELD = [
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
]


# Format je Eintrag: (Port, Ziel, VLAN, PoE, Bemerkung)
# Die folgenden Belegungen sind Beispiele – bitte anpassen.
PORTS_SWITCH = [
    (1, "Patchpanel Port 2\nBüro: Access Point - U7 In-Wall", "1", "Ja", ""),
    (2, "Patchpanel Port 3\nWohnzimmer: Access Point - U6+", "1", "Ja", ""),
    (3, "Patchpanel Port 4\nFlur: Access Point - U7-Pro-XG", "1", "Ja", ""),
    (4, "", "", "Ja", ""),
    (5, "Proxmox Host M720q", "1", "Nein", ""),
    (6, "", "", "Nein", ""),
    (7, "", "", "Nein", ""),
    (8, "UCG-Ultra LAN out", "", "Nein", ""),
]


# Format je Eintrag: (Port, Ziel, VLAN, PoE, Bemerkung)
# Die folgenden Belegungen sind Beispiele – bitte anpassen.
PORTS_UCG_ULTRA = [
    (1, "Switch Lite-8-PoE", "1", "Nein", ""),
    (2, "", "", "", ""),
    (3, "", "", "", ""),
    (4, "", "", "", ""),
    (5, "WAN", "", "Nein", "Uplink"),
]

def erstelle_pdf(hochformat=True):
    """Erstellt Patchpanel-, Switch- und UCG-Ultra-Portplan in einer PDF.


    Jeder Plan erhält eine eigene Seite.
    Gibt den Pfad zur erzeugten PDF zurück.
    """
    erstellt_am = datetime.now().astimezone()
    unterzeile = erstellt_am.strftime("Stand: %d.%m.%Y – %H:%M Uhr")


    AUSGABEORDNER.mkdir(parents=True, exist_ok=True)
    if ZEITSTEMPEL_IM_DATEINAMEN:
        dateiname = erstellt_am.strftime(
            "netzwerkschrank_portplan_%Y-%m-%d_%H-%M-%S.pdf"
        )
    else:
        dateiname = "netzwerkschrank_portplan.pdf"
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


    def portplan_elemente(ueberschrift, ports):
        elemente = [
            absatz(ueberschrift, titel_stil),
            absatz(unterzeile, untertitel_stil),
            Spacer(1, 5 * mm),
        ]


        elemente.extend(vlan_referenz_elemente())


        daten = [[
            absatz(name, kopf_stil)
            for name in ("Port", "Ziel", "VLAN", "PoE", "Bemerkung")
        ]]


        for port, ziel, vlan, poe, bemerkung in ports:
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


    elemente = []
    elemente.extend(
        portplan_elemente("Patchpanel-Portplan", PORTS_PATCHFELD)
    )
    elemente.append(PageBreak())
    elemente.extend(
        portplan_elemente("Switch-Portplan Lite-8-PoE", PORTS_SWITCH)
    )
    elemente.append(PageBreak())
    elemente.extend(
        portplan_elemente("UCG-Ultra-Portplan", PORTS_UCG_ULTRA)
    )


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
