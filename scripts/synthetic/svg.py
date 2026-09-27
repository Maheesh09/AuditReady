"""Original vector artwork: rubber-stamp seals, signatures, emblems, guilloche borders.

All designs are generated here; no real logos or insignia are reproduced.
"""

from __future__ import annotations

import math
import random
import zlib
from html import escape


def seal(
    outer: str, center: str, color: str = "#2b3f8f", size: int = 150, rotate: float = -8
) -> str:
    """A round rubber-stamp seal with curved text, like an official office stamp."""
    r = size / 2
    txt_r = r - 17
    uid = f"s{zlib.crc32(f'{outer}|{center}|{size}'.encode())}"  # deterministic id
    lines = center.split("\n")
    center_svg = "".join(
        f'<text x="{r}" y="{r + (i - (len(lines) - 1) / 2) * 13 + 4}" text-anchor="middle" '
        f'font-size="11" font-weight="700" fill="{color}">{escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    return (
        f'<svg class="seal" width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
        f'style="transform:rotate({rotate}deg);opacity:.82;mix-blend-mode:multiply" xmlns="http://www.w3.org/2000/svg">'
        f'<defs><path id="{uid}" d="M {r},{r} m -{txt_r},0 a {txt_r},{txt_r} 0 1,1 {2 * txt_r},0 '
        f'a {txt_r},{txt_r} 0 1,1 -{2 * txt_r},0"/></defs>'
        f'<circle cx="{r}" cy="{r}" r="{r - 3}" fill="none" stroke="{color}" stroke-width="3"/>'
        f'<circle cx="{r}" cy="{r}" r="{r - 27}" fill="none" stroke="{color}" stroke-width="1.5"/>'
        f'<text font-family="Arial, sans-serif" font-size="11.5" font-weight="700" fill="{color}">'
        f'<textPath href="#{uid}" textLength="{2 * math.pi * txt_r * 0.96:.1f}" '
        f'lengthAdjust="spacing">{escape(outer)}</textPath></text>'
        f'<g font-family="Arial, sans-serif">{center_svg}</g></svg>'
    )


def rect_stamp(lines: list[str], color: str = "#b3261e", rotate: float = -12) -> str:
    """Rectangular 'RECEIVED' style stamp, used to obscure fields in the stress set."""
    h = 22 + 18 * len(lines)
    body = "".join(
        f'<text x="110" y="{30 + i * 18}" text-anchor="middle" font-size="{15 if i == 0 else 12}" '
        f'font-weight="700" fill="{color}">{escape(t)}</text>'
        for i, t in enumerate(lines)
    )
    return (
        f'<svg class="rstamp" width="220" height="{h}" viewBox="0 0 220 {h}" '
        f'style="transform:rotate({rotate}deg);mix-blend-mode:multiply;opacity:.85" '
        f'xmlns="http://www.w3.org/2000/svg"><rect x="3" y="3" width="214" height="{h - 6}" rx="6" fill="none" stroke="{color}" '
        f'stroke-width="3"/><g font-family="Arial, sans-serif" opacity=".9">{body}</g></svg>'
    )


