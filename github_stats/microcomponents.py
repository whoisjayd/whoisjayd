"""Small SVG microcomponents for README visuals."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import List, Tuple

from .language_colors import with_distinct_language_colors
from .models import GitHubStats

GENERATED_DIR = "generated"
LANGUAGE_BAR = "generated/language_bar.svg"

LanguageDisplay = Tuple[str, float, str]


def _language_bar_svg(
    languages: List[LanguageDisplay], width: int = 1200, height: int = 12
) -> str:
    segments = []
    cursor = 0
    for index, (_, proportion, color) in enumerate(languages):
        segment_width = max(2, round((proportion / 100) * width))
        if index == len(languages) - 1:
            segment_width = max(2, width - cursor)
        segments.append(
            f'<rect x="{cursor}" y="0" width="{segment_width}" height="{height}" fill="{escape(color)}"/>'
        )
        cursor += segment_width
        if cursor >= width:
            break
    radius = height // 2
    return f"""<svg width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\" xmlns=\"http://www.w3.org/2000/svg\" role=\"img\">
<rect x=\"0\" y=\"0\" width=\"{width}\" height=\"{height}\" rx=\"{radius}\" fill=\"#21262d\" opacity=\"0.65\"/>
<g clip-path=\"url(#clip)\">{"".join(segments)}</g>
<defs><clipPath id=\"clip\"><rect x=\"0\" y=\"0\" width=\"{width}\" height=\"{height}\" rx=\"{radius}\"/></clipPath></defs>
</svg>
"""


def generate_microcomponents(stats: GitHubStats, root: str) -> list[str]:
    """Generate small SVG assets and return written paths."""
    output_dir = Path(root) / GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    languages = with_distinct_language_colors(
        [
            (name, data.proportion)
            for name, data in stats.sorted_languages
            if data.proportion >= 0.2
        ]
    )[:12]
    language_bar = Path(root) / LANGUAGE_BAR
    language_bar.write_text(_language_bar_svg(languages), encoding="utf-8")

    return [str(language_bar)]


__all__ = ["LANGUAGE_BAR", "generate_microcomponents"]
