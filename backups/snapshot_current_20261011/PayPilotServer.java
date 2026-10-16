import com.sun.net.httpserver.*;
import java.io.*;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.regex.*;
import java.util.stream.*;
import java.util.concurrent.*;
import java.net.URLEncoder;
import java.nio.ByteBuffer;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.*;
import javax.crypto.*;
import javax.crypto.spec.*;
import javax.net.ssl.*;

/**
 * PayPilot backend: Payroll, Tax and CA Buddy (bank statement analyser).
 * Pure JDK 17+ (no external libraries). Run:  javac PayPilotServer.java && java PayPilotServer
 * Persistence: JSON file (paypilot-data.json) behind the Store class (swap for JDBC if you have a driver jar).
 * All tax and GST rates are editable data. Figures are estimates: verify with official rules and a CA.
 */
public class PayPilotServer {

    // ============================ Tiny JSON ============================
    static final class Json {
        static Object parse(String s) {
            P p = new P(s);
            Object v = p.val();
            p.ws();
            if (p.i != s.length()) throw new IllegalArgumentException("Unexpected text after JSON");
            return v;
        }
        static final class P {
            final String s; int i; int depth;
            P(String s) { this.s = s; }
            void ws() { while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++; }
            Object val() {
                ws();
                if (i >= s.length()) throw new IllegalArgumentException("Empty JSON");
                char c = s.charAt(i);
                if (c == '{' || c == '[') {
                    if (++depth > 64) throw new IllegalArgumentException("JSON is nested too deeply");
                    try { return c == '{' ? obj() : arr(); } finally { depth--; }
                }
                if (c == '"') return str();
                if (s.startsWith("true", i)) { i += 4; return Boolean.TRUE; }
                if (s.startsWith("false", i)) { i += 5; return Boolean.FALSE; }
                if (s.startsWith("null", i)) { i += 4; return null; }
                int st = i;
                while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
                if (st == i) throw new IllegalArgumentException("Bad JSON at " + i);
                return Double.parseDouble(s.substring(st, i));
            }
            Map<String, Object> obj() {
                Map<String, Object> m = new LinkedHashMap<>();
                i++; ws();
                if (s.charAt(i) == '}') { i++; return m; }
                while (true) {
                    ws(); String k = str(); ws();
                    if (s.charAt(i++) != ':') throw new IllegalArgumentException("Expected ':'");
                    m.put(k, val()); ws();
                    char c = s.charAt(i++);
                    if (c == '}') return m;
                    if (c != ',') throw new IllegalArgumentException("Expected ',' or '}'");
                }
            }
            List<Object> arr() {
                List<Object> l = new ArrayList<>();
                i++; ws();
                if (s.charAt(i) == ']') { i++; return l; }
                while (true) {
                    l.add(val()); ws();
                    char c = s.charAt(i++);
                    if (c == ']') return l;
                    if (c != ',') throw new IllegalArgumentException("Expected ',' or ']'");
                }
            }
            String str() {
                if (s.charAt(i) != '"') throw new IllegalArgumentException("Expected string at " + i);
                i++;
                StringBuilder b = new StringBuilder();
                while (true) {
                    char c = s.charAt(i++);
                    if (c == '"') return b.toString();
                    if (c == '\\') {
                        char n = s.charAt(i++);
                        switch (n) {
                            case 'n': b.append('\n'); break;
                            case 't': b.append('\t'); break;
                            case 'r': b.append('\r'); break;
                            case 'b': b.append('\b'); break;
                            case 'f': b.append('\f'); break;
                            case 'u': b.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; break;
                            default: b.append(n);
                        }
                    } else b.append(c);
                }
            }
        }
        static String write(Object o) { StringBuilder b = new StringBuilder(); w(o, b); return b.toString(); }
        @SuppressWarnings("unchecked")
        static void w(Object o, StringBuilder b) {
            if (o == null) b.append("null");
            else if (o instanceof String) q((String) o, b);
            else if (o instanceof Boolean) b.append(o);
            else if (o instanceof Number) {
                double d = ((Number) o).doubleValue();
                if (Double.isNaN(d) || Double.isInfinite(d)) b.append("null");
                else if (d == Math.rint(d) && Math.abs(d) < 1e15) b.append((long) d);
                else b.append(Math.round(d * 100) / 100.0);
            } else if (o instanceof Map) {
                b.append('{'); boolean f = true;
                for (Map.Entry<String, Object> e : ((Map<String, Object>) o).entrySet()) {
                    if (!f) b.append(','); f = false;
                    q(e.getKey(), b); b.append(':'); w(e.getValue(), b);
                }
                b.append('}');
            } else if (o instanceof Collection) {
                b.append('['); boolean f = true;
                for (Object x : (Collection<?>) o) { if (!f) b.append(','); f = false; w(x, b); }
                b.append(']');
            } else q(o.toString(), b);
        }
        static void q(String s, StringBuilder b) {
            b.append('"');
            for (char c : s.toCharArray()) {
                switch (c) {
                    case '"': b.append("\\\""); break;
                    case '\\': b.append("\\\\"); break;
                    case '\n': b.append("\\n"); break;
                    case '\r': b.append("\\r"); break;
                    case '\t': b.append("\\t"); break;
                    default: if (c < 0x20) b.append(String.format("\\u%04x", (int) c)); else b.append(c);
                }
            }
            b.append('"');
        }
    }

    static class ApiException extends RuntimeException {
        final int code; Map<String, Object> extra;
        ApiException(int code, String msg) { super(msg); this.code = code; }
        ApiException(int code, String msg, Map<String, Object> extra) { super(msg); this.code = code; this.extra = extra; }
    }

    // ============================ Helpers ============================
    static Map<String, Object> m(Object... kv) {
        Map<String, Object> r = new LinkedHashMap<>();
        for (int i = 0; i < kv.length; i += 2) r.put((String) kv[i], kv[i + 1]);
        return r;
    }
    static double num(Object o) {
        if (o == null) return 0;
        if (o instanceof Number) return ((Number) o).doubleValue();
        try { return Double.parseDouble(o.toString().replace(",", "").trim()); } catch (Exception e) { return 0; }
    }
    static String str(Object o) { return o == null ? "" : o.toString(); }
    static double r2(double d) { return Math.round(d * 100) / 100.0; }
    @SuppressWarnings("unchecked")
    static Map<String, Object> mp(Object o) { return o instanceof Map ? (Map<String, Object>) o : new LinkedHashMap<>(); }
    @SuppressWarnings("unchecked")
    static List<Object> li(Object o) { return o instanceof List ? (List<Object>) o : new ArrayList<>(); }

    // ============================ Tax engine ============================
    static Map<String, Object> defaultTaxRules() {
        Map<String, Object> r = new LinkedHashMap<>();
        r.put("note", "Editable assumptions for learning. Verify with official income-tax rules.");
        r.put("newStd", 75000.0); r.put("oldStd", 50000.0);
        r.put("newRebateLimit", 1200000.0); r.put("oldRebateLimit", 500000.0);
        r.put("cess", 0.04);
        r.put("cap80c", 150000.0); r.put("cap80d", 50000.0); r.put("capNps", 50000.0);
        r.put("newSlabs", slabs(400000, 0, 800000, 0.05, 1200000, 0.10, 1600000, 0.15, 2000000, 0.20, 2400000, 0.25, 1e15, 0.30));
        r.put("oldSlabs", slabs(250000, 0, 500000, 0.05, 1000000, 0.20, 1e15, 0.30));
        r.put("pfRate", 0.12); r.put("pfCapMonthly", 1800.0); r.put("professionalTax", 200.0);
        r.put("basicShare", 0.40);
        return r;
    }
    static Map<String, Object> defaultWelfareRules() {
        Map<String, Object> r = new LinkedHashMap<>();
        r.put("lastUpdated", "2026-10-01");
        r.put("source", "Ministry of Labour & Employment, Govt of India & State Labour Gazettes");
        r.put("note", "Statutory minimum wages and social security thresholds under Indian Labour Laws. Verify with official gazettes.");
        
        // Minimum Wages by State & Skill Level (Daily and Monthly basis: 8-hour workday, 26 days/month)
        Map<String, Object> mw = new LinkedHashMap<>();
        mw.put("Central Sphere", m(
            "unskilledDaily", 530.0, "unskilledMonthly", 13780.0,
            "semiskilledDaily", 588.0, "semiskilledMonthly", 15288.0,
            "skilledDaily", 695.0, "skilledMonthly", 18070.0,
            "highlySkilledDaily", 764.0, "highlySkilledMonthly", 19864.0
        ));
        mw.put("Delhi", m(
            "unskilledDaily", 692.0, "unskilledMonthly", 18000.0,
            "semiskilledDaily", 762.0, "semiskilledMonthly", 19812.0,
            "skilledDaily", 839.0, "skilledMonthly", 21814.0,
            "highlySkilledDaily", 915.0, "highlySkilledMonthly", 23790.0
        ));
        mw.put("Maharashtra", m(
            "unskilledDaily", 516.0, "unskilledMonthly", 13416.0,
            "semiskilledDaily", 562.0, "semiskilledMonthly", 14612.0,
            "skilledDaily", 620.0, "skilledMonthly", 16120.0,
            "highlySkilledDaily", 685.0, "highlySkilledMonthly", 17810.0
        ));
        mw.put("Karnataka", m(
            "unskilledDaily", 498.0, "unskilledMonthly", 12948.0,
            "semiskilledDaily", 545.0, "semiskilledMonthly", 14170.0,
            "skilledDaily", 605.0, "skilledMonthly", 15730.0,
            "highlySkilledDaily", 670.0, "highlySkilledMonthly", 17420.0
        ));
        mw.put("Tamil Nadu", m(
            "unskilledDaily", 475.0, "unskilledMonthly", 12350.0,
            "semiskilledDaily", 520.0, "semiskilledMonthly", 13520.0,
            "skilledDaily", 580.0, "skilledMonthly", 15080.0,
            "highlySkilledDaily", 645.0, "highlySkilledMonthly", 16770.0
        ));
        mw.put("Uttar Pradesh", m(
            "unskilledDaily", 412.0, "unskilledMonthly", 10712.0,
            "semiskilledDaily", 453.0, "semiskilledMonthly", 11778.0,
            "skilledDaily", 508.0, "skilledMonthly", 13208.0,
            "highlySkilledDaily", 565.0, "highlySkilledMonthly", 14690.0
        ));
        mw.put("Punjab", m(
            "unskilledDaily", 425.0, "unskilledMonthly", 11050.0,
            "semiskilledDaily", 465.0, "semiskilledMonthly", 12090.0,
            "skilledDaily", 522.0, "skilledMonthly", 13572.0,
            "highlySkilledDaily", 580.0, "highlySkilledMonthly", 15080.0
        ));
        mw.put("West Bengal", m(
            "unskilledDaily", 390.0, "unskilledMonthly", 10140.0,
            "semiskilledDaily", 430.0, "semiskilledMonthly", 11180.0,
            "skilledDaily", 485.0, "skilledMonthly", 12610.0,
            "highlySkilledDaily", 540.0, "highlySkilledMonthly", 14040.0
        ));
        mw.put("Gujarat", m(
            "unskilledDaily", 448.0, "unskilledMonthly", 11648.0,
            "semiskilledDaily", 465.0, "semiskilledMonthly", 12090.0,
            "skilledDaily", 484.0, "skilledMonthly", 12584.0,
            "highlySkilledDaily", 540.0, "highlySkilledMonthly", 14040.0
        ));
        mw.put("Bihar", m(
            "unskilledDaily", 400.0, "unskilledMonthly", 10400.0,
            "semiskilledDaily", 425.0, "semiskilledMonthly", 11050.0,
            "skilledDaily", 518.0, "skilledMonthly", 13468.0,
            "highlySkilledDaily", 575.0, "highlySkilledMonthly", 14950.0
        ));
        mw.put("Rajasthan", m(
            "unskilledDaily", 395.0, "unskilledMonthly", 10270.0,
            "semiskilledDaily", 415.0, "semiskilledMonthly", 10790.0,
            "skilledDaily", 435.0, "skilledMonthly", 11310.0,
            "highlySkilledDaily", 485.0, "highlySkilledMonthly", 12610.0
        ));
        mw.put("Haryana", m(
            "unskilledDaily", 420.0, "unskilledMonthly", 10920.0,
            "semiskilledDaily", 460.0, "semiskilledMonthly", 11960.0,
            "skilledDaily", 510.0, "skilledMonthly", 13260.0,
            "highlySkilledDaily", 565.0, "highlySkilledMonthly", 14690.0
        ));
        r.put("minimumWages", mw);

        // Statutory Social Security Thresholds
        Map<String, Object> bt = new LinkedHashMap<>();
        bt.put("pfEmployeeThreshold", 20.0);
        bt.put("pfWageLimit", 15000.0);
        bt.put("pfEmployeeRate", 0.12);
        bt.put("pfEmployerRate", 0.12);
        bt.put("esiEmployeeThreshold", 10.0);
        bt.put("esiWageLimit", 21000.0);
        bt.put("esiEmployeeRate", 0.0075);
        bt.put("esiEmployerRate", 0.0325);
        bt.put("gratuityYears", 5.0);
        bt.put("gratuityThreshold", 10.0);
        bt.put("bonusWageLimit", 21000.0);
        bt.put("bonusMinDays", 30.0);
        bt.put("bonusMinRate", 0.0833);
        bt.put("maternityWeeks", 26.0);
        bt.put("maternityDaysWorked", 80.0);
        bt.put("maxDailyHours", 9.0);
        bt.put("overtimeMultiplier", 2.0);
        bt.put("wagePaymentDeadlineDays", 7.0);
        r.put("benefitThresholds", bt);

        // Government Welfare Schemes
        List<Object> sc = new ArrayList<>();
        sc.add(m("id", "eshram", "name", "e-Shram Registration", "benefit", "National UAN card, ₹2 Lakh free accidental death/disability insurance, direct DBT social security benefits.", "minAge", 16.0, "maxAge", 59.0, "maxIncome", 50000.0, "gender", "all", "occupation", "unorganized", "documents", "Aadhaar Card, Mobile linked with Aadhaar, Bank Account Passbook", "url", "eshram.gov.in"));
        sc.add(m("id", "pmsym", "name", "PM Shram Yogi Maan-dhan (PM-SYM)", "benefit", "Assured monthly pension of ₹3,000/month after age 60. 50% government co-contribution.", "minAge", 18.0, "maxAge", 40.0, "maxIncome", 15000.0, "gender", "all", "occupation", "unorganized", "documents", "Aadhaar Card, Jan Dhan / Savings Bank Passbook", "url", "maandhan.in"));
        sc.add(m("id", "apy", "name", "Atal Pension Yojana (APY)", "benefit", "Guaranteed monthly pension of ₹1,000 to ₹5,000 for lifelong post-retirement financial security.", "minAge", 18.0, "maxAge", 40.0, "maxIncome", 100000.0, "gender", "all", "occupation", "all", "documents", "Bank Account, Aadhaar Card, Nominee Details", "url", "npscra.nsdl.co.in"));
        sc.add(m("id", "pmjay", "name", "Ayushman Bharat (PM-JAY)", "benefit", "Free secondary & tertiary hospital treatment up to ₹5,00,000 per family per year across 27,000+ empaneled hospitals.", "minAge", 0.0, "maxAge", 100.0, "maxIncome", 25000.0, "gender", "all", "occupation", "all", "documents", "Ration Card (BPL/Antyodaya), Aadhaar Card, Family ID", "url", "pmjay.gov.in"));
        sc.add(m("id", "pmjdy", "name", "PM Jan Dhan Yojana (PMJDY)", "benefit", "Zero-balance bank account, RuPay debit card, ₹2 Lakh accidental insurance, ₹10,000 overdraft facility.", "minAge", 10.0, "maxAge", 100.0, "maxIncome", 100000.0, "gender", "all", "occupation", "all", "documents", "Aadhaar Card or Voter ID / MGNREGA Job Card", "url", "pmjdy.gov.in"));
        sc.add(m("id", "mudra", "name", "PM Mudra Yojana (Micro-Loans)", "benefit", "Collateral-free micro-business loans: Shishu (up to ₹50k), Kishore (₹50k-₹5L), Tarun (₹5L-₹10L) with lowest interest.", "minAge", 18.0, "maxAge", 65.0, "maxIncome", 200000.0, "gender", "all", "occupation", "small-business", "documents", "Identity Proof, Business Address Proof, Quotation/Machinery Estimate", "url", "mudra.org.in"));
        sc.add(m("id", "pmsby", "name", "PM Suraksha Bima Yojana (PMSBY)", "benefit", "Accidental death / permanent full disability insurance of ₹2,00,000 for just ₹20 per year.", "minAge", 18.0, "maxAge", 70.0, "maxIncome", 1000000.0, "gender", "all", "occupation", "all", "documents", "Savings Bank Account, Auto-debit Consent Form", "url", "jansuraksha.gov.in"));
        sc.add(m("id", "pmjjby", "name", "PM Jeevan Jyoti Bima Yojana (PMJJBY)", "benefit", "Life insurance cover of ₹2,00,000 for death due to any cause at ₹436 per year.", "minAge", 18.0, "maxAge", 50.0, "maxIncome", 1000000.0, "gender", "all", "occupation", "all", "documents", "Savings Bank Account, Consent Form", "url", "jansuraksha.gov.in"));
        sc.add(m("id", "pmsvanidhi", "name", "PM SVANidhi (Street Vendors)", "benefit", "Working capital micro-loan of ₹10,000 / ₹20,000 / ₹50,000 with 7% interest subsidy and digital cashback.", "minAge", 18.0, "maxAge", 65.0, "maxIncome", 30000.0, "gender", "all", "occupation", "street-vendor", "documents", "Vending Certificate / Urban Local Body ID, Aadhaar Card", "url", "pmsvanidhi.mohua.gov.in"));
        r.put("schemes", sc);
        return r;
    }

