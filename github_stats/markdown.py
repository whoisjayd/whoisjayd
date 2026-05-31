"""Profile README markdown generator."""

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from typing import Iterable, List, Tuple
from urllib.parse import quote

from .content import bullet_lines, load_bullets, social_links
from .microcomponents import LANGUAGE_BAR, progress_path
from .models import GitHubStats

LanguageDisplay = Tuple[str, float, str]


def _comma(value: int) -> str:
    return f"{value:,}"


def _repo_display_name(full_name: str) -> str:
    return full_name.split("/", 1)[1] if "/" in full_name else full_name


def _icon(name: str, color: str, size: int = 14) -> str:
    color_value = quote(color if color.startswith("#") else f"#{color}")
    src = (
        f"https://api.iconify.design/lucide/{name}.svg"
        f"?color={color_value}&amp;width={size}&amp;height={size}"
    )
    return f'<img height="{size}" width="{size}" src="{src}" alt="">'


def _bar(value: int, max_value: int, width: int = 10) -> str:
    if value <= 0 or max_value <= 0:
        return "▫" * width
    filled = max(1, round((value / max_value) * width))
    return "▰" * filled + "▫" * (width - filled)


def _join(items: Iterable[str]) -> str:
    return "<br>".join(item for item in items if item)


def _filtered_languages(
    stats: GitHubStats, threshold: float = 0.2
) -> List[LanguageDisplay]:
    return [
        (name, data.proportion, data.color or "#8b949e")
        for name, data in stats.sorted_languages
        if data.proportion >= threshold
    ]


def _metric(icon_name: str, color: str, value: str, label: str) -> str:
    return f"{_icon(icon_name, color)} <b>{escape(value)}</b> {escape(label)}"


def _paired_lines(items: list[str]) -> str:
    rows = []
    for index in range(0, len(items), 2):
        left = items[index]
        right = items[index + 1] if index + 1 < len(items) else ""
        rows.append(f"{left} &nbsp;&nbsp; {right}" if right else left)
    return "<br>".join(rows)


def _column_lines(items: list[str], columns: int) -> str:
    rows = []
    for index in range(0, len(items), columns):
        row = items[index : index + columns]
        rows.append(" &nbsp;&nbsp; ".join(row))
    return "<br>".join(rows)


def _repo_lines(rows: list[tuple[str, str, int, int]]) -> str:
    lines = [
        "<sub><b>Repository</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
        f"{_icon('star', '#e3b341', 12)} <b>Stars</b> &nbsp;&nbsp; "
        f"{_icon('git-fork', '#79c0ff', 12)} <b>Forks</b></sub>"
    ]
    for name, url, stars, forks in rows:
        lines.append(
            f'<a href="{escape(url, quote=True)}"><b>{escape(name)}</b></a>'
            f" &nbsp;&nbsp; {_comma(stars)}"
            f" &nbsp;&nbsp; {_comma(forks)}"
        )
    return "<br>".join(lines)


def _inline_group(title: str, body: str) -> str:
    return f"<p><b>{escape(title)}</b><br>{body}</p>"


def _table_panel(width: str, cells: list[tuple[str, str, str]]) -> str:
    rendered_cells = []
    for cell_width, title, body in cells:
        rendered_cells.append(
            f'<td width="{escape(cell_width, quote=True)}" valign="top">'
            f"<b>{escape(title)}</b><br>{body}"
            "</td>"
        )
    return (
        '<div align="center">'
        f'<table width="{escape(width, quote=True)}"><tr>'
        f"{''.join(rendered_cells)}"
        "</tr></table>"
        "</div>"
    )


