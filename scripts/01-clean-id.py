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
import fileinput

DEFAULT_INPUT_FOLDER = "doc/_build/markdown"


def remove_links_from_markdown_files(directory_path):
    # Define the regular expression pattern to match <a id="..."></a> tags at the beginning of the file
    tag_pattern = r'^<a id=".*?"></a>'
    # Define the regular expression pattern to remove vale on/off comments
    vale_pattern = r'^<!-- vale .*? -->'

    # Iterate over all files and subdirectories in the specified directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}")
                # Only want to remove first <a></a> tag
                first_a_tag = False

                with fileinput.FileInput(file_path, inplace = True, encoding='utf-8') as f: 
                    for line in f: 
                        # Remove vale on/off comments
                        if bool(re.match(fr"{vale_pattern}", line)):
                            line = line.replace(line, "")
                            print(line, end ='\n')
                        # Remove first <a></a> tag
                        elif first_a_tag == False and bool(re.match(fr"{tag_pattern}", line)):
                            line = line.replace(line, "")
                            print(line)
                            first_a_tag = True
                        else:
                            print(line, end ='') 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean string starting with #id in Markdown files."
    )
    parser.add_argument(
        "--input_folder",
        type=str,
        help="Path to the folder containing Markdown files",
        default=DEFAULT_INPUT_FOLDER,
    )
    args = parser.parse_args()

    folder_path = args.input_folder
    # Replace 'your_directory' with the actual path to the directory containing your Markdown files
    remove_links_from_markdown_files(folder_path)