def signature(rng: random.Random, width: int = 190, color: str = "#1b2a6b") -> str:
    """A believable handwritten flourish built from random cubic curves."""
    x, y = 8.0, 42.0
    d = f"M {x:.1f} {y:.1f}"
    for _ in range(rng.randint(5, 8)):
        nx = min(width - 10, x + rng.uniform(18, 34))
        ny = rng.uniform(18, 58)
        d += (
            f" C {x + rng.uniform(4, 16):.1f} {y - rng.uniform(-30, 30):.1f},"
            f" {nx - rng.uniform(4, 16):.1f} {ny + rng.uniform(-30, 30):.1f}, {nx:.1f} {ny:.1f}"
        )
        x, y = nx, ny
    tail = f" M {rng.uniform(10, 40):.1f} {rng.uniform(55, 62):.1f} q {width * 0.4:.1f} {rng.uniform(-10, 6):.1f} {width * 0.75:.1f} {rng.uniform(-8, 4):.1f}"
    return (
        f'<svg class="sig" width="{width}" height="70" viewBox="0 0 {width} 70" '
        f'xmlns="http://www.w3.org/2000/svg"><path d="{d}{tail}" fill="none" stroke="{color}" '
        f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


def emblem(kind: str, color: str, size: int = 76) -> str:
    """Simple original emblems for the fictional issuing bodies."""
    c = size / 2
    if kind == "flame":
        art = (
            f'<path d="M{c} 10 C{c + 18} 28,{c + 22} 44,{c + 12} 58 C{c + 16} 46,{c + 6} 40,{c + 4} 34 '
            f'C{c + 2} 46,{c - 10} 50,{c - 6} 62 C{c - 22} 52,{c - 20} 30,{c} 10 Z" fill="{color}"/>'
        )
    elif kind == "gear":
        teeth = "".join(
            f'<rect x="{c - 5}" y="4" width="10" height="14" fill="{color}" '
            f'transform="rotate({a} {c} {c})"/>'
            for a in range(0, 360, 45)
        )
        art = teeth + (
            f'<circle cx="{c}" cy="{c}" r="{c - 14}" fill="{color}"/>'
            f'<circle cx="{c}" cy="{c}" r="{c - 26}" fill="#fff"/>'
        )
    elif kind == "leaf":
        art = (
            f'<path d="M14 {size - 14} C14 30,40 10,{size - 12} 12 C{size - 10} 46,50 {size - 12},14 {size - 14} Z" '
            f'fill="{color}"/><path d="M16 {size - 16} L{size - 22} 22" stroke="#fff" stroke-width="2.5"/>'
        )
    elif kind == "pillar":
        cols = "".join(
            f'<rect x="{16 + i * 12}" y="30" width="7" height="30" fill="{color}"/>'
            for i in range(4)
        )
        art = (
            f'<path d="M10 28 L{c} 8 L{size - 10} 28 Z" fill="{color}"/>{cols}'
            f'<rect x="10" y="62" width="{size - 20}" height="6" fill="{color}"/>'
        )
    elif kind == "bolt":
        art = (
            f'<circle cx="{c}" cy="{c}" r="{c - 4}" fill="{color}"/>'
            f'<path d="M{c + 4} 12 L{c - 12} {c + 4} L{c} {c + 4} L{c - 6} {size - 12} '
            f'L{c + 14} {c - 6} L{c + 2} {c - 6} Z" fill="#fff"/>'
        )
    elif kind == "drop":
        art = (
            f'<path d="M{c} 8 C{c + 20} 34,{c + 24} 46,{c + 20} 56 A 21 21 0 0 1 {c - 20} 56 '
            f'C{c - 24} 46,{c - 20} 34,{c} 8 Z" fill="{color}"/>'
        )
    elif kind == "shield":
        art = (
            f'<path d="M{c} 6 L{size - 10} 16 L{size - 12} 42 C{size - 14} 58,{c + 10} 66,{c} 72 '
            f'C{c - 10} 66,14 58,12 42 L10 16 Z" fill="{color}"/>'
            f'<path d="M{c - 14} 38 L{c - 4} 48 L{c + 16} 26" stroke="#fff" stroke-width="5" fill="none"/>'
        )
    else:
        raise ValueError(kind)
    return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">{art}</svg>'


def guilloche_data_uri(color: str, w: int = 400, h: int = 60, seed: int = 1) -> str:
    """A security-print style band of interlaced sine waves, as a CSS background."""
    rng = random.Random(seed)
    paths = []
    for k in range(9):
        amp = h / 2 - 4 - k * 1.3
        freq = rng.choice([3, 4, 5, 6])
        phase = k * 0.7
        pts = " ".join(
            f"{x},{h / 2 + amp * math.sin(2 * math.pi * freq * x / w + phase):.1f}"
            for x in range(0, w + 1, 4)
        )
        paths.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="0.6"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{"".join(paths)}</svg>'
    return "data:image/svg+xml;utf8," + svg.replace("#", "%23").replace('"', "'")