def generate_readme(stats: GitHubStats) -> str:
    """Generate the complete README markdown."""
    profile = stats.profile
    login = profile.login or "whoisjayd"
    name = profile.name or ("Jaydeep" if login == "whoisjayd" else login)
    total_stars = sum(repo.stars for repo in stats.owned_repos)
    total_forks = sum(repo.forks for repo in stats.owned_repos)
    private_repos = sum(1 for repo in stats.owned_repos if repo.is_private)

    header = f"""<h3 align="center">Hey, I'm {escape(name)} 👋</h3>

<p align="center">
  <samp>Backend Engineer &nbsp;•&nbsp; Open Source &nbsp;•&nbsp; Graduate</samp>
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
    if private_repos:
        glance.append(_metric("lock", "#8b949e", _comma(private_repos), "private"))
    if total_stars:
        glance.append(_metric("star", "#e3b341", _comma(total_stars), "stars"))
    if total_forks:
        glance.append(_metric("git-fork", "#79c0ff", _comma(total_forks), "forks"))
    if stats.repo_traffic.views:
        glance.append(
            _metric("eye", "#58a6ff", _comma(stats.repo_traffic.views), "repo views")
        )
    if stats.repo_traffic.visitors:
        glance.append(
            _metric(
                "users", "#a371f7", _comma(stats.repo_traffic.visitors), "repo visitors"
            )
        )
    if profile.joined_year and profile.joined_year != "N/A":
        glance.append(_metric("calendar-days", "#8b949e", profile.joined_year, "since"))

    coding = []
    if stats.wakatime and stats.wakatime.total_text:
        waka = stats.wakatime
        coding.append(_metric("code-2", "#2dba4e", waka.total_text, "total"))
        if waka.daily_average_text:
            coding.append(
                _metric("calendar", "#58a6ff", waka.daily_average_text, "daily")
            )
        if waka.best_day and waka.best_day.get("date"):
            coding.append(
                _metric("sparkles", "#e3b341", str(waka.best_day["date"]), "best day")
            )
    else:
        coding.append("<sub>WakaTime data unavailable</sub>")

    top_panel = "\n\n".join(
        [
            _inline_group("What I do", intro),
            _inline_group("At a glance", _column_lines(glance, 4)),
            _inline_group("Coding rhythm", _join(coding)),
        ]
    )

    max_count = max((item.count for item in stats.contributions), default=0)
    contribution_lines = []
    for item in sorted(stats.contributions, key=lambda row: row.year, reverse=True)[:6]:
        contribution_lines.append(
            f"{escape(item.year)} &nbsp; "
            f'<img src="./{progress_path(item.year)}" width="120" height="8" alt="">'
            f" &nbsp; <b>{_comma(item.count)}</b>"
        )

    mix = []
    for icon_name, color, label, value in (
        (
            "git-pull-request",
            "#a371f7",
            "PRs",
            stats.contribution_mix.get("pull_requests", 0),
        ),
        ("circle-alert", "#f85149", "issues", stats.contribution_mix.get("issues", 0)),
        (
            "messages-square",
            "#58a6ff",
            "reviews",
            stats.contribution_mix.get("reviews", 0),
        ),
    ):
        if value:
            mix.append(_metric(icon_name, color, _comma(value), label))

    repo_rows = []
    for repo in stats.top_repos[:5]:
        url = f"https://github.com/{repo.name}"
        repo_rows.append((_repo_display_name(repo.name), url, repo.stars, repo.forks))

    languages = _filtered_languages(stats, threshold=0.2)
    language_lines = []
    for name_, proportion, color in languages[:10]:
        language_lines.append(
            f'<img height="8" width="8" src="https://singlecolorimage.com/get/{escape(color.lstrip("#"), quote=True)}/8x8" alt=""> '
            f"<b>{escape(name_)}</b> {proportion:.1f}%"
        )

    bottom_panel = "\n\n".join(
        [
            _inline_group(
                "Contribution History",
                f"{_join(contribution_lines)}<br><br><b>Contribution Mix</b><br>{_paired_lines(mix)}",
            ),
            _inline_group("Top Repositories", _repo_lines(repo_rows)),
            _inline_group(
                "Most Used Languages",
                f'<img src="./{LANGUAGE_BAR}" width="74%" height="8" alt="Language usage bar"><br><br>'
                f"{_column_lines(language_lines, 3)}",
            ),
        ]
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

    return "\n\n".join([header, top_panel, bottom_panel, footer])


def write_readme(content: str, path: str = "README.md") -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


__all__ = ["generate_readme", "write_readme"]
