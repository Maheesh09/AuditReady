"""HTML -> PDF (Chromium via Playwright), PDF -> images (PyMuPDF), and image degradation.

Degradation simulates what real factory uploads look like: phone photos taken on a desk
(perspective, rotation, uneven light, blur, JPEG) and office scans (grey, skewed, noisy).
Real photos of printed pages are still required for at least 10 documents (Plan 14.1).
"""

from __future__ import annotations

import io
import random
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from playwright.sync_api import Browser

from .certificates import Page

HEADER_FOOTER_STYLE = (
    "font-family:Arial,sans-serif;font-size:7.5pt;color:#555;width:100%;padding:0 14mm;"
)


def html_to_pdf(browser: Browser, page_spec: Page, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    pg = browser.new_page()
    pg.set_content(page_spec.html, wait_until="load")
    m = f"{page_spec.margin_mm}mm"
    has_hf = bool(page_spec.header_html or page_spec.footer_html)
    pg.pdf(
        path=str(out),
        format="A4",
        landscape=page_spec.landscape,
        print_background=True,
        prefer_css_page_size=not has_hf,
        margin={"top": m, "bottom": m, "left": "0mm", "right": "0mm"} if has_hf else None,
        display_header_footer=has_hf,
        header_template=f"<div style='{HEADER_FOOTER_STYLE}'>{page_spec.header_html}</div>"
        if has_hf
        else "",
        footer_template=f"<div style='{HEADER_FOOTER_STYLE}'>{page_spec.footer_html}</div>"
        if has_hf
        else "",
    )
    pg.close()


def pdf_to_images(pdf: Path, dpi: int = 170) -> list[Image.Image]:
    images = []
    with pymupdf.open(pdf) as doc:  # type: ignore[no-untyped-call]  # PyMuPDF ships no type hints
        for p in doc:
            pix = p.get_pixmap(dpi=dpi)
            images.append(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB"))
    return images


def images_to_pdf(images: list[Image.Image], out: Path, dpi: int = 150) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    first, rest = images[0], images[1:]
    first.save(out, "PDF", resolution=dpi, save_all=True, append_images=rest)


# ------------------------------------------------------------------ geometry helpers
def _perspective_coeffs(
    dst: list[tuple[float, float]], src: list[tuple[float, float]]
) -> list[float]:
    """Coefficients mapping output (dst) points back to input (src) points for PIL."""
    a = []
    b = []
    for (x, y), (u, v) in zip(dst, src, strict=True):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        b.extend([u, v])
    return [float(c) for c in np.linalg.solve(np.array(a, float), np.array(b, float))]


def _desk_background(w: int, h: int, rng: random.Random) -> Image.Image:
    base = np.array(rng.choice([(122, 94, 70), (86, 88, 92), (168, 150, 128), (60, 62, 70)]), float)
    nprng = np.random.default_rng(rng.randint(0, 10**6))
    grain = nprng.normal(0, 9, (h // 4 + 1, w // 4 + 1, 1))
    tiled = np.kron(grain, np.ones((4, 4, 1)))[:h, :w]
    streaks = np.sin(np.linspace(0, rng.uniform(20, 60), w))[None, :, None] * 6
    arr = np.clip(base + tiled + streaks, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def phone_photo(
    page: Image.Image, rng: random.Random, blur: float = 1.0, max_rot: float = 3.0
) -> Image.Image:
    """A photo of a printed page lying on a desk, taken with a phone."""
    pw, ph = page.size
    # 1. uneven lighting + warm indoor tint on the paper itself
    arr = np.asarray(page).astype(float)
    yy, xx = np.mgrid[0:ph, 0:pw]
    lx, ly = rng.uniform(0.2, 0.8), rng.uniform(0.1, 0.5)
    dist = np.sqrt(((xx / pw) - lx) ** 2 + ((yy / ph) - ly) ** 2)
    light = 1.02 - 0.22 * dist
    tint = np.array([1.0, 0.97, 0.9])
    arr = np.clip(arr * light[..., None] * tint, 0, 255)
    paper = Image.fromarray(arr.astype(np.uint8))

    # 2. place on a larger desk canvas with perspective and rotation
    cw, ch = int(pw * 1.22), int(ph * 1.16)
    ox, oy = (cw - pw) / 2, (ch - ph) / 2
    j = 0.035
    dst = [
        (ox + rng.uniform(-j, j) * pw, oy + rng.uniform(-j, j) * ph),
        (ox + pw + rng.uniform(-j, j) * pw, oy + rng.uniform(-j, j) * ph),
        (ox + pw + rng.uniform(-j, j) * pw, oy + ph + rng.uniform(-j, j) * ph),
        (ox + rng.uniform(-j, j) * pw, oy + ph + rng.uniform(-j, j) * ph),
    ]
    src: list[tuple[float, float]] = [(0.0, 0.0), (pw, 0.0), (pw, ph), (0.0, ph)]
    coeffs = _perspective_coeffs(dst, src)
    warped = paper.transform(
        (cw, ch), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC
    )
    mask = Image.new("L", (pw, ph), 255).transform(
        (cw, ch), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BILINEAR
    )
    canvas = _desk_background(cw, ch, rng)
    # soft drop shadow under the sheet
    shadow = mask.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.45))
    canvas.paste(Image.new("RGB", (cw, ch), (20, 18, 16)), (14, 18), shadow)
    canvas.paste(warped, (0, 0), mask)
    canvas = canvas.rotate(
        rng.uniform(-max_rot, max_rot),
        resample=Image.Resampling.BICUBIC,
        expand=False,
        fillcolor=(40, 38, 36),
    )

    # 3. the phone's own shadow falling across one corner
    shade = Image.new("L", canvas.size, 0)
    d = ImageDraw.Draw(shade)
    sx = rng.choice([0, cw])
    d.ellipse([sx - cw * 0.55, ch * 0.7, sx + cw * 0.55, ch * 1.5], fill=70)
    shade = shade.filter(ImageFilter.GaussianBlur(60))
    canvas = Image.composite(Image.new("RGB", canvas.size, (0, 0, 0)), canvas, shade)

    # 4. crop the edges a little, lens blur, sensor noise, JPEG round trip
    canvas = canvas.crop((int(cw * 0.04), int(ch * 0.03), int(cw * 0.96), int(ch * 0.97)))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    noise = np.random.default_rng(rng.randint(0, 10**6)).normal(
        0, 5, (canvas.height, canvas.width, 1)
    )
    canvas = Image.fromarray(
        np.clip(np.asarray(canvas).astype(float) + noise, 0, 255).astype(np.uint8)
    )
    buf = io.BytesIO()
    canvas.save(buf, "JPEG", quality=72)
    return Image.open(io.BytesIO(buf.getvalue())).convert("RGB")


def office_scan(page: Image.Image, rng: random.Random, skew: float = 1.0) -> Image.Image:
    """A page fed through an office scanner: grey, slightly skewed, speckled."""
    g = ImageOps.grayscale(page)
    g = g.rotate(
        rng.uniform(-skew, skew), resample=Image.Resampling.BICUBIC, expand=True, fillcolor=235
    )
    arr = np.asarray(g).astype(float)
    nprng = np.random.default_rng(rng.randint(0, 10**6))
    arr = arr * rng.uniform(0.92, 0.98) + nprng.normal(0, 7, arr.shape)
    speck = nprng.random(arr.shape) < 0.0008
    arr[speck] = rng.uniform(20, 80)
    # darker scanner-lid edge on one side
    edge = np.linspace(0.82, 1.0, 40)
    arr[:, :40] *= edge[None, :]
    g = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(0.55)
    )
    g = ImageOps.autocontrast(g, cutoff=1)
    return g.convert("RGB")