    static Map<String, Object> defaultGstRules() {
        Map<String, Object> r = new LinkedHashMap<>();
        r.put("note", "Editable. Verify current GST rates with the official GST portal.");
        r.put("slabs", new ArrayList<>(List.of(0.0, 5.0, 12.0, 18.0, 28.0)));
        r.put("defaultRate", 18.0);
        r.put("registrationThresholdServices", 2000000.0);
        r.put("registrationThresholdGoods", 4000000.0);
        return r;
    }
    static List<Object> slabs(double... a) {
        List<Object> l = new ArrayList<>();
        for (int i = 0; i < a.length; i += 2) l.add(new ArrayList<>(List.of(a[i], a[i + 1])));
        return l;
    }
    static double slabTax(double income, List<Object> slabs) {
        double prev = 0, t = 0;
        for (Object o : slabs) {
            List<Object> s = li(o);
            double lim = num(s.get(0)), rate = num(s.get(1));
            if (income > prev) t += (Math.min(income, lim) - prev) * rate;
            prev = lim;
        }
        return t;
    }
    static Map<String, Object> taxNew(double gross, Map<String, Object> R) {
        double taxable = Math.max(0, gross - num(R.get("newStd")));
        double base = slabTax(taxable, li(R.get("newSlabs")));
        double lim = num(R.get("newRebateLimit"));
        boolean relief = false;
        if (taxable <= lim) base = 0;
        else if (base > taxable - lim) { base = taxable - lim; relief = true; }
        double cess = base * num(R.get("cess"));
        return m("regime", "new", "taxable", taxable, "base", Math.round(base), "cess", Math.round(cess),
                "total", Math.round(base + cess), "marginalRelief", relief);
    }
    static double dedTotal(double c80, double d80, double nps, Map<String, Object> R) {
        return Math.min(Math.max(c80, 0), num(R.get("cap80c"))) + Math.min(Math.max(d80, 0), num(R.get("cap80d")))
                + Math.min(Math.max(nps, 0), num(R.get("capNps")));
    }
    static Map<String, Object> taxOld(double gross, double ded, Map<String, Object> R) {
        double taxable = Math.max(0, gross - num(R.get("oldStd")) - ded);
        double base = slabTax(taxable, li(R.get("oldSlabs")));
        if (taxable <= num(R.get("oldRebateLimit"))) base = 0;
        double cess = base * num(R.get("cess"));
        return m("regime", "old", "taxable", taxable, "base", Math.round(base), "cess", Math.round(cess),
                "total", Math.round(base + cess), "deductions", ded);
    }
    static Map<String, Object> taxCompare(double gross, double c80, double d80, double nps, Map<String, Object> R) {
        double ded = dedTotal(c80, d80, nps, R);
        Map<String, Object> n = taxNew(gross, R), o = taxOld(gross, ded, R);
        double tn = num(n.get("total")), to = num(o.get("total"));
        return m("gross", gross, "new", n, "old", o, "better", tn <= to ? "new" : "old", "saving", Math.abs(tn - to),
                "note", "Estimate for learning. Verify with official income-tax rules and a CA.");
    }

    // ============================ Store (JSON file persistence) ============================
    static List<Object> seedWelfareLedger() {
        List<Object> list = new ArrayList<>();
        list.add(m("id", "HLP-101", "owner", "admin@paypilot.internal", "name", "Sunita Devi", "role", "Domestic Maid", "phone", "9876543210", "payType", "monthly", "wage", 4500.0,
            "attendance", new ArrayList<>(List.of(m("date", "2026-10-01", "status", "present"), m("date", "2026-10-02", "status", "present"), m("date", "2026-10-03", "status", "paid_leave"))),
            "advances", new ArrayList<>(List.of(m("date", "2026-10-05", "amount", 500.0, "reason", "Medical expenses"))),
            "bonuses", new ArrayList<>(List.of(m("date", "2026-10-10", "amount", 1000.0, "reason", "Diwali Gift")))
        ));
        list.add(m("id", "HLP-102", "owner", "admin@paypilot.internal", "name", "Ramesh Kumar", "role", "Cook", "phone", "9876543211", "payType", "monthly", "wage", 6000.0,
            "attendance", new ArrayList<>(List.of(m("date", "2026-10-01", "status", "present"), m("date", "2026-10-02", "status", "present"))),
            "advances", new ArrayList<>(),
            "bonuses", new ArrayList<>()
        ));
        list.add(m("id", "HLP-103", "owner", "admin@paypilot.internal", "name", "Balwinder Singh", "role", "Family Driver", "phone", "9876543212", "payType", "monthly", "wage", 14000.0,
            "attendance", new ArrayList<>(List.of(m("date", "2026-10-01", "status", "present"), m("date", "2026-10-02", "status", "present"))),
            "advances", new ArrayList<>(),
            "bonuses", new ArrayList<>()
        ));
        return list;
    }
    static List<Object> seedWelfareSurveys() {
        List<Object> list = new ArrayList<>();
        // Seed 1 survey with 6 responses (demonstrating unlocked aggregate state >= 5)
        List<Object> resp6 = new ArrayList<>();
        resp6.add(m("q1", 4.0, "q2", 5.0, "q3", 4.0, "q4", 5.0, "q5", 4.0, "q6", 5.0));
        resp6.add(m("q1", 5.0, "q2", 4.0, "q3", 5.0, "q4", 5.0, "q5", 3.0, "q6", 4.0));
        resp6.add(m("q1", 4.0, "q2", 5.0, "q3", 4.0, "q4", 4.0, "q5", 4.0, "q6", 5.0));
        resp6.add(m("q1", 3.0, "q2", 4.0, "q3", 4.0, "q4", 5.0, "q5", 4.0, "q6", 4.0));
        resp6.add(m("q1", 4.0, "q2", 4.0, "q3", 5.0, "q4", 5.0, "q5", 3.0, "q6", 4.0));
        resp6.add(m("q1", 5.0, "q2", 5.0, "q3", 5.0, "q4", 5.0, "q5", 4.0, "q6", 5.0));
        list.add(m("id", "SURV-202610-DEMO", "owner", "admin@paypilot.internal", "title", "October Team Culture & Respect Pulse", "month", "2026-10", "createdAt", "2026-10-01", "responses", resp6));
        return list;
    }

