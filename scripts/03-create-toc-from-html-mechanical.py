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
"""Create a table of contents file from HTML files."""

import argparse
import os
from pathlib import Path
import sys

from bs4 import BeautifulSoup

DEFAULT_API_FOLDER = "doc/_build/html/api"
DEFAULT_HTML_FILE = "index.html"
DEFAULT_OUTPUT_FOLDER = "output"


# This script must be run as follows: python script_name api index.html
def parse_index_html(html_file):
    """Read & return the HTML content and index.html file name."""
    with html_file.open("r", encoding="utf-8") as f:
        html_content = f.read()
    # Return HTML content and directory of the HTML file
    return html_content, html_file.parent


def extract_nav_items(base_dir, html_content):
    """Extract navigation items and append them to a dictionary."""
    soup = BeautifulSoup(html_content, "html.parser")
    # nav_links = soup.find_all('a', class_='nav-link nav-internal')  # Find nav links with class 'nav-link nav-internal'
    reference_links = soup.find_all(
        "a", class_="reference internal"
    )  # Find reference links with class 'reference internal'
    items = []
    # for link in nav_links + reference_links:  # Combine nav_links and reference_links
    for link in reference_links:
        href = link.get("href")
        if href.startswith("../") or "#" in href:
            # print('SKIP ../index.html file=', href)
            continue  # Skip '../index.html' paths and path not ending with just index.html
        item = {"name": link.text.strip(), "href": str(Path(base_dir, href))}
        if item not in items:
            # print('ITEM=', item)
            items.append(item)

    return items


def build_indented_items(nav_items, base_dir="", indentation=1):
    """Create a list from the navigation items dictionary with indentation."""
    indented_items = []
    for nav_item in nav_items:
        # print('NAV_ITEM=', nav_item)
        indented_items.append((indentation, nav_item))
        if "index.html" in nav_item["href"]:
            # nested_html_path = str(pathlib.Path(base_dir, nav_item['href']) # Construct nested HTML file path
            # print('NAV_ITEM[HREF]= ', nav_item['href'])
            # find the index of index.html
            str = "index.html"
            index = nav_item["href"].index("index.html")
            nested_html_path = nav_item["href"][0:index]
            # print('nested_html_path= ', nested_html_path)
            try:
                full_path = Path(nested_html_path, str)
                # print('full_path=',full_path)
                nested_html_content, _ = parse_index_html(full_path)  # Parse nested HTML file
                nested_items = extract_nav_items(nested_html_path, nested_html_content)
                nested_indented_items = build_indented_items(
                    nested_items, nested_html_path, indentation=indentation + 1
                )  # Recursive call with updated base directory and indentation level
                if nested_indented_items:
                    indented_items.append(
                        (indentation, {"name": "items:", "href": ""})
                    )  # Append 'items:' keyword at the new indentation level
                    indented_items.extend(
                        nested_indented_items
                    )  # Extend the list of indented items
            except FileNotFoundError:
                print(f"Error: File '{nested_html_path}' not found. Skipping...")
    return indented_items


def create_toc_file(api_folder, indented_items):
    """Create the toc.yml file with the indented_items list."""
    toc_file_name = Path("toc.yml")
    with toc_file_name.open("w", encoding="utf-8") as f:
        f.write("- name: Introduction\n")
        f.write("  href: index.md\n")
        f.write("- name: API reference\n")
        f.write("  href: " + api_folder + "/" + "index.md\n")
        f.write("  items: \n")
        for indentation, nav_item in indented_items:
            if nav_item["name"] == "items:":
                f.write("  " * (indentation + 1) + "items:\n")
            else:
                f.write("  " * indentation + "- name: " + nav_item["name"] + "\n")
            if nav_item["href"]:
                f.write(
                    "  " * indentation
                    + "  href: "
                    + api_folder
                    + "/"
                    + nav_item["href"].replace("html", "md")
                    + "\n"
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create table of contents from html files.")
    parser.add_argument(
        "--api_folder",
        type=str,
        help="Path to the api folder.",
        default=DEFAULT_API_FOLDER,
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        help="Name of the folder where toc.yml should be stored.",
        default=DEFAULT_OUTPUT_FOLDER,
    )
    parser.add_argument(
        "--html_file",
        type=str,
        help="Name of the html file to create the table of contents from.",
        default=DEFAULT_HTML_FILE,
    )
    args = parser.parse_args()

    api_folder = args.api_folder
    html_file = Path(args.html_file)
    output_folder = Path(args.output_folder)

    repo_dir = Path(__file__).parent.parent
    full_file_path = Path(repo_dir, api_folder, html_file)
    full_dir_path = str(Path(repo_dir, api_folder))

    if not full_file_path.is_file():
        print(f"Error: {full_file_path} does not exist.")
        sys.exit(1)

    print(f"HTML_PATH={str(Path(full_dir_path, html_file))}")
    os.chdir(full_dir_path)
    html_content, base_dir = parse_index_html(html_file)
    nav_items = extract_nav_items(base_dir, html_content)
    indented_items = build_indented_items(nav_items, base_dir)

    output_folder_path = Path(repo_dir, output_folder)
    os.chdir(repo_dir)
    if not output_folder_path.is_dir():
        output_folder.mkdir()

    os.chdir(output_folder_path)

    if not api_folder.is_dir():
        print(f"Error: {api_folder} does not exist.")
        sys.exit(1)

    if not html_file.is_file():
        print(f"Error: {html_file} does not exist.")
        sys.exit(1)

    create_toc_file(api_folder, indented_items)

    print("toc.yml file created successfully!")
