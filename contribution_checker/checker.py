#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 DB Systel GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Check for contributions matching a certain pattern in repositories"""

import argparse
import logging

from contribution_checker._commits import (
    extract_matching_commits,
    get_commit_data,
    get_unique_authors,
)
from contribution_checker._plot import plot_commits
from contribution_checker._report import RepoReport, print_report

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Also print INFO output",
)
parser.add_argument(
    "--debug",
    action="store_true",
    help="Also print DEBUG output. Includes --verbose",
)
parser.add_argument(
    "-e",
    "--email",
    default="",
    help=(
        "Pattern for email addresses that shall be searched for in commits. "
        "Can be any Python regex, e.g.: .*@deutschebahn.com"
    ),
)
parser.add_argument(
    "-p",
    "--plot",
    action="store_true",
    help="Show plot of commits",
)
parser.add_argument(
    "-c",
    "--cache",
    action="store_true",
    help="Cache cloned remote repositories to speed up subsequent checks",
)
# Mutually exclusive arguments, but at least one required
parser_repotype = parser.add_mutually_exclusive_group(required=True)
parser_repotype.add_argument(
    "-r",
    "--repository",
    dest="repourl",
    help=(
        "A single Git repository URL to clone and check. "
        "Example: -r https://github.com/db-ui/core.git"
    ),
)
parser_repotype.add_argument(
    "-d",
    "--directory",
    dest="repodir",
    help=("A single local directory to lint. Example: -d ../git/foo/bar"),
)


def configure_logger(args) -> logging.Logger:
    """Set logging options"""
    log = logging.getLogger()
    logging.basicConfig(
        encoding="utf-8",
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Set loglevel based on --verbose and --debug flag
    if args.debug:
        log.setLevel(logging.DEBUG)
    elif args.verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARN)

    return log


def analyse_dates(report: RepoReport, dates: list) -> None:
    """Do some analysis of the dates of given commits"""
    report.matched_total = len(dates)
    report.matched_oldest = min(dates)
    report.matched_newest = max(dates)


def main():
    """Main function"""
    args = parser.parse_args()

    # Set logger settings
    configure_logger(args=args)

    # Initialise the report dataclass
    report = RepoReport()

    # Define whether to clone a remote repo or use a local one, and if caching
    # should be applied
    repoinfo = {"path": "", "remote": False, "cache": False}
    if args.repourl:
        repoinfo["cache"] = args.cache
        repoinfo["path"] = args.repourl
        repoinfo["remote"] = True
    else:
        repoinfo["path"] = args.repodir

    # Get all commits from the project with certain fields
    # and extract commits that match the given pattern
    matched_commits = extract_matching_commits(report, repoinfo, args.email)

    # Identify the number of unique authors inside the matched commits
    get_unique_authors(report, matched_commits)

    # Extract the dates of the matched commits
    commit_data = get_commit_data(report, matched_commits)

    # Analyse the commit data, e.g. by dates
    analyse_dates(report, commit_data)

    # Print report to user
    print_report(report)

    if args.plot:
        plot_commits(report)


if __name__ == "__main__":
    main()
