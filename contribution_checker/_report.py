# SPDX-FileCopyrightText: 2023 DB Systel GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Dataclass holding the analysis of the repository"""

import json
import logging
from dataclasses import asdict, dataclass, field


@dataclass
class RepoReport:  # pylint: disable=too-many-instance-attributes
    """Data class that holds a report about a repository"""

    schema_version: str = "1.0"  # version for the JSON schema in case we introduce breaking changes
    path: str = ""
    commits_total: int = 0
    matched_total: int = 0
    matched_newest: str = ""
    matched_oldest: str = ""
    matched_unique_authors: int = 0
    matched_commit_data: list = field(default_factory=list)


def print_report(report: RepoReport) -> None:
    """Pretty print the report, based on the dataclass"""
    logging.debug("Report class content to be printed: %s", report)
    report_dict = asdict(report)
    print(json.dumps(report_dict, indent=2))
