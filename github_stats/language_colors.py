"""Generated language colors for README visuals."""

from __future__ import annotations

from colorsys import hls_to_rgb
from typing import Iterable, List, Tuple

LanguageInput = Tuple[str, float]
LanguageDisplay = Tuple[str, float, str]


PASTEL_HUES = (195, 303, 51, 231, 123, 339, 25, 267, 180, 15, 285, 75)


def _hue_to_hex(hue: float, index: int) -> str:
    saturation = 0.68
    lightness = 0.68 + (0.04 if index % 2 else 0)
    red, green, blue = hls_to_rgb(hue / 360, lightness, saturation)
    return f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"


def _generated_hue(index: int) -> float:
    if index < len(PASTEL_HUES):
        return float(PASTEL_HUES[index])
    return float((PASTEL_HUES[-1] + 137 * (index - len(PASTEL_HUES) + 1)) % 360)


def with_distinct_language_colors(
    languages: Iterable[LanguageInput],
) -> List[LanguageDisplay]:
    """Assign stable generated colors with strong adjacent contrast."""
    colored: List[LanguageDisplay] = []
    for index, (name, proportion) in enumerate(languages):
        colored.append((name, proportion, _hue_to_hex(_generated_hue(index), index)))
    return colored


__all__ = ["with_distinct_language_colors"]
