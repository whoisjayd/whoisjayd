"""Modern async GitHub API client."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import aiohttp


class WakaTimeClient:
    """Async WakaTime API client."""

    BASE_URL = "https://wakatime.com/api/v1"

    def __init__(
        self,
        api_key: str,
        session: aiohttp.ClientSession,
        max_connections: int = 5,
    ):
        self.api_key = api_key
        self.session = session
        self.semaphore = asyncio.Semaphore(max_connections)

    async def _get(self, endpoint: str) -> Dict[str, Any]:
        """Execute a GET request to the WakaTime API."""
        url = f"{self.BASE_URL}{endpoint}"
        params = {"api_key": self.api_key}

        async with self.semaphore:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return data if data is not None else {}

    async def get_stats(self, range_: str = "last_7_days") -> Dict[str, Any]:
        """Get WakaTime stats for the given time range."""
        return await self._get(f"/users/current/stats/{range_}")

    async def get_all_time(self) -> Dict[str, Any]:
        """Get all-time WakaTime stats."""
        return await self._get("/users/current/all_time_since_today")


class GitHubClient:
    """Async GitHub GraphQL (v4) and REST (v3) client."""

    GRAPHQL_URL = "https://api.github.com/graphql"
    REST_URL = "https://api.github.com"

    def __init__(
        self,
        access_token: str,
        session: aiohttp.ClientSession,
        max_connections: int = 10,
    ):
        self.access_token = access_token
        self.session = session
        self.semaphore = asyncio.Semaphore(max_connections)

    async def graphql(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a GraphQL query and return the JSON response."""
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        headers = {"Authorization": f"Bearer {self.access_token}"}

        async with self.semaphore:
            async with self.session.post(
                self.GRAPHQL_URL,
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                data = await response.json()

        if data is None:
            return {}

        if "errors" in data:
            for error in data["errors"]:
                print(f"GraphQL error: {error.get('message', error)}")

        return data

    async def rest(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 5,
    ) -> Dict[str, Any]:
        """Execute a REST API GET request with retry logic."""
        if path.startswith("/"):
            path = path[1:]

        headers = {"Authorization": f"token {self.access_token}"}
        url = f"{self.REST_URL}/{path}"
        query_params = tuple(params.items()) if params else ()

        for attempt in range(max_retries):
            async with self.semaphore:
                async with self.session.get(
                    url,
                    headers=headers,
                    params=query_params,
                ) as response:
                    if response.status == 202:
                        # GitHub is computing stats; retry after delay
                        wait = 2 + attempt * 2
                        print(f"REST 202 for {path}, retrying in {wait}s...")
                        await asyncio.sleep(wait)
                        continue

                    response.raise_for_status()
                    data = await response.json()
                    return data if data is not None else {}

        print(f"REST query failed after {max_retries} retries: {path}")
        return {}
