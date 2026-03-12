#!/usr/bin/python3

import asyncio
import os
from html import escape

import aiohttp

from github_stats import Stats


################################################################################
# Helper Functions
################################################################################


def generate_output_folder() -> None:
    """
    Create the output folder if it does not already exist
    """
    if not os.path.isdir("generated"):
        os.mkdir("generated")


def escape_text(value: str) -> str:
    """
    Escape dynamic text before embedding it into SVG/XHTML templates.
    """
    return escape(value, quote=False)


################################################################################
# Individual Image Generation Functions
################################################################################


async def generate_overview(s: Stats) -> None:
    """
    Generate an SVG badge with summary statistics
    :param s: Represents user's GitHub statistics
    """
    with open("templates/overview.svg", "r") as f:
        output = f.read()

    output = output.replace("{{ name }}", escape_text(await s.name))
    output = output.replace("{{ stars }}", f"{await s.stargazers:,}")
    output = output.replace("{{ forks }}", f"{await s.forks:,}")
    output = output.replace("{{ contributions }}", f"{await s.total_contributions:,}")
    lines_changed = await s.lines_changed
    output = output.replace("{{ lines_added }}", f"{lines_changed[0]:,}")
    output = output.replace("{{ lines_deleted }}", f"{lines_changed[1]:,}")
    output = output.replace("{{ views }}", f"{await s.views:,}")
    output = output.replace("{{ repos }}", f"{len(await s.repos):,}")

    generate_output_folder()
    with open("generated/overview.svg", "w") as f:
        f.write(output)


async def generate_languages(s: Stats) -> None:
    """
    Generate an SVG badge with summary languages used
    :param s: Represents user's GitHub statistics
    """
    with open("templates/languages.svg", "r") as f:
        output = f.read()

    progress = ""
    lang_list = ""
    sorted_languages = sorted(
        (await s.languages).items(), reverse=True, key=lambda t: t[1].get("size")
    )
    delay_between = 150
    for i, (lang, data) in enumerate(sorted_languages):
        color = data.get("color")
        color = color if color is not None else "#000000"
        progress += (
            f'<span style="background-color: {color};'
            f'width: {data.get("prop", 0):0.3f}%;" '
            f'class="progress-item"></span>'
        )
        lang_list += f"""
<li style="animation-delay: {i * delay_between}ms;">
<svg xmlns="http://www.w3.org/2000/svg" class="octicon" style="fill:{color};"
viewBox="0 0 16 16" version="1.1" width="16" height="16"><path
fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8z"></path></svg>
<span class="lang">{escape_text(lang)}</span>
<span class="percent">{data.get("prop", 0):0.2f}%</span>
</li>

"""

    output = output.replace("{{ progress }}", progress)
    output = output.replace("{{ lang_list }}", lang_list)

    generate_output_folder()
    with open("generated/languages.svg", "w") as f:
        f.write(output)


async def generate_profile(s: Stats) -> None:
    """
    Generate an SVG badge with profile-level statistics
    :param s: Represents user's GitHub statistics
    """
    with open("templates/profile.svg", "r") as f:
        output = f.read()

    output = output.replace("{{ name }}", escape_text(await s.name))
    output = output.replace("{{ followers }}", f"{await s.followers:,}")
    output = output.replace("{{ following }}", f"{await s.following:,}")
    output = output.replace("{{ pull_requests }}", f"{await s.pull_requests:,}")
    output = output.replace("{{ issues }}", f"{await s.issues_count:,}")
    output = output.replace("{{ joined }}", escape_text(await s.joined_at))

    generate_output_folder()
    with open("generated/profile.svg", "w") as f:
        f.write(output)


