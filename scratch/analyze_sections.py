import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

print("File size:", len(text), "chars")

# Find how many lines
lines = text.splitlines()
print("Lines:", len(lines))

# Find the structure: head, styles, body, sidebar, main-content, scripts
head_end = text.find('</head>')
print("Head ends around line:", text[:head_end].count('\n'))

sidebar_start = text.find('<aside id="sidebar-dock">')
sidebar_end = text.find('</aside>', sidebar_start)
print("Sidebar lines:", text[:sidebar_start].count('\n'), "to", text[:sidebar_end].count('\n'))

main_start = text.find('<section id="main-content">')
main_end = text.find('</section>', main_start)
print("Main content lines:", text[:main_start].count('\n'), "to", text[:main_end].count('\n'))

script_start = text.find('<script', main_end)
print("Scripts start around line:", text[:script_start].count('\n'))
