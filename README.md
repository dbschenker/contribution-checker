<!--
SPDX-FileCopyrightText: 2023 DB Systel GmbH

SPDX-License-Identifier: Apache-2.0
-->

# Contribution Checker

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

You can find all supported flags by running `poetry run contribcheck --help`.

Basic examples are:

```bash
# Check a remote repository for DB authors
poetry run contribcheck -e ".*@deutschebahn.com" -r https://github.com/dbsystel/playground
# Check a remote repository for DB authors and plot the results
poetry run contribcheck -e ".*@deutschebahn.com" -r https://github.com/fsfe/reuse-tool --plot
# Check a local repository for DB authors
poetry run contribcheck -e ".*@deutschebahn.com" -d ../Git/dbsystel-playground
```

The output is JSON and could look like the following:

```json
{
  "commits_total": 32,
  "matched_total": 14,
  "matched_newest": [
    "2022-12-20T19:31:41",
    "24 files, +173 lines, -1 lines"
  ],
  "matched_oldest": [
    "2019-10-01T08:17:09",
    "1 files, +4 lines, -0 lines"
  ],
  "matched_unique_authors": 3,
  "matched_commit_data": [
    [
      "2022-12-20T19:31:41",
      "24 files, +173 lines, -1 lines"
    ],
    [
      "2022-12-09T15:57:30",
      "1 files, +11 lines, -2 lines"
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