async def generate_contributions(s: Stats) -> None:
    """
    Generate an SVG badge with yearly contribution history
    :param s: Represents user's GitHub statistics
    """
    with open("templates/contributions.svg", "r") as f:
        output = f.read()

    contribs = await s.contribs_by_year
    # Sort by year descending, show most recent 7
    sorted_years = sorted(contribs.items(), key=lambda t: t[0], reverse=True)[:7]

    # Compute max for the relative bar widths
    max_count = max(1, max((v for _, v in sorted_years), default=0))

    rows = ""
    for i, (year, count) in enumerate(sorted_years):
        pct = 100 * count / max_count
        rows += f"""
<tr style="animation-delay: {i * 80}ms">
  <td>{escape_text(year)}</td>
  <td class="bar-cell">
    <div class="bar-bg">
      <div class="bar-fill" style="width:{pct:.1f}%;"></div>
    </div>
  </td>
  <td class="value">{count:,}</td>
</tr>
"""

    output = output.replace("{{ contrib_rows }}", rows)
    output = output.replace("{{ total_contributions }}", f"{await s.total_contributions:,}")

    generate_output_folder()
    with open("generated/contributions.svg", "w") as f:
        f.write(output)


async def generate_top_repos(s: Stats) -> None:
    """
    Generate an SVG badge showing top repositories by star count
    :param s: Represents user's GitHub statistics
    """
    with open("templates/top-repos.svg", "r") as f:
        output = f.read()

    top = await s.top_repos
    rows = ""
    for i, repo in enumerate(top):
        name = escape_text(str(repo["name"]))
        stars = repo["stars"]
        forks = repo["forks"]
        rows += f"""
<tr style="animation-delay: {i * 80}ms">
  <td class="repo-name">{name}</td>
  <td class="repo-meta">
    <svg class="octicon star-icon" viewBox="0 0 16 16" width="12" height="12"
    xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 .25a.75.75 0
    01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719
    4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0
    01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75
    0 018 .25z"></path></svg>
    {stars:,}
    &#160;
    <svg class="octicon" viewBox="0 0 16 16" width="12" height="12"
    xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M5
    3.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm0 2.122a2.25 2.25 0
    10-1.5 0v.878A2.25 2.25 0 005.75 8.5h1.5v2.128a2.251 2.251 0
    101.5 0V8.5h1.5a2.25 2.25 0
    002.25-2.25v-.878a2.25 2.25 0
    10-1.5 0v.878a.75.75 0
    01-.75.75h-4.5A.75.75 0 015
    6.25v-.878zm3.75 7.378a.75.75 0
    11-1.5 0 .75.75 0 011.5
    0zm3-8.75a.75.75 0 100-1.5.75.75 0 000 1.5z"></path></svg>
    {forks:,}
  </td>
</tr>
"""

    output = output.replace("{{ repo_rows }}", rows)

    generate_output_folder()
    with open("generated/top-repos.svg", "w") as f:
        f.write(output)


################################################################################
# Main Function
################################################################################


async def main() -> None:
    """
    Generate all badges
    """
    access_token = os.getenv("ACCESS_TOKEN")
    if not access_token:
        # access_token = os.getenv("GITHUB_TOKEN")
        raise Exception("A personal access token is required to proceed!")
    user = os.getenv("GITHUB_ACTOR")
    if user is None:
        raise RuntimeError("Environment variable GITHUB_ACTOR must be set.")
    exclude_repos = os.getenv("EXCLUDED")
    excluded_repos = (
        {x.strip() for x in exclude_repos.split(",")} if exclude_repos else None
    )
    exclude_langs = os.getenv("EXCLUDED_LANGS")
    excluded_langs = (
        {x.strip() for x in exclude_langs.split(",")} if exclude_langs else None
    )
    # Convert a truthy value to a Boolean
    raw_ignore_forked_repos = os.getenv("EXCLUDE_FORKED_REPOS")
    ignore_forked_repos = (
        not not raw_ignore_forked_repos
        and raw_ignore_forked_repos.strip().lower() != "false"
    )
    async with aiohttp.ClientSession() as session:
        s = Stats(
            user,
            access_token,
            session,
            exclude_repos=excluded_repos,
            exclude_langs=excluded_langs,
            ignore_forked_repos=ignore_forked_repos,
        )
        await asyncio.gather(
            generate_languages(s),
            generate_overview(s),
            generate_profile(s),
            generate_contributions(s),
            generate_top_repos(s),
        )


if __name__ == "__main__":
    asyncio.run(main())
