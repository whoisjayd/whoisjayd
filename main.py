"""Generate the profile README using live GitHub and WakaTime data."""

from __future__ import annotations

import asyncio
import os
import sys

import aiohttp

REPO_ROOT = os.path.dirname(__file__)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from github_stats.client import GitHubClient, WakaTimeClient
from github_stats.fetcher import StatsFetcher
from github_stats.markdown import generate_readme, write_readme
from github_stats.microcomponents import generate_microcomponents
from github_stats.settings import Settings


async def main() -> None:
    """Fetch stats and write the complete README."""
    settings = Settings.from_env()

    async with aiohttp.ClientSession() as session:
        client = GitHubClient(settings.access_token, session)
        wakatime_client = (
            WakaTimeClient(settings.wakatime_api_key, session)
            if settings.wakatime_api_key
            else None
        )
        fetcher = StatsFetcher(
            client,
            wakatime_client=wakatime_client,
            exclude_repos=settings.exclude_repos,
            exclude_langs=settings.exclude_langs,
            ignore_forked_repos=settings.ignore_forked_repos,
        )
        stats = await fetcher.fetch_all()

    previous_readme = None
    if os.path.exists(settings.readme_path):
        with open(settings.readme_path, encoding="utf-8") as f:
            previous_readme = f.read()

    generate_microcomponents(stats, REPO_ROOT)
    write_readme(generate_readme(stats, previous_readme), settings.readme_path)
    print("README.md updated")


if __name__ == "__main__":
    asyncio.run(main())
