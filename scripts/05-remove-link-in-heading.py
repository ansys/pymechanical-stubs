import argparse
import os
import re


def process_markdown_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    updated_content = re.sub(r"(#+)\s*\[`([^`]+)`\]\(#.*?\)", r"\1 `\2`", content)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)


def process_directory(directory):
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".md"):
                file_path = os.path.join(dirpath, filename)
                process_markdown_file(file_path)


if __name__ == "__main__":
    # directory_path = input("Enter the path to the directory containing markdown files: ")
    parser = argparse.ArgumentParser(description="Remove links in heading if any.")
    parser.add_argument("--input_folder", help="Path to the folder of Markdown files")
    args = parser.parse_args()

    folder_path = args.input_folder
    process_directory(folder_path)
    print("Markdown files processed successfully.")
