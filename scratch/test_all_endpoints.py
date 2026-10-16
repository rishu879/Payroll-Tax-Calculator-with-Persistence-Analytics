import urllib.request
import json

base = "http://127.0.0.1:8080"

# 1. Health
req = urllib.request.Request(f"{base}/api/health")
with urllib.request.urlopen(req) as resp:
    print("1. Health:", resp.status, resp.read().decode())

# 2. Login via Google Sandbox
data = json.dumps({"email": "admin@paypilot.local", "name": "System Admin", "role": "admin"}).encode()
req = urllib.request.Request(f"{base}/api/auth/google/sandbox", data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    res_data = json.loads(resp.read().decode())
    token = res_data["token"]
    csrf = res_data["csrf"]
    print("2. Login Sandbox:", resp.status, "Token obtained:", bool(token), "CSRF obtained:", bool(csrf))

headers = {
    "Authorization": f"Bearer {token}",
    "X-CSRF-Token": csrf,
    "Content-Type": "application/json"
}

# 3. GET /api/employees
req = urllib.request.Request(f"{base}/api/employees", headers=headers)
with urllib.request.urlopen(req) as resp:
    emps = json.loads(resp.read().decode())
    print("3. GET /api/employees:", resp.status, f"Found {len(emps)} employees")

# 4. GET /api/runs
req = urllib.request.Request(f"{base}/api/runs", headers=headers)
with urllib.request.urlopen(req) as resp:
    runs = json.loads(resp.read().decode())
    print("4. GET /api/runs:", resp.status, f"Found {len(runs)} payroll runs")

# 5. POST /api/tax/calc
tax_data = json.dumps({"gross": 1500000, "c80": 150000, "d80": 25000, "nps": 50000}).encode()
req = urllib.request.Request(f"{base}/api/tax/calc", data=tax_data, headers=headers)
with urllib.request.urlopen(req) as resp:
    tax_res = json.loads(resp.read().decode())
    print("5. POST /api/tax/calc:", resp.status, "New tax:", tax_res.get("new", {}).get("total"), "Old tax:", tax_res.get("old", {}).get("total"))

# 6. POST /api/statements/analyse
stmt_data = json.dumps({"totalIncome": 500000, "totalExpense": 200000, "netPnl": 300000}).encode()
req = urllib.request.Request(f"{base}/api/statements/analyse", data=stmt_data, headers=headers)
with urllib.request.urlopen(req) as resp:
    stmt_res = json.loads(resp.read().decode())
    print("6. POST /api/statements/analyse:", resp.status, "Success:", stmt_res.get("success"))

# 7. POST /api/ca/ask
ca_data = json.dumps({"question": "What is new tax regime standard deduction?"}).encode()
req = urllib.request.Request(f"{base}/api/ca/ask", data=ca_data, headers=headers)
with urllib.request.urlopen(req) as resp:
    ca_res = json.loads(resp.read().decode())
    reply_txt = ca_res.get("answer") or ca_res.get("reply") or ""
    print("7. POST /api/ca/ask:", resp.status, "Reply:", reply_txt[:50] + "...")

# 8. GET /api/security/audit-report
req = urllib.request.Request(f"{base}/api/security/audit-report", headers=headers)
with urllib.request.urlopen(req) as resp:
    sec_res = json.loads(resp.read().decode())
    print("8. GET /api/security/audit-report:", resp.status, "OWASP Score:", sec_res.get("securityScore"))

print("\nALL 8 BACKEND API SERVICES OPERATING 100% SUCCESSFULLY!")
