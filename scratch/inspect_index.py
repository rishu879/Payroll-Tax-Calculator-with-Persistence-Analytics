import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

out = []

sidebar_match = re.search(r'<aside id="sidebar-dock">(.*?)</aside>', text, re.DOTALL)
nav_ids = []
if sidebar_match:
    sidebar_html = sidebar_match.group(1)
    nav_items = re.findall(r'<a([^>]+)>(.*?)</a>', sidebar_html, re.DOTALL)
    for attrs, label in nav_items:
        clean_label = re.sub(r'<[^>]+>', '', label).strip()
        m = re.search(r'switchTab\(["\']([^"\']+)["\']\)', attrs)
        tab_id = m.group(1) if m else "UNKNOWN"
        nav_ids.append((tab_id, clean_label, attrs))

panes = set(re.findall(r'id=["\']pane-([^"\']+)["\']', text))

# Look for pane contents
pane_contents = {}
for p in panes:
    m = re.search(r'<div id=["\']pane-' + re.escape(p) + r'["\'][^>]*>(.*?)</div>\s*<!--\s*==', text, re.DOTALL)
    if not m:
        m = re.search(r'<div id=["\']pane-' + re.escape(p) + r'["\'][^>]*>(.*?)</div>', text, re.DOTALL)
    pane_contents[p] = len(m.group(1).strip()) if m else 0

functions = set(re.findall(r'function\s+([a-zA-Z0-9_$]+)\s*\(', text))

out.append(f"{'Menu Item':25} | {'Tab ID':20} | {'Has Click Handler':18} | {'Pane Exists':12} | {'Pane Content Len':16} | {'Render/Action Funcs'}")
out.append("-" * 120)
for tab_id, label, attrs in nav_ids:
    has_click = 'onclick' in attrs
    has_pane = tab_id in panes
    c_len = pane_contents.get(tab_id, 0)
    
    # check functions
    matching_fns = [fn for fn in functions if tab_id.replace('-', '').lower() in fn.lower() or any(w in fn.lower() for w in tab_id.split('-') if len(w) > 3)]
    out.append(f"{label:25} | {tab_id:20} | {str(has_click):18} | {str(has_pane):12} | {str(c_len):16} | {', '.join(matching_fns[:3])}")

with open('scratch/diagnosis.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))

print("Diagnosis updated")
