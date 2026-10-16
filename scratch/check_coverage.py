import re

css = open('style.css', 'r', encoding='utf-8').read()
assert css.strip().endswith('/* END OF CSS */'), 'Missing /* END OF CSS */'

classes = open('scratch/all_classes.txt', 'r', encoding='utf-8').read().splitlines()
real_classes = [c for c in classes if not any(c.startswith(x) for x in ['<=', '===', '?', 'res.'])]

ids = open('scratch/all_ids.txt', 'r', encoding='utf-8').read().splitlines()
real_ids = [i for i in ids if not ('${' in i or '}' in i)]

styled_classes = [c for c in real_classes if re.search(r'\b' + re.escape(c) + r'\b', css)]
styled_ids = [i for i in real_ids if f"#{i}" in css]

print(f"Classes: {len(styled_classes)} / {len(real_classes)}")
print(f"IDs: {len(styled_ids)} / {len(real_ids)}")
