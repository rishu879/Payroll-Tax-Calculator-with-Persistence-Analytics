import re

with open("PayPilotServer.java", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add defaultWelfareRules() right after defaultGstRules()
welfare_rules_method = """    static Map<String, Object> defaultWelfareRules() {
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
"""

if "defaultWelfareRules" not in code:
    code = code.replace("    static Map<String, Object> defaultGstRules() {", welfare_rules_method + "\n    static Map<String, Object> defaultGstRules() {")

# 2. Add welfare helper methods in Store
store_methods = """        Map<String, Object> welfareRules() {
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
"""
if "welfareRules()" not in code:
    code = code.replace("        Map<String, Object> gstRules() { return mp(data.get(\"gstRules\")); }", "        Map<String, Object> gstRules() { return mp(data.get(\"gstRules\")); }\n" + store_methods)

# 3. Seed welfare data in Store.seed()
seed_init = """            data.put("welfareRules", defaultWelfareRules());
            data.put("welfareLedger", seedWelfareLedger());
            data.put("welfareSurveys", seedWelfareSurveys());
            data.put("welfareSaved", new ArrayList<>());
"""
if "seedWelfareLedger" not in code:
    seed_helpers = """    static List<Object> seedWelfareLedger() {
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
"""
    code = code.replace("    static final class Store {", seed_helpers + "\n    static final class Store {")
    code = code.replace("            data.put(\"gstRules\", defaultGstRules());", "            data.put(\"gstRules\", defaultGstRules());\n" + seed_init)

# 4. Rate limiter for survey
if "SURVEY_RL" not in code:
    code = code.replace("static final Limiter GLOBAL = new Limiter(), LOGIN = new Limiter(), FAILS = new Limiter(), HEAVY = new Limiter(), DENIED = new Limiter();",
                        "static final Limiter GLOBAL = new Limiter(), LOGIN = new Limiter(), FAILS = new Limiter(), HEAVY = new Limiter(), DENIED = new Limiter(), SURVEY_RL = new Limiter();")

# 5. Handle route case "welfare"
welfare_route = """            case "welfare": {
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
"""
if 'case "welfare":' not in code:
    code = code.replace('            case "reset": {', welfare_route + '            case "reset": {')

# 6. In handle(), allow public GET for /api/welfare/rules and public POST for /api/welfare/surveys/<id>/submit
public_check = """            boolean isPublicRules = method.equals("GET") && seg.length == 2 && seg[0].equals("welfare") && seg[1].equals("rules");
            boolean isAnonSurvey = method.equals("POST") && seg.length == 4 && seg[0].equals("welfare") && seg[1].equals("surveys") && seg[3].equals("submit");
"""
if "isPublicRules" not in code:
    code = code.replace("            boolean isLogin = seg.length == 2 && seg[0].equals(\"auth\") && seg[1].equals(\"login\"), isHealth = seg.length == 1 && seg[0].equals(\"health\");",
                        "            boolean isLogin = seg.length == 2 && seg[0].equals(\"auth\") && seg[1].equals(\"login\"), isHealth = seg.length == 1 && seg[0].equals(\"health\");\n" + public_check)

    # Replace 401 unauthenticated check
    code = code.replace("""            if (!isLogin && s == null && !(seg.length == 2 && seg[0].equals("auth") && seg[1].equals("logout"))) {""",
                        """            if (!isLogin && !isPublicRules && !isAnonSurvey && s == null && !(seg.length == 2 && seg[0].equals("auth") && seg[1].equals("logout"))) {""")

    # Replace CSRF check for anon survey
    code = code.replace("""                if (!isLogin && !(seg.length == 2 && seg[0].equals("auth") && seg[1].equals("logout") && s == null)) {""",
                        """                if (!isLogin && !isAnonSurvey && !(seg.length == 2 && seg[0].equals("auth") && seg[1].equals("logout") && s == null)) {""")

    # Add rate limiting on anon survey submit
    anon_rl_check = """            if (isAnonSurvey && !SURVEY_RL.allow(ip, 10, 60_000L)) {
                ex.getResponseHeaders().set("Retry-After", "60");
                send(ex, 429, m("error", "Too many submissions. Please wait a minute.")); return;
            }
"""
    code = code.replace("""            Session s = lookupSession(ex, secure);""", anon_rl_check + """            Session s = lookupSession(ex, secure);""")

# Sweep SURVEY_RL in scheduler
if "SURVEY_RL.sweep" not in code:
    code = code.replace("GLOBAL.sweep(120_000L);", "GLOBAL.sweep(120_000L); SURVEY_RL.sweep(120_000L);")

with open("PayPilotServer.java", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated PayPilotServer.java successfully!")
