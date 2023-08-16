# SPDX-FileCopyrightText: 2023 DB Systel GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Misc helper functions"""

import logging
import os
import re

from git import Repo
from platformdirs import user_cache_path


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
        repo.remotes.origin.pull()
        logging.info(
            "Repository already exists and has been successfully updated in %s", local_path
        )

    # Directory is empty, so probably a temp dir or first-time cache
    else:
        repo = Repo.clone_from(url=repo_url, to_path=local_path)
        logging.info(
            "Repository didn't exist yet locally and has been successfully cloned to %s",
            local_path,
        )
