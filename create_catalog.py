#!/usr/bin/env python3
"""
Create organized GitHub catalog of all Artapli designs
With thumbnails and links to artapli.shop
"""

import csv
import os
from pathlib import Path
from collections import defaultdict

# Category definitions from customer-fonts.js
CATEGORIES = {
    'BX Fonts': ['bx', 'embrilliance'],
    'Script Fonts': ['script', 'cursive', 'handwriting'],
    'Applique Fonts': ['applique font', 'applique alphabet'],
    'Satin Stitch Fonts': ['satin font', 'satin stitch font'],
    'Monogram Fonts': ['monogram'],
    'Fringe Fonts': ['fringe font'],
    'Chain Stitch': ['chain stitch'],
    'Shadow Fonts': ['shadow', 'outline font'],
    'Christmas': ['christmas', 'xmas', 'santa', 'snowman', 'reindeer'],
    'Halloween': ['halloween', 'pumpkin', 'witch', 'ghost'],
    'Easter': ['easter', 'bunny', 'egg'],
    'Valentine': ['valentine', 'heart', 'love'],
    'Animals': ['animal', 'dog', 'cat', 'bird', 'horse', 'farm'],
    'Baby & Kids': ['baby', 'child', 'kid', 'nursery'],
    'Florals': ['flower', 'floral', 'rose', 'botanical'],
    'ITH Keychains': ['ith keychain', 'keychain'],
    'ITH Towel Toppers': ['towel topper'],
    'All Fonts': ['font', 'alphabet', 'letter'],
}

def get_categories(title):
    """Match product to categories based on title keywords"""
    title_lower = title.lower()
    matched = []

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in title_lower:
                matched.append(category)
                break

    return matched if matched else ['Other']

def create_category_readme(category, products):
    """Create README for a category with products table"""

    readme = f"""# {category}

{len(products)} designs in this category

[🛍️ Browse all {category} on artapli.shop](https://artapli.shop/collections/{category.lower().replace(' ', '-').replace('&', 'and')})

---

## Designs

| | Product Name | Shop Link |
|---|-------------|-----------|
"""

    for product in products[:200]:  # Limit to 200 per category
        handle = product['handle']
        title = product['title']
        img_url = product['image']

        # Create thumbnail with link
        readme += f"| <img src=\"{img_url}\" width=\"80\"> | {title} | [View](https://artapli.shop/products/{handle}) |\n"

    if len(products) > 200:
        readme += f"\n*...and {len(products) - 200} more designs in this category*\n"

    readme += f"""

---

[← Back to All Categories](../README.md) | [Browse on artapli.shop →](https://artapli.shop)
"""

    return readme

def main():
    """Process products and create catalog"""

    csv_file = '/home/anna/all products - compare_with_descriptions.csv'

    print("Reading products...")

    products_by_category = defaultdict(list)
    all_products = {}

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            handle = row.get('n ', '').strip()
            title = row.get('Title', '').strip()
            image = row.get('Image Src', '').strip()

            if not handle or not title:
                continue

            # Store unique products only
            if handle not in all_products:
                all_products[handle] = {
                    'handle': handle,
                    'title': title,
                    'image': image
                }

                # Categorize
                categories = get_categories(title)
                for cat in categories:
                    products_by_category[cat].append(all_products[handle])

    print(f"Found {len(all_products)} unique products")
    print(f"Creating {len(products_by_category)} category pages...")

    # Create category folders and READMEs
    for category, products in products_by_category.items():
        cat_folder = Path('categories') / category.lower().replace(' ', '-').replace('&', 'and')
        cat_folder.mkdir(parents=True, exist_ok=True)

        readme_path = cat_folder / 'README.md'
        readme_content = create_category_readme(category, products)

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"✓ Created {category}: {len(products)} products")

    # Create main README
    create_main_readme(products_by_category, len(all_products))

    print("\n✅ Catalog created!")
    print("Location: /home/anna/GitHub/Artapli-Design-Catalog/")

def create_main_readme(categories, total_count):
    """Create main landing page README"""

    readme = f"""# Artapli Embroidery Design Catalog

> Browse {total_count:,} professional machine embroidery designs

**Official Store**: [artapli.shop](https://artapli.shop)

This catalog provides an organized view of all Artapli embroidery designs with thumbnails and direct links to purchase on artapli.shop.

---

## Browse by Category

"""

    # Sort categories by product count
    sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

    for category, products in sorted_cats:
        cat_link = category.lower().replace(' ', '-').replace('&', 'and')
        readme += f"### [{category}](categories/{cat_link}/)\n"
        readme += f"{len(products)} designs | [View on Shop](https://artapli.shop/collections/{cat_link})\n\n"

    readme += f"""---

## About This Catalog

This is a reference catalog showing Artapli's embroidery design collection.

**To Purchase**:
- Click any product link to visit artapli.shop
- All designs are digital downloads
- Instant access after purchase

**File Formats**:
- DST, PES, JEF, EXP, HUS, VP3, XXX, VIP
- Multiple sizes included
- BX fonts for Embrilliance
- ESA fonts for Wilcom/Hatch

**Categories**:
Designs are automatically organized by keywords. Some products appear in multiple categories.

---

## Related Resources

- **[Artapli Knowledge Base](https://github.com/artapli/Artapli-Machine-Embroidery)** - Software guides & technical docs
- **[Lettering Tool](https://artapli.shop/pages/lettering-app)** - FREE browser-based lettering app
- **[Shop](https://artapli.shop)** - Browse and purchase designs

---

**© 2026 Artapli**
*This catalog is for browsing only. All designs are copyrighted and available for purchase at artapli.shop*
"""

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)

    print("✓ Created main README")

if __name__ == '__main__':
    main()
