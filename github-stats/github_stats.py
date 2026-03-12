#!/usr/bin/python3

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any, cast

import aiohttp
import requests


###############################################################################
# Main Classes
###############################################################################


class Queries(object):
    """
    Class with functions to query the GitHub GraphQL (v4) API and the REST (v3)
    API. Also includes functions to dynamically generate GraphQL queries.
    """

    def __init__(
        self,
        username: str,
        access_token: str,
        session: aiohttp.ClientSession,
        max_connections: int = 10,
    ):
        self.username = username
        self.access_token = access_token
        self.session = session
        self.semaphore = asyncio.Semaphore(max_connections)

    async def query(self, generated_query: str) -> Dict:
        """
        Make a request to the GraphQL API using the authentication token from
        the environment
        :param generated_query: string query to be sent to the API
        :return: decoded GraphQL JSON output
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        try:
            async with self.semaphore:
                r_async = await self.session.post(
                    "https://api.github.com/graphql",
                    headers=headers,
                    json={"query": generated_query},
                )
            result = await r_async.json()
            if result is not None:
                return result
        except Exception as e:
            print(f"aiohttp failed for GraphQL query: {e}")
            # Fall back on non-async requests
            try:
                async with self.semaphore:
                    r_requests = await asyncio.to_thread(
                        requests.post,
                        "https://api.github.com/graphql",
                        headers=headers,
                        json={"query": generated_query},
                    )
                    result = r_requests.json()
                    if result is not None:
                        return result
            except Exception as e2:
                print(f"requests fallback also failed for GraphQL query: {e2}")
        return dict()

    async def query_rest(self, path: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the REST API
        :param path: API path to query
        :param params: Query parameters to be passed to the API
        :return: deserialized REST JSON output
        """

        for _ in range(60):
            headers = {
                "Authorization": f"token {self.access_token}",
            }
            if params is None:
                params = dict()
            if path.startswith("/"):
                path = path[1:]
            try:
                async with self.semaphore:
                    r_async = await self.session.get(
                        f"https://api.github.com/{path}",
                        headers=headers,
                        params=tuple(params.items()),
                    )
                if r_async.status == 202:
                    print(f"A path returned 202. Retrying...")
                    await asyncio.sleep(2)
                    continue

                result = await r_async.json()
                if result is not None:
                    return result
            except Exception as e:
                print(f"aiohttp failed for REST query: {e}")
                # Fall back on non-async requests
                try:
                    async with self.semaphore:
                        r_requests = await asyncio.to_thread(
                            requests.get,
                            f"https://api.github.com/{path}",
                            headers=headers,
                            params=tuple(params.items()),
                        )
                    if r_requests.status_code == 202:
                        print(f"A path returned 202. Retrying...")
                        await asyncio.sleep(2)
                        continue
                    elif r_requests.status_code == 200:
                        return r_requests.json()
                except Exception as e2:
                    print(f"requests fallback also failed for REST query: {e2}")
        # print(f"There were too many 202s. Data for {path} will be incomplete.")
        print("There were too many 202s. Data for this repository will be incomplete.")
        return dict()

    @staticmethod
    def repos_overview(
        contrib_cursor: Optional[str] = None, owned_cursor: Optional[str] = None
    ) -> str:
        """
        :return: GraphQL query with overview of user repositories
        """
        return f"""{{
  viewer {{
    login,
    name,
    repositories(
        first: 100,
        orderBy: {{
            field: UPDATED_AT,
            direction: DESC
        }},
        isFork: false,
        after: {"null" if owned_cursor is None else '"'+ owned_cursor +'"'}
    ) {{
      pageInfo {{
        hasNextPage
        endCursor
      }}
      nodes {{
        nameWithOwner
        stargazers {{
          totalCount
        }}
        forkCount
        languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{
          edges {{
            size
            node {{
              name
              color
            }}
          }}
        }}
      }}
    }}
    repositoriesContributedTo(
        first: 100,
        includeUserRepositories: false,
        orderBy: {{
            field: UPDATED_AT,
            direction: DESC
        }},
        contributionTypes: [
            COMMIT,
            PULL_REQUEST,
            REPOSITORY,
            PULL_REQUEST_REVIEW
        ]
        after: {"null" if contrib_cursor is None else '"'+ contrib_cursor +'"'}
    ) {{
      pageInfo {{
        hasNextPage
        endCursor
      }}
      nodes {{
        nameWithOwner
        stargazers {{
          totalCount
        }}
        forkCount
        languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{
          edges {{
            size
            node {{
              name
              color
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""

    @staticmethod
    def contrib_years() -> str:
        """
        :return: GraphQL query to get all years the user has been a contributor
        """
        return """
