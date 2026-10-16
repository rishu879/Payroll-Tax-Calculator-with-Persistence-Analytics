import re

with open('PayPilotServer.java', 'r', encoding='utf-8') as f:
    code = f.read()

# Look for route matching blocks
routes = []
for line in code.splitlines():
    if 'p.length' in line or 'p[0]' in line or 'p[1]' in line or 'method.equals' in line or 'case ' in line:
        routes.append(line.strip())

print(f"Found {len(routes)} route logic lines. Sample:")
for r in routes[:25]:
    print("  ", r)
