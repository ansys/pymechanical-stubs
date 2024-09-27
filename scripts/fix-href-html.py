# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
"""Update the html file with local href paths if necessary."""

import argparse
import os
from pathlib import Path
import re

DEFAULT_API_FOLDER = "doc/_build/html/api"


def fix_hrefs(api_dir):
    """Update the markdown file with local href paths if necessary."""
    for root, dirs, files in os.walk(api_dir, topdown=True):
        for file in files:
            # If the html file is not index.html
            if ("index.html" not in file) and ("html" in file):
                # The full path to the html file
                full_file_path = Path(root) / Path(file)
                print(full_file_path)

                pattern = re.compile(
                    r"\<tr class\=\".*\"\>\<td\>\<p\>\<a class\=\"reference internal\" href\=\"\.\.\/.*\" "
                )
                with Path.open(full_file_path, encoding="utf-8") as f:
                    lines = f.readlines()
                    # Join all lines in the file into one string
                    joined_lines = "".join(lines)
                    # Check if the string contains the regex pattern
                    matches = pattern.findall(joined_lines)
                    if matches:
                        for match in matches:
                            # '<tr class="row-odd"><td><p><a class="reference internal" href="../../../../../../../v241/Ansys/ACT/Automation/Mechanical/Results/DeformationResults/VectorDeformation.html#VectorDeformation.Activate"
                            # get index of href="
                            href_eq = match.index("href=") + 6
                            # get index of #
                            pound = match.index("#")
                            # remove href= to #
                            new_match = match[0:href_eq] + match[pound:]
                            print(f"Replacing {match} with {new_match}")
                            # Replace original matched regex (match) with fixed href using local references (new_match)
                            joined_lines = joined_lines.replace(match, new_match)

                with Path.open(full_file_path, "w", encoding="utf-8") as myfile:
                    myfile.write(joined_lines)


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
    print(full_api_dir_path)

    if full_api_dir_path.exists():
        fix_hrefs(full_api_dir_path)


if __name__ == "__main__":
    main()
