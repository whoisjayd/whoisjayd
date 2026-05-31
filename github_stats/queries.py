"""GraphQL query definitions for GitHub statistics."""

from __future__ import annotations

from typing import List, Optional


def repos_overview(
    owned_cursor: Optional[str] = None,
    contrib_cursor: Optional[str] = None,
) -> str:
    """GraphQL query for repository overview with languages."""
    owned_after = "null" if owned_cursor is None else f'"{owned_cursor}"'
    contrib_after = "null" if contrib_cursor is None else f'"{contrib_cursor}"'
    return f"""{{
  viewer {{
    login
    name
    repositories(
      first: 100
      orderBy: {{ field: UPDATED_AT, direction: DESC }}
      isFork: false
      after: {owned_after}
    ) {{
      pageInfo {{
        hasNextPage
        endCursor
      }}
      nodes {{
        nameWithOwner
        isPrivate
        stargazers {{ totalCount }}
        forkCount
        languages(first: 10, orderBy: {{ field: SIZE, direction: DESC }}) {{
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
      first: 100
      includeUserRepositories: false
      orderBy: {{ field: UPDATED_AT, direction: DESC }}
      contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY, PULL_REQUEST_REVIEW]
      after: {contrib_after}
    ) {{
      pageInfo {{
        hasNextPage
        endCursor
      }}
      nodes {{
        nameWithOwner
        isPrivate
        stargazers {{ totalCount }}
        forkCount
        languages(first: 10, orderBy: {{ field: SIZE, direction: DESC }}) {{
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
}}"""


def contrib_years() -> str:
    """GraphQL query to get contribution years."""
    return """
query {
  viewer {
    contributionsCollection {
      contributionYears
    }
  }
}
"""


def _contrib_by_year(year: str) -> str:
    """Fragment for contributions in a single year."""
    next_year = int(year) + 1
    return f"""
    year{year}: contributionsCollection(
      from: "{year}-01-01T00:00:00Z"
      to: "{next_year}-01-01T00:00:00Z"
    ) {{
      contributionCalendar {{
        totalContributions
      }}
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
    }}"""


def all_contribs(years: List[str]) -> str:
    """GraphQL query for contributions across all years."""
    by_years = "\n".join(_contrib_by_year(y) for y in years)
    return f"""query {{
  viewer {{
    {by_years}
  }}
}}"""


def profile_info() -> str:
    """GraphQL query for profile statistics with modern fields."""
    return """
query {
  viewer {
    login
    name
    bio
    company
    location
    websiteUrl
    twitterUsername
    followers { totalCount }
    following { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    createdAt
    gists(privacy: PUBLIC) { totalCount }
    starredRepositories { totalCount }
    packages { totalCount }
    repositoryDiscussions { totalCount }
    watching { totalCount }
    socialAccounts(first: 10) {
      nodes {
        provider
        url
      }
    }
  }
}
"""
