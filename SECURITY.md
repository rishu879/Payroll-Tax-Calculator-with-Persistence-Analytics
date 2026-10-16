# PayPilot Security Report

Scope: the Java backend (`PayPilotServer.java`) and the way the website talks to it.
Status: hardened and tested with 101 automated attack checks (all pass). This is **not** a substitute for an independent penetration test before you handle real money or real people's data.

## 1. What was wrong before (findings)

| # | Finding | Severity | OWASP | Fixed by |
|---|---|---|---|---|
| 1 | No sign-in at all: anyone could read employees, run payroll, reset all data | Critical | A01, A07 | Session login, RBAC on every endpoint |
| 2 | `Access-Control-Allow-Origin: *` on every response | High | A05 | Same-origin by default, allow-list only |
| 3 | No CSRF protection | High | A01 | CSRF token + Origin check + JSON-only bodies |
| 4 | Server source, data file and logs could be requested as static files | High | A05 | Static allow-list (index page and sample CSV only) |
| 5 | Payroll data stored as readable text | High | A02 | AES-256-GCM encryption at rest, file mode 600 |
| 6 | Recursive JSON parser had no depth limit (stack overflow = easy denial of service) | Medium | A04 | Depth limit 64 |
| 7 | No request size limit, no rate limiting, no slow-request limits | Medium | A04, A05 | 2 MB cap, per-IP and per-user limits, server timeouts |
| 8 | Server errors returned internal exception text | Medium | A05 | Generic message + reference id, details in the security log |
| 9 | No security headers (CSP, HSTS, framing, sniffing) | Medium | A05 | Full header set, per-response CSP nonce |
| 10 | Listened on all network interfaces | Medium | A05 | Binds to 127.0.0.1 unless you opt in |
| 11 | If the data file could not be read, the app silently re-created demo data (data loss) | Medium | A08 | Refuses to start and never overwrites |
| 12 | No input length or character limits | Low | A03 | Length caps, control characters stripped, `<` `>` refused |
| 13 | Audit log did not say who did what | Low | A09 | Actor recorded on every change |
| 14 | `/api/ca/ask` trusts a summary sent by the browser | Low | A04 | Accepted: it only affects the caller's own answer. Size-capped and rate-limited |

## 2. What is now in place

**Authentication and sessions**
- Email + password sign-in. Passwords hashed with PBKDF2-HMAC-SHA256, 600,000 iterations, random 16-byte salt (OWASP-accepted; see "Not done" for Argon2id).
- Password policy: 12 to 128 characters, upper, lower, number, symbol, no common passwords, must not contain your email name.
- Multi-factor authentication: TOTP (RFC 6238, works with Google Authenticator, Authy, 1Password), 30 second window with replay protection, plus 8 one-time recovery codes (stored hashed). **Admins must enable MFA** before they can use the app.
- Sessions are random 256-bit ids kept on the server, sent in an `HttpOnly; SameSite=Strict` cookie (`Secure` and `__Host-` prefix on HTTPS). JavaScript can never read them. They can be revoked instantly, which a stateless JWT cannot.
- Session fixation: a new id is issued at sign-in and when MFA is enabled. Old ids stop working.
- Hijacking: 30 minute idle timeout, 8 hour absolute timeout, bound to the browser's User-Agent, 5 sessions per user, password change signs out other devices, logout revokes server-side.
- Lockout: 5 wrong passwords locks the account (15 minutes, doubling up to 24 hours). Login always does the same hashing work and gives the same message for unknown users, so accounts cannot be discovered.

**Authorization (RBAC)**

| Action | user | moderator | admin |
|---|---|---|---|
| Tax calculator, CA Buddy, own payslip | yes | yes | yes |
| Employees (read, add, edit), payroll runs, approve a run, analytics, any payslip | no | yes | yes |
| Release payment (Approved to Paid), delete employee, edit tax rules, audit log, users, reset | no | no | yes |

**API protection**: every endpoint except `/api/health` and sign-in needs a session. All state-changing calls need the CSRF token header and a same-origin `Origin`. Bodies must be `application/json`, max 2 MB. Statements are limited to 50,000 rows. Rate limits: 300 requests/minute/IP, 20 sign-ins/15 minutes/IP, 10 statement analyses/minute/user.

