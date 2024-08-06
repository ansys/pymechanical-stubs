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
"""Clean empty rows before heading 1 (h1) in markdown files."""

import argparse
import os
import pathlib
import re

DEFAULT_INPUT_FOLDER = "doc/_build/markdown"


def remove_empty_rows_at_top_and_before_heading1(directory_path):
    """Remove empty rows before heading 1 in Markdown files."""
    # Define the regular expression pattern to match empty rows at the top and before Heading 1
    pattern = r"^\s*\n+"

    # Iterate over all files and subdirectories in the specified directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".md"):
                file_path = str(pathlib.Path(root, file))

                # Read the content of the Markdown file
                with pathlib.Path.open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Use re.sub() to remove empty rows at the top and before the first Heading 1
                new_content = re.sub(pattern, "", content, count=1)

                # Write the modified content back to the file
                with pathlib.Path.open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                print(f"Removed empty rows at the top and before Heading 1 in {file_path}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean empty rows before heading 1 in Markdown files."
    )
    parser.add_argument(
        "--input_folder",
        type=str,
        help="Path to the folder containing Markdown files",
        default=DEFAULT_INPUT_FOLDER,
    )
    args = parser.parse_args()

    folder_path = args.input_folder
    repo_dir = pathlib.Path(__file__).parent.parent
    full_dir_path = repo_dir / folder_path

    # Replace 'your_directory' with the actual path to the directory containing your Markdown files
    remove_empty_rows_at_top_and_before_heading1(folder_path)
