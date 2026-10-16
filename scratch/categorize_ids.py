import re

with open('scratch/all_ids.txt', 'r', encoding='utf-8') as f:
    ids = [line.strip() for line in f if line.strip() and not any(x in line for x in ['${', '}', ' '])]

print(f"Total clean IDs: {len(ids)}")
categories = {}
for i in ids:
    prefix = i.split('-')[0] if '-' in i else 'other'
    categories.setdefault(prefix, []).append(i)

for cat, items in sorted(categories.items()):
    print(f"Prefix '{cat}': {len(items)} IDs (e.g. {items[:3]})")
