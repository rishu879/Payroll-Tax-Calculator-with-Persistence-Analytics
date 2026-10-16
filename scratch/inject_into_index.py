# -*- coding: utf-8 -*-
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open("scratch/welfare_module.js", "r", encoding="utf-8") as f:
    js_code = f.read()

marker = "// MASTER SCREENS REGISTRY & ROUTER IMPLEMENTATION"
if "WORKER RIGHTS & WELFARE: INTERNATIONALIZATION" not in html:
    pos = html.rfind(marker)
    if pos != -1:
        html = html[:pos] + js_code + "\n\n    " + html[pos:]
        print("Injected welfare_module.js before master router registry.")
    else:
        last_script = html.rfind("</script>")
        html = html[:last_script] + "\n" + js_code + "\n" + html[last_script:]
        print("Injected welfare_module.js before </script>.")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated index.html successfully.")
