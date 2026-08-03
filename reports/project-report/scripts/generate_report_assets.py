"""Generate reproducible charts and extract images used by the project report."""

from __future__ import annotations

import base64
import csv
import json
import re
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


REPORT_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = REPORT_DIR.parents[1]
IMAGE_DIR = REPORT_DIR / "images"
CHART_DIR = IMAGE_DIR / "charts"
FUSION_DIR = IMAGE_DIR / "fusion"

PARTS = ("bracket", "padeye", "stabilizer")
COLORS = {
    "bracket": "#2563EB",
    "padeye": "#0F766E",
    "stabilizer": "#B45309",
}
INK = "#111827"
MUTED = "#64748B"
GRID = "#D1D5DB"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    path = Path("C:/Windows/Fonts") / name
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _canvas(title: str, y_label: str) -> tuple[Image.Image, ImageDraw.ImageDraw, tuple[int, int, int, int]]:
    image = Image.new("RGB", (1720, 960), "white")
    draw = ImageDraw.Draw(image)
    plot = (180, 135, 1640, 805)
    draw.text((860, 45), title, font=_font(42, True), fill=INK, anchor="ma")
    label_layer = Image.new("RGBA", (420, 70), (255, 255, 255, 0))
    label_draw = ImageDraw.Draw(label_layer)
    label_draw.text(
        (210, 35),
        y_label,
        font=_font(29),
        fill=INK,
        anchor="mm",
    )
    label_layer = label_layer.rotate(90, expand=True)
    image.paste(label_layer, (25, 300), label_layer)
    draw.line((plot[0], plot[1], plot[0], plot[3]), fill=INK, width=3)
    draw.line((plot[0], plot[3], plot[2], plot[3]), fill=INK, width=3)
    return image, draw, plot


