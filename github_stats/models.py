"""Data models for GitHub statistics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class RepoInfo:
    """Basic repository information."""

    name: str
    stars: int = 0
    forks: int = 0
    is_private: bool = False


@dataclass
class LanguageInfo:
    """Language statistics."""

    name: str
    size: int = 0
    occurrences: int = 0
    color: Optional[str] = None
    proportion: float = 0.0


@dataclass
class ProfileInfo:
    """Profile-level statistics."""

    name: str = ""
    login: str = ""
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    twitter_username: Optional[str] = None
    followers: int = 0
    following: int = 0
    pull_requests: int = 0
    issues: int = 0
    joined_year: str = "N/A"
    gists: int = 0
    starred_repos: int = 0
    packages: int = 0
    discussions: int = 0
    watched_repos: int = 0
    social_accounts: list[SocialAccount] = field(default_factory=list)


@dataclass
class SocialAccount:
    """Social account link."""

    provider: str
    url: str


@dataclass
class ContributionYear:
    """Contributions for a single year."""

    year: str
    count: int


@dataclass
class WakaTimeStats:
    """WakaTime coding statistics."""

    total_seconds: int = 0
    total_text: str = ""
    daily_average_seconds: int = 0
    daily_average_text: str = ""
    languages: List[Dict[str, Any]] = field(default_factory=list)
    editors: List[Dict[str, Any]] = field(default_factory=list)
    categories: List[Dict[str, Any]] = field(default_factory=list)
    best_day: Optional[Dict[str, Any]] = None


@dataclass
class RepoTrafficStats:
    """Aggregated repository traffic statistics."""

    views: int = 0
    visitors: int = 0


@dataclass
class GitHubStats:
    """Container for all fetched GitHub statistics."""

    profile: ProfileInfo = field(default_factory=ProfileInfo)
    repos: List[RepoInfo] = field(default_factory=list)
    owned_repos: List[RepoInfo] = field(default_factory=list)
    languages: Dict[str, LanguageInfo] = field(default_factory=dict)
    contributions: List[ContributionYear] = field(default_factory=list)
    total_contributions: int = 0
    contribution_mix: Dict[str, int] = field(default_factory=dict)
    repo_traffic: RepoTrafficStats = field(default_factory=RepoTrafficStats)
    social_accounts: List[SocialAccount] = field(default_factory=list)
    repo_names: Set[str] = field(default_factory=set)

    @property
    def top_repos(self, limit: int = 5) -> List[RepoInfo]:
        """Return top public owned repositories by star count."""
        public_repos = [repo for repo in self.owned_repos if not repo.is_private]
        return sorted(public_repos, key=lambda r: r.stars, reverse=True)[:limit]

    wakatime: Optional[WakaTimeStats] = None

    @property
    def sorted_languages(self) -> List[tuple[str, LanguageInfo]]:
        """Return languages sorted by size descending."""
        return sorted(
            self.languages.items(),
            key=lambda t: t[1].size,
            reverse=True,
        )