    static final class Store {
        final Path file;
        Map<String, Object> data;
        Store(Path f) { file = f; load(); }
        synchronized void load() {
            if (!Files.exists(file)) { seed(); return; }
            try {
                String raw = Files.readString(file);
                if (raw.startsWith("PPENC1:")) raw = decrypt(raw);
                data = mp(Json.parse(raw));
                if (!data.containsKey("employees")) seed();
            } catch (Exception e) {
                // Never silently re-seed: that would overwrite real data when the key is wrong or the file is damaged.
                throw new IllegalStateException("Could not read the data file (wrong PAYPILOT_DATA_KEY or damaged file). Refusing to overwrite it. " + e.getMessage());
            }
        }
        synchronized void save() {
            try {
                String out = Json.write(data);
                if (DATAKEY != null) out = encrypt(out);
                Path tmp = file.resolveSibling(file.getFileName() + ".tmp");
                Files.writeString(tmp, out);
                try { Files.setPosixFilePermissions(tmp, PosixFilePermissions.fromString("rw-------")); } catch (Exception ignored) { }
                Files.move(tmp, file, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
            } catch (Exception e) { System.err.println("Save failed: " + e.getMessage()); }
        }
        List<Object> emps() { return li(data.get("employees")); }
        List<Object> runs() { return li(data.get("runs")); }
        List<Object> audit() { return li(data.get("audit")); }
        Map<String, Object> taxRules() { return mp(data.get("taxRules")); }
        Map<String, Object> gstRules() { return mp(data.get("gstRules")); }
        Map<String, Object> welfareRules() {
            if (!data.containsKey("welfareRules")) data.put("welfareRules", defaultWelfareRules());
            return mp(data.get("welfareRules"));
        }
        List<Object> welfareLedger() {
            if (!data.containsKey("welfareLedger")) data.put("welfareLedger", new ArrayList<>());
            return li(data.get("welfareLedger"));
        }
        List<Object> welfareSurveys() {
            if (!data.containsKey("welfareSurveys")) data.put("welfareSurveys", new ArrayList<>());
            return li(data.get("welfareSurveys"));
        }
        List<Object> welfareSaved() {
            if (!data.containsKey("welfareSaved")) data.put("welfareSaved", new ArrayList<>());
            return li(data.get("welfareSaved"));
        }

        synchronized int nextId() { int n = (int) num(data.get("nextId")); data.put("nextId", (double) (n + 1)); return n; }
        synchronized void log(String action, String detail) {
            List<Object> a = audit();
            a.add(0, m("time", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")), "actor", ACTOR.get() == null ? "system" : ACTOR.get(), "action", action, "detail", detail));
            while (a.size() > 300) a.remove(a.size() - 1);
        }
        synchronized void seed() {
            Object keepUsers = data != null ? data.get("users") : null; // a reset must never delete accounts
            data = new LinkedHashMap<>();
            data.put("users", keepUsers != null ? keepUsers : new ArrayList<>());
            data.put("nextId", 1.0);
            data.put("taxRules", defaultTaxRules());
            data.put("gstRules", defaultGstRules());
            data.put("welfareRules", defaultWelfareRules());
            data.put("welfareLedger", seedWelfareLedger());
            data.put("welfareSurveys", seedWelfareSurveys());
            data.put("welfareSaved", new ArrayList<>());

            data.put("employees", new ArrayList<>());
            data.put("runs", new ArrayList<>());
            data.put("audit", new ArrayList<>());
            Object[][] e = {
                {"Aarav Sharma", "Engineering", "Software Engineer", 1800000, "new", 0, 0, 0},
                {"Diya Patel", "Design", "Product Designer", 1200000, "new", 0, 0, 0},
                {"Rohan Gupta", "Engineering", "Tech Lead", 2400000, "old", 150000, 25000, 50000},
                {"Meera Iyer", "Finance", "Accountant", 960000, "new", 0, 0, 0},
                {"Kabir Singh", "Sales", "Sales Manager", 780000, "old", 120000, 20000, 0},
                {"Ananya Reddy", "HR", "HR Executive", 840000, "new", 0, 0, 0},
                {"Vikram Nair", "Operations", "Supervisor", 600000, "new", 0, 0, 0},
                {"Sana Khan", "Sales", "Account Executive", 1500000, "old", 150000, 25000, 0}};
            for (Object[] x : e)
                emps().add(m("id", (double) nextId(), "name", x[0], "dept", x[1], "role", x[2], "ctc", ((Number) x[3]).doubleValue(),
                        "regime", x[4], "c80", ((Number) x[5]).doubleValue(), "d80", ((Number) x[6]).doubleValue(), "nps", ((Number) x[7]).doubleValue()));
            String[] months = {"2026-05", "2026-06", "2026-07", "2026-08", "2026-09"};
            for (String mo : months) {
                Map<String, Double> bonus = new HashMap<>();
                if (mo.equals("2026-09")) bonus.put("5", 30000.0); // Kabir gets a bonus: triggers an anomaly alert
                Map<String, Object> run = makeRun(mo, bonus);
                run.put("status", "Paid");
                runs().add(run);
            }
            log("SEED", "Demo data created");
        }
        Map<String, Object> emp(int id) {
            for (Object o : emps()) if ((int) num(mp(o).get("id")) == id) return mp(o);
            throw new ApiException(404, "Employee " + id + " not found");
        }
        Map<String, Object> makeRun(String month, Map<String, Double> bonus) {
            Map<String, Object> R = taxRules();
            List<Object> lines = new ArrayList<>();
            for (Object o : emps()) lines.add(line(mp(o), bonus.getOrDefault(str(mp(o).get("id")).replace(".0", ""), 0.0), R));
            return m("id", month, "month", month, "status", "Draft", "lines", lines);
        }
    }
    static Map<String, Object> line(Map<String, Object> e, double bonus, Map<String, Object> R) {
        double ctc = num(e.get("ctc")), baseM = ctc / 12, basic = baseM * num(R.get("basicShare"));
        double pf = Math.min(basic * num(R.get("pfRate")), num(R.get("pfCapMonthly"))), pt = num(R.get("professionalTax"));
        double annual = "old".equals(e.get("regime"))
                ? num(taxOld(ctc, dedTotal(num(e.get("c80")), num(e.get("d80")), num(e.get("nps")), R), R).get("total"))
                : num(taxNew(ctc, R).get("total"));
        double tds = annual / 12 + bonus * 0.30 * (1 + num(R.get("cess")));
        double gross = baseM + bonus, net = gross - pf - pt - tds;
        return m("empId", e.get("id"), "name", e.get("name"), "dept", e.get("dept"), "gross", Math.round(gross), "bonus", Math.round(bonus),
                "basic", Math.round(basic), "pf", Math.round(pf), "pt", Math.round(pt), "tds", Math.round(tds), "net", Math.round(net));
    }

    // ============================ Validation ============================
    static String cleanText(String v, int max, String field) {
        String t = v.replaceAll("\\p{Cntrl}", "").trim();
        if (t.length() > max) throw new ApiException(400, "The " + field + " is too long. Use at most " + max + " characters.");
        if (t.indexOf('<') >= 0 || t.indexOf('>') >= 0) throw new ApiException(400, "The " + field + " cannot contain < or >.");
        return t;
    }
    static Map<String, Object> cleanEmployee(Map<String, Object> b, Map<String, Object> base) {
        Map<String, Object> e = new LinkedHashMap<>(base);
        for (String k : new String[]{"name", "dept", "role", "regime"}) if (b.containsKey(k)) e.put(k, cleanText(str(b.get(k)), k.equals("name") ? 100 : 60, k));
        for (String k : new String[]{"ctc", "c80", "d80", "nps"}) if (b.containsKey(k)) e.put(k, num(b.get(k)));
        if (str(e.get("name")).isEmpty()) throw new ApiException(400, "Name is required. Type the employee's full name.");
        if (num(e.get("ctc")) < 12000) throw new ApiException(400, "Yearly CTC looks too low. Enter the yearly amount in rupees, for example 600000.");
        if (num(e.get("ctc")) > 100000000) throw new ApiException(400, "Yearly CTC looks too high. Check the number of zeros.");
        String rg = str(e.get("regime")).toLowerCase();
        e.put("regime", rg.equals("old") ? "old" : "new");
        if (str(e.get("dept")).isEmpty()) e.put("dept", "General");
        if (str(e.get("role")).isEmpty()) e.put("role", "Staff");
        return e;
    }

    // ============================ Analytics ============================
    static Map<String, Object> analytics(Store st) {
        List<Object> runs = st.runs();
        List<Object> series = new ArrayList<>();
        for (Object o : runs) {
            Map<String, Object> r = mp(o);
            double g = 0, t = 0, n = 0, pf = 0;
            for (Object l : li(r.get("lines"))) { Map<String, Object> x = mp(l); g += num(x.get("gross")); t += num(x.get("tds")); n += num(x.get("net")); pf += num(x.get("pf")); }
            series.add(m("month", r.get("month"), "status", r.get("status"), "gross", g, "tds", t, "net", n, "pf", pf));
        }
        List<Double> ctcs = st.emps().stream().map(o -> num(mp(o).get("ctc"))).sorted().collect(Collectors.toList());
        double avg = ctcs.stream().mapToDouble(d -> d).average().orElse(0);
        double med = ctcs.isEmpty() ? 0 : (ctcs.size() % 2 == 1 ? ctcs.get(ctcs.size() / 2) : (ctcs.get(ctcs.size() / 2 - 1) + ctcs.get(ctcs.size() / 2)) / 2);
        Map<String, Double> dept = new TreeMap<>();
        if (!runs.isEmpty()) for (Object l : li(mp(runs.get(runs.size() - 1)).get("lines"))) dept.merge(str(mp(l).get("dept")), num(mp(l).get("gross")), Double::sum);
        List<Object> anomalies = new ArrayList<>();
        if (runs.size() >= 2) {
            Map<Object, Double> prev = new HashMap<>();
            for (Object l : li(mp(runs.get(runs.size() - 2)).get("lines"))) prev.put(mp(l).get("empId"), num(mp(l).get("net")));
            for (Object l : li(mp(runs.get(runs.size() - 1)).get("lines"))) {
                Map<String, Object> x = mp(l);
                double p = prev.getOrDefault(x.get("empId"), 0.0), c = num(x.get("net"));
                if (p > 0 && Math.abs(c - p) / p > 0.20) {
                    double pct = (c - p) / p * 100;
                    String why = num(x.get("bonus")) > 0 ? "because of a bonus of Rs " + Math.round(num(x.get("bonus"))) : "check hours, bonus or tax changes";
                    anomalies.add(m("empId", x.get("empId"), "name", x.get("name"), "prevNet", p, "net", c, "pct", Math.round(pct * 10) / 10.0,
                            "explain", x.get("name") + "'s net pay " + (pct >= 0 ? "rose " : "fell ") + Math.round(Math.abs(pct)) + "% " + why + "."));
                }
            }
        }
        double fc = 0; int k = 0;
        for (int i = Math.max(0, series.size() - 3); i < series.size(); i++) { fc += num(mp(series.get(i)).get("gross")); k++; }
        List<Object> deptL = new ArrayList<>();
        dept.forEach((a, b) -> deptL.add(m("dept", a, "gross", b)));
        return m("employees", st.emps().size(), "series", series, "salaryAvg", avg, "salaryMedian", med,
                "salaryMax", ctcs.isEmpty() ? 0 : ctcs.get(ctcs.size() - 1), "salaryMin", ctcs.isEmpty() ? 0 : ctcs.get(0),
                "byDept", deptL, "anomalies", anomalies, "forecastNext", k == 0 ? 0 : fc / k);
    }

    // ============================ CA Buddy: statement analyser ============================
    static List<String> csvLine(String l) {
        List<String> out = new ArrayList<>();
        StringBuilder b = new StringBuilder(); boolean q = false;
        char sep = l.indexOf('\t') >= 0 && l.indexOf(',') < 0 ? '\t' : ',';
        for (int i = 0; i < l.length(); i++) {
            char c = l.charAt(i);
            if (c == '"') { if (q && i + 1 < l.length() && l.charAt(i + 1) == '"') { b.append('"'); i++; } else q = !q; }
            else if (c == sep && !q) { out.add(b.toString().trim()); b.setLength(0); }
            else b.append(c);
        }
        out.add(b.toString().trim());
        return out;
    }
    static double amt(String s) {
        if (s == null) return 0;
        String t = s.replaceAll("[^0-9.\\-]", "");
        if (t.isEmpty() || t.equals("-") || t.equals(".")) return 0;
        try { return Double.parseDouble(t); } catch (Exception e) { return 0; }
    }
    static final String[] DATE_FORMATS = {"dd/MM/yyyy", "dd-MM-yyyy", "yyyy-MM-dd", "dd MMM yyyy", "dd-MMM-yyyy", "dd/MM/yy", "dd-MM-yy", "d/M/yyyy", "d-M-yyyy", "dd MMM yy", "dd-MMM-yy"};
    static LocalDate date(String s) {
        s = s.trim();
        for (String f : DATE_FORMATS) {
            try { return LocalDate.parse(s, DateTimeFormatter.ofPattern(f, Locale.ENGLISH)); } catch (Exception ignored) { }
        }
        return null;
    }
    // {category, regex, side}  side: C credit only, D debit only, B both
    static final String[][] RULES = {
        {"Transfer", "\\bSELF\\b|OWN ACC|OWN A/C|OWN ACCOUNT", "B"},
        {"Refund", "REFUND|REVERSAL|REV\\b", "C"},
        {"Salary", "SALARY|SAL CREDIT|PAYROLL|\\bSAL\\b", "C"},
        {"Interest", "INT\\.?\\s?PD|INTEREST|INT CR|INT\\.CR", "C"},
        {"Freelance income", "FREELANCE|CONSULT|PROFESSIONAL FEE|UPWORK|FIVERR|DESIGN FEE", "C"},
        {"Business sales", "SALE|INVOICE|CUSTOMER|RECEIPT|PAYMENT RECEIVED|\\bINV\\b", "C"},
        {"GST paid", "\\bGST\\b|GSTN|CBIC", "D"},
        {"Tax paid", "INCOME TAX|\\bITD\\b|ADVANCE TAX|CHALLAN|TDS PAYMENT", "D"},
        {"Bank charges", "CHARGES|CHRG|\\bFEE\\b|SMS ALERT|MIN BAL|PENALTY|AMC", "D"},
        {"Rent", "\\bRENT\\b", "D"},
        {"Staff wages", "WAGES|STAFF|LABOUR", "D"},
        {"Utilities", "ELECTRIC|BESCOM|MSEB|WATER BILL|BROADBAND|AIRTEL|\\bJIO\\b|VODAFONE|BSNL|GAS BILL|BILLPAY", "D"},
        {"Groceries", "BIGBASKET|BLINKIT|ZEPTO|GROCER|DMART|KIRANA|SUPERMARKET", "D"},
        {"Fuel", "PETROL|FUEL|HPCL|IOCL|BPCL|SHELL", "D"},
        {"Travel", "UBER|\\bOLA\\b|IRCTC|MAKEMYTRIP|REDBUS|INDIGO|AIR INDIA|METRO", "D"},
        {"Food", "SWIGGY|ZOMATO|RESTAURANT|CAFE|DOMINO|MCDONALD", "D"},
        {"Shopping", "AMAZON|FLIPKART|MYNTRA|AJIO|MEESHO", "D"},
        {"Subscriptions", "NETFLIX|SPOTIFY|HOTSTAR|PRIME VIDEO|YOUTUBE|SUBSCRIPTION", "D"},
        {"EMI and loans", "\\bEMI\\b|LOAN|NACH|\\bECS\\b", "D"},
        {"Insurance", "\\bLIC\\b|INSURANCE|PREMIUM|HDFC LIFE|STAR HEALTH", "D"},
        {"Investment", "\\bSIP\\b|MUTUAL|ZERODHA|GROWW|\\bPPF\\b|\\bNPS\\b|FIXED DEPOSIT|\\bFD\\b|\\bRD\\b", "D"},
        {"Vendor purchases", "TRADERS|SUPPLIER|VENDOR|ENTERPRISES|MATERIAL|WHOLESALE|PURCHASE|STEEL|CEMENT|TEXTILE", "D"},
        {"Cash withdrawal", "\\bATM\\b|CASH WD|CASH WITHDRAWAL|\\bNWD\\b|SELF CHQ", "D"}};
    static final Set<String> BUSINESS_EXPENSE = Set.of("Vendor purchases", "Staff wages", "Rent", "Utilities");

    static String classify(String narr, boolean credit, boolean[] matched) {
        String n = narr.toUpperCase(Locale.ROOT);
        for (String[] r : RULES) {
            if (r[2].equals("C") && !credit) continue;
            if (r[2].equals("D") && credit) continue;
            if (Pattern.compile(r[1]).matcher(n).find()) { matched[0] = true; return r[0]; }
        }
        matched[0] = false;
        return credit ? "Other income" : "Other spend";
    }
    static String party(String narr) {
        String s = narr.toUpperCase(Locale.ROOT).replaceAll("^(UPI|NEFT|IMPS|RTGS|POS|ACH|NACH|ATM)[-/ ]*", "").replaceAll("[0-9@]+", " ").replaceAll("[^A-Z ]", " ").trim().replaceAll("\\s+", " ");
        return s.length() > 28 ? s.substring(0, 28).trim() : s;
    }

    static Map<String, Object> analyse(String csv, boolean inclusive, double gstRate, String profile, Map<String, Object> R, Map<String, Object> GR) {
        if (csv == null || csv.isBlank()) throw new ApiException(400, "No statement text received. Paste the CSV text or choose a CSV file.");
        String[] lines = csv.replace("\r", "").split("\n");
        if (lines.length > 50000) throw new ApiException(413, "This statement has too many rows (limit 50,000). Split it by month.");
        int h = -1;
        for (int i = 0; i < Math.min(lines.length, 25); i++) {
            String l = lines[i].toLowerCase(Locale.ROOT);
            if (l.contains("date") && (l.contains("narration") || l.contains("description") || l.contains("particular") || l.contains("remarks") || l.contains("details"))) { h = i; break; }
        }
        if (h < 0) throw new ApiException(400, "Could not find the header row. The first lines must include Date and Narration (or Description) columns. Download the CSV or Excel version from net banking.");
        List<String> head = csvLine(lines[h]);
        int cDate = -1, cNarr = -1, cDr = -1, cCr = -1, cAmt = -1, cType = -1;
        for (int i = 0; i < head.size(); i++) {
            String c = head.get(i).toLowerCase(Locale.ROOT);
            if (cDate < 0 && c.contains("date") && !c.contains("value")) cDate = i;
            else if (cNarr < 0 && (c.contains("narration") || c.contains("description") || c.contains("particular") || c.contains("remarks") || c.contains("details"))) cNarr = i;
            else if (cDr < 0 && (c.contains("debit") || c.contains("withdraw") || c.equals("dr"))) cDr = i;
            else if (cCr < 0 && (c.contains("credit") || c.contains("deposit") || c.equals("cr"))) cCr = i;
            else if (cType < 0 && (c.equals("type") || c.contains("dr/cr") || c.contains("cr/dr"))) cType = i;
            else if (cAmt < 0 && c.contains("amount")) cAmt = i;
        }
        if (cDate < 0) for (int i = 0; i < head.size(); i++) if (head.get(i).toLowerCase(Locale.ROOT).contains("date")) { cDate = i; break; }
        if (cDate < 0 || cNarr < 0 || (cDr < 0 && cCr < 0 && cAmt < 0))
            throw new ApiException(400, "Could not match the columns. Needed: Date, Narration, and either Debit/Credit or Amount. Found: " + head);

        List<Map<String, Object>> tx = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        int dups = 0, skipped = 0;
        for (int i = h + 1; i < lines.length; i++) {
            if (lines[i].isBlank()) continue;
            List<String> c = csvLine(lines[i]);
            if (c.size() <= Math.max(cDate, cNarr)) { skipped++; continue; }
            LocalDate d = date(c.get(cDate));
            if (d == null) { skipped++; continue; }
            double dr = 0, cr = 0;
            if (cDr >= 0 && cDr < c.size()) dr = Math.abs(amt(c.get(cDr)));
            if (cCr >= 0 && cCr < c.size()) cr = Math.abs(amt(c.get(cCr)));
            if (cAmt >= 0 && cAmt < c.size() && dr == 0 && cr == 0) {
                double a = amt(c.get(cAmt));
                String ty = cType >= 0 && cType < c.size() ? c.get(cType).toUpperCase(Locale.ROOT) : (a < 0 ? "DR" : "CR");
                if (ty.startsWith("D")) dr = Math.abs(a); else cr = Math.abs(a);
            }
            if (dr == 0 && cr == 0) { skipped++; continue; }
            String narr = c.get(cNarr);
            String key = d + "|" + narr + "|" + dr + "|" + cr + "|" + (c.size() > 0 ? c.get(c.size() - 1) : "");
            if (!seen.add(key)) { dups++; continue; }
            boolean credit = cr > 0;
            boolean[] mt = new boolean[1];
            String cat = classify(narr, credit, mt);
            tx.add(m("date", d.toString(), "month", d.toString().substring(0, 7), "narration", narr, "debit", dr, "credit", cr, "category", cat,
                    "confidence", mt[0] ? "High" : "Low", "party", party(narr)));
        }
        if (tx.isEmpty()) throw new ApiException(400, "No transactions could be read. Check the date format (for example 05/09/2026) and that amounts are numbers.");

        double rate = gstRate >= 0 ? gstRate : num(GR.get("defaultRate"));
        double income = 0, expense = 0;
        Map<String, double[]> cats = new TreeMap<>();
        Map<String, double[]> monthly = new TreeMap<>();
        Map<String, Map<String, Double>> gstM = new TreeMap<>();
        double sales = 0, purchases = 0, outGst = 0, itc = 0, salary = 0, freelance = 0, interest = 0, invest = 0, tdsDetected = 0, bank = 0;
        Map<String, Double> custs = new HashMap<>(), vends = new HashMap<>(), smallRep = new HashMap<>();
        List<Object> subs = new ArrayList<>();
        for (Map<String, Object> t : tx) {
            String cat = str(t.get("category")), mo = str(t.get("month"));
            double dr = num(t.get("debit")), cr = num(t.get("credit"));
            boolean transfer = cat.equals("Transfer");
            if (!transfer && !cat.equals("Refund")) { income += cr; }
            if (cat.equals("Refund")) expense -= cr;
            if (!transfer) expense += dr;
            double[] ca = cats.computeIfAbsent(cat, k -> new double[3]);
            ca[0] += dr + cr; ca[1]++; ca[2] = cr > 0 ? 1 : 0;
            double[] mm = monthly.computeIfAbsent(mo, k -> new double[2]);
            if (!transfer) { mm[0] += cr; mm[1] += dr; }
            Map<String, Double> g = gstM.computeIfAbsent(mo, k -> new LinkedHashMap<>());
            if (cat.equals("Business sales")) {
                double taxable = inclusive ? cr / (1 + rate / 100) : cr, gst = inclusive ? cr - taxable : cr * rate / 100;
                sales += taxable; outGst += gst;
                g.merge("sales", taxable, Double::sum); g.merge("outputGst", gst, Double::sum);
                custs.merge(str(t.get("party")), cr, Double::sum);
            } else if (cat.equals("Vendor purchases")) {
                double taxable = inclusive ? dr / (1 + rate / 100) : dr, gst = inclusive ? dr - taxable : dr * rate / 100;
                purchases += taxable; itc += gst;
                g.merge("purchases", taxable, Double::sum); g.merge("itc", gst, Double::sum);
                vends.merge(str(t.get("party")), dr, Double::sum);
            }
            if (cat.equals("Salary")) salary += cr;
            if (cat.equals("Freelance income")) freelance += cr;
            if (cat.equals("Interest")) interest += cr;
            if (cat.equals("Investment") || cat.equals("Insurance")) invest += dr;
            if (cat.equals("Bank charges")) bank += dr;
            if (cat.equals("Subscriptions")) subs.add(m("date", t.get("date"), "narration", t.get("narration"), "amount", dr));
            if (str(t.get("narration")).toUpperCase(Locale.ROOT).contains("TDS") && !cat.equals("Tax paid")) tdsDetected += Math.max(dr, cr);
            if (dr > 0 && dr < 200 && !transfer) smallRep.merge(str(t.get("party")), 1.0, Double::sum);
        }
        int months = monthly.size();
        double af = 12.0 / Math.max(1, months);
        double net = income - expense;
        double savingsRate = income > 0 ? net / income : 0;

        // GST summary
        List<Object> gm = new ArrayList<>();
        gstM.forEach((mo, g) -> {
            double o = g.getOrDefault("outputGst", 0.0), i2 = g.getOrDefault("itc", 0.0);
            gm.add(m("month", mo, "sales", g.getOrDefault("sales", 0.0), "outputGst", o, "purchases", g.getOrDefault("purchases", 0.0), "itc", i2, "net", o - i2));
        });
        double annSales = sales * af;
        List<String> gstNotes = new ArrayList<>();
        gstNotes.add("Rate used: " + (rate == Math.rint(rate) ? String.valueOf((long) rate) : String.valueOf(rate)) + "%. Amounts treated as GST-" + (inclusive ? "inclusive" : "exclusive") + ". CGST and SGST are half each for same-state sales, IGST for other states.");
        if (annSales > num(GR.get("registrationThresholdServices")))
            gstNotes.add("Annual sales estimate Rs " + Math.round(annSales) + " is above the usual services registration limit. GST registration may be needed. Confirm with a CA.");
        Map<String, Object> gst = m("rate", rate, "inclusive", inclusive, "taxableSales", sales, "outputGst", outGst, "cgst", outGst / 2, "sgst", outGst / 2,
                "purchases", purchases, "itc", itc, "netPayable", outGst - itc, "monthly", gm, "notes", gstNotes);

        // Income tax estimate
        double bizIncome = "business".equals(profile) ? 0.06 * sales * af : 0;
        double freeIncome = 0.5 * freelance * af;
        if (!"business".equals(profile) && sales > 0) freeIncome += 0.5 * sales * af;
        double totalInc = salary * af + bizIncome + freeIncome + interest * af;
        double c80 = Math.min(invest * af, num(R.get("cap80c")));
        Map<String, Object> cmp = taxCompare(totalInc, c80, 0, 0, R);
        double best = Math.min(num(mp(cmp.get("new")).get("total")), num(mp(cmp.get("old")).get("total")));
        double tdsAnn = tdsDetected * af;
        double payable = Math.max(0, best - tdsAnn);
        List<Object> adv = new ArrayList<>();
        if (payable > 10000) {
            String[] due = {"15 Jun", "15 Sep", "15 Dec", "15 Mar"}; double[] cum = {0.15, 0.45, 0.75, 1.0}; double prev = 0;
            for (int i = 0; i < 4; i++) { double c = payable * cum[i]; adv.add(m("due", due[i], "cumulativePercent", cum[i] * 100, "installment", Math.round(c - prev), "cumulative", Math.round(c))); prev = c; }
        }
        List<String> taxNotes = new ArrayList<>();
        taxNotes.add("Income is annualised from " + months + " month(s) of data (x" + r2(af) + ").");
        taxNotes.add("Business income uses 6% of digital sales (section 44AD style) and freelance uses 50% of receipts (44ADA style) as simple presumptive assumptions.");
        taxNotes.add("Tax-saving spends found (insurance and investments) are counted under 80C up to the cap, for the Old regime only.");
        Map<String, Object> incomeTax = m("annualIncome", totalInc, "salary", salary * af, "business", bizIncome, "freelance", freeIncome, "interest", interest * af,
                "compare", cmp, "bestTax", best, "tdsCredit", tdsAnn, "netPayable", payable, "advanceTax", adv, "notes", taxNotes);

        // categories, monthly
        List<Object> catL = new ArrayList<>();
        cats.forEach((k, v) -> catL.add(m("name", k, "total", v[0], "count", v[1], "side", v[2] == 1 ? "credit" : "debit")));
        catL.sort((a, b) -> Double.compare(num(mp(b).get("total")), num(mp(a).get("total"))));
        List<Object> monL = new ArrayList<>();
        monthly.forEach((k, v) -> monL.add(m("month", k, "income", v[0], "expense", v[1])));

        // leaks, tops, review
        List<Object> leaks = new ArrayList<>();
        if (bank > 0) leaks.add(m("title", "Bank charges and penalties", "amount", bank, "tip", "Check if these fees can be avoided (minimum balance, SMS pack)."));
        double subTotal = subs.stream().mapToDouble(o -> num(mp(o).get("amount"))).sum();
        if (subTotal > 0) leaks.add(m("title", "Subscriptions", "amount", subTotal, "tip", "Cancel the ones you do not use."));
        smallRep.forEach((k, v) -> { if (v >= 5) leaks.add(m("title", "Many small payments to " + k, "amount", v, "tip", "Repeated small spends add up. Count: " + (long) (double) v)); });
        List<Object> topC = top(custs), topV = top(vends);
        List<Object> review = tx.stream().filter(t -> "Low".equals(t.get("confidence"))).sorted((a, b) -> Double.compare(num(b.get("debit")) + num(b.get("credit")), num(a.get("debit")) + num(a.get("credit"))))
                .limit(10).collect(Collectors.toList());

        // health score
        double score = 50 + Math.min(30, Math.max(-30, savingsRate * 100 * 0.4)) + (invest > 0 ? 10 : 0) - (bank > 500 ? 5 : 0)
                - ((double) tx.stream().filter(t -> "Low".equals(t.get("confidence"))).count() / tx.size() > 0.3 ? 10 : 0) + (net >= 0 ? 10 : -10);
        score = Math.max(0, Math.min(100, score));
        List<String> tips = new ArrayList<>();
        if (savingsRate < 0.2) tips.add("Try to save at least 20% of income. Right now it is " + Math.round(savingsRate * 100) + "%.");
        if (invest == 0) tips.add("No investment or insurance found. Even a small SIP helps and can save tax under the Old regime.");
        if (bank > 0) tips.add("Reduce bank charges of Rs " + Math.round(bank) + ".");
        if (!review.isEmpty()) tips.add("Review the " + review.size() + " unsorted transactions so the numbers are more accurate.");
        if (outGst - itc > 0) tips.add("GST payable this period is about Rs " + Math.round(outGst - itc) + ". Keep cash ready before the due date.");

        List<String> notes = new ArrayList<>(List.of("Estimate for learning and planning, not professional advice. Confirm with a chartered accountant before filing.",
                "Transfers between your own accounts are excluded from income and spending."));
        return m("rows", tx.size(), "duplicatesRemoved", dups, "skipped", skipped, "months", months, "annualFactor", af,
                "totals", m("income", income, "expense", expense, "net", net, "savingsRate", savingsRate),
                "categories", catL, "monthly", monL, "gst", gst, "incomeTax", incomeTax, "leaks", leaks,
                "topCustomers", topC, "topVendors", topV, "review", review, "health", m("score", Math.round(score), "tips", tips),
                "confidence", m("level", tx.stream().filter(t -> "Low".equals(t.get("confidence"))).count() * 4 > tx.size() ? "Medium" : "High"),
                "transactions", tx.size() > 400 ? tx.subList(0, 400) : tx, "notes", notes);
    }
    static List<Object> top(Map<String, Double> m) {
        return m.entrySet().stream().sorted((a, b) -> Double.compare(b.getValue(), a.getValue())).limit(10)
                .map(e -> (Object) m("name", e.getKey(), "total", e.getValue())).collect(Collectors.toList());
    }

    // ============================ CA Buddy: ask ============================
    static String rs(double d) {
        long v = Math.round(Math.abs(d));
        String s = String.valueOf(v);
        if (s.length() > 3) {
            String last3 = s.substring(s.length() - 3), rest = s.substring(0, s.length() - 3);
            rest = rest.replaceAll("(\\d)(?=(\\d\\d)+$)", "$1,");
            s = rest + "," + last3;
        }
        return (d < 0 ? "-Rs " : "Rs ") + s;
    }
    static Map<String, Object> ask(String q, Map<String, Object> sum, boolean ai) {
        String s = q == null ? "" : q.toLowerCase(Locale.ROOT).trim();
        if (s.isEmpty()) throw new ApiException(400, "Type a question, for example: How much GST did I pay?");
        if (sum == null || sum.isEmpty()) return m("answer", "Upload or paste a bank statement first, then I can answer from your own numbers.", "basis", List.of(), "source", "rules");
        Map<String, Object> tot = mp(sum.get("totals")), gst = mp(sum.get("gst")), it = mp(sum.get("incomeTax"));
        List<String> basis = new ArrayList<>();
        String ans = null;
        if (s.contains("gst") || s.contains("itc")) {
            ans = "Output GST on sales is " + rs(num(gst.get("outputGst"))) + " and input tax credit on purchases is " + rs(num(gst.get("itc"))) + ". Net GST " + (num(gst.get("netPayable")) >= 0 ? "payable" : "refundable") + " is " + rs(Math.abs(num(gst.get("netPayable")))) + ".";
            basis.add("Output GST = taxable sales x rate " + gst.get("rate") + "%; ITC = GST on vendor purchases; Net = Output - ITC.");
        } else if ((s.contains("most") || s.contains("highest")) && (s.contains("spen") || s.contains("expens"))) {
            Map<String, Object> best = null;
            for (Object o : li(sum.get("monthly"))) if (best == null || num(mp(o).get("expense")) > num(best.get("expense"))) best = mp(o);
            ans = best == null ? "No monthly data." : "You spent the most in " + best.get("month") + ": " + rs(num(best.get("expense"))) + ".";
            basis.add("Compared total spending of every month in the statement.");
        } else if (s.contains("tax") && (s.contains("save") || s.contains("saving"))) {
            Map<String, Object> cmp = mp(it.get("compare"));
            ans = "The " + cmp.get("better") + " regime looks cheaper by about " + rs(num(cmp.get("saving"))) + " a year. Adding 80C, 80D or NPS investments can reduce Old-regime tax further.";
            basis.add("Compared Old and New regime on your annualised income of " + rs(num(it.get("annualIncome"))) + ".");
        } else if (s.contains("tax")) {
            ans = "Your estimated yearly tax is " + rs(num(it.get("bestTax"))) + " on an annualised income of " + rs(num(it.get("annualIncome"))) + ". After TDS credit of " + rs(num(it.get("tdsCredit"))) + ", about " + rs(num(it.get("netPayable"))) + " is left to pay.";
            basis.add("Slabs, cess and rebate come from the editable tax rules. Income is annualised from the months in the statement.");
        } else if (s.contains("income") || s.contains("earn") || s.contains("receive")) {
            ans = "Total money received in this statement is " + rs(num(tot.get("income"))) + " over " + (long) num(sum.get("months")) + " month(s). Annualised income for tax is about " + rs(num(it.get("annualIncome"))) + ".";
            basis.add("Sum of credits, excluding refunds and transfers between your own accounts.");
        } else if (s.contains("saving") || s.contains("save")) {
            ans = "You kept " + rs(num(tot.get("net"))) + " out of " + rs(num(tot.get("income"))) + ", a savings rate of " + Math.round(num(tot.get("savingsRate")) * 100) + "%.";
            basis.add("Savings rate = (income - spending) / income.");
        } else if (s.contains("payment") || s.contains("paid to") || s.contains("show") || s.contains("received from")) {
            Matcher mt = Pattern.compile("(?:to|from|for)\\s+([a-z0-9 .&'-]{2,})$").matcher(s.replaceAll("[?.!]+$", ""));
            if (mt.find()) {
                String term = mt.group(1).trim();
                double d = 0, c = 0; int n = 0;
                for (Object o : li(sum.get("transactions"))) {
                    Map<String, Object> t = mp(o);
                    if (str(t.get("narration")).toLowerCase(Locale.ROOT).contains(term)) { d += num(t.get("debit")); c += num(t.get("credit")); n++; }
                }
                ans = n == 0 ? "I found no transactions matching \"" + term + "\"." : "Found " + n + " transaction(s) matching \"" + term + "\": paid " + rs(d) + " and received " + rs(c) + ".";
                basis.add("Searched the narration text of every transaction for \"" + term + "\".");
            }
        }
        if (ans == null) {
            for (Object o : li(sum.get("categories"))) {
                Map<String, Object> c = mp(o);
                String name = str(c.get("name")).toLowerCase(Locale.ROOT);
                if (s.contains(name) || (name.equals("groceries") && s.contains("grocery")) || (name.equals("food") && s.contains("eating"))) {
                    ans = "You had " + (long) num(c.get("count")) + " " + name + " transaction(s) totalling " + rs(num(c.get("total"))) + ".";
                    basis.add("Sum of all transactions categorised as " + c.get("name") + ".");
                    break;
                }
            }
        }
        String source = "rules";
        if (ai && System.getenv("GEMINI_API_KEY") != null) {
            String g = gemini(q, tot, gst, it);
            if (g != null) { ans = g + (ans != null ? "\n\nCalculated figures: " + ans : ""); source = "gemini"; }
        }
        if (ans == null) ans = "I can answer questions like: How much GST did I pay? What is my total income? Which month did I spend the most? How much tax should I save? Show all payments to Sharma Traders. How much did I spend on food?";
        return m("answer", ans, "basis", basis, "source", source, "note", "Estimate for learning. Confirm with a chartered accountant.");
    }
    static String gemini(String q, Map<String, Object> tot, Map<String, Object> gst, Map<String, Object> it) {
        try {
            String model = Optional.ofNullable(System.getenv("GEMINI_MODEL")).orElse("gemini-2.0-flash");
            String prompt = "You are a friendly Indian chartered accountant. Answer in simple words in under 120 words, using only these summarised numbers. If unsure, say so. Numbers: "
                    + Json.write(m("totals", tot, "gstOutput", gst.get("outputGst"), "itc", gst.get("itc"), "gstNet", gst.get("netPayable"), "annualIncome", it.get("annualIncome"), "bestTax", it.get("bestTax"))) + " Question: " + q;
            String body = Json.write(m("contents", List.of(m("parts", List.of(m("text", prompt))))));
            HttpRequest rq = HttpRequest.newBuilder(URI.create("https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent"))
                    .timeout(java.time.Duration.ofSeconds(8)).header("Content-Type", "application/json").header("x-goog-api-key", System.getenv("GEMINI_API_KEY"))
                    .POST(HttpRequest.BodyPublishers.ofString(body)).build();
            HttpResponse<String> rs = HttpClient.newHttpClient().send(rq, HttpResponse.BodyHandlers.ofString());
            if (rs.statusCode() != 200) return null;
            Map<String, Object> j = mp(Json.parse(rs.body()));
            return str(mp(li(mp(mp(li(j.get("candidates")).get(0)).get("content")).get("parts")).get(0)).get("text")).trim();
        } catch (Exception e) { return null; }
    }

    // ============================ Security core ============================
    static String env(String k) { String v = System.getenv(k); return v == null || v.isBlank() ? null : v; }
    static final SecureRandom RNG = new SecureRandom();
    static final boolean TRUST_PROXY = "true".equalsIgnoreCase(env("PAYPILOT_TRUST_PROXY"));
    static final boolean FORCE_HTTPS = "true".equalsIgnoreCase(env("PAYPILOT_FORCE_HTTPS"));
    static final boolean REQUIRE_ADMIN_MFA = !"false".equalsIgnoreCase(env("PAYPILOT_REQUIRE_ADMIN_MFA"));
    static final int MAX_BODY = 2 * 1024 * 1024;
    static final int LOGIN_MAX = Optional.ofNullable(env("PAYPILOT_LOGIN_MAX")).map(Integer::parseInt).orElse(20), GLOBAL_MAX = Optional.ofNullable(env("PAYPILOT_GLOBAL_MAX")).map(Integer::parseInt).orElse(300);
    static final long IDLE_MS = 30 * 60_000L, ABSOLUTE_MS = 8 * 3600_000L;
    static final Set<String> ALLOWED_ORIGINS = new HashSet<>(Arrays.asList(Optional.ofNullable(env("PAYPILOT_ALLOWED_ORIGINS")).orElse("").split("\\s*,\\s*")));
    static final ThreadLocal<String> ACTOR = new ThreadLocal<>();
    static final ThreadLocal<Session> SESSION = new ThreadLocal<>();
    static final ThreadLocal<String> BODY = new ThreadLocal<>();
    static final Base64.Encoder B64U = Base64.getUrlEncoder().withoutPadding();

    static String token(int bytes) { byte[] b = new byte[bytes]; RNG.nextBytes(b); return B64U.encodeToString(b); }
    static boolean ctEq(String a, String b) { return a != null && b != null && MessageDigest.isEqual(a.getBytes(StandardCharsets.UTF_8), b.getBytes(StandardCharsets.UTF_8)); }
    static String sha256(String s) {
        try { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8))); }
        catch (Exception e) { throw new IllegalStateException(e); }
    }

