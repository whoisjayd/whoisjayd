"""Profile README markdown generator."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from html import escape
from typing import List, Tuple
from urllib.parse import quote

from .content import bullet_lines, load_bullets, social_links
from .language_colors import with_distinct_language_colors
from .models import GitHubStats

LanguageDisplay = Tuple[str, float, str]
LANGUAGE_BAR_URL = (
    "https://raw.githubusercontent.com/whoisjayd/whoisjayd/"
    "refs/heads/main/generated/language_bar.svg"
)


def _comma(value: int) -> str:
    return f"{value:,}"


def _icon(name: str, color: str, size: int = 14) -> str:
    color_value = quote(color if color.startswith("#") else f"#{color}")
    src = (
        f"https://api.iconify.design/lucide/{name}.svg"
        f"?color={color_value}&amp;width={size}&amp;height={size}"
    )
    return f'<img height="{size}" width="{size}" src="{src}" alt="">'


def _filtered_languages(
    stats: GitHubStats, threshold: float = 0.2
) -> List[LanguageDisplay]:
    return with_distinct_language_colors(
        [
            (name, data.proportion)
            for name, data in stats.sorted_languages
            if data.proportion >= threshold
        ]
    )


def _metric(icon_name: str, color: str, value: str, label: str) -> str:
    return f"{_icon(icon_name, color)} <b>{escape(value)}</b> {escape(label)}"


def _flow_items(items: list[str], separator: str = " &nbsp;&nbsp; ") -> str:
    return separator.join(items)


def _previous_metric(previous_readme: str | None, label: str) -> str | None:
    if not previous_readme:
        return None
    match = re.search(rf"<b>([^<]+)</b>\s+{re.escape(label)}", previous_readme)
    return match.group(1) if match else None


def _panel_cell(title: str, body: str) -> str:
    return f'<td valign="top"><b>{escape(title)}</b><br><br>{body}</td>'


def _profile_panel(intro: str, glance: str, languages: str) -> str:
    return (
        '<div align="center"><table width="100%">'
        f"<tr>{_panel_cell('What I do', intro)}</tr>"
        f"<tr>{_panel_cell('At a glance', glance)}</tr>"
        f"<tr>{_panel_cell('Most Used Languages', languages)}</tr>"
        "</table></div>"
    )


def generate_readme(stats: GitHubStats, previous_readme: str | None = None) -> str:
    """Generate the complete README markdown."""
    profile = stats.profile
    login = profile.login or "whoisjayd"
    name = profile.name or ("Jaydeep" if login == "whoisjayd" else login)
    total_stars = sum(repo.stars for repo in stats.owned_repos)

    header = f"""<h3 align="center">Hey, I'm {escape(name)} 👋</h3>

<p align="center">
  <samp>Backend Engineer&nbsp;•&nbsp;Open Source&nbsp;•&nbsp;Graduate</samp>
</p>"""

    socials = social_links(stats)
    intro = bullet_lines(load_bullets())

    if socials:
        header += f'\n\n<p align="center">{socials}</p>'

    glance = []
    if stats.total_contributions:
        glance.append(
            _metric(
                "activity",
                "#2dba4e",
                _comma(stats.total_contributions),
                "contributions",
            )
        )
    if stats.owned_repos:
        glance.append(
            _metric("book-open", "#58a6ff", _comma(len(stats.owned_repos)), "repos")
        )
    if total_stars:
        glance.append(_metric("star", "#e3b341", _comma(total_stars), "stars"))

    if stats.wakatime and stats.wakatime.total_text:
        waka = stats.wakatime
        glance.append(_metric("code-2", "#2dba4e", waka.total_text, "coding"))
        if waka.daily_average_text:
            glance.append(
                _metric("calendar", "#58a6ff", waka.daily_average_text, "daily")
            )
    else:
        previous_coding = _previous_metric(previous_readme, "coding")
        previous_daily = _previous_metric(previous_readme, "daily")
        if previous_coding:
            glance.append(_metric("code-2", "#2dba4e", previous_coding, "coding"))
        if previous_daily:
            glance.append(_metric("calendar", "#58a6ff", previous_daily, "daily"))
    if profile.joined_year and profile.joined_year != "N/A":
        glance.append(_metric("calendar-days", "#8b949e", profile.joined_year, "since"))

    languages = _filtered_languages(stats, threshold=0.2)
    language_lines = []
    for name_, proportion, color in languages[:10]:
        language_lines.append(
            f'<img height="8" width="8" src="https://singlecolorimage.com/get/{escape(color.lstrip("#"), quote=True)}/8x8" alt=""> '
            f"<b>{escape(name_)}</b> {proportion:.1f}%"
        )

    profile_panel = _profile_panel(
        intro,
        _flow_items(glance, separator=" &nbsp;&nbsp;·&nbsp;&nbsp; "),
        '<div align="left">'
        f'<img src="{LANGUAGE_BAR_URL}" width="100%" height="12" alt="Language usage bar"><br><br>'
        f"{_flow_items(language_lines)}"
        "</div>",
    )

    visitor_badge = (
        f'<img src="https://komarev.com/ghpvc/?username={escape(login, quote=True)}&color=00d9ff&style=pixel&label=views" '
        'alt="Profile views">'
    )
    footer = (
        '<div align="right">'
        f"<sub>{visitor_badge} &nbsp; Updated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</sub>"
        "</div>"
    )

    return "\n\n".join([header, profile_panel, footer])


def write_readme(content: str, path: str = "README.md") -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


__all__ = ["generate_readme", "write_readme"]
