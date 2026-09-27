"""Utility bill templates (fictional providers). One page each, printed-invoice style."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import timedelta
from html import escape

from .certificates import Page
from .common import SYNTHETIC_NOTICE, Factory, Month, fmt_date, money
from .svg import emblem, rect_stamp, signature

BILL_CSS = """
@page { size: A4; margin: 0 }
html, body { margin: 0; }
body { font-family: Arial, 'Liberation Sans', Helvetica, sans-serif; color: #222; font-size: 9.5pt; }
.page { width: 210mm; height: 297mm; box-sizing: border-box; padding: 12mm 14mm; position: relative; background: #fff; }
.top { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid __INK__; padding-bottom: 8px; }
.brand { display: flex; gap: 10px; align-items: center; }
.brand .name { font-size: 15pt; font-weight: 700; color: __INK__; }
.brand .tag { font-size: 8pt; color: #555; }
.doctitle { text-align: right; font-size: 13pt; font-weight: 700; }
.doctitle small { display: block; font-size: 8pt; font-weight: 400; color: #555; }
.grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: 10px; margin-top: 10px; }
.box { border: 1px solid #bbb; border-radius: 3px; padding: 7px 9px; }
.box h3 { margin: 0 0 5px; font-size: 8.5pt; text-transform: uppercase; color: __INK__; letter-spacing: .5px; }
table { border-collapse: collapse; width: 100%; }
.kv td { padding: 2px 0; } .kv td:first-child { color: #444; width: 48%; }
.kv td:last-child { font-weight: 700; }
.lines { margin-top: 12px; }
.lines th { background: __INK__; color: #fff; font-size: 8.5pt; padding: 5px 6px; text-align: left; }
.lines td { border-bottom: 1px solid #ddd; padding: 5px 6px; }
.lines td.n, .lines th.n { text-align: right; }
.total td { font-weight: 700; font-size: 11pt; border-top: 2px solid #333; }
.highlight { background: #f3f6fb; }
.usage { margin-top: 12px; }
.bars { display: flex; align-items: flex-end; gap: 4px; height: 70px; border-bottom: 1px solid #999; padding: 0 4px; }
.bars div { flex: 1; background: __INK__; opacity: .75; }
.barlabels { display: flex; gap: 4px; padding: 0 4px; font-size: 6.5pt; color: #555; }
.barlabels span { flex: 1; text-align: center; }
.stub { position: absolute; left: 14mm; right: 14mm; bottom: 16mm; border-top: 1.5px dashed #777; padding-top: 8px; }
.notes { font-size: 7.5pt; color: #555; margin-top: 10px; line-height: 1.4; }
.v { position: relative; } .v .over { position: absolute; left: -60px; top: -30px; mix-blend-mode: multiply; }
.notice { position: absolute; bottom: 5mm; left: 0; right: 0; text-align: center; font-size: 6.5pt; color: #9a9a9a; }
"""


@dataclass(frozen=True)
class Reading:
    month: Month
    value: int  # kWh or m3


def _wrap(body: str, ink: str) -> Page:
    html = (
        "<!doctype html><html><head><meta charset='utf-8'><style>"
        + BILL_CSS.replace("__INK__", ink)
        + "</style></head><body><section class='page'>"
        + body
        + f"<div class='notice'>{escape(SYNTHETIC_NOTICE)}</div></section></body></html>"
    )
    return Page(html)


def _history(history: list[Reading], ink: str, unit: str) -> str:
    mx = max(r.value for r in history) or 1
    bars = "".join(f"<div style='height:{r.value / mx * 100:.0f}%'></div>" for r in history)
    labels = "".join(f"<span>{r.month.label[:3]}</span>" for r in history)
    return (
        f"<div class='usage box'><h3>Consumption history ({unit})</h3>"
        f"<div class='bars'>{bars}</div><div class='barlabels'>{labels}</div></div>"
    )


def electricity_bill(
    f: Factory,
    m: Month,
    kwh: int,
    history: list[Reading],
    bill_no: str,
    overlay: dict[str, str] | None = None,
) -> tuple[Page, dict[str, object]]:
    ink = "#0b4f8a"
    # Time-of-use split and fictional industrial tariff
    day, peak = round(kwh * 0.58), round(kwh * 0.17)
    off = kwh - day - peak
    rates = {"day": 26.5, "peak": 35.0, "off": 17.5}
    md_kva, md_rate, fixed = round(kwh / 330), 1_650.0, 5_000.0
    energy = day * rates["day"] + peak * rates["peak"] + off * rates["off"]
    demand = md_kva * md_rate
    subtotal = energy + demand + fixed
    sscl = round(subtotal * 0.025, 2)
    total = round(subtotal + sscl, 2)
    prev = 4_812_300 + (m.year * 12 + m.month) * 311  # cumulative meter, cosmetic only
    issue = m.last_day + timedelta(days=4)
    due = issue + timedelta(days=21)
    units = f"{kwh:,}"
    if overlay:
        mark = (
            rect_stamp(["PAID", overlay.get("text", "")], "#1d6b2a")
            if overlay["kind"] == "stamp"
            else signature(random.Random(kwh), 130)
        )
        units = f"<span class='v'>{units}<span class='over'>{mark}</span></span>"
    body = f"""
    <div class='top'><div class='brand'>{emblem("bolt", ink, 52)}<div>
      <div class='name'>Western Grid Power Company</div>
      <div class='tag'>Electricity Distribution &middot; Customer Care 1900 &middot; VAT Reg 114-552-7730</div></div></div>
      <div class='doctitle'>ELECTRICITY BILL<small>Tax Invoice No. {escape(bill_no)}</small></div></div>
    <div class='grid'>
      <div class='box'><h3>Account holder</h3><table class='kv'>
        <tr><td>Account Holder:</td><td>{escape(f.name)}</td></tr>
        <tr><td>Supply Address:</td><td>{escape(", ".join(f.address))}</td></tr>
        <tr><td>Account No:</td><td>{escape(f.elec_account)}</td></tr>
        <tr><td>Tariff:</td><td>Industrial I-2 (Time of Use)</td></tr>
        <tr><td>Contract Demand:</td><td>750 kVA</td></tr></table></div>
      <div class='box'><h3>Bill summary</h3><table class='kv'>
        <tr><td>Bill Month:</td><td>{escape(m.label)}</td></tr>
        <tr><td>Billing Period:</td><td>{fmt_date(m.first_day, "slash")} - {fmt_date(m.last_day, "slash")}</td></tr>
        <tr><td>Date of Issue:</td><td>{fmt_date(issue, "slash")}</td></tr>
        <tr><td>Payment Due Date:</td><td>{fmt_date(due, "slash")}</td></tr>
        <tr class='highlight'><td>Total Units Consumed (kWh):</td><td>{units}</td></tr>
        <tr class='highlight'><td>Amount Payable (LKR):</td><td>{money(total)}</td></tr></table></div>
    </div>
    <table class='lines'><tr><th>Meter / Register</th><th class='n'>Previous Reading</th><th class='n'>Present Reading</th><th class='n'>Multiplier</th><th class='n'>Units (kWh)</th></tr>
      <tr><td>Day (05:30 - 18:30)</td><td class='n'>{prev:,}</td><td class='n'>{prev + day // 20:,}</td><td class='n'>20</td><td class='n'>{day:,}</td></tr>
      <tr><td>Peak (18:30 - 22:30)</td><td class='n'>{prev // 3:,}</td><td class='n'>{prev // 3 + peak // 20:,}</td><td class='n'>20</td><td class='n'>{peak:,}</td></tr>
      <tr><td>Off-peak (22:30 - 05:30)</td><td class='n'>{prev // 2:,}</td><td class='n'>{prev // 2 + off // 20:,}</td><td class='n'>20</td><td class='n'>{off:,}</td></tr>
      <tr class='total'><td colspan='4'>Total Units Consumed</td><td class='n'>{kwh:,}</td></tr></table>
    <table class='lines'><tr><th>Charges</th><th class='n'>Quantity</th><th class='n'>Rate (LKR)</th><th class='n'>Amount (LKR)</th></tr>
      <tr><td>Energy charge - Day</td><td class='n'>{day:,} kWh</td><td class='n'>{rates["day"]:.2f}</td><td class='n'>{money(day * rates["day"])}</td></tr>
      <tr><td>Energy charge - Peak</td><td class='n'>{peak:,} kWh</td><td class='n'>{rates["peak"]:.2f}</td><td class='n'>{money(peak * rates["peak"])}</td></tr>
      <tr><td>Energy charge - Off-peak</td><td class='n'>{off:,} kWh</td><td class='n'>{rates["off"]:.2f}</td><td class='n'>{money(off * rates["off"])}</td></tr>
      <tr><td>Maximum demand charge</td><td class='n'>{md_kva} kVA</td><td class='n'>{money(md_rate)}</td><td class='n'>{money(demand)}</td></tr>
      <tr><td>Fixed charge</td><td class='n'>1</td><td class='n'>{money(fixed)}</td><td class='n'>{money(fixed)}</td></tr>
      <tr><td>Social Security Contribution Levy (2.5%)</td><td class='n'></td><td class='n'></td><td class='n'>{money(sscl)}</td></tr>
      <tr class='total'><td colspan='3'>Amount Payable</td><td class='n'>{money(total)}</td></tr></table>
    {_history(history, ink, "kWh")}
    <div class='notes'>Readings taken by meter reader on {fmt_date(m.last_day, "slash")}. Please quote your account
      number in all correspondence. Supply may be disconnected if payment is not received within 30 days of the due date.</div>
    <div class='stub'><table class='kv'><tr><td>Payment stub &middot; Account No:</td><td>{escape(f.elec_account)}</td>
      <td>Bill Month:</td><td>{escape(m.label)}</td><td>Amount (LKR):</td><td>{money(total)}</td></tr></table></div>
    """
    gt = {
        "utility_kind": "electricity",
        "billing_period": m.period,
        "consumption_value": kwh,
        "consumption_unit": "kWh",
        "account_holder": f.name,
    }
    return _wrap(body, ink), gt


def water_bill(
    f: Factory, m: Month, m3: int, history: list[Reading], bill_no: str
) -> tuple[Page, dict[str, object]]:
    ink = "#0e7a8a"
    tiers = [(1000, 90.0), (1500, 118.0), (10**9, 142.0)]
    remaining, lines, used = m3, [], 0
    for cap, rate in tiers:
        q = min(remaining, cap - used if cap < 10**9 else remaining)
        if q <= 0:
            continue
        lines.append((f"{used + 1:,} - {used + q:,} m\u00b3", q, rate))
        used += q
        remaining -= q
    usage = sum(q * r for _, q, r in lines)
    service, drainage = 3_500.0, round(m3 * 12.0, 2)
    total = round(usage + service + drainage, 2)
    issue = m.last_day + timedelta(days=6)
    meter_prev = 918_400 + (m.year * 12 + m.month) * 3
    rows = "".join(
        f"<tr><td>Water usage charge ({escape(label)})</td><td class='n'>{q:,} m\u00b3</td><td class='n'>{r:.2f}</td><td class='n'>{money(q * r)}</td></tr>"
        for label, q, r in lines
    )
    body = f"""
    <div class='top'><div class='brand'>{emblem("drop", ink, 52)}<div>
      <div class='name'>Greater Colombo Water Services</div>
      <div class='tag'>Water Supply &amp; Drainage &middot; Hotline 1939 &middot; Industrial Accounts Unit</div></div></div>
      <div class='doctitle'>WATER BILL<small>Bill No. {escape(bill_no)}</small></div></div>
    <div class='grid'>
      <div class='box'><h3>Consumer details</h3><table class='kv'>
        <tr><td>Name of Consumer:</td><td>{escape(f.name)}</td></tr>
        <tr><td>Premises:</td><td>{escape(", ".join(f.address))}</td></tr>
        <tr><td>Account Number:</td><td>{escape(f.water_account)}</td></tr>
        <tr><td>Category:</td><td>Industrial (BOI Zone)</td></tr>
        <tr><td>Meter No:</td><td>WM-{escape(f.water_account[-6:])}</td></tr></table></div>
      <div class='box'><h3>This bill</h3><table class='kv'>
        <tr><td>Billing Month:</td><td>{escape(m.label)}</td></tr>
        <tr><td>Reading Period:</td><td>{fmt_date(m.first_day, "dot")} to {fmt_date(m.last_day, "dot")}</td></tr>
        <tr><td>Bill Date:</td><td>{fmt_date(issue, "dot")}</td></tr>
        <tr class='highlight'><td>Water Consumed (m\u00b3):</td><td>{m3:,}</td></tr>
        <tr class='highlight'><td>Total Due (LKR):</td><td>{money(total)}</td></tr></table></div>
    </div>
    <table class='lines'><tr><th>Meter</th><th class='n'>Previous</th><th class='n'>Present</th><th class='n'>Consumption (m\u00b3)</th></tr>
      <tr><td>WM-{escape(f.water_account[-6:])}</td><td class='n'>{meter_prev:,}</td><td class='n'>{meter_prev + m3:,}</td><td class='n'>{m3:,}</td></tr></table>
    <table class='lines'><tr><th>Description</th><th class='n'>Quantity</th><th class='n'>Rate (LKR)</th><th class='n'>Amount (LKR)</th></tr>
      {rows}
      <tr><td>Service charge</td><td class='n'>1</td><td class='n'>{money(service)}</td><td class='n'>{money(service)}</td></tr>
      <tr><td>Drainage charge</td><td class='n'>{m3:,} m\u00b3</td><td class='n'>12.00</td><td class='n'>{money(drainage)}</td></tr>
      <tr class='total'><td colspan='3'>Total Due</td><td class='n'>{money(total)}</td></tr></table>
    {_history(history, ink, "m\u00b3")}
    <div class='notes'>Average daily consumption this period: {m3 / m.last_day.day:.1f} m\u00b3. Report leaks and
      meter faults to the hotline. Disconnection notices are issued for arrears exceeding two billing months.</div>
    """
    gt = {
        "utility_kind": "water",
        "billing_period": m.period,
        "consumption_value": m3,
        "consumption_unit": "m3",
        "account_holder": f.name,
    }
    return _wrap(body, ink), gt