**Injection**: there is no SQL, no shell command and no XML parsing in the server, so SQL injection, command injection and XXE have no entry point. User text is stored as data. The website escapes every value it prints. The only outbound request is to a fixed Gemini URL, so SSRF has no user-controlled target. If you later add a JDBC database, use `PreparedStatement` only.

**Transport and browser**: HTTPS (built-in TLS 1.2/1.3 only, or any proxy), HSTS, `Content-Security-Policy` with a fresh nonce for scripts and styles, `frame-ancestors 'none'`, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy: no-referrer`, Permissions-Policy, COOP and CORP, `Cache-Control: no-store` on the API.

**Data**: AES-256-GCM encryption at rest (`PAYPILOT_DATA_KEY`), atomic writes, mode 600, automatic encrypted backups at start and every 6 hours (last 14 kept).

**Monitoring**: `security.log` is JSON lines: logins, failures, lockouts, MFA events, CSRF and permission denials, rate limits, backups, server errors. Passwords, tokens and session ids are never written. `ALERT_BRUTE_FORCE` is raised at 10 failures in 5 minutes from one IP and printed to stderr.

## 3. Not done, or not possible here (read this)

| Request | Status |
|---|---|
| Sign in with Google (OAuth 2.0) | **Not built.** It needs your Google Cloud client id and secret and live access to Google, which this environment does not have, so I could not test it. Plan: see section 6. |
| Argon2id | **Not available** in the Java standard library. PBKDF2-SHA256 at 600,000 iterations is the OWASP fallback. To switch, add Bouncy Castle (`Argon2BytesGenerator`) and keep the `pbkdf2-sha256$` prefix so old hashes still verify. |
| JWT with refresh tokens | **Replaced** by opaque server sessions in secure cookies (your requirement allowed either). Easier to revoke, nothing to steal from local storage. |
| Cloudflare WAF, DDoS protection, CDN, firewall rules | **Configuration in your Cloudflare account**, not code. A checklist is in section 5. I cannot test it from here. |
| Database encryption, parameterized queries | The project uses an encrypted file store, not SQL. Nothing to parameterize yet. |
| Full OWASP Top 10 audit, vulnerability scanning, penetration test | I did a **white-box review plus 101 automated attack checks**. I did not run ZAP, Burp, Nessus or StackHawk (no scanner or API key here). Run section 4 steps 3 and 5 before going live. |
| Dependency vulnerabilities | The server has **zero third-party dependencies** (JDK only), so there is nothing to patch except Java itself. Keep Java updated. |
| Multiple servers | Sessions and rate limits live in memory, so run **one instance**. For several, move both into Redis. |
| Frontend | The new website files are prepared for the strict CSP (no inline event handlers, nonce placeholders), but the sign-in screen and final assembly still need to be finished. |

Accepted risks: inline `style=""` attributes are allowed (`style-src-attr`) because the page styles many elements that way; scripts are not. Backups are on the same disk: copy them off the server.

## 4. How to verify (do these in order)

**1. Run the automated attack suite** (about 1 minute). It starts its own server in a temp folder, so it never touches your data.
```
javac PayPilotServer.java
python3 security-tests/verify_security.py
```
Expected last line: `101 passed, 0 failed`. Each line names the attack it simulates (CSRF, session fixation, JSON bomb, role escalation, brute force, TOTP replay, path traversal and more).

**2. Check it by hand** (server running, replace the host):
```
curl -i http://127.0.0.1:8080/api/employees            # 401, no data
curl -i -H "Origin: https://evil.example" http://127.0.0.1:8080/api/health   # no Access-Control-Allow-Origin
curl -i http://127.0.0.1:8080/PayPilotServer.java      # 404
head -c 7 paypilot-data.json                           # PPENC1: means encrypted
tail -n 5 security.log                                 # recent security events
ls -l paypilot-data.json backups/                      # -rw------- permissions, backups exist
```
In a browser: sign in, open DevTools, Application, Cookies. The session cookie must show **HttpOnly** and **SameSite=Strict** (and **Secure** on HTTPS). In the Console, `document.cookie` must NOT list it.

**3. Check the live site from outside** (after you deploy with HTTPS):
- https://observatory.mozilla.org and https://securityheaders.com: aim for A or A+.
- https://www.ssllabs.com/ssltest/: aim for A or A+ (TLS 1.2/1.3 only).
- OWASP ZAP baseline scan: `docker run -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t https://your-site`
- Run it only against a site you own.

