#!/usr/bin/env python3
"""
Create organized GitHub catalog of all Artapli designs
With thumbnails and links to artapli.shop
"""

import sqlite3
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

def get_categories(title, tags=''):
    """Match product to categories based on title and tags keywords"""
    title_lower = title.lower()
    tags_lower = tags.lower() if tags else ''
    search_text = f"{title_lower} {tags_lower}"
    matched = []

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in search_text:
                matched.append(category)
                break

    return matched if matched else ['Other']

def create_category_readme(category, products):
    """Create README for a category with products table"""

    readme = f"""# {category}

{len(products)} designs in this category

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

    db_file = '/home/anna/FireflareDocs/complete_integrated_database.db'

    print("Reading products from database...")

    products_by_category = defaultdict(list)
    all_products = {}

    # Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Query all active products with valid data including tags
    cursor.execute("""
        SELECT DISTINCT
            shopify_handle,
            product_name,
            image_url,
            shopify_tags
        FROM products
        WHERE shopify_status = 'active'
        AND shopify_handle IS NOT NULL
        AND product_name IS NOT NULL
        ORDER BY product_name
    """)

    for row in cursor.fetchall():
        handle, title, image, tags = row

        if not handle or not title or not image:
            continue

        # Store unique products only
        if handle not in all_products:
            all_products[handle] = {
                'handle': handle,
                'title': title,
                'image': image
            }

            # Categorize using both title and tags
            categories = get_categories(title, tags)
            for cat in categories:
                products_by_category[cat].append(all_products[handle])

    conn.close()

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

Index of {total_count:,} machine embroidery designs

This repository contains a structured catalog of Artapli embroidery designs, including thumbnails, design IDs/names, and direct product links for reference and lookup. It is intended for browsing, organization, and quick access to design pages.

**Official store**: [artapli.shop](https://artapli.shop)

*Catalog data may be updated periodically; product availability and pricing are managed on the official store.*

---

## Browse by Category

"""

    # Sort categories by product count
    sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

    for category, products in sorted_cats:
        cat_link = category.lower().replace(' ', '-').replace('&', 'and')
        readme += f"### [{category}](categories/{cat_link}/)\n"
        readme += f"{len(products)} designs\n\n"

    readme += f"""---

## Catalog Structure

**Categories**: Products are automatically categorized by keywords from product titles and tags. Some products may appear in multiple categories.

**Data Source**: Product data is sourced from Shopify (active products only) including handles, titles, images, and tags.

**File Formats**: Artapli designs typically include DST, PES, JEF, EXP, HUS, VP3, XXX, VIP formats, with BX fonts for Embrilliance and ESA fonts for Wilcom/Hatch where applicable.

---

## Related Resources

- **[Artapli Machine Embroidery Knowledge Base](https://github.com/artapli/Artapli-Machine-Embroidery)** - Technical documentation, software guides, and file format specifications
- **[Lettering Tool](https://artapli.shop/pages/lettering-app)** - Free browser-based embroidery lettering application
- **[Official Store](https://artapli.shop)** - Product pages, purchasing, and download access

---

## Repository Information

**Purpose**: Design index and reference catalog
**Maintainer**: Artapli
**Last Updated**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
**License**: Catalog for reference purposes. All designs are copyrighted by Artapli.
"""

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)

    print("✓ Created main README")

if __name__ == '__main__':
    main()
