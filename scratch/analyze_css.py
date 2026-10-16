import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract existing style tags
style_matches = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
existing_css = '\n'.join(style_matches)

# Extract classes from HTML
class_attrs = re.findall(r'class=["\']([^"\']+)["\']', html)
all_classes = set()
for c in class_attrs:
    for item in c.split():
        if item.strip() and not item.startswith('${'):
            all_classes.add(item.strip())

# Extract IDs from HTML
id_attrs = re.findall(r'id=["\']([^"\']+)["\']', html)
all_ids = set()
for i in id_attrs:
    item = i.strip()
    if item and not item.startswith('${'):
        all_ids.add(item)

print(f"Total unique classes: {len(all_classes)}")
print(f"Total unique IDs: {len(all_ids)}")

styled_classes = set()
unstyled_classes = set()
for c in all_classes:
    if f".{c}" in existing_css or re.search(r'\b' + re.escape(c) + r'\b', existing_css):
        styled_classes.add(c)
    else:
        unstyled_classes.add(c)

styled_ids = set()
unstyled_ids = set()
for i in all_ids:
    if f"#{i}" in existing_css or re.search(r'\b' + re.escape(i) + r'\b', existing_css):
        styled_ids.add(i)
    else:
        unstyled_ids.add(i)

print(f"Styled classes: {len(styled_classes)}, Unstyled classes: {len(unstyled_classes)}")
print(f"Styled IDs: {len(styled_ids)}, Unstyled IDs: {len(unstyled_ids)}")

print("\nSample unstyled classes (first 30):")
print(sorted(list(unstyled_classes))[:30])

print("\nSample unstyled IDs (first 30):")
print(sorted(list(unstyled_ids))[:30])

with open('scratch/all_classes.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sorted(all_classes)))

with open('scratch/all_ids.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sorted(all_ids)))
