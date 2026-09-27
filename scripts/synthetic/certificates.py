"""Certificate templates: fire safety, boiler inspection, ISO, business registration.

Issuing bodies are fictional. Values go through `val()` so the stress set can drop a
rubber stamp or scribble over any single field.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from html import escape

from .common import SYNTHETIC_NOTICE
from .svg import emblem, guilloche_data_uri, rect_stamp, seal, signature


@dataclass(frozen=True)
class Page:
    """A renderable document: HTML plus print settings."""

    html: str
    landscape: bool = False
    margin_mm: int = 0
    header_html: str = ""
    footer_html: str = ""


CERT_CSS = """
@page { size: __SIZE__; margin: 0 }
html, body { margin: 0; padding: 0; }
body { font-family: 'Times New Roman', 'Liberation Serif', Georgia, serif; color: #1d1d1f; }
.page { width: 210mm; height: 297mm; position: relative; overflow: hidden; box-sizing: border-box;
        background: __PAPER__; }
.page.landscape { width: 297mm; height: 210mm; }
.frame { position: absolute; inset: 9mm; border: 2.2px solid __INK__; padding: 3px; }
.frame-inner { position: absolute; inset: 3px; border: 1px solid __INK__; }
.band { position: absolute; left: 12mm; right: 12mm; height: 13mm; background-image: url("__BAND__");
        background-size: auto 100%; opacity: .55; }
.band.top { top: 12mm } .band.bottom { bottom: 12mm }
.content { position: absolute; inset: 28mm 22mm 26mm 22mm; }
.head { text-align: center; }
.authority { font-size: 17pt; font-weight: 700; letter-spacing: .6px; color: __INK__; margin-top: 6px; }
.sub { font-size: 10.5pt; color: #444; margin-top: 2px; }
h1 { font-size: 25pt; letter-spacing: 3px; margin: 18px 0 4px; color: __INK__; }
.lead { text-align: center; font-size: 11pt; font-style: italic; color: #333; margin-bottom: 18px; }
table.kv { width: 100%; border-collapse: collapse; font-size: 11.5pt; }
table.kv td { padding: 6px 4px; vertical-align: top; border-bottom: 1px dotted #9aa; }
table.kv td.k { width: 42%; font-weight: 700; }
table.kv td + td { font-family: 'Courier New', 'Liberation Mono', monospace; font-size: 11.5pt; }
.v { position: relative; }
.v .over { position: absolute; left: -30px; top: -26px; }
.v .over.scribble { left: -6px; top: -26px; mix-blend-mode: multiply; }
.conditions { font-size: 9.5pt; margin-top: 14px; line-height: 1.45; }
.conditions ol { margin: 4px 0 0 18px; padding: 0; }
.signrow { position: absolute; left: 0; right: 0; bottom: 6mm; display: flex;
           justify-content: space-between; align-items: flex-end; }
.signbox { width: 70mm; text-align: center; font-size: 10pt; }
.signbox .line { border-top: 1px solid #333; padding-top: 3px; }
.ref { position: absolute; top: 26.5mm; right: 21mm; font-size: 8.5pt; color: #555; font-family: Arial, sans-serif; }
.notice { position: absolute; bottom: 3.5mm; left: 0; right: 0; text-align: center;
          font: 6.5pt Arial, 'Liberation Sans', sans-serif; color: #9a9a9a; }
"""


def _doc(pages: list[str], ink: str, paper: str, band_seed: int, landscape: bool = False) -> str:
    css = (
        CERT_CSS.replace("__SIZE__", "A4 landscape" if landscape else "A4")
        .replace("__INK__", ink)
        .replace("__PAPER__", paper)
        .replace("__BAND__", guilloche_data_uri(ink, seed=band_seed))
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8'><style>"
        + css
        + "</style></head><body>"
        + "".join(pages)
        + "</body></html>"
    )


def val(key: str, text: str, overlay: dict[str, str] | None, rng: random.Random) -> str:
    """Render a field value, optionally with a stamp or scribble on top (stress set)."""
    inner = escape(text)
    if overlay and overlay.get("field") == key:
        if overlay["kind"] == "stamp":
            inner += (
                f'<span class="over">{rect_stamp(["RECEIVED", overlay.get("text", "")])}</span>'
            )
        else:
            inner += f'<span class="over scribble">{signature(rng, 150, "#0d2a8a")}</span>'
    return f'<span class="v">{inner}</span>'


def _kv(rows: list[tuple[str, str]]) -> str:
    return (
        "<table class='kv'>"
        + "".join(f"<tr><td class='k'>{escape(k)}:</td><td>{v}</td></tr>" for k, v in rows)
        + "</table>"
    )


def _page(body: str, cls: str = "") -> str:
    return (
        f"<section class='page {cls}'><div class='frame'><div class='frame-inner'></div></div>"
        f"<div class='band top'></div><div class='band bottom'></div>{body}"
        f"<div class='notice'>{escape(SYNTHETIC_NOTICE)}</div></section>"
    )


# --------------------------------------------------------------------------- fire safety
def fire_safety_certificate(
    d: dict[str, str], rng: random.Random, overlay: dict[str, str] | None = None
) -> Page:
    ink = "#7a1414"
    rows = [
        ("Certificate No", val("certificate_number", d["certificate_number"], overlay, rng)),
        ("Name of Premises", val("premises_name", d["premises_name"], overlay, rng)),
        ("Address of Premises", escape(d["address"])),
        ("Occupancy Classification", escape(d["occupancy"])),
        ("Maximum Permitted Occupancy", escape(d["max_occupancy"])),
        ("Date of Inspection", escape(d["inspection_date"])),
        ("Date of Issue", val("issue_date", d["issue_date"], overlay, rng)),
        ("Valid Until", val("expiry_date", d["expiry_date"], overlay, rng)),
    ]
    body = f"""
    <div class='ref'>Ref: {escape(d["ref"])}</div>
    <div class='content'>
      <div class='head'>{emblem("flame", ink)}
        <div class='authority'>{escape(d["issuing_authority"]).upper()}</div>
        <div class='sub'>{escape(d["division"])} &middot; Fire Prevention Branch</div>
      </div>
      <h1 style='text-align:center'>FIRE SAFETY CERTIFICATE</h1>
      <div class='lead'>This is to certify that the premises described below were inspected and found to
        comply with the fire prevention and protection requirements applicable to their occupancy.</div>
      {_kv(rows)}
      <div class='conditions'><b>Conditions of this certificate</b><ol>
        <li>All fire extinguishers shall be inspected monthly and serviced annually by a registered agent.</li>
        <li>Emergency exits and escape routes shall be kept unobstructed and illuminated at all times.</li>
        <li>A fire drill shall be conducted at least once every three months and records maintained.</li>
        <li>Any structural alteration or change of occupancy invalidates this certificate.</li>
        <li>This certificate shall be displayed at a conspicuous place within the premises.</li>
      </ol></div>
      <div class='signrow'>
        <div>{seal(d["issuing_authority"].upper() + " * ", "FIRE\nPREVENTION\nBRANCH", ink)}</div>
        <div class='signbox'>{signature(rng)}<div class='line'>{escape(d["officer"])}<br>
          Chief Fire Officer, {escape(d["division"])}</div></div>
      </div>
    </div>"""
    return Page(_doc([_page(body)], ink, "#fffdf6", band_seed=11))


# --------------------------------------------------------------------------- boiler
def boiler_inspection_certificate(
    d: dict[str, str], rng: random.Random, overlay: dict[str, str] | None = None
) -> Page:
    ink = "#1f3d6b"
    rows = [
        ("Certificate No", val("certificate_number", d["certificate_number"], overlay, rng)),
        ("Owner / Occupier", escape(d["owner"])),
        ("Location of Boiler", escape(d["location"])),
        ("Boiler Registration No", val("equipment_id", d["equipment_id"], overlay, rng)),
        ("Type of Boiler", escape(d["boiler_type"])),
        ("Maker and Year of Manufacture", escape(d["maker"])),
        ("Maximum Permissible Working Pressure", escape(d["pressure"])),
        ("Hydraulic Test Pressure", escape(d["test_pressure"])),
        ("Date of Inspection", escape(d["inspection_date"])),
        ("Date of Issue", val("issue_date", d["issue_date"], overlay, rng)),
        ("Date of Expiry", val("expiry_date", d["expiry_date"], overlay, rng)),
    ]
    body = f"""
    <div class='ref'>File No: {escape(d["ref"])}</div>
    <div class='content' style='top:24mm'>
      <div class='head'>{emblem("gear", ink)}
        <div class='authority'>{escape(d["issuing_authority"]).upper()}</div>
        <div class='sub'>Statutory Inspection of Steam Boilers and Pressure Vessels</div>
      </div>
      <h1 style='text-align:center;font-size:21pt'>CERTIFICATE OF INSPECTION</h1>
      <div class='lead'>Steam Boiler &mdash; Thorough Examination (Internal, External and Hydraulic)</div>
      {_kv(rows)}
      <div class='conditions'>The boiler described above was thoroughly examined on the date stated and is
        in a fit condition to be worked at the pressure shown, subject to: (a) safety valves being set at
        or below the permissible working pressure; (b) water level gauges and low-water cut-off being
        tested daily by the attendant; (c) the boiler being operated only by a certified attendant.</div>
      <div class='signrow'>
        <div class='signbox'>{signature(rng)}<div class='line'>{escape(d["officer"])}<br>Chartered Engineer, Inspecting Officer</div></div>
        <div>{seal(d["issuing_authority"].upper() + " * ", "BOILER\nINSPECTION", ink, rotate=6)}</div>
      </div>
    </div>"""
    return Page(_doc([_page(body)], ink, "#fbfcff", band_seed=23))


# --------------------------------------------------------------------------- ISO
def iso_certificate(
    d: dict[str, str], rng: random.Random, overlay: dict[str, str] | None = None
) -> Page:
    ink = "#0f5a45"
    body = f"""
    <div class='content' style='inset:24mm 28mm 22mm 28mm;text-align:center'>
      <div class='head' style='display:flex;align-items:center;justify-content:center;gap:14px'>
        {emblem("leaf", ink, 58)}<div style='text-align:left'>
        <div class='authority' style='margin:0'>{escape(d["certification_body"]).upper()}</div>
        <div class='sub'>Management System Certification</div></div></div>
      <h1 style='font-size:30pt;margin-top:14px'>CERTIFICATE</h1>
      <div style='font-size:12pt'>This is to certify that the Environmental Management System of</div>
      <div style='font-size:20pt;font-weight:700;margin:8px 0 2px'>{escape(d["company"])}</div>
      <div style='font-size:11pt'>{escape(d["address"])}</div>
      <div style='font-size:12pt;margin-top:10px'>has been assessed and found to conform to the requirements of</div>
      <div style='font-size:24pt;font-weight:700;color:{ink};margin:6px 0'>{val("standard_name", d["standard_name"], overlay, rng)}</div>
      <div style='font-size:11pt;max-width:190mm;margin:0 auto'><b>Scope of certification:</b> {escape(d["scope"])}</div>
      <table class='kv' style='width:150mm;margin:14px auto 0;font-size:11pt;text-align:left'>
        <tr><td class='k'>Certificate Number:</td><td>{val("certificate_number", d["certificate_number"], overlay, rng)}</td></tr>
        <tr><td class='k'>Initial Certification Date:</td><td>{escape(d["initial_date"])}</td></tr>
        <tr><td class='k'>Issue Date:</td><td>{val("issue_date", d["issue_date"], overlay, rng)}</td></tr>
        <tr><td class='k'>Expiry Date:</td><td>{val("expiry_date", d["expiry_date"], overlay, rng)}</td></tr>
      </table>
      <div class='signrow' style='bottom:0'>
        <div>{seal(d["certification_body"].upper() + " * ", "CERTIFIED\nEMS", ink, 120, rotate=-4)}</div>
        <div class='signbox'>{signature(rng)}<div class='line'>{escape(d["officer"])}<br>Head of Certification</div></div>
      </div>
      <div style='position:absolute;bottom:-8mm;left:0;right:0;font-size:7.5pt;color:#555'>
        Validity of this certificate is subject to satisfactory annual surveillance audits.
        Verify at the certification body register quoting the certificate number.</div>
    </div>"""
    return Page(
        _doc([_page(body, "landscape")], ink, "#fcfffb", band_seed=37, landscape=True),
        landscape=True,
    )


# --------------------------------------------------------------------------- business registration
def business_registration(
    d: dict[str, str], rng: random.Random, overlay: dict[str, str] | None = None
) -> Page:
    ink = "#3a2a10"
    body = f"""
    <div class='ref'>Form 2A</div>
    <div class='content' style='text-align:center'>
      <div class='head'>{emblem("pillar", ink)}
        <div class='authority'>{escape(d["registry"]).upper()}</div>
        <div class='sub'>Democratic Socialist Republic of Sri Lanka</div></div>
      <h1 style='font-size:22pt'>CERTIFICATE OF INCORPORATION</h1>
      <div style='font-size:11pt;margin-bottom:22px'>(Issued under Section 5 of the Companies Act, No. 7 of 2007)</div>
      <div style='font-size:13pt;line-height:2'>I hereby certify that<br>
        <span style='font-size:19pt;font-weight:700'>{val("company_name", d["company_name"], overlay, rng)}</span><br>
        is on this day incorporated under the Companies Act, No. 7 of 2007,<br>
        and that the company is a private limited company.</div>
      <table class='kv' style='width:140mm;margin:26px auto 0;text-align:left'>
        <tr><td class='k'>Company Registration No:</td><td>{val("registration_number", d["registration_number"], overlay, rng)}</td></tr>
        <tr><td class='k'>Date of Incorporation:</td><td>{val("registration_date", d["registration_date"], overlay, rng)}</td></tr>
        <tr><td class='k'>Registered Office:</td><td>{escape(d["address"])}</td></tr>
      </table>
      <div style='font-size:11pt;margin-top:24px'>Given under my hand at Colombo on {escape(d["given_on"])}.</div>
      <div class='signrow'>
        <div>{seal(d["registry"].upper() + " * ", "OFFICIAL\nSEAL", ink, 135)}</div>
        <div class='signbox'>{signature(rng)}<div class='line'>{escape(d["officer"])}<br>Registrar</div></div>
      </div>
    </div>"""
    return Page(_doc([_page(body)], ink, "#fffaf0", band_seed=41))
