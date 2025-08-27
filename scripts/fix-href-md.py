# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Update the markdown file with local href paths if necessary."""

import argparse
import fileinput
import os
from pathlib import Path
import re

DEFAULT_API_FOLDER = "doc/_build/markdown/api"


def fix_hrefs(api_dir):
    """Update the markdown file with local href paths and remove ansys.mechanical.stubs from class name."""
    for root, dirs, files in os.walk(api_dir, topdown=True):
        for file in files:
            # If the html file is not index.html
            if ("index.md" not in file) and ("md" in file):
                # The full path to the html file
                full_file_path = Path(root) / Path(file)

                # | [`DataType`](../../../../v241/Ansys/Mechanical/Interfaces/IReadOnlyDataSeries.md#IReadOnlyDataSeries.DataType)
                link_regex = r"\| \[\`.*\`\]\(\.\.\/.*\)"
                # #### *class* ansys.mechanical.stubs.v241.Ansys.ACT.Automation.Mechanical.AdditiveManufacturing.AMBuildSettings
                class_regex = r"\#\#\#\# \*class\* ansys\.mechanical\.stubs\.v[0-9][0-9][0-9]\."

                for line in fileinput.input(full_file_path, inplace=True, encoding="utf-8"):
                    # Make the href local
                    if re.match(link_regex, line):
                        open_paren = line.index("(")
                        pound = line.index("#")
                        close_paren = line.index(")")
                        line = (
                            line[0 : open_paren + 1] + line[pound:close_paren] + line[close_paren:]
                        )
                    # Remove ansys.mechanical.stubs.v### from class name
                    if re.match(class_regex, line):
                        line = re.sub(class_regex, "#### *class* ", line)
                    print(line, end="")


def main():
    """Fix hrefs to be local hrefs."""
    parser = argparse.ArgumentParser(description="Create table of contents from html files.")
    parser.add_argument(
        "--api_folder",
        type=str,
        help="Path to the api folder.",
        default=DEFAULT_API_FOLDER,
    )
    args = parser.parse_args()

    repo_dir = Path(__file__).parent.parent
    api_folder = Path(args.api_folder)
    full_api_dir_path = repo_dir / api_folder

    if full_api_dir_path.exists():
        fix_hrefs(full_api_dir_path)
    else:
        raise NotADirectoryError(f"{full_api_dir_path} is not a valid directory.")


if __name__ == "__main__":
    main()
