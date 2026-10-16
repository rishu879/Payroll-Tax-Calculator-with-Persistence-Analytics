import re

css = open('style.css', 'r', encoding='utf-8').read()
ids = open('scratch/all_ids.txt', 'r', encoding='utf-8').read().splitlines()
real_ids = [i for i in ids if not any(x in i for x in ['${', '}', ' '])]

styled_ids = []
for i in real_ids:
    if f'#{i}' in css or re.search(r'\b' + re.escape(i) + r'\b', css):
        styled_ids.append(i)

print(f"Total IDs: {len(real_ids)}, Styled/Scoped IDs in CSS: {len(styled_ids)}")