query {
  viewer {
    contributionsCollection {
      contributionYears
    }
  }
}
"""

    @staticmethod
    def contribs_by_year(year: str) -> str:
        """
        :param year: year to query for
        :return: portion of a GraphQL query with desired info for a given year
        """
        return f"""
    year{year}: contributionsCollection(
        from: "{year}-01-01T00:00:00Z",
        to: "{int(year) + 1}-01-01T00:00:00Z"
    ) {{
      contributionCalendar {{
        totalContributions
      }}
    }}
"""

    @classmethod
    def all_contribs(cls, years: List[str]) -> str:
        """
        :param years: list of years to get contributions for
        :return: query to retrieve contribution information for all user years
        """
        by_years = "\n".join(map(cls.contribs_by_year, years))
        return f"""
query {{
  viewer {{
    {by_years}
  }}
}}
"""

    @staticmethod
    def profile_info() -> str:
        """
        :return: GraphQL query to get profile-level statistics
        """
        return """
query {
  viewer {
    followers { totalCount }
    following { totalCount }
    createdAt
    pullRequests { totalCount }
    issues { totalCount }
  }
}
"""


class Stats(object):
    """
    Retrieve and store statistics about GitHub usage.
    """

    def __init__(
        self,
        username: str,
        access_token: str,
        session: aiohttp.ClientSession,
        exclude_repos: Optional[Set] = None,
        exclude_langs: Optional[Set] = None,
        ignore_forked_repos: bool = False,
    ):
        self.username = username
        self._ignore_forked_repos = ignore_forked_repos
        self._exclude_repos = set() if exclude_repos is None else exclude_repos
        self._exclude_langs = set() if exclude_langs is None else exclude_langs
        self.queries = Queries(username, access_token, session)

        self._name: Optional[str] = None
        self._stargazers: Optional[int] = None
        self._forks: Optional[int] = None
        self._total_contributions: Optional[int] = None
        self._languages: Optional[Dict[str, Any]] = None
        self._repos: Optional[Set[str]] = None
        self._lines_changed: Optional[Tuple[int, int]] = None
        self._views: Optional[int] = None
        self._pull_requests: Optional[int] = None
        self._issues_count: Optional[int] = None
        self._followers: Optional[int] = None
        self._following: Optional[int] = None
        self._joined_at: Optional[str] = None
        self._contribs_by_year: Optional[Dict[str, int]] = None
        self._top_repos: Optional[List[Dict]] = None
        self._stats_loaded = False
        self._profile_info_loaded = False
        self._total_contributions_loaded = False
        self._stats_lock = asyncio.Lock()
        self._profile_info_lock = asyncio.Lock()
        self._total_contributions_lock = asyncio.Lock()

    async def to_str(self) -> str:
        """
        :return: summary of all available statistics
        """
        languages = await self.languages_proportional
        formatted_languages = "\n  - ".join(
            [f"{k}: {v:0.4f}%" for k, v in languages.items()]
        )
        lines_changed = await self.lines_changed
        return f"""Name: {await self.name}
