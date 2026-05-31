"""Fetch and aggregate GitHub statistics using parallel API calls."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from .client import GitHubClient, WakaTimeClient
from .models import (
    ContributionYear,
    GitHubStats,
    LanguageInfo,
    ProfileInfo,
    RepoTrafficStats,
    RepoInfo,
    SocialAccount,
    WakaTimeStats,
)
from .queries import all_contribs, contrib_years, profile_info, repos_overview


class StatsFetcher:
    """Orchestrates parallel fetching of GitHub and WakaTime statistics."""

    def __init__(
        self,
        client: GitHubClient,
        wakatime_client: Optional[WakaTimeClient] = None,
        exclude_repos: Optional[Set[str]] = None,
        exclude_langs: Optional[Set[str]] = None,
        ignore_forked_repos: bool = False,
    ):
        self.client = client
        self.wakatime_client = wakatime_client
        self.exclude_repos = exclude_repos or set()
        self.exclude_langs = {x.lower() for x in (exclude_langs or set())}
        self.ignore_forked_repos = ignore_forked_repos

    async def fetch_all(self) -> GitHubStats:
        """Fetch all statistics in parallel where possible."""
        stats = GitHubStats()

        # Fetch profile first to get login for repo filtering
        profile_result = await self._fetch_profile()
        user_login = profile_result.login

        # Fire remaining queries in parallel
        repos_task = asyncio.create_task(self._fetch_repos(user_login))
        contributions_task = asyncio.create_task(self._fetch_contributions())
        wakatime_task = asyncio.create_task(self._fetch_wakatime())

        # Wait for all independent queries
        repos_result, contributions_result, wakatime_result = await asyncio.gather(
            repos_task,
            contributions_task,
            wakatime_task,
        )

        repo_traffic = await self._fetch_repo_traffic(repos_result["owned_repos"])

        stats.repos = repos_result["repos"]
        stats.owned_repos = repos_result["owned_repos"]
        stats.languages = repos_result["languages"]
        stats.repo_names = repos_result["repo_names"]
        stats.profile = profile_result
        stats.contributions = contributions_result["years"]
        stats.total_contributions = contributions_result["total"]
        stats.contribution_mix = contributions_result["mix"]
        stats.repo_traffic = repo_traffic
        stats.social_accounts = profile_result.social_accounts
        stats.wakatime = wakatime_result

        return stats

    async def _fetch_repos(self, user_login: str = "") -> Dict[str, Any]:
        """Fetch repository overview with languages."""
        repos: List[RepoInfo] = []
        owned_repos: List[RepoInfo] = []
        languages: Dict[str, LanguageInfo] = {}
        repo_names: Set[str] = set()
        stargazers = 0
        forks = 0

        next_owned = None
        next_contrib = None

        while True:
            raw = await self.client.graphql(
                repos_overview(owned_cursor=next_owned, contrib_cursor=next_contrib)
            )
            viewer = raw.get("data", {}).get("viewer", {})
            login = user_login or viewer.get("login", "")

            owned_repos_data = viewer.get("repositories", {})
            contrib_repos_data = viewer.get("repositoriesContributedTo", {})

            # Process owned repos - only include repos owned by the user
            for repo in owned_repos_data.get("nodes", []):
                if repo is None:
                    continue
                name = repo.get("nameWithOwner", "")
                if name in repo_names or name in self.exclude_repos:
                    continue

                # Skip external repos (not owned by user)
                owner = name.split("/")[0] if "/" in name else ""
                if owner and owner.lower() != login.lower():
                    continue

                repo_names.add(name)

                stars = repo.get("stargazers", {}).get("totalCount", 0)
                fork_count = repo.get("forkCount", 0)
                stargazers += stars
                forks += fork_count

                repo_info = RepoInfo(
                    name=name,
                    stars=stars,
                    forks=fork_count,
                    is_private=repo.get("isPrivate", False),
                )
                repos.append(repo_info)
                owned_repos.append(repo_info)

                for edge in repo.get("languages", {}).get("edges", []):
                    lang_name = edge.get("node", {}).get("name", "Other")
                    if lang_name.lower() in self.exclude_langs:
                        continue
                    size = edge.get("size", 0)
                    if lang_name in languages:
                        languages[lang_name].size += size
                        languages[lang_name].occurrences += 1
                    else:
                        languages[lang_name] = LanguageInfo(
                            name=lang_name,
                            size=size,
                            occurrences=1,
                            color=edge.get("node", {}).get("color"),
                        )

            # Process contributed repos (for language stats only, not top repos)
            if not self.ignore_forked_repos:
                for repo in contrib_repos_data.get("nodes", []):
                    if repo is None:
                        continue
                    name = repo.get("nameWithOwner", "")
                    if name in repo_names or name in self.exclude_repos:
                        continue
                    repo_names.add(name)

                    stars = repo.get("stargazers", {}).get("totalCount", 0)
                    fork_count = repo.get("forkCount", 0)

                    repos.append(
                        RepoInfo(
                            name=name,
                            stars=stars,
                            forks=fork_count,
                            is_private=repo.get("isPrivate", False),
                        )
                    )

                    for edge in repo.get("languages", {}).get("edges", []):
                        lang_name = edge.get("node", {}).get("name", "Other")
                        if lang_name.lower() in self.exclude_langs:
                            continue
                        size = edge.get("size", 0)
                        if lang_name in languages:
                            languages[lang_name].size += size
                            languages[lang_name].occurrences += 1
                        else:
                            languages[lang_name] = LanguageInfo(
                                name=lang_name,
                                size=size,
                                occurrences=1,
                                color=edge.get("node", {}).get("color"),
                            )

            has_next_owned = owned_repos_data.get("pageInfo", {}).get(
                "hasNextPage", False
            )
            has_next_contrib = contrib_repos_data.get("pageInfo", {}).get(
                "hasNextPage", False
            )

            if has_next_owned or has_next_contrib:
                next_owned = owned_repos_data.get("pageInfo", {}).get(
                    "endCursor", next_owned
                )
                next_contrib = contrib_repos_data.get("pageInfo", {}).get(
                    "endCursor", next_contrib
                )
            else:
                break

        # Calculate language proportions
        total_size = sum(l.size for l in languages.values())
        if total_size > 0:
            for lang in languages.values():
                lang.proportion = 100.0 * (lang.size / total_size)

        return {
            "repos": repos,
            "owned_repos": owned_repos,
            "languages": languages,
            "repo_names": repo_names,
        }

    async def _fetch_repo_traffic(self, repos: List[RepoInfo]) -> RepoTrafficStats:
        """Fetch and aggregate 14-day public repository traffic."""
        if not repos:
            return RepoTrafficStats()

        async def fetch_one(repo: RepoInfo) -> RepoTrafficStats:
            try:
                data = await self.client.rest(
                    f"/repos/{repo.name}/traffic/views",
                    params={"per": "day"},
                    max_retries=2,
                )
            except Exception as exc:
                print(f"Traffic unavailable for {repo.name}: {exc}")
                return RepoTrafficStats()

            return RepoTrafficStats(
                views=data.get("count", 0) or 0,
                visitors=data.get("uniques", 0) or 0,
            )

        results = await asyncio.gather(*(fetch_one(repo) for repo in repos))
        return RepoTrafficStats(
            views=sum(item.views for item in results),
            visitors=sum(item.visitors for item in results),
        )

    async def _fetch_profile(self) -> ProfileInfo:
        """Fetch profile information."""
        raw = await self.client.graphql(profile_info())
        viewer = raw.get("data", {}).get("viewer", {})

        raw_date = viewer.get("createdAt", "")
        joined_year = "N/A"
        if raw_date:
            try:
                joined_year = datetime.fromisoformat(
                    raw_date.replace("Z", "+00:00")
                ).strftime("%Y")
            except ValueError:
                joined_year = raw_date[:4] if len(raw_date) >= 4 else "N/A"

        social_accounts = []
        for node in viewer.get("socialAccounts", {}).get("nodes", []):
            provider = node.get("provider", "")
            url = node.get("url", "")
            if provider and url:
                social_accounts.append(SocialAccount(provider=provider, url=url))

        return ProfileInfo(
            login=viewer.get("login", ""),
            name=viewer.get("name") or viewer.get("login", ""),
            bio=viewer.get("bio"),
            company=viewer.get("company"),
            location=viewer.get("location"),
            website_url=viewer.get("websiteUrl"),
            twitter_username=viewer.get("twitterUsername"),
            followers=viewer.get("followers", {}).get("totalCount", 0),
            following=viewer.get("following", {}).get("totalCount", 0),
            pull_requests=viewer.get("pullRequests", {}).get("totalCount", 0),
            issues=viewer.get("issues", {}).get("totalCount", 0),
            joined_year=joined_year,
            gists=viewer.get("gists", {}).get("totalCount", 0),
            starred_repos=viewer.get("starredRepositories", {}).get("totalCount", 0),
            packages=viewer.get("packages", {}).get("totalCount", 0),
            discussions=viewer.get("repositoryDiscussions", {}).get("totalCount", 0),
            watched_repos=viewer.get("watching", {}).get("totalCount", 0),
            social_accounts=social_accounts,
        )

    async def _fetch_contributions(self) -> Dict[str, Any]:
        """Fetch contribution history across all years."""
        years_raw = await self.client.graphql(contrib_years())
        years_list = (
            years_raw.get("data", {})
            .get("viewer", {})
            .get("contributionsCollection", {})
            .get("contributionYears", [])
        )

        if not years_list:
            return {"years": [], "total": 0, "mix": {}}

        by_year_raw = await self.client.graphql(all_contribs(years_list))
        by_year_data = by_year_raw.get("data", {}).get("viewer", {})

        total = 0
        mix = {
            "commits": 0,
            "pull_requests": 0,
            "issues": 0,
            "reviews": 0,
            "repositories": 0,
        }
        years: List[ContributionYear] = []
        for key, year_data in by_year_data.items():
            count = year_data.get("contributionCalendar", {}).get(
                "totalContributions", 0
            )
            total += count
            mix["commits"] += year_data.get("totalCommitContributions", 0)
            mix["pull_requests"] += year_data.get("totalPullRequestContributions", 0)
            mix["issues"] += year_data.get("totalIssueContributions", 0)
            mix["reviews"] += year_data.get("totalPullRequestReviewContributions", 0)
            mix["repositories"] += year_data.get("totalRepositoryContributions", 0)
            year = key.replace("year", "")
            years.append(ContributionYear(year=year, count=count))

        # Sort by year descending
        years.sort(key=lambda y: y.year, reverse=True)

        return {"years": years, "total": total, "mix": mix}

    async def _fetch_wakatime(self) -> Optional[WakaTimeStats]:
        """Fetch WakaTime coding statistics."""
        if not self.wakatime_client:
            return None

        try:
            # Fetch both all-time and recent stats in parallel
            all_time_task = asyncio.create_task(self.wakatime_client.get_all_time())
            recent_task = asyncio.create_task(
                self.wakatime_client.get_stats("last_7_days")
            )

            all_time_data, recent_data = await asyncio.gather(
                all_time_task, recent_task
            )

            # Use all-time data for total, recent for breakdowns
            all_time = all_time_data.get("data", {})
            recent = recent_data.get("data", {})

            total_seconds = all_time.get("total_seconds", 0)
            total_text = all_time.get("text", "")
            if not total_text:
                total_text = recent.get("human_readable_total", "")

            daily_avg_seconds = recent.get("daily_average", 0)
            daily_avg_text = recent.get("human_readable_daily_average", "")

            return WakaTimeStats(
                total_seconds=total_seconds,
                total_text=total_text,
                daily_average_seconds=daily_avg_seconds,
                daily_average_text=daily_avg_text,
                languages=recent.get("languages", []),
                editors=recent.get("editors", []),
                categories=recent.get("categories", []),
                best_day=recent.get("best_day"),
            )
        except Exception as e:
            print(f"WakaTime API error: {e}")
            return None
