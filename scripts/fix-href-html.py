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

from bs4 import BeautifulSoup

DEFAULT_API_FOLDER = "doc/_build/html/api"


def update_soup(file_updates, soup):
    """Replace each original href line with a local href line in the HTML."""
    if file_updates:
        for href, local_href in file_updates.items():
            # Replace the original href with the local href
            # For example, replace
            # '../../../../v242/Ansys/Mechanical/Interfaces/IVariable.html#IVariable.QuantityName'
            # with '#IVariable.QuantityName'
            soup = BeautifulSoup(str(soup).replace(href, local_href))
            # Remove the href from the file_updates dictionary
            file_updates.pop(href)
            return update_soup(file_updates, soup)
    else:
        return soup


def fix_hrefs(api_dir):
    """Update the html file with local href paths if necessary."""
    for root, dirs, files in os.walk(api_dir, topdown=True):
        for file in files:
            # If the html file is not index.html
            if ("index.html" not in file) and ("html" in file):
                # Dictionary that keeps track of the original href and local href
                file_updates = {}
                # The full path to the html file
                full_file_path = Path(root) / Path(file)

                with Path.open(full_file_path, encoding="utf-8") as f:
                    # Parse HTML file
                    soup = BeautifulSoup(f, "html.parser")
                    # Find all tables
                    tables = soup.find_all("table")
                    for table in tables:
                        # Find all rows in the table
                        rows = table.find_all("tr")
                        # For each row, create a local href for the <a> tag if applicable
                        for row in rows:
                            # '../../../../v242/Ansys/Mechanical/Interfaces/IVariable.html#IVariable.QuantityName'
                            href = row.a["href"]
                            if href[0] != "#":
                                # Get the index of the # symbol
                                hash_index = href.index("#")
                                # Create a string only containing the local href path. For example, #IVariable.QuantityName
                                local_href = href[hash_index:]
                                # {'../../../../v242/Ansys/Mechanical/Interfaces/IVariable.html#IVariable.QuantityName': '#IVariable.QuantityName', ...}
                                file_updates[href] = local_href

                # If the href could be updated with local paths, update the HTML and write to the file
                if file_updates:
                    # Update the HTML for each href that has to be updated
                    local_href_soup = update_soup(file_updates, soup)
                    # Overwrite the updated HTML to the file
                    with Path.open(full_file_path, "w", encoding="utf-8") as file:
                        file.write(str(local_href_soup))


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


if __name__ == "__main__":
    main()
