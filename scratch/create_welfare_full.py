# -*- coding: utf-8 -*-
"""
Python script to assemble and inject the complete Worker Rights & Welfare JS module into index.html.
"""
import re

print("Building complete Welfare JS module...")

with open("scratch/welfare_module.js", "w", encoding="utf-8") as f:
    f.write(r'''
    // =========================================================================
    // WORKER RIGHTS & WELFARE: INTERNATIONALIZATION, VOICE, CALCS & ROUTER
    // =========================================================================

    // Current Active Language (Remembers in localStorage)
    window.currentLang = (function() {
      try {
        return localStorage.getItem('paypilot_lang') || 'en';
      } catch (e) {
        return 'en';
      }
    })();

    // 1. Comprehensive 4-Language Dictionary (English, Hindi, Punjabi, Urdu)
    const WELFARE_I18N = {
      en: {
        welfareTitle: "Worker Rights & Welfare Hub",
        welfareSubtitle: "Practical statutory guidance, fair-pay calculation, and social security tools for workers, domestic staff, and small business owners in India.",
        lastUpdatedPrefix: "Based on rules last updated:",
        sourcePrefix: "Source:",
        disclaimer: "Please verify with the official government source or a labour officer.",
        readAloud: "🔊 Read Aloud",
        copyText: "📋 Copy Result",
        copied: "✓ Copied!",
        shareWhatsApp: "💬 WhatsApp",
        saveResult: "💾 Save to Vault",
        savedSuccess: "✓ Saved securely to your device and account!",
        speakMic: "🎤 Speak",
        whatToDoNext: "What To Do Next",
        numbersUsed: "Numbers & Rules Used",
        calcButton: "Calculate Now",
        backToHub: "← Back to Welfare Hub",
        openTool: "Open Tool ➔",
        speechNotSupported: "Speech recognition is not supported in this browser. Please type directly into the input.",
        ttsNotSupported: "Text-to-speech is not supported on this device.",

        // Hub Cards
        fairPayName: "Fair-Pay Checker",
        fairPayDesc: "Check if wages meet state minimum wage laws, overtime double-pay, and rest day rules.",
        ledgerName: "Domestic & Daily-Wage Ledger",
        ledgerDesc: "Track attendance, advances, and Diwali gifts for maids, cooks, and drivers with easy WhatsApp payslips.",
        benefitsName: "Benefits Finder",
        benefitsDesc: "Answer 5 questions to find out what PF, ESI, gratuity, bonus, and maternity benefits apply to you.",
        schemesName: "Government Scheme Matcher",
        schemesDesc: "Match with e-Shram, PM-SYM pension, Ayushman Bharat, APY, Mudra, and insurance schemes.",
        loanTrapName: "Loan Trap Detector",
        loanTrapDesc: "Uncover the real yearly APR interest rate on daily, weekly, or EMI loans and spot red flags.",
        womenFamilyName: "Women & Family Support",
        womenFamilyDesc: "Maternity benefit planner (26 paid weeks), safe night shift checklist, and equal pay checker.",
        pulseName: "Work-Culture Pulse (Anonymous)",
        pulseDesc: "6-question monthly team survey. Anonymous protection: owner sees averages only after 5+ responses.",
        gigIncomeName: "Gig & Freelancer Helper",
        gigIncomeDesc: "Track app earnings across Swiggy, Uber, gigs. See 44ADA tax savings and loan income certificates.",
        savingsCoachName: "Money Lessons & Savings Coach",
        savingsCoachDesc: "10 simple lessons on emergency funds, UPI fraud, and debt traps with badges & savings split coach.",
        grievanceName: "Grievance Helper",
        grievanceDesc: "Generate legal complaint letters for unpaid wages or PF fraud, and find official helplines.",
        adminRulesName: "Rules & Data Editor",
        adminRulesDesc: "Admin portal to update state minimum wages, scheme records, and social security thresholds.",

        // Fair-Pay
        state: "State / Jurisdiction",
        skillLevel: "Skill Level",
        unskilled: "Unskilled",
        semiSkilled: "Semi-Skilled",
        skilled: "Skilled",
        highlySkilled: "Highly Skilled",
        payType: "Payment Type",
        monthly: "Monthly Pay",
        daily: "Daily Wage",
        amountPaid: "Amount Paid (₹)",
        hoursPerDay: "Working Hours Per Day",
        daysPerWeek: "Days Worked Per Week",
        overtimeHours: "Overtime Hours in Month",
        payDate: "Salary Paid on Day of Month",
        statutoryMinWage: "Statutory Minimum Wage",
        overtimeDue: "Overtime Due (Double Rate)",
        shortfallLabel: "Monthly Shortfall",
        verdictGreen: "VERDICT: GREEN — FAIR & LAWFUL PAY",
        verdictAmber: "VERDICT: AMBER — MINIMUM WAGE MET, BUT OVERTIME OR TIMING ISSUES DETECTED",
        verdictRed: "VERDICT: RED — WAGES BELOW STATUTORY MINIMUM LIMIT",
        msgToBossTitle: "Polite Message To Show / Send Employer",

        // Ledger
        helpersList: "Your Household & Shop Helpers",
        addHelper: "+ Add New Helper",
        helperName: "Helper Name",
        helperRole: "Role (Maid, Cook, Driver, Worker)",
        helperPhone: "WhatsApp Phone Number",
        agreedWage: "Agreed Wage (₹)",
        todayAttendance: "Today's Attendance",
        present: "Present",
        absent: "Absent",
        halfDay: "Half Day",
        paidLeave: "Paid Leave",
        advancesTaken: "Advances Taken (₹)",
        addAdvance: "+ Add Advance",
        bonusGift: "Festival / Bonus Gift (₹)",
        netToPay: "Net Salary Payable",
        generatePayslip: "📄 Generate Payslip",
        incomeProofCert: "📜 Print Loan Income Proof",

        // Benefits
        yearsInJob: "Years In This Job",
        numEmployees: "Number of Employees in Company",
        gender: "Gender",
        male: "Male",
        female: "Female",
        other: "Other",

        // Loan Trap
        loanAmount: "Cash Amount Received (₹)",
        instalmentAmount: "Instalment Amount (₹)",
        instalmentFreq: "Payment Frequency",
        numInstalments: "Total Number of Instalments",
        procFees: "Processing Fee Deducted Upfront (₹)",
        trueApr: "True Yearly Interest Rate (APR)",
        totalRepaid: "Total Amount Repaid (₹)",
        extraPaid: "Extra Interest & Fees Paid (₹)",
        bankComparison: "Bank Loan Comparison (11% p.a.)",
        loanFair: "FAIR LOAN: Rate is reasonable and within formal banking norms.",
        loanHigh: "HIGH COST: Rate is high (MFI / NBFC personal loan range). Negotiate lower rate.",
        loanTrap: "DANGEROUS LOAN TRAP: Annual interest exceeds 36% p.a. High risk of debt trap!",

        // Pulse
        surveyTitle: "Workplace Respect & Culture Pulse",
        anonNotice: "Your answers are 100% anonymous. The employer can NEVER see individual answers. Aggregated scores unlock only after at least 5 team members have participated.",
        submitVote: "Submit Anonymous Response",
        activeSurveys: "Active Surveys & Team Scores",
        createSurvey: "+ Create New Monthly Survey",
        lockedSurvey: "🔒 Anonymous Protection Active: Responses collected so far. Individual replies are hidden. Scores will unlock once at least 5 team members participate.",
        unlockedSurvey: "Unlocked Aggregate Team Scores (Average 1 to 5)",

        // Grievance
        issueType: "Select Problem / Dispute",
        unpaidSalary: "Unpaid or Delayed Salary / Wages",
        illegalTerm: "Illegal Termination / Fired without notice",
        pfFraud: "PF Deducted but not deposited to EPFO",
        harassment: "Workplace Harassment / Unsafe Conditions",
        deniedMaternity: "Denial of Maternity Leave or Benefits",
        workerName: "Your Full Name",
        employerName: "Employer / Company / Shop Name",
        workplaceAddr: "Workplace Address & City",
        joiningDate: "Date of Joining",
        unpaidAmount: "Unpaid Amount Claimed (₹)",
        generateNotice: "📝 Generate Formal Legal Notice",
        helplineTitle: "Official Helplines & Govt Grievance Portals",
        proofToKeep: "Critical Proof & Documents To Keep"
      },

      hi: {
        welfareTitle: "मजदूर व कामगार अधिकार एवं कल्याण केंद्र",
        welfareSubtitle: "भारतीय मजदूरों, घरेलू सहायकों और छोटे दुकानदारों के लिए कानूनी न्यूनतम वेतन, सरकारी योजनाएं और सामाजिक सुरक्षा के आसान साधन।",
        lastUpdatedPrefix: "नियम अंतिम अपडेट:",
        sourcePrefix: "स्रोत:",
        disclaimer: "कृपया आधिकारिक सरकारी स्रोत या श्रम अधिकारी से पुष्टि अवश्य करें।",
        readAloud: "🔊 बोलकर सुनाएं",
        copyText: "📋 परिणाम कॉपी करें",
        copied: "✓ कॉपी हो गया!",
        shareWhatsApp: "💬 व्हाट्सएप पर भेजें",
        saveResult: "💾 सुरक्षित सहेजें",
        savedSuccess: "✓ आपके उपकरण पर सुरक्षित सहेजा गया!",
        speakMic: "🎤 बोलें",
        whatToDoNext: "आगे क्या कदम उठाएं?",
        numbersUsed: "उपयोग किए गए नियम व आंकड़े",
        calcButton: "अभी गणना करें",
        backToHub: "← कल्याण केंद्र पर वापस जाएं",
        openTool: "सुविधा खोलें ➔",
        speechNotSupported: "इस ब्राउज़र में आवाज़ पहचान उपलब्ध नहीं है। कृपया लिखकर भरें।",
        ttsNotSupported: "इस फोन/कंप्यूटर पर आवाज़ में पढ़ना उपलब्ध नहीं है।",

        fairPayName: "उचित वेतन जांच (Fair-Pay)",
        fairPayDesc: "जांचें कि क्या वेतन सरकारी न्यूनतम मजदूरी, दोहरे ओवरटाइम और साप्ताहिक छुट्टी के नियमों के अनुसार है।",
        ledgerName: "घरेलू व दिहाड़ी सहायक बहीखाता",
        ledgerDesc: "कामवाली, रसोइया और ड्राइवर की हाजिरी, एडवांस और त्योहार बोनस का हिसाब रखें। व्हाट्सएप पर सैलरी स्लिप भेजें।",
        benefitsName: "अधिकार व लाभ खोजक (Benefits)",
        benefitsDesc: "5 आसान सवालों के जवाब दें और जानें कि क्या आपको PF, ESI, ग्रेच्युटी, बोनस और मातृत्व लाभ मिलना चाहिए।",
        schemesName: "सरकारी योजना खोजक (Schemes)",
        schemesDesc: "ई-श्रम, श्रम योगी मान-धन पेंशन, आयुष्मान भारत, जन धन और सुरक्षा बीमा योजनाओं से तुरंत जुड़ें।",
        loanTrapName: "कर्ज जाल पहचानकर्ता (Loan Trap)",
        loanTrapDesc: "दैनिक, साप्ताहिक या किस्तों वाले कर्ज का असली सालाना ब्याज (APR) जानें और सूदखोरों से बचें।",
        womenFamilyName: "महिला व परिवार सुरक्षा",
        womenFamilyDesc: "26 हफ्तों का सवेतन मातृत्व अवकाश प्लानर, सुरक्षित नाइट-शिफ्ट चेकलिस्ट और समान वेतन जांच।",
        pulseName: "कार्यस्थल संस्कृति सर्वे (गुप्त)",
        pulseDesc: "6 सवालों का मासिक सर्वे। मालिक को 5 से कम जवाबों पर कुछ नहीं दिखेगा—पूरी गोपनीयता की गारंटी।",
        gigIncomeName: "गिग व डिलीवरी साथी आय सहायक",
        gigIncomeDesc: "स्विगी, जोमैटो, उबर की कमाई और खर्च जोड़ें। धारा 44ADA टैक्स छूट और लोन के लिए आय प्रमाण बनाएं।",
        savingsCoachName: "पैसे की सीख व बचत गुरु",
        savingsCoachDesc: "इमरजेंसी फंड, UPI फ्रॉड से बचाव और कर्ज मुक्ति के 10 आसान पाठ, क्विज और बैज।",
        grievanceName: "शिकायत व कानूनी पत्र सहायक",
        grievanceDesc: "रुके वेतन या PF चोरी के लिए कानूनी नोटिस पत्र तैयार करें और सरकारी हेल्पलाइन नंबर पाएं।",
        adminRulesName: "नियम व दर संपादक",
        adminRulesDesc: "एडमिन स्क्रीन: न्यूनतम मजदूरी, सरकारी योजनाओं की पात्रता और लाभ सीमाओं को अपडेट करें।",

        state: "राज्य / केंद्र शासित प्रदेश",
        skillLevel: "कार्य कुशलता (Skill)",
        unskilled: "अकुशल (Unskilled)",
        semiSkilled: "अर्ध-कुशल (Semi-Skilled)",
        skilled: "कुशल (Skilled)",
        highlySkilled: "अति-कुशल (Highly Skilled)",
        payType: "वेतन का प्रकार",
        monthly: "मासिक वेतन",
        daily: "दैनिक मजदूरी",
        amountPaid: "प्राप्त वेतन (₹)",
        hoursPerDay: "प्रतिदिन काम के घंटे",
        daysPerWeek: "हफ्ते में काम के दिन",
        overtimeHours: "महीने में ओवरटाइम के कुल घंटे",
        payDate: "वेतन मिलने की तारीख (माह का दिन)",
        statutoryMinWage: "सरकारी न्यूनतम मजदूरी",
        overtimeDue: "बकाया ओवरटाइम (दोगुनी दर)",
        shortfallLabel: "मासिक कमी (रुपयों में)",
        verdictGreen: "निर्णय: हरा (GREEN) — वेतन पूरी तरह कानूनी व उचित है",
        verdictAmber: "निर्णय: पीला (AMBER) — न्यूनतम वेतन मिला है, लेकिन ओवरटाइम या देरी की समस्या है",
        verdictRed: "निर्णय: लाल (RED) — वेतन सरकारी न्यूनतम मजदूरी से कम है!",
        msgToBossTitle: "मालिक को दिखाने / व्हाट्सएप पर भेजने योग्य संदेश",

        helpersList: "आपके घरेलू व दुकान के सहायक",
        addHelper: "+ नया सहायक जोड़ें",
        helperName: "सहायक का नाम",
        helperRole: "काम (सफाई, रसोइया, ड्राइवर, मजदूर)",
        helperPhone: "व्हाट्सएप फोन नंबर",
        agreedWage: "तय वेतन (₹)",
        todayAttendance: "आज की हाजिरी",
        present: "उपस्थित",
        absent: "अनुपस्थित",
        halfDay: "आधा दिन",
        paidLeave: "सवेतन छुट्टी",
        advancesTaken: "लिया गया एडवांस (₹)",
        addAdvance: "+ एडवांस दर्ज करें",
        bonusGift: "त्योहार उपहार / बोनस (₹)",
        netToPay: "कुल देय वेतन",
        generatePayslip: "📄 सैलरी स्लिप बनाएं",
        incomeProofCert: "📜 लोन के लिए आय प्रमाण पत्र",

        yearsInJob: "इस नौकरी में कुल वर्ष",
        numEmployees: "कंपनी में कुल कर्मचारियों की संख्या",
        gender: "लिंग",
        male: "पुरुष",
        female: "महिला",
        other: "अन्य",

        loanAmount: "हाथ में मिला कुल कर्ज (₹)",
        instalmentAmount: "किस्त की राशि (₹)",
        instalmentFreq: "किस्त की अवधि",
        numInstalments: "कुल किस्तों की संख्या",
        procFees: "पहले काटी गई फीस (₹)",
        trueApr: "असली सालाना ब्याज दर (APR %)",
        totalRepaid: "कुल वापस चुकाई गई राशि (₹)",
        extraPaid: "कुल अतिरिक्त ब्याज व फीस (₹)",
        bankComparison: "सरकारी बैंक कर्ज से तुलना (11% सालाना)",
        loanFair: "उचित कर्ज: ब्याज दर सामान्य और बैंक नियमों के दायरे में है।",
        loanHigh: "महंगा कर्ज: ब्याज दर ऊंची है (माइक्रोफाइनेंस सीमा)। ध्यान से निर्णय लें।",
        loanTrap: "खतरनाक कर्ज जाल! सालाना ब्याज 36% से अधिक है। सूदखोरी का भारी खतरा!",

        surveyTitle: "मासिक कार्यस्थल सम्मान व संस्कृति सर्वे",
        anonNotice: "आपके जवाब 100% गुप्त हैं। मालिक किसी भी व्यक्ति का जवाब नहीं देख सकता। जब कम से कम 5 साथी जवाब देंगे, तभी सिर्फ औसत स्कोर दिखेगा।",
        submitVote: "गुप्त रूप से जवाब भेजें",
        activeSurveys: "सक्रिय सर्वे व टीम का स्कोर",
        createSurvey: "+ नया मासिक सर्वे बनाएं",
        lockedSurvey: "🔒 गोपनीयता सुरक्षा सक्रिय: अभी तक जवाब मिले हैं। व्यक्तिगत उत्तर सुरक्षित हैं। 5 जवाब पूरे होने पर औसत स्कोर खुलेगा।",
        unlockedSurvey: "टीम का औसत स्कोर (1 से 5 सितारे)",

        issueType: "समस्या का चयन करें",
        unpaidSalary: "वेतन नहीं मिला या बहुत देरी से मिला",
        illegalTerm: "बिना नोटिस या बिना कारण नौकरी से निकाला",
        pfFraud: "सैलरी से PF काटा लेकिन खाते में जमा नहीं किया",
        harassment: "कार्यस्थल पर प्रताड़ना या असुरक्षित माहौल",
        deniedMaternity: "मातृत्व अवकाश या मातृत्व लाभ देने से इनकार",
        workerName: "आपका पूरा नाम",
        employerName: "मालिक / कंपनी / दुकान का नाम",
        workplaceAddr: "कार्यस्थल का पता व शहर",
        joiningDate: "नौकरी शुरू करने की तारीख",
        unpaidAmount: "बकाया दावा राशि (₹)",
        generateNotice: "📝 कानूनी मांग पत्र तैयार करें",
        helplineTitle: "सरकारी हेल्पलाइन व शिकायत पोर्टल",
        proofToKeep: "सुरक्षित रखने योग्य जरूरी सबूत"
      },

      pa: {
        welfareTitle: "ਕਾਮਿਆਂ ਦੇ ਅਧਿਕਾਰ ਅਤੇ ਭਲਾਈ ਕੇਂਦਰ",
        welfareSubtitle: "ਭਾਰਤੀ ਮਜ਼ਦੂਰਾਂ, ਘਰੇਲੂ ਸਹਾਇਕਾਂ ਅਤੇ ਛੋਟੇ ਦੁਕਾਨਦਾਰਾਂ ਲਈ ਕਾਨੂੰਨੀ ਘੱਟੋ-ਘੱਟ ਤਨਖਾਹ, ਸਰਕਾਰੀ ਸਕੀਮਾਂ ਅਤੇ ਸਮਾਜਿਕ ਸੁਰੱਖਿਆ।",
        lastUpdatedPrefix: "ਨਿਯਮ ਆਖਰੀ ਵਾਰ ਅੱਪਡੇਟ ਕੀਤੇ ਗਏ:",
        sourcePrefix: "ਸਰੋਤ:",
        disclaimer: "ਕਿਰਪਾ ਕਰਕੇ ਅਧਿਕਾਰਤ ਸਰਕਾਰੀ ਸਰੋਤ ਜਾਂ ਕਿਰਤ ਅਧਿਕਾਰੀ ਤੋਂ ਪੁਸ਼ਟੀ ਜ਼ਰੂਰ ਕਰੋ।",
        readAloud: "🔊 ਪੜ੍ਹ ਕੇ ਸੁਣਾਓ",
        copyText: "📋 ਕਾਪੀ ਕਰੋ",
        copied: "✓ ਕਾਪੀ ਹੋ ਗਿਆ!",
        shareWhatsApp: "💬 ਵਟਸਐਪ 'ਤੇ ਭੇਜੋ",
        saveResult: "💾 ਸੁਰੱਖਿਅਤ ਰੱਖੋ",
        savedSuccess: "✓ ਤੁਹਾਡੇ ਯੰਤਰ 'ਤੇ ਸੁਰੱਖਿਅਤ ਹੋ ਗਿਆ!",
        speakMic: "🎤 ਬੋਲੋ",
        whatToDoNext: "ਅਗਲਾ ਕਦਮ ਕੀ ਚੁੱਕਣਾ ਹੈ?",
        numbersUsed: "ਵਰਤੇ ਗਏ ਨਿਯਮ ਅਤੇ ਅੰਕੜੇ",
        calcButton: "ਹੁਣੇ ਹਿਸਾਬ ਲਗਾਓ",
        backToHub: "← ਵਾਪਸ ਭਲਾਈ ਕੇਂਦਰ ਜਾਓ",
        openTool: "ਟੂਲ ਖੋਲ੍ਹੋ ➔",
        speechNotSupported: "ਇਸ ਬ੍ਰਾਊਜ਼ਰ ਵਿੱਚ ਬੋਲਣ ਦੀ ਸਹੂਲਤ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।",
        ttsNotSupported: "ਇਸ ਫ਼ੋਨ 'ਤੇ ਪੜ੍ਹ ਕੇ ਸੁਣਾਉਣ ਦੀ ਸਹੂਲਤ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।",

        fairPayName: "ਸਹੀ ਤਨਖਾਹ ਜਾਂਚ (Fair-Pay)",
        fairPayDesc: "ਜਾਂਚੋ ਕਿ ਤਨਖਾਹ ਘੱਟੋ-ਘੱਟ ਮਜ਼ਦੂਰੀ ਅਤੇ ਦੁੱਗਣੇ ਓਵਰਟਾਈਮ ਦੇ ਨਿਯਮਾਂ ਅਨੁਸਾਰ ਹੈ ਜਾਂ ਨਹੀਂ।",
        ledgerName: "ਘਰੇਲੂ ਤੇ ਦਿਹਾੜੀਦਾਰ ਵਹੀਖਾਤਾ",
        ledgerDesc: "ਕੰਮ ਵਾਲੀ, ਰਸੋਈਏ ਅਤੇ ਡਰਾਈਵਰ ਦੀ ਹਾਜ਼ਰੀ, ਐਡਵਾਂਸ ਅਤੇ ਤਿਉਹਾਰ ਬੋਨਸ ਦਾ ਆਸਾਨ ਹਿਸਾਬ। ਵਟਸਐਪ 'ਤੇ ਸਲਿੱਪ ਭੇਜੋ।",
        benefitsName: "ਸਹੂਲਤਾਂ ਤੇ ਹੱਕ ਖੋਜੀ (Benefits)",
        benefitsDesc: "5 ਸੌਖੇ ਸਵਾਲਾਂ ਦੇ ਜਵਾਬ ਦਿਓ ਅਤੇ ਜਾਣੋ ਕਿ ਤੁਹਾਨੂੰ PF, ESI, ਗ੍ਰੈਚੁਟੀ ਅਤੇ ਬੋਨਸ ਮਿਲਣਾ ਚਾਹੀਦਾ ਹੈ।",
        schemesName: "ਸਰਕਾਰੀ ਸਕੀਮਾਂ ਮਿਲਾਓ",
        schemesDesc: "ਈ-ਸ਼੍ਰਮ, ਪੀਐਮ-ਮਾਨਧਨ ਪੈਨਸ਼ਨ, ਆਯੁਸ਼ਮਾਨ ਭਾਰਤ, ਜਨ ਧਨ ਅਤੇ ਸੁਰੱਖਿਆ ਬੀਮਾ ਸਕੀਮਾਂ ਲੱਭੋ।",
        loanTrapName: "ਕਰਜ਼ੇ ਦਾ ਜਾਲ ਪਛਾਣੋ (Loan Trap)",
        loanTrapDesc: "ਰੋਜ਼ਾਨਾ ਜਾਂ ਕਿਸ਼ਤਾਂ ਵਾਲੇ ਕਰਜ਼ੇ ਦਾ ਅਸਲ ਸਾਲਾਨਾ ਵਿਆਜ (APR) ਜਾਣੋ ਅਤੇ ਧੋਖੇ ਤੋਂ ਬਚੋ।",
        womenFamilyName: "ਮਹਿਲਾ ਤੇ ਪਰਿਵਾਰ ਸੁਰੱਖਿਆ",
        womenFamilyDesc: "26 ਹਫ਼ਤਿਆਂ ਦੀ ਤਨਖਾਹ ਵਾਲੀ ਜਣੇਪਾ ਛੁੱਟੀ, ਸੁਰੱਖਿਅਤ ਨਾਈਟ-ਸ਼ਿਫਟ ਅਤੇ ਬਰਾਬਰ ਤਨਖਾਹ ਜਾਂਚ।",
        pulseName: "ਕੰਮ ਦਾ ਮਾਹੌਲ ਸਰਵੇਖਣ (ਗੁਪਤ)",
        pulseDesc: "6 ਸਵਾਲਾਂ ਦਾ ਸਰਵੇਖਣ। ਪੂਰੀ ਗੁਪਤਤਾ: 5 ਤੋਂ ਘੱਟ ਜਵਾਬਾਂ 'ਤੇ ਮਾਲਕ ਨੂੰ ਕੁਝ ਨਹੀਂ ਦਿਸੇਗਾ।",
        gigIncomeName: "ਡਿਲੀਵਰੀ ਤੇ ਫ੍ਰੀਲਾਂਸ ਕਮਾਈ ਸਹਾਇਕ",
        gigIncomeDesc: "ਸਵਿਗੀ, ਜ਼ੋਮੈਟੋ, ਓਲਾ ਦੀ ਕਮਾਈ ਅਤੇ ਖਰਚੇ ਜੋੜੋ। ਟੈਕਸ ਬੱਚਤ ਅਤੇ ਲੋਨ ਲਈ ਆਮਦਨ ਸਰਟੀਫਿਕੇਟ ਬਣਾਓ।",
        savingsCoachName: "ਪੈਸੇ ਦੀ ਸਿੱਖਿਆ ਤੇ ਬੱਚਤ ਗੁਰੂ",
        savingsCoachDesc: "ਐਮਰਜੈਂਸੀ ਫੰਡ, UPI ਧੋਖਾਧੜੀ ਤੋਂ ਬਚਾਅ ਦੇ 10 ਆਸਾਨ ਸਬਕ, ਕੁਇਜ਼ ਅਤੇ ਬੱਚਤ ਕੋਚ।",
        grievanceName: "ਸ਼ਿਕਾਇਤ ਤੇ ਕਾਨੂੰਨੀ ਨੋਟਿਸ ਸਹਾਇਕ",
        grievanceDesc: "ਰੁਕੀ ਤਨਖਾਹ ਜਾਂ PF ਲਈ ਕਾਨੂੰਨੀ ਨੋਟਿਸ ਤਿਆਰ ਕਰੋ ਅਤੇ ਹੈਲਪਲਾਈਨ ਨੰਬਰ ਪ੍ਰਾਪਤ ਕਰੋ।",
        adminRulesName: "ਨਿਯਮ ਤੇ ਡਾਟਾ ਸੰਪਾਦਕ",
        adminRulesDesc: "ਐਡਮਿਨ ਸਕ੍ਰੀਨ: ਘੱਟੋ-ਘੱਟ ਮਜ਼ਦੂਰੀ ਦਰਾਂ ਅਤੇ ਸਮਾਜਿਕ ਸੁਰੱਖਿਆ ਸੀਮਾਵਾਂ ਅੱਪਡੇਟ ਕਰੋ।",

        state: "ਰਾਜ / ਖੇਤਰ",
        skillLevel: "ਹੁਨਰ ਪੱਧਰ",
        unskilled: "ਅਣਸਿੱਖਿਅਤ (Unskilled)",
        semiSkilled: "ਅੱਧ-ਸਿੱਖਿਅਤ (Semi-Skilled)",
        skilled: "ਸਿੱਖਿਅਤ (Skilled)",
        highlySkilled: "ਮਾਹਰ (Highly Skilled)",
        payType: "ਭੁਗਤਾਨ ਦੀ ਕਿਸਮ",
        monthly: "ਮਹੀਨਾਵਾਰ ਤਨਖਾਹ",
        daily: "ਦਿਹਾੜੀ",
        amountPaid: "ਮਿਲੀ ਤਨਖਾਹ (₹)",
        hoursPerDay: "ਰੋਜ਼ਾਨਾ ਕੰਮ ਦੇ ਘੰਟੇ",
        daysPerWeek: "ਹਫ਼ਤੇ ਵਿੱਚ ਕੰਮ ਦੇ ਦਿਨ",
        overtimeHours: "ਮਹੀਨੇ ਵਿੱਚ ਓਵਰਟਾਈਮ ਘੰਟੇ",
        payDate: "ਤਨਖਾਹ ਮਿਲਣ ਦੀ ਮਿਤੀ",
        statutoryMinWage: "ਕਾਨੂੰਨੀ ਘੱਟੋ-ਘੱਟ ਮਜ਼ਦੂਰੀ",
        overtimeDue: "ਬਕਾਇਆ ਓਵਰਟਾਈਮ (ਦੁੱਗਣੀ ਦਰ)",
        shortfallLabel: "ਮਹੀਨਾਵਾਰ ਕਮੀ (ਰੁਪਏ)",
        verdictGreen: "ਫੈਸਲਾ: ਹਰਾ (GREEN) — ਤਨਖਾਹ ਕਾਨੂੰਨ ਅਨੁਸਾਰ ਬਿਲਕੁਲ ਸਹੀ ਹੈ",
        verdictAmber: "ਫੈਸਲਾ: ਪੀਲਾ (AMBER) — ਘੱਟੋ-ਘੱਟ ਮਜ਼ਦੂਰੀ ਮਿਲੀ ਹੈ, ਪਰ ਓਵਰਟਾਈਮ ਜਾਂ ਦੇਰੀ ਦਾ ਮਸਲਾ ਹੈ",
        verdictRed: "ਫੈਸਲਾ: ਲਾਲ (RED) — ਤਨਖਾਹ ਕਾਨੂੰਨੀ ਘੱਟੋ-ਘੱਟ ਹੱਦ ਤੋਂ ਘੱਟ ਹੈ!",
        msgToBossTitle: "ਮਾਲਕ ਨੂੰ ਦਿਖਾਉਣ / ਭੇਜਣ ਲਈ ਸੁਨੇਹਾ",

        helpersList: "ਤੁਹਾਡੇ ਘਰੇਲੂ ਅਤੇ ਦੁਕਾਨ ਦੇ ਸਹਾਇਕ",
        addHelper: "+ ਨਵਾਂ ਸਹਾਇਕ ਜੋੜੋ",
        helperName: "ਸਹਾਇਕ ਦਾ ਨਾਮ",
        helperRole: "ਕੰਮ (ਸਫ਼ਾਈ, ਰਸੋਈਆ, ਡਰਾਈਵਰ, ਮਜ਼ਦੂਰ)",
        helperPhone: "ਵਟਸਐਪ ਫ਼ੋਨ ਨੰਬਰ",
        agreedWage: "ਤੈਅ ਤਨਖਾਹ (₹)",
        todayAttendance: "ਅੱਜ ਦੀ ਹਾਜ਼ਰੀ",
        present: "ਹਾਜ਼ਰ",
        absent: "ਗ਼ੈਰ-ਹਾਜ਼ਰ",
        halfDay: "ਅੱਧਾ ਦਿਨ",
        paidLeave: "ਛੁੱਟੀ (ਤਨਖਾਹ ਸਮੇਤ)",
        advancesTaken: "ਲਿਆ ਗਿਆ ਐਡਵਾਂਸ (₹)",
        addAdvance: "+ ਐਡਵਾਂਸ ਦਰਜ ਕਰੋ",
        bonusGift: "ਤਿਉਹਾਰ ਤੋਹਫ਼ਾ / ਬੋਨਸ (₹)",
        netToPay: "ਕੁੱਲ ਦੇਣਯੋਗ ਤਨਖਾਹ",
        generatePayslip: "📄 ਤਨਖਾਹ ਸਲਿੱਪ ਬਣਾਓ",
        incomeProofCert: "📜 ਕਰਜ਼ੇ ਲਈ ਆਮਦਨ ਸਰਟੀਫਿਕੇਟ",

        yearsInJob: "ਇਸ ਨੌਕਰੀ ਵਿੱਚ ਕੁੱਲ ਸਾਲ",
        numEmployees: "ਕੰਪਨੀ ਵਿੱਚ ਕੁੱਲ ਕਾਮੇ",
        gender: "ਲਿੰਗ",
        male: "ਮਰਦ",
        female: "ਔਰਤ",
        other: "ਹੋਰ",

        loanAmount: "ਮਿਲਿਆ ਕਰਜ਼ਾ (₹)",
        instalmentAmount: "ਕਿਸ਼ਤ ਦੀ ਰਕਮ (₹)",
        instalmentFreq: "ਕਿਸ਼ਤ ਦੀ ਮਿਆਦ",
        numInstalments: "ਕੁੱਲ ਕਿਸ਼ਤਾਂ ਦੀ ਗਿਣਤੀ",
        procFees: "ਪਹਿਲਾਂ ਕੱਟੀ ਫੀਸ (₹)",
        trueApr: "ਅਸਲ ਸਾਲਾਨਾ ਵਿਆਜ ਦਰ (APR %)",
        totalRepaid: "ਕੁੱਲ ਵਾਪਸ ਕੀਤੀ ਰਕਮ (₹)",
        extraPaid: "ਕੁੱਲ ਵਾਧੂ ਵਿਆਜ ਤੇ ਫੀਸ (₹)",
        bankComparison: "ਸਰਕਾਰੀ ਬੈਂਕ ਕਰਜ਼ੇ ਨਾਲ ਤੁਲਨਾ (11% ਸਾਲਾਨਾ)",
        loanFair: "ਵਾਜਬ ਕਰਜ਼ਾ: ਵਿਆਜ ਦਰ ਬੈਂਕ ਨਿਯਮਾਂ ਅਨੁਸਾਰ ਠੀਕ ਹੈ।",
        loanHigh: "ਮਹਿੰਗਾ ਕਰਜ਼ਾ: ਵਿਆਜ ਦਰ ਕਾਫ਼ੀ ਜ਼ਿਆਦਾ ਹੈ। ਧਿਆਨ ਨਾਲ ਫੈਸਲਾ ਲਓ।",
        loanTrap: "ਖ਼ਤਰਨਾਕ ਕਰਜ਼ੇ ਦਾ ਜਾਲ! ਸਾਲਾਨਾ ਵਿਆਜ 36% ਤੋਂ ਵੱਧ ਹੈ!",

        surveyTitle: "ਮਹੀਨਾਵਾਰ ਕੰਮਕਾਜੀ ਮਾਹੌਲ ਸਰਵੇਖਣ",
        anonNotice: "ਤੁਹਾਡੇ ਜਵਾਬ 100% ਗੁਪਤ ਹਨ। ਜਦੋਂ ਤੱਕ 5 ਸਾਥੀ ਜਵਾਬ ਨਹੀਂ ਦਿੰਦੇ, ਕੋਈ ਨਤੀਜਾ ਨਹੀਂ ਦਿਸੇਗਾ।",
        submitVote: "ਗੁਪਤ ਜਵਾਬ ਦਰਜ ਕਰੋ",
        activeSurveys: "ਚੱਲ ਰਹੇ ਸਰਵੇਖਣ ਅਤੇ ਸਕੋਰ",
        createSurvey: "+ ਨਵਾਂ ਮਹੀਨਾਵਾਰ ਸਰਵੇਖਣ ਬਣਾਓ",
        lockedSurvey: "🔒 ਗੁਪਤਤਾ ਸੁਰੱਖਿਆ ਚਾਲੂ: 5 ਜਵਾਬ ਪੂਰੇ ਹੋਣ ਤੋਂ ਬਾਅਦ ਹੀ ਔਸਤ ਸਕੋਰ ਖੁੱਲ੍ਹੇਗਾ।",
        unlockedSurvey: "ਟੀਮ ਦਾ ਔਸਤ ਸਕੋਰ (1 ਤੋਂ 5 ਸਿਤਾਰੇ)",

        issueType: "ਮਸਲੇ ਦੀ ਚੋਣ ਕਰੋ",
        unpaidSalary: "ਤਨਖਾਹ ਨਹੀਂ ਮਿਲੀ ਜਾਂ ਦੇਰੀ ਹੋਈ",
        illegalTerm: "ਬਿਨਾਂ ਨੋਟਿਸ ਕੰਮ ਤੋਂ ਹਟਾਇਆ",
        pfFraud: "ਤਨਖਾਹ ਵਿੱਚੋਂ PF ਕੱਟਿਆ ਪਰ ਜਮ੍ਹਾ ਨਹੀਂ ਕੀਤਾ",
        harassment: "ਕੰਮ ਵਾਲੀ ਥਾਂ 'ਤੇ ਤੰਗ-ਪ੍ਰੇਸ਼ਾਨ ਕਰਨਾ",
        deniedMaternity: "ਜਣੇਪਾ ਛੁੱਟੀ ਦੇਣ ਤੋਂ ਇਨਕਾਰ",
        workerName: "ਤੁਹਾਡਾ ਪੂਰਾ ਨਾਮ",
        employerName: "ਮਾਲਕ / ਕੰਪਨੀ ਦਾ ਨਾਮ",
        workplaceAddr: "ਕੰਮ ਵਾਲੀ ਥਾਂ ਦਾ ਪਤਾ",
        joiningDate: "ਕੰਮ ਸ਼ੁਰੂ ਕਰਨ ਦੀ ਮਿਤੀ",
        unpaidAmount: "ਬਕਾਇਆ ਰਕਮ ਦਾ ਦਾਅਵਾ (₹)",
        generateNotice: "📝 ਕਾਨੂੰਨੀ ਮੰਗ ਪੱਤਰ ਤਿਆਰ ਕਰੋ",
        helplineTitle: "ਸਰਕਾਰੀ ਹੈਲਪਲਾਈਨ ਅਤੇ ਪੋਰਟਲ",
        proofToKeep: "ਸਾਂਭ ਕੇ ਰੱਖਣ ਵਾਲੇ ਜ਼ਰੂਰੀ ਸਬੂਤ"
      },

      ur: {
        welfareTitle: "مزدور اور کارکنان کے حقوق و بہبود کا مرکز",
        welfareSubtitle: "ہندوستانی مزدوروں، گھریلو ملازمین اور چھوٹے دکانداروں کے لیے قانونی کم از کم اجرت، سرکاری اسکیمیں اور سماجی تحفظ۔",
        lastUpdatedPrefix: "قواعد کی آخری تجدید:",
        sourcePrefix: "ماخذ:",
        disclaimer: "براہ کرم سرکاری ماخذ یا لیبر آفیسر سے تصدیق ضرور کریں۔",
        readAloud: "🔊 پڑھ کر سنائیں",
        copyText: "📋 نتیجہ کاپی کریں",
        copied: "✓ کاپی ہو گیا!",
        shareWhatsApp: "💬 واٹس ایپ پر شیئر کریں",
        saveResult: "💾 محفوظ کریں",
        savedSuccess: "✓ آپ کی ڈیوائس پر کامیابی سے محفوظ ہو گیا!",
        speakMic: "🎤 بول کر درج کریں",
        whatToDoNext: "آگے کیا قدم اٹھائیں؟",
        numbersUsed: "استعمال شدہ اصول اور اعداد و شمار",
        calcButton: "ابھی حساب لگائیں",
        backToHub: "← بہبود مرکز پر واپس جائیں",
        openTool: "ٹول کھولیں ➔",
        speechNotSupported: "اس براؤزر میں بولنے کی سہولت دستیاب نہیں ہے۔ براہ کرم ٹائپ کریں۔",
        ttsNotSupported: "اس ڈیوائس پر آواز میں پڑھنے کی سہولت میسر نہیں ہے۔",

        fairPayName: "منصفانہ اجرت چیکر (Fair-Pay)",
        fairPayDesc: "چیک کریں کہ کیا تنخواہ سرکاری کم از کم اجرت، دگنے اوور ٹائم اور چھٹی کے قوانین کے مطابق ہے۔",
        ledgerName: "گھریلو و یومیہ ملازمین کا بہی کھاتہ",
        ledgerDesc: "خادمہ، باورچی اور ڈرائیور کی حاضری، پیشگی رقم اور عیدی/بونس کا حساب۔ واٹس ایپ پر سلپ بھیجیں۔",
        benefitsName: "حقوق و فوائد تلاش کنندہ (Benefits)",
        benefitsDesc: "5 آسان سوالات کے جواب دیں اور جانیں کہ کیا آپ کو پی ایف، ای ایس آئی، گریجویٹی اور بونس ملنا چاہیے۔",
        schemesName: "سرکاری اسکیموں کا ملاپ (Schemes)",
        schemesDesc: "ای-شرم، پردھان منتری پنشن، آیوشمان بھارت، جن دھن اور بیمہ اسکیموں سے فوری فائدہ اٹھائیں۔",
        loanTrapName: "قرض کے جال کی پہچان (Loan Trap)",
        loanTrapDesc: "روزانہ یا اقساط والے قرض کا اصل سالانہ سود (APR) معلوم کریں اور سود خوروں سے بچیں۔",
        womenFamilyName: "خواتین اور خاندانی تحفظ",
        womenFamilyDesc: "26 ہفتوں کی با اجرت زچگی کی چھٹی کا منصوبہ، محفوظ نائٹ شفٹ اور مساوی تنخواہ چیکر۔",
        pulseName: "کام کے ماحول کا سروے (خفیہ)",
        pulseDesc: "6 سوالات کا ماہانہ سروے مکمل رازداری کے ساتھ۔ 5 سے کم جوابات پر مالک کو کچھ نظر نہیں آئے گا۔",
        gigIncomeName: "ڈیلیوری و فری لانس آمدنی معاون",
        gigIncomeDesc: "سوئیگی، زوماٹو، اوبر کی کمائی اور اخراجات کا حساب۔ ٹیکس چھوٹ اور قرض کے لیے آمدنی کا سرٹیفکیٹ۔",
        savingsCoachName: "مالی اسباق اور بچت کوچ",
        savingsCoachDesc: "ہنگامی فنڈ، یو پی آئی فراڈ سے بچاؤ کے 10 آسان اسباق، کوئز اور بچت کے مشورے۔",
        grievanceName: "شکایات اور قانونی نوٹس معاون",
        grievanceDesc: "باقی تنخواہ یا پی ایف کے غبن کے خلاف قانونی نوٹس تیار کریں اور سرکاری ہیلپ لائن نمبر حاصل کریں۔",
        adminRulesName: "قواعد و ڈیٹا ایڈیٹر",
        adminRulesDesc: "ایڈمن اسکرین: کم از کم اجرت کی شرحیں اور سماجی تحفظ کی حدود اپ ڈیٹ کریں۔",

        state: "ریاست / علاقہ",
        skillLevel: "مہارت کی سطح",
        unskilled: "غیر ہنر مند (Unskilled)",
        semiSkilled: "نیم ہنر مند (Semi-Skilled)",
        skilled: "ہنر مند (Skilled)",
        highlySkilled: "اعلی ہنر مند (Highly Skilled)",
        payType: "ادائیگی کی قسم",
        monthly: "ماہانہ تنخواہ",
        daily: "روزانہ اجرت",
        amountPaid: "موصولہ رقم (₹)",
        hoursPerDay: "روزانہ کام کے گھنٹے",
        daysPerWeek: "ہفتے میں کام کے دن",
        overtimeHours: "مہینے میں اوور ٹائم کے گھنٹے",
        payDate: "تنخواہ ملنے کی تاریخ",
        statutoryMinWage: "قانونی کم از کم اجرت",
        overtimeDue: "واجب الادا اوور ٹائم (دگنی شرح)",
        shortfallLabel: "ماہانہ کمی (روپوں میں)",
        verdictGreen: "فیصلہ: سبز (GREEN) — تنخواہ قانون کے مطابق منصفانہ ہے",
        verdictAmber: "فیصلہ: پیلا (AMBER) — کم از کم اجرت تو ملی لیکن اوور ٹائم یا تاخیر کا مسئلہ ہے",
        verdictRed: "فیصلہ: سرخ (RED) — تنخواہ قانونی کم از کم حد سے کم ہے!",
        msgToBossTitle: "مالک کو دکھانے / بھیجنے کے لیے شائستہ پیغام",

        helpersList: "آپ کے گھریلو اور دکان کے ملازمین",
        addHelper: "+ نیا ملازم شامل کریں",
        helperName: "ملازم کا نام",
        helperRole: "کام (صفائی، باورچی، ڈرائیور، مزدور)",
        helperPhone: "واٹس ایپ موبائل نمبر",
        agreedWage: "طے شدہ تنخواہ (₹)",
        todayAttendance: "آج کی حاضری",
        present: "حاضر",
        absent: "غیر حاضر",
        halfDay: "نصف دن",
        paidLeave: "با اجرت چھٹی",
        advancesTaken: "لی گئی پیشگی رقم (₹)",
        addAdvance: "+ پیشگی رقم درج کریں",
        bonusGift: "عیدی / تہوار کا بونس (₹)",
        netToPay: "کل واجب الادا رقم",
        generatePayslip: "📄 تنخواہ کی سلپ بنائیں",
        incomeProofCert: "📜 قرض کے لیے آمدنی کا سرٹیفکیٹ",

        yearsInJob: "اس ملازمت میں کل سال",
        numEmployees: "کمپنی میں کل ملازمین",
        gender: "جنس",
        male: "مرد",
        female: "عورت",
        other: "دیگر",

        loanAmount: "موصول شدہ قرض کی رقم (₹)",
        instalmentAmount: "قسط کی رقم (₹)",
        instalmentFreq: "قسط کی میعاد",
        numInstalments: "کل اقساط کی تعداد",
        procFees: "پہلے کٹوتی کی گئی فیس (₹)",
        trueApr: "اصل سالانہ شرح سود (APR %)",
        totalRepaid: "کل واپس کی گئی رقم (₹)",
        extraPaid: "کل اضافی سود اور فیس (₹)",
        bankComparison: "سرکاری بینک قرض سے موازنہ (11% سالانہ)",
        loanFair: "منصفانہ قرض: شرح سود بینک کے قواعد کے مطابق ہے۔",
        loanHigh: "مہنگا قرض: شرح سود کافی زیادہ ہے۔ سوچ سمجھ کر فیصلہ لیں۔",
        loanTrap: "خطرناک قرض کا جال! سالانہ سود 36 فیصد سے زیادہ ہے!",

        surveyTitle: "ماہانہ کام کی جگہ کی عزت اور ماحول کا سروے",
        anonNotice: "آپ کے جوابات 100 فیصد خفیہ ہیں۔ جب تک کم از کم 5 ساتھی جواب نہیں دیں گے، کوئی اوسط نتیجہ ظاہر نہیں ہوگا۔",
        submitVote: "خفیہ جواب جمع کریں",
        activeSurveys: "جاری سروے اور ٹیم کے اسکور",
        createSurvey: "+ نیا ماہانہ سروے بنائیں",
        lockedSurvey: "🔒 رازداری کا تحفظ فعال: 5 جوابات مکمل ہونے کے بعد ہی اوسط اسکور ظاہر ہوگا۔",
        unlockedSurvey: "ٹیم کا اوسط اسکور (1 تا 5 ستارے)",

        issueType: "مسئلے کا انتخاب کریں",
        unpaidSalary: "تنخواہ نہیں ملی یا تاخیر ہوئی",
        illegalTerm: "بغیر نوٹس نوکری سے برطرف کیا",
        pfFraud: "تنخواہ سے پی ایف کاٹا مگر جمع نہیں کروایا",
        harassment: "کام کی جگہ پر ہراسانی یا غیر محفوظ ماحول",
        deniedMaternity: "زچگی کی چھٹی دینے سے انکار",
        workerName: "آپ کا پورا نام",
        employerName: "مالک / کمپنی کا نام",
        workplaceAddr: "کام کی جگہ کا پتہ",
        joiningDate: "ملازمت شروع کرنے کی تاریخ",
        unpaidAmount: "واجب الادا دعوے کی رقم (₹)",
        generateNotice: "📝 قانونی نوٹس تیار کریں",
        helplineTitle: "سرکاری ہیلپ لائن اور پورٹل",
        proofToKeep: "سنبھال کر رکھنے کے اہم ثبوت"
      }
    };

    // Translation helper
    function getT(key) {
      const l = window.currentLang || 'en';
      if (WELFARE_I18N[l] && WELFARE_I18N[l][key] !== undefined) return WELFARE_I18N[l][key];
      if (WELFARE_I18N['en'] && WELFARE_I18N['en'][key] !== undefined) return WELFARE_I18N['en'][key];
      return key;
    }

    // 2. Language Switcher (Remembers and sets RTL for Urdu)
    function changeLanguage(lang) {
      try {
        const l = String(lang || 'en').toLowerCase().trim();
        window.currentLang = l;
        localStorage.setItem('paypilot_lang', l);

        document.documentElement.lang = l;
        if (l === 'ur') {
          document.documentElement.setAttribute('dir', 'rtl');
        } else {
          document.documentElement.setAttribute('dir', 'ltr');
        }

        // Update select dropdown
        const sel = document.getElementById('lang-select');
        if (sel) sel.value = l;

        // Update pill buttons
        document.querySelectorAll('.lang-pill-btn').forEach(btn => {
          const onclickAttr = btn.getAttribute('onclick') || '';
          btn.classList.toggle('active', onclickAttr.includes(`'${l}'`) || onclickAttr.includes(`"${l}"`));
        });

        // Re-render currently active view if it's a welfare screen
        const activePane = document.querySelector('.view-pane.active');
        if (activePane && activePane.id && activePane.id.startsWith('pane-welfare-')) {
          const screenId = activePane.id.replace(/^pane-/, '');
          if (typeof window.showScreen === 'function') window.showScreen(screenId);
        }
      } catch (err) {
        console.error('Error in changeLanguage:', err);
      }
    }

    // Initialize saved language immediately on load
    document.addEventListener('DOMContentLoaded', () => {
      changeLanguage(window.currentLang);
    });

    // 3. Web Speech Recognition (Mic Input with Graceful Fallback)
    function startVoiceInput(targetInputId) {
      try {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {
          alert(getT('speechNotSupported'));
          return;
        }
        const rec = new SpeechRec();
        const langMap = { en: 'en-IN', hi: 'hi-IN', pa: 'pa-IN', ur: 'ur-PK' };
        rec.lang = langMap[window.currentLang] || 'en-IN';
        rec.interimResults = false;
        rec.maxAlternatives = 1;

        const btn = document.querySelector(`[data-mic-for="${targetInputId}"]`);
        if (btn) btn.classList.add('listening');

        rec.onresult = (evt) => {
          if (btn) btn.classList.remove('listening');
          if (evt.results && evt.results[0] && evt.results[0][0]) {
            const transcript = evt.results[0][0].transcript.trim();
            const input = document.getElementById(targetInputId);
            if (input) {
              // If input is number, try to extract digits
              if (input.type === 'number') {
                const cleaned = transcript.replace(/[^0-9.]/g, '');
                if (cleaned) input.value = cleaned;
              } else {
                input.value = transcript;
              }
              input.dispatchEvent(new Event('input', { bubbles: true }));
            }
          }
        };
        rec.onerror = (err) => {
          if (btn) btn.classList.remove('listening');
          console.warn('Speech recognition error:', err);
        };
        rec.onend = () => {
          if (btn) btn.classList.remove('listening');
        };
        rec.start();
      } catch (e) {
        console.error('Failed to start voice input:', e);
        alert(getT('speechNotSupported'));
      }
    }

    // 4. Text-To-Speech (TTS Read Aloud with Graceful Fallback)
    function readAloudText(text) {
      try {
        if (!window.speechSynthesis) {
          alert(getT('ttsNotSupported'));
          return;
        }
        window.speechSynthesis.cancel();
        const clean = String(text || '').replace(/[#*_`]/g, '').trim();
        if (!clean) return;

        const utt = new SpeechSynthesisUtterance(clean);
        const langMap = { en: 'en-IN', hi: 'hi-IN', pa: 'pa-IN', ur: 'ur' };
        utt.lang = langMap[window.currentLang] || 'en-IN';
        utt.rate = 0.95;
        window.speechSynthesis.speak(utt);
      } catch (e) {
        console.error('Speech synthesis error:', e);
        alert(getT('ttsNotSupported'));
      }
    }

    // 5. Sharing Helpers (Copy text and WhatsApp Link)
    function copyWelfareText(text, btnElement) {
      try {
        navigator.clipboard.writeText(text).then(() => {
          if (btnElement) {
            const original = btnElement.innerText;
            btnElement.innerText = getT('copied');
            setTimeout(() => { btnElement.innerText = original; }, 2000);
          }
        }).catch(() => {
          const ta = document.createElement('textarea');
          ta.value = text;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          if (btnElement) {
            btnElement.innerText = getT('copied');
            setTimeout(() => { btnElement.innerText = getT('copyText'); }, 2000);
          }
        });
      } catch (err) {
        console.error('Copy error:', err);
      }
    }

    function shareWelfareWhatsApp(text) {
      try {
        const url = 'https://wa.me/?text=' + encodeURIComponent(text);
        window.open(url, '_blank');
      } catch (e) {
        console.error('WhatsApp share error:', e);
      }
    }

    // 6. Offline Statutory Rules Table (Default dataset)
    const DEFAULT_WELFARE_RULES = {
      lastUpdated: "2026-10-01",
      source: "Ministry of Labour & Employment, Govt of India & State Labour Gazettes",
      minimumWages: {
        "Central Sphere": { unskilledDaily: 530, unskilledMonthly: 13780, semiskilledDaily: 588, semiskilledMonthly: 15288, skilledDaily: 695, skilledMonthly: 18070, highlySkilledDaily: 764, highlySkilledMonthly: 19864 },
        "Delhi": { unskilledDaily: 692, unskilledMonthly: 18000, semiskilledDaily: 762, semiskilledMonthly: 19812, skilledDaily: 839, skilledMonthly: 21814, highlySkilledDaily: 915, highlySkilledMonthly: 23790 },
        "Maharashtra": { unskilledDaily: 516, unskilledMonthly: 13416, semiskilledDaily: 562, semiskilledMonthly: 14612, skilledDaily: 620, skilledMonthly: 16120, highlySkilledDaily: 685, highlySkilledMonthly: 17810 },
        "Karnataka": { unskilledDaily: 498, unskilledMonthly: 12948, semiskilledDaily: 545, semiskilledMonthly: 14170, skilledDaily: 605, skilledMonthly: 15730, highlySkilledDaily: 670, highlySkilledMonthly: 17420 },
        "Tamil Nadu": { unskilledDaily: 475, unskilledMonthly: 12350, semiskilledDaily: 520, semiskilledMonthly: 13520, skilledDaily: 580, skilledMonthly: 15080, highlySkilledDaily: 645, highlySkilledMonthly: 16770 },
        "Uttar Pradesh": { unskilledDaily: 412, unskilledMonthly: 10712, semiskilledDaily: 453, semiskilledMonthly: 11778, skilledDaily: 508, skilledMonthly: 13208, highlySkilledDaily: 565, highlySkilledMonthly: 14690 },
        "Punjab": { unskilledDaily: 425, unskilledMonthly: 11050, semiskilledDaily: 465, semiskilledMonthly: 12090, skilledDaily: 522, skilledMonthly: 13572, highlySkilledDaily: 580, highlySkilledMonthly: 15080 },
        "West Bengal": { unskilledDaily: 390, unskilledMonthly: 10140, semiskilledDaily: 430, semiskilledMonthly: 11180, skilledDaily: 485, skilledMonthly: 12610, highlySkilledDaily: 540, highlySkilledMonthly: 14040 },
        "Gujarat": { unskilledDaily: 448, unskilledMonthly: 11648, semiskilledDaily: 465, semiskilledMonthly: 12090, skilledDaily: 484, skilledMonthly: 12584, highlySkilledDaily: 540, highlySkilledMonthly: 14040 },
        "Bihar": { unskilledDaily: 400, unskilledMonthly: 10400, semiskilledDaily: 425, semiskilledMonthly: 11050, skilledDaily: 518, skilledMonthly: 13468, highlySkilledDaily: 575, highlySkilledMonthly: 14950 },
        "Rajasthan": { unskilledDaily: 395, unskilledMonthly: 10270, semiskilledDaily: 415, semiskilledMonthly: 10790, skilledDaily: 435, skilledMonthly: 11310, highlySkilledDaily: 485, highlySkilledMonthly: 12610 },
        "Haryana": { unskilledDaily: 420, unskilledMonthly: 10920, semiskilledDaily: 460, semiskilledMonthly: 11960, skilledDaily: 510, skilledMonthly: 13260, highlySkilledDaily: 565, highlySkilledMonthly: 14690 }
      },
      benefitThresholds: {
        pfEmployeeThreshold: 20,
        pfWageLimit: 15000,
        pfEmployeeRate: 0.12,
        pfEmployerRate: 0.12,
        esiEmployeeThreshold: 10,
        esiWageLimit: 21000,
        esiEmployeeRate: 0.0075,
        esiEmployerRate: 0.0325,
        gratuityYears: 5,
        gratuityThreshold: 10,
        bonusWageLimit: 21000,
        bonusMinDays: 30,
        bonusMinRate: 0.0833,
        maternityWeeks: 26,
        maternityDaysWorked: 80,
        maxDailyHours: 9,
        overtimeMultiplier: 2.0,
        wagePaymentDeadlineDays: 7
      },
      schemes: [
        { id: "eshram", name: "e-Shram Registration", benefit: "National UAN card, ₹2 Lakh free accidental death/disability insurance, direct social security benefits.", minAge: 16, maxAge: 59, maxIncome: 50000, gender: "all", occupation: "unorganized", documents: "Aadhaar Card, Mobile linked with Aadhaar, Bank Account Passbook", url: "eshram.gov.in" },
        { id: "pmsym", name: "PM Shram Yogi Maan-dhan (PM-SYM)", benefit: "Assured pension of ₹3,000/month after age 60. 50% govt co-contribution.", minAge: 18, maxAge: 40, maxIncome: 15000, gender: "all", occupation: "unorganized", documents: "Aadhaar Card, Jan Dhan / Savings Bank Passbook", url: "maandhan.in" },
        { id: "apy", name: "Atal Pension Yojana (APY)", benefit: "Guaranteed monthly pension of ₹1,000 to ₹5,000 for lifelong post-retirement security.", minAge: 18, maxAge: 40, maxIncome: 100000, gender: "all", occupation: "all", documents: "Bank Account, Aadhaar Card, Nominee Details", url: "npscra.nsdl.co.in" },
        { id: "pmjay", name: "Ayushman Bharat (PM-JAY)", benefit: "Free secondary & tertiary hospital treatment up to ₹5,00,000 per family per year across 27,000+ empaneled hospitals.", minAge: 0, maxAge: 100, maxIncome: 25000, gender: "all", occupation: "all", documents: "Ration Card (BPL/Antyodaya), Aadhaar Card", url: "pmjay.gov.in" },
        { id: "pmjdy", name: "PM Jan Dhan Yojana (PMJDY)", benefit: "Zero-balance bank account, RuPay debit card, ₹2 Lakh accidental insurance, ₹10,000 overdraft facility.", minAge: 10, maxAge: 100, maxIncome: 100000, gender: "all", occupation: "all", documents: "Aadhaar Card or Voter ID / MGNREGA Job Card", url: "pmjdy.gov.in" },
        { id: "mudra", name: "PM Mudra Yojana (Micro-Loans)", benefit: "Collateral-free micro-business loans: Shishu (up to ₹50k), Kishore (₹50k-₹5L), Tarun (₹5L-₹10L) with lowest interest.", minAge: 18, maxAge: 65, maxIncome: 200000, gender: "all", occupation: "small-business", documents: "Identity Proof, Business Address Proof, Quotation/Machinery Estimate", url: "mudra.org.in" },
        { id: "pmsby", name: "PM Suraksha Bima Yojana (PMSBY)", benefit: "Accidental death / permanent disability insurance of ₹2,00,000 for just ₹20 per year.", minAge: 18, maxAge: 70, maxIncome: 1000000, gender: "all", occupation: "all", documents: "Savings Bank Account, Auto-debit Consent Form", url: "jansuraksha.gov.in" },
        { id: "pmjjby", name: "PM Jeevan Jyoti Bima Yojana (PMJJBY)", benefit: "Life insurance cover of ₹2,00,000 for death due to any cause at ₹436 per year.", minAge: 18, maxAge: 50, maxIncome: 1000000, gender: "all", occupation: "all", documents: "Savings Bank Account, Consent Form", url: "jansuraksha.gov.in" },
        { id: "pmsvanidhi", name: "PM SVANidhi (Street Vendors)", benefit: "Working capital micro-loan of ₹10,000 / ₹20,000 / ₹50,000 with 7% interest subsidy & cashback.", minAge: 18, maxAge: 65, maxIncome: 30000, gender: "all", occupation: "street-vendor", documents: "Vending Certificate / Urban Local Body ID, Aadhaar Card", url: "pmsvanidhi.mohua.gov.in" }
      ]
    };

    // Client memory rules (Loads from server if online, otherwise uses offline fallback)
    window.welfareRules = JSON.parse(JSON.stringify(DEFAULT_WELFARE_RULES));

    function syncWelfareRulesFromServer() {
      fetch('/api/welfare/rules')
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data && data.minimumWages) {
            window.welfareRules = data;
          }
        })
        .catch(() => {
          // Offline mode: continue with DEFAULT_WELFARE_RULES
        });
    }
    syncWelfareRulesFromServer();

    function getLegalAttributionHtml() {
      const r = window.welfareRules || DEFAULT_WELFARE_RULES;
      const date = escapeHtml(r.lastUpdated || "2026-10-01");
      const src = escapeHtml(r.source || "Ministry of Labour & Employment");
      return `
        <div class="welfare-legal-notice">
          ℹ️ <strong>${getT('lastUpdatedPrefix')}</strong> ${date} • <strong>${getT('sourcePrefix')}</strong> ${src}.<br>
          ${getT('disclaimer')}
        </div>
      `;
    }
''')

print("Welfare base module written successfully.")
