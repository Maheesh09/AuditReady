"""Narrative documents (doc type policy_or_audit_report).

They answer questionnaire items HS-03, HS-04, EN-04, PO-02, PO-03, AU-01, AU-02.
Deliberately NO document describes a grievance or complaints mechanism: PO-01 must
produce "No evidence found" in the demo (Plan Section 2 and 11.1).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from html import escape

from .certificates import Page
from .common import SYNTHETIC_NOTICE, Factory, fmt_date

DOC_CSS = """
@page { size: A4; }
html, body { margin: 0; }
body { font-family: 'Times New Roman', 'Liberation Serif', Georgia, serif; font-size: 11pt; line-height: 1.45;
       color: #1a1a1a; padding: 0 20mm; }
h1 { font-family: Arial, 'Liberation Sans', sans-serif; font-size: 17pt; margin: 4mm 0 2mm; color: #1d3557; }
h2 { font-family: Arial, 'Liberation Sans', sans-serif; font-size: 12.5pt; margin: 6mm 0 2mm; color: #1d3557;
     border-bottom: 1px solid #c9d2de; padding-bottom: 1mm; break-after: avoid; }
h3 { font-size: 11pt; margin: 3mm 0 1mm; break-after: avoid; }
p { margin: 0 0 2.4mm; text-align: justify; }
ul, ol { margin: 0 0 2.4mm 6mm; padding-left: 4mm; }
li { margin-bottom: 1mm; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 4mm; font-size: 9.5pt; break-inside: avoid; }
th, td { border: 1px solid #8a96a8; padding: 4px 6px; text-align: left; vertical-align: top; }
th { background: #e8edf4; font-family: Arial, sans-serif; font-size: 8.8pt; }
td:first-child { white-space: nowrap; }
.control td { font-family: Arial, sans-serif; font-size: 8.8pt; }
.company { font-family: Arial, sans-serif; font-size: 9.5pt; color: #555; letter-spacing: .4px; }
.signoff { margin-top: 10mm; display: flex; gap: 20mm; font-size: 10pt; break-inside: avoid; }
.signoff div { border-top: 1px solid #333; padding-top: 2mm; width: 60mm; }
"""


@dataclass(frozen=True)
class Narrative:
    page: Page
    facts: list[str]


def _page(f: Factory, doc_no: str, title: str, body: str, font: str = "") -> Page:
    style = DOC_CSS + (f"body {{ font-family: {font}; }}" if font else "")
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>{style}</style></head><body>{body}</body></html>"
    header = (
        f"<div style='display:flex;justify-content:space-between;border-bottom:0.5px solid #999;padding-bottom:2px'>"
        f"<span>{escape(f.name)}</span><span>{escape(title)} &middot; {escape(doc_no)}</span></div>"
    )
    footer = (
        "<div style='display:flex;justify-content:space-between'>"
        "<span>Uncontrolled when printed</span>"
        "<span>Page <span class='pageNumber'></span> of <span class='totalPages'></span></span></div>"
        f"<div style='text-align:center;color:#9a9a9a;font-size:6.5pt;margin-top:2px'>{escape(SYNTHETIC_NOTICE)}</div>"
    )
    return Page(html, margin_mm=20, header_html=header, footer_html=footer)


def _control(doc_no: str, rev: str, effective: date, owner: str, approver: str) -> str:
    return (
        "<table class='control'><tr><th>Document No</th><th>Revision</th><th>Effective Date</th>"
        "<th>Document Owner</th><th>Approved By</th></tr>"
        f"<tr><td>{doc_no}</td><td>{rev}</td><td>{fmt_date(effective, 'slash')}</td>"
        f"<td>{escape(owner)}</td><td>{escape(approver)}</td></tr></table>"
    )


# --------------------------------------------------------------------------- HS-03, HS-04
def health_safety_manual(
    f: Factory, effective: date, last_drill: date, drill_people: int
) -> Narrative:
    doc_no = f"{f.key.upper()}-HS-001"
    body = f"""
    <div class='company'>{escape(f.name.upper())}</div>
    <h1>Occupational Health and Safety Manual</h1>
    {_control(doc_no, "04", effective, f.compliance_manager + " (Compliance Manager)", f.factory_manager + " (Factory Manager)")}
    <h2>1. Purpose and scope</h2>
    <p>This manual sets out how {escape(f.name)} protects the health and safety of every person working at its
    premises at {escape(", ".join(f.address))}. It applies to all permanent, temporary and contract workers,
    visitors and service providers, across all production floors, stores, the boiler house and the canteen.</p>
    <h2>2. Responsibilities</h2>
    <p>The Factory Manager holds overall responsibility for occupational health and safety. The Compliance Manager
    maintains this manual, keeps safety records and reports monthly to the management team. Line supervisors are
    responsible for the day-to-day safety of the workers in their lines, including the headcount during an evacuation.</p>
    <h2>3. Fire evacuation procedure</h2>
    <h3>3.1 Raising the alarm</h3>
    <p>Any person discovering a fire shall immediately operate the nearest manual call point and inform the security
    control room on extension 100. The fire alarm is a continuous electronic siren audible in all buildings. Sewing
    machines and irons shall be switched off at the line isolator before leaving, where it is safe to do so.</p>
    <h3>3.2 Evacuation</h3>
    <ol>
      <li>On hearing the alarm, all workers leave by the nearest marked exit, walking in single file without running
      and without stopping to collect personal belongings.</li>
      <li>Trained floor wardens, at a ratio of one warden for every 25 workers, guide their sections to the exits and
      check toilets, stores and fitting rooms before leaving.</li>
      <li>Workers proceed to the designated assembly points: <b>Assembly Point A</b> (main car park) for Building A
      and <b>Assembly Point B</b> (staff sports ground) for Building B.</li>
      <li>Line supervisors complete a headcount against the daily attendance sheet and report any missing person to
      the Chief Fire Warden within five minutes of arrival.</li>
      <li>No person re-enters a building until the Chief Fire Warden declares it safe.</li>
    </ol>
    <p>The target is for all buildings to be fully evacuated within <b>three minutes</b> of the alarm. Workers with
    reduced mobility and pregnant workers are assigned a named buddy who assists them during evacuation.</p>
    <h2>4. Fire drills</h2>
    <p>A full-site fire drill is conducted <b>once every quarter</b>, at least one of which each year is unannounced.
    Drills alternate between day and night shifts so that every worker takes part at least twice a year. The Compliance
    Manager records the date, time, number of persons evacuated, evacuation time and any problems observed, and
    corrective actions are tracked to closure.</p>
    <table><tr><th>Most recent drill</th><th>Shift</th><th>Persons evacuated</th><th>Evacuation time</th><th>Observation</th></tr>
      <tr><td>{fmt_date(last_drill, "slash")}</td><td>Day (unannounced)</td><td>{drill_people}</td><td>2 min 48 s</td>
      <td>Exit 4 partially blocked by cartons; cleared and re-briefed stores team.</td></tr></table>
    <h2>5. Fire fighting equipment</h2>
    <p>Fire extinguishers are inspected monthly by the maintenance team and serviced annually by a registered agent;
    each unit carries an inspection tag. The hydrant system and fire pump are test-run weekly. At least 20% of the
    workforce on each shift is trained in the use of extinguishers, with refresher training every year.</p>
    <h2>6. Health and Safety Committee</h2>
    <p>The factory maintains a joint Health and Safety Committee of <b>twelve members</b>: six worker representatives
    elected by secret ballot every two years and six management representatives. The committee is chaired by the Factory
    Manager, and the Compliance Manager acts as secretary.</p>
    <ul>
      <li>The committee <b>meets monthly, on the first Wednesday of each month</b>. Extraordinary meetings are called
      within 48 hours after any serious accident or dangerous occurrence.</li>
      <li>A quorum is seven members, of whom at least three must be worker representatives.</li>
      <li>The committee reviews accident and near-miss reports, inspection findings, drill results and the status of
      open corrective actions, and carries out a walk-through inspection of one production area each month.</li>
      <li>Minutes are displayed on all notice boards in English, Sinhala and Tamil within five working days.</li>
    </ul>
    <h2>7. First aid and medical care</h2>
    <p>A first aid box is maintained on every production floor, with at least one certified first aider for every 50
    workers on each shift. A nurse is on duty in the medical room during all working hours, and a visiting doctor
    attends twice a week.</p>
    <div class='signoff'><div>{escape(f.factory_manager)}<br>Factory Manager</div><div>{escape(f.compliance_manager)}<br>Compliance Manager</div></div>
    """
    facts = [
        "Alarm raised via manual call point and security control room extension 100",
        "One trained floor warden per 25 workers",
        "Assembly Point A (main car park) for Building A, Assembly Point B (staff sports ground) for Building B",
        "Target full evacuation within three minutes",
        "Fire drills conducted quarterly, at least one unannounced per year, alternating day and night shifts",
        f"Most recent drill on {last_drill.isoformat()} evacuated {drill_people} persons in 2 min 48 s",
        "Health and Safety Committee has 12 members: 6 elected worker representatives and 6 management",
        "Committee chaired by the Factory Manager and meets monthly on the first Wednesday",
        "Committee minutes posted on notice boards in English, Sinhala and Tamil within five working days",
    ]
    return Narrative(_page(f, doc_no, "OHS Manual", body), facts)


# --------------------------------------------------------------------------- EN-04
def environmental_procedure(f: Factory, effective: date) -> Narrative:
    doc_no = f"{f.key.upper()}-ENV-003"
    body = f"""
    <div class='company'>{escape(f.name.upper())}</div>
    <h1>Wastewater Management Procedure</h1>
    {_control(doc_no, "02", effective, f.compliance_manager + " (Compliance Manager)", f.factory_manager + " (Factory Manager)")}
    <h2>1. Purpose</h2>
    <p>This procedure describes how wastewater generated at the factory is collected, treated and monitored so that
    discharges meet the tolerance limits set in the factory's Environmental Protection Licence
    (EPL No. {escape(f.epl_no)}) and the requirements of the export processing zone.</p>
    <h2>2. Sources of wastewater</h2>
    <p>The factory carries out cutting, sewing, finishing and packing only; there is no dyeing, printing or garment
    washing on site. Wastewater therefore consists of sanitary wastewater from toilets and washrooms, canteen kitchen
    wastewater and minor floor-cleaning water. Average generation is approximately 85 m&sup3; per day.</p>
    <h2>3. Treatment process</h2>
    <p>All wastewater is treated in the on-site sewage treatment plant (STP), an extended aeration activated sludge
    system with a design capacity of <b>120 m&sup3; per day</b>. Canteen wastewater first passes through a grease trap
    that is cleaned weekly.</p>
    <table><tr><th>Stage</th><th>Unit</th><th>Function</th></tr>
      <tr><td>1</td><td>Bar screen</td><td>Removes solids, plastics and fabric waste</td></tr>
      <tr><td>2</td><td>Equalisation tank</td><td>Balances flow and load over 24 hours</td></tr>
      <tr><td>3</td><td>Aeration tank</td><td>Biological treatment with diffused air (two blowers, duty and standby)</td></tr>
      <tr><td>4</td><td>Secondary clarifier</td><td>Settles biological sludge; part is returned to aeration</td></tr>
      <tr><td>5</td><td>Chlorine contact tank</td><td>Disinfection before discharge</td></tr>
      <tr><td>6</td><td>Sludge drying beds</td><td>Dewatering of excess sludge, disposed of by a licensed contractor</td></tr></table>
    <p>Treated effluent is discharged to the zone's central wastewater treatment plant through a metered connection.
    The STP operator records flow, dissolved oxygen, pH and chlorine residual daily in the STP log book.</p>
    <h2>4. Monitoring and testing</h2>
    <p>A sample of treated effluent is tested <b>monthly by an accredited external laboratory</b> for pH, BOD5, COD,
    total suspended solids, and oil and grease. Results are compared with the licence tolerance limits and filed by the
    Compliance Manager. Any exceedance is reported to the Factory Manager within 24 hours, the cause is investigated,
    and a re-test is done within seven days.</p>
    <h2>5. Records</h2>
    <ul><li>STP daily log book (retained for three years)</li><li>Monthly laboratory test reports</li>
    <li>Sludge disposal manifests</li><li>Grease trap cleaning checklist</li></ul>
    """
    facts = [
        "No dyeing, printing or washing on site; wastewater is sanitary, canteen and floor cleaning",
        "Average wastewater generation about 85 m3 per day",
        "Treated in on-site extended aeration STP with 120 m3 per day capacity",
        "Stages: bar screen, equalisation, aeration, secondary clarifier, chlorination, sludge drying beds",
        "Treated effluent discharged to the zone central wastewater treatment plant",
        "Effluent tested monthly by an accredited external laboratory for pH, BOD5, COD, TSS, oil and grease",
    ]
    return Narrative(_page(f, doc_no, "Wastewater Procedure", body), facts)


# --------------------------------------------------------------------------- PO-02, PO-03
def social_compliance_policy(f: Factory, effective: date) -> Narrative:
    doc_no = f"{f.key.upper()}-HR-010"
    body = f"""
    <div class='company'>{escape(f.name.upper())}</div>
    <h1>Social Compliance Policy: Child Labour and Forced Labour</h1>
    {_control(doc_no, "03", effective, f.hr_manager + " (HR Manager)", f.managing_director + " (Managing Director)")}
    <h2>1. Policy statement</h2>
    <p>{escape(f.name)} does not use or support child labour or any form of forced, bonded or involuntary labour.
    This policy applies to all workers employed directly by the company and to workers supplied by any labour agency
    or contractor working on our premises.</p>
    <h2>2. Child labour and young workers</h2>
    <h3>2.1 Minimum age</h3>
    <p>The minimum age for employment in any role at the factory is <b>18 years</b>. This is higher than the legal
    minimum and applies equally to apprentices, trainees and agency workers.</p>
    <h3>2.2 Age verification</h3>
    <ol>
      <li>Every applicant presents an original National Identity Card (NIC) at recruitment. The HR officer checks the
      date of birth encoded in the NIC number against the date of birth on the card.</li>
      <li>The birth certificate is requested as a second document and compared with the NIC.</li>
      <li>Where documents are doubtful, the applicant is not employed until age is confirmed by the relevant
      Divisional Secretariat.</li>
      <li>A photocopy of the verified NIC is kept on the personnel file; the original is always returned to the
      applicant on the same day.</li>
      <li>HR conducts an internal audit of 10% of new personnel files each quarter to confirm that age verification
      was completed.</li>
    </ol>
    <h3>2.3 Remediation</h3>
    <p>If a person under 18 is ever found working on the premises, they are removed from work immediately, paid their
    full wages to date, and supported to return to education or vocational training, with a monthly stipend until they
    reach the minimum age, at which time they are offered employment.</p>
    <h2>3. Forced labour and freedom of movement</h2>
    <ul>
      <li><b>No retention of documents.</b> The company never keeps original identity cards, passports, certificates
      or any other personal documents.</li>
      <li><b>No recruitment fees.</b> Workers pay no fee or deposit to the company or to any agent for recruitment.
      Any fee found to have been charged is reimbursed in full.</li>
      <li><b>Freedom to resign.</b> Workers may leave employment by giving the notice stated in their contract, and
      final wages are paid within the statutory period. No penalty or deduction is applied for resignation.</li>
      <li><b>Freedom of movement.</b> Workers may use toilets, drinking water and rest areas at any time without
      permission. Gates are not locked during working hours, and workers are free to leave the premises after their
      shift.</li>
      <li><b>Voluntary overtime.</b> Overtime is voluntary. Each worker signs a monthly overtime consent form, and
      refusal of overtime does not lead to any penalty or loss of benefits.</li>
      <li><b>No wage deductions as punishment.</b> Deductions are limited to those permitted by law.</li>
    </ul>
    <h2>4. Responsibilities and review</h2>
    <p>The HR Manager is responsible for implementing this policy and for training all supervisors on it annually.
    Labour agencies must sign an undertaking to comply with this policy before supplying any worker. The policy is
    reviewed every year by the Managing Director.</p>
    <div class='signoff'><div>{escape(f.managing_director)}<br>Managing Director</div><div>{escape(f.hr_manager)}<br>HR Manager</div></div>
    """
    facts = [
        "Minimum age for employment is 18 years, including apprentices and agency workers",
        "Age verified with original NIC plus birth certificate; doubtful cases confirmed with Divisional Secretariat",
        "Original NIC returned the same day; only a photocopy is kept",
        "Quarterly internal audit of 10% of new personnel files",
        "Remediation: removal, full wages, support for education with monthly stipend",
        "No retention of original documents, no recruitment fees, freedom to resign with contractual notice",
        "Free access to toilets and water, gates not locked, overtime voluntary with monthly signed consent",
    ]
    return Narrative(_page(f, doc_no, "Social Compliance Policy", body), facts)


# --------------------------------------------------------------------------- AU-01, AU-02
def social_audit_report(f: Factory, audit_start: date, report_date: date) -> Narrative:
    doc_no = "VSA-26-0519"
    audit_end = date.fromordinal(audit_start.toordinal() + 1)
    body = f"""
    <div class='company'>VERITRUST SOCIAL AUDITS (PVT) LTD &middot; INDEPENDENT THIRD-PARTY ASSESSMENT</div>
    <h1>Social Compliance Audit Report &mdash; Summary</h1>
    <table><tr><th>Site audited</th><td>{escape(f.name)}, {escape(", ".join(f.address))}</td></tr>
      <tr><th>Audit type</th><td>Full initial audit, semi-announced (two-week window)</td></tr>
      <tr><th>Audit scope</th><td>Four pillars: labour standards, health and safety, environment, business ethics</td></tr>
      <tr><th>Audit dates</th><td>{fmt_date(audit_start, "long")} to {fmt_date(audit_end, "long")}</td></tr>
      <tr><th>Audit man-days</th><td>3 (two auditors)</td></tr>
      <tr><th>Workers on site</th><td>{f.workers} (interviewed: 28, of which 12 in group interviews)</td></tr>
      <tr><th>Report reference</th><td>{doc_no}, issued {fmt_date(report_date, "long")}</td></tr></table>
    <h2>1. Overall result</h2>
    <p>The audit found <b>no critical and no major non-conformities</b>. <b>Four minor non-conformities</b> and one
    observation were raised. The site is rated <b>&ldquo;Approved &mdash; minor improvements required&rdquo;</b>, with a
    desktop review of corrective action evidence required within 90 days of the audit.</p>
    <table><tr><th>Area</th><th>Critical</th><th>Major</th><th>Minor</th><th>Observation</th></tr>
      <tr><td>Labour standards</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
      <tr><td>Health and safety</td><td>0</td><td>0</td><td>2</td><td>1</td></tr>
      <tr><td>Environment</td><td>0</td><td>0</td><td>1</td><td>0</td></tr>
      <tr><td>Business ethics</td><td>0</td><td>0</td><td>0</td><td>0</td></tr></table>
    <h2>2. Good practices noted</h2>
    <ul><li>Wages for the sampled months were paid on time, by bank transfer, and above the national minimum wage.</li>
      <li>Fire drill records were complete, including night-shift drills.</li>
      <li>Age verification records were complete for all 40 personnel files sampled.</li></ul>
    <h2>3. Corrective action plan</h2>
    <table><tr><th>No.</th><th>Finding</th><th>Severity</th><th>Corrective action agreed</th><th>Due date</th><th>Status</th></tr>
      <tr><td>NC-01</td><td>Monthly inspection tags missing on 4 fire extinguishers in Building B.</td><td>Minor</td>
        <td>Tag and inspect all units; add tag check to monthly checklist.</td><td>{fmt_date(date(2026, 6, 15), "slash")}</td><td>Closed {fmt_date(date(2026, 6, 5), "slash")}</td></tr>
      <tr><td>NC-02</td><td>First aid box in cutting section missing burn dressings and eye wash.</td><td>Minor</td>
        <td>Restock; assign weekly checks to section first aider.</td><td>{fmt_date(date(2026, 6, 15), "slash")}</td><td>Closed {fmt_date(date(2026, 5, 28), "slash")}</td></tr>
      <tr><td>NC-03</td><td>Overtime consent forms not signed by 7 of 40 sampled workers for April 2026.</td><td>Minor</td>
        <td>Re-brief supervisors; HR to reconcile consent forms against overtime register monthly.</td><td>{fmt_date(date(2026, 11, 30), "slash")}</td><td>Open</td></tr>
      <tr><td>NC-04</td><td>Chemical store (machine oils, spot-cleaning solvent) lacks secondary containment.</td><td>Minor</td>
        <td>Install bunded pallets and spill kit; update chemical inventory.</td><td>{fmt_date(date(2026, 10, 31), "slash")}</td><td>Open</td></tr>
      <tr><td>OB-01</td><td>Some aisle markings faded in Building A sewing floor.</td><td>Observation</td>
        <td>Repaint during next maintenance shutdown.</td><td>&ndash;</td><td>Open</td></tr></table>
    <h2>4. Auditor declaration</h2>
    <p>This report reflects the conditions observed during the audit days only. Findings are based on document review,
    site observation and worker and management interviews. The full report with evidence is held by the audit firm.</p>
    <div class='signoff'><div>R. K. Seneviratne<br>Lead Auditor</div><div>M. F. Rizna<br>Auditor</div></div>
    """
    facts = [
        f"Last third-party social audit held {audit_start.isoformat()} to {audit_end.isoformat()} by Veritrust Social Audits",
        "Outcome: no critical, no major, four minor non-conformities and one observation",
        "Rating: Approved - minor improvements required",
        "NC-01 and NC-02 closed",
        "Open: NC-03 overtime consent forms (due 2026-11-30) and NC-04 chemical store secondary containment (due 2026-10-31)",
        "Observation OB-01 (faded aisle markings) open",
    ]
    return Narrative(_page(f, doc_no, "Social Audit Summary", body), facts)
