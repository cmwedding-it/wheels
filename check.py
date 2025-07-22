#/usr/bin/env python3

import os
import re
import sys
import requests

from datetime import datetime


def get_release_version(repository: str) -> str: 
    try:
        return requests.get(f"https://api.github.com/repos/{repository}/releases/latest").json()["tag_name"].removeprefix("v")
    except Exception:
        return requests.get(f"https://api.github.com/repos/{repository}/tags").json()[0]["name"].removeprefix("v")


def get_unstable_version(repository: str, branch: str) -> str:
    base_url = f"https://api.github.com/repos/{repository}/commits?sha={branch}"

    latest_commit = requests.get(f"{base_url}&per_page=1").json()[0]
    commit_date = datetime.strptime(latest_commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")

    since_iso = commit_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z")
    
    commit_count = 0
    page = 1
    
    while True:
        commits = requests.get(f"{base_url}&since={since_iso}&per_page=100&page={page}").json()
        commit_count += len(commits)

        if len(commits) < 100:
            break
        
        page += 1

    return f"{branch}.{commit_date.strftime("%Y%m%d")}.dev{commit_count}"


def does_pypi_version_exist(base_url: str, package: str, version: str) -> bool:
    base_url = base_url.removesuffix("/")
    version = version.replace(".", "\\.")

    body = requests.get(f"{base_url}/simple/{package}").text
    return len(re.findall(rf"<a href=\".+\">{package}-{version}-.+</a>", body, re.MULTILINE)) > 0


def main():
    package = os.environ["PACKAGE"]
    base_url = os.environ["BASE_URL"]
    repository = os.environ["REPOSITORY"]

    version = get_release_version(repository) if not os.environ.get("BRANCH", False) else get_unstable_version(repository, os.environ["BRANCH"]) 
    
    if does_pypi_version_exist(base_url, package, version):
        sys.exit(0)

    print(f"version={version}")


if __name__ == "__main__":
    main()

