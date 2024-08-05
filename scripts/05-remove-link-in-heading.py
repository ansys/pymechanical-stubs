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

import argparse
import os
import re

DEFAULT_INPUT_FOLDER = "doc/_build/markdown"


def process_markdown_file(file_path):
    """Update markdown file content."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    updated_content = re.sub(r"(#+)\s*\[`([^`]+)`\]\(#.*?\)", r"\1 `\2`", content)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)


def process_directory(directory):
    """Process all markdown files within a directory."""
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".md"):
                file_path = os.path.join(dirpath, filename)
                process_markdown_file(file_path)


if __name__ == "__main__":
    # directory_path = input("Enter the path to the directory containing markdown files: ")
    parser = argparse.ArgumentParser(description="Remove links in heading if any.")
    parser.add_argument(
        "--input_folder",
        type=str,
        help="Path to the folder containing Markdown files",
        default=DEFAULT_INPUT_FOLDER,
    )
    args = parser.parse_args()

    folder_path = args.input_folder
    process_directory(folder_path)
    print("Markdown files processed successfully.")
