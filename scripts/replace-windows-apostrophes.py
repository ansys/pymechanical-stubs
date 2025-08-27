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
"""Update the html file with local href paths if necessary."""

import argparse
import fileinput
import os
from pathlib import Path

DEFAULT_HTML_API_FOLDER = "doc/_build/html/api"
DEFAULT_MARKDOWN_API_FOLDER = "doc/_build/markdown/api"


def replace_windows_apostrophes(api_dir):
    """Update the markdown file with local href paths if necessary."""
    for root, dirs, files in os.walk(api_dir, topdown=True):
        for file in files:
            # The full path to the html file
            full_file_path = Path(root) / Path(file)

            for line in fileinput.input(full_file_path, inplace=True, encoding="utf-8"):
                if "" in line:
                    line = line.replace("‘", "'")
                if "" in line:
                    line = line.replace("’", "'")
                print(line, end="")


def main():
    """Fix hrefs to be local hrefs."""
    parser = argparse.ArgumentParser(description="Create table of contents from html files.")
    parser.add_argument(
        "--html_api_folder",
        type=str,
        help="Path to the html api folder.",
        default=DEFAULT_HTML_API_FOLDER,
    )
    parser.add_argument(
        "--markdown_api_folder",
        type=str,
        help="Path to the markdown api folder.",
        default=DEFAULT_MARKDOWN_API_FOLDER,
    )
    args = parser.parse_args()

    repo_dir = Path(__file__).parent.parent
    html_api_folder = Path(args.html_api_folder)
    markdown_api_folder = Path(args.markdown_api_folder)
    full_html_api_dir = repo_dir / html_api_folder
    full_markdown_api_dir = repo_dir / markdown_api_folder

    if full_html_api_dir.exists():
        replace_windows_apostrophes(full_html_api_dir)
    else:
        print(f"Error: {full_html_api_dir} does not exist.")
        exit(1)

    if full_markdown_api_dir.exists():
        replace_windows_apostrophes(full_html_api_dir)
    else:
        print(f"Error: {full_markdown_api_dir} does not exist.")
        exit(1)


if __name__ == "__main__":
    main()
