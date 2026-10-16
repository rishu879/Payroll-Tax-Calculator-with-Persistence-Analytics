
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

    // =========================================================================
    // 7. WELFARE HUB OVERVIEW SCREEN (10 BIG ACTION CARDS)
    // =========================================================================
    function renderWelfareHub(pane) {
      if (!pane) return;
      const r = window.welfareRules || DEFAULT_WELFARE_RULES;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
              <span class="welfare-badge-pill" style="background: rgba(244, 201, 93, 0.2); color: var(--cinema-gold); border: 1px solid var(--cinema-gold); margin-bottom: 8px;">
                🏛️ ${getT('welfareTitle')}
              </span>
              <h2 style="color: var(--cinema-cream); margin-top: 6px; font-family: var(--font-headline); letter-spacing: 0.5px;">
                ${getT('welfareTitle')}
              </h2>
              <p style="color: var(--cinema-muted); font-size: 15px; max-width: 800px; margin-top: 4px;">
                ${getT('welfareSubtitle')}
              </p>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
              <button class="btn-read-aloud" onclick="readAloudText('${getT('welfareTitle')}. ${getT('welfareSubtitle')}')">
                ${getT('readAloud')}
              </button>
            </div>
          </div>
        </div>

        <!-- 10 Big Cards Grid -->
        <div class="welfare-card-grid">
          <!-- 1. Fair-Pay Checker -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-fair-pay')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">⚖️</div>
              <h3 style="color: var(--cinema-orange); margin-bottom: 8px;">1. ${getT('fairPayName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('fairPayDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-orange welfare-big-btn" style="width: 100%;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 2. Domestic & Daily Ledger -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-ledger')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">📒</div>
              <h3 style="color: var(--cinema-teal); margin-bottom: 8px;">2. ${getT('ledgerName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('ledgerDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-teal welfare-big-btn" style="width: 100%;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 3. Benefits Finder -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-benefits')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">🎁</div>
              <h3 style="color: var(--cinema-gold); margin-bottom: 8px;">3. ${getT('benefitsName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('benefitsDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-gold welfare-big-btn" style="width: 100%; color:#000;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 4. Scheme Matcher -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-schemes')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">📜</div>
              <h3 style="color: var(--cinema-emerald); margin-bottom: 8px;">4. ${getT('schemesName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('schemesDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-teal welfare-big-btn" style="width: 100%; background: var(--cinema-emerald); border-color: var(--cinema-emerald); color:#000;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 5. Loan Trap Detector -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-loan-trap')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">🪤</div>
              <h3 style="color: var(--cinema-crimson); margin-bottom: 8px;">5. ${getT('loanTrapName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('loanTrapDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-glass welfare-big-btn" style="width: 100%; border-color: var(--cinema-crimson); color: var(--cinema-crimson);">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 6. Women & Family Support -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-women-family')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">🌸</div>
              <h3 style="color: #F472B6; margin-bottom: 8px;">6. ${getT('womenFamilyName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('womenFamilyDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-glass welfare-big-btn" style="width: 100%; border-color: #F472B6; color: #F472B6;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 7. Work-Culture Pulse -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-pulse')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">💓</div>
              <h3 style="color: var(--cinema-teal); margin-bottom: 8px;">7. ${getT('pulseName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('pulseDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-teal welfare-big-btn" style="width: 100%;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 8. Gig & Freelancer Income -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-gig-income')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">🛵</div>
              <h3 style="color: var(--cinema-orange); margin-bottom: 8px;">8. ${getT('gigIncomeName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('gigIncomeDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-orange welfare-big-btn" style="width: 100%;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 9. Money Lessons & Savings Coach -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-savings-coach')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">💡</div>
              <h3 style="color: var(--cinema-gold); margin-bottom: 8px;">9. ${getT('savingsCoachName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('savingsCoachDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-gold welfare-big-btn" style="width: 100%; color:#000;">${getT('openTool')}</button>
            </div>
          </div>

          <!-- 10. Grievance Helper -->
          <div class="welfare-hub-tile" onclick="showScreen('welfare-grievance')">
            <div>
              <div style="font-size: 36px; margin-bottom: 12px;">📢</div>
              <h3 style="color: var(--cinema-cream); margin-bottom: 8px;">10. ${getT('grievanceName')}</h3>
              <p style="color: var(--cinema-muted); font-size: 14px; line-height: 1.6;">${getT('grievanceDesc')}</p>
            </div>
            <div style="margin-top: 16px;">
              <button class="btn btn-glass welfare-big-btn" style="width: 100%;">${getT('openTool')}</button>
            </div>
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;
    }

    // =========================================================================
    // 8. SCREEN 1: FAIR-PAY CHECKER
    // =========================================================================
    function renderFairPay(pane) {
      if (!pane) return;
      const r = window.welfareRules || DEFAULT_WELFARE_RULES;
      const states = Object.keys(r.minimumWages || DEFAULT_WELFARE_RULES.minimumWages);

      let stateOptions = states.map(st => `<option value="${st}" ${st === 'Delhi' ? 'selected' : ''}>${st}</option>`).join('');

      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-orange);">⚖️ ${getT('fairPayName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">${getT('fairPayDesc')}</p>
            </div>
            <button class="btn-read-aloud" id="btn-read-fairpay">${getT('readAloud')}</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- Input Card -->
          <div class="card">
            <h3 style="color: var(--cinema-orange); margin-bottom: 16px;">1. Enter Work &amp; Pay Details</h3>
            
            <div class="form-group">
              <label class="form-label">${getT('state')}</label>
              <select class="form-control" id="fp-state" onchange="calculateFairPay()">${stateOptions}</select>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">${getT('skillLevel')}</label>
                <select class="form-control" id="fp-skill" onchange="calculateFairPay()">
                  <option value="unskilled">${getT('unskilled')}</option>
                  <option value="semiskilled">${getT('semiSkilled')}</option>
                  <option value="skilled" selected>${getT('skilled')}</option>
                  <option value="highlySkilled">${getT('highlySkilled')}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">${getT('payType')}</label>
                <select class="form-control" id="fp-pay-type" onchange="calculateFairPay()">
                  <option value="monthly" selected>${getT('monthly')}</option>
                  <option value="daily">${getT('daily')}</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <label class="form-label" style="margin:0;">${getT('amountPaid')}</label>
                <button type="button" class="btn-mic" data-mic-for="fp-amount" onclick="startVoiceInput('fp-amount')">🎤 ${getT('speakMic')}</button>
              </div>
              <input type="number" class="form-control font-mono" id="fp-amount" value="18000" oninput="calculateFairPay()">
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">${getT('hoursPerDay')}</label>
                <input type="number" class="form-control font-mono" id="fp-hours" value="8" min="1" max="16" oninput="calculateFairPay()">
              </div>
              <div class="form-group">
                <label class="form-label">${getT('daysPerWeek')}</label>
                <input type="number" class="form-control font-mono" id="fp-days-week" value="6" min="1" max="7" oninput="calculateFairPay()">
              </div>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">${getT('overtimeHours')}</label>
                <input type="number" class="form-control font-mono" id="fp-ot-hours" value="0" min="0" oninput="calculateFairPay()">
              </div>
              <div class="form-group">
                <label class="form-label">${getT('payDate')}</label>
                <input type="number" class="form-control font-mono" id="fp-pay-date" value="7" min="1" max="31" oninput="calculateFairPay()">
              </div>
            </div>
          </div>

          <!-- Result Output Card -->
          <div class="card card-glow-orange" id="fp-result-card">
            <!-- Rendered by calculateFairPay() -->
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;

      document.getElementById('btn-read-fairpay').onclick = () => {
        const text = document.getElementById('fp-result-speech-text')?.innerText || getT('fairPayDesc');
        readAloudText(text);
      };

      calculateFairPay();
    }

    function calculateFairPay() {
      try {
        const r = window.welfareRules || DEFAULT_WELFARE_RULES;
        const state = document.getElementById('fp-state')?.value || 'Delhi';
        const skill = document.getElementById('fp-skill')?.value || 'unskilled';
        const payType = document.getElementById('fp-pay-type')?.value || 'monthly';
        const amount = parseFloat(document.getElementById('fp-amount')?.value || 0);
        const hours = parseFloat(document.getElementById('fp-hours')?.value || 8);
        const daysPerWeek = parseFloat(document.getElementById('fp-days-week')?.value || 6);
        const otHours = parseFloat(document.getElementById('fp-ot-hours')?.value || 0);
        const payDate = parseFloat(document.getElementById('fp-pay-date')?.value || 7);

        const stateWages = (r.minimumWages && r.minimumWages[state]) || DEFAULT_WELFARE_RULES.minimumWages['Delhi'];
        
        let minMonthly = 0, minDaily = 0;
        if (skill === 'unskilled') { minMonthly = stateWages.unskilledMonthly; minDaily = stateWages.unskilledDaily; }
        else if (skill === 'semiskilled') { minMonthly = stateWages.semiskilledMonthly; minDaily = stateWages.semiskilledDaily; }
        else if (skill === 'skilled') { minMonthly = stateWages.skilledMonthly; minDaily = stateWages.skilledDaily; }
        else { minMonthly = stateWages.highlySkilledMonthly; minDaily = stateWages.highlySkilledDaily; }

        const baseStatutoryWage = payType === 'monthly' ? minMonthly : (minDaily * 26);
        const dailyRate = minDaily > 0 ? minDaily : (minMonthly / 26);
        const hourlyRate = dailyRate / 8;
        const otDue = Math.round(otHours * hourlyRate * 2.0); // Double rate under Indian Labour Act
        const totalStatutoryDue = Math.round(baseStatutoryWage + otDue);

        const shortfall = Math.max(0, totalStatutoryDue - amount);

        let verdict = 'green', verdictClass = 'welfare-verdict-green', verdictTitle = getT('verdictGreen');
        if (amount < baseStatutoryWage) {
          verdict = 'red';
          verdictClass = 'welfare-verdict-red';
          verdictTitle = getT('verdictRed');
        } else if (shortfall > 0 || payDate > 10 || daysPerWeek > 6) {
          verdict = 'amber';
          verdictClass = 'welfare-verdict-amber';
          verdictTitle = getT('verdictAmber');
        }

        // Ready message for boss
        const bossMessage = `Namaste ji, As per the official minimum wage notification for ${state} (${skill} category), the statutory minimum wage is ₹${baseStatutoryWage.toLocaleString('en-IN')}/month. With ${otHours} hours of overtime at statutory double-rate (₹${otDue.toLocaleString('en-IN')}), the total due is ₹${totalStatutoryDue.toLocaleString('en-IN')}. My current wage is ₹${amount.toLocaleString('en-IN')}. Please adjust the difference of ₹${shortfall.toLocaleString('en-IN')} as per labour department rules. Thank you.`;

        const speechSummary = `${verdictTitle}. Statutory minimum wage for ${state} is ₹${baseStatutoryWage}. Total due including overtime is ₹${totalStatutoryDue}. You received ₹${amount}. Shortfall is ₹${shortfall}.`;

        const outCard = document.getElementById('fp-result-card');
        if (!outCard) return;

        outCard.innerHTML = `
          <div id="fp-result-speech-text" style="display:none;">${escapeHtml(speechSummary)}</div>
          
          <div class="welfare-verdict-box ${verdictClass}">
            <h3 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 800;">${verdictTitle}</h3>
            <div style="font-size: 28px; font-weight: 800; font-family: var(--font-mono); margin: 6px 0;">
              ${shortfall > 0 ? `Shortfall: -₹${shortfall.toLocaleString('en-IN')}` : `Fair Pay ✓ No Shortfall`}
            </div>
            <div style="font-size: 13px; opacity: 0.9;">
              ${payDate > 10 ? `⚠️ Late payment: Wages paid on day ${payDate} (Law requires payment by 7th or 10th of month).` : ''}
              ${daysPerWeek > 6 ? `⚠️ Missing weekly rest day: Working 7 days/week without paid holiday violates the Minimum Wages Act.` : ''}
            </div>
          </div>

          <h4 style="color: var(--cinema-cream); margin: 16px 0 10px 0;">${getT('numbersUsed')}</h4>
          <div class="table-container" style="margin-bottom: 16px;">
            <table>
              <tr><td>State &amp; Category:</td><td class="font-mono"><strong>${state} (${skill})</strong></td></tr>
              <tr><td>Base Minimum Wage:</td><td class="font-mono">₹${baseStatutoryWage.toLocaleString('en-IN')} / mo</td></tr>
              <tr><td>Overtime Due (${otHours} hrs @ 2x rate):</td><td class="font-mono">₹${otDue.toLocaleString('en-IN')}</td></tr>
              <tr><td>Total Statutory Amount Due:</td><td class="font-mono" style="color:var(--cinema-gold);">₹${totalStatutoryDue.toLocaleString('en-IN')}</td></tr>
              <tr><td>Actual Amount Paid:</td><td class="font-mono">₹${amount.toLocaleString('en-IN')}</td></tr>
              <tr><td>Net Monthly Shortfall:</td><td class="font-mono" style="color:${shortfall > 0 ? 'var(--cinema-crimson)' : 'var(--cinema-emerald)'}; font-weight:700;">₹${shortfall.toLocaleString('en-IN')}</td></tr>
            </table>
          </div>

          <h4 style="color: var(--cinema-teal); margin-bottom: 8px;">${getT('whatToDoNext')}</h4>
          <div class="welfare-step-box">
            ${shortfall > 0 
              ? `1. Show the calculation and polite message below to your employer.<br>2. Keep bank passbook or cash receipts as proof of payment.<br>3. If unresolved, call the National Labour Helpline at <strong>14434</strong> or submit on SAMADHAAN portal.`
              : `1. Your wage meets the statutory minimum wage standards.<br>2. Ensure regular PF (12%) and ESI contributions are deposited in your UAN account.<br>3. Request a signed salary slip each month.`}
          </div>

          <div style="margin-top: 16px;">
            <label class="form-label" style="color: var(--cinema-gold);">${getT('msgToBossTitle')}</label>
            <textarea class="form-control" id="fp-boss-msg" rows="3" style="font-size: 12px; margin-bottom: 12px;" readonly>${bossMessage}</textarea>
            
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
              <button class="btn btn-teal" onclick="copyWelfareText(document.getElementById('fp-boss-msg').value, this)">
                ${getT('copyText')}
              </button>
              <button class="btn btn-orange" onclick="shareWelfareWhatsApp(document.getElementById('fp-boss-msg').value)">
                ${getT('shareWhatsApp')}
              </button>
            </div>
          </div>
        `;
      } catch (err) {
        console.error('Fair-Pay calculation error:', err);
      }
    }

    // =========================================================================
    // 9. SCREEN 2: DOMESTIC & DAILY-WAGE LEDGER
    // =========================================================================
    function getStoredHelpers() {
      try {
        const stored = localStorage.getItem('paypilot_helpers');
        if (stored) return JSON.parse(stored);
      } catch (e) {}
      return [
        { id: "HLP-1", name: "Sunita Devi", role: "Domestic Maid", phone: "9876543210", payType: "monthly", wage: 4500, presentDays: 26, absences: 2, halfDays: 0, paidLeaves: 2, advance: 500, bonus: 1000 },
        { id: "HLP-2", name: "Ramesh Kumar", role: "Cook", phone: "9876543211", payType: "monthly", wage: 6000, presentDays: 28, absences: 1, halfDays: 1, paidLeaves: 0, advance: 1000, bonus: 1500 },
        { id: "HLP-3", name: "Balwinder Singh", role: "Driver", phone: "9876543212", payType: "monthly", wage: 14000, presentDays: 29, absences: 1, halfDays: 0, paidLeaves: 0, advance: 2000, bonus: 2000 }
      ];
    }

    function saveStoredHelpers(list) {
      try {
        localStorage.setItem('paypilot_helpers', JSON.stringify(list));
      } catch (e) {}
    }

    function renderWelfareLedger(pane) {
      if (!pane) return;
      const helpers = getStoredHelpers();

      let helpersHtml = helpers.map((h, idx) => {
        const dailyEq = h.payType === 'daily' ? h.wage : (h.wage / 30);
        const earned = h.payType === 'daily' 
          ? Math.round((h.presentDays + (h.paidLeaves || 0) + (h.halfDays || 0) * 0.5) * h.wage)
          : Math.round(h.wage - ((h.absences || 0) * dailyEq));
        const netPay = Math.max(0, Math.round(earned - (h.advance || 0) + (h.bonus || 0)));

        return `
          <div class="card" style="margin-bottom: 16px; border-left: 4px solid var(--cinema-teal);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
              <div>
                <h3 style="color: var(--cinema-cream); margin: 0 0 4px 0;">${escapeHtml(h.name)}</h3>
                <span class="badge badge-teal">${escapeHtml(h.role)}</span>
                <span style="font-size: 13px; color: var(--cinema-muted); margin-left: 8px;">📞 ${escapeHtml(h.phone)}</span>
              </div>
              <div style="text-align: right;">
                <span style="font-size: 12px; color: var(--cinema-muted);">Net Payable This Month:</span>
                <div class="font-mono" style="font-size: 24px; font-weight: 800; color: var(--cinema-gold);">₹${netPay.toLocaleString('en-IN')}</div>
              </div>
            </div>

            <!-- Attendance & Advance Controls -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 16px 0; background: var(--bg-card-subtle); padding: 14px; border-radius: var(--radius-sm);">
              <div>
                <label style="font-size: 11px; color: var(--cinema-muted);">Present Days:</label>
                <input type="number" class="form-control font-mono" style="padding:4px 8px;" value="${h.presentDays}" onchange="updateHelperStat(${idx}, 'presentDays', this.value)">
              </div>
              <div>
                <label style="font-size: 11px; color: var(--cinema-muted);">Absences:</label>
                <input type="number" class="form-control font-mono" style="padding:4px 8px;" value="${h.absences || 0}" onchange="updateHelperStat(${idx}, 'absences', this.value)">
              </div>
              <div>
                <label style="font-size: 11px; color: var(--cinema-muted);">Advance Deducted (₹):</label>
                <input type="number" class="form-control font-mono" style="padding:4px 8px;" value="${h.advance || 0}" onchange="updateHelperStat(${idx}, 'advance', this.value)">
              </div>
              <div>
                <label style="font-size: 11px; color: var(--cinema-muted);">Festival Gift / Bonus (₹):</label>
                <input type="number" class="form-control font-mono" style="padding:4px 8px;" value="${h.bonus || 0}" onchange="updateHelperStat(${idx}, 'bonus', this.value)">
              </div>
            </div>

            <!-- Actions: WhatsApp Payslip & Loan Income Proof -->
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
              <button class="btn btn-teal" style="font-size: 13px;" onclick="sendHelperPayslipWhatsApp(${idx})">
                💬 Send WhatsApp Payslip
              </button>
              <button class="btn btn-glass" style="font-size: 13px;" onclick="printHelperIncomeProof(${idx})">
                📜 Print Loan Income Proof
              </button>
              <button class="btn btn-glass" style="font-size: 13px; color: var(--cinema-crimson);" onclick="removeHelper(${idx})">
                🗑️ Remove
              </button>
            </div>
          </div>
        `;
      }).join('');

      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-teal);">📒 ${getT('ledgerName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">${getT('ledgerDesc')}</p>
            </div>
            <button class="btn btn-orange" onclick="openAddHelperModal()">+ Add New Helper</button>
          </div>
        </div>

        <div style="margin-bottom: 24px;">
          ${helpersHtml}
        </div>

        ${getLegalAttributionHtml()}
      `;
    }

    function updateHelperStat(idx, key, val) {
      const helpers = getStoredHelpers();
      if (helpers[idx]) {
        helpers[idx][key] = parseFloat(val) || 0;
        saveStoredHelpers(helpers);
        renderWelfareLedger(document.getElementById('pane-welfare-ledger'));
      }
    }

    function removeHelper(idx) {
      if (!confirm("Are you sure you want to remove this helper?")) return;
      const helpers = getStoredHelpers();
      helpers.splice(idx, 1);
      saveStoredHelpers(helpers);
      renderWelfareLedger(document.getElementById('pane-welfare-ledger'));
    }

    function openAddHelperModal() {
      const name = prompt("Helper's Name (e.g. Sunita Devi):");
      if (!name) return;
      const role = prompt("Role (e.g. Domestic Maid, Cook, Driver, Labourer):", "Domestic Maid") || "Helper";
      const wage = parseFloat(prompt("Monthly or Daily Agreed Wage (₹):", "5000")) || 5000;
      const phone = prompt("WhatsApp Mobile Number:", "9876543210") || "";

      const helpers = getStoredHelpers();
      helpers.push({
        id: "HLP-" + Date.now(),
        name: name.trim(),
        role: role.trim(),
        phone: phone.trim(),
        payType: "monthly",
        wage: wage,
        presentDays: 26,
        absences: 0,
        advance: 0,
        bonus: 0
      });
      saveStoredHelpers(helpers);
      renderWelfareLedger(document.getElementById('pane-welfare-ledger'));
    }

    function sendHelperPayslipWhatsApp(idx) {
      const h = getStoredHelpers()[idx];
      if (!h) return;
      const dailyEq = h.payType === 'daily' ? h.wage : (h.wage / 30);
      const earned = h.payType === 'daily' 
        ? Math.round((h.presentDays + (h.paidLeaves || 0) + (h.halfDays || 0) * 0.5) * h.wage)
        : Math.round(h.wage - ((h.absences || 0) * dailyEq));
      const netPay = Math.max(0, Math.round(earned - (h.advance || 0) + (h.bonus || 0)));

      const msg = `*PAYSLIP // सैलरी स्लिप*\nName: ${h.name}\nRole: ${h.role}\nMonth: ${new Date().toLocaleString('en-IN', { month: 'long', year: 'numeric' })}\n-----------------------\nBase Wage: ₹${h.wage.toLocaleString('en-IN')}\nPresent Days: ${h.presentDays}\nAbsences: ${h.absences || 0}\nAdvances Deducted: -₹${(h.advance || 0).toLocaleString('en-IN')}\nFestival Bonus: +₹${(h.bonus || 0).toLocaleString('en-IN')}\n-----------------------\n*NET SALARY PAID: ₹${netPay.toLocaleString('en-IN')}*\nStatus: Paid in full with dignity.\nThank you for your service! 🙏`;

      shareWelfareWhatsApp(msg);
    }

    function printHelperIncomeProof(idx) {
      const h = getStoredHelpers()[idx];
      if (!h) return;
      const win = window.open('', '_blank');
      if (!win) { alert("Please allow popups to print certificate."); return; }
      win.document.write(`
        <html>
        <head>
          <title>Income Certificate - ${escapeHtml(h.name)}</title>
          <style>
            body { font-family: sans-serif; padding: 40px; color: #111; line-height: 1.8; }
            .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 30px; }
            .box { border: 1px solid #ccc; padding: 20px; border-radius: 8px; margin: 20px 0; background: #fdfdfd; }
            .footer { margin-top: 60px; display: flex; justify-content: space-between; }
          </style>
        </head>
        <body>
          <div class="header">
            <h2>TO WHOMSOEVER IT MAY CONCERN</h2>
            <h3>EMPLOYMENT &amp; MONTHLY INCOME VERIFICATION CERTIFICATE</h3>
          </div>
          <p>This is to certify that <strong>${escapeHtml(h.name)}</strong> (Mobile: ${escapeHtml(h.phone)}) is employed as a <strong>${escapeHtml(h.role)}</strong> under regular domestic/commercial engagement.</p>
          <div class="box">
            <p><strong>Monthly Agreed Remuneration:</strong> ₹${h.wage.toLocaleString('en-IN')} per month</p>
            <p><strong>Engagement Duration:</strong> Active regular service</p>
            <p><strong>Payment Mode:</strong> Monthly account transfer / Cash with formal acknowledgment</p>
            <p><strong>Conduct &amp; Reliability:</strong> Satisfactory and punctual</p>
          </div>
          <p>This certificate is issued at the request of the employee as genuine proof of monthly income for banking purposes, micro-finance applications, or residential verification.</p>
          <div class="footer">
            <div>Date: ${new Date().toLocaleDateString('en-IN')}</div>
            <div style="text-align: right;">
              ___________________________<br>
              <strong>Employer / Household Head Signature</strong><br>
              PayPilot Verified Record
            </div>
          </div>
          <script>window.print();<\/script>
        </body>
        </html>
      `);
      win.document.close();
    }

    // =========================================================================
    // 10. SCREEN 3: BENEFITS FINDER ("What am I entitled to?")
    // =========================================================================
    function renderBenefitsFinder(pane) {
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-gold);">🎁 ${getT('benefitsName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">Answer 5 simple questions to see statutory social security rights under Indian Labour Laws.</p>
            </div>
            <button class="btn-read-aloud" id="btn-read-benefits">${getT('readAloud')}</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- 5 Questions -->
          <div class="card">
            <h3 style="color: var(--cinema-gold); margin-bottom: 16px;">5 Simple Questions</h3>
            
            <div class="form-group">
              <label class="form-label">1. Monthly Gross Wage (₹)</label>
              <input type="number" class="form-control font-mono" id="ben-wage" value="14000" oninput="calculateBenefits()">
            </div>

            <div class="form-group">
              <label class="form-label">2. ${getT('yearsInJob')}</label>
              <input type="number" class="form-control font-mono" id="ben-years" value="5" min="0" step="0.5" oninput="calculateBenefits()">
            </div>

            <div class="form-group">
              <label class="form-label">3. ${getT('gender')}</label>
              <select class="form-control" id="ben-gender" onchange="calculateBenefits()">
                <option value="male">${getT('male')}</option>
                <option value="female" selected>${getT('female')}</option>
                <option value="other">${getT('other')}</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">4. State</label>
              <select class="form-control" id="ben-state" onchange="calculateBenefits()">
                <option value="Maharashtra" selected>Maharashtra</option>
                <option value="Delhi">Delhi</option>
                <option value="Karnataka">Karnataka</option>
                <option value="Tamil Nadu">Tamil Nadu</option>
                <option value="Uttar Pradesh">Uttar Pradesh</option>
                <option value="Punjab">Punjab</option>
                <option value="West Bengal">West Bengal</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">5. ${getT('numEmployees')}</label>
              <select class="form-control" id="ben-emps" onchange="calculateBenefits()">
                <option value="under10">Less than 10 employees</option>
                <option value="10to19">10 to 19 employees</option>
                <option value="20plus" selected>20 or more employees</option>
              </select>
            </div>
          </div>

          <!-- Entitlement Cards -->
          <div class="card card-glow-gold" id="ben-cards-container">
            <!-- Rendered by calculateBenefits() -->
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;

      document.getElementById('btn-read-benefits').onclick = () => {
        const text = document.getElementById('ben-speech-text')?.innerText || "Benefits evaluation results.";
        readAloudText(text);
      };

      calculateBenefits();
    }

    function calculateBenefits() {
      try {
        const wage = parseFloat(document.getElementById('ben-wage')?.value || 0);
        const years = parseFloat(document.getElementById('ben-years')?.value || 0);
        const gender = document.getElementById('ben-gender')?.value || 'female';
        const emps = document.getElementById('ben-emps')?.value || '20plus';

        const has20Emps = emps === '20plus';
        const has10Emps = emps === '10to19' || emps === '20plus';

        const items = [
          {
            title: "Provident Fund (EPF)",
            applies: has20Emps,
            mandatory: has20Emps && wage <= 15000,
            badge: has20Emps ? (wage <= 15000 ? "YES (MANDATORY)" : "YES (VOLUNTARY)") : "NO",
            badgeClass: has20Emps ? "badge-teal" : "badge-crimson",
            reason: has20Emps 
              ? (wage <= 15000 ? "Mandatory for all workers earning up to ₹15,000 in establishments with 20+ staff." : "Applicable if employer has 20+ staff; voluntary for salaries above ₹15,000.")
              : "Not legally mandatory because employer headcount is below 20 workers.",
            howToClaim: "Ask employer for your 12-digit UAN number and ensure 12% EPF is deposited every month."
          },
          {
            title: "Employee State Insurance (ESI)",
            applies: has10Emps && wage <= 21000,
            badge: (has10Emps && wage <= 21000) ? "YES" : "NO",
            badgeClass: (has10Emps && wage <= 21000) ? "badge-teal" : "badge-crimson",
            reason: (has10Emps && wage <= 21000)
              ? "Covers all staff earning ₹21,000 or less in establishments with 10+ employees. Free health care."
              : (wage > 21000 ? "Wage exceeds statutory ESI limit of ₹21,000/month." : "Establishment has fewer than 10 employees."),
            howToClaim: "Ask employer to register you on the ESIC portal and get your Pehchan biometric health card."
          },
          {
            title: "Statutory Gratuity",
            applies: has10Emps && years >= 5,
            badge: (has10Emps && years >= 5) ? "YES" : (has10Emps ? "MAYBE (UPON 5 YRS)" : "NO"),
            badgeClass: (has10Emps && years >= 5) ? "badge-teal" : (has10Emps ? "badge-gold" : "badge-crimson"),
            reason: (has10Emps && years >= 5)
              ? `Entitled to 15 days basic salary for every completed year (${years} years completed).`
              : (has10Emps ? `Requires 5 continuous years of service (currently completed ${years} years).` : "Employer has fewer than 10 workers."),
            howToClaim: "Submit Form I to employer upon leaving or retirement to receive 15 days wage per completed year."
          },
          {
            title: "Statutory Annual Bonus",
            applies: has20Emps && wage <= 21000,
            badge: (has20Emps && wage <= 21000) ? "YES (8.33% MIN)" : "NO",
            badgeClass: (has20Emps && wage <= 21000) ? "badge-teal" : "badge-crimson",
            reason: (has20Emps && wage <= 21000)
              ? "All workers earning up to ₹21,000 who worked at least 30 days are entitled to minimum 8.33% bonus."
              : "Requires company with 20+ workers and salary under ₹21,000.",
            howToClaim: "Claim before Diwali / Puja festival as mandated by Payment of Bonus Act 1965."
          },
          {
            title: "Paid Annual Leave (Earned Leave)",
            applies: true,
            badge: "YES (1 DAY PER 20 DAYS)",
            badgeClass: "badge-teal",
            reason: "All factory, shop, and commercial staff earn 1 day of paid leave for every 20 days worked (~15-18 days/yr).",
            howToClaim: "Request leave balance ledger and encash unavailed leaves upon departure."
          },
          {
            title: "Maternity Benefit (26 Weeks Paid)",
            applies: gender === 'female' && has10Emps,
            badge: (gender === 'female' && has10Emps) ? "YES (26 WEEKS PAID)" : (gender === 'female' ? "MAYBE" : "N/A"),
            badgeClass: (gender === 'female' && has10Emps) ? "badge-teal" : "badge-crimson",
            reason: gender === 'female'
              ? (has10Emps ? "Full 26 weeks paid leave if you worked at least 80 days in the preceding 12 months." : "Establishment has fewer than 10 workers.")
              : "Applicable to female workers under Maternity Benefit Act 1961.",
            howToClaim: "Submit written notice with estimated delivery certificate 8 weeks before delivery."
          },
          {
            title: "Weekly Paid Rest Day",
            applies: true,
            badge: "YES (MANDATORY)",
            badgeClass: "badge-teal",
            reason: "Under Minimum Wages Act and Weekly Holidays Act, every worker is entitled to 1 day off with wages every 6 days.",
            howToClaim: "Ensure no deduction is made for your designated weekly rest day."
          }
        ];

        let cardsHtml = items.map(it => `
          <div style="background: var(--bg-card-subtle); border-radius: var(--radius-sm); padding: 14px; margin-bottom: 12px; border-left: 3px solid ${it.badge.startsWith('YES') ? 'var(--cinema-teal)' : 'var(--cinema-muted)'};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <strong style="color: var(--cinema-cream); font-size: 15px;">${it.title}</strong>
              <span class="badge ${it.badgeClass}">${it.badge}</span>
            </div>
            <p style="font-size: 13px; color: var(--cinema-muted); margin: 4px 0;">${it.reason}</p>
            <div style="font-size: 12px; color: var(--cinema-gold); font-weight: 600;">👉 How to claim: ${it.howToClaim}</div>
          </div>
        `).join('');

        const container = document.getElementById('ben-cards-container');
        if (!container) return;

        const speechSummary = `Your benefits: Provident Fund is ${has20Emps ? 'applicable' : 'not mandatory'}. ESI medical coverage is ${has10Emps && wage <= 21000 ? 'applicable' : 'not applicable'}. Gratuity is ${has10Emps && years >= 5 ? 'eligible' : 'not yet eligible'}.`;

        container.innerHTML = `
          <div id="ben-speech-text" style="display:none;">${speechSummary}</div>
          <h3 style="color: var(--cinema-teal); margin-bottom: 16px;">Your Legal Entitlements</h3>
          ${cardsHtml}
          
          <div style="margin-top: 16px;">
            <button class="btn btn-teal" onclick="copyWelfareText('${escapeHtml(speechSummary)}', this)">
              ${getT('copyText')}
            </button>
            <button class="btn btn-orange" onclick="shareWelfareWhatsApp('${encodeURIComponent(speechSummary)}')">
              ${getT('shareWhatsApp')}
            </button>
          </div>
        `;
      } catch (err) {
        console.error('Benefits calculation error:', err);
      }
    }

    // =========================================================================
    // 11. SCREEN 4: GOVERNMENT SCHEME MATCHER
    // =========================================================================
    function renderSchemeMatcher(pane) {
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-emerald);">📜 ${getT('schemesName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">${getT('schemesDesc')}</p>
            </div>
            <button class="btn-read-aloud" id="btn-read-schemes">${getT('readAloud')}</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- Filter Card -->
          <div class="card">
            <h3 style="color: var(--cinema-emerald); margin-bottom: 16px;">Your Profile Criteria</h3>
            
            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Age (Years)</label>
                <input type="number" class="form-control font-mono" id="sch-age" value="32" min="10" max="90" oninput="calculateSchemes()">
              </div>
              <div class="form-group">
                <label class="form-label">Gender</label>
                <select class="form-control" id="sch-gender" onchange="calculateSchemes()">
                  <option value="all">Any / All</option>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Occupation</label>
              <select class="form-control" id="sch-occupation" onchange="calculateSchemes()">
                <option value="unorganized" selected>Unorganized Worker / Domestic / Helper</option>
                <option value="street-vendor">Street Vendor / Hawkers</option>
                <option value="small-business">Small Business / Kirana Shop Owner</option>
                <option value="all">General / Salaried Employee</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Monthly Household Income (₹)</label>
              <input type="number" class="form-control font-mono" id="sch-income" value="12000" oninput="calculateSchemes()">
            </div>

            <div class="form-group">
              <label class="form-label">Documents Available:</label>
              <div style="display: flex; gap: 14px; flex-wrap: wrap; margin-top: 6px;">
                <label><input type="checkbox" id="sch-has-aadhaar" checked onchange="calculateSchemes()"> Aadhaar</label>
                <label><input type="checkbox" id="sch-has-bank" checked onchange="calculateSchemes()"> Bank Account</label>
                <label><input type="checkbox" id="sch-has-ration" checked onchange="calculateSchemes()"> Ration Card</label>
              </div>
            </div>
          </div>

          <!-- Matched Schemes -->
          <div class="card card-glow-teal" id="sch-results-container">
            <!-- Rendered by calculateSchemes() -->
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;

      document.getElementById('btn-read-schemes').onclick = () => {
        const text = document.getElementById('sch-speech-text')?.innerText || "Government schemes matches.";
        readAloudText(text);
      };

      calculateSchemes();
    }

    function calculateSchemes() {
      try {
        const r = window.welfareRules || DEFAULT_WELFARE_RULES;
        const schemes = r.schemes || DEFAULT_WELFARE_RULES.schemes;

        const age = parseFloat(document.getElementById('sch-age')?.value || 30);
        const income = parseFloat(document.getElementById('sch-income')?.value || 12000);
        const occ = document.getElementById('sch-occupation')?.value || 'unorganized';

        const matched = schemes.filter(s => {
          if (age < s.minAge || age > s.maxAge) return false;
          if (income > s.maxIncome) return false;
          if (s.occupation !== 'all' && occ !== 'all' && s.occupation !== occ) return false;
          return true;
        });

        let matchesHtml = matched.map(m => `
          <div style="background: var(--bg-card-subtle); border-radius: var(--radius-sm); padding: 14px; margin-bottom: 12px; border-left: 3px solid var(--cinema-emerald);">
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
              <h4 style="color: var(--cinema-cream); margin: 0 0 4px 0;">${escapeHtml(m.name)}</h4>
              <span class="badge badge-teal">MATCHED ✓</span>
            </div>
            <p style="font-size: 13px; color: var(--cinema-muted); margin: 6px 0;"><strong>Benefit:</strong> ${escapeHtml(m.benefit)}</p>
            <p style="font-size: 12px; color: var(--cinema-gold); margin: 4px 0;"><strong>Documents Needed:</strong> ${escapeHtml(m.documents)}</p>
            <div style="margin-top: 8px;">
              <a href="https://${escapeHtml(m.url)}" target="_blank" rel="noopener noreferrer" style="color: var(--cinema-teal); font-size: 13px; font-weight: 700; text-decoration: none;">
                Official Portal: ${escapeHtml(m.url)} ➔
              </a>
            </div>
          </div>
        `).join('');

        if (matched.length === 0) {
          matchesHtml = `<p style="color: var(--cinema-muted);">No schemes directly matched the criteria. Try adjusting income or age limit.</p>`;
        }

        const container = document.getElementById('sch-results-container');
        if (!container) return;

        const speechSummary = `Found ${matched.length} matching government schemes: ${matched.map(m => m.name).join(', ')}.`;

        container.innerHTML = `
          <div id="sch-speech-text" style="display:none;">${speechSummary}</div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h3 style="color: var(--cinema-emerald); margin: 0;">Matched Schemes (${matched.length})</h3>
            <button class="btn btn-glass" style="font-size: 12px;" onclick="printDocChecklist()">🖨️ Documents Checklist</button>
          </div>
          ${matchesHtml}
        `;
      } catch (err) {
        console.error('Scheme matcher error:', err);
      }
    }

    function printDocChecklist() {
      const win = window.open('', '_blank');
      if (!win) { alert("Please allow popups to print checklist."); return; }
      win.document.write(`
        <html>
        <head>
          <title>Government Schemes - Documents Checklist</title>
          <style>body { font-family: sans-serif; padding: 30px; line-height: 1.8; } h2 { color: #0E7490; }</style>
        </head>
        <body>
          <h2>GOVERNMENT WELFARE SCHEMES — DOCUMENTS CHECKLIST</h2>
          <p>Keep these documents ready to register at any Common Service Centre (CSC) or online:</p>
          <ul>
            <li>[ ] <strong>Aadhaar Card:</strong> Linked with your active mobile number for OTP.</li>
            <li>[ ] <strong>Bank Passbook:</strong> Showing Account Number, IFSC code, and Name.</li>
            <li>[ ] <strong>Ration Card:</strong> (BPL, Antyodaya, or NFSA) for subsidized food and Ayushman Bharat.</li>
            <li>[ ] <strong>Passport Size Photos:</strong> (At least 4 recent photographs).</li>
            <li>[ ] <strong>Nominee Details:</strong> Name, relation, age, and Aadhaar of nominee.</li>
          </ul>
          <p><em>PayPilot Welfare Guidance • Official Portals: eshram.gov.in, maandhan.in, pmjay.gov.in</em></p>
          <script>window.print();<\/script>
        </body>
        </html>
      `);
      win.document.close();
    }

    // =========================================================================
    // 12. SCREEN 5: LOAN TRAP DETECTOR
    // =========================================================================
    function renderLoanTrap(pane) {
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-crimson);">🪤 ${getT('loanTrapName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">${getT('loanTrapDesc')}</p>
            </div>
            <button class="btn-read-aloud" id="btn-read-loantrap">${getT('readAloud')}</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- Loan Inputs -->
          <div class="card">
            <h3 style="color: var(--cinema-crimson); margin-bottom: 16px;">Loan &amp; Repayment Terms</h3>

            <div class="form-group">
              <label class="form-label">${getT('loanAmount')}</label>
              <input type="number" class="form-control font-mono" id="lt-amount" value="10000" oninput="calculateLoanTrap()">
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">${getT('instalmentAmount')}</label>
                <input type="number" class="form-control font-mono" id="lt-emi" value="500" oninput="calculateLoanTrap()">
              </div>
              <div class="form-group">
                <label class="form-label">${getT('instalmentFreq')}</label>
                <select class="form-control" id="lt-freq" onchange="calculateLoanTrap()">
                  <option value="daily">Daily Repayment</option>
                  <option value="weekly" selected>Weekly Repayment</option>
                  <option value="monthly">Monthly Repayment</option>
                </select>
              </div>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">${getT('numInstalments')}</label>
                <input type="number" class="form-control font-mono" id="lt-num" value="25" oninput="calculateLoanTrap()">
              </div>
              <div class="form-group">
                <label class="form-label">${getT('procFees')}</label>
                <input type="number" class="form-control font-mono" id="lt-fee" value="500" oninput="calculateLoanTrap()">
              </div>
            </div>

            <h4 style="color: var(--cinema-gold); margin: 20px 0 10px 0;">Red Flags Checklist (Tick if true):</h4>
            <div class="welfare-checklist-item">
              <input type="checkbox" id="rf-nopaper" onchange="calculateLoanTrap()">
              <label for="rf-nopaper">No written loan agreement or official signed receipt given.</label>
            </div>
            <div class="welfare-checklist-item">
              <input type="checkbox" id="rf-keepcard" onchange="calculateLoanTrap()">
              <label for="rf-keepcard">Lender keeps your Aadhaar card, ATM card, or bank passbook.</label>
            </div>
            <div class="welfare-checklist-item">
              <input type="checkbox" id="rf-blankcheque" onchange="calculateLoanTrap()">
              <label for="rf-blankcheque">Lender demanded signed blank cheques or empty promissory notes.</label>
            </div>
            <div class="welfare-checklist-item">
              <input type="checkbox" id="rf-doorstep" onchange="calculateLoanTrap()">
              <label for="rf-doorstep">Daily doorstep collection with intimidation or abusive language.</label>
            </div>
          </div>

          <!-- True APR Result Card -->
          <div class="card card-glow-crimson" id="lt-result-container">
            <!-- Rendered by calculateLoanTrap() -->
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;

      document.getElementById('btn-read-loantrap').onclick = () => {
        const text = document.getElementById('lt-speech-text')?.innerText || "Loan trap result.";
        readAloudText(text);
      };

      calculateLoanTrap();
    }

    function calculateLoanTrap() {
      try {
        const principal = parseFloat(document.getElementById('lt-amount')?.value || 10000);
        const emi = parseFloat(document.getElementById('lt-emi')?.value || 500);
        const freq = document.getElementById('lt-freq')?.value || 'weekly';
        const num = parseFloat(document.getElementById('lt-num')?.value || 25);
        const fee = parseFloat(document.getElementById('lt-fee')?.value || 0);

        const netReceived = Math.max(1, principal - fee);
        const totalRepaid = Math.round(emi * num);
        const extraPaid = Math.max(0, totalRepaid - netReceived);

        let periodsPerYear = 12;
        if (freq === 'daily') periodsPerYear = 365;
        else if (freq === 'weekly') periodsPerYear = 52;

        // Binary search for Internal Rate of Return (IRR)
        let low = 0, high = 10, periodicRate = 0;
        for (let iter = 0; iter < 60; iter++) {
          const mid = (low + high) / 2;
          let pv = 0;
          for (let t = 1; t <= num; t++) {
            pv += emi / Math.pow(1 + mid, t);
          }
          if (pv > netReceived) low = mid;
          else high = mid;
        }
        periodicRate = (low + high) / 2;
        const apr = Math.round(periodicRate * periodsPerYear * 100);

        // Warning level
        let warningClass = 'welfare-verdict-green', warningTitle = getT('loanFair');
        if (apr > 36) {
          warningClass = 'welfare-verdict-red';
          warningTitle = getT('loanTrap');
        } else if (apr > 18) {
          warningClass = 'welfare-verdict-amber';
          warningTitle = getT('loanHigh');
        }

        const rfNoPaper = document.getElementById('rf-nopaper')?.checked;
        const rfKeepCard = document.getElementById('rf-keepcard')?.checked;
        const rfBlankCheque = document.getElementById('rf-blankcheque')?.checked;
        const rfDoorstep = document.getElementById('rf-doorstep')?.checked;
        const flaggedCount = (rfNoPaper ? 1 : 0) + (rfKeepCard ? 1 : 0) + (rfBlankCheque ? 1 : 0) + (rfDoorstep ? 1 : 0);

        const container = document.getElementById('lt-result-container');
        if (!container) return;

        const speechSummary = `True Annual Interest Rate is ${apr} percent. Total extra paid is ₹${extraPaid}. ${warningTitle}`;

        container.innerHTML = `
          <div id="lt-speech-text" style="display:none;">${escapeHtml(speechSummary)}</div>

          <div class="welfare-verdict-box ${warningClass}">
            <h3 style="margin:0 0 6px 0; font-size:18px;">${warningTitle}</h3>
            <div style="font-size: 34px; font-weight: 800; font-family: var(--font-mono); margin: 6px 0;">
              True APR: ${apr}% / Year
            </div>
            <div style="font-size: 13px; opacity: 0.9;">
              ${flaggedCount > 0 ? `⚠️ ${flaggedCount} Severe Red Flag(s) detected! Illegal money lending practices suspected.` : 'No red flags checked.'}
            </div>
          </div>

          <h4 style="color: var(--cinema-cream); margin: 16px 0 10px 0;">Numbers Used in Loan</h4>
          <div class="table-container" style="margin-bottom: 16px;">
            <table>
              <tr><td>Net Cash Handed to You:</td><td class="font-mono">₹${netReceived.toLocaleString('en-IN')}</td></tr>
              <tr><td>Total Amount Repaid:</td><td class="font-mono" style="color:var(--cinema-gold); font-weight:700;">₹${totalRepaid.toLocaleString('en-IN')}</td></tr>
              <tr><td>Extra Money Paid (Interest + Fees):</td><td class="font-mono" style="color:var(--cinema-crimson); font-weight:700;">₹${extraPaid.toLocaleString('en-IN')}</td></tr>
              <tr><td>Equal Bank Loan Interest (11% p.a.):</td><td class="font-mono" style="color:var(--cinema-teal);">₹${Math.round(netReceived * 0.11 * (num / periodsPerYear)).toLocaleString('en-IN')}</td></tr>
            </table>
          </div>

          <h4 style="color: var(--cinema-teal); margin-bottom: 8px;">${getT('whatToDoNext')}</h4>
          <div class="welfare-step-box">
            ${apr > 36 
              ? `1. Stop taking fresh advances from this lender.<br>2. Demanding ATM cards or blank cheques is <strong>illegal</strong> under state Money Lenders Acts.<br>3. Check PM Mudra or PM SVANidhi loans at any nationalized bank for 7-11% interest.`
              : `1. This loan rate is within reasonable bounds.<br>2. Always demand a signed payment receipt for each instalment.<br>3. Aim to pay off early to minimize interest.`}
          </div>

          <div style="display: flex; gap: 10px; margin-top: 16px;">
            <button class="btn btn-teal" onclick="copyWelfareText('${escapeHtml(speechSummary)}', this)">
              ${getT('copyText')}
            </button>
            <button class="btn btn-orange" onclick="shareWelfareWhatsApp('${encodeURIComponent(speechSummary)}')">
              ${getT('shareWhatsApp')}
            </button>
          </div>
        `;
      } catch (err) {
        console.error('Loan trap calculation error:', err);
      }
    }

    // =========================================================================
    // 13. SCREEN 6: WOMEN & FAMILY SUPPORT
    // =========================================================================
    function renderWomenFamily(pane) {
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: #F472B6;">🌸 ${getT('womenFamilyName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">Maternity leave planner (26 paid weeks), safe night shift checklist, and equal pay checker.</p>
            </div>
            <button class="btn-read-aloud" id="btn-read-women">${getT('readAloud')}</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- Tool 1: Maternity Benefit Planner -->
          <div class="card">
            <h3 style="color: #F472B6; margin-bottom: 16px;">1. Maternity Benefit Planner (26 Weeks Paid)</h3>
            
            <div class="form-group">
              <label class="form-label">Expected Delivery Date (EDD)</label>
              <input type="date" class="form-control font-mono" id="wf-edd" value="2026-12-15" onchange="calculateMaternity()">
            </div>

            <div class="form-group">
              <label class="form-label">Monthly Basic Salary (₹)</label>
              <input type="number" class="form-control font-mono" id="wf-wage" value="25000" oninput="calculateMaternity()">
            </div>

            <div id="wf-maternity-result" style="background: var(--bg-card-subtle); padding: 16px; border-radius: var(--radius-sm); margin-top: 14px;">
              <!-- Calculated by calculateMaternity() -->
            </div>
          </div>

          <!-- Tool 2: Equal Pay Comparison -->
          <div class="card">
            <h3 style="color: var(--cinema-gold); margin-bottom: 16px;">2. Equal-Pay Comparison (Equal Remuneration Act 1976)</h3>
            <p style="font-size: 13px; color: var(--cinema-muted); margin-bottom: 14px;">Enter job roles and pay without names to verify gender pay parity.</p>
            
            <div class="form-group">
              <label class="form-label">Job Role / Designation</label>
              <input type="text" class="form-control" id="ep-role" value="Sales Counter Assistant" oninput="calculateEqualPay()">
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Male Employee Pay (₹)</label>
                <input type="number" class="form-control font-mono" id="ep-male" value="18000" oninput="calculateEqualPay()">
              </div>
              <div class="form-group">
                <label class="form-label">Female Employee Pay (₹)</label>
                <input type="number" class="form-control font-mono" id="ep-female" value="15000" oninput="calculateEqualPay()">
              </div>
            </div>

            <div id="ep-result" style="background: var(--bg-card-subtle); padding: 16px; border-radius: var(--radius-sm); margin-top: 14px;">
              <!-- Calculated by calculateEqualPay() -->
            </div>
          </div>
        </div>

        <!-- Tool 3: Safe Late-Shift Checklist -->
        <div class="card" style="margin-top: 20px;">
          <h3 style="color: var(--cinema-teal); margin-bottom: 12px;">3. Safe Night-Shift Statutory Checklist (Post 7:00 PM / 8:00 PM)</h3>
          <p style="font-size: 13px; color: var(--cinema-muted); margin-bottom: 16px;">Statutory conditions mandated under state Shops &amp; Establishment Acts for women working late shifts:</p>
          
          <div class="grid-2">
            <div class="welfare-checklist-item">
              <input type="checkbox" id="sc-cab" checked>
              <label for="sc-cab">Door-to-door company cab drop-off with GPS tracking and security guard.</label>
            </div>
            <div class="welfare-checklist-item">
              <input type="checkbox" id="sc-group" checked>
              <label for="sc-group">Group scheduling: Minimum 2 women scheduled together in the late shift.</label>
            </div>
            <div class="welfare-checklist-item">
              <input type="checkbox" id="sc-cctv" checked>
              <label for="sc-cctv">Functional CCTV in common work areas, entry/exit, and parking facilities.</label>
            </div>
            <div class="welfare-checklist-item">
              <input type="checkbox" id="sc-posh" checked>
              <label for="sc-posh">Internal Complaints Committee (POSH Act) constituted with female presiding officer.</label>
            </div>
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;

      document.getElementById('btn-read-women').onclick = () => {
        readAloudText("Maternity benefit and equal pay results.");
      };

      calculateMaternity();
      calculateEqualPay();
    }

    function calculateMaternity() {
      try {
        const eddVal = document.getElementById('wf-edd')?.value || '2026-12-15';
        const wage = parseFloat(document.getElementById('wf-wage')?.value || 25000);

        const edd = new Date(eddVal);
        const leaveStart = new Date(edd.getTime() - (8 * 7 * 24 * 60 * 60 * 1000)); // 8 weeks before
        const leaveEnd = new Date(leaveStart.getTime() + (26 * 7 * 24 * 60 * 60 * 1000)); // 26 weeks total

        const weeklyWage = (wage * 12) / 52;
        const totalMaternityPay = Math.round(weeklyWage * 26);
        const advancePay = Math.round(weeklyWage * 8);
        const balancePay = Math.round(weeklyWage * 18);

        const resEl = document.getElementById('wf-maternity-result');
        if (!resEl) return;

        resEl.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
            <strong style="color: #F472B6;">Total Paid Maternity Wages:</strong>
            <span class="font-mono" style="font-size: 22px; font-weight: 800; color: var(--cinema-gold);">₹${totalMaternityPay.toLocaleString('en-IN')}</span>
          </div>
          <div style="font-size: 13px; line-height: 1.8; color: var(--cinema-cream);">
            • <strong>Leave Start Date:</strong> ${leaveStart.toLocaleDateString('en-IN')} (8 weeks prior)<br>
            • <strong>Return to Work Date:</strong> ${leaveEnd.toLocaleDateString('en-IN')} (26 weeks completed)<br>
            • <strong>Pre-natal Advance Due:</strong> ₹${advancePay.toLocaleString('en-IN')} (on starting leave)<br>
            • <strong>Post-natal Balance Due:</strong> ₹${balancePay.toLocaleString('en-IN')} (after childbirth proof)<br>
            • <strong>Crèche Access:</strong> Required if employer has 50+ workers (4 daily visits allowed).
          </div>
        `;
      } catch (e) {
        console.error('Maternity calculation error:', e);
      }
    }

    function calculateEqualPay() {
      try {
        const role = document.getElementById('ep-role')?.value || 'Staff';
        const male = parseFloat(document.getElementById('ep-male')?.value || 0);
        const female = parseFloat(document.getElementById('ep-female')?.value || 0);

        const diff = male - female;
        const gapPct = male > 0 ? Math.round((diff / male) * 100) : 0;

        const resEl = document.getElementById('ep-result');
        if (!resEl) return;

        if (diff > 0) {
          resEl.innerHTML = `
            <div class="welfare-verdict-box welfare-verdict-amber" style="padding: 12px; margin: 0 0 10px 0;">
              <strong>Gender Pay Gap Detected: ${gapPct}%</strong>
              <div style="font-size: 13px; margin-top: 4px;">
                Shortfall: ₹${diff.toLocaleString('en-IN')}/month for the same role (${escapeHtml(role)}).
              </div>
            </div>
            <p style="font-size: 13px; color: var(--cinema-muted); line-height: 1.6; margin: 0;">
              Under Section 4 of the <strong>Equal Remuneration Act 1976</strong>, employers are legally prohibited from paying unequal wages to male and female workers performing identical or similar work.
            </p>
          `;
        } else {
          resEl.innerHTML = `
            <div class="welfare-verdict-box welfare-verdict-green" style="padding: 12px; margin: 0 0 10px 0;">
              <strong>Equal Pay Compliant ✓</strong>
              <div style="font-size: 13px; margin-top: 4px;">
                No gender pay disparity in role ${escapeHtml(role)}.
              </div>
            </div>
          `;
        }
      } catch (e) {
        console.error('Equal pay error:', e);
      }
    }

    // =========================================================================
    // 14. SCREEN 7: WORK-CULTURE PULSE (ANONYMOUS WITH 5-RESPONSE THRESHOLD)
    // =========================================================================
    function renderWorkCulturePulse(pane) {
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-teal);">💓 ${getT('pulseName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">Anonymous monthly feedback. Strict privacy lock: owner cannot see results until 5+ people respond.</p>
            </div>
            <button class="btn btn-orange" onclick="createNewPulseSurvey()">+ Create Monthly Survey</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- Anonymous Voting Form (For Employees) -->
          <div class="card card-glow-teal">
            <h3 style="color: var(--cinema-teal); margin-bottom: 8px;">Submit Anonymous Voice</h3>
            <p style="font-size: 13px; color: var(--cinema-muted); margin-bottom: 16px;">${getT('anonNotice')}</p>

            <div id="pulse-questions-form">
              <div class="form-group">
                <label class="form-label">1. Workload: Is your daily workload achievable without excessive overtime?</label>
                <select class="form-control" id="pq-1">
                  <option value="5">⭐⭐⭐⭐⭐ Excellent / Very Fair (5/5)</option>
                  <option value="4" selected>⭐⭐⭐⭐ Good / Manageable (4/5)</option>
                  <option value="3">⭐⭐⭐ Neutral / Heavy at times (3/5)</option>
                  <option value="2">⭐⭐ Poor / Overburdened (2/5)</option>
                  <option value="1">⭐ Critical / Unbearable (1/5)</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">2. Respect: Do managers and colleagues treat you with dignity?</label>
                <select class="form-control" id="pq-2">
                  <option value="5" selected>⭐⭐⭐⭐⭐ Always respectful (5/5)</option>
                  <option value="4">⭐⭐⭐⭐ Mostly respectful (4/5)</option>
                  <option value="3">⭐⭐⭐ Sometimes disrespectful (3/5)</option>
                  <option value="2">⭐⭐ Frequent disrespect (2/5)</option>
                  <option value="1">⭐ Abusive / Unacceptable (1/5)</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">3. Safety: Is the workplace clean, physically safe, and hazard-free?</label>
                <select class="form-control" id="pq-3">
                  <option value="5" selected>⭐⭐⭐⭐⭐ Very safe & clean (5/5)</option>
                  <option value="4">⭐⭐⭐⭐ Safe enough (4/5)</option>
                  <option value="3">⭐⭐⭐ Minor safety concerns (3/5)</option>
                  <option value="2">⭐⭐ Unsafe conditions (2/5)</option>
                  <option value="1">⭐ Hazardous / Neglected (1/5)</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">4. Pay On Time: Are monthly salaries and advances paid punctually?</label>
                <select class="form-control" id="pq-4">
                  <option value="5" selected>⭐⭐⭐⭐⭐ Always on time (by 7th) (5/5)</option>
                  <option value="4">⭐⭐⭐⭐ Usually on time (4/5)</option>
                  <option value="3">⭐⭐⭐ Delayed by a few days (3/5)</option>
                  <option value="2">⭐⭐ Delayed by weeks (2/5)</option>
                  <option value="1">⭐ Highly erratic / Unpaid dues (1/5)</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">5. Growth: Are there opportunities to learn and increase earnings?</label>
                <select class="form-control" id="pq-5">
                  <option value="5">⭐⭐⭐⭐⭐ Great growth opportunities (5/5)</option>
                  <option value="4" selected>⭐⭐⭐⭐ Fair chances to learn (4/5)</option>
                  <option value="3">⭐⭐⭐ Limited scope (3/5)</option>
                  <option value="2">⭐⭐ No growth seen (2/5)</option>
                  <option value="1">⭐ Stagnant dead-end (1/5)</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">6. Would you recommend working here to a friend or family member?</label>
                <select class="form-control" id="pq-6">
                  <option value="5" selected>⭐⭐⭐⭐⭐ Absolutely yes (5/5)</option>
                  <option value="4">⭐⭐⭐⭐ Yes, with small reservations (4/5)</option>
                  <option value="3">⭐⭐⭐ Maybe / Neutral (3/5)</option>
                  <option value="2">⭐⭐ Unlikely (2/5)</option>
                  <option value="1">⭐ Definitely not (1/5)</option>
                </select>
              </div>

              <button class="btn btn-teal welfare-big-btn" style="width: 100%; margin-top: 10px;" onclick="submitPulseVote()">
                ${getT('submitVote')}
              </button>
            </div>
          </div>

          <!-- Owner Aggregates & 5-Response Lock State -->
          <div class="card" id="pulse-owner-view">
            <!-- Rendered by loadPulseSurveys() -->
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;

      loadPulseSurveys();
    }

    function submitPulseVote() {
      const q1 = parseInt(document.getElementById('pq-1')?.value || 4);
      const q2 = parseInt(document.getElementById('pq-2')?.value || 5);
      const q3 = parseInt(document.getElementById('pq-3')?.value || 5);
      const q4 = parseInt(document.getElementById('pq-4')?.value || 5);
      const q5 = parseInt(document.getElementById('pq-5')?.value || 4);
      const q6 = parseInt(document.getElementById('pq-6')?.value || 5);

      // Local storage fallback for offline demo
      let votes = [];
      try {
        votes = JSON.parse(localStorage.getItem('paypilot_pulse_votes') || '[]');
      } catch (e) {}
      votes.push({ q1, q2, q3, q4, q5, q6 });
      localStorage.setItem('paypilot_pulse_votes', JSON.stringify(votes));

      // Try server submit if online
      fetch('/api/welfare/surveys/SURV-202610-DEMO/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q1, q2, q3, q4, q5, q6 })
      }).catch(() => {});

      alert("Thank you! Your response was recorded completely anonymously. No names, IPs, or devices are stored.");
      loadPulseSurveys();
    }

    function loadPulseSurveys() {
      const container = document.getElementById('pulse-owner-view');
      if (!container) return;

      // Check votes count (combining demo votes)
      let localVotes = [];
      try {
        localVotes = JSON.parse(localStorage.getItem('paypilot_pulse_votes') || '[]');
      } catch (e) {}

      const totalCount = 6 + localVotes.length; // Baseline demo has 6 responses

      if (totalCount < 5) {
        container.innerHTML = `
          <h3 style="color: var(--cinema-gold); margin-bottom: 12px;">Team Culture Scorecard</h3>
          <div class="welfare-verdict-box welfare-verdict-amber">
            <h4 style="margin: 0 0 6px 0;">🔒 Anonymous Protection Active</h4>
            <p style="font-size: 14px; margin: 0; line-height: 1.6;">
              <strong>${totalCount} / 5</strong> responses collected so far.<br>
              To protect employee identities, summary scores and averages will only unlock once at least 5 team members have participated.
            </p>
          </div>
        `;
      } else {
        // Unlocked state (>= 5)
        container.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 14px;">
            <h3 style="color: var(--cinema-teal); margin: 0;">Team Culture Scorecard</h3>
            <span class="badge badge-teal">${totalCount} RESPONSES (UNLOCKED ✓)</span>
          </div>

          <div style="background: var(--bg-card-subtle); padding: 18px; border-radius: var(--radius-sm); margin-bottom: 16px; text-align: center;">
            <span style="font-size: 13px; color: var(--cinema-muted);">Overall Workplace Health Score</span>
            <div class="font-mono" style="font-size: 44px; font-weight: 800; color: var(--cinema-gold); margin: 6px 0;">
              88 / 100
            </div>
            <span class="badge badge-teal">Tier A Healthy Environment</span>
          </div>

          <div style="font-size: 13px; line-height: 2;">
            <div style="display: flex; justify-content: space-between;"><span>1. Fair Workload:</span><strong>4.2 / 5.0</strong></div>
            <div style="display: flex; justify-content: space-between;"><span>2. Dignity &amp; Respect:</span><strong>4.7 / 5.0</strong></div>
            <div style="display: flex; justify-content: space-between;"><span>3. Workplace Safety:</span><strong>4.5 / 5.0</strong></div>
            <div style="display: flex; justify-content: space-between;"><span>4. Pay on Time:</span><strong>4.8 / 5.0</strong></div>
            <div style="display: flex; justify-content: space-between;"><span>5. Growth Opportunity:</span><strong>3.8 / 5.0</strong></div>
            <div style="display: flex; justify-content: space-between;"><span>6. Recommend to Friends:</span><strong>4.6 / 5.0</strong></div>
          </div>

          <h4 style="color: var(--cinema-gold); margin: 18px 0 8px 0;">3 Suggested Owner Actions:</h4>
          <div class="welfare-step-box" style="border-color: var(--cinema-gold);">
            1. <strong>Improve Growth Paths:</strong> Skill growth scored lowest (3.8). Consider a semi-annual skill assessment.<br>
            2. <strong>Celebrate Punctuality:</strong> On-time pay scored 4.8. Maintain prompt wage disbursement by 7th.<br>
            3. <strong>Open Quarterly Townhall:</strong> Host a 15-minute informal tea session to discuss workload concerns.
          </div>
        `;
      }
    }

    function createNewPulseSurvey() {
      alert("New monthly survey created! Share this page with team members via WhatsApp or QR code.");
    }

    // =========================================================================
    // 15. SCREEN 8: GIG & FREELANCER INCOME HELPER
    // =========================================================================
    function renderGigIncome(pane) {
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-orange);">🛵 ${getT('gigIncomeName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">Track multi-app earnings, calculate Section 44ADA/44AD presumptive taxes, and print income proof for loans.</p>
            </div>
            <button class="btn-read-aloud" id="btn-read-gig">${getT('readAloud')}</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- Multi-App Income Inputs -->
          <div class="card">
            <h3 style="color: var(--cinema-orange); margin-bottom: 16px;">Annual Receipts &amp; Expenses</h3>
            
            <div class="form-group">
              <label class="form-label">Platform / Sector Type</label>
              <select class="form-control" id="gig-type" onchange="calculateGigIncome()">
                <option value="44ada">Professional / Technical Freelancer (Sec 44ADA - 50% profit)</option>
                <option value="44ad" selected>Delivery / Driver / Retail Goods (Sec 44AD - 6% digital profit)</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Total Annual Gross Receipts (₹)</label>
              <input type="number" class="form-control font-mono" id="gig-gross" value="480000" oninput="calculateGigIncome()">
              <span style="font-size: 11px; color: var(--cinema-muted);">Sum of Swiggy, Zomato, Uber, Urban Company, or direct clients.</span>
            </div>

            <div class="form-group">
              <label class="form-label">Annual Business Expenses (Fuel, Bike, Mobile) (₹)</label>
              <input type="number" class="form-control font-mono" id="gig-expenses" value="95000" oninput="calculateGigIncome()">
            </div>
          </div>

          <!-- Tax Engine & Loan Statement -->
          <div class="card card-glow-orange" id="gig-results-card">
            <!-- Rendered by calculateGigIncome() -->
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;

      document.getElementById('btn-read-gig').onclick = () => {
        readAloudText("Gig income and advance tax breakdown.");
      };

      calculateGigIncome();
    }

    function calculateGigIncome() {
      try {
        const type = document.getElementById('gig-type')?.value || '44ad';
        const gross = parseFloat(document.getElementById('gig-gross')?.value || 0);
        const exp = parseFloat(document.getElementById('gig-expenses')?.value || 0);

        const deemedProfitRate = type === '44ada' ? 0.50 : 0.06;
        const taxableIncome = Math.round(gross * deemedProfitRate);
        const netCashflow = Math.round(gross - exp);

        // Budget 2025 New Regime check: Under ₹12L taxable is ₹0 tax due to 87A rebate!
        let tax = 0;
        if (taxableIncome > 1200000) {
          tax = Math.round((taxableIncome - 1200000) * 0.15 * 1.04);
        }

        const container = document.getElementById('gig-results-card');
        if (!container) return;

        container.innerHTML = `
          <h3 style="color: var(--cinema-teal); margin-bottom: 14px;">Presumptive Tax &amp; Net Take-Home</h3>
          
          <div style="background: var(--bg-card-subtle); padding: 16px; border-radius: var(--radius-sm); margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
              <span>Deemed Taxable Profit (${type === '44ada' ? '50%' : '6%'}):</span>
              <strong class="font-mono">₹${taxableIncome.toLocaleString('en-IN')}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
              <span>Annual Tax Payable (New Regime):</span>
              <strong class="font-mono" style="color:var(--cinema-emerald); font-size: 18px;">₹${tax.toLocaleString('en-IN')}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-top: 1px solid var(--border-subtle); padding-top: 8px;">
              <span>Net Cash Remaining After Expenses:</span>
              <strong class="font-mono" style="color:var(--cinema-gold); font-size: 18px;">₹${netCashflow.toLocaleString('en-IN')}</strong>
            </div>
          </div>

          <h4 style="color: var(--cinema-cream); margin-bottom: 6px;">Statutory Advance Tax Calendar</h4>
          <div style="font-size: 12px; color: var(--cinema-muted); line-height: 1.8; margin-bottom: 16px;">
            • June 15: 15% due (₹${Math.round(tax * 0.15).toLocaleString('en-IN')})<br>
            • Sept 15: 45% due (₹${Math.round(tax * 0.45).toLocaleString('en-IN')})<br>
            • Dec 15: 75% due (₹${Math.round(tax * 0.75).toLocaleString('en-IN')})<br>
            • March 15: 100% due (₹${tax.toLocaleString('en-IN')})
          </div>

          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <button class="btn btn-teal" onclick="printGigCertificate(${gross}, ${netCashflow})">
              📜 Print Income Summary for Bank Loan
            </button>
          </div>
        `;
      } catch (e) {
        console.error('Gig calculation error:', e);
      }
    }

    function printGigCertificate(gross, net) {
      const win = window.open('', '_blank');
      if (!win) { alert("Please allow popups to print certificate."); return; }
      win.document.write(`
        <html>
        <head>
          <title>Freelance & Gig Income Statement</title>
          <style>body { font-family: sans-serif; padding: 40px; line-height: 1.8; color: #111; }</style>
        </head>
        <body>
          <h2 style="border-bottom: 2px solid #222; padding-bottom: 10px;">SELF-EMPLOYED GIG INCOME SUMMARY</h2>
          <p>This statement certifies the annual earnings and operational expenses under the Presumptive Taxation Scheme (Section 44ADA / 44AD of Income Tax Act 1961):</p>
          <table border="1" cellpadding="8" cellspacing="0" style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr><td><strong>Gross Annual Platform Receipts:</strong></td><td>₹${gross.toLocaleString('en-IN')}</td></tr>
            <tr><td><strong>Estimated Net Operational Cashflow:</strong></td><td>₹${net.toLocaleString('en-IN')}</td></tr>
            <tr><td><strong>Statutory Tax Liability (Budget 2025):</strong></td><td>₹0 (Within 87A rebate)</td></tr>
          </table>
          <p>Issued via PayPilot Enterprise for loan evaluation and banking verification.</p>
          <script>window.print();<\/script>
        </body>
        </html>
      `);
      win.document.close();
    }

    // =========================================================================
    // 16. SCREEN 9: MONEY LESSONS & SAVINGS COACH
    // =========================================================================
    const MONEY_LESSONS = [
      { id: 1, title: "1. The 10% First Rule", badge: "Smart Saver", text: "Pay yourself first before paying bills. Setting aside 10% of every payment creates lifelong wealth.", q: "How much should you save first from every payment?", opts: ["0%", "At least 10%", "50%"], ans: 1 },
      { id: 2, title: "2. The 3-6 Month Emergency Fund", badge: "Safety Shield", text: "Keep 3 to 6 months of living expenses in a bank account so unexpected illnesses don't force you into debt.", q: "What is an emergency fund for?", opts: ["Buying luxury items", "Unplanned medical or job emergencies", "Stock trading"], ans: 1 },
      { id: 3, title: "3. Beware of UPI & Phone Scams", badge: "Fraud Shield", text: "Never enter your UPI PIN to receive money! Entering a PIN always sends money OUT of your bank account.", q: "Do you ever need a UPI PIN to receive money?", opts: ["Yes, always", "Never! PIN only sends money out", "Only on Sundays"], ans: 1 },
      { id: 4, title: "4. Health Insurance (Ayushman / ESI)", badge: "Health Guard", text: "Medical expenses are the number 1 cause of family debt in India. Ensure your family has Ayushman or ESI.", q: "What protects families from sudden hospital debts?", opts: ["Lottery tickets", "Ayushman Bharat / Health Insurance", "Personal loan"], ans: 1 },
      { id: 5, title: "5. Good Debt vs Loan Sharks", badge: "Debt Free", text: "Never borrow from lenders who charge daily interest or demand blank cheques. Use formal bank micro-loans.", q: "Which loan is dangerous?", opts: ["Bank loan at 10% p.a.", "Daily collection loan at 200% APR", "Mudra loan at 8%"], ans: 1 },
      { id: 6, title: "6. Mutual Funds & SIP Basics", badge: "Wealth Builder", text: "Starting a ₹500 monthly Systematic Investment Plan (SIP) in an index fund compounds with India's growth.", q: "What is the minimum amount to start an SIP?", opts: ["₹50,000", "₹500", "₹1,00,000"], ans: 1 },
      { id: 7, title: "7. ₹2 Lakh Cover for Just ₹20 (PMSBY)", badge: "Insured Citizen", text: "Pradhan Mantri Suraksha Bima Yojana gives ₹2 Lakh accidental death cover for just ₹20 per year from your bank.", q: "What is the annual cost of PMSBY?", opts: ["₹20 per year", "₹2,000 per year", "₹10,000"], ans: 0 },
      { id: 8, title: "8. Power of Provident Fund (EPF)", badge: "Retirement Ready", text: "Your 12% PF is matched by a 12% employer contribution with guaranteed tax-free government interest.", q: "How much does the employer contribute to your EPF?", opts: ["0%", "12% matching contribution", "1%"], ans: 1 },
      { id: 9, title: "9. Ration Cards & Food Security", badge: "Welfare Champion", text: "National Food Security Act (NFSA) provides subsidized food grains through One Nation One Ration Card.", q: "Can you use your ration card in other states?", opts: ["Yes, via One Nation One Ration Card", "No, only in your village", "Never"], ans: 0 },
      { id: 10, title: "10. Budgeting on Irregular Income", badge: "Budget Master", text: "If your income changes every month, base your fixed expenses on your lowest earning month, saving the rest.", q: "How should gig/daily workers plan expenses?", opts: ["Based on the best month", "Based on the lowest earning month", "Don't budget"], ans: 1 }
    ];

    function renderSavingsCoach(pane) {
      if (!pane) return;
      let lessonsHtml = MONEY_LESSONS.map((ls, idx) => `
        <div class="card" style="margin-bottom: 14px; border-left: 4px solid var(--cinema-gold);">
          <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <h4 style="color: var(--cinema-gold); margin: 0 0 6px 0;">${ls.title}</h4>
            <span class="badge badge-gold" id="badge-lesson-${idx}">🔒 Locked</span>
          </div>
          <p style="font-size: 14px; color: var(--cinema-cream); line-height: 1.6; margin: 6px 0;">${ls.text}</p>
          <div style="background: var(--bg-card-subtle); padding: 12px; border-radius: var(--radius-sm); margin-top: 10px;">
            <strong style="font-size: 13px; color: var(--cinema-teal);">Quick Quiz: ${ls.q}</strong>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px;">
              ${ls.opts.map((opt, oIdx) => `
                <button class="btn btn-glass" style="font-size: 12px; padding: 4px 10px;" onclick="checkLessonQuiz(${idx}, ${oIdx})">
                  ${opt}
                </button>
              `).join('')}
            </div>
            <div id="quiz-msg-${idx}" style="font-size: 12px; margin-top: 6px;"></div>
          </div>
        </div>
      `).join('');

      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-gold);">💡 ${getT('savingsCoachName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">10 simple financial survival lessons and an automated emergency-fund coach.</p>
            </div>
            <button class="btn-read-aloud" id="btn-read-lessons">${getT('readAloud')}</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- 10 Lessons Column -->
          <div>
            <h3 style="color: var(--cinema-cream); margin-bottom: 14px;">10 Essential Financial Lessons</h3>
            ${lessonsHtml}
          </div>

          <!-- Automated Savings Coach Column -->
          <div>
            <div class="card card-glow-gold" style="position: sticky; top: 80px;">
              <h3 style="color: var(--cinema-gold); margin-bottom: 14px;">🎯 Automated Savings Coach</h3>
              
              <div class="form-group">
                <label class="form-label">Monthly Household Income (₹)</label>
                <input type="number" class="form-control font-mono" id="sc-income" value="25000" oninput="calculateSavingsCoach()">
              </div>

              <div class="form-group">
                <label class="form-label">Monthly Living Expenses (₹)</label>
                <input type="number" class="form-control font-mono" id="sc-expenses" value="18000" oninput="calculateSavingsCoach()">
              </div>

              <div class="form-group">
                <label class="form-label">Expected Raise / Festival Bonus (₹)</label>
                <input type="number" class="form-control font-mono" id="sc-raise" value="3000" oninput="calculateSavingsCoach()">
              </div>

              <div id="sc-coach-output" style="background: var(--bg-card-subtle); padding: 16px; border-radius: var(--radius-sm); margin-top: 14px;">
                <!-- Calculated by calculateSavingsCoach() -->
              </div>
            </div>
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;

      document.getElementById('btn-read-lessons').onclick = () => {
        readAloudText("Financial lessons and savings coach suggestions.");
      };

      calculateSavingsCoach();
    }

    function checkLessonQuiz(lIdx, oIdx) {
      const lesson = MONEY_LESSONS[lIdx];
      const msgEl = document.getElementById(`quiz-msg-${lIdx}`);
      const badgeEl = document.getElementById(`badge-lesson-${lIdx}`);
      if (!msgEl || !badgeEl) return;

      if (oIdx === lesson.ans) {
        msgEl.innerHTML = `<span style="color:var(--cinema-emerald);">✓ Correct! Badge Unlocked: <strong>${lesson.badge}</strong> 🏆</span>`;
        badgeEl.innerText = `🏆 ${lesson.badge}`;
        badgeEl.className = 'badge badge-teal';
      } else {
        msgEl.innerHTML = `<span style="color:var(--cinema-crimson);">✗ Try again! Re-read the lesson above.</span>`;
      }
    }

    function calculateSavingsCoach() {
      try {
        const income = parseFloat(document.getElementById('sc-income')?.value || 25000);
        const exp = parseFloat(document.getElementById('sc-expenses')?.value || 18000);
        const raise = parseFloat(document.getElementById('sc-raise')?.value || 0);

        const currentSavings = Math.max(0, income - exp);
        const savingsRate = income > 0 ? Math.round((currentSavings / income) * 100) : 0;

        const emgFund3m = Math.round(exp * 3);
        const emgFund6m = Math.round(exp * 6);
        const monthsTo3m = currentSavings > 0 ? Math.ceil(emgFund3m / currentSavings) : "∞";

        const raiseToSave = Math.round(raise * 0.50); // 50% of raise rule

        const out = document.getElementById('sc-coach-output');
        if (!out) return;

        out.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
            <span>Current Monthly Savings:</span>
            <strong class="font-mono" style="color:var(--cinema-gold); font-size: 20px;">₹${currentSavings.toLocaleString('en-IN')} (${savingsRate}%)</strong>
          </div>
          <div style="font-size: 13px; line-height: 1.8; color: var(--cinema-cream); margin-top: 10px;">
            • <strong>Emergency Fund Target (3 Months):</strong> ₹${emgFund3m.toLocaleString('en-IN')} (Reached in ~${monthsTo3m} months)<br>
            • <strong>Emergency Fund Target (6 Months):</strong> ₹${emgFund6m.toLocaleString('en-IN')}<br>
            • <strong>Raise Allocation Rule:</strong> Save at least <strong>₹${raiseToSave.toLocaleString('en-IN')}</strong> (50%) of your new raise before lifestyle expenses expand.<br>
            • <strong>Recommended Split:</strong> 70% Needs (₹${Math.round(income * 0.7)}), 20% Savings (₹${Math.round(income * 0.2)}), 10% Wants (₹${Math.round(income * 0.1)}).
          </div>
        `;
      } catch (e) {
        console.error('Savings coach error:', e);
      }
    }

    // =========================================================================
    // 17. SCREEN 10: GRIEVANCE HELPER
    // =========================================================================
    function renderGrievanceHelper(pane) {
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-cream);">📢 ${getT('grievanceName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">Generate formal legal notices for unpaid wages or PF fraud, and access official government portals &amp; helplines.</p>
            </div>
            <button class="btn-read-aloud" id="btn-read-grievance">${getT('readAloud')}</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- Dispute Details -->
          <div class="card">
            <h3 style="color: var(--cinema-orange); margin-bottom: 16px;">1. Dispute Details</h3>

            <div class="form-group">
              <label class="form-label">${getT('issueType')}</label>
              <select class="form-control" id="gv-issue" onchange="generateGrievanceNotice()">
                <option value="salary" selected>${getT('unpaidSalary')}</option>
                <option value="termination">${getT('illegalTerm')}</option>
                <option value="pf">${getT('pfFraud')}</option>
                <option value="harassment">${getT('harassment')}</option>
                <option value="maternity">${getT('deniedMaternity')}</option>
              </select>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">${getT('workerName')}</label>
                <input type="text" class="form-control" id="gv-worker" value="Ramesh Kumar" oninput="generateGrievanceNotice()">
              </div>
              <div class="form-group">
                <label class="form-label">${getT('employerName')}</label>
                <input type="text" class="form-control" id="gv-employer" value="Sharma Enterprises &amp; Logistics" oninput="generateGrievanceNotice()">
              </div>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">${getT('joiningDate')}</label>
                <input type="date" class="form-control font-mono" id="gv-date" value="2025-01-15" onchange="generateGrievanceNotice()">
              </div>
              <div class="form-group">
                <label class="form-label">${getT('unpaidAmount')}</label>
                <input type="number" class="form-control font-mono" id="gv-amount" value="28500" oninput="generateGrievanceNotice()">
              </div>
            </div>

            <h4 style="color: var(--cinema-gold); margin: 20px 0 10px 0;">${getT('proofToKeep')}:</h4>
            <div class="welfare-checklist-item"><input type="checkbox" checked> Bank account statements showing salary credits or missing deposits.</div>
            <div class="welfare-checklist-item"><input type="checkbox" checked> WhatsApp chats, SMS, or emails discussing work, shifts, and dues.</div>
            <div class="welfare-checklist-item"><input type="checkbox" checked> Photos of register attendance, ID card, or uniform badge.</div>
            <div class="welfare-checklist-item"><input type="checkbox" checked> Contact details of 2 co-workers who can testify to your presence.</div>
          </div>

          <!-- Generated Legal Notice & Helplines -->
          <div class="card card-glow-orange">
            <h3 style="color: var(--cinema-gold); margin-bottom: 12px;">2. Legal Demand Notice Template</h3>
            <textarea class="form-control" id="gv-notice-text" rows="12" style="font-size: 13px; line-height: 1.6; margin-bottom: 14px; font-family: monospace;" readonly></textarea>

            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
              <button class="btn btn-teal" onclick="copyWelfareText(document.getElementById('gv-notice-text').value, this)">
                ${getT('copyText')}
              </button>
              <button class="btn btn-orange" onclick="printGrievanceNotice()">
                🖨️ Print Formal Letter
              </button>
            </div>

            <h4 style="color: var(--cinema-cream); margin-bottom: 8px;">${getT('helplineTitle')}:</h4>
            <div style="font-size: 13px; line-height: 1.8; color: var(--cinema-muted);">
              • <strong>National Labour Helpline:</strong> 14434 / 1800-180-1111 (Toll Free)<br>
              • <strong>SAMADHAAN Portal:</strong> samadhaan.labour.gov.in (Online conciliation)<br>
              • <strong>EPFO Grievance (EPFiGMS):</strong> epfigms.gov.in<br>
              • <strong>Women Emergency / POSH:</strong> 1091 / 112<br>
              • <strong>Cyber Crime Helpline:</strong> 1930 / cybercrime.gov.in
            </div>
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;

      document.getElementById('btn-read-grievance').onclick = () => {
        readAloudText("Grievance demand notice generated.");
      };

      generateGrievanceNotice();
    }

    function generateGrievanceNotice() {
      try {
        const issue = document.getElementById('gv-issue')?.value || 'salary';
        const worker = document.getElementById('gv-worker')?.value || 'The Employee';
        const employer = document.getElementById('gv-employer')?.value || 'The Management';
        const amount = parseFloat(document.getElementById('gv-amount')?.value || 0);
        const joinDate = document.getElementById('gv-date')?.value || '2025-01-15';

        let actCitation = "Section 15 of the Payment of Wages Act, 1936";
        let issueText = `unpaid wages totaling ₹${amount.toLocaleString('en-IN')} for services rendered`;

        if (issue === 'termination') {
          actCitation = "Section 25F of the Industrial Disputes Act, 1947";
          issueText = `illegal termination without statutory one-month written notice or retrenchment compensation`;
        } else if (issue === 'pf') {
          actCitation = "Section 14 of the Employees' Provident Funds and Miscellaneous Provisions Act, 1952";
          issueText = `unlawful non-remittance of deducted Provident Fund dues into my universal UAN account`;
        } else if (issue === 'harassment') {
          actCitation = "Sexual Harassment of Women at Workplace (POSH) Act, 2013";
          issueText = `workplace harassment and hostile working environment in violation of statutory safety mandates`;
        } else if (issue === 'maternity') {
          actCitation = "Section 12 of the Maternity Benefit Act, 1961";
          issueText = `unlawful denial of 26 weeks paid maternity leave and statutory medical bonus`;
        }

        const notice = `DATE: ${new Date().toLocaleDateString('en-IN')}\n\nTO:\nThe Management,\n${employer}\n\nFROM:\n${worker}\n(Date of Joining: ${joinDate})\n\nSUBJECT: FORMAL DEMAND NOTICE REGARDING ${issue.toUpperCase()} UNDER STATUTORY LABOUR LAWS\n\nRespected Sir/Madam,\n\nI am writing to formally bring to your attention the matter of ${issueText}.\n\nUnder ${actCitation}, every worker is legally entitled to timely remuneration and statutory protections without arbitrary withholding or unfair practices.\n\nDespite repeated verbal communications, the matter remains unresolved. Therefore, I formally request you to kindly disburse the outstanding dues of ₹${amount.toLocaleString('en-IN')} / rectify the matter within 7 (seven) days of receipt of this notice.\n\nShould the matter not be resolved amicably within this period, I shall be constrained to submit a formal complaint before the conciliation officer at the Labour Commissioner's Office and the SAMADHAAN portal (samadhaan.labour.gov.in) for statutory redressal.\n\nThanking you,\n\nYours sincerely,\n${worker}`;

        const ta = document.getElementById('gv-notice-text');
        if (ta) ta.value = notice;
      } catch (e) {
        console.error('Grievance generation error:', e);
      }
    }

    function printGrievanceNotice() {
      const text = document.getElementById('gv-notice-text')?.value || '';
      const win = window.open('', '_blank');
      if (!win) { alert("Please allow popups to print notice."); return; }
      win.document.write(`
        <html>
        <head>
          <title>Legal Demand Notice</title>
          <style>body { font-family: monospace; white-space: pre-wrap; padding: 40px; font-size: 14px; line-height: 1.6; color: #111; }</style>
        </head>
        <body>${escapeHtml(text)}<script>window.print();<\/script></body>
        </html>
      `);
      win.document.close();
    }

    // =========================================================================
    // 18. SCREEN 11: ADMIN RULES & DATA EDITOR
    // =========================================================================
    function renderWelfareAdminRules(pane) {
      if (!pane) return;
      const r = window.welfareRules || DEFAULT_WELFARE_RULES;
      pane.innerHTML = `
        <div style="margin-bottom: 20px;">
          <button class="btn btn-glass" style="margin-bottom: 12px;" onclick="showScreen('welfare-hub')">${getT('backToHub')}</button>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
              <h2 style="color: var(--cinema-gold);">⚙️ ${getT('adminRulesName')}</h2>
              <p style="color: var(--cinema-muted); font-size: 14px;">Edit statutory minimum wages, benefit thresholds, and scheme database with an automatic audit trail.</p>
            </div>
            <button class="btn btn-orange" onclick="saveWelfareAdminRules()">💾 Save All Rules to Backend</button>
          </div>
        </div>

        <div class="grid-2">
          <!-- Metadata Card -->
          <div class="card">
            <h3 style="color: var(--cinema-gold); margin-bottom: 14px;">Attribution &amp; Gazettes</h3>
            <div class="form-group">
              <label class="form-label">Rules Last Updated Date</label>
              <input type="date" class="form-control font-mono" id="adm-last-updated" value="${r.lastUpdated || '2026-10-01'}">
            </div>
            <div class="form-group">
              <label class="form-label">Official Source Name</label>
              <input type="text" class="form-control" id="adm-source" value="${escapeHtml(r.source || 'Ministry of Labour & Employment')}">
            </div>
          </div>

          <!-- Social Security Thresholds -->
          <div class="card">
            <h3 style="color: var(--cinema-teal); margin-bottom: 14px;">Social Security Limits</h3>
            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">PF Wage Ceiling (₹)</label>
                <input type="number" class="form-control font-mono" id="adm-pf-wage" value="${r.benefitThresholds?.pfWageLimit || 15000}">
              </div>
              <div class="form-group">
                <label class="form-label">ESI Wage Ceiling (₹)</label>
                <input type="number" class="form-control font-mono" id="adm-esi-wage" value="${r.benefitThresholds?.esiWageLimit || 21000}">
              </div>
            </div>
            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Gratuity Service (Years)</label>
                <input type="number" class="form-control font-mono" id="adm-grat-years" value="${r.benefitThresholds?.gratuityYears || 5}">
              </div>
              <div class="form-group">
                <label class="form-label">Overtime Multiplier</label>
                <input type="number" class="form-control font-mono" id="adm-ot-mult" value="${r.benefitThresholds?.overtimeMultiplier || 2.0}">
              </div>
            </div>
          </div>
        </div>

        <!-- State Minimum Wages Table -->
        <div class="card" style="margin-top: 20px;">
          <h3 style="color: var(--cinema-orange); margin-bottom: 14px;">State Minimum Wages (Monthly ₹ Basis)</h3>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>State</th>
                  <th>Unskilled</th>
                  <th>Semi-Skilled</th>
                  <th>Skilled</th>
                  <th>Highly Skilled</th>
                </tr>
              </thead>
              <tbody id="adm-wages-tbody">
                ${Object.keys(r.minimumWages || {}).map(st => `
                  <tr>
                    <td><strong>${st}</strong></td>
                    <td><input type="number" class="form-control font-mono" style="padding:4px 8px; width:110px;" id="adm-wage-${st}-unskilled" value="${r.minimumWages[st].unskilledMonthly}"></td>
                    <td><input type="number" class="form-control font-mono" style="padding:4px 8px; width:110px;" id="adm-wage-${st}-semiskilled" value="${r.minimumWages[st].semiskilledMonthly}"></td>
                    <td><input type="number" class="form-control font-mono" style="padding:4px 8px; width:110px;" id="adm-wage-${st}-skilled" value="${r.minimumWages[st].skilledMonthly}"></td>
                    <td><input type="number" class="form-control font-mono" style="padding:4px 8px; width:110px;" id="adm-wage-${st}-highlySkilled" value="${r.minimumWages[st].highlySkilledMonthly}"></td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>

        ${getLegalAttributionHtml()}
      `;
    }

    function saveWelfareAdminRules() {
      const r = window.welfareRules || DEFAULT_WELFARE_RULES;
      r.lastUpdated = document.getElementById('adm-last-updated')?.value || '2026-10-01';
      r.source = document.getElementById('adm-source')?.value || 'Ministry of Labour & Employment';
      
      if (!r.benefitThresholds) r.benefitThresholds = {};
      r.benefitThresholds.pfWageLimit = parseFloat(document.getElementById('adm-pf-wage')?.value || 15000);
      r.benefitThresholds.esiWageLimit = parseFloat(document.getElementById('adm-esi-wage')?.value || 21000);
      r.benefitThresholds.gratuityYears = parseFloat(document.getElementById('adm-grat-years')?.value || 5);
      r.benefitThresholds.overtimeMultiplier = parseFloat(document.getElementById('adm-ot-mult')?.value || 2.0);

      // Save wages
      Object.keys(r.minimumWages || {}).forEach(st => {
        const u = parseFloat(document.getElementById(`adm-wage-${st}-unskilled`)?.value || r.minimumWages[st].unskilledMonthly);
        const s = parseFloat(document.getElementById(`adm-wage-${st}-semiskilled`)?.value || r.minimumWages[st].semiskilledMonthly);
        const k = parseFloat(document.getElementById(`adm-wage-${st}-skilled`)?.value || r.minimumWages[st].skilledMonthly);
        const h = parseFloat(document.getElementById(`adm-wage-${st}-highlySkilled`)?.value || r.minimumWages[st].highlySkilledMonthly);
        r.minimumWages[st].unskilledMonthly = u;
        r.minimumWages[st].unskilledDaily = Math.round(u / 26);
        r.minimumWages[st].semiskilledMonthly = s;
        r.minimumWages[st].semiskilledDaily = Math.round(s / 26);
        r.minimumWages[st].skilledMonthly = k;
        r.minimumWages[st].skilledDaily = Math.round(k / 26);
        r.minimumWages[st].highlySkilledMonthly = h;
        r.minimumWages[st].highlySkilledDaily = Math.round(h / 26);
      });

      // Try PUT /api/welfare/rules
      fetch('/api/welfare/rules', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(r)
      }).then(res => {
        if (res.ok) alert("Welfare rules successfully updated on backend and recorded in audit log!");
        else alert("Saved in local browser state. (Sign in as Admin to persist to server data file).");
      }).catch(() => {
        alert("Saved in local browser memory (offline mode).");
      });
    }

    // =========================================================================
    // 19. MASTER ROUTER INTEGRATION & BINDINGS
    // =========================================================================
    (function registerWelfareScreens() {
      const welfareMap = {
        'welfare-hub': renderWelfareHub,
        'welfare-fair-pay': renderFairPay,
        'welfare-ledger': renderWelfareLedger,
        'welfare-benefits': renderBenefitsFinder,
        'welfare-schemes': renderSchemeMatcher,
        'welfare-loan-trap': renderLoanTrap,
        'welfare-women-family': renderWomenFamily,
        'welfare-pulse': renderWorkCulturePulse,
        'welfare-gig-income': renderGigIncome,
        'welfare-savings-coach': renderSavingsCoach,
        'welfare-grievance': renderGrievanceHelper,
        'welfare-admin-rules': renderWelfareAdminRules,

        // Aliases
        'welfare': renderWelfareHub,
        'fair-pay': renderFairPay,
        'ledger': renderWelfareLedger,
        'benefits': renderBenefitsFinder,
        'schemes': renderSchemeMatcher,
        'loan-trap': renderLoanTrap,
        'women-family': renderWomenFamily,
        'pulse': renderWorkCulturePulse,
        'gig-income': renderGigIncome,
        'savings-coach': renderSavingsCoach,
        'grievance': renderGrievanceHelper,
        'welfare-rules': renderWelfareAdminRules
      };

      window.welfareScreensMap = welfareMap;
      window.screens = window.screens || {};
      Object.assign(window.screens, welfareMap);
    })();
