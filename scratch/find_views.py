with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'app-container' in l or 'view-landing' in l or 'function navigateTo' in l or 'window.navigateTo' in l or 'navigateTo(' in l:
        print(f"{i+1}: {l.strip()[:120]}")
