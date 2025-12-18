import json
import os

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved to {filename}")

def index_products_by_category(product_list):
    """
    Creates a dictionary where keys are category URLs and values are lists of products.
    """
    mapping = {}
    for p in product_list:
        cat_url = p.get("categoryUrl")
        if cat_url:
            mapping.setdefault(cat_url, []).append(p)
    return mapping

def update_tree_recursive(node, new_products_map):
    """
    Recursively traverses the tree. If a node URL matches new products,
    it appends them, avoiding duplicates based on product_id.
    """
    node_url = node.get("url")
    
    # 1. Get existing products in this node (if any)
    existing_products = node.get("products", [])
    
    # 2. Get new products destined for this node
    incoming_products = new_products_map.get(node_url, [])
    
    if incoming_products:
        # Create a set of existing IDs for fast lookup
        existing_ids = {p.get("product_id") for p in existing_products if p.get("product_id")}
        
        # Append only truly new products
        added_count = 0
        for prod in incoming_products:
            pid = prod.get("product_id")
            # If product has no ID, or ID is not in existing, add it
            if not pid or pid not in existing_ids:
                existing_products.append(prod)
                existing_ids.add(pid)
                added_count += 1
        
        if added_count > 0:
            print(f"Added {added_count} new products to category: {node.get('name')}")

    # 3. Update the node with the merged list
    node["products"] = existing_products

    # 4. Recurse into subcategories
    for sub in node.get("subcategories", []):
        update_tree_recursive(sub, new_products_map)

def main():
    # FILES CONFIGURATION
    TREE_FILE = "full_tree.json"       # Target tree to update
    SOURCE_TREE = "categories_tree.json" # Fallback if full_tree doesn't exist
    NEW_PRODUCTS_FILE = "telewizory.json" # The output from your scraper
    tree_data = load_json(TREE_FILE)
        

    if not tree_data:
        print("Error: No tree data found. Exiting.")
        return

    # 2. Load New Products
    print(f"Loading new products from {NEW_PRODUCTS_FILE}...")
    new_products = load_json(NEW_PRODUCTS_FILE)
    if not new_products:
        print("No new products to merge. Exiting.")
        return

    # 3. Index new products for faster lookup
    product_map = index_products_by_category(new_products)

    # 4. Update the tree
    print("Merging data...")
    for root_node in tree_data:
        update_tree_recursive(root_node, product_map)

    # 5. Save the result
    save_json(tree_data, TREE_FILE)

if __name__ == "__main__":
    main()