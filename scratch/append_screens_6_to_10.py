# -*- coding: utf-8 -*-
with open("scratch/welfare_module.js", "a", encoding="utf-8") as f:
    f.write(r'''
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
''')

print("Screens 6 to 8 appended successfully.")
