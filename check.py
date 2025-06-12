#/usr/bin/env python3

import os
import re
import sys
import requests


def get_github_version(repository: str) -> str: 
    try:
        return requests.get(f"https://api.github.com/repos/{repository}/releases/latest").json()["tag_name"].removeprefix("v")
    except Exception:
        return requests.get(f"https://api.github.com/repos/{repository}/tags").json()[0]


def does_pypi_version_exist(base_url: str, package: str, version: str) -> bool:
    base_url = base_url.removesuffix("/")
    version = version.replace(".", "\\.")

    body = requests.get(f"{base_url}/simple/{package}").text
    return len(re.findall(rf"<a href=\".+\">{package}-{version}-.+</a>", body, re.MULTILINE)) > 0


def main():
    repository = os.environ["REPOSITORY"]
    package = os.environ["PACKAGE"]
    base_url = os.environ["BASE_URL"]

    version = get_github_version(repository)

    if does_pypi_version_exist(base_url, package, version):
        sys.exit(0)

    print(f"version=v{version}")


if __name__ == "__main__":
    main()