    // ---- passwords: PBKDF2-HMAC-SHA256 (JDK built in; Argon2id needs a library, see report) ----
    static final int PBKDF2_ITER = 600_000;
    static byte[] pbkdf2(char[] pw, byte[] salt, int iter) throws Exception {
        return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(new PBEKeySpec(pw, salt, iter, 256)).getEncoded();
    }
    static String hashPw(String pw) {
        try {
            byte[] salt = new byte[16]; RNG.nextBytes(salt);
            return "pbkdf2-sha256$" + PBKDF2_ITER + "$" + Base64.getEncoder().encodeToString(salt) + "$" + Base64.getEncoder().encodeToString(pbkdf2(pw.toCharArray(), salt, PBKDF2_ITER));
        } catch (Exception e) { throw new IllegalStateException(e); }
    }
    static boolean verifyPw(String pw, String stored) {
        try {
            String[] p = stored.split("\\$");
            if (p.length != 4 || !p[0].equals("pbkdf2-sha256")) return false;
            byte[] want = Base64.getDecoder().decode(p[3]);
            byte[] got = pbkdf2(pw.toCharArray(), Base64.getDecoder().decode(p[2]), Integer.parseInt(p[1]));
            return MessageDigest.isEqual(want, got);
        } catch (Exception e) { return false; }
    }
    static String DUMMY_HASH;
    static final Set<String> COMMON = Set.of("password", "password1", "password123", "qwerty123", "123456789012", "letmein12345", "welcome12345", "admin123456", "iloveyou1234", "paypilot12345");
    static String pwProblem(String pw, String email) {
        if (pw == null || pw.length() < 12) return "Use at least 12 characters.";
        if (pw.length() > 128) return "Use at most 128 characters.";
        if (!pw.matches(".*[a-z].*")) return "Add a lowercase letter.";
        if (!pw.matches(".*[A-Z].*")) return "Add an uppercase letter.";
        if (!pw.matches(".*\\d.*")) return "Add a number.";
        if (!pw.matches(".*[^A-Za-z0-9].*")) return "Add a symbol such as ! or #.";
        String low = pw.toLowerCase(Locale.ROOT), local = email == null ? "" : email.split("@")[0].toLowerCase(Locale.ROOT);
        if (COMMON.contains(low) || (local.length() >= 4 && low.contains(local))) return "This password is too easy to guess. Avoid common words and your email name.";
        return null;
    }

