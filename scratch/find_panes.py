import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Find all view-pane divs in main-content
main_start = text.find('<section id="main-content">')
main_end = text.find('</section>', main_start)
main_text = text[main_start:main_end]

panes = re.findall(r'<div\s+id="([^"]+)"\s+class="view-pane([^"]*)"', main_text)
print("Found", len(panes), "view-panes:")
for pid, pcls in panes:
    print(f"  {pid} (class='view-pane{pcls}')")
