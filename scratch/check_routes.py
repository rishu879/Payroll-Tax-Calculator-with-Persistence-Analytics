import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

frontend_calls = sorted(list(set(re.findall(r'[\'\"`](/api/[a-zA-Z0-9_\-\/${}]+)[\'\"`]', html))))

print("Frontend API calls found in index.html:")
for call in frontend_calls:
    print(" -", call)

with open('PayPilotServer.java', 'r', encoding='utf-8') as f:
    java = f.read()

print("\nBackend route matching check:")
for call in frontend_calls:
    # normalize path by stripping query or dynamic params
    base_route = re.sub(r'/[0-9]+', '/:id', call)
    base_route = re.sub(r'/\${[^}]+}', '/:id', base_route)
    clean_part = call.split('/')[2] if len(call.split('/')) > 2 else ''
    match = clean_part in java
    print(f"Call: {call:<45} Base: {base_route:<30} Found in Java: {match}")
