"""Builds every synthetic document set (Plan Section 14.1).

- lotus_apparel/  main demo factory, 34 documents, with the planted problems from Plan Section 2
- kandy_knits/    second factory, 8 documents, proves data separation
- stress/         20 certificate/bill variants: 5 clean, 5 scanned, 5 phone photo, 5 stamped
"""

from __future__ import annotations

import random
import shutil
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser

from . import bills, certificates, policies, spreadsheets
from .certificates import Page
from .common import DocRecord, Factory, fmt_date, last_full_months, write_json
from .render import html_to_pdf, images_to_pdf, office_scan, pdf_to_images, phone_photo

LOTUS = Factory(
    key="la",
    name="Lotus Apparel (Pvt) Ltd",
    address=("No. 42, Zone Access Road", "Biyagama Export Processing Zone", "Walgama, Malwana"),
    district="Gampaha",
    workers=408,
    reg_no="PV 00214573",
    reg_date=date(2012, 3, 23),
    epl_no="BOI/ENV/EPL/2025/0871",
    elec_account="4102-338-716",
    water_account="10-2291-40-512377",
    managing_director="Rohan Weerakkody",
    factory_manager="Chandana Liyanage",
    hr_manager="Shiromi Gunasekara",
    compliance_manager="Dilhani Rodrigo",
)
KANDY = Factory(
    key="kk",
    name="Kandy Knits (Pvt) Ltd",
    address=("Lot 7, Industrial Estate Road", "Pallekele Industrial Zone", "Kundasale"),
    district="Kandy",
    workers=150,
    reg_no="PV 00301188",
    reg_date=date(2016, 8, 9),
    epl_no="CP/EPL/IND/2024/0335",
    elec_account="7730-104-229",
    water_account="22-4410-07-118832",
    managing_director="Asoka Jayawardena",
    factory_manager="Mahesh Ratnayake",
    hr_manager="Nilanthi Herath",
    compliance_manager="Fathima Nazeer",
)

FIRE_BODY = "Metropolitan Fire & Rescue Service"
BOILER_BODY = "Institute of Pressure Vessel Inspection (Ceylon)"
CERT_BODY = "Lankacert Assurance Services (Pvt) Ltd"
REGISTRY = "Registry of Companies"


