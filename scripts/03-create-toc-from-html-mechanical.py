import os
import sys
from urllib.parse import urljoin

from bs4 import BeautifulSoup


# This script must be run as follows: python script_name api index.html
def parse_index_html(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content, os.path.dirname(
        html_file
    )  # Return HTML content and directory of the HTML file


def extract_nav_items(base_dir, html_content):
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
        item = {"name": link.text.strip(), "href": base_dir + href}
        # print('ITEM=', item)
        items.append(item)

    return items


def build_indented_items(nav_items, base_dir="", indentation=1):
    indented_items = []
    for nav_item in nav_items:
        # print('NAV_ITEM=', nav_item)
        indented_items.append((indentation, nav_item))
        if "index.html" in nav_item["href"]:
            # nested_html_path = os.path.join(base_dir, nav_item['href'])  # Construct nested HTML file path
            # print('NAV_ITEM[HREF]= ', nav_item['href'])
            # find the index of index.html
            str = "index.html"
            index = nav_item["href"].index("index.html")
            nested_html_path = nav_item["href"][0:index]
            # print('nested_html_path= ', nested_html_path)
            try:
                full_path = nested_html_path + str
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


def create_toc_file(indented_items):
    os.chdir("..")
    cnt = 0
    with open("toc.yml", "w", encoding="utf-8") as f:
        f.write("- name: Introduction\n")
        f.write("  href: index.md\n")
        f.write("- name: API reference\n")
        f.write("  href: " + subpath + "/" + "index.md\n")
        f.write("  items: \n")
        for indentation, nav_item in indented_items:
            print(nav_item)
            if nav_item["href"] == "ansys/mechanical/stubs/index.html":
                cnt = cnt + 1
            if cnt <= 1:
                if nav_item["name"] == "items:":
                    f.write("  " * (indentation + 1) + "items:\n")
                else:
                    f.write("  " * indentation + "- name: " + nav_item["name"] + "\n")
                if nav_item["href"]:
                    f.write(
                        "  " * indentation
                        + "  href: "
                        + subpath
                        + "/"
                        + nav_item["href"].replace("html", "md")
                        + "\n"
                    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <subpath> <index.html>")
        sys.exit(1)

    subpath = sys.argv[1]
    html_file = sys.argv[2]

    if not os.path.isfile(html_file):
        print(f"Error: {html_file} does not exist.")
        sys.exit(1)
    print("HTML_PATH= ", subpath, "/", html_file)
    os.chdir(subpath)
    html_content, base_dir = parse_index_html(html_file)
    nav_items = extract_nav_items(base_dir, html_content)
    indented_items = build_indented_items(nav_items, base_dir)
    create_toc_file(indented_items)

    print("toc.yml file created successfully!")