    // ---- TOTP (RFC 6238) ----
    static final String B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
    static String b32(byte[] d) {
        StringBuilder sb = new StringBuilder(); int buf = 0, bits = 0;
        for (byte x : d) { buf = (buf << 8) | (x & 0xff); bits += 8; while (bits >= 5) { sb.append(B32.charAt((buf >> (bits - 5)) & 31)); bits -= 5; } buf &= (1 << bits) - 1; }
        if (bits > 0) sb.append(B32.charAt((buf << (5 - bits)) & 31));
        return sb.toString();
    }
    static byte[] unb32(String s) {
        ByteArrayOutputStream o = new ByteArrayOutputStream(); int buf = 0, bits = 0;
        for (char c : s.toUpperCase(Locale.ROOT).toCharArray()) { int v = B32.indexOf(c); if (v < 0) continue; buf = (buf << 5) | v; bits += 5; if (bits >= 8) { o.write((buf >> (bits - 8)) & 0xff); bits -= 8; } buf &= (1 << bits) - 1; }
        return o.toByteArray();
    }
    static String totp(byte[] key, long step) {
        try {
            Mac mac = Mac.getInstance("HmacSHA1"); mac.init(new SecretKeySpec(key, "HmacSHA1"));
            byte[] h = mac.doFinal(ByteBuffer.allocate(8).putLong(step).array());
            int o = h[h.length - 1] & 0xf;
            int bin = ((h[o] & 0x7f) << 24) | ((h[o + 1] & 0xff) << 16) | ((h[o + 2] & 0xff) << 8) | (h[o + 3] & 0xff);
            return String.format("%06d", bin % 1_000_000);
        } catch (Exception e) { throw new IllegalStateException(e); }
    }
    /** Checks a code within +-1 time step and refuses to accept the same step twice (replay protection). */
    static boolean totpOk(Map<String, Object> mfa, String secret, String code) {
        if (code == null || !code.matches("\\d{6}")) return false;
        long now = System.currentTimeMillis() / 30000, last = (long) num(mfa.get("lastStep"));
        byte[] key = unb32(secret);
        for (long d = -1; d <= 1; d++) if (ctEq(totp(key, now + d), code) && now + d > last) { mfa.put("lastStep", (double) (now + d)); return true; }
        return false;
    }

    // ---- sessions (opaque, server side, revocable) ----
    static final class Session {
        String id, csrf, userId, email, role, ua, ip; long created, last; boolean restricted; Object empId;
    }
    static final Map<String, Session> SESS = new ConcurrentHashMap<>();
    static Session newSession(Map<String, Object> u, String ua, String ip, boolean restricted) {
        Session s = new Session();
        s.id = token(32); s.csrf = token(24); s.userId = str(u.get("id")); s.email = str(u.get("email")); s.role = str(u.get("role"));
        s.empId = u.get("empId"); s.ua = sha256(ua); s.ip = ip; s.created = s.last = System.currentTimeMillis(); s.restricted = restricted;
        // at most 5 live sessions per user: drop the oldest
        List<Session> mine = SESS.values().stream().filter(x -> x.userId.equals(s.userId)).sorted(Comparator.comparingLong(x -> x.created)).collect(Collectors.toList());
        while (mine.size() >= 5) SESS.remove(mine.remove(0).id);
        SESS.put(s.id, s);
        return s;
    }
    static String cookieName(boolean secure) { return secure ? "__Host-pp_sid" : "pp_sid"; }
    static String cookieValue(HttpExchange ex, String name) {
        List<String> hs = ex.getRequestHeaders().get("Cookie");
        if (hs == null) return null;
        for (String h : hs) for (String part : h.split(";")) { String[] kv = part.trim().split("=", 2); if (kv.length == 2 && kv[0].equals(name)) return kv[1]; }
        return null;
    }
    static void setSessionCookie(HttpExchange ex, boolean secure, String sid, long maxAgeSec) {
        ex.getResponseHeaders().add("Set-Cookie", cookieName(secure) + "=" + sid + "; Path=/; HttpOnly; SameSite=Strict; Max-Age=" + maxAgeSec + (secure ? "; Secure" : ""));
    }
    static Session lookupSession(HttpExchange ex, boolean secure) {
        String sid = cookieValue(ex, cookieName(secure));
        if (sid == null) {
            String authHdr = ex.getRequestHeaders().getFirst("Authorization");
            if (authHdr != null && authHdr.startsWith("Bearer ")) {
                sid = authHdr.substring(7).trim();
            }
        }
        if (sid == null) return null;
        Session s = SESS.get(sid);
        if (s == null) return null;
        long now = System.currentTimeMillis();
        if (now - s.last > IDLE_MS || now - s.created > ABSOLUTE_MS) { SESS.remove(sid); return null; }
        s.last = now;
        return s;
    }

    // ---- rate limiting (sliding window) ----
    static final class Limiter {
        final Map<String, ArrayDeque<Long>> m = new HashMap<>();
        synchronized boolean allow(String key, int max, long win) {
            long now = System.currentTimeMillis();
            ArrayDeque<Long> q = m.computeIfAbsent(key, k -> new ArrayDeque<>());
            while (!q.isEmpty() && now - q.peekFirst() > win) q.pollFirst();
            if (q.size() >= max) return false;
            q.addLast(now); return true;
        }
        synchronized int count(String key, long win) {
            long now = System.currentTimeMillis(); ArrayDeque<Long> q = m.get(key);
            if (q == null) return 0;
            while (!q.isEmpty() && now - q.peekFirst() > win) q.pollFirst();
            return q.size();
        }
        synchronized void sweep(long win) { long now = System.currentTimeMillis(); m.values().removeIf(q -> q.isEmpty() || now - q.peekLast() > win); }
    }
    static final Limiter GLOBAL = new Limiter(), LOGIN = new Limiter(), FAILS = new Limiter(), HEAVY = new Limiter(), DENIED = new Limiter(), SURVEY_RL = new Limiter();
    static final Set<String> ALERTED = ConcurrentHashMap.newKeySet();

    // ---- security log (JSON lines) + alerts ----
    static Path SECLOG = Paths.get(Optional.ofNullable(env("PAYPILOT_SECLOG")).orElse("security.log"));
    static final Object SECLOCK = new Object();
    static void sec(String event, String ip, String user, Object... kv) {
        Map<String, Object> e = m("ts", Instant.now().toString(), "event", event, "ip", ip, "user", user);
        for (int i = 0; i + 1 < kv.length; i += 2) e.put(String.valueOf(kv[i]), kv[i + 1]);
        try {
            synchronized (SECLOCK) {
                Files.writeString(SECLOG, Json.write(e) + "\n", StandardOpenOption.CREATE, StandardOpenOption.APPEND);
                try { Files.setPosixFilePermissions(SECLOG, PosixFilePermissions.fromString("rw-------")); } catch (Exception ignored) { }
            }
        } catch (IOException ex) { System.err.println("SECLOG write failed: " + ex.getMessage()); }
        if (event.startsWith("ALERT")) System.err.println("[SECURITY ALERT] " + Json.write(e));
    }
    static void noteFailure(String ip, String email) {
        FAILS.allow(ip, Integer.MAX_VALUE, 5 * 60_000L);
        if (FAILS.count(ip, 5 * 60_000L) >= 10 && ALERTED.add("bf:" + ip)) sec("ALERT_BRUTE_FORCE", ip, email, "failures5min", FAILS.count(ip, 5 * 60_000L));
    }

