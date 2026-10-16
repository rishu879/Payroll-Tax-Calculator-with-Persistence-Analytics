# -*- coding: utf-8 -*-
with open("scratch/welfare_module.js", "a", encoding="utf-8") as f:
    f.write(r'''
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
''')

print("Screens 2 to 5 appended successfully.")
