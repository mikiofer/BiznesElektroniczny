import json

def count_items(category):
    """
    Recursively counts subcategories and products for a given category node.
    Returns a tuple: (subcategory_count, product_count)
    """
    # Base counts for current level
    sub_count = len(category.get('subcategories', []))
    prod_count = len(category.get('products', []))
    
    # Recursively add counts from children
    for sub in category.get('subcategories', []):
        child_sub, child_prod = count_items(sub)
        sub_count += child_sub
        prod_count += child_prod
        
    return sub_count, prod_count

def analyze_json_structure(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"{'Category Name':<50} | {'Subcategories':<15} | {'Products':<10}")
    print("-" * 80)
    
    total_subs = 0
    total_prods = 0
    
    # The root is a list of categories
    for category in data:
        s_count, p_count = count_items(category)
        print(f"{category.get('name', 'Unknown')[:48]:<50} | {s_count:<15} | {p_count:<10}")
        
        total_subs += s_count
        total_prods += p_count
        
    print("-" * 80)
    print(f"{'TOTAL':<50} | {total_subs:<15} | {total_prods:<10}")

# To use this script, replace 'full_tree.json' with your actual file path
analyze_json_structure('pruned_tree.json')