# -*- coding: utf-8 -*-
import urllib.request
import json
import http.client

BASE = "http://127.0.0.1:8080"

print("--- Running Host & System Checks ---")
checks = []

def check(ok, desc, extra=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {desc} {extra}")
    checks.append((ok, desc))

# 1. Health check
try:
    with urllib.request.urlopen(f"{BASE}/api/health") as res:
        data = json.loads(res.read().decode())
        check(res.status == 200 and data.get("ok") is True, "Server Health Check (/api/health)")
except Exception as e:
    check(False, "Server Health Check (/api/health)", str(e))

# 2. Index page check
try:
    with urllib.request.urlopen(BASE) as res:
        html = res.read().decode()
        csp = res.headers.get("Content-Security-Policy", "")
        has_nonce = "nonce-" in csp
        has_welfare_nav = "welfare-hub" in html
        has_fair_pay = "welfare-fair-pay" in html
        has_ledger = "welfare-ledger" in html
        check(res.status == 200 and has_nonce and has_welfare_nav and has_fair_pay and has_ledger, 
              "Frontend Delivery & CSP Nonce Check (/)", 
              f"Length: {len(html)} bytes, CSP Nonce: {has_nonce}")
except Exception as e:
    check(False, "Frontend Delivery Check (/)", str(e))

# 3. Public Welfare Rules API
try:
    with urllib.request.urlopen(f"{BASE}/api/welfare/rules") as res:
        rules = json.loads(res.read().decode())
        has_mw = "minimumWages" in rules
        has_delhi = "Delhi" in rules.get("minimumWages", {})
        has_schemes = len(rules.get("schemes", [])) >= 8
        check(res.status == 200 and has_mw and has_delhi and has_schemes,
              "Welfare Rules Public API (/api/welfare/rules)",
              f"States: {len(rules.get('minimumWages', {}))}, Schemes: {len(rules.get('schemes', []))}")
except Exception as e:
    check(False, "Welfare Rules Public API (/api/welfare/rules)", str(e))

# 4. Anonymous Survey Submission (No login required, anonymous worker)
try:
    req = urllib.request.Request(
        f"{BASE}/api/welfare/surveys/SURV-202610-DEMO/submit",
        data=json.dumps({"q1": 5, "q2": 4, "q3": 5, "q4": 5, "q5": 4, "q6": 5}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Origin": BASE}
    )
    with urllib.request.urlopen(req) as res:
        ans = json.loads(res.read().decode())
        check(res.status in (200, 201) and ans.get("submitted") is True,
              "Anonymous Pulse Survey Submit (/api/welfare/surveys/.../submit)",
              ans.get("message", ""))
except Exception as e:
    check(False, "Anonymous Pulse Survey Submit (/api/welfare/surveys/.../submit)", str(e))

# 5. Security: Unauthenticated access to /api/employees is refused (401)
try:
    urllib.request.urlopen(f"{BASE}/api/employees")
    check(False, "Protected Employee Endpoint Refuses Anonymous Access")
except urllib.error.HTTPError as e:
    check(e.code == 401, "Protected Employee Endpoint Refuses Anonymous Access (401)", f"HTTP {e.code}")
except Exception as e:
    check(False, "Protected Employee Endpoint Refuses Anonymous Access", str(e))

# 6. Security: Source code / data files never served as static assets
blocked = ["/PayPilotServer.java", "/paypilot-data.json", "/security.log"]
for path in blocked:
    try:
        urllib.request.urlopen(f"{BASE}{path}")
        check(False, f"Static File Blocklist ({path})")
    except urllib.error.HTTPError as e:
        check(e.code == 404, f"Static File Blocklist ({path}) (404)", f"HTTP {e.code}")

# 7. Static Stylesheet & Sample Statement Delivery
try:
    with urllib.request.urlopen(f"{BASE}/style.css") as res:
        css = res.read().decode("utf-8")
        ct = res.headers.get("Content-Type", "")
        check(res.status == 200 and "text/css" in ct and "/* END OF CSS */" in css,
              "Static Stylesheet Delivery (/style.css)", f"Length: {len(css)} bytes, Content-Type: {ct}")
except Exception as e:
    check(False, "Static Stylesheet Delivery (/style.css)", str(e))

try:
    with urllib.request.urlopen(f"{BASE}/sample-statement.csv") as res:
        csv_data = res.read().decode("utf-8")
        ct = res.headers.get("Content-Type", "")
        check(res.status == 200 and "text/csv" in ct and "Date" in csv_data,
              "Sample Statement CSV Delivery (/sample-statement.csv)", f"Length: {len(csv_data)} bytes")
except Exception as e:
    check(False, "Sample Statement CSV Delivery (/sample-statement.csv)", str(e))

passed = sum(1 for ok, _ in checks if ok)
total = len(checks)
print(f"\nSummary: {passed}/{total} host checks passed.")
if passed == total:
    print("ALL SYSTEMS OPERATIONAL AND WORKING PROPERLY!")
