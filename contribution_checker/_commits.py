# SPDX-FileCopyrightText: 2023 DB Systel GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Functions for extracting and analysing commits"""

import logging
import re
import tempfile
from datetime import datetime

from git import Repo, exc

from contribution_checker._helper import clone_or_pull_repository, get_cache_dir
from contribution_checker._report import RepoReport


def extract_matching_commits(report: RepoReport, repoinfo: dict, pattern: str) -> list:
    """Clone a repository and get all its commits"""

    # Remote repository, clone into temp directory
    if repoinfo["remote"]:
        logging.info("Using remote repository: %s", repoinfo["path"])

        # Define path the remote repository shall be cloned to
        if repoinfo["cache"]:
            repodir = get_cache_dir(repoinfo["path"])
        else:
            repodir_object = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
            repodir = repodir_object.name

        clone_or_pull_repository(repoinfo["path"], repodir)

    # Local directory
    else:
        logging.info("Using local Git repository %s", repoinfo["path"])
        repodir = repoinfo["path"]

    repo = Repo(path=repodir)

    all_commits = _extract_all_commits(report, repo)

    matched_commits = _find_commit_matches(repo, all_commits, pattern)

    # Delete temporary directory if it has been created
    if not repoinfo["cache"]:
        logging.info("Deleting temporary directory in which remote repository has been cloned to")
        repodir_object.cleanup()

    return matched_commits


def _extract_all_commits(report: RepoReport, repo: Repo) -> list:
    """Extract all commits from a local Git repository"""
    mainbranch = repo.head.reference

    commits = list(repo.iter_commits(rev=mainbranch))
    report.commits_total = len(commits)

    # Get a list of all commits of the repo
    return [
        {
            "name": str(c.author),
            "email": c.author.email,
            "msg": c.message,
            "unixdate": c.authored_date,
            "hash": c.hexsha,
            "changes": {},
        }
        for c in commits
    ]


def _find_commit_matches(repo: Repo, commits: list, pattern: str) -> list:
    """Go through each commit and check for pattern. If positive, add to list"""
    matched_commits = []
    pattern_re = re.compile(pattern)

    for commit in commits:
        if pattern_re.match(commit["email"]):
            logging.debug(
                "Commit %s by author '%s' matches pattern", commit["hash"], commit["email"]
            )
            # Extract stats for this commit
            files = []
            added = 0
            removed = 0
            try:
                diff = repo.git.diff("--numstat", f"{commit['hash']}~1", commit["hash"])
            except exc.GitCommandError:
                # Most likely happens if commit is the first in the repo
                # In this case, 4b825dc642cb6eb9a060e54bf8d69288fbee4904 is empty object tree
                diff = repo.git.diff(
                    "--numstat", "4b825dc642cb6eb9a060e54bf8d69288fbee4904", commit["hash"]
                )

            for line in diff.split("\n"):
                match = re.match(r"(\d+)\s+(\d+)\s+(.+)", line)
                if match:
                    files.append(match[3])
                    added += int(match[1])
                    removed += int(match[2])

            commit["changes"] = {
                "files": len(files),
                "added": added,
                "removed": removed,
            }

            # Append commit to list
            matched_commits.append(commit)
        else:
            logging.debug(
                "Commit %s by author '%s' does not match pattern", commit["hash"], commit["email"]
            )

    logging.info("Found %s commits matching given pattern", len(matched_commits))

    return matched_commits


def get_commit_data(report: RepoReport, commits: list) -> list:
    """Extract commit dates"""
    commit_data = []
    for commit in commits:
        date = datetime.utcfromtimestamp(commit["unixdate"]).isoformat()
        stats = (
            f"{commit['changes']['files']} files, "
            f"+{commit['changes']['added']} lines, "
            f"-{commit['changes']['removed']} lines"
        )
        commit_data.append([date, stats])

    report.matched_commit_data = commit_data

    return commit_data


def get_unique_authors(report: RepoReport, commits: list) -> None:
    """Get amount of unique committers in the list of matched commits"""
    # Get all unique emails (lowercased) from all given commits
    emails = {c["email"].lower() for c in commits if "email" in c}

    logging.debug("Found %s unique emails matching pattern: %s", len(emails), emails)

    report.matched_unique_authors = len(emails)
