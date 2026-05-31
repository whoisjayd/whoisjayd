"""Environment settings for README generation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Set


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    access_token: str
    wakatime_api_key: Optional[str]
    exclude_repos: Optional[Set[str]]
    exclude_langs: Optional[Set[str]]
    ignore_forked_repos: bool
    readme_path: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from GitHub Actions or local environment."""
        access_token = (
            os.getenv("ACCESS_TOKEN")
            or os.getenv("METRICS_TOKEN")
            or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        )
        if not access_token:
            raise RuntimeError("A personal access token is required")

        return cls(
            access_token=access_token,
            wakatime_api_key=os.getenv("WAKATIME_API_KEY"),
            exclude_repos=_csv_set(os.getenv("EXCLUDED")),
            exclude_langs=_csv_set(os.getenv("EXCLUDED_LANGS")),
            ignore_forked_repos=_env_flag("EXCLUDE_FORKED_REPOS"),
            readme_path=_readme_path(),
        )


def _csv_set(value: Optional[str]) -> Optional[Set[str]]:
    if not value:
        return None
    items = {item.strip() for item in value.split(",") if item.strip()}
    return items or None


def _env_flag(name: str) -> bool:
    value = os.getenv(name)
    return bool(value) and value.strip().lower() not in {"0", "false", "no", "off"}


def _readme_path() -> str:
    package_dir = os.path.dirname(__file__)
    repo_root = os.path.dirname(package_dir)
    return os.path.join(repo_root, "README.md")


__all__ = ["Settings"]
