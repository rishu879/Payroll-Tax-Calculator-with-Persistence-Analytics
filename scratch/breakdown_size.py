with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Sections:
# 1. <head> ... </head>
# 2. <style> ... </style>
# 3. <body> up to <aside id="sidebar-dock">
# 4. <aside id="sidebar-dock"> ... </aside>
# 5. <section id="main-content"> ... </section>
# 6. Modals / overlays
# 7. <script> ... </script>

head_match = re.search(r'<head>(.*?)</head>', text, re.DOTALL)
style_match = re.search(r'<style>(.*?)</style>', text, re.DOTALL)
sidebar_match = re.search(r'<aside id="sidebar-dock">(.*?)</aside>', text, re.DOTALL)
main_match = re.search(r'<section id="main-content">(.*?)</section>', text, re.DOTALL)
scripts = re.findall(r'<script[^>]*>(.*?)</script>', text, re.DOTALL)

print("Total len:", len(text))
if style_match:
    print("Style len:", len(style_match.group(1)))
if sidebar_match:
    print("Sidebar len:", len(sidebar_match.group(1)))
if main_match:
    print("Main content len:", len(main_match.group(1)))
print("Number of script blocks:", len(scripts))
for i, sc in enumerate(scripts):
    print(f"  Script {i} len: {len(sc)}")