**4. Check your secrets are clean**: `git log -p | grep -iE "api[_-]?key|password|secret"` should find nothing real. `.env`, data, logs and backups are in `.gitignore`.

**5. Independent review**: before real payroll data, ask a professional tester or use a service such as StackHawk, and re-run step 1 after every change.

## 5. Cloudflare and server checklist (your account, not code)

1. Add the domain to Cloudflare, set SSL/TLS mode to **Full (strict)**, turn on **Always Use HTTPS**, **HSTS**, **Minimum TLS 1.2**, **Automatic HTTPS Rewrites**.
2. Security: enable the **Managed WAF ruleset** and **OWASP Core Ruleset**; **Bot Fight Mode**; **Browser Integrity Check**.
3. WAF custom rule: block or challenge `http.request.uri.path contains "/api/auth/login"` when requests exceed 10 per minute per IP (Rate limiting rule). This sits in front of the app's own limit.
4. DDoS protection is on by default; set Security Level to Medium or High.
5. Firewall the origin: allow ports 80 and 443 only from Cloudflare's published IP ranges, and block everything else (`ufw` or a cloud security group). Keep SSH on a key and restrict by IP.
6. Cache: only cache static assets. Never cache `/api/*` (the app already sends `no-store`).
7. Set `PAYPILOT_TRUST_PROXY=true` only when the origin is reachable **only** through Cloudflare, otherwise clients can spoof their IP.
8. Store `.env` in a secrets manager (or root-only `/etc/paypilot.env`, mode 600). Back up `PAYPILOT_DATA_KEY` separately: **without it the encrypted data cannot be recovered**.
9. Run the app with `deploy/paypilot.service` (sandboxed, non-root). Keep Java and the OS patched.

## 6. Plan for Google sign-in (when you have the keys)

1. In Google Cloud Console create an OAuth client (Web application), add your HTTPS redirect URI, and copy the client id and secret into `.env`.
2. Use the authorization-code flow with **PKCE** and a random `state` and `nonce`.
3. On the callback, exchange the code on the server, then verify the ID token: signature against Google's keys (`https://www.googleapis.com/oauth2/v3/certs`), `iss`, `aud` equal to your client id, `exp`, `nonce`, and `email_verified`.
4. Match the verified email to an existing user (do not auto-create admins), then create the same server session as password sign-in. Keep MFA for admin accounts.
5. Add tests for a forged token, wrong audience, expired token and replayed state.

## 7. Standards mapping

| Standard | Covered by |
|---|---|
| OWASP Top 10 A01 Broken Access Control | RBAC, ownership check on payslips, CSRF, tests in the RBAC section |
| A02 Cryptographic Failures | PBKDF2 600k, AES-256-GCM, TLS 1.2/1.3, HSTS, Secure cookies |
| A03 Injection | No SQL/shell/XML in server, input validation, CSP, output escaping |
| A04 Insecure Design | Maker-checker for payments, rate limits, size limits, lockout |
| A05 Security Misconfiguration | Headers, CORS allow-list, loopback bind, static allow-list, no verbose errors |
| A06 Vulnerable Components | Zero third-party dependencies |
| A07 Identification and Authentication Failures | MFA, lockout, session rotation, timeouts, password policy |
| A08 Software and Data Integrity | Refuses to overwrite unreadable data, atomic writes, encrypted backups |
| A09 Logging and Monitoring Failures | security.log, alerts, audit log with actor |
| A10 SSRF | Only one fixed outbound URL |
| NIST SP 800-63B (passwords, MFA, sessions) | Length-based policy, TOTP second factor, session timeouts, hashed secrets |
| NIST SP 800-132 (password hashing) | PBKDF2 with salt and high iteration count |
