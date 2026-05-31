"""User editable README content loaders."""

from __future__ import annotations

import os
from html import escape
from typing import List, Tuple

from .models import GitHubStats

SocialDisplay = Tuple[str, str, str]


def load_bullets() -> List[str]:
    """Load intro bullets from intro.txt."""
    path = project_file("intro.txt")
    if not os.path.isfile(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def bullet_lines(bullets: List[str]) -> str:
    """Render intro bullets with GitHub safe HTML."""
    lines = []
    for bullet in bullets:
        if " — " in bullet:
            title, detail = bullet.split(" — ", 1)
            lines.append(f"• <b>{escape(title)}</b> — {escape(detail)}")
        else:
            lines.append(f"• {escape(bullet)}")
    return "<br>\n".join(lines)


def social_links(stats: GitHubStats) -> str:
    """Render icon only social links from socials.txt and GitHub profile links."""
    icon_slugs = {
        "twitter": "x",
        "x": "x",
        "peerlist": "peerlist",
        "linkedin": "linkedin",
        "github": "github",
        "email": "gmail",
        "mail": "gmail",
        "website": "googlechrome",
        "web": "googlechrome",
    }
    icon_colors = {
        "twitter": "111111/f0f6fc",
        "x": "111111/f0f6fc",
        "peerlist": "00AA45",
        "linkedin": "0A66C2",
        "github": "181717/f0f6fc",
        "email": "EA4335",
        "mail": "EA4335",
        "website": "0969DA",
        "web": "0969DA",
    }

    socials = _load_socials_file()
    seen_urls = {url for _, url, _ in socials}
    for account in stats.profile.social_accounts:
        if account.url in seen_urls:
            continue
        provider = account.provider.lower()
        socials.append((account.provider, account.url, provider))
        seen_urls.add(account.url)

    links = []
    for label, url, provider in socials:
        slug = icon_slugs.get(provider, "linktree")
        color = icon_colors.get(provider, "0969DA")
        title = escape("X" if provider in {"x", "twitter"} else label, quote=True)
        src = (
            "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/linkedin/linkedin-original.svg"
            if provider == "linkedin"
            else f"https://cdn.simpleicons.org/{slug}/{color}?viewbox=auto"
        )
        links.append(
            f'<a href="{escape(url, quote=True)}" title="{title}">'
            f'<img height="22" width="22" src="{src}" alt="{title}"></a>'
        )

    return " &nbsp; ".join(links)


def project_file(filename: str) -> str:
    repo_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(repo_root, filename)


def _load_socials_file() -> List[SocialDisplay]:
    path = project_file("socials.txt")
    if not os.path.isfile(path):
        return []

    socials: List[SocialDisplay] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            parsed = _parse_social_line(line)
            if parsed is None:
                continue

            label, url = parsed
            socials.append((label, url, _provider_from(label, url)))

    return socials


def _parse_social_line(line: str) -> tuple[str, str] | None:
    if " — " in line:
        label, url = line.split(" — ", 1)
    elif ": " in line:
        label, url = line.split(": ", 1)
    else:
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            return None
        label, url = parts

    label = label.strip()
    url = _normalize_url(url.strip())
    if not label or not url:
        return None
    return label, url


def _normalize_url(url: str) -> str:
    if "@" in url and "://" not in url and not url.startswith("mailto:"):
        return f"mailto:{url}"
    if "://" not in url and not url.startswith("mailto:"):
        return f"https://{url}"
    return url


def _provider_from(label: str, url: str) -> str:
    text = f"{label} {url}".lower()
    if "peerlist" in text:
        return "peerlist"
    if "linkedin" in text:
        return "linkedin"
    if "x.com" in text or label.strip().lower() == "x":
        return "x"
    if "twitter" in text:
        return "x"
    if "github" in text:
        return "github"
    if "mailto:" in text or "email" in text or "mail" in text:
        return "mail"
    return "website"


__all__ = ["bullet_lines", "load_bullets", "social_links"]
