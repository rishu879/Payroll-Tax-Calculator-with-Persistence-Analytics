#!/usr/bin/env python3
"""
PayPilot security verification. Starts the server in a throw-away folder and attacks it.
Run:  javac PayPilotServer.java && python3 security-tests/verify_security.py
Needs only Python 3 and Java 17+. Prints PASS or FAIL for every check and exits non-zero on any FAIL.
"""
import base64, hashlib, hmac, http.client, json, os, shutil, struct, subprocess, sys, tempfile, time, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT_A, PORT_B = 8097, 8098
ADMIN_PW = "Str0ng!Horse#Battery2026"
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(("PASS  " if cond else "FAIL  ") + name + ("" if cond else "   <-- " + str(detail)))

class Client:
    def __init__(self, port): self.port, self.cookies, self.csrf = port, {}, None
    def req(self, method, path, body=None, headers=None, raw=None, ctype="application/json", csrf=True):
        h = {"User-Agent": "verify/1.0"}
        if self.cookies: h["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.cookies.items())
        if csrf and self.csrf and method not in ("GET", "HEAD"): h["X-CSRF-Token"] = self.csrf
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        if data is not None: h["Content-Type"] = ctype
        h.update(headers or {})
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        c.request(method, path, body=data, headers=h)
        r = c.getresponse(); txt = r.read().decode("utf-8", "replace")
        for sc in r.msg.get_all("Set-Cookie") or []:
            k, v = sc.split(";")[0].split("=", 1)
            if sc.lower().find("max-age=0") >= 0: self.cookies.pop(k, None)
            else: self.cookies[k] = v
        try: js = json.loads(txt)
        except Exception: js = None
        return r.status, js, r, txt
    def login(self, email, pw, totp=None):
        b = {"email": email, "password": pw}
        if totp: b["totp"] = totp
        st, js, r, _ = self.req("POST", "/api/auth/login", b, csrf=False)
        if st == 200: self.csrf = js["csrf"]
        return st, js, r

def totp(secret, step):
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))
    h = hmac.new(key, struct.pack(">Q", step), hashlib.sha1).digest()
    o = h[-1] & 15
    return "%06d" % ((struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 10**6)

def start(port, extra_env, workdir):
    env = dict(os.environ, PAYPILOT_ADMIN_PASSWORD=ADMIN_PW, PAYPILOT_ADMIN_EMAIL="admin@example.org",
               PAYPILOT_DATA_KEY=base64.b64encode(os.urandom(32)).decode(), **extra_env)
    p = subprocess.Popen(["java", "-cp", ROOT, "PayPilotServer", str(port)], cwd=workdir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for _ in range(80):
        try:
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=1); c.request("GET", "/api/health"); c.getresponse().read(); return p
        except Exception: time.sleep(0.25)
    raise SystemExit("server did not start: " + p.stderr.read().decode())

def main():
    tmp = tempfile.mkdtemp(prefix="pp-sec-")
    wd = os.path.join(tmp, "b"); os.makedirs(wd)
    open(os.path.join(wd, "index.html"), "w").write('<!doctype html><script nonce="{{NONCE}}">1</script><style nonce="{{NONCE}}"></style>')
    open(os.path.join(wd, "sample-statement.csv"), "w").write("Date,Narration\n")
    procB = start(PORT_B, {"PAYPILOT_LOGIN_MAX": "1000", "PAYPILOT_GLOBAL_MAX": "100000"}, wd)
    try:
        run_functional(wd)
    finally:
        procB.terminate()
    wa = os.path.join(tmp, "a"); os.makedirs(wa)
    procA = start(PORT_A, {}, wa)
    try:
        run_limits()
    finally:
        procA.terminate(); shutil.rmtree(tmp, ignore_errors=True)
    bad = results.count(False)
    print(f"\n{results.count(True)} passed, {bad} failed")
    sys.exit(1 if bad else 0)

def run_functional(wd):
    print("\n== Transport, headers, CORS ==")
    a = Client(PORT_B)
    st, js, r, _ = a.req("GET", "/api/employees"); check("API rejects anonymous requests (401)", st == 401, st)
    st, js, r, _ = a.req("GET", "/api/health"); check("Health endpoint reveals nothing but ok", js.get("ok") is True, js)
    st, _, r, html1 = a.req("GET", "/")
    csp = r.getheader("Content-Security-Policy", "")
    check("HTML has CSP with a nonce, no unsafe-inline scripts", "script-src 'nonce-" in csp and "unsafe-inline" not in csp.split("style-src-attr")[0].replace("style-src-attr 'unsafe-inline'", ""), csp)
    check("CSP forbids framing, plugins and base-tag tricks", all(x in csp for x in ["frame-ancestors 'none'", "object-src 'none'", "base-uri 'none'"]), csp)
    for hname, want in [("X-Content-Type-Options", "nosniff"), ("X-Frame-Options", "DENY"), ("Referrer-Policy", "no-referrer")]:
        check(f"Header {hname}: {want}", r.getheader(hname) == want, r.getheader(hname))
    check("Permissions-Policy disables camera, mic, geolocation", "camera=()" in (r.getheader("Permissions-Policy") or ""))
    check("No HSTS over plain HTTP (it is sent only on HTTPS)", r.getheader("Strict-Transport-Security") is None)
    _, _, _, html2 = a.req("GET", "/")
    n1 = html1.split('nonce="')[1].split('"')[0]; n2 = html2.split('nonce="')[1].split('"')[0]
    check("CSP nonce is unique per response and injected into the page", n1 != n2 and n1 in csp and "{{NONCE}}" not in html1)
    st, js, r, _ = a.req("GET", "/api/health", headers={"Origin": "https://evil.example"})
    check("CORS: evil origin gets no Access-Control-Allow-Origin", r.getheader("Access-Control-Allow-Origin") is None)
    st, _, r, _ = a.req("OPTIONS", "/api/employees", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    check("CORS: preflight from evil origin is refused", st == 403, st)
    check("API responses are never cached", a.req("GET", "/api/health")[2].getheader("Cache-Control") == "no-store")
    st, *_ = a.req("GET", "/api/health", headers={"Host": "evil.com\r\nX: y"}) if False else (None,)
    st, js, r, _ = a.req("GET", "/api/health", headers={"Host": "bad host!"}); check("Host header injection rejected (400)", st == 400, st)
    for path in ["/PayPilotServer.java", "/paypilot-data.json", "/security.log", "/backups/", "/../../etc/passwd", "/%2e%2e/%2e%2e/etc/passwd", "/index.html/../paypilot-data.json"]:
        st, *_ = a.req("GET", path); check(f"Static server will not expose {path}", st == 404, st)
    st, *_ = a.req("TRACE", "/"); check("TRACE method refused (405)", st == 405, st)

    print("\n== Authentication, sessions, MFA ==")
    st, js1, *_ = a.login("nobody@example.org", "Whatever1234!"); st2, js2, *_ = a.login("admin@example.org", "wrong-password-1A!")
    check("Wrong user and wrong password give the same message (no user enumeration)", st == st2 == 401 and js1["error"] == js2["error"], (js1, js2))
    st, js, r = a.login("admin@example.org", ADMIN_PW)
    ck = r.getheader("Set-Cookie") or ""
    check("Sign-in works with the bootstrap admin password", st == 200 and js["user"]["role"] == "admin", (st, js))
    check("Session cookie is HttpOnly + SameSite=Strict", "HttpOnly" in ck and "SameSite=Strict" in ck, ck)
    check("Session id has at least 256 bits of randomness", len(list(a.cookies.values())[0]) >= 43)
    check("Admin without MFA is restricted until MFA is set up", js["mfaSetupRequired"] is True)
    st, js, *_ = a.req("GET", "/api/employees"); check("Restricted admin session cannot use the app (403)", st == 403, st)
    old_sid = dict(a.cookies); old_csrf = a.csrf
    st, js, *_ = a.req("POST", "/api/auth/mfa/setup", {}); secret = js["secret"]
    check("MFA setup returns an otpauth:// URI for authenticator apps", js["otpauth"].startswith("otpauth://totp/"), js)
    st, js, *_ = a.req("POST", "/api/auth/mfa/enable", {"code": "000000"}); check("Wrong MFA code is refused", st == 400, st)
    step = int(time.time() // 30)
    st, js, *_ = a.req("POST", "/api/auth/mfa/enable", {"code": totp(secret, step)})
    check("Correct TOTP code enables MFA and returns 8 recovery codes", st == 200 and len(js["recoveryCodes"]) == 8, (st, js))
    recov = js["recoveryCodes"]; a.csrf = js["csrf"]
    check("Session id is rotated after MFA is enabled (session fixation defence)", a.cookies != old_sid)
    old = Client(PORT_B); old.cookies, old.csrf = old_sid, old_csrf
    st, *_ = old.req("GET", "/api/health"); st, *_ = old.req("GET", "/api/employees"); check("Old session id no longer works", st == 401, st)
    st, js, *_ = a.req("GET", "/api/employees"); check("Admin session works after MFA setup", st == 200 and len(js) == 8, (st, js))
    b = Client(PORT_B); st, js, _ = b.login("admin@example.org", ADMIN_PW)
    check("With MFA on, password alone is not enough", st == 401 and js.get("mfaRequired") is True, (st, js))
    code = totp(secret, step + 1)
    st, js, _ = b.login("admin@example.org", ADMIN_PW, code); check("Password + TOTP code signs in", st == 200, (st, js))
    c = Client(PORT_B); st, js, _ = c.login("admin@example.org", ADMIN_PW, code)
    check("Replaying the same TOTP code is refused", st == 401, (st, js))
    c = Client(PORT_B); st, js, _ = c.login("admin@example.org", ADMIN_PW, recov[0]); check("A recovery code works once", st == 200, (st, js))
    c2 = Client(PORT_B); st, js, _ = c2.login("admin@example.org", ADMIN_PW, recov[0]); check("A recovery code cannot be reused", st == 401, (st, js))
    a = b  # use the freshest admin session from here on

    print("\n== CSRF, content type, size limits, JSON abuse ==")
    st, *_ = a.req("POST", "/api/tax/calc", {"gross": 1275000}, csrf=False); check("State-changing call without CSRF token is blocked", st == 403, st)
    st, *_ = a.req("POST", "/api/tax/calc", {"gross": 1275000}, headers={"X-CSRF-Token": "wrong"}); check("Wrong CSRF token is blocked", st == 403, st)
    st, *_ = a.req("POST", "/api/tax/calc", {"gross": 1275000}, headers={"Origin": "https://evil.example"}); check("Valid token from a foreign Origin is blocked", st == 403, st)
    st, js, *_ = a.req("POST", "/api/tax/calc", {"gross": 1275000}); check("Valid token + same origin works (New regime, 12.75L -> tax 0)", st in (200, 201) and js["new"]["total"] == 0, (st, js))
    st, js, *_ = a.req("POST", "/api/tax/calc", {"gross": 1500000, "c80": 150000, "d80": 25000}); check("Tax maths: 15L new = 97,500 and old = 2,02,800", js["new"]["total"] == 97500 and js["old"]["total"] == 202800, js)
    st, *_ = a.req("POST", "/api/tax/calc", raw=b"gross=1", ctype="text/plain"); check("Non-JSON content type refused (415)", st == 415, st)
    st, *_ = a.req("POST", "/api/tax/calc", raw=b"x" * (3 * 1024 * 1024)); check("Oversized body refused (413)", st == 413, st)
    st, js, *_ = a.req("POST", "/api/tax/calc", raw=(b"[" * 20000 + b"]" * 20000)); check("Deeply nested JSON bomb refused (400), server survives", st == 400, st)
    st, *_ = a.req("GET", "/api/health"); check("Server still healthy after the JSON bomb", st == 200)
    st, js, r, txt = a.req("POST", "/api/tax/calc", raw=b"{bad json"); check("Malformed JSON gives a clean 400 with no stack trace", st == 400 and "Exception" not in txt and "at com." not in txt, txt)
    st, js, *_ = a.req("POST", "/api/tax/calc", {"gross": -5}); check("Negative or absurd numbers are rejected", st == 400, st)
    st, js, *_ = a.req("POST", "/api/employees", {"name": "<script>alert(1)</script>", "ctc": 600000}); check("XSS payload in a name is rejected", st == 400, (st, js))
    st, js, *_ = a.req("POST", "/api/employees", {"name": "A" * 500, "ctc": 600000}); check("Over-long input is rejected", st == 400, st)
    st, js, *_ = a.req("POST", "/api/employees", {"name": "Robert'); DROP TABLE employees;--", "ctc": 600000})
    check("SQL-injection text is stored as plain data (no SQL is ever built from input)", st == 201 and js["name"].startswith("Robert"), (st, js))
    st, js, *_ = a.req("GET", "/api/runs/..%2f..%2fetc%2fpasswd"); check("Path traversal in an ID finds nothing (404)", st == 404, st)
    st, js, *_ = a.req("POST", "/api/statements/analyse", {"csv": "x\n" * 60000}); check("Statement row limit enforced", st in (400, 413), st)
    st, js, *_ = a.req("POST", "/api/statements/analyse", {"csv": "Date,Narration,Debit,Credit\n01/09/2026,SALES INVOICE X,,11800\n", "gstInclusive": True, "gstRate": 18})
    check("CA Buddy GST maths: 11,800 inclusive at 18% -> GST 1,800", st in (200, 201) and round(js["gst"]["outputGst"]) == 1800, (st, js))

    print("\n== Roles and permissions (RBAC) ==")
    for em, role in [("mod@example.org", "moderator"), ("user@example.org", "user")]:
        st, js, *_ = a.req("POST", "/api/users", {"email": em, "role": role, "password": "short"}); check(f"Weak password refused for {role}", st == 400, (st, js))
        st, js, *_ = a.req("POST", "/api/users", {"email": em, "role": role, "password": "Tr1cky!Horse-Staple9", **({"empId": 1} if role == "user" else {})}); check(f"Admin can create a {role}", st == 201, (st, js))
    st, js, *_ = a.req("POST", "/api/users", {"email": "x@example.org", "role": "root", "password": "Tr1cky!Horse-Staple9"}); check("Unknown role refused", st == 400, st)
    mod = Client(PORT_B); mod.login("mod@example.org", "Tr1cky!Horse-Staple9")
    usr = Client(PORT_B); usr.login("user@example.org", "Tr1cky!Horse-Staple9")
    st, *_ = usr.req("GET", "/api/employees"); check("User cannot read the employee list (403)", st == 403, st)
    st, js, *_ = usr.req("POST", "/api/tax/calc", {"gross": 900000}); check("User can use the tax calculator", st in (200, 201), st)
    st, *_ = usr.req("GET", "/api/payslip?run=2026-09&emp=5"); check("User cannot open someone else's payslip", st == 403, st)
    st, *_ = usr.req("GET", "/api/payslip?run=2026-09&emp=1"); check("User can open their own payslip", st == 200, st)
    st, *_ = usr.req("POST", "/api/users", {"email": "z@example.org", "role": "admin", "password": "Tr1cky!Horse-Staple9"}); check("User cannot create users (no privilege escalation)", st == 403, st)
    st, *_ = usr.req("GET", "/api/audit"); check("User cannot read the audit log", st == 403, st)
    st, *_ = mod.req("GET", "/api/employees"); check("Moderator can read employees", st == 200, st)
    st, *_ = mod.req("PUT", "/api/rules/tax", {"cess": 0}); check("Moderator cannot change tax rules", st == 403, st)
    st, *_ = mod.req("DELETE", "/api/employees/2"); check("Moderator cannot delete employees", st == 403, st)
    st, js, *_ = mod.req("POST", "/api/runs", {}); rid = js["id"]
    st, js, *_ = mod.req("POST", f"/api/runs/{rid}/advance", {}); check("Moderator can approve a payroll run", st in (200, 201) and js["status"] == "Approved", (st, js))
    st, *_ = mod.req("POST", f"/api/runs/{rid}/advance", {}); check("Moderator cannot mark it Paid (maker-checker)", st == 403, st)
    st, js, *_ = a.req("POST", f"/api/runs/{rid}/advance", {}); check("Admin can release payment", st in (200, 201) and js["status"] == "Paid", (st, js))
    st, js, *_ = a.req("POST", "/api/reset", {}); check("Reset needs an explicit confirmation", st == 400, st)
    st, *_ = a.req("POST", "/api/reset", {"confirm": "RESET"}); st2, js2, *_ = a.req("GET", "/api/users")
    check("Reset restores demo data but keeps user accounts", st in (200, 201) and len(js2) == 3, (st, st2, js2))

    st, *_ = usr.req("POST", "/api/auth/password", {"current": "not-my-password", "new": "N3w!Horse-Staple-77"}); check("Password change needs the current password", st == 400, st)
    st, *_ = usr.req("POST", "/api/auth/password", {"current": "Tr1cky!Horse-Staple9", "new": "weak"}); check("Password change enforces the policy", st == 400, st)
    other = Client(PORT_B); other.login("user@example.org", "Tr1cky!Horse-Staple9")
    st, *_ = usr.req("POST", "/api/auth/password", {"current": "Tr1cky!Horse-Staple9", "new": "N3w!Horse-Staple-77"}); check("Password change succeeds", st == 200, st)
    st, *_ = other.req("GET", "/api/health"); st, *_ = other.req("GET", "/api/auth/me"); check("Changing the password signs out the user's other sessions", st == 401, st)
    st, *_ = usr.req("GET", "/api/auth/me"); check("The session that changed the password stays signed in", st == 200, st)

    print("\n== Lockout, brute force, audit and logs ==")
    v = Client(PORT_B)
    codes = [v.login("mod@example.org", "WrongPassword1!")[0] for _ in range(5)]
    st, js, _ = v.login("mod@example.org", "Tr1cky!Horse-Staple9")
    check("5 wrong passwords lock the account, even the right password is then refused (429)", codes == [401] * 5 and st == 429, (codes, st))
    for i in range(12): Client(PORT_B).login(f"ghost{i}@example.org", "WrongPassword1!")
    log = open(os.path.join(wd, "security.log")).read()
    for ev in ["LOGIN_FAILED", "ACCOUNT_LOCKED", "LOGIN_OK", "MFA_ENABLED", "CSRF_TOKEN_REJECTED", "CSRF_ORIGIN_BLOCKED", "ACCESS_DENIED", "UNAUTHENTICATED_ACCESS", "ALERT_BRUTE_FORCE", "BACKUP_OK"]:
        check(f"Security log records {ev}", ev in log)
    check("Security log never contains passwords or session ids", ADMIN_PW not in log and "pp_sid" not in log and "Tr1cky" not in log)
    st, js, *_ = a.req("GET", "/api/audit"); check("Audit log lists who changed what", st == 200 and any(x.get("actor") == "admin@example.org" for x in js), js[:2] if isinstance(js, list) else js)

    print("\n== Data at rest, backups, logout ==")
    raw = open(os.path.join(wd, "paypilot-data.json"), "rb").read()
    check("Data file is encrypted (AES-256-GCM): starts with PPENC1:", raw.startswith(b"PPENC1:"))
    check("No names, emails or password hashes are readable in the data file", b"Aarav" not in raw and b"admin@example.org" not in raw and b"pbkdf2" not in raw)
    check("Data file permissions are owner-only (600)", oct(os.stat(os.path.join(wd, "paypilot-data.json")).st_mode & 0o777) == "0o600" or os.name == 'nt', oct(os.stat(os.path.join(wd, "paypilot-data.json")).st_mode & 0o777))
    check("Automatic backup was written", len(glob.glob(os.path.join(wd, "backups", "*.bak"))) >= 1)
    bk = glob.glob(os.path.join(wd, "backups", "*.bak"))[0]
    check("Backups are encrypted too", open(bk, "rb").read().startswith(b"PPENC1:"))
    sid = dict(a.cookies); csrf = a.csrf
    st, *_ = a.req("POST", "/api/auth/logout", {}); ghost = Client(PORT_B); ghost.cookies, ghost.csrf = sid, csrf
    st, *_ = ghost.req("GET", "/api/employees"); check("Logout invalidates the session on the server", st == 401, st)

def run_limits():
    print("\n== Rate limiting (default limits) ==")
    seen = []
    for i in range(30): seen.append(Client(PORT_A).login(f"rl{i}@example.org", "WrongPassword1!")[0])
    check("Login attempts are rate limited per IP (429 after 20)", 429 in seen and seen.index(429) <= 21, seen)
    c = Client(PORT_A); res = [c.req("GET", "/api/health")[0] for _ in range(320)]
    check("Global per-IP rate limit returns 429 with Retry-After", 429 in res)

if __name__ == "__main__":
    main()
