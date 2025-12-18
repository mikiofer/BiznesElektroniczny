import json
import re
from urllib.parse import urlparse

def extract_name_from_url(url):
    """
    Extracts category name from typical x-kom URLs.
    Handles:
    - https://www.x-kom.pl/g/2-laptopy-i-komputery.html
    - https://www.x-kom.pl/g-12/c/46-kable-i-przejsciowki.html
    """

    path = urlparse(url).path  # /g/2-laptopy-i-komputery.html
    last = path.strip("/").split("/")[-1]  # 2-laptopy-i-komputery.html

    # Remove extension
    last = last.replace(".html", "")

    # Remove numeric prefix: "46-kable-i..." → "kable-i..."
    last = re.sub(r"^\d+-", "", last)

    # Remove category id in format c/46-name → "46-name"
    last = re.sub(r"^\d+-", "", last)

    # Convert dashes to spaces
    last = last.replace("-", " ")

    # Capitalize each word
    return " ".join(word.capitalize() for word in last.split())


def load_categories(path="categories.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_tree(categories):
    nodes = []

    for cat in categories:
        name = cat["name"].strip()

        # If name is empty → extract from URL
        if not name:
            name = extract_name_from_url(cat["url"])

        nodes.append({
            "name": name,
            "url": cat["url"],
            "level": cat["level"],
            "parent_raw": (cat["parent"] or "").strip(),
            "subcategories": []
        })

    tree = []

    # Helper: check parent/child match
    def is_parent(parent, child):
        if child["level"] != parent["level"] + 1:
            return False
        if not child["parent_raw"]:
            return False

        return child["parent_raw"].lower() in parent["name"].lower()

    # Build nested structure
    for node in nodes:
        parent_found = False
        for potential_parent in nodes:
            if is_parent(potential_parent, node):
                potential_parent["subcategories"].append(node)
                parent_found = True
                break

        if not parent_found and node["level"] == 0:
            tree.append(node)

    return tree


def save_tree(tree, path="categories_tree.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    categories = load_categories()
    tree = build_tree(categories)
    save_tree(tree)
    print("✔ categories_tree.json created successfully.")