class Builder:
    def __init__(self, browser: Browser, data_root: Path, demo_date: date, seed: int) -> None:
        self.browser = browser
        self.synthetic = data_root / "synthetic"
        self.truth = data_root / "ground_truth"
        self.demo_date = demo_date
        self.rng = random.Random(seed)
        self.records: list[DocRecord] = []
        self.months = last_full_months(demo_date, 12)

    # ------------------------------------------------------------------ output helpers
    def _pdf(self, page: Page, rel: str) -> Path:
        out = self.synthetic / rel
        html_to_pdf(self.browser, page, out)
        return out

    def _photo(self, page: Page, rel: str, blur: float, max_rot: float) -> None:
        tmp = self.synthetic / "_tmp.pdf"
        html_to_pdf(self.browser, page, tmp)
        img = pdf_to_images(tmp, dpi=170)[0]
        out = self.synthetic / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        phone_photo(img, self.rng, blur=blur, max_rot=max_rot).save(out, "JPEG", quality=80)
        tmp.unlink()

    def _scan(self, page: Page, rel: str, skew: float = 1.0) -> None:
        tmp = self.synthetic / "_tmp.pdf"
        html_to_pdf(self.browser, page, tmp)
        pages = [office_scan(p, self.rng, skew) for p in pdf_to_images(tmp, dpi=150)]
        images_to_pdf(pages, self.synthetic / rel, dpi=150)
        tmp.unlink()

    def _emit(self, page: Page, rel: str, quality: str, **kw: float) -> None:
        if quality == "photo":
            self._photo(page, rel, kw.get("blur", 1.0), kw.get("max_rot", 3.0))
        elif quality == "scanned":
            self._scan(page, rel, kw.get("skew", 1.0))
        else:
            self._pdf(page, rel)

    def add(self, rec: DocRecord) -> None:
        self.records.append(rec)
        write_json(self.truth / f"{rec.rel_path}.json", rec.ground_truth())

    # ------------------------------------------------------------------ certificate data
    def fire_data(self, f: Factory, number: str, issue: date, division: str) -> dict[str, str]:
        return {
            "certificate_number": number,
            "premises_name": f.name,
            "address": ", ".join(f.address),
            "occupancy": "Industrial - Garment Manufacturing (Group F)",
            "max_occupancy": f"{self.rng.choice([420, 560, 680, 750])} persons",
            "inspection_date": fmt_date(issue - timedelta(days=7), "slash"),
            "issue_date": fmt_date(issue, "slash"),
            "expiry_date": fmt_date(
                issue.replace(year=issue.year + 1) - timedelta(days=1), "slash"
            ),
            "issuing_authority": FIRE_BODY,
            "division": division,
            "officer": self.rng.choice(
                ["S. A. Wickramaratne", "K. P. Munasinghe", "A. M. Rasheed"]
            ),
            "ref": f"MFRS/{division[:2].upper()}/FP/{issue.year}/{self.rng.randint(100, 999):04d}",
        }

    def boiler_data(
        self, f: Factory, number: str, equipment: str, issue: date, expiry: date
    ) -> dict[str, str]:
        return {
            "certificate_number": number,
            "owner": f.name,
            "location": f"Boiler House, {f.address[1]}",
            "equipment_id": equipment,
            "boiler_type": "Horizontal fire-tube (3-pass), oil fired, 2.5 t/h",
            "maker": self.rng.choice(
                ["Thermax Ltd, 2014", "Cochran Ltd, 2016", "Babcock Wanson, 2012"]
            ),
            "pressure": "10.5 bar (g)",
            "test_pressure": "15.8 bar (g)",
            "inspection_date": fmt_date(issue - timedelta(days=5), "dot"),
            "issue_date": fmt_date(issue, "dot"),
            "expiry_date": fmt_date(expiry, "dot"),
            "issuing_authority": BOILER_BODY,
            "officer": self.rng.choice(["Eng. H. D. Samarasekara", "Eng. T. Kanagaratnam"]),
            "ref": f"IPVI/BI/{issue.year}/{self.rng.randint(1000, 9999)}",
        }

    def iso_data(
        self, f: Factory, number: str, issue: date, expiry_printed: date, initial: date
    ) -> dict[str, str]:
        return {
            "certification_body": CERT_BODY,
            "company": f.name,
            "address": ", ".join(f.address),
            "standard_name": "ISO 14001:2015",
            "certificate_number": number,
            "scope": "Cutting, sewing, finishing and packing of woven and knitted garments for export.",
            "initial_date": fmt_date(initial, "mon"),
            "issue_date": fmt_date(issue, "mon"),
            "expiry_date": fmt_date(expiry_printed, "mon"),
            "officer": "Priyantha de Mel",
        }

    def reg_data(self, f: Factory) -> dict[str, str]:
        return {
            "registry": REGISTRY,
            "company_name": f.name,
            "registration_number": f.reg_no,
            "registration_date": fmt_date(f.reg_date, "slash"),
            "address": ", ".join(f.address),
            "given_on": fmt_date(f.reg_date, "long"),
            "officer": "W. M. S. Wijesundara",
        }

    # ------------------------------------------------------------------ Lotus Apparel
    def build_lotus(self) -> None:
        f, base, rng = LOTUS, "lotus_apparel", self.rng
        order = iter(range(1, 9))

        # 1. Fire certificate: phone photo, blurry and tilted (planted: low-confidence date)
        issue = date(2026, 1, 11)
        d = self.fire_data(f, "FS-29183", issue, "Gampaha District Division")
        self._emit(
            certificates.fire_safety_certificate(d, rng),
            f"{base}/fire_certificate_2026_photo.jpg",
            "photo",
            blur=2.1,
            max_rot=4.5,
        )
        self.add(
            DocRecord(
                f"{base}/fire_certificate_2026_photo.jpg",
                "fire_safety_certificate",
                f.key,
                "standard",
                "photo",
                fields={
                    "certificate_number": "FS-29183",
                    "issuing_authority": FIRE_BODY,
                    "issue_date": issue.isoformat(),
                    "expiry_date": "2027-01-10",
                    "premises_name": f.name,
                },
                planted_issues=[
                    "Blurry, tilted phone photo: expiry date should read at low confidence and go to review"
                ],
                demo_upload_order=next(order),
            )
        )

        # 2. Boiler certificate: office scan, expires 23 days after demo day (planted)
        expiry = self.demo_date + timedelta(days=23)
        b_issue = expiry.replace(year=expiry.year - 1) + timedelta(days=1)
        d = self.boiler_data(f, "BIC/2025/0417", "BLR-LA-02", b_issue, expiry)
        self._emit(
            certificates.boiler_inspection_certificate(d, rng),
            f"{base}/boiler_inspection_certificate_scan.pdf",
            "scanned",
            skew=0.8,
        )
        self.add(
            DocRecord(
                f"{base}/boiler_inspection_certificate_scan.pdf",
                "boiler_inspection_certificate",
                f.key,
                "standard",
                "scanned",
                fields={
                    "certificate_number": "BIC/2025/0417",
                    "issue_date": b_issue.isoformat(),
                    "expiry_date": expiry.isoformat(),
                    "equipment_id": "BLR-LA-02",
                },
                planted_issues=[
                    f"Expires {expiry.isoformat()}, 23 days after demo day: R04 expiring soon"
                ],
                demo_upload_order=next(order),
            )
        )

        # 3. ISO 14001: expiry printed BEFORE issue date (planted typo 2024 instead of 2028)
        iso_issue = date(2025, 6, 15)
        d = self.iso_data(f, "LAS-EMS-14001-2381", iso_issue, date(2024, 6, 14), date(2019, 6, 15))
        self._emit(
            certificates.iso_certificate(d, rng), f"{base}/iso_14001_certificate.pdf", "clean"
        )
        self.add(
            DocRecord(
                f"{base}/iso_14001_certificate.pdf",
                "iso_certificate",
                f.key,
                "standard",
                "clean",
                fields={
                    "standard_name": "ISO 14001:2015",
                    "certificate_number": "LAS-EMS-14001-2381",
                    "certification_body": CERT_BODY,
                    "issue_date": "2025-06-15",
                    "expiry_date": "2024-06-14",
                },
                planted_issues=[
                    "Expiry date (2024-06-14) is before issue date: R01 must fail, Low tier"
                ],
                demo_upload_order=next(order),
            )
        )

        # 4. Business registration
        self._emit(
            certificates.business_registration(self.reg_data(f), rng),
            f"{base}/certificate_of_incorporation.pdf",
            "clean",
        )
        self.add(
            DocRecord(
                f"{base}/certificate_of_incorporation.pdf",
                "business_registration",
                f.key,
                "standard",
                "clean",
                fields={
                    "registration_number": f.reg_no,
                    "company_name": f.name,
                    "registration_date": f.reg_date.isoformat(),
                },
            )
        )

        # 5-6. Payroll (March missing, planted) and attendance
        workforce = spreadsheets.build_workforce(rng, 440, 12, "LA")
        self._payroll(
            f,
            base,
            workforce,
            {"2026-03"},
            next(order),
            ["March 2026 payroll register missing: R08 warning and missing-month gap"],
        )
        self._attendance(f, base, workforce)

        # 7-30. Utility bills, 12 electricity + 12 water
        elec = self._series(200_000, 0.05, seasonal={3: 1.08, 4: 1.1, 5: 1.06, 12: 0.9})
        water = self._series(2_850, 0.05, seasonal={4: 1.06, 12: 0.92})
        demo_elec = self._bills(f, base, elec, water)
        for r in self.records:
            if r.rel_path in demo_elec:
                r.demo_upload_order = next(order)
                write_json(self.truth / f"{r.rel_path}.json", r.ground_truth())

        # 31-34. Narrative documents (no grievance mechanism anywhere: PO-01 stays unanswered)
        n = policies.health_safety_manual(f, date(2026, 2, 1), date(2026, 8, 14), 612)
        self._narrative(n, f"{base}/ohs_manual_rev04.pdf", f.key, "clean", next(order))
        self._narrative(
            policies.environmental_procedure(f, date(2025, 9, 15)),
            f"{base}/wastewater_management_procedure.pdf",
            f.key,
            "clean",
        )
        self._narrative(
            policies.social_compliance_policy(f, date(2026, 1, 15)),
            f"{base}/social_compliance_policy_child_forced_labour.pdf",
            f.key,
            "clean",
        )
        self._narrative(
            policies.social_audit_report(f, date(2026, 5, 19), date(2026, 5, 29)),
            f"{base}/social_audit_report_may2026_scan.pdf",
            f.key,
            "scanned",
            next(order),
        )

    # ------------------------------------------------------------------ Kandy Knits
    def build_kandy(self) -> None:
        f, base, rng = KANDY, "kandy_knits", self.rng
        issue = date(2026, 4, 2)
        d = self.fire_data(f, "FS-31877", issue, "Central Province Division")
        self._emit(
            certificates.fire_safety_certificate(d, rng), f"{base}/fire_certificate.pdf", "clean"
        )
        self.add(
            DocRecord(
                f"{base}/fire_certificate.pdf",
                "fire_safety_certificate",
                f.key,
                "standard",
                "clean",
                fields={
                    "certificate_number": "FS-31877",
                    "issuing_authority": FIRE_BODY,
                    "issue_date": issue.isoformat(),
                    "expiry_date": (issue.replace(year=2027) - timedelta(days=1)).isoformat(),
                    "premises_name": f.name,
                },
            )
        )
        b_issue, b_exp = date(2026, 2, 20), date(2027, 2, 19)
        d = self.boiler_data(f, "BIC/2026/0088", "BLR-KK-01", b_issue, b_exp)
        self._emit(
            certificates.boiler_inspection_certificate(d, rng),
            f"{base}/boiler_certificate.pdf",
            "clean",
        )
        self.add(
            DocRecord(
                f"{base}/boiler_certificate.pdf",
                "boiler_inspection_certificate",
                f.key,
                "standard",
                "clean",
                fields={
                    "certificate_number": "BIC/2026/0088",
                    "issue_date": b_issue.isoformat(),
                    "expiry_date": b_exp.isoformat(),
                    "equipment_id": "BLR-KK-01",
                },
            )
        )
        d = self.iso_data(
            f, "LAS-EMS-14001-2610", date(2025, 11, 3), date(2028, 11, 2), date(2025, 11, 3)
        )
        self._emit(
            certificates.iso_certificate(d, rng), f"{base}/iso_14001_certificate.pdf", "clean"
        )
        self.add(
            DocRecord(
                f"{base}/iso_14001_certificate.pdf",
                "iso_certificate",
                f.key,
                "standard",
                "clean",
                fields={
                    "standard_name": "ISO 14001:2015",
                    "certificate_number": "LAS-EMS-14001-2610",
                    "certification_body": CERT_BODY,
                    "issue_date": "2025-11-03",
                    "expiry_date": "2028-11-02",
                },
            )
        )
        self._emit(
            certificates.business_registration(self.reg_data(f), rng),
            f"{base}/certificate_of_incorporation.pdf",
            "clean",
        )
        self.add(
            DocRecord(
                f"{base}/certificate_of_incorporation.pdf",
                "business_registration",
                f.key,
                "standard",
                "clean",
                fields={
                    "registration_number": f.reg_no,
                    "company_name": f.name,
                    "registration_date": f.reg_date.isoformat(),
                },
            )
        )
        workforce = spreadsheets.build_workforce(rng, 150, 12, "KK")
        self._payroll(f, base, workforce, set(), None, [])
        self._attendance(f, base, workforce)
        m = self.months[-1]
        page, gt = bills.electricity_bill(
            f,
            m,
            64_300,
            [bills.Reading(x, 60_000 + i * 400) for i, x in enumerate(self.months)],
            "EB-KK-" + m.period.replace("-", ""),
        )
        self._pdf(page, f"{base}/electricity_bill_{m.period}.pdf")
        self.add(
            DocRecord(
                f"{base}/electricity_bill_{m.period}.pdf",
                "utility_bill",
                f.key,
                "standard",
                "clean",
                fields=gt,
            )
        )
        self._narrative(
            policies.health_safety_manual(f, date(2026, 3, 1), date(2026, 7, 22), 141),
            f"{base}/ohs_manual.pdf",
            f.key,
            "clean",
        )

    # ------------------------------------------------------------------ stress set
    def build_stress(self) -> None:
        rng = self.rng
        names = [
            "Ceylon Stitchcraft (Pvt) Ltd",
            "Horizon Knitwear Lanka (Pvt) Ltd",
            "Palmyra Garments (Pvt) Ltd",
            "Blue Lagoon Apparel (Pvt) Ltd",
            "Mahaweli Fashion Works (Pvt) Ltd",
        ]
        towns = [
            ("Katunayake Export Processing Zone", "Katunayake"),
            ("Koggala Export Processing Zone", "Koggala"),
            ("Horana Industrial Park", "Horana"),
            ("Seethawaka Industrial Park", "Avissawella"),
            ("Mirigama Export Processing Zone", "Mirigama"),
        ]
        qualities = ["clean", "scanned", "photo", "stamped"]
        templates: list[
            Callable[[Factory, str, dict[str, str] | None], tuple[Page, str, dict[str, Any]]]
        ] = [
            self._stress_fire,
            self._stress_boiler,
            self._stress_iso,
            self._stress_reg,
            self._stress_bill,
        ]
        for ti, make in enumerate(templates):
            for qi, quality in enumerate(qualities):
                i = ti * 4 + qi
                zone, town = towns[(ti + qi) % 5]
                f = Factory(
                    key=f"st{i:02d}",
                    name=names[(ti + 2 * qi) % 5],
                    address=(f"No. {rng.randint(3, 120)}, Block {rng.choice('ABCDE')}", zone, town),
                    district=town,
                    workers=0,
                    reg_no=f"PV {rng.randint(10**7, 10**8 - 1):08d}",
                    reg_date=date(rng.randint(2004, 2020), rng.randint(1, 12), rng.randint(1, 28)),
                    epl_no="-",
                    elec_account=f"{rng.randint(1000, 9999)}-{rng.randint(100, 999)}-{rng.randint(100, 999)}",
                    water_account="-",
                    managing_director="-",
                    factory_manager="-",
                    hr_manager="-",
                    compliance_manager="-",
                )
                overlay = None
                if quality == "stamped":
                    overlay = {
                        "kind": rng.choice(["stamp", "scribble"]),
                        "text": fmt_date(
                            self.demo_date - timedelta(days=rng.randint(20, 200)), "mon"
                        ).upper(),
                    }
                page, doc_type, fields = make(f, str(i), overlay)
                ext = "jpg" if quality == "photo" else "pdf"
                rel = f"stress/{i:02d}_{doc_type}_{quality}.{ext}"
                self._emit(
                    page,
                    rel,
                    quality,
                    blur=rng.uniform(0.7, 1.5),
                    max_rot=rng.uniform(1.5, 5),
                    skew=rng.uniform(0.4, 1.6),
                )
                issues = (
                    [f"{overlay['kind']} drawn over field '{overlay['field']}'"] if overlay else []
                )
                self.add(
                    DocRecord(
                        rel,
                        doc_type,
                        f.key,
                        "standard",
                        quality,
                        fields=fields,
                        planted_issues=issues,
                    )
                )

    def _rand_issue(self) -> date:
        return self.demo_date - timedelta(days=self.rng.randint(30, 300))

    def _stress_fire(
        self, f: Factory, i: str, overlay: dict[str, str] | None
    ) -> tuple[Page, str, dict[str, Any]]:
        issue = self._rand_issue()
        num = f"FS-{self.rng.randint(20000, 39999)}"
        d = self.fire_data(f, num, issue, f"{f.district} Division")
        if overlay:
            overlay["field"] = "expiry_date"
        exp = issue.replace(year=issue.year + 1) - timedelta(days=1)
        return (
            certificates.fire_safety_certificate(d, self.rng, overlay),
            "fire_safety_certificate",
            {
                "certificate_number": num,
                "issuing_authority": FIRE_BODY,
                "issue_date": issue.isoformat(),
                "expiry_date": exp.isoformat(),
                "premises_name": f.name,
            },
        )

    def _stress_boiler(
        self, f: Factory, i: str, overlay: dict[str, str] | None
    ) -> tuple[Page, str, dict[str, Any]]:
        issue = self._rand_issue()
        exp = issue.replace(year=issue.year + 1) - timedelta(days=1)
        num, eq = (
            f"BIC/{issue.year}/{self.rng.randint(100, 999):04d}",
            f"BLR-{self.rng.randint(10, 99)}-{self.rng.randint(1, 4):02d}",
        )
        if overlay:
            overlay["field"] = "certificate_number"
        return (
            certificates.boiler_inspection_certificate(
                self.boiler_data(f, num, eq, issue, exp), self.rng, overlay
            ),
            "boiler_inspection_certificate",
            {
                "certificate_number": num,
                "issue_date": issue.isoformat(),
                "expiry_date": exp.isoformat(),
                "equipment_id": eq,
            },
        )

    def _stress_iso(
        self, f: Factory, i: str, overlay: dict[str, str] | None
    ) -> tuple[Page, str, dict[str, Any]]:
        issue = self._rand_issue()
        exp = issue.replace(year=issue.year + 3) - timedelta(days=1)
        num = f"LAS-EMS-14001-{self.rng.randint(1000, 9999)}"
        if overlay:
            overlay["field"] = "issue_date"
        return (
            certificates.iso_certificate(
                self.iso_data(f, num, issue, exp, issue), self.rng, overlay
            ),
            "iso_certificate",
            {
                "standard_name": "ISO 14001:2015",
                "certificate_number": num,
                "certification_body": CERT_BODY,
                "issue_date": issue.isoformat(),
                "expiry_date": exp.isoformat(),
            },
        )

    def _stress_reg(
        self, f: Factory, i: str, overlay: dict[str, str] | None
    ) -> tuple[Page, str, dict[str, Any]]:
        if overlay:
            overlay["field"] = "registration_date"
        return (
            certificates.business_registration(self.reg_data(f), self.rng, overlay),
            "business_registration",
            {
                "registration_number": f.reg_no,
                "company_name": f.name,
                "registration_date": f.reg_date.isoformat(),
            },
        )

    def _stress_bill(
        self, f: Factory, i: str, overlay: dict[str, str] | None
    ) -> tuple[Page, str, dict[str, Any]]:
        m = self.months[self.rng.randint(0, 11)]
        kwh = self.rng.randint(40_000, 260_000)
        hist = [bills.Reading(x, int(kwh * self.rng.uniform(0.85, 1.1))) for x in self.months]
        if overlay:
            overlay["field"] = "consumption_value"
        page, gt = bills.electricity_bill(
            f, m, kwh, hist, f"EB-{i}-{m.period.replace('-', '')}", overlay
        )
        return page, "utility_bill", gt

    # ------------------------------------------------------------------ shared pieces
    def _series(self, base: float, noise: float, seasonal: dict[int, float]) -> list[int]:
        return [
            int(base * seasonal.get(m.month, 1.0) * self.rng.uniform(1 - noise, 1 + noise))
            for m in self.months
        ]

    def _bills(self, f: Factory, base: str, elec: list[int], water: list[int]) -> set[str]:
        demo: set[str] = set()
        for i, m in enumerate(self.months):
            hist_e = [
                bills.Reading(x, v)
                for x, v in zip(self.months[: i + 1], elec[: i + 1], strict=True)
            ][-12:]
            page, gt = bills.electricity_bill(
                f,
                m,
                elec[i],
                hist_e,
                f"EB-{m.period.replace('-', '')}-{self.rng.randint(10000, 99999)}",
            )
            rel = f"{base}/electricity_bill_{m.period}.pdf"
            self._pdf(page, rel)
            self.add(DocRecord(rel, "utility_bill", f.key, "standard", "clean", fields=gt))
            hist_w = [
                bills.Reading(x, v)
                for x, v in zip(self.months[: i + 1], water[: i + 1], strict=True)
            ][-12:]
            page, gt = bills.water_bill(
                f, m, water[i], hist_w, f"W{self.rng.randint(10**7, 10**8 - 1)}"
            )
            rel_w = f"{base}/water_bill_{m.period}.pdf"
            self._pdf(page, rel_w)
            self.add(DocRecord(rel_w, "utility_bill", f.key, "standard", "clean", fields=gt))
            if i == len(self.months) - 1:
                demo |= {rel, rel_w}
        return demo

    def _payroll(
        self,
        f: Factory,
        base: str,
        workforce: list[spreadsheets.Worker],
        skip: set[str],
        order: int | None,
        issues: list[str],
    ) -> None:
        wb, series = spreadsheets.payroll_workbook(
            f, workforce, self.months, skip, self.rng, self.demo_date - timedelta(days=10)
        )
        rel = f"{base}/payroll_register_{self.months[0].period}_to_{self.months[-1].period}.xlsx"
        (self.synthetic / rel).parent.mkdir(parents=True, exist_ok=True)
        wb.save(self.synthetic / rel)
        self.add(
            DocRecord(
                rel,
                "payroll_summary",
                f.key,
                "sensitive",
                "spreadsheet",
                series=series,
                planted_issues=issues,
                demo_upload_order=order,
            )
        )

    def _attendance(self, f: Factory, base: str, workforce: list[spreadsheets.Worker]) -> None:
        wb, series = spreadsheets.attendance_workbook(
            f, workforce, self.months, self.rng, self.demo_date - timedelta(days=10)
        )
        rel = f"{base}/attendance_register_{self.months[0].period}_to_{self.months[-1].period}.xlsx"
        wb.save(self.synthetic / rel)
        self.add(
            DocRecord(rel, "attendance_register", f.key, "sensitive", "spreadsheet", series=series)
        )

    def _narrative(
        self, n: policies.Narrative, rel: str, factory: str, quality: str, order: int | None = None
    ) -> None:
        self._emit(n.page, rel, quality, skew=0.7)
        self.add(
            DocRecord(
                rel,
                "policy_or_audit_report",
                factory,
                "standard",
                quality,
                narrative_facts=n.facts,
                demo_upload_order=order,
            )
        )

    # ------------------------------------------------------------------ entry
    def run(self) -> list[DocRecord]:
        for d in (self.synthetic, self.truth):
            for sub in ("lotus_apparel", "kandy_knits", "stress"):
                shutil.rmtree(d / sub, ignore_errors=True)
        self.build_lotus()
        self.build_kandy()
        self.build_stress()
        write_json(
            self.synthetic / "manifest.json",
            {
                "demo_date": self.demo_date.isoformat(),
                "months": [m.period for m in self.months],
                "documents": [
                    {
                        "path": r.rel_path,
                        "doc_type": r.doc_type,
                        "factory": r.factory,
                        "sensitivity": r.sensitivity,
                        "quality": r.quality,
                        "demo_upload_order": r.demo_upload_order,
                        "planted_issues": r.planted_issues,
                    }
                    for r in self.records
                ],
            },
        )
        return self.records
