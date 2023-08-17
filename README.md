<!--
SPDX-FileCopyrightText: 2023 DB Systel GmbH

SPDX-License-Identifier: Apache-2.0
-->

# Contribution Checker

[![Test suites](https://github.com/dbschenker/contribution-checker/actions/workflows/test.yaml/badge.svg)](https://github.com/dbschenker/contribution-checker/actions/workflows/test.yaml)
<!-- TODO: Add REUSE API badge once public -->

Check for all commits matching a certain email address pattern in a local or
remote Git repository. Useful for creating statistics about contributions by a
certain organisation in selected projects.

## Requirements

* `python` >= 3.9
* `poetry` >= 1.1.0

## Usage

We recommend to run this tool via `poetry` that takes care of installing the
correct dependencies in a clean encironment.

You can find all supported flags by running `poetry run contribution-checker --help`.

Basic examples are:

```bash
# Check a remote repository for DB authors
poetry run contribution-checker -e ".*@deutschebahn.com" -r https://github.com/dbsystel/playground
# Check a remote repository for DB authors and plot the results
poetry run contribution-checker -e ".*@deutschebahn.com" -r https://github.com/fsfe/reuse-tool --plot
# Check a local repository for DB authors
poetry run contribution-checker -e ".*@deutschebahn.com" -d ../Git/dbsystel-playground
```

The output is JSON and could look like the following:

```json
{
  "schema_version": "1.0",
  "path": "https://github.com/fsfe/reuse-tool",
  "commits_total": 1860,
  "matched_total": 12,
  "matched_newest": [
    "2023-06-22T12:59:39",
    "1 files, +7 lines, -2 lines"
  ],
  "matched_oldest": [
    "2023-01-19T10:10:52",
    "1 files, +3 lines, -0 lines"
  ],
  "matched_unique_authors": 1,
  "matched_commit_data": [
    [
      "2023-06-22T12:59:39",
      "1 files, +7 lines, -2 lines"
    ],
    [
      "2023-06-22T09:45:24",
      "5 files, +385 lines, -10 lines"
    ],
    [
      "redacted to save space",
      "..."
    ],
  ]
}
```

## License and copyright

The content of this repository is licensed under the [Apache 2.0
license](https://www.apache.org/licenses/LICENSE-2.0).

This repository is [REUSE](https://reuse.software) compliant. You can find
licensing and copyright information for each file in the file header or
accompying files.

The project has been started as a collaboration between DB Systel GmbH and DB
Schenker. [We welcome contributions from everyone](CONTRIBUTING.md).
