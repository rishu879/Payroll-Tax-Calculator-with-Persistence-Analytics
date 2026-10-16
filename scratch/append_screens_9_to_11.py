# -*- coding: utf-8 -*-
with open("scratch/welfare_module.js", "a", encoding="utf-8") as f:
    f.write(r'''
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
''')

print("All screens 9 to 11 and router registration written successfully!")
