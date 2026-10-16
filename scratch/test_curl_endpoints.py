import http.client
import json

conn = http.client.HTTPConnection("127.0.0.1", 8080)

# Sign in as bootstrap admin: read bootstrap password from log or sign in
with open("security.log", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Test login or public endpoints
print("Testing live curl endpoints against running server...")
conn.request("GET", "/api/health")
r1 = conn.getresponse()
print("1. GET /api/health ->", r1.status, r1.read().decode())

conn.request("GET", "/api/welfare/rules")
r2 = conn.getresponse()
print("2. GET /api/welfare/rules ->", r2.status, "Length:", len(r2.read().decode()))

conn.request("POST", "/api/welfare/surveys/SURV-202610-DEMO/submit", 
             body=json.dumps({"q1": 5, "q2": 4, "q3": 5, "q4": 4, "q5": 5, "q6": 5}),
             headers={"Content-Type": "application/json", "Origin": "http://127.0.0.1:8080"})
r3 = conn.getresponse()
print("3. POST /api/welfare/surveys/.../submit ->", r3.status, r3.read().decode())

conn.request("GET", "/api/employees")
r4 = conn.getresponse()
print("4. GET /api/employees (unauthenticated) ->", r4.status, r4.read().decode())

conn.request("GET", "/style.css")
r5 = conn.getresponse()
print("5. GET /style.css ->", r5.status, "Content-Type:", r5.getheader("Content-Type"))