Stargazers: {await self.stargazers:,}
Forks: {await self.forks:,}
All-time contributions: {await self.total_contributions:,}
Repositories with contributions: {len(await self.repos)}
Lines of code added: {lines_changed[0]:,}
Lines of code deleted: {lines_changed[1]:,}
Lines of code changed: {lines_changed[0] + lines_changed[1]:,}
Project page views: {await self.views:,}
Followers: {await self.followers:,}
Following: {await self.following:,}
Pull Requests: {await self.pull_requests:,}
Issues Opened: {await self.issues_count:,}
Member Since: {await self.joined_at}
Languages:
  - {formatted_languages}"""

    async def get_stats(self) -> None:
        """
        Get lots of summary statistics using one big query. Sets many attributes
        """
        stargazers = 0
        forks = 0
        languages: Dict[str, Any] = dict()
        repos_seen: Set[str] = set()
        profile_name: Optional[str] = None

        exclude_langs_lower = {x.lower() for x in self._exclude_langs}
        repos_data: List[Dict] = []

        next_owned = None
        next_contrib = None
        while True:
            raw_results = await self.queries.query(
                Queries.repos_overview(
                    owned_cursor=next_owned, contrib_cursor=next_contrib
                )
            )
            raw_results = raw_results if raw_results is not None else {}

            viewer = raw_results.get("data", {}).get("viewer", {})
            viewer_login = viewer.get("login")
            if viewer_login:
                self.username = viewer_login

            profile_name = viewer.get("name", None)
            if profile_name is None:
                profile_name = viewer.get("login", "No Name")

            contrib_repos = (
                raw_results.get("data", {})
                .get("viewer", {})
                .get("repositoriesContributedTo", {})
            )
            owned_repos = (
                raw_results.get("data", {}).get("viewer", {}).get("repositories", {})
            )

            repos = owned_repos.get("nodes", [])
            if not self._ignore_forked_repos:
                repos += contrib_repos.get("nodes", [])

            for repo in repos:
                if repo is None:
                    continue
                repo_name = repo.get("nameWithOwner")
                if repo_name in repos_seen or repo_name in self._exclude_repos:
                    continue
                repos_seen.add(repo_name)
                repo_stars = repo.get("stargazers", {}).get("totalCount", 0)
                stargazers += repo_stars
                forks += repo.get("forkCount", 0)
                repos_data.append({
                    "name": repo_name,
                    "stars": repo_stars,
                    "forks": repo.get("forkCount", 0),
                })

                for lang in repo.get("languages", {}).get("edges", []):
                    lang_name = lang.get("node", {}).get("name", "Other")
                    if lang_name.lower() in exclude_langs_lower:
                        continue
                    if lang_name in languages:
                        languages[lang_name]["size"] += lang.get("size", 0)
                        languages[lang_name]["occurrences"] += 1
                    else:
                        languages[lang_name] = {
                            "size": lang.get("size", 0),
                            "occurrences": 1,
                            "color": lang.get("node", {}).get("color"),
                        }

            if owned_repos.get("pageInfo", {}).get(
                "hasNextPage", False
            ) or contrib_repos.get("pageInfo", {}).get("hasNextPage", False):
                next_owned = owned_repos.get("pageInfo", {}).get(
                    "endCursor", next_owned
                )
                next_contrib = contrib_repos.get("pageInfo", {}).get(
                    "endCursor", next_contrib
                )
            else:
                break

        # TODO: Improve languages to scale by number of contributions to
        #       specific filetypes
        langs_total = sum(v.get("size", 0) for v in languages.values())
        if langs_total == 0:
            for v in languages.values():
                v["prop"] = 0
        else:
            for v in languages.values():
                v["prop"] = 100 * (v.get("size", 0) / langs_total)

        repos_data.sort(key=lambda r: r["stars"], reverse=True)
        self._name = profile_name
        self._stargazers = stargazers
        self._forks = forks
        self._languages = languages
        self._repos = repos_seen
        self._top_repos = repos_data[:5]
        self._stats_loaded = True

    async def _ensure_stats_loaded(self) -> None:
        if self._stats_loaded:
            return
        async with self._stats_lock:
            if self._stats_loaded:
                return
            await self.get_stats()

    async def _ensure_profile_info_loaded(self) -> None:
        if self._profile_info_loaded:
            return
        async with self._profile_info_lock:
            if self._profile_info_loaded:
                return
            await self.get_profile_info()

    async def _ensure_total_contributions_loaded(self) -> None:
        if self._total_contributions_loaded:
            return
        async with self._total_contributions_lock:
            if self._total_contributions_loaded:
                return
            await self._load_total_contributions()

    @property
    async def name(self) -> str:
        """
        :return: GitHub user's name (e.g., Jacob Strieb)
        """
        if self._stats_loaded:
            assert self._name is not None
            return self._name
        await self._ensure_stats_loaded()
        assert self._name is not None
        return self._name

    @property
    async def stargazers(self) -> int:
        """
        :return: total number of stargazers on user's repos
        """
        if self._stats_loaded:
            assert self._stargazers is not None
            return self._stargazers
        await self._ensure_stats_loaded()
        assert self._stargazers is not None
        return self._stargazers

    @property
    async def forks(self) -> int:
        """
        :return: total number of forks on user's repos
        """
        if self._stats_loaded:
            assert self._forks is not None
            return self._forks
        await self._ensure_stats_loaded()
        assert self._forks is not None
        return self._forks

    @property
    async def languages(self) -> Dict:
        """
        :return: summary of languages used by the user
        """
        if self._stats_loaded:
            assert self._languages is not None
            return self._languages
        await self._ensure_stats_loaded()
        assert self._languages is not None
        return self._languages

    @property
    async def languages_proportional(self) -> Dict:
        """
        :return: summary of languages used by the user, with proportional usage
        """
        await self._ensure_stats_loaded()
        assert self._languages is not None
        return {k: v.get("prop", 0) for (k, v) in self._languages.items()}

    @property
    async def repos(self) -> Set[str]:
        """
        :return: list of names of user's repos
        """
        if self._stats_loaded:
            assert self._repos is not None
            return self._repos
        await self._ensure_stats_loaded()
        assert self._repos is not None
        return self._repos

    async def _load_total_contributions(self) -> None:
        """
        Load the user's total contribution count and yearly breakdown.
        """
        years_list = (
            (await self.queries.query(Queries.contrib_years()))
            .get("data", {})
            .get("viewer", {})
            .get("contributionsCollection", {})
            .get("contributionYears", [])
        )
        total_contributions = 0
        contribs_by_year: Dict[str, int] = {}
        by_year_data = (
            (await self.queries.query(Queries.all_contribs(years_list)))
            .get("data", {})
            .get("viewer", {})
        )
        for key, year_data in by_year_data.items():
            count = year_data.get("contributionCalendar", {}).get("totalContributions", 0)
            total_contributions += count
            year = key.replace("year", "")
            contribs_by_year[year] = count
        self._total_contributions = total_contributions
        self._contribs_by_year = contribs_by_year
        self._total_contributions_loaded = True

    @property
    async def total_contributions(self) -> int:
        """
        :return: count of user's total contributions as defined by GitHub
        """
        if self._total_contributions_loaded:
            assert self._total_contributions is not None
            return self._total_contributions
        await self._ensure_total_contributions_loaded()
        assert self._total_contributions is not None
        return cast(int, self._total_contributions)

    @property
    async def lines_changed(self) -> Tuple[int, int]:
        """
        :return: count of total lines added, removed, or modified by the user
        """
        if self._lines_changed is not None:
            return self._lines_changed
        additions = 0
        deletions = 0
        for repo in await self.repos:
            r = await self.queries.query_rest(f"/repos/{repo}/stats/contributors")
            for author_obj in r:
                # Handle malformed response from the API by skipping this repo
                if not isinstance(author_obj, dict) or not isinstance(
                    author_obj.get("author", {}), dict
                ):
                    continue
                author = author_obj.get("author", {}).get("login", "")
                if author != self.username:
                    continue

                for week in author_obj.get("weeks", []):
                    additions += week.get("a", 0)
                    deletions += week.get("d", 0)

        self._lines_changed = (additions, deletions)
        return self._lines_changed

    @property
    async def views(self) -> int:
        """
        Note: only returns views for the last 14 days (as-per GitHub API)
        :return: total number of page views the user's projects have received
        """
        if self._views is not None:
            return self._views

        total = 0
        for repo in await self.repos:
            r = await self.queries.query_rest(f"/repos/{repo}/traffic/views")
            for view in r.get("views", []):
                total += view.get("count", 0)

        self._views = total
        return total

    async def get_profile_info(self) -> None:
        """
        Fetch profile-level stats: followers, following, PRs, issues, join date
        """
        result = await self.queries.query(Queries.profile_info())
        viewer = result.get("data", {}).get("viewer", {})
        followers = viewer.get("followers", {}).get("totalCount", 0)
        following = viewer.get("following", {}).get("totalCount", 0)
        pull_requests = viewer.get("pullRequests", {}).get("totalCount", 0)
        issues_count = viewer.get("issues", {}).get("totalCount", 0)
        raw_date = viewer.get("createdAt", "")
        joined_at = "N/A"
        if raw_date:
            try:
                joined_at = datetime.fromisoformat(
                    raw_date.replace("Z", "+00:00")
                ).strftime("%Y")
            except ValueError:
                joined_at = raw_date[:4]

        self._followers = followers
        self._following = following
        self._pull_requests = pull_requests
        self._issues_count = issues_count
        self._joined_at = joined_at
        self._profile_info_loaded = True

    @property
    async def followers(self) -> int:
        """
        :return: number of followers the user has
        """
        if self._profile_info_loaded:
            assert self._followers is not None
            return self._followers
        await self._ensure_profile_info_loaded()
        assert self._followers is not None
        return self._followers

    @property
    async def following(self) -> int:
        """
        :return: number of users this user is following
        """
        if self._profile_info_loaded:
            assert self._following is not None
            return self._following
        await self._ensure_profile_info_loaded()
        assert self._following is not None
        return self._following

    @property
    async def pull_requests(self) -> int:
        """
        :return: total number of pull requests opened by the user
        """
        if self._profile_info_loaded:
            assert self._pull_requests is not None
            return self._pull_requests
        await self._ensure_profile_info_loaded()
        assert self._pull_requests is not None
        return self._pull_requests

    @property
    async def issues_count(self) -> int:
        """
        :return: total number of issues opened by the user
        """
        if self._profile_info_loaded:
            assert self._issues_count is not None
            return self._issues_count
        await self._ensure_profile_info_loaded()
        assert self._issues_count is not None
        return self._issues_count

    @property
    async def joined_at(self) -> str:
        """
        :return: year the user joined GitHub
        """
        if self._profile_info_loaded:
            assert self._joined_at is not None
            return self._joined_at
        await self._ensure_profile_info_loaded()
        assert self._joined_at is not None
        return self._joined_at

    @property
    async def contribs_by_year(self) -> Dict[str, int]:
        """
        :return: dict mapping year string to contribution count for that year
        """
        if self._total_contributions_loaded:
            assert self._contribs_by_year is not None
            return self._contribs_by_year
        await self._ensure_total_contributions_loaded()
        assert self._contribs_by_year is not None
        return self._contribs_by_year

    @property
    async def top_repos(self) -> List[Dict]:
        """
        :return: list of top repos by star count (up to 5), each with name/stars/forks
        """
        if self._stats_loaded:
            assert self._top_repos is not None
            return self._top_repos
        await self._ensure_stats_loaded()
        assert self._top_repos is not None
        return self._top_repos


###############################################################################
# Main Function
###############################################################################


async def main() -> None:
    """
    Used mostly for testing; this module is not usually run standalone
    """
    access_token = os.getenv("ACCESS_TOKEN")
    user = os.getenv("GITHUB_ACTOR")
    if access_token is None or user is None:
        raise RuntimeError(
            "ACCESS_TOKEN and GITHUB_ACTOR environment variables cannot be None!"
        )
    async with aiohttp.ClientSession() as session:
        s = Stats(user, access_token, session)
        print(await s.to_str())


if __name__ == "__main__":
    asyncio.run(main())
