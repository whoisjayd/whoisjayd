"""Small SVG microcomponents for README visuals."""

from __future__ import annotations

import os
from html import escape
from pathlib import Path
from typing import Iterable, List, Tuple

from .models import GitHubStats

GENERATED_DIR = "generated"
LANGUAGE_BAR = "generated/language_bar.svg"

LanguageDisplay = Tuple[str, float, str]


def _bar_width(value: int, max_value: int, max_width: int) -> int:
    if value <= 0 or max_value <= 0:
        return 2
    return max(3, round((value / max_value) * max_width))


def _progress_svg(width: int, fill_width: int) -> str:
    return f"""<svg width=\"{width}\" height=\"8\" viewBox=\"0 0 {width} 8\" xmlns=\"http://www.w3.org/2000/svg\" role=\"img\">
<style>
.track {{ fill: #21262d; }}
.fill {{ fill: #2dba4e; }}
@media (prefers-color-scheme: light) {{ .track {{ fill: #d8dee4; }} }}
</style>
<rect class=\"track\" x=\"0\" y=\"0\" width=\"{width}\" height=\"8\" rx=\"4\"/>
<rect class=\"fill\" x=\"0\" y=\"0\" width=\"{fill_width}\" height=\"8\" rx=\"4\"/>
</svg>
"""


def _language_bar_svg(languages: List[LanguageDisplay], width: int = 360) -> str:
    segments = []
    cursor = 0
    for index, (_, proportion, color) in enumerate(languages):
        segment_width = max(2, round((proportion / 100) * width))
        if index == len(languages) - 1:
            segment_width = max(2, width - cursor)
        segments.append(
            f'<rect x="{cursor}" y="0" width="{segment_width}" height="8" fill="{escape(color)}"/>'
        )
        cursor += segment_width
        if cursor >= width:
            break
    return f"""<svg width=\"{width}\" height=\"8\" viewBox=\"0 0 {width} 8\" xmlns=\"http://www.w3.org/2000/svg\" role=\"img\">
<rect x=\"0\" y=\"0\" width=\"{width}\" height=\"8\" rx=\"4\" fill=\"#21262d\" opacity=\"0.65\"/>
<g clip-path=\"url(#clip)\">{''.join(segments)}</g>
<defs><clipPath id=\"clip\"><rect x=\"0\" y=\"0\" width=\"{width}\" height=\"8\" rx=\"4\"/></clipPath></defs>
</svg>
"""


def progress_path(year: str) -> str:
    return f"generated/progress_{year}.svg"


def generate_microcomponents(stats: GitHubStats, root: str) -> list[str]:
    """Generate small SVG assets and return written paths."""
    output_dir = Path(root) / GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    max_count = max((item.count for item in stats.contributions), default=0)
    for item in stats.contributions:
        path = Path(root) / progress_path(item.year)
        fill_width = _bar_width(item.count, max_count, 120)
        path.write_text(_progress_svg(120, fill_width), encoding="utf-8")
        written.append(os.fspath(path))

    languages = [
        (name, data.proportion, data.color or "#8b949e")
        for name, data in stats.sorted_languages
        if data.proportion >= 0.2
    ][:12]
    language_bar = Path(root) / LANGUAGE_BAR
    language_bar.write_text(_language_bar_svg(languages), encoding="utf-8")
    written.append(os.fspath(language_bar))

    return written


__all__ = ["LANGUAGE_BAR", "generate_microcomponents", "progress_path"]