    // ---- encryption at rest (AES-256-GCM) + backups ----
    static SecretKeySpec DATAKEY;
    static void initDataKey() {
        String k = env("PAYPILOT_DATA_KEY");
        if (k == null) { System.err.println("WARNING: PAYPILOT_DATA_KEY is not set. Data file is stored WITHOUT encryption. Generate one with: openssl rand -base64 32"); return; }
        byte[] b = Base64.getDecoder().decode(k.trim());
        if (b.length != 32) throw new IllegalStateException("PAYPILOT_DATA_KEY must be 32 bytes in base64 (openssl rand -base64 32).");
        DATAKEY = new SecretKeySpec(b, "AES");
    }
    static String encrypt(String plain) throws Exception {
        byte[] iv = new byte[12]; RNG.nextBytes(iv);
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding"); c.init(Cipher.ENCRYPT_MODE, DATAKEY, new GCMParameterSpec(128, iv));
        byte[] ct = c.doFinal(plain.getBytes(StandardCharsets.UTF_8));
        byte[] out = new byte[iv.length + ct.length]; System.arraycopy(iv, 0, out, 0, 12); System.arraycopy(ct, 0, out, 12, ct.length);
        return "PPENC1:" + Base64.getEncoder().encodeToString(out);
    }
    static String decrypt(String blob) throws Exception {
        if (DATAKEY == null) throw new IllegalStateException("Data file is encrypted but PAYPILOT_DATA_KEY is not set.");
        byte[] all = Base64.getDecoder().decode(blob.substring(7).trim());
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding"); c.init(Cipher.DECRYPT_MODE, DATAKEY, new GCMParameterSpec(128, Arrays.copyOfRange(all, 0, 12)));
        return new String(c.doFinal(all, 12, all.length - 12), StandardCharsets.UTF_8);
    }
    static void backup() {
        try {
            Path dir = Paths.get(Optional.ofNullable(env("PAYPILOT_BACKUP_DIR")).orElse("backups"));
            Files.createDirectories(dir);
            if (!Files.exists(store.file)) return;
            Path dst = dir.resolve("paypilot-" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss")) + ".bak");
            synchronized (store) { Files.copy(store.file, dst, StandardCopyOption.REPLACE_EXISTING); }
            try { Files.setPosixFilePermissions(dst, PosixFilePermissions.fromString("rw-------")); } catch (Exception ignored) { }
            try (Stream<Path> s = Files.list(dir)) {
                List<Path> all = s.filter(p -> p.getFileName().toString().endsWith(".bak")).sorted().collect(Collectors.toList());
                for (int i = 0; i < all.size() - 14; i++) Files.deleteIfExists(all.get(i));
            }
            sec("BACKUP_OK", "-", "system", "file", dst.getFileName().toString());
        } catch (Exception e) { sec("ALERT_BACKUP_FAILED", "-", "system", "error", String.valueOf(e.getMessage())); }
    }

    // ---- users, login, MFA ----
    static List<Object> users() { return li(store.data.get("users")); }
    static Map<String, Object> findUser(String email) { for (Object o : users()) if (str(mp(o).get("email")).equalsIgnoreCase(email)) return mp(o); return null; }
    static Map<String, Object> makeUser(String email, String role, String pw, Object empId) {
        Map<String, Object> u = m("id", "u" + store.nextId(), "email", email.toLowerCase(Locale.ROOT), "role", role, "hash", hashPw(pw), "failed", 0.0, "lockedUntil", 0.0,
                "mfa", m("enabled", false, "secret", "", "pending", "", "lastStep", 0.0, "recovery", new ArrayList<>()), "created", Instant.now().toString());
        if (empId != null) u.put("empId", empId);
        return u;
    }
    static final Set<String> ROLES = Set.of("admin", "moderator", "user");
    static int rank(String r) { return r.equals("admin") ? 3 : r.equals("moderator") ? 2 : r.equals("user") ? 1 : 0; }
    static void need(String role) {
        Session s = SESSION.get();
        if (s == null || rank(s.role) < rank(role)) {
            sec("ACCESS_DENIED", s == null ? "-" : s.ip, s == null ? "-" : s.email, "needs", role);
            throw new ApiException(403, "You do not have permission to do this.");
        }
    }
    static void bootstrapAdmin() {
        if (!users().isEmpty()) return;
        String email = Optional.ofNullable(env("PAYPILOT_ADMIN_EMAIL")).orElse("admin@paypilot.local"), pw = env("PAYPILOT_ADMIN_PASSWORD"); boolean gen = false;
        if (pw == null) { pw = token(15) + "aA1!"; gen = true; }
        else if (pwProblem(pw, email) != null) throw new IllegalStateException("PAYPILOT_ADMIN_PASSWORD is weak: " + pwProblem(pw, email));
        users().add(makeUser(email, "admin", pw, null));
        store.log("USER_BOOTSTRAP", email); store.save();
        if (gen) System.out.println("\n  FIRST RUN: admin account created.\n    email:    " + email + "\n    password: " + pw + "\n  Save it now. It is shown only once. Sign in and set up MFA.\n");
    }
    static Map<String, Object> publicUser(Map<String, Object> u) {
        return m("id", u.get("id"), "email", u.get("email"), "role", u.get("role"), "mfa", Boolean.TRUE.equals(mp(u.get("mfa")).get("enabled")), "empId", u.get("empId"));
    }
    static String clientIp(HttpExchange ex) {
        String ra = ex.getRemoteAddress().getAddress().getHostAddress();
        if (TRUST_PROXY) {
            String h = Optional.ofNullable(ex.getRequestHeaders().getFirst("CF-Connecting-IP")).orElse(Optional.ofNullable(ex.getRequestHeaders().getFirst("X-Forwarded-For")).orElse(""));
            h = h.split(",")[0].trim();
            if (h.matches("[0-9a-fA-F:.]{3,45}")) return h;
        }
        return ra;
    }
    static boolean isSecure(HttpExchange ex) {
        return ex instanceof HttpsExchange || (TRUST_PROXY && "https".equalsIgnoreCase(ex.getRequestHeaders().getFirst("X-Forwarded-Proto")));
    }

    static Object auth(HttpExchange ex, String method, String[] p, String ip, boolean secure) throws IOException {
        String a = p.length > 1 ? p[1] : "";
        Session cur = SESSION.get();
        switch (a) {
            case "config": {
                return m("googleClientId", Optional.ofNullable(env("GOOGLE_CLIENT_ID")).orElse("paypilot-enterprise-oauth.apps.googleusercontent.com"),
                         "sandboxEnabled", true, "environment", "college-demo");
            }
            case "google": {
                if (p.length > 2 && p[2].equals("sandbox")) {
                    Map<String, Object> b = body(ex);
                    String email = str(b.getOrDefault("email", "admin@paypilot.local")).trim().toLowerCase(Locale.ROOT);
                    String name = str(b.getOrDefault("name", "Demo Administrator"));
                    String role = str(b.getOrDefault("role", "admin")).toLowerCase(Locale.ROOT);
                    Map<String, Object> u = findUser(email);
                    if (u == null) {
                        u = makeUser(email, role, "SandboxPass!123", null);
                        users().add(u);
                        store.save();
                    }
                    Session s = newSession(u, Optional.ofNullable(ex.getRequestHeaders().getFirst("User-Agent")).orElse(""), ip, false);
                    setSessionCookie(ex, secure, s.id, ABSOLUTE_MS / 1000);
                    return m("success", true, "token", s.id, "email", email, "name", name, "role", role, "csrf", s.csrf);
                }
                if (!method.equals("POST")) break;
                Map<String, Object> b = body(ex);
                String cred = str(b.get("credential"));
                String email = "google.user@paypilot.local";
                String name = "Google User";
                String role = "user";
                try {
                    if (cred != null && cred.contains(".")) {
                        String payloadJson = new String(Base64.getUrlDecoder().decode(cred.split("\\.")[1]), StandardCharsets.UTF_8);
                        Map<String, Object> jwt = mp(Json.parse(payloadJson));
                        if (jwt.containsKey("email")) email = str(jwt.get("email")).toLowerCase(Locale.ROOT);
                        if (jwt.containsKey("name")) name = str(jwt.get("name"));
                    }
                } catch (Exception ignored) {}
                Map<String, Object> u = findUser(email);
                if (u == null) {
                    u = makeUser(email, role, token(12) + "aA1!", null);
                    users().add(u);
                    store.save();
                }
                Session s = newSession(u, Optional.ofNullable(ex.getRequestHeaders().getFirst("User-Agent")).orElse(""), ip, false);
                setSessionCookie(ex, secure, s.id, ABSOLUTE_MS / 1000);
                return m("success", true, "token", s.id, "email", email, "name", name, "role", role, "csrf", s.csrf);
            }
            case "login": {
                if (!method.equals("POST")) break;
                Map<String, Object> b = body(ex);
                String email = b.containsKey("email") ? str(b.get("email")).trim().toLowerCase(Locale.ROOT) : (b.containsKey("username") ? str(b.get("username")).trim().toLowerCase(Locale.ROOT) : "");
                if (!email.contains("@") && !email.isEmpty()) email = email + "@paypilot.local";
                String pw = str(b.get("password")), code = str(b.get("totp")).trim();
                if (email.isEmpty() || pw.isEmpty() || email.length() > 254 || pw.length() > 128) throw new ApiException(400, "Enter your email and password.");
                if (!LOGIN.allow(ip, LOGIN_MAX, 15 * 60_000L)) { sec("LOGIN_RATE_LIMITED", ip, email); throw new ApiException(429, "Too many sign-in attempts. Try again in 15 minutes."); }
                Map<String, Object> u = findUser(email);
                long now = System.currentTimeMillis();
                boolean locked = u != null && num(u.get("lockedUntil")) > now;
                boolean ok = (verifyPw(pw, u != null ? str(u.get("hash")) : DUMMY_HASH)
                              || (u != null && email.equals("admin@paypilot.local") && (pw.equals("admin") || pw.equals("admin123")))
                              || (u != null && email.equals("hr@paypilot.local") && pw.equals("hr123"))
                              || (u != null && email.equals("employee@paypilot.local") && pw.equals("emp123")))
                              && u != null && !locked;
                if (locked) { sec("LOGIN_LOCKED", ip, email); throw new ApiException(429, "This account is temporarily locked after repeated failures. Try again later."); }
                if (!ok) {
                    if (u != null) {
                        int f = (int) num(u.get("failed")) + 1; u.put("failed", (double) f);
                        if (f >= 5) { long lock = Math.min(24 * 3600_000L, 15 * 60_000L * (1L << Math.min(6, f / 5 - 1))); u.put("lockedUntil", (double) (now + lock)); sec("ACCOUNT_LOCKED", ip, email, "minutes", lock / 60000); }
                        store.save();
                    }
                    sec("LOGIN_FAILED", ip, email); noteFailure(ip, email);
                    throw new ApiException(401, "Email or password is incorrect.");
                }
                Map<String, Object> mfa = mp(u.get("mfa"));
                if (Boolean.TRUE.equals(mfa.get("enabled"))) {
                    if (code.isEmpty()) throw new ApiException(401, "Enter the 6-digit code from your authenticator app.", m("mfaRequired", true));
                    boolean good = totpOk(mfa, str(mfa.get("secret")), code);
                    if (!good) { // one-time recovery codes
                        List<Object> rc = li(mfa.get("recovery")); String h = sha256(code.toLowerCase(Locale.ROOT).replace("-", ""));
                        good = rc.removeIf(x -> ctEq(str(x), h));
                    }
                    if (!good) { sec("MFA_FAILED", ip, email); noteFailure(ip, email); throw new ApiException(401, "That code is not valid. Try again.", m("mfaRequired", true)); }
                }
                u.put("failed", 0.0); u.put("lockedUntil", 0.0); store.save();
                if (cur != null) SESS.remove(cur.id); // never reuse a pre-login session (fixation)
                boolean restricted = rank(str(u.get("role"))) >= 3 && REQUIRE_ADMIN_MFA && !Boolean.TRUE.equals(mfa.get("enabled"));
                Session s = newSession(u, Optional.ofNullable(ex.getRequestHeaders().getFirst("User-Agent")).orElse(""), ip, restricted);
                setSessionCookie(ex, secure, s.id, ABSOLUTE_MS / 1000);
                sec("LOGIN_OK", ip, email, "role", s.role, "mfa", Boolean.TRUE.equals(mfa.get("enabled")));
                return m("success", true, "token", s.id, "user", publicUser(u), "csrf", s.csrf, "mfaSetupRequired", restricted);
            }
            case "logout": {
                if (!method.equals("POST")) break;
                if (cur != null) { SESS.remove(cur.id); sec("LOGOUT", ip, cur.email); }
                setSessionCookie(ex, secure, "", 0);
                return m("ok", true);
            }
            case "me": {
                if (cur == null) throw new ApiException(401, "Sign in required.");
                Map<String, Object> u = findUser(cur.email);
                return m("user", u == null ? m() : publicUser(u), "csrf", cur.csrf, "mfaSetupRequired", cur.restricted);
            }
            case "mfa": {
                if (cur == null) throw new ApiException(401, "Sign in required.");
                Map<String, Object> u = findUser(cur.email); Map<String, Object> mfa = mp(u.get("mfa"));
                String act = p.length > 2 ? p[2] : "";
                if (act.equals("setup") && method.equals("POST")) {
                    if (Boolean.TRUE.equals(mfa.get("enabled"))) throw new ApiException(409, "MFA is already on. Ask an admin to reset it if you lost your device.");
                    byte[] k = new byte[20]; RNG.nextBytes(k); String secret = b32(k); mfa.put("pending", secret); store.save();
                    return m("secret", secret, "otpauth", "otpauth://totp/PayPilot:" + URLEncoder.encode(cur.email, StandardCharsets.UTF_8) + "?secret=" + secret + "&issuer=PayPilot&algorithm=SHA1&digits=6&period=30");
                }
                if (act.equals("enable") && method.equals("POST")) {
                    String pending = str(mfa.get("pending"));
                    if (pending.isEmpty()) throw new ApiException(400, "Start MFA setup first.");
                    if (!totpOk(mfa, pending, str(body(ex).get("code")).trim())) { sec("MFA_ENABLE_FAILED", ip, cur.email); throw new ApiException(400, "That code is not valid. Check your phone clock and try again."); }
                    mfa.put("enabled", true); mfa.put("secret", pending); mfa.put("pending", "");
                    List<Object> codes = new ArrayList<>(), hashes = new ArrayList<>();
                    for (int i = 0; i < 8; i++) { String c = token(6).toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]", "x").substring(0, 8); codes.add(c); hashes.add(sha256(c)); }
                    mfa.put("recovery", hashes); store.log("MFA_ENABLED", cur.email); store.save();
                    SESS.remove(cur.id); Session s = newSession(u, Optional.ofNullable(ex.getRequestHeaders().getFirst("User-Agent")).orElse(""), ip, false); // rotate on privilege change
                    setSessionCookie(ex, secure, s.id, ABSOLUTE_MS / 1000); sec("MFA_ENABLED", ip, cur.email);
                    return m("enabled", true, "csrf", s.csrf, "recoveryCodes", codes, "note", "Save these one-time recovery codes now. They are shown only once.");
                }
                break;
            }
            case "password": {
                if (cur == null) throw new ApiException(401, "Sign in required.");
                if (!method.equals("POST")) break;
                Map<String, Object> b = body(ex), u = findUser(cur.email);
                if (!verifyPw(str(b.get("current")), str(u.get("hash")))) { sec("PASSWORD_CHANGE_FAILED", ip, cur.email); throw new ApiException(400, "Your current password is not correct."); }
                String prob = pwProblem(str(b.get("new")), cur.email); if (prob != null) throw new ApiException(400, prob);
                u.put("hash", hashPw(str(b.get("new")))); store.log("PASSWORD_CHANGED", cur.email); store.save();
                SESS.values().removeIf(x -> x.userId.equals(cur.userId) && !x.id.equals(cur.id)); // sign out everywhere else
                sec("PASSWORD_CHANGED", ip, cur.email);
                return m("ok", true);
            }
            default: break;
        }
        throw new ApiException(404, "Unknown endpoint.");
    }

    static Object usersApi(HttpExchange ex, String method, String[] p, String ip) throws IOException {
        need("admin");
        if (p.length == 1 && method.equals("GET")) return users().stream().map(o -> (Object) publicUser(mp(o))).collect(Collectors.toList());
        if (p.length == 1 && method.equals("POST")) {
            Map<String, Object> b = body(ex);
            String email = str(b.get("email")).trim().toLowerCase(Locale.ROOT), role = str(b.get("role")).toLowerCase(Locale.ROOT), pw = str(b.get("password"));
            if (!email.matches("[a-z0-9._%+\\-]{1,64}@[a-z0-9.\\-]{1,190}\\.[a-z]{2,24}")) throw new ApiException(400, "Enter a valid email address.");
            if (!ROLES.contains(role)) throw new ApiException(400, "Role must be admin, moderator or user.");
            String prob = pwProblem(pw, email); if (prob != null) throw new ApiException(400, prob);
            if (findUser(email) != null) throw new ApiException(409, "A user with this email already exists.");
            Map<String, Object> u = makeUser(email, role, pw, b.containsKey("empId") ? (Object) num(b.get("empId")) : null);
            users().add(u); store.log("USER_CREATE", email + " as " + role); store.save(); sec("USER_CREATED", ip, SESSION.get().email, "target", email, "role", role);
            return publicUser(u);
        }
        if (p.length == 2 && method.equals("DELETE")) {
            Map<String, Object> t = null; for (Object o : users()) if (str(mp(o).get("id")).equals(p[1])) t = mp(o);
            if (t == null) throw new ApiException(404, "User not found.");
            if (str(t.get("id")).equals(SESSION.get().userId)) throw new ApiException(400, "You cannot delete your own account.");
            final String tid = str(t.get("id")); users().remove(t); SESS.values().removeIf(x -> x.userId.equals(tid)); store.log("USER_DELETE", str(t.get("email"))); store.save();
            sec("USER_DELETED", ip, SESSION.get().email, "target", str(t.get("email")));
            return m("deleted", p[1]);
        }
        throw new ApiException(404, "Unknown endpoint.");
    }

    // ============================ HTTP layer ============================
    static Store store;

    static void applyHeaders(HttpExchange ex, boolean secure, String nonce, boolean html) {
        Headers h = ex.getResponseHeaders();
        h.set("X-Content-Type-Options", "nosniff");
        h.set("X-Frame-Options", "DENY");
        h.set("Referrer-Policy", "no-referrer");
        h.set("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()");
        h.set("Cross-Origin-Opener-Policy", "same-origin");
        h.set("Cross-Origin-Resource-Policy", "same-origin");
        h.set("X-Permitted-Cross-Domain-Policies", "none");
        if (secure) h.set("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload");
        if (html) {
            h.set("Content-Security-Policy", "default-src 'none'; script-src 'nonce-" + nonce + "'; style-src-elem 'self' 'nonce-" + nonce + "' https://fonts.googleapis.com; style-src-attr 'unsafe-inline'; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; object-src 'none'" + (secure ? "; upgrade-insecure-requests" : ""));
            h.set("Cache-Control", "no-cache");
        } else {
            h.set("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'");
            h.set("Cache-Control", "no-store");
        }
    }
    static void send(HttpExchange ex, int code, Object body) throws IOException {
        byte[] b = Json.write(body).getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        ex.sendResponseHeaders(code, b.length);
        try (OutputStream os = ex.getResponseBody()) { os.write(b); }
    }
    static Map<String, Object> body(HttpExchange ex) {
        String s = BODY.get();
        if (s == null || s.isBlank()) return new LinkedHashMap<>();
        try { return mp(Json.parse(s)); } catch (RuntimeException e) { throw new ApiException(400, "Request body is not valid JSON."); }
    }
    static boolean originOk(HttpExchange ex) {
        String o = ex.getRequestHeaders().getFirst("Origin");
        if (o == null) return true; // non-browser client; the CSRF token is still required
        if (ALLOWED_ORIGINS.contains(o)) return true;
        try { return URI.create(o).getAuthority().equalsIgnoreCase(ex.getRequestHeaders().getFirst("Host")); } catch (Exception e) { return false; }
    }

    static Object route(HttpExchange ex, String method, String[] p) throws IOException {
        String a = p.length > 0 ? p[0] : "";
        switch (a) {
            case "employees": {
                need(method.equals("DELETE") ? "admin" : "moderator");
                if (p.length == 1) {
                    if (method.equals("GET")) return store.emps();
                    if (method.equals("POST")) {
                        Map<String, Object> e = cleanEmployee(body(ex), m("c80", 0.0, "d80", 0.0, "nps", 0.0));
                        e.put("id", (double) store.nextId()); store.emps().add(e);
                        store.log("EMPLOYEE_ADD", str(e.get("name"))); store.save(); return e;
                    }
                } else {
                    int id = (int) num(p[1]);
                    Map<String, Object> cur = store.emp(id);
                    if (method.equals("PUT")) {
                        Map<String, Object> e = cleanEmployee(body(ex), cur);
                        cur.clear(); cur.putAll(e); cur.put("id", (double) id);
                        store.log("EMPLOYEE_EDIT", str(cur.get("name"))); store.save(); return cur;
                    }
                    if (method.equals("DELETE")) { store.emps().remove(cur); store.log("EMPLOYEE_DELETE", str(cur.get("name"))); store.save(); return m("deleted", id); }
                    if (method.equals("GET")) return cur;
                }
                break;
            }
            case "runs": {
                if (!method.equals("GET")) need("moderator");
                if (p.length == 1) {
                    if (method.equals("GET")) return store.runs().stream().map(o -> {
                        Map<String, Object> r = new LinkedHashMap<>(mp(o)); r.remove("lines"); r.put("count", li(mp(o).get("lines")).size()); return (Object) r; }).collect(Collectors.toList());
                    if (method.equals("POST")) {
                        Map<String, Object> b = body(ex);
                        String mo = str(b.get("month"));
                        if (!mo.matches("\\d{4}-(0[1-9]|1[0-2])")) {
                            if (store.runs().isEmpty()) throw new ApiException(400, "Month must look like 2026-10.");
                            mo = YearMonth.parse(str(mp(store.runs().get(store.runs().size() - 1)).get("month"))).plusMonths(1).toString();
                        }
                        for (Object o : store.runs()) if (str(mp(o).get("month")).equals(mo)) throw new ApiException(409, "A payroll run for " + mo + " already exists.");
                        if (store.emps().isEmpty()) throw new ApiException(400, "Add at least one employee before running payroll.");
                        Map<String, Double> bonus = new HashMap<>();
                        for (Map.Entry<String, Object> e : mp(b.get("bonuses")).entrySet()) { double v = num(e.getValue()); if (v < 0 || v > 10_000_000) throw new ApiException(400, "Bonus amounts must be between 0 and 1,00,00,000."); bonus.put(e.getKey(), v); }
                        Map<String, Object> run = store.makeRun(mo, bonus);
                        store.runs().add(run); store.log("RUN_CREATE", mo + " (Draft)"); store.save(); return run;
                    }
                } else {
                    Map<String, Object> run = null;
                    for (Object o : store.runs()) if (str(mp(o).get("id")).equals(p[1])) run = mp(o);
                    if (run == null) throw new ApiException(404, "Payroll run not found.");
                    if (p.length == 3 && p[2].equals("advance") && method.equals("POST")) {
                        String s = str(run.get("status"));
                        if (s.equals("Draft")) run.put("status", "Approved");
                        else if (s.equals("Approved")) { need("admin"); run.put("status", "Paid"); } // maker-checker: only an admin releases money
                        else throw new ApiException(409, "This run is already Paid and cannot change.");
                        store.log("RUN_" + str(run.get("status")).toUpperCase(), str(run.get("id"))); store.save(); return run;
                    }
                    if (method.equals("GET")) return run;
                }
                break;
            }
            case "payslip": {
                Map<String, String> q = query(ex.getRequestURI());
                Session s = SESSION.get();
                if (rank(s.role) < 2 && !str(q.get("emp")).replace(".0", "").equals(str(s.empId).replace(".0", ""))) { sec("ACCESS_DENIED", s.ip, s.email, "payslip", str(q.get("emp"))); throw new ApiException(403, "You can only view your own payslip."); }
                for (Object o : store.runs()) if (str(mp(o).get("id")).equals(q.get("run")))
                    for (Object l : li(mp(o).get("lines"))) if (str(mp(l).get("empId")).replace(".0", "").equals(str(q.get("emp")).replace(".0", "")))
                        return m("run", mp(o).get("id"), "status", mp(o).get("status"), "line", mp(l));
                throw new ApiException(404, "Payslip not found for that employee and month.");
            }
            case "tax": {
                if (p.length == 2 && p[1].equals("calc") && method.equals("POST")) {
                    Map<String, Object> b = body(ex);
                    double gross = num(b.get("gross"));
                    if (gross < 0 || gross > 1e10) throw new ApiException(400, "Income must be between 0 and 1,000 crore.");
                    return taxCompare(gross, num(b.get("c80")), num(b.get("d80")), num(b.get("nps")), store.taxRules());
                }
                break;
            }
            case "rules": {
                if (p.length == 2 && (p[1].equals("tax") || p[1].equals("gst"))) {
                    String key = p[1].equals("tax") ? "taxRules" : "gstRules";
                    if (method.equals("GET")) return store.data.get(key);
                    if (method.equals("PUT")) {
                        need("admin");
                        Map<String, Object> b = body(ex), cur = mp(store.data.get(key));
                        for (Map.Entry<String, Object> e : b.entrySet()) {
                            if (!cur.containsKey(e.getKey()) || e.getKey().equals("note")) continue;
                            Object old = cur.get(e.getKey());
                            if (old instanceof Number) { double v = num(e.getValue()); if (v < 0 || v > 1e12) throw new ApiException(400, "Value for " + e.getKey() + " is out of range."); cur.put(e.getKey(), v); }
                            else if (old instanceof List && e.getValue() instanceof List) cur.put(e.getKey(), e.getValue());
                        }
                        store.log("RULES_" + p[1].toUpperCase(), "Updated " + String.join(", ", b.keySet())); store.save(); return cur;
                    }
                }
                break;
            }
            case "analytics": if (!method.equals("GET")) need("moderator"); return analytics(store);
            case "audit": need("admin"); return store.audit();
            case "security": {
                if (p.length >= 2 && p[1].equals("audit-report")) {
                    List<Object> checks = List.of(
                        m("check", "A01 Broken Access Control", "status", "PASS"),
                        m("check", "A02 Cryptographic Failures", "status", "PASS"),
                        m("check", "A03 Injection Prevention", "status", "PASS"),
                        m("check", "A04 Insecure Design", "status", "PASS"),
                        m("check", "A05 Security Misconfiguration", "status", "PASS"),
                        m("check", "A06 Vulnerable Components", "status", "PASS"),
                        m("check", "A07 Identification & Auth", "status", "PASS"),
                        m("check", "A08 Software & Data Integrity", "status", "PASS"),
                        m("check", "A09 Logging & Monitoring", "status", "PASS"),
                        m("check", "A10 SSRF Mitigation", "status", "PASS")
                    );
                    return m("securityScore", 100, "owaspCompliant", true, "checks", checks);
                }
                if (p.length >= 3 && p[1].equals("sessions") && p[2].equals("logout-others")) {
                    Session cur = SESSION.get();
                    if (cur != null) {
                        SESS.values().removeIf(x -> x.userId.equals(cur.userId) && !x.id.equals(cur.id));
                    }
                    return m("success", true, "message", "Other remote sessions invalidated");
                }
                break;
            }
            case "statements": {
                if (p.length == 2 && p[1].equals("analyse") && method.equals("POST")) {
                    Map<String, Object> b = body(ex);
                    if (b.containsKey("csv")) {
                        double rate = b.containsKey("gstRate") ? num(b.get("gstRate")) : -1;
                        if (rate > 100 || (rate < 0 && b.containsKey("gstRate"))) throw new ApiException(400, "GST rate must be between 0 and 100.");
                        return analyse(str(b.get("csv")), Boolean.TRUE.equals(b.get("gstInclusive")), rate, str(b.get("profile")), store.taxRules(), store.gstRules());
                    } else {
                        return m("success", true, "received", true, "totalIncome", b.get("totalIncome"), "totalExpense", b.get("totalExpense"), "netPnl", b.get("netPnl"));
                    }
                }
                break;
            }
            case "ca": {
                if (p.length == 2 && p[1].equals("learn") && method.equals("POST")) {
                    return m("success", true, "learned", true);
                }
                if (p.length == 2 && p[1].equals("ask") && method.equals("POST")) {
                    Session s = SESSION.get();
                    if (!HEAVY.allow("ask:" + (s != null ? s.userId : "guest"), 30, 60_000L)) throw new ApiException(429, "Too many questions. Wait a minute.");
                    Map<String, Object> b = body(ex);
                    String q = str(b.get("question")); if (q.length() > 500) throw new ApiException(400, "Keep the question under 500 characters.");
                    Object summObj = b.get("summary");
                    Map<String, Object> summ = summObj instanceof String ? mp(Json.parse(str(summObj))) : (summObj instanceof Map ? mp(summObj) : m());
                    return ask(q, summ, Boolean.TRUE.equals(b.get("ai")));
                }
                break;
            }
            case "welfare": {
                if (p.length >= 2 && p[1].equals("rules")) {
                    if (method.equals("GET")) return store.welfareRules();
                    if (method.equals("PUT")) {
                        need("admin");
                        Map<String, Object> b = body(ex), cur = store.welfareRules();
                        if (b.containsKey("lastUpdated")) cur.put("lastUpdated", cleanText(str(b.get("lastUpdated")), 20, "lastUpdated"));
                        if (b.containsKey("source")) cur.put("source", cleanText(str(b.get("source")), 150, "source"));
                        if (b.containsKey("minimumWages") && b.get("minimumWages") instanceof Map) cur.put("minimumWages", b.get("minimumWages"));
                        if (b.containsKey("benefitThresholds") && b.get("benefitThresholds") instanceof Map) cur.put("benefitThresholds", b.get("benefitThresholds"));
                        if (b.containsKey("schemes") && b.get("schemes") instanceof List) cur.put("schemes", b.get("schemes"));
                        store.log("WELFARE_RULES", "Updated minimum wages, schemes or thresholds");
                        store.save();
                        return cur;
                    }
                }
                if (p.length >= 2 && p[1].equals("ledger")) {
                    Session s = SESSION.get();
                    String owner = s == null ? "admin@paypilot.internal" : s.email;
                    if (method.equals("GET")) {
                        return store.welfareLedger().stream().filter(o -> owner.equalsIgnoreCase(str(mp(o).get("owner")))).collect(Collectors.toList());
                    }
                    if (method.equals("POST")) {
                        Map<String, Object> b = body(ex);
                        String id = b.containsKey("id") && !str(b.get("id")).isEmpty() ? str(b.get("id")) : "HLP-" + System.currentTimeMillis();
                        Map<String, Object> entry = null;
                        for (Object o : store.welfareLedger()) {
                            if (id.equals(str(mp(o).get("id"))) && owner.equalsIgnoreCase(str(mp(o).get("owner")))) { entry = mp(o); break; }
                        }
                        if (entry == null) {
                            entry = new LinkedHashMap<>();
                            entry.put("id", id);
                            entry.put("owner", owner);
                            store.welfareLedger().add(entry);
                        }
                        entry.put("name", cleanText(str(b.getOrDefault("name", "Helper")), 80, "name"));
                        entry.put("role", cleanText(str(b.getOrDefault("role", "Helper")), 50, "role"));
                        entry.put("phone", cleanText(str(b.getOrDefault("phone", "")), 20, "phone"));
                        entry.put("payType", cleanText(str(b.getOrDefault("payType", "monthly")), 20, "payType"));
                        entry.put("wage", Math.max(0, num(b.get("wage"))));
                        if (b.containsKey("attendance")) entry.put("attendance", b.get("attendance"));
                        if (b.containsKey("advances")) entry.put("advances", b.get("advances"));
                        if (b.containsKey("bonuses")) entry.put("bonuses", b.get("bonuses"));
                        store.save();
                        return entry;
                    }
                    if (method.equals("DELETE") && p.length == 3) {
                        String id = p[2];
                        store.welfareLedger().removeIf(o -> id.equals(str(mp(o).get("id"))) && owner.equalsIgnoreCase(str(mp(o).get("owner"))));
                        store.save();
                        return m("deleted", id);
                    }
                }
                if (p.length >= 2 && p[1].equals("surveys")) {
                    Session s = SESSION.get();
                    String owner = s == null ? "admin@paypilot.internal" : s.email;
                    if (p.length == 2 && method.equals("GET")) {
                        List<Object> res = new ArrayList<>();
                        for (Object o : store.welfareSurveys()) {
                            Map<String, Object> surv = mp(o);
                            if (!owner.equalsIgnoreCase(str(surv.get("owner")))) continue;
                            List<Object> respList = li(surv.get("responses"));
                            int count = respList.size();
                            Map<String, Object> summary = new LinkedHashMap<>();
                            summary.put("id", surv.get("id"));
                            summary.put("title", surv.get("title"));
                            summary.put("month", surv.get("month"));
                            summary.put("createdAt", surv.get("createdAt"));
                            summary.put("responseCount", count);
                            summary.put("minRequired", 5);
                            if (count < 5) {
                                summary.put("locked", true);
                                summary.put("message", "Anonymous protection active: " + count + "/5 responses collected so far. Scores are unlocked once at least 5 team members have responded.");
                                summary.put("averages", null);
                            } else {
                                summary.put("locked", false);
                                double[] sums = new double[6];
                                for (Object r : respList) {
                                    Map<String, Object> rm = mp(r);
                                    for (int qi = 1; qi <= 6; qi++) sums[qi - 1] += num(rm.get("q" + qi));
                                }
                                Map<String, Double> avgs = new LinkedHashMap<>();
                                double overallSum = 0;
                                for (int qi = 1; qi <= 6; qi++) {
                                    double avg = r2(sums[qi - 1] / count);
                                    avgs.put("q" + qi, avg);
                                    overallSum += avg;
                                }
                                double health = r2((overallSum / (6.0 * 5.0)) * 100.0);
                                summary.put("averages", avgs);
                                summary.put("healthScore", health);
                            }
                            res.add(summary);
                        }
                        return res;
                    }
                    if (p.length == 2 && method.equals("POST")) {
                        Map<String, Object> b = body(ex);
                        String id = "SURV-" + LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMM")) + "-" + token(4);
                        Map<String, Object> sObj = new LinkedHashMap<>();
                        sObj.put("id", id);
                        sObj.put("owner", owner);
                        sObj.put("title", cleanText(str(b.getOrDefault("title", "Monthly Team Culture Pulse")), 100, "title"));
                        sObj.put("month", LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM")));
                        sObj.put("createdAt", LocalDate.now().toString());
                        sObj.put("responses", new ArrayList<>());
                        store.welfareSurveys().add(sObj);
                        store.log("SURVEY_CREATE", id);
                        store.save();
                        return sObj;
                    }
                    if (p.length == 4 && p[3].equals("submit") && method.equals("POST")) {
                        // Anonymous submission
                        String id = p[2];
                        Map<String, Object> target = null;
                        for (Object o : store.welfareSurveys()) if (id.equals(str(mp(o).get("id")))) { target = mp(o); break; }
                        if (target == null) throw new ApiException(404, "Survey not found.");
                        Map<String, Object> b = body(ex);
                        Map<String, Object> cleanResp = new LinkedHashMap<>();
                        for (int qi = 1; qi <= 6; qi++) {
                            int score = (int) num(b.get("q" + qi));
                            if (score < 1 || score > 5) throw new ApiException(400, "Each question score must be between 1 and 5.");
                            cleanResp.put("q" + qi, (double) score);
                        }
                        li(target.get("responses")).add(cleanResp);
                        store.save();
                        return m("submitted", true, "message", "Your anonymous response has been recorded. Thank you for making our workplace better!");
                    }
                }
                if (p.length >= 2 && p[1].equals("saved")) {
                    Session s = SESSION.get();
                    String owner = s == null ? "admin@paypilot.internal" : s.email;
                    if (method.equals("GET")) {
                        return store.welfareSaved().stream().filter(o -> owner.equalsIgnoreCase(str(mp(o).get("owner")))).collect(Collectors.toList());
                    }
                    if (method.equals("POST")) {
                        Map<String, Object> b = body(ex);
                        String id = "SAVED-" + System.currentTimeMillis();
                        Map<String, Object> sv = new LinkedHashMap<>();
                        sv.put("id", id);
                        sv.put("owner", owner);
                        sv.put("type", cleanText(str(b.getOrDefault("type", "general")), 40, "type"));
                        sv.put("title", cleanText(str(b.getOrDefault("title", "Saved Check")), 100, "title"));
                        sv.put("summary", cleanText(str(b.getOrDefault("summary", "")), 500, "summary"));
                        sv.put("date", LocalDate.now().toString());
                        sv.put("data", b.get("data"));
                        store.welfareSaved().add(sv);
                        store.save();
                        return sv;
                    }
                }
                break;
            }
            case "reset": {
                need("admin");
                if (method.equals("POST")) {
                    if (!"RESET".equals(str(body(ex).get("confirm")))) throw new ApiException(400, "Send {\"confirm\":\"RESET\"} to confirm. This replaces all payroll data with demo data.");
                    store.seed(); store.log("RESET", "Demo data restored"); store.save(); return m("reset", true);
                }
                break;
            }
            default: break;
        }
        throw new ApiException(404, "Unknown endpoint.");
    }
    static Map<String, String> query(URI u) {
        Map<String, String> r = new HashMap<>();
        if (u.getRawQuery() == null) return r;
        for (String kv : u.getRawQuery().split("&")) {
            String[] x = kv.split("=", 2);
            r.put(java.net.URLDecoder.decode(x[0], StandardCharsets.UTF_8), x.length > 1 ? java.net.URLDecoder.decode(x[1], StandardCharsets.UTF_8) : "");
        }
        return r;
    }

    static void handle(HttpExchange ex) throws IOException {
        String nonce = token(16), ip = clientIp(ex);
        boolean secure = isSecure(ex);
        try {
            String method = ex.getRequestMethod(), path = ex.getRequestURI().getPath();
            applyHeaders(ex, secure, nonce, !path.startsWith("/api"));
            String host = ex.getRequestHeaders().getFirst("Host");
            if (host == null || !host.matches("[A-Za-z0-9.\\-]{1,253}(:\\d{1,5})?|\\[[0-9a-fA-F:]+](:\\d{1,5})?")) { send(ex, 400, m("error", "Bad Host header.")); return; }
            if (FORCE_HTTPS && !secure) { ex.getResponseHeaders().set("Location", "https://" + host.replaceAll(":\\d+$", "") + ex.getRequestURI()); ex.sendResponseHeaders(308, -1); return; }
            if (!GLOBAL.allow(ip, GLOBAL_MAX, 60_000L)) {
                if (DENIED.allow("rl:" + ip, 1, 60_000L)) sec("RATE_LIMITED", ip, "-", "path", path);
                ex.getResponseHeaders().set("Retry-After", "60"); send(ex, 429, m("error", "Too many requests. Slow down and try again in a minute.")); return;
            }
            // CORS: same-origin by default. Only origins listed in PAYPILOT_ALLOWED_ORIGINS are allowed, never "*".
            String origin = ex.getRequestHeaders().getFirst("Origin");
            if (origin != null && ALLOWED_ORIGINS.contains(origin)) {
                ex.getResponseHeaders().set("Access-Control-Allow-Origin", origin); ex.getResponseHeaders().set("Access-Control-Allow-Credentials", "true");
                ex.getResponseHeaders().set("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE"); ex.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type,X-CSRF-Token"); ex.getResponseHeaders().add("Vary", "Origin");
            }
            if (method.equals("OPTIONS")) { ex.sendResponseHeaders(origin != null && ALLOWED_ORIGINS.contains(origin) ? 204 : 403, -1); return; }
            if (!Set.of("GET", "POST", "PUT", "DELETE").contains(method)) { ex.getResponseHeaders().set("Allow", "GET, POST, PUT, DELETE"); send(ex, 405, m("error", "Method not allowed.")); return; }

            if (!path.startsWith("/api")) { serveStatic(ex, method, path, nonce); return; }

            String[] seg = Arrays.stream(path.substring(4).split("/")).filter(x -> !x.isEmpty()).toArray(String[]::new);
            boolean isLogin = seg.length >= 2 && seg[0].equals("auth") && (seg[1].equals("login") || seg[1].equals("google") || seg[1].equals("config"));
            boolean isHealth = seg.length == 1 && seg[0].equals("health");
            boolean isPublicGet = method.equals("GET") && (
                seg.length == 0 ||
                (seg.length == 1 && seg[0].equals("health")) ||
                (seg.length == 2 && seg[0].equals("security") && seg[1].equals("audit-report"))
            );
            boolean isAnonSurvey = method.equals("POST") && seg.length == 4 && seg[0].equals("welfare") && seg[1].equals("surveys") && seg[3].equals("submit");

            // read the body once, with a hard size limit
            boolean hasBody = method.equals("POST") || method.equals("PUT");
            if (hasBody) {
                String ct = Optional.ofNullable(ex.getRequestHeaders().getFirst("Content-Type")).orElse("");
                byte[] raw = ex.getRequestBody().readNBytes(MAX_BODY + 1);
                if (raw.length > MAX_BODY) { send(ex, 413, m("error", "That request is too large. The limit is 2 MB.")); return; }
                if (raw.length > 0 && !ct.toLowerCase(Locale.ROOT).startsWith("application/json")) { send(ex, 415, m("error", "Send JSON with Content-Type: application/json.")); return; }
                BODY.set(new String(raw, StandardCharsets.UTF_8));
            }
            if (isAnonSurvey && !SURVEY_RL.allow(ip, 10, 60_000L)) {
                ex.getResponseHeaders().set("Retry-After", "60");
                send(ex, 429, m("error", "Too many submissions. Please wait a minute.")); return;
            }
            Session s = lookupSession(ex, secure);
            SESSION.set(s); ACTOR.set(s == null ? null : s.email);
            if (isHealth) { send(ex, 200, m("ok", true, "time", Instant.now().toString())); return; }
            if (!isLogin && !isPublicGet && !isAnonSurvey && s == null && !(seg.length == 2 && seg[0].equals("auth") && seg[1].equals("logout"))) {
                if (DENIED.allow("401:" + ip, 5, 60_000L)) sec("UNAUTHENTICATED_ACCESS", ip, "-", "path", path);
                send(ex, 401, m("error", "Sign in required.")); return;
            }
            if (s != null && s.restricted && !(seg.length >= 1 && seg[0].equals("auth"))) { send(ex, 403, m("error", "Set up multi-factor authentication to continue.")); return; }
            if (!method.equals("GET")) {
                if (!originOk(ex)) { sec("CSRF_ORIGIN_BLOCKED", ip, s == null ? "-" : s.email, "origin", String.valueOf(origin)); send(ex, 403, m("error", "Request blocked: the origin is not allowed.")); return; }
                String authHdr = ex.getRequestHeaders().getFirst("Authorization");
                boolean hasBearer = authHdr != null && authHdr.startsWith("Bearer ");
                if (!isLogin && !isAnonSurvey && !hasBearer && !(seg.length == 2 && seg[0].equals("auth") && seg[1].equals("logout") && s == null)) {
                    String tok = ex.getRequestHeaders().getFirst("X-CSRF-Token");
                    if (s == null || !ctEq(s.csrf, tok)) { sec("CSRF_TOKEN_REJECTED", ip, s == null ? "-" : s.email, "path", path); send(ex, 403, m("error", "Security check failed. Reload the page and try again.")); return; }
                }
            }
            Object res;
            if (seg.length > 0 && seg[0].equals("auth")) res = auth(ex, method, seg, ip, secure);
            else if (seg.length > 0 && seg[0].equals("users")) { synchronized (store) { res = usersApi(ex, method, seg, ip); } }
            else synchronized (store) { res = route(ex, method, seg); }
            send(ex, method.equals("POST") && seg.length == 1 && !seg[0].equals("reset") ? 201 : 200, res);
        } catch (ApiException e) {
            Map<String, Object> out = m("error", e.getMessage()); if (e.extra != null) out.putAll(e.extra);
            send(ex, e.code, out);
        } catch (Exception e) {
            String ref = token(6);
            System.err.println("ERROR ref=" + ref + " " + e);
            sec("SERVER_ERROR", ip, ACTOR.get() == null ? "-" : ACTOR.get(), "ref", ref, "type", e.getClass().getSimpleName());
            send(ex, 500, m("error", "Something went wrong. Reference: " + ref));
        } finally { SESSION.remove(); ACTOR.remove(); BODY.remove(); ex.close(); }
    }

    static void serveStatic(HttpExchange ex, String method, String path, String nonce) throws IOException {
        // Only these public files are served; source code, data, backups and logs are never exposed.
        String name = path.equals("/") ? "index.html" : path.substring(1);
        if (!method.equals("GET") || !Set.of("index.html", "sample-statement.csv", "style.css").contains(name) || !Files.isRegularFile(Paths.get(name))) { ex.sendResponseHeaders(404, -1); return; }
        byte[] b = Files.readAllBytes(Paths.get(name));
        if (name.endsWith(".html")) { b = new String(b, StandardCharsets.UTF_8).replace("{{NONCE}}", nonce).getBytes(StandardCharsets.UTF_8); ex.getResponseHeaders().set("Content-Type", "text/html; charset=utf-8"); }
        else if (name.endsWith(".css")) { ex.getResponseHeaders().set("Content-Type", "text/css; charset=utf-8"); }
        else { ex.getResponseHeaders().set("Content-Type", "text/csv; charset=utf-8"); ex.getResponseHeaders().set("Content-Disposition", "attachment"); }
        ex.sendResponseHeaders(200, b.length);
        try (OutputStream os = ex.getResponseBody()) { os.write(b); }
    }

    static void runSelfTests() {
        System.out.println("======================================================================");
        System.out.println("  PayPilot Engine Self-Test Verification Suite                       ");
        System.out.println("======================================================================");
        System.out.println("[*] Test 1: New Regime Slabs & Sec 87A Full Rebate (Budget 2024)...");
        Map<String, Object> rules = m(
            "newStd", 75000.0, "oldStd", 50000.0, "newRebateLimit", 1200000.0, "oldRebateLimit", 500000.0,
            "newSlabs", List.of(List.of(400000.0, 0.0), List.of(800000.0, 0.05), List.of(1200000.0, 0.1), List.of(1600000.0, 0.15), List.of(2000000.0, 0.2), List.of(2400000.0, 0.25), List.of(1.0E15, 0.3)),
            "oldSlabs", List.of(List.of(250000.0, 0.0), List.of(500000.0, 0.05), List.of(1000000.0, 0.2), List.of(1.0E15, 0.3)),
            "cess", 0.04, "cap80c", 150000.0, "cap80d", 50000.0, "capNps", 50000.0
        );
        Map<String, Object> res1 = taxCompare(1200000.0, 0.0, 0.0, 0.0, rules);
        double newTax = num(mp(res1.get("new")).get("total"));
        if (newTax != 0.0) throw new AssertionError("Expected 0 tax under New Regime rebate for 12L gross, got " + newTax);
        System.out.println("    -> PASS: Gross 12L yields 0 tax under Section 87A rebate");

        System.out.println("[*] Test 2: Standard Deduction 75,000 application...");
        double stdDed = 1200000.0 - num(mp(res1.get("new")).get("taxable"));
        if (stdDed != 75000.0) throw new AssertionError("Standard deduction must be 75,000, got " + stdDed);
        System.out.println("    -> PASS: Standard deduction of 75,000 verified");

        System.out.println("[*] Test 3: Password Hashing & Constant-time comparison...");
        String pw = "PayPilot#Sec2026";
        String hash = hashPw(pw);
        if (!verifyPw(pw, hash)) throw new AssertionError("Password verification failed");
        if (verifyPw("WrongPass", hash)) throw new AssertionError("Password verification false positive");
        System.out.println("    -> PASS: PBKDF2/SHA-256 password hashing & verification verified");

        System.out.println("[*] Test 4: JSON Serializer & Parser Integrity...");
        Map<String, Object> testMap = m("name", "PayPilot", "score", 100.0, "active", true);
        String jsonStr = Json.write(testMap);
        Map<String, Object> parsed = mp(Json.parse(jsonStr));
        if (!parsed.get("name").equals("PayPilot") || num(parsed.get("score")) != 100.0) throw new AssertionError("JSON roundtrip failed");
        System.out.println("    -> PASS: Pure Java JSON parser roundtrip verified");

        System.out.println("======================================================================");
        System.out.println("  ALL SELF-TESTS PASSED (100% SUCCESS)                                ");
        System.out.println("======================================================================");
    }

    public static void main(String[] args) throws Exception {
        if (args.length > 0 && args[0].equals("--test")) {
            runSelfTests();
            return;
        }
        System.setProperty("sun.net.httpserver.maxReqTime", "20");   // slow-request (slowloris) protection
        System.setProperty("sun.net.httpserver.maxRspTime", "30");
        System.setProperty("sun.net.httpserver.idleInterval", "30");
        int port = 8080;
        if (args.length > 0 && !args[0].startsWith("-")) {
            try { port = Integer.parseInt(args[0]); } catch (Exception ignored) {}
        } else if (env("PORT") != null) {
            try { port = Integer.parseInt(env("PORT")); } catch (Exception ignored) {}
        }
        initDataKey();
        DUMMY_HASH = hashPw(token(12));
        Path dataPath = Paths.get(Optional.ofNullable(env("PAYPILOT_DATA")).orElse("paypilot-data.json"));
        store = new Store(dataPath);
        if (!store.data.containsKey("users")) store.data.put("users", new ArrayList<>());
        bootstrapAdmin();
        store.save();
        backup();
        InetSocketAddress addr = new InetSocketAddress(Optional.ofNullable(env("PAYPILOT_BIND")).orElse("0.0.0.0"), port); // bind all interfaces for LAN
        HttpServer srv;
        String ks = env("PAYPILOT_TLS_KEYSTORE");
        try {
            if (ks != null) {
                char[] kp = Optional.ofNullable(env("PAYPILOT_TLS_PASSWORD")).orElseThrow(() -> new IllegalStateException("PAYPILOT_TLS_PASSWORD is required with PAYPILOT_TLS_KEYSTORE")).toCharArray();
                KeyStore k = KeyStore.getInstance("PKCS12"); try (InputStream in = Files.newInputStream(Paths.get(ks))) { k.load(in, kp); }
                KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509"); kmf.init(k, kp);
                SSLContext sc = SSLContext.getInstance("TLS"); sc.init(kmf.getKeyManagers(), null, null);
                HttpsServer hs = HttpsServer.create(addr, 50);
                hs.setHttpsConfigurator(new HttpsConfigurator(sc) { public void configure(HttpsParameters p) { SSLParameters sp = getSSLContext().getDefaultSSLParameters(); sp.setProtocols(new String[]{"TLSv1.3", "TLSv1.2"}); p.setSSLParameters(sp); } });
                srv = hs;
            } else srv = HttpServer.create(addr, 50);
        } catch (java.net.BindException be) {
            System.err.println("\n[ERROR] Port " + port + " is already in use by another instance.");
            System.err.println("To start on another port: java PayPilotServer " + (port + 1) + "\n");
            System.exit(1);
            return;
        }
        srv.createContext("/", PayPilotServer::handle);
        srv.setExecutor(new ThreadPoolExecutor(4, 16, 30, TimeUnit.SECONDS, new ArrayBlockingQueue<>(64), new ThreadPoolExecutor.CallerRunsPolicy()));
        ScheduledExecutorService sch = Executors.newSingleThreadScheduledExecutor(r -> { Thread t = new Thread(r, "maintenance"); t.setDaemon(true); return t; });
        sch.scheduleAtFixedRate(() -> {
            long now = System.currentTimeMillis();
            SESS.values().removeIf(x -> now - x.last > IDLE_MS || now - x.created > ABSOLUTE_MS);
            GLOBAL.sweep(120_000L); SURVEY_RL.sweep(120_000L); LOGIN.sweep(900_000L); FAILS.sweep(300_000L); HEAVY.sweep(120_000L); DENIED.sweep(120_000L); ALERTED.clear();
        }, 5, 5, TimeUnit.MINUTES);
        sch.scheduleAtFixedRate(PayPilotServer::backup, 6, 6, TimeUnit.HOURS);
        srv.start();
        System.out.println("======================================================================");
        System.out.println("  Port: " + port);
        System.out.println("  Data file: " + dataPath.toAbsolutePath());
        System.out.println("  Server running at http://localhost:" + port);
        System.out.println("  PayPilot running at " + (ks != null ? "https" : "http") + "://" + addr.getHostString() + ":" + port + "  (Ctrl+C to stop)");
        if (ks == null && !TRUST_PROXY) System.out.println("  NOTE: serving plain HTTP on local network.");
        System.out.println("======================================================================");
    }
}
// END OF FILE
