with open('PayPilotServer.java', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'p[0].equals' in l or 'p.length' in l or 'handle(' in l or 'handleApi' in l:
        print(f"{i+1}: {l.strip()[:100]}")
