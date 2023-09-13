# SPDX-FileCopyrightText: 2023 DB Systel GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Misc helper functions"""

import logging
import os
import re
from shutil import rmtree

from git import GitCommandError, RemoteProgress, Repo
from platformdirs import user_cache_path
from tqdm import tqdm


class CloneProgress(RemoteProgress):
    """Clone progress bar"""

    def __init__(self):
        super().__init__()
        self.progbar = tqdm()
        self.progbar.write("Cloning repository...")

    def __call__(self, op_code, cur_count, max_count=None, message=""):
        self.progbar.total = max_count
        self.progbar.n = cur_count
        self.progbar.refresh()


def url_to_dirname(url: str) -> str:
    """Shorten and escape a repository URL so it can be used as a directory name"""
    # Remove http schema
    url = re.sub(r"^https?://", "", url)
    # Replace disallowed characters with underscores
    unix_escaped = re.sub(r"[^a-zA-Z0-9\-_]", "_", url)
    # Windows has some more limitations
    win_escaped = re.sub(r'[\\/:*?"<>|]', "_", unix_escaped)
    # Trim or truncate the name if it's too long (Windows limit: 260 characters)
    return win_escaped[:260]


def clean_cache() -> None:
    """Clean the whole cache directory"""
    cache_dir = user_cache_path("contribution-checker")
    try:
        rmtree(cache_dir)
        print("Cache cleaned")
    except FileNotFoundError:
        print("Cache directory does not exist")


def get_cache_dir(url: str) -> str:
    """Create/get a cache directory for the remote repository"""
    cachedir = os.path.join(user_cache_path("contribution-checker"), url_to_dirname(url))

    if not os.path.isdir(cachedir):
        logging.info("Creating cache directory: %s", cachedir)
        os.makedirs(cachedir)

    return cachedir


def clone_or_pull_repository(repo_url: str, local_path: str):
    """Clone a repository if local directory does not exist yet, or pull if it does"""
    # Local directory isn't empty so we assume it's been cached before
    if os.listdir(local_path):
        repo = Repo(local_path)
        if repo.head.is_detached or repo.is_dirty():
            logging.error(
                "HEAD of repository %s is detached or dirty. Did you make "
                "manual changes in the cached repository (%s)?",
                repo_url,
                local_path,
            )
        try:
            # fetch origin
            repo.remotes.origin.fetch()
            # reset --hard to origin/$branchname, assuming that the user did not
            # change the branch and that the project did not change their main
            # branch
            repo.git.reset(f"origin/{repo.head.ref}", "--hard")
        except (GitCommandError, TypeError) as exc:
            logging.error("Fetching and resetting to the newest commits failed: %s", exc)

        logging.info(
            "Repository already exists and has been successfully updated in %s", local_path
        )

    # Directory is empty, so probably a temp dir or first-time cache
    else:
        repo = Repo.clone_from(url=repo_url, to_path=local_path, progress=CloneProgress())
        logging.info(
            "Repository didn't exist yet locally and has been successfully cloned to %s",
            local_path,
        )