def _load_candidates(part_id: str) -> list[dict[str, str]]:
    path = (
        REPO_DIR
        / "reports"
        / f"final_20260728_{part_id}_validation"
        / "validation_candidates.csv"
    )
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _load_cad_mass(part_id: str, candidate_id: str) -> float:
    path = (
        REPO_DIR
        / "reports"
        / f"final_20260728_{part_id}_validation"
        / "fusion_responses"
        / f"{candidate_id}_request_response.json"
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    return float(data["metrics"]["mass_kg"])


def _draw_y_grid(
    draw: ImageDraw.ImageDraw,
    plot: tuple[int, int, int, int],
    maximum: float,
    steps: int = 5,
) -> None:
    left, top, right, bottom = plot
    for index in range(steps + 1):
        value = maximum * index / steps
        y = bottom - (bottom - top) * index / steps
        draw.line((left, y, right, y), fill=GRID, width=2)
        draw.text(
            (left - 18, y),
            f"{value:.1f}",
            font=_font(23),
            fill=MUTED,
            anchor="rm",
        )


def _legend(
    draw: ImageDraw.ImageDraw,
    entries: list[tuple[str, str]],
    origin: tuple[int, int],
) -> None:
    x, y = origin
    for color, label in entries:
        draw.rectangle((x, y, x + 30, y + 22), fill=color, outline=INK, width=1)
        draw.text((x + 42, y + 11), label, font=_font(22), fill=INK, anchor="lm")
        x += 330


def make_mass_comparison() -> None:
    baselines = []
    finalists = []
    reductions = []
    for part_id in PARTS:
        rows = _load_candidates(part_id)
        baseline = float(rows[0]["mass_kg"])
        finalist = float(rows[1]["mass_kg"])
        baselines.append(baseline)
        finalists.append(finalist)
        reductions.append(100.0 * (baseline - finalist) / baseline)

    labels = ["Bracket", "Padeye", "Stabilizer"]
    maximum = 24.0
    image, draw, plot = _canvas(
        "Baseline and Selected Finalist Mass", "Mass (kg)"
    )
    _draw_y_grid(draw, plot, maximum, 6)
    left, top, right, bottom = plot
    centers = [430, 910, 1390]
    scale = (bottom - top) / maximum
    for index, center in enumerate(centers):
        for x0, value, color in (
            (center - 118, baselines[index], "#94A3B8"),
            (center + 18, finalists[index], COLORS[PARTS[index]]),
        ):
            y0 = bottom - value * scale
            draw.rectangle((x0, y0, x0 + 100, bottom), fill=color, outline=INK, width=2)
            draw.text(
                (x0 + 50, y0 - 10),
                f"{value:.2f}",
                font=_font(24, True),
                fill=INK,
                anchor="mb",
            )
        draw.text((center, bottom + 24), labels[index], font=_font(28, True), fill=INK, anchor="ma")
        draw.text(
            (center, top + 25),
            f"{reductions[index]:.1f}% reduction",
            font=_font(24),
            fill=INK,
            anchor="ma",
        )
    _legend(
        draw,
        [
            ("#94A3B8", "Baseline"),
            ("#2563EB", "Bracket finalist"),
            ("#0F766E", "Padeye finalist"),
            ("#B45309", "Stabilizer finalist"),
        ],
        (215, 875),
    )
    image.save(CHART_DIR / "mass_baseline_finalist.png", dpi=(240, 240))


def make_constraint_margin() -> None:
    fos_min = 2.5
    deflection_limits = {"bracket": 0.5, "padeye": 0.5, "stabilizer": 5.0}
    fos_ratios = []
    deflection_ratios = []
    for part_id in PARTS:
        row = _load_candidates(part_id)[1]
        fos_ratios.append(float(row["factor_of_safety"]) / fos_min)
        deflection_ratios.append(
            float(row["max_deflection_mm"]) / deflection_limits[part_id]
        )

    labels = ["Bracket", "Padeye", "Stabilizer"]
    maximum = 1.2
    image, draw, plot = _canvas(
        "Selected Finalist Constraint Use", "Normalized response"
    )
    _draw_y_grid(draw, plot, maximum, 6)
    left, top, right, bottom = plot
    centers = [430, 910, 1390]
    scale = (bottom - top) / maximum
    for index, center in enumerate(centers):
        for x0, value, color in (
            (center - 118, fos_ratios[index], "#0F766E"),
            (center + 18, deflection_ratios[index], "#B45309"),
        ):
            y0 = bottom - value * scale
            draw.rectangle((x0, y0, x0 + 100, bottom), fill=color, outline=INK, width=2)
            draw.text((x0 + 50, y0 - 10), f"{value:.2f}", font=_font(24, True), fill=INK, anchor="mb")
        draw.text((center, bottom + 24), labels[index], font=_font(28, True), fill=INK, anchor="ma")
    limit_y = bottom - 1.0 * scale
    for x0 in range(left, right, 28):
        draw.line((x0, limit_y, min(x0 + 15, right), limit_y), fill="#B91C1C", width=4)
    _legend(
        draw,
        [
            ("#0F766E", "FOS / minimum FOS"),
            ("#B45309", "Deflection / limit"),
            ("#B91C1C", "Constraint limit"),
        ],
        (230, 875),
    )
    image.save(CHART_DIR / "constraint_use.png", dpi=(240, 240))


def make_cad_agreement() -> None:
    analytical = []
    cad = []
    annotations = []
    for part_id in PARTS:
        rows = _load_candidates(part_id)
        for candidate_id, label in (("baseline", "baseline"), ("candidate_01", "finalist")):
            row = next(item for item in rows if item["candidate_id"] == candidate_id)
            analytical.append(float(row["mass_kg"]))
            cad.append(_load_cad_mass(part_id, candidate_id))
            annotations.append(f"{part_id.title()} {label}")

    maximum = 22.0
    image, draw, plot = _canvas(
        "Analytical and Native-CAD Mass Agreement", "Fusion CAD mass (kg)"
    )
    _draw_y_grid(draw, plot, maximum, 5)
    left, top, right, bottom = plot
    for index in range(6):
        x = left + (right - left) * index / 5
        value = maximum * index / 5
        draw.line((x, top, x, bottom), fill=GRID, width=2)
        draw.text((x, bottom + 18), f"{value:.1f}", font=_font(23), fill=MUTED, anchor="ma")
    for start in range(0, 1000, 32):
        x0 = left + (right - left) * start / 1000
        y0 = bottom - (bottom - top) * start / 1000
        x1 = left + (right - left) * min(start + 18, 1000) / 1000
        y1 = bottom - (bottom - top) * min(start + 18, 1000) / 1000
        draw.line((x0, y0, x1, y1), fill="#475569", width=3)
    for index, (x_value, y_value, label) in enumerate(
        zip(analytical, cad, annotations, strict=True)
    ):
        part_id = PARTS[index // 2]
        x = left + (right - left) * x_value / maximum
        y = bottom - (bottom - top) * y_value / maximum
        radius = 13 if index % 2 == 0 else 11
        if index % 2 == 0:
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=COLORS[part_id], outline=INK, width=2)
        else:
            draw.rectangle((x - radius, y - radius, x + radius, y + radius), fill=COLORS[part_id], outline=INK, width=2)
        draw.text((x + 18, y - 10), label, font=_font(21), fill=INK, anchor="ls")
    draw.text((910, 900), "Analytical mass (kg)", font=_font(29), fill=INK, anchor="ma")
    image.save(CHART_DIR / "cad_mass_agreement.png", dpi=(240, 240))


def extract_fusion_images() -> None:
    pattern = re.compile(
        r"data:image/(?P<kind>png|jpeg|jpg);base64,(?P<data>[A-Za-z0-9+/=\s]+)",
        re.IGNORECASE,
    )
    reports = (
        ("study_1", REPO_DIR / "F360 report" / "Study 1.html"),
        ("study_2", REPO_DIR / "F360 report" / "Study Final.html"),
        ("study_final", REPO_DIR / "F360 report" / "Study Final.html"),
    )
    extracted: list[Path] = []
    for prefix, source in reports:
        html = source.read_text(encoding="utf-8", errors="replace")
        for index, match in enumerate(pattern.finditer(html), start=1):
            extension = (
                "jpg"
                if match.group("kind").lower() in {"jpeg", "jpg"}
                else "png"
            )
            output = FUSION_DIR / f"{prefix}_{index:02d}.{extension}"
            decoded = base64.b64decode(
                re.sub(r"\s+", "", match.group("data"))
            )
            image = Image.open(BytesIO(decoded)).convert("RGB")
            difference = ImageChops.difference(
                image, Image.new("RGB", image.size, "white")
            )
            bounds = difference.getbbox()
            if bounds is not None:
                left, top, right, bottom = bounds
                padding = 24
                bounds = (
                    max(0, left - padding),
                    max(0, top - padding),
                    min(image.width, right + padding),
                    min(image.height, bottom + padding),
                )
                image = image.crop(bounds)
            image.save(output)
            extracted.append(output)

    thumbnails = []
    for path in extracted:
        with Image.open(path) as image:
            copy = image.convert("RGB")
            copy.thumbnail((300, 190))
            tile = Image.new("RGB", (320, 225), "white")
            tile.paste(copy, ((320 - copy.width) // 2, 8))
            draw = ImageDraw.Draw(tile)
            draw.text((10, 202), path.name, fill="#111827")
            thumbnails.append(tile)

    if thumbnails:
        columns = 3
        rows = (len(thumbnails) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * 320, rows * 225), "#E5E7EB")
        for index, tile in enumerate(thumbnails):
            sheet.paste(tile, ((index % columns) * 320, (index // columns) * 225))
        sheet.save(FUSION_DIR / "contact_sheet.png", quality=95)


def main() -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    FUSION_DIR.mkdir(parents=True, exist_ok=True)
    make_mass_comparison()
    make_constraint_margin()
    make_cad_agreement()
    extract_fusion_images()


if __name__ == "__main__":
    main()
