import json
import os
import sys

# Define default input/output files
INPUT_FILE = "full_tree.json"
OUTPUT_FILE = "pruned_tree.json"

def prune_node(node):
    """
    Returns True if the node should be kept (it has products or valid children).
    Returns False if the node is empty and should be removed.
    """
    # 1. Prune children first (depth-first traversal)
    if "subcategories" in node:
        # Keep only subcategories that return True
        node["subcategories"] = [child for child in node["subcategories"] if prune_node(child)]

    # 2. Check if this node has any products
    has_products = len(node.get("products", [])) > 0

    # 3. Check if this node has any remaining subcategories
    has_subcategories = len(node.get("subcategories", [])) > 0

    # 4. Decision: Keep if it has content OR children
    # NOTE: You can adjust logic here. 
    # Currently, it keeps a category if it has products OR if it has valid subcategories.
    if has_products or has_subcategories:
        return True
    
    return False

def main():
    # Allow optional command line args: python pruner.py [input_file] [output_file]
    in_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    out_file = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_FILE

    if not os.path.exists(in_file):
        print(f"Error: Input file '{in_file}' not found.")
        return

    print(f"Loading tree from {in_file}...")
    with open(in_file, 'r', encoding='utf-8') as f:
        tree_data = json.load(f)

    original_count = len(tree_data)
    
    # Apply pruning to the top-level list
    # We only keep root nodes that return True
    pruned_tree = [node for node in tree_data if prune_node(node)]

    print(f"Pruning complete. Root nodes reduced from {original_count} to {len(pruned_tree)}.")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(pruned_tree, f, ensure_ascii=False, indent=2)
    
    print(f"Saved pruned tree to {out_file}")

if __name__ == "__main__":
    main()