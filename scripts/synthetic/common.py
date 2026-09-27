"""Shared types and helpers for synthetic document generation.

Everything here is fictional: organisations, people, IDs and account numbers are
generated. Every rendered page carries a small notice saying so.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

SYNTHETIC_NOTICE = (
    "Synthetic test document generated for AuditReady (IntelliCon '26). "
    "Fictional organisation and people. Not a genuine document."
)

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


@dataclass(frozen=True)
class Factory:
    key: str
    name: str
    address: tuple[str, ...]
    district: str
    workers: int
    reg_no: str
    reg_date: date
    epl_no: str
    elec_account: str
    water_account: str
    managing_director: str
    factory_manager: str
    hr_manager: str
    compliance_manager: str


@dataclass(frozen=True)
class Month:
    year: int
    month: int

    @property
    def period(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"

    @property
    def label(self) -> str:
        return f"{MONTHS[self.month - 1]} {self.year}"

    @property
    def first_day(self) -> date:
        return date(self.year, self.month, 1)

    @property
    def last_day(self) -> date:
        nxt = date(self.year + (self.month == 12), self.month % 12 + 1, 1)
        return nxt - timedelta(days=1)


def last_full_months(demo_date: date, n: int = 12) -> list[Month]:
    """The n full calendar months before the demo month, oldest first."""
    y, m = demo_date.year, demo_date.month
    out: list[Month] = []
    for _ in range(n):
        m -= 1
        if m == 0:
            y, m = y - 1, 12
        out.append(Month(y, m))
    return list(reversed(out))


def fmt_date(d: date, style: str) -> str:
    """Date styles seen on Sri Lankan documents. Ambiguous ones are DD/MM (Plan Section 9)."""
    if style == "slash":
        return d.strftime("%d/%m/%Y")
    if style == "dot":
        return d.strftime("%d.%m.%Y")
    if style == "mon":
        return d.strftime("%d-%b-%Y")
    if style == "long":
        return f"{d.day} {MONTHS[d.month - 1]} {d.year}"
    raise ValueError(style)


def money(v: float) -> str:
    return f"{v:,.2f}"


@dataclass
class DocRecord:
    """One generated document plus its ground truth (Plan Section 14.2)."""

    rel_path: str  # relative to data/synthetic
    doc_type: str
    factory: str
    sensitivity: str  # standard | sensitive
    quality: str  # clean | scanned | photo | stamped | spreadsheet
    fields: dict[str, Any] = field(default_factory=dict)
    series: list[dict[str, Any]] = field(default_factory=list)
    narrative_facts: list[str] = field(default_factory=list)
    planted_issues: list[str] = field(default_factory=list)
    demo_upload_order: int | None = None

    def ground_truth(self) -> dict[str, Any]:
        gt: dict[str, Any] = {
            "document": self.rel_path,
            "doc_type": self.doc_type,
            "factory": self.factory,
            "sensitivity": self.sensitivity,
            "quality": self.quality,
        }
        if self.fields:
            gt["fields"] = self.fields
        if self.series:
            gt["series"] = self.series
        if self.narrative_facts:
            gt["narrative_facts"] = self.narrative_facts
        gt["planted_issues"] = self.planted_issues
        gt["checked_by"] = None  # second person fills this in (Plan 14.2)
        return gt


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n", "utf-8")
