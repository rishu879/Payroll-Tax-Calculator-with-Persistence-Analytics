# -*- coding: utf-8 -*-
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open("scratch/welfare_module.js", "r", encoding="utf-8") as f:
    full_js = f.read()

start_marker = "    // =========================================================================\n    // WORKER RIGHTS & WELFARE: INTERNATIONALIZATION, VOICE, CALCS & ROUTER\n    // ========================================================================="
end_marker = "    // MASTER SCREENS REGISTRY & ROUTER IMPLEMENTATION"

start_pos = html.find(start_marker)
end_pos = html.rfind(end_marker)

if start_pos != -1 and end_pos != -1:
    html = html[:start_pos] + full_js + "\n\n    // -------------------------------------------------------------------------\n" + html[end_pos:]
    print("Replaced welfare module with full verified version in index.html.")
else:
    print(f"Markers not found as expected. start_pos={start_pos}, end_pos={end_pos}")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Saved updated index.html.")
