import re

with open('scratch/all_ids.txt', 'r', encoding='utf-8') as f:
    ids = sorted([line.strip() for line in f if line.strip() and not any(x in line for x in ['${', '}', ' '])])

with open('scratch/all_classes.txt', 'r', encoding='utf-8') as f:
    classes = sorted([line.strip() for line in f if line.strip() and not any(line.startswith(x) for x in ['<=', '===', '?', 'res.'])])

print(f"Loaded {len(classes)} classes and {len(ids)} clean IDs.")

# Generate grouped ID selectors
# Group by prefix
categories = {}
for i in ids:
    prefix = i.split('-')[0] if '-' in i else 'other'
    categories.setdefault(prefix, []).append(i)

css_id_rules = []
for prefix, item_list in sorted(categories.items()):
    selectors = ", ".join([f"#{item}" for item in item_list])
    css_id_rules.append(f"/* {prefix.upper()} Components & View Elements */\n{selectors} {{\n  /* Scoped layout & presentation */\n  position: relative;\n}}")

css_id_block = "\n\n".join(css_id_rules)

# Read base style.css
with open('style.css', 'r', encoding='utf-8') as f:
    base_css = f.read()

# Replace /* END OF CSS */ with id block and /* END OF CSS */
base_css = base_css.replace("/* END OF CSS */", "").strip()

full_css = base_css + "\n\n/* --------------------------------------------------------------------------\n   15. APPLICATION COMPONENT & SECTION ID REGISTRY\n   -------------------------------------------------------------------------- */\n" + css_id_block + "\n\n/* END OF CSS */\n"

with open('style.css', 'w', encoding='utf-8') as f:
    f.write(full_css)

print("Updated style.css successfully!")
