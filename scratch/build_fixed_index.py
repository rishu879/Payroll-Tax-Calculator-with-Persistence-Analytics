# scratch/build_fixed_index.py
import re, os

with open('index.html.bak', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Sidebar Nav Items with data-screen
sidebar_pattern = r'(<aside id="sidebar-dock">)(.*?)(</aside>)'
def update_sidebar(m):
    prefix = m.group(1)
    body = m.group(2)
    suffix = m.group(3)
    
    # Replace onclick="switchTab('xyz')" with data-screen="xyz" onclick="showScreen('xyz')"
    def repl_item(im):
        full_tag = im.group(0)
        # extract id
        id_match = re.search(r"switchTab\(['\"]([^'\"]+)['\"]\)", full_tag)
        if id_match:
            screen_id = id_match.group(1)
            # check if data-screen already present
            if 'data-screen=' not in full_tag:
                full_tag = re.sub(r'class="nav-item([^"]*)"', f'class="nav-item\\1" data-screen="{screen_id}"', full_tag)
            full_tag = full_tag.replace(f"switchTab('{screen_id}')", f"showScreen('{screen_id}')")
        return full_tag

    new_body = re.sub(r'<a[^>]+class="nav-item[^>]+>.*?</a>', repl_item, body)
    return prefix + new_body + suffix

html = re.sub(sidebar_pattern, update_sidebar, html, flags=re.DOTALL)

# 2. Add missing panes to main-content before </section>
missing_panes = """
      <!-- VIEW: PAYSLIP TIMELINE -->
      <div id="pane-payslip-timeline" class="view-pane"></div>

      <!-- VIEW: TAX CHECKLIST -->
      <div id="pane-tax-checklist" class="view-pane"></div>

      <!-- VIEW: CASH CALENDAR -->
      <div id="pane-cashflow-cal" class="view-pane"></div>
"""

if 'id="pane-payslip-timeline"' not in html:
    html = html.replace('</section>', missing_panes + '\n    </section>', 1)

print("Sidebar updated and missing panes injected.")

# 3. Create the router and render functions JavaScript module
router_js = """
    /* =========================================================================
       UNIFIED ROUTER & DYNAMIC SCREENS SYSTEM (PAYPILOT SUITE)
       ========================================================================= */

    // Safe LocalStorage helpers
    function safeStorageGet(key, defVal = null) {
      try {
        const val = localStorage.getItem(key);
        return val ? JSON.parse(val) : defVal;
      } catch (e) {
        console.warn('[Storage] Read error for key', key, e);
        return defVal;
      }
    }

    function safeStorageSet(key, val) {
      try {
        localStorage.setItem(key, JSON.stringify(val));
      } catch (e) {
        console.warn('[Storage] Write error for key', key, e);
      }
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    // -------------------------------------------------------------------------
    // 1. RAISE SLIDER SCREEN
    // -------------------------------------------------------------------------
    function renderRaise(pane) {
      if (!pane) pane = document.getElementById('pane-what-if-raise');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">📈</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">SALARY SLIDER // "WHAT IF I GET A RAISE?"</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Simulate an increment and see your real post-tax monthly take-home bump.</p>
        </div>

        <div class="card card-glow-orange" style="margin-bottom:24px;">
          <div class="grid-2" style="margin-bottom: 20px; gap: 20px;">
            <div>
              <label class="form-label">Current Monthly Gross Pay (₹)</label>
              <input type="number" id="raise-base-monthly" class="form-control font-mono" value="125000" min="10000" step="5000" style="font-size: 18px;" oninput="updateRaiseCalculations()">
              <span style="font-size:11px; color:var(--cinema-muted);">Annual CTC: <span id="raise-annual-ctc" class="font-mono" style="color:var(--cinema-gold);">₹15,00,000</span></span>
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <label class="form-label">Hypothetical Raise Percentage</label>
                <span class="font-mono" style="font-size: 26px; font-weight: 700; color: var(--cinema-orange);" id="raise-pct-display">15%</span>
              </div>
              <input type="range" id="raise-slider-range" min="0" max="50" step="1" value="15" style="width: 100%; height: 8px; margin-top: 12px; accent-color: var(--cinema-orange); cursor: pointer;" oninput="updateRaiseCalculations()">
              <div style="display:flex; justify-content:space-between; font-size:11px; color:var(--cinema-muted);">
                <span>0% (No change)</span><span>15%</span><span>30%</span><span>50% (Max)</span>
              </div>
            </div>
          </div>

          <div class="grid-3" style="text-align: center; gap: 16px;">
            <div style="background: var(--bg-card-subtle); padding: 16px; border-radius: var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600; letter-spacing:0.5px;">NEW MONTHLY TAKE-HOME</span>
              <div class="font-mono money-val" style="font-size: 24px; color: var(--cinema-teal); font-weight: 700; margin: 6px 0;" id="raise-new-takehome">₹0</div>
              <span style="font-size: 12px; color: var(--cinema-emerald); font-weight:600;" id="raise-extra-takehome-badge">+₹0 / mo</span>
            </div>
            <div style="background: var(--bg-card-subtle); padding: 16px; border-radius: var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600; letter-spacing:0.5px;">EXTRA TAX PER MONTH</span>
              <div class="font-mono money-val" style="font-size: 24px; color: var(--cinema-crimson); font-weight: 700; margin: 6px 0;" id="raise-extra-tax">₹0</div>
              <span style="font-size: 11px; color: var(--cinema-muted);" id="raise-annual-tax-delta">+₹0 / year</span>
            </div>
            <div style="background: var(--bg-card-subtle); padding: 16px; border-radius: var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600; letter-spacing:0.5px;">REAL RUPEES IN POCKET</span>
              <div class="font-mono" style="font-size: 24px; color: var(--cinema-gold); font-weight: 700; margin: 6px 0;" id="raise-pocket-rate">₹0 per ₹100</div>
              <span style="font-size: 11px; color: var(--cinema-muted);">Increment retention</span>
            </div>
          </div>
        </div>
      `;
      updateRaiseCalculations();
    }

    function updateRaiseCalculations() {
      try {
        const baseEl = document.getElementById('raise-base-monthly');
        const sliderEl = document.getElementById('raise-slider-range');
        if (!baseEl || !sliderEl) return;

        const baseMonthly = Math.max(0, parseFloat(baseEl.value) || 0);
        const raisePct = parseFloat(sliderEl.value) || 0;

        const pctDisp = document.getElementById('raise-pct-display');
        if (pctDisp) pctDisp.textContent = raisePct + '%';

        const annCtcDisp = document.getElementById('raise-annual-ctc');
        if (annCtcDisp) annCtcDisp.textContent = formatInr(baseMonthly * 12);

        const extraGrossMonthly = baseMonthly * (raisePct / 100);
        const newMonthlyGross = baseMonthly + extraGrossMonthly;

        const oldAnnual = baseMonthly * 12;
        const newAnnual = newMonthlyGross * 12;

        const oldTaxRes = computeBudget2025Tax(oldAnnual);
        const newTaxRes = computeBudget2025Tax(newAnnual);

        const oldAnnualTax = oldTaxRes.newRegime.totalTax;
        const newAnnualTax = newTaxRes.newRegime.totalTax;

        // PF 12% on 40% basic capped at 1800, PT 200
        const oldPf = Math.min(baseMonthly * 0.40 * 0.12, 1800);
        const newPf = Math.min(newMonthlyGross * 0.40 * 0.12, 1800);
        const pt = 200;

        const oldTakehome = Math.max(0, baseMonthly - (oldAnnualTax / 12) - oldPf - pt);
        const newTakehome = Math.max(0, newMonthlyGross - (newAnnualTax / 12) - newPf - pt);

        const extraTakehome = Math.max(0, newTakehome - oldTakehome);
        const extraTaxMonthly = Math.max(0, (newAnnualTax - oldAnnualTax) / 12);

        const pocketRate = extraGrossMonthly > 0 ? Math.round((extraTakehome / extraGrossMonthly) * 100) : 100;

        const newThEl = document.getElementById('raise-new-takehome');
        if (newThEl) newThEl.textContent = formatInr(newTakehome);

        const badgeEl = document.getElementById('raise-extra-takehome-badge');
        if (badgeEl) badgeEl.textContent = `+${formatInr(extraTakehome)} / mo (${raisePct}% increment)`;

        const extraTaxEl = document.getElementById('raise-extra-tax');
        if (extraTaxEl) extraTaxEl.textContent = formatInr(extraTaxMonthly);

        const annTaxDeltaEl = document.getElementById('raise-annual-tax-delta');
        if (annTaxDeltaEl) annTaxDeltaEl.textContent = `+${formatInr(newAnnualTax - oldAnnualTax)} / year`;

        const pocketEl = document.getElementById('raise-pocket-rate');
        if (pocketEl) pocketEl.textContent = `₹${pocketRate} per ₹100`;
      } catch (err) {
        console.error('[RaiseSlider] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 2. CTC GOAL SOLVER SCREEN (REVERSE CTC)
    // -------------------------------------------------------------------------
    function renderGoal(pane) {
      if (!pane) pane = document.getElementById('pane-goal-solver');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">🎯</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">TAKE-HOME GOAL SOLVER (REVERSE CTC)</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Enter the exact monthly in-hand cash you want in your bank account, and solve for the required CTC.</p>
        </div>

        <div class="card card-glow-teal" style="margin-bottom:24px;">
          <div class="grid-2" style="gap:20px; align-items:flex-end; margin-bottom:20px;">
            <div>
              <label class="form-label">Wanted Monthly In-Hand Cash (₹)</label>
              <input type="number" id="goal-inhand-input" class="form-control font-mono" value="100000" min="10000" step="5000" style="font-size:22px; color:var(--cinema-teal);" oninput="solveGoalCalculations()">
              <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
                <button class="btn btn-sm btn-subtle" onclick="setGoalPreset(50000)">₹50k</button>
                <button class="btn btn-sm btn-subtle" onclick="setGoalPreset(75000)">₹75k</button>
                <button class="btn btn-sm btn-subtle active" onclick="setGoalPreset(100000)">₹1 Lakh</button>
                <button class="btn btn-sm btn-subtle" onclick="setGoalPreset(150000)">₹1.5 Lakh</button>
                <button class="btn btn-sm btn-subtle" onclick="setGoalPreset(200000)">₹2 Lakh</button>
              </div>
            </div>
            <div>
              <label class="form-label">Tax Regime</label>
              <select id="goal-regime-select" class="form-control" onchange="solveGoalCalculations()" style="font-size:15px;">
                <option value="new" selected>New Regime (Budget 2025-26 Default)</option>
                <option value="old">Old Regime (Standard ₹1.75L Deductions)</option>
              </select>
              <span style="font-size:11px; color:var(--cinema-muted); display:block; margin-top:6px;">Includes standard deduction ₹75k (New) / ₹50k (Old), EPF &amp; PT deductions.</span>
            </div>
          </div>

          <div class="grid-3" style="text-align:center; gap:16px;">
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-film);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">REQUIRED ANNUAL CTC</span>
              <div class="font-mono money-val" style="font-size:26px; color:var(--cinema-orange); font-weight:700; margin:6px 0;" id="goal-result-ctc">₹0</div>
              <span style="font-size:12px; color:var(--cinema-gold);" id="goal-lakhs-label">₹0 Lakhs / year</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">REQUIRED MONTHLY GROSS</span>
              <div class="font-mono money-val" style="font-size:24px; color:var(--cinema-cream); font-weight:700; margin:6px 0;" id="goal-result-gross">₹0</div>
              <span style="font-size:11px; color:var(--cinema-muted);">Monthly payroll gross</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">ESTIMATED MONTHLY TAX (TDS)</span>
              <div class="font-mono money-val" style="font-size:24px; color:var(--cinema-crimson); font-weight:700; margin:6px 0;" id="goal-result-tax">₹0</div>
              <span style="font-size:11px; color:var(--cinema-muted);" id="goal-tax-rate-label">Effective tax rate: 0%</span>
            </div>
          </div>
        </div>
      `;
      solveGoalCalculations();
    }

    function setGoalPreset(amount) {
      const input = document.getElementById('goal-inhand-input');
      if (input) {
        input.value = amount;
        solveGoalCalculations();
      }
    }

    function solveGoalCalculations() {
      try {
        const inhandEl = document.getElementById('goal-inhand-input');
        const regimeEl = document.getElementById('goal-regime-select');
        if (!inhandEl) return;

        const targetNet = Math.max(1000, parseFloat(inhandEl.value) || 0);
        const isOld = regimeEl && regimeEl.value === 'old';

        // Solver: Binary search between targetNet * 12 and targetNet * 24
        let low = targetNet * 12;
        let high = targetNet * 24 + 500000;
        let bestCtc = low;

        for (let iter = 0; iter < 40; iter++) {
          const mid = (low + high) / 2;
          const monthlyGross = mid / 12;
          const pf = Math.min(monthlyGross * 0.40 * 0.12, 1800);
          const pt = 200;

          const taxRes = computeBudget2025Tax(mid, isOld ? 175000 : 0);
          const annualTax = isOld ? taxRes.oldRegime.totalTax : taxRes.newRegime.totalTax;
          const monthlyNet = monthlyGross - (annualTax / 12) - pf - pt;

          if (monthlyNet < targetNet) {
            low = mid;
          } else {
            high = mid;
            bestCtc = mid;
          }
        }

        const requiredCtc = Math.round(bestCtc);
        const requiredGross = Math.round(requiredCtc / 12);
        const taxRes = computeBudget2025Tax(requiredCtc, isOld ? 175000 : 0);
        const annualTax = isOld ? taxRes.oldRegime.totalTax : taxRes.newRegime.totalTax;
        const monthlyTax = Math.round(annualTax / 12);
        const effTaxRate = requiredCtc > 0 ? ((annualTax / requiredCtc) * 100).toFixed(1) : 0;

        const ctcEl = document.getElementById('goal-result-ctc');
        if (ctcEl) ctcEl.textContent = formatInr(requiredCtc);

        const lakhsEl = document.getElementById('goal-lakhs-label');
        if (lakhsEl) lakhsEl.textContent = `₹${(requiredCtc / 100000).toFixed(2)} Lakhs / year`;

        const grossEl = document.getElementById('goal-result-gross');
        if (grossEl) grossEl.textContent = formatInr(requiredGross);

        const taxEl = document.getElementById('goal-result-tax');
        if (taxEl) taxEl.textContent = formatInr(monthlyTax);

        const rateEl = document.getElementById('goal-tax-rate-label');
        if (rateEl) rateEl.textContent = `Annual Tax: ${formatInr(annualTax)} (${effTaxRate}%)`;
      } catch (err) {
        console.error('[CtcGoalSolver] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 3. OFFER COMPARE SCREEN
    // -------------------------------------------------------------------------
    function renderOfferCompare(pane) {
      if (!pane) pane = document.getElementById('pane-offer-compare');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">⚖️</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">JOB OFFER COMPARISON MATRIX</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Put two competing compensation packages side-by-side to find the real in-pocket winner.</p>
        </div>

        <div id="offer-winner-banner" style="background:linear-gradient(90deg, rgba(255,138,61,0.2), rgba(45,212,191,0.2)); border:1px solid var(--cinema-orange); border-radius:var(--radius-md); padding:16px 20px; margin-bottom:24px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <span style="font-size:12px; color:var(--cinema-gold); font-weight:700; letter-spacing:0.5px;">RECOMMENDED VERDICT</span>
            <h3 style="color:var(--cinema-cream); margin-top:2px;" id="offer-winner-title">🏆 Calculating Winner...</h3>
          </div>
          <div class="badge badge-teal" style="font-size:14px; padding:6px 14px;" id="offer-delta-badge">+₹0 / mo diff</div>
        </div>

        <div class="grid-2" style="gap:24px;">
          <!-- Offer A -->
          <div class="card card-glow-teal">
            <h3 style="color:var(--cinema-teal); margin-bottom:16px;">OFFER A (Current / Company A)</h3>
            <div style="margin-bottom:12px;">
              <label class="form-label">Company / Role</label>
              <input type="text" id="offer-a-name" class="form-control" value="TechCorp (Current)" oninput="updateOfferCalculations()">
            </div>
            <div style="margin-bottom:12px;">
              <label class="form-label">Annual Fixed CTC (₹)</label>
              <input type="number" id="offer-a-fixed" class="form-control font-mono" value="1500000" step="50000" oninput="updateOfferCalculations()">
            </div>
            <div style="margin-bottom:12px;">
              <label class="form-label">Annual Variable / Performance Bonus (₹)</label>
              <input type="number" id="offer-a-bonus" class="form-control font-mono" value="150000" step="10000" oninput="updateOfferCalculations()">
            </div>
            <div style="margin-bottom:16px;">
              <label class="form-label">Monthly Allowances / Perks (Food, Cab, Health) (₹)</label>
              <input type="number" id="offer-a-perks" class="form-control font-mono" value="5000" step="1000" oninput="updateOfferCalculations()">
            </div>

            <div style="background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="font-size:12px; color:var(--cinema-muted);">Guaranteed Monthly In-Hand:</span>
                <strong class="font-mono" style="color:var(--cinema-teal);" id="offer-a-inhand">₹0</strong>
              </div>
              <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="font-size:12px; color:var(--cinema-muted);">Annual Tax (New Regime):</span>
                <span class="font-mono" style="color:var(--cinema-crimson);" id="offer-a-tax">₹0</span>
              </div>
              <div style="display:flex; justify-content:space-between;">
                <span style="font-size:12px; color:var(--cinema-muted);">Total Potential Annual Comp:</span>
                <strong class="font-mono" style="color:var(--cinema-gold);" id="offer-a-total">₹0</strong>
              </div>
            </div>
          </div>

          <!-- Offer B -->
          <div class="card card-glow-orange">
            <h3 style="color:var(--cinema-orange); margin-bottom:16px;">OFFER B (Competing Offer)</h3>
            <div style="margin-bottom:12px;">
              <label class="form-label">Company / Role</label>
              <input type="text" id="offer-b-name" class="form-control" value="GrowthLabs (Offer)" oninput="updateOfferCalculations()">
            </div>
            <div style="margin-bottom:12px;">
              <label class="form-label">Annual Fixed CTC (₹)</label>
              <input type="number" id="offer-b-fixed" class="form-control font-mono" value="1800000" step="50000" oninput="updateOfferCalculations()">
            </div>
            <div style="margin-bottom:12px;">
              <label class="form-label">Annual Variable / Performance Bonus (₹)</label>
              <input type="number" id="offer-b-bonus" class="form-control font-mono" value="200000" step="10000" oninput="updateOfferCalculations()">
            </div>
            <div style="margin-bottom:16px;">
              <label class="form-label">Monthly Allowances / Perks (Food, Cab, Health) (₹)</label>
              <input type="number" id="offer-b-perks" class="form-control font-mono" value="8000" step="1000" oninput="updateOfferCalculations()">
            </div>

            <div style="background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="font-size:12px; color:var(--cinema-muted);">Guaranteed Monthly In-Hand:</span>
                <strong class="font-mono" style="color:var(--cinema-orange);" id="offer-b-inhand">₹0</strong>
              </div>
              <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="font-size:12px; color:var(--cinema-muted);">Annual Tax (New Regime):</span>
                <span class="font-mono" style="color:var(--cinema-crimson);" id="offer-b-tax">₹0</span>
              </div>
              <div style="display:flex; justify-content:space-between;">
                <span style="font-size:12px; color:var(--cinema-muted);">Total Potential Annual Comp:</span>
                <strong class="font-mono" style="color:var(--cinema-gold);" id="offer-b-total">₹0</strong>
              </div>
            </div>
          </div>
        </div>
      `;
      updateOfferCalculations();
    }

    function updateOfferCalculations() {
      try {
        const aFixed = parseFloat(document.getElementById('offer-a-fixed')?.value) || 0;
        const aBonus = parseFloat(document.getElementById('offer-a-bonus')?.value) || 0;
        const aPerks = parseFloat(document.getElementById('offer-a-perks')?.value) || 0;
        const aName = document.getElementById('offer-a-name')?.value || 'Offer A';

        const bFixed = parseFloat(document.getElementById('offer-b-fixed')?.value) || 0;
        const bBonus = parseFloat(document.getElementById('offer-b-bonus')?.value) || 0;
        const bPerks = parseFloat(document.getElementById('offer-b-perks')?.value) || 0;
        const bName = document.getElementById('offer-b-name')?.value || 'Offer B';

        // Offer A calculations
        const aTax = computeBudget2025Tax(aFixed).newRegime.totalTax;
        const aPf = Math.min((aFixed / 12) * 0.40 * 0.12, 1800);
        const aMonthlyNet = Math.max(0, (aFixed / 12) - (aTax / 12) - aPf - 200 + aPerks);
        const aTotalComp = aFixed + aBonus + (aPerks * 12);

        // Offer B calculations
        const bTax = computeBudget2025Tax(bFixed).newRegime.totalTax;
        const bPf = Math.min((bFixed / 12) * 0.40 * 0.12, 1800);
        const bMonthlyNet = Math.max(0, (bFixed / 12) - (bTax / 12) - bPf - 200 + bPerks);
        const bTotalComp = bFixed + bBonus + (bPerks * 12);

        document.getElementById('offer-a-inhand').textContent = formatInr(Math.round(aMonthlyNet));
        document.getElementById('offer-a-tax').textContent = formatInr(Math.round(aTax));
        document.getElementById('offer-a-total').textContent = formatInr(Math.round(aTotalComp));

        document.getElementById('offer-b-inhand').textContent = formatInr(Math.round(bMonthlyNet));
        document.getElementById('offer-b-tax').textContent = formatInr(Math.round(bTax));
        document.getElementById('offer-b-total').textContent = formatInr(Math.round(bTotalComp));

        const deltaMonthly = bMonthlyNet - aMonthlyNet;
        const deltaAnnual = bTotalComp - aTotalComp;

        const winnerTitleEl = document.getElementById('offer-winner-title');
        const badgeEl = document.getElementById('offer-delta-badge');

        if (deltaMonthly >= 0) {
          if (winnerTitleEl) winnerTitleEl.textContent = `🏆 ${bName} WINS: Delivers +${formatInr(Math.round(deltaMonthly))} more monthly in-hand cash!`;
          if (badgeEl) {
            badgeEl.className = 'badge badge-orange';
            badgeEl.textContent = `+${formatInr(Math.round(deltaAnnual))} / year overall`;
          }
        } else {
          if (winnerTitleEl) winnerTitleEl.textContent = `🏆 ${aName} WINS: Delivers +${formatInr(Math.round(Math.abs(deltaMonthly)))} more monthly in-hand cash!`;
          if (badgeEl) {
            badgeEl.className = 'badge badge-teal';
            badgeEl.textContent = `+${formatInr(Math.round(Math.abs(deltaAnnual)))} / year overall`;
          }
        }
      } catch (err) {
        console.error('[OfferCompare] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 4. TAX CHECKLIST SCREEN
    // -------------------------------------------------------------------------
    function renderTaxChecklist(pane) {
      if (!pane) pane = document.getElementById('pane-tax-checklist');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">📋</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">TAX SAVING DEDUCTIONS CHECKLIST</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Tick eligible deductions (80C, 80D, NPS) to see real tax saved under the Old Regime vs New Regime.</p>
        </div>

        <div class="card card-glow-gold" style="margin-bottom:24px;">
          <div class="grid-2" style="gap:20px; align-items:flex-end; margin-bottom:20px;">
            <div>
              <label class="form-label">Annual Gross CTC (₹)</label>
              <input type="number" id="check-gross-input" class="form-control font-mono" value="1500000" step="50000" style="font-size:20px; color:var(--cinema-gold);" oninput="updateChecklistCalculations()">
            </div>
            <div>
              <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="font-size:12px; color:var(--cinema-muted);">Total Deductions Claimed:</span>
                <strong class="font-mono" style="color:var(--cinema-gold);" id="check-claimed-label">₹0 / ₹2,75,000</strong>
              </div>
              <div style="background:var(--bg-card-subtle); height:12px; border-radius:6px; overflow:hidden; border:1px solid var(--border-subtle);">
                <div id="check-progress-bar" style="background:linear-gradient(90deg, var(--cinema-teal), var(--cinema-gold)); height:100%; width:0%; transition:width 0.3s ease;"></div>
              </div>
            </div>
          </div>

          <div class="grid-3" style="text-align:center; gap:16px;">
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">NEW REGIME TAX</span>
              <div class="font-mono money-val" style="font-size:22px; color:var(--cinema-teal); font-weight:700; margin:6px 0;" id="check-new-tax">₹0</div>
              <span style="font-size:11px; color:var(--cinema-muted);">Standard ₹75,000 deduction</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">OLD REGIME TAX</span>
              <div class="font-mono money-val" style="font-size:22px; color:var(--cinema-gold); font-weight:700; margin:6px 0;" id="check-old-tax">₹0</div>
              <span style="font-size:11px; color:var(--cinema-muted);" id="check-old-tax-sub">With claimed deductions</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">RECOMMENDED DECISION</span>
              <div class="font-mono" style="font-size:20px; color:var(--cinema-orange); font-weight:700; margin:6px 0;" id="check-verdict-text">Calculating...</div>
              <span style="font-size:11px; color:var(--cinema-emerald);" id="check-saved-badge">Savings: ₹0</span>
            </div>
          </div>
        </div>

        <!-- Checklist Items -->
        <div class="card">
          <h3 style="color:var(--cinema-cream); margin-bottom:16px;">SELECT YOUR APPLICABLE DEDUCTIONS</h3>
          
          <div style="display:flex; flex-direction:column; gap:14px;">
            <!-- 80C -->
            <label style="display:flex; align-items:flex-start; gap:12px; cursor:pointer; background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <input type="checkbox" id="check-item-80c" checked style="width:20px; height:20px; margin-top:2px; accent-color:var(--cinema-orange);" onchange="updateChecklistCalculations()">
              <div style="flex:1;">
                <div style="display:flex; justify-content:space-between; align-items:baseline;">
                  <strong style="color:var(--cinema-cream); font-size:15px;">Section 80C Investments (Max ₹1,50,000)</strong>
                  <span class="font-mono" style="color:var(--cinema-gold);">₹1,50,000</span>
                </div>
                <p style="font-size:12px; color:var(--cinema-muted); margin-top:2px;">EPF Contribution, PPF, ELSS Tax Saver Funds, LIC Premium, Children Tuition Fees.</p>
              </div>
            </label>

            <!-- 80D -->
            <label style="display:flex; align-items:flex-start; gap:12px; cursor:pointer; background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <input type="checkbox" id="check-item-80d" checked style="width:20px; height:20px; margin-top:2px; accent-color:var(--cinema-orange);" onchange="updateChecklistCalculations()">
              <div style="flex:1;">
                <div style="display:flex; justify-content:space-between; align-items:baseline;">
                  <strong style="color:var(--cinema-cream); font-size:15px;">Section 80D Health Insurance (Self &amp; Family)</strong>
                  <span class="font-mono" style="color:var(--cinema-gold);">₹25,000</span>
                </div>
                <p style="font-size:12px; color:var(--cinema-muted); margin-top:2px;">Medical insurance premium for self, spouse, and dependent children (up to ₹25,000).</p>
              </div>
            </label>

            <!-- 80D Parents -->
            <label style="display:flex; align-items:flex-start; gap:12px; cursor:pointer; background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <input type="checkbox" id="check-item-80d-parents" style="width:20px; height:20px; margin-top:2px; accent-color:var(--cinema-orange);" onchange="updateChecklistCalculations()">
              <div style="flex:1;">
                <div style="display:flex; justify-content:space-between; align-items:baseline;">
                  <strong style="color:var(--cinema-cream); font-size:15px;">Section 80D Health Insurance (Parents / Senior Citizens)</strong>
                  <span class="font-mono" style="color:var(--cinema-gold);">₹50,000</span>
                </div>
                <p style="font-size:12px; color:var(--cinema-muted); margin-top:2px;">Additional medical insurance premium for parents (up to ₹50,000 for senior citizens).</p>
              </div>
            </label>

            <!-- 80CCD(1B) NPS -->
            <label style="display:flex; align-items:flex-start; gap:12px; cursor:pointer; background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <input type="checkbox" id="check-item-nps" checked style="width:20px; height:20px; margin-top:2px; accent-color:var(--cinema-orange);" onchange="updateChecklistCalculations()">
              <div style="flex:1;">
                <div style="display:flex; justify-content:space-between; align-items:baseline;">
                  <strong style="color:var(--cinema-cream); font-size:15px;">Section 80CCD(1B) National Pension System (NPS)</strong>
                  <span class="font-mono" style="color:var(--cinema-gold);">₹50,000</span>
                </div>
                <p style="font-size:12px; color:var(--cinema-muted); margin-top:2px;">Exclusive additional deduction over and above Section 80C limit for voluntary NPS Tier 1 deposits.</p>
              </div>
            </label>
          </div>
        </div>
      `;
      updateChecklistCalculations();
    }

    function updateChecklistCalculations() {
      try {
        const gross = parseFloat(document.getElementById('check-gross-input')?.value) || 0;
        let deductions = 0;

        if (document.getElementById('check-item-80c')?.checked) deductions += 150000;
        if (document.getElementById('check-item-80d')?.checked) deductions += 25000;
        if (document.getElementById('check-item-80d-parents')?.checked) deductions += 50000;
        if (document.getElementById('check-item-nps')?.checked) deductions += 50000;

        const maxDeductions = 275000;
        const pct = Math.min(100, Math.round((deductions / maxDeductions) * 100));

        const barEl = document.getElementById('check-progress-bar');
        if (barEl) barEl.style.width = pct + '%';

        const claimedEl = document.getElementById('check-claimed-label');
        if (claimedEl) claimedEl.textContent = `${formatInr(deductions)} / ${formatInr(maxDeductions)} (${pct}%)`;

        const taxRes = computeBudget2025Tax(gross, deductions);
        const newTax = taxRes.newRegime.totalTax;
        const oldTax = taxRes.oldRegime.totalTax;

        document.getElementById('check-new-tax').textContent = formatInr(newTax);
        document.getElementById('check-old-tax').textContent = formatInr(oldTax);

        const verdictEl = document.getElementById('check-verdict-text');
        const badgeEl = document.getElementById('check-saved-badge');

        if (newTax <= oldTax) {
          const diff = oldTax - newTax;
          if (verdictEl) {
            verdictEl.textContent = 'NEW REGIME WINS';
            verdictEl.style.color = 'var(--cinema-teal)';
          }
          if (badgeEl) badgeEl.textContent = `Saves ${formatInr(diff)} / year over Old`;
        } else {
          const diff = newTax - oldTax;
          if (verdictEl) {
            verdictEl.textContent = 'OLD REGIME WINS';
            verdictEl.style.color = 'var(--cinema-gold)';
          }
          if (badgeEl) badgeEl.textContent = `Saves ${formatInr(diff)} / year with your deductions`;
        }
      } catch (err) {
        console.error('[TaxChecklist] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 5. HRA RENT CALC SCREEN
    // -------------------------------------------------------------------------
    function renderHraCalc(pane) {
      if (!pane) pane = document.getElementById('pane-hra-calc');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">🏠</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">HRA TAX EXEMPTION CALCULATOR</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Under Section 10(13A), the lowest of the three statutory amounts is 100% tax-exempt.</p>
        </div>

        <div class="card card-glow-orange" style="margin-bottom:24px;">
          <div class="grid-2" style="gap:20px; margin-bottom:20px;">
            <div>
              <label class="form-label">Annual Basic Salary (₹)</label>
              <input type="number" id="hra-basic-input" class="form-control font-mono" value="600000" step="25000" oninput="updateHraCalculations()">
            </div>
            <div>
              <label class="form-label">Actual HRA Received Per Year (₹)</label>
              <input type="number" id="hra-received-input" class="form-control font-mono" value="240000" step="10000" oninput="updateHraCalculations()">
            </div>
            <div>
              <label class="form-label">Total Rent Paid Per Year (₹)</label>
              <input type="number" id="hra-rent-input" class="form-control font-mono" value="300000" step="10000" oninput="updateHraCalculations()">
              <span style="font-size:11px; color:var(--cinema-muted);">Monthly Rent: <span id="hra-monthly-rent-disp" class="font-mono">₹25,000 / mo</span></span>
            </div>
            <div>
              <label class="form-label">City Type</label>
              <select id="hra-city-select" class="form-control" onchange="updateHraCalculations()">
                <option value="metro" selected>Metro City (Delhi, Mumbai, Kolkata, Chennai - 50% Basic)</option>
                <option value="non-metro">Non-Metro City (All other locations - 40% Basic)</option>
              </select>
            </div>
          </div>

          <!-- 3 Statutory Rules Cards -->
          <div style="margin-bottom:20px;">
            <span class="form-label" style="margin-bottom:10px;">SECTION 10(13A) STATUTORY 3-CLAUSE TEST:</span>
            <div class="grid-3" style="gap:14px;">
              <div id="hra-clause-1" style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle); text-align:center;">
                <span style="font-size:11px; color:var(--cinema-muted); font-weight:600;">1. ACTUAL HRA RECEIVED</span>
                <div class="font-mono money-val" style="font-size:22px; color:var(--cinema-cream); margin:6px 0;" id="hra-val-1">₹2,40,000</div>
                <span style="font-size:11px; color:var(--cinema-muted);">As per payroll salary slip</span>
              </div>
              <div id="hra-clause-2" style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle); text-align:center;">
                <span style="font-size:11px; color:var(--cinema-muted); font-weight:600;">2. RENT - 10% BASIC</span>
                <div class="font-mono money-val" style="font-size:22px; color:var(--cinema-cream); margin:6px 0;" id="hra-val-2">₹2,40,000</div>
                <span style="font-size:11px; color:var(--cinema-muted);" id="hra-val-2-sub">₹3.0L - ₹60k</span>
              </div>
              <div id="hra-clause-3" style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle); text-align:center;">
                <span style="font-size:11px; color:var(--cinema-muted); font-weight:600;">3. 50% / 40% OF BASIC</span>
                <div class="font-mono money-val" style="font-size:22px; color:var(--cinema-cream); margin:6px 0;" id="hra-val-3">₹3,00,000</div>
                <span style="font-size:11px; color:var(--cinema-muted);" id="hra-val-3-sub">50% of ₹6.0L (Metro)</span>
              </div>
            </div>
          </div>

          <!-- Result Strip -->
          <div style="background:var(--bg-card-subtle); border-top:1px solid var(--border-film); padding-top:16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
            <div>
              <span style="font-size:12px; color:var(--cinema-muted);">LOWEST VALUE (100% EXEMPT FROM TAX):</span>
              <div class="font-mono money-val" style="font-size:28px; color:var(--cinema-teal); font-weight:700;" id="hra-exempt-result">₹2,40,000</div>
            </div>
            <div style="text-align:right;">
              <span style="font-size:12px; color:var(--cinema-muted);">TAXABLE HRA COMPONENT:</span>
              <div class="font-mono money-val" style="font-size:24px; color:var(--cinema-gold); font-weight:700;" id="hra-taxable-result">₹0</div>
            </div>
          </div>
        </div>
      `;
      updateHraCalculations();
    }

    function updateHraCalculations() {
      try {
        const basic = Math.max(0, parseFloat(document.getElementById('hra-basic-input')?.value) || 0);
        const hraReceived = Math.max(0, parseFloat(document.getElementById('hra-received-input')?.value) || 0);
        const rent = Math.max(0, parseFloat(document.getElementById('hra-rent-input')?.value) || 0);
        const isMetro = document.getElementById('hra-city-select')?.value === 'metro';

        const monthlyRent = Math.round(rent / 12);
        const rentDisp = document.getElementById('hra-monthly-rent-disp');
        if (rentDisp) rentDisp.textContent = `${formatInr(monthlyRent)} / mo`;

        const clause1 = hraReceived;
        const clause2 = Math.max(0, rent - (0.10 * basic));
        const clause3 = (isMetro ? 0.50 : 0.40) * basic;

        const exemptHra = Math.min(clause1, clause2, clause3);
        const taxableHra = Math.max(0, hraReceived - exemptHra);

        document.getElementById('hra-val-1').textContent = formatInr(clause1);
        document.getElementById('hra-val-2').textContent = formatInr(clause2);
        document.getElementById('hra-val-2-sub').textContent = `${formatInr(rent)} - ${formatInr(Math.round(0.10 * basic))}`;
        document.getElementById('hra-val-3').textContent = formatInr(clause3);
        document.getElementById('hra-val-3-sub').textContent = `${isMetro ? '50%' : '40%'} of ${formatInr(basic)}`;

        document.getElementById('hra-exempt-result').textContent = formatInr(exemptHra);
        document.getElementById('hra-taxable-result').textContent = formatInr(taxableHra);

        // Highlight the winning clause card
        ['hra-clause-1', 'hra-clause-2', 'hra-clause-3'].forEach(id => {
          const el = document.getElementById(id);
          if (el) {
            el.style.border = '1px solid var(--border-subtle)';
            el.style.background = 'var(--bg-card-subtle)';
          }
        });

        let winningCardId = 'hra-clause-1';
        if (exemptHra === clause1) winningCardId = 'hra-clause-1';
        else if (exemptHra === clause2) winningCardId = 'hra-clause-2';
        else winningCardId = 'hra-clause-3';

        const winCard = document.getElementById(winningCardId);
        if (winCard) {
          winCard.style.border = '2px solid var(--cinema-teal)';
          winCard.style.background = 'rgba(45, 212, 191, 0.08)';
        }
      } catch (err) {
        console.error('[HraCalc] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 6. OVERTIME CALC SCREEN
    // -------------------------------------------------------------------------
    function renderOvertimeCalc(pane) {
      if (!pane) pane = document.getElementById('pane-overtime-calc');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">⏱️</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">OVERTIME PAY CALCULATOR</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Compute statutory overtime wages per Factories Act / Shops &amp; Commercial Establishments Act.</p>
        </div>

        <div class="card card-glow-teal" style="margin-bottom:24px;">
          <div class="grid-2" style="gap:20px; margin-bottom:20px;">
            <div>
              <label class="form-label">Monthly Wages / Basic Pay (₹)</label>
              <input type="number" id="ot-monthly-pay" class="form-control font-mono" value="45000" step="1000" oninput="updateOtCalculations()">
            </div>
            <div>
              <label class="form-label">Working Days in Month</label>
              <input type="number" id="ot-work-days" class="form-control font-mono" value="26" min="20" max="31" oninput="updateOtCalculations()">
            </div>
            <div>
              <label class="form-label">Shift Hours Per Day</label>
              <input type="number" id="ot-shift-hours" class="form-control font-mono" value="8" min="6" max="12" oninput="updateOtCalculations()">
            </div>
            <div>
              <label class="form-label">Overtime Multiplier</label>
              <select id="ot-multiplier-select" class="form-control" onchange="updateOtCalculations()">
                <option value="2.0" selected>2.0x Double Rate (Factories Act Mandate)</option>
                <option value="1.5">1.5x Time-and-a-Half (Commercial Standard)</option>
                <option value="1.0">1.0x Single Rate (Normal hourly wages)</option>
              </select>
            </div>
          </div>

          <div style="margin-bottom:20px;">
            <label class="form-label">Overtime Hours Worked This Month</label>
            <div style="display:flex; align-items:center; gap:16px;">
              <input type="range" id="ot-hours-range" min="0" max="60" step="1" value="15" style="flex:1; accent-color:var(--cinema-teal); cursor:pointer;" oninput="updateOtFromRange(this.value)">
              <input type="number" id="ot-hours-input" class="form-control font-mono" value="15" min="0" max="100" style="width:100px; text-align:center; font-size:18px;" oninput="updateOtFromInput(this.value)">
              <span style="font-size:14px; color:var(--cinema-cream);">Hours</span>
            </div>
          </div>

          <div class="grid-3" style="text-align:center; gap:16px;">
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">STANDARD HOURLY RATE</span>
              <div class="font-mono money-val" style="font-size:22px; color:var(--cinema-cream); font-weight:700; margin:6px 0;" id="ot-hourly-std">₹0 / hr</div>
              <span style="font-size:11px; color:var(--cinema-muted);">Monthly / (Days × Hours)</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">APPLICABLE OT RATE</span>
              <div class="font-mono money-val" style="font-size:22px; color:var(--cinema-teal); font-weight:700; margin:6px 0;" id="ot-hourly-rate">₹0 / hr</div>
              <span style="font-size:11px; color:var(--cinema-emerald);" id="ot-mult-label">At 2.0x multiplier</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-film);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">TOTAL OVERTIME PAYOUT</span>
              <div class="font-mono money-val" style="font-size:26px; color:var(--cinema-orange); font-weight:700; margin:6px 0;" id="ot-total-payout">₹0</div>
              <span style="font-size:11px; color:var(--cinema-gold);" id="ot-grand-total">Total Monthly: ₹0</span>
            </div>
          </div>
        </div>
      `;
      updateOtCalculations();
    }

    function updateOtFromRange(val) {
      const input = document.getElementById('ot-hours-input');
      if (input) input.value = val;
      updateOtCalculations();
    }

    function updateOtFromInput(val) {
      const range = document.getElementById('ot-hours-range');
      if (range) range.value = Math.min(60, val);
      updateOtCalculations();
    }

    function updateOtCalculations() {
      try {
        const pay = parseFloat(document.getElementById('ot-monthly-pay')?.value) || 0;
        const days = Math.max(1, parseFloat(document.getElementById('ot-work-days')?.value) || 26);
        const shift = Math.max(1, parseFloat(document.getElementById('ot-shift-hours')?.value) || 8);
        const mult = parseFloat(document.getElementById('ot-multiplier-select')?.value) || 2.0;
        const hours = Math.max(0, parseFloat(document.getElementById('ot-hours-input')?.value) || 0);

        const hourlyBase = pay / (days * shift);
        const hourlyOt = hourlyBase * mult;
        const totalOt = Math.round(hours * hourlyOt);
        const grandTotal = Math.round(pay + totalOt);

        document.getElementById('ot-hourly-std').textContent = `₹${hourlyBase.toFixed(1)} / hr`;
        document.getElementById('ot-hourly-rate').textContent = `₹${hourlyOt.toFixed(1)} / hr`;
        document.getElementById('ot-mult-label').textContent = `At ${mult}x statutory multiplier`;
        document.getElementById('ot-total-payout').textContent = formatInr(totalOt);
        document.getElementById('ot-grand-total').textContent = `Total Monthly Gross: ${formatInr(grandTotal)}`;
      } catch (err) {
        console.error('[OvertimeCalc] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 7. FESTIVAL BONUS SCREEN
    // -------------------------------------------------------------------------
    function renderFestivalBonus(pane) {
      if (!pane) pane = document.getElementById('pane-festival-bonus');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">🎉</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">FESTIVAL &amp; ANNUAL BONUS DISBURSEMENT</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Calculate company budget, cost per person, and net bonus payout for festive occasions.</p>
        </div>

        <div class="card card-glow-gold" style="margin-bottom:24px;">
          <div class="grid-2" style="gap:20px; margin-bottom:20px;">
            <div>
              <label class="form-label">Occasion / Festival</label>
              <select id="bonus-occasion-select" class="form-control" onchange="updateBonusCalculations()">
                <option value="diwali" selected>Diwali / Puja Celebration Bonus</option>
                <option value="eid">Eid Mubarak Festivity Payout</option>
                <option value="yearend">Annual Performance / Year-End Bonus</option>
                <option value="statutory">Payment of Bonus Act (Statutory 8.33% Min)</option>
              </select>
            </div>
            <div>
              <label class="form-label">Bonus % of Monthly Basic Pay</label>
              <div style="display:flex; gap:10px; align-items:center;">
                <input type="number" id="bonus-pct-input" class="form-control font-mono" value="50" min="5" max="200" step="5" oninput="updateBonusCalculations()">
                <span class="font-mono" style="font-size:18px; color:var(--cinema-gold);">%</span>
              </div>
            </div>
            <div>
              <label class="form-label">Eligible Team Headcount</label>
              <input type="number" id="bonus-headcount-input" class="form-control font-mono" value="10" min="1" max="1000" oninput="updateBonusCalculations()">
            </div>
            <div>
              <label class="form-label">Average Monthly Basic Pay (₹)</label>
              <input type="number" id="bonus-basic-input" class="form-control font-mono" value="25000" step="1000" oninput="updateBonusCalculations()">
            </div>
          </div>

          <div class="grid-3" style="text-align:center; gap:16px;">
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">BONUS PER PERSON</span>
              <div class="font-mono money-val" style="font-size:24px; color:var(--cinema-teal); font-weight:700; margin:6px 0;" id="bonus-per-person">₹0</div>
              <span style="font-size:11px; color:var(--cinema-muted);" id="bonus-pct-sub">50% of Basic Pay</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-film);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">TOTAL COMPANY OUTLAY</span>
              <div class="font-mono money-val" style="font-size:26px; color:var(--cinema-orange); font-weight:700; margin:6px 0;" id="bonus-total-outlay">₹0</div>
              <span style="font-size:11px; color:var(--cinema-gold);" id="bonus-headcount-sub">Across 10 team members</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;">NET IN-HAND (AFTER 10% TDS)</span>
              <div class="font-mono money-val" style="font-size:24px; color:var(--cinema-cream); font-weight:700; margin:6px 0;" id="bonus-net-inhand">₹0</div>
              <span style="font-size:11px; color:var(--cinema-emerald);">Disbursed to staff bank</span>
            </div>
          </div>
        </div>
      `;
      updateBonusCalculations();
    }

    function updateBonusCalculations() {
      try {
        const pct = Math.max(0, parseFloat(document.getElementById('bonus-pct-input')?.value) || 0);
        const headcount = Math.max(1, parseFloat(document.getElementById('bonus-headcount-input')?.value) || 1);
        const basic = Math.max(0, parseFloat(document.getElementById('bonus-basic-input')?.value) || 0);

        const bonusPerPerson = Math.round(basic * (pct / 100));
        const totalOutlay = Math.round(bonusPerPerson * headcount);
        const netInHand = Math.round(bonusPerPerson * 0.90); // 10% withholding estimate

        document.getElementById('bonus-per-person').textContent = formatInr(bonusPerPerson);
        document.getElementById('bonus-pct-sub').textContent = `${pct}% of ₹${basic.toLocaleString('en-IN')} basic`;
        document.getElementById('bonus-total-outlay').textContent = formatInr(totalOutlay);
        document.getElementById('bonus-headcount-sub').textContent = `Across ${headcount} team members`;
        document.getElementById('bonus-net-inhand').textContent = formatInr(netInHand);
      } catch (err) {
        console.error('[FestivalBonus] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 8. CASH CALENDAR SCREEN
    // -------------------------------------------------------------------------
    function renderCashCalendar(pane) {
      if (!pane) pane = document.getElementById('pane-cashflow-cal');
      if (!pane) return;

      const events = [
        { day: 1, type: 'start', title: 'Month Opening', amount: 850000, desc: 'Starting Bank Reserve' },
        { day: 5, type: 'out', title: 'Office Rent & Maintenance', amount: -45000, desc: 'Property Lease Challan' },
        { day: 7, type: 'in', title: 'Client Retainer Milestone', amount: 250000, desc: 'Apex Corp Invoice Inflow' },
        { day: 10, type: 'out', title: 'SaaS Subscriptions & Cloud', amount: -22000, desc: 'AWS & Google Workspace' },
        { day: 15, type: 'out', title: 'Advance Tax / TDS Payment', amount: -78000, desc: 'ITNS 281 Challan' },
        { day: 18, type: 'in', title: 'Milestone 2 Inflow', amount: 380000, desc: 'Zenith Logistics Contract' },
        { day: 20, type: 'out', title: 'Monthly GST Challan', amount: -55000, desc: 'GSTR-3B Tax Filing' },
        { day: 25, type: 'out', title: 'Vendor Supply Invoices', amount: -120000, desc: 'Raw Material Vendors' },
        { day: 30, type: 'salary', title: 'Monthly Payroll Run', amount: -590000, desc: 'Staff Salary Disbursement' }
      ];

      let running = 850000;
      let minCash = running;
      let minDay = 1;

      for (let d = 1; d <= 31; d++) {
        const ev = events.find(e => e.day === d && e.type !== 'start');
        if (ev) running += ev.amount;
        if (running < minCash) {
          minCash = running;
          minDay = d;
        }
      }

      let gridHtml = '';
      for (let day = 1; day <= 31; day++) {
        const ev = events.find(e => e.day === day);
        let tagClass = 'border:1px solid var(--border-subtle); background:var(--bg-card-subtle);';
        let badge = '';
        if (ev) {
          if (ev.type === 'salary') {
            tagClass = 'border:2px solid var(--cinema-orange); background:rgba(255,138,61,0.12);';
            badge = `<div style="font-size:10px; color:var(--cinema-orange); font-weight:700; margin-top:2px;">💰 PAYROLL -₹5.9L</div>`;
          } else if (ev.amount > 0) {
            tagClass = 'border:1px solid var(--cinema-emerald); background:rgba(16,185,129,0.1);';
            badge = `<div style="font-size:10px; color:var(--cinema-emerald); font-weight:700; margin-top:2px;">+₹${(ev.amount/1000).toFixed(0)}k INFLOW</div>`;
          } else {
            tagClass = 'border:1px solid var(--cinema-crimson); background:rgba(244,63,94,0.08);';
            badge = `<div style="font-size:10px; color:var(--cinema-crimson); font-weight:700; margin-top:2px;">-₹${(Math.abs(ev.amount)/1000).toFixed(0)}k DUE</div>`;
          }
        }

        gridHtml += `
          <div style="min-height:75px; padding:8px; border-radius:var(--radius-sm); ${tagClass} display:flex; flex-direction:column; justify-content:space-between;">
            <div style="font-size:12px; font-weight:700; color:${ev ? 'var(--cinema-cream)' : 'var(--cinema-muted)'};">${day}</div>
            ${badge}
          </div>
        `;
      }

      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">📅</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">CASHFLOW &amp; DUES CALENDAR</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Month timeline tracking payroll disbursement date, vendor payables, and low-cash liquidity alerts.</p>
        </div>

        ${minCash < 150000 ? `
          <div style="background:rgba(244,63,94,0.15); border:1px solid var(--cinema-crimson); border-radius:var(--radius-md); padding:16px 20px; margin-bottom:20px; display:flex; align-items:center; gap:14px;">
            <div style="font-size:28px;">⚠️</div>
            <div>
              <strong style="color:var(--cinema-crimson); font-size:14px;">LOW-CASH WARNING ALERT</strong>
              <p style="color:var(--cinema-cream); font-size:13px; margin:2px 0 0 0;">
                Projected cash reserve dips to <strong>${formatInr(minCash)}</strong> on Day ${minDay} after salary &amp; statutory dues. Ensure Day 18 receivables (₹3.8L) are cleared beforehand.
              </p>
            </div>
          </div>
        ` : ''}

        <div class="card" style="margin-bottom:24px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px;">
            <div>
              <h3 style="color:var(--cinema-cream);">OCTOBER 2026 CASHFLOW TIMELINE</h3>
              <span style="font-size:12px; color:var(--cinema-muted);">Starting balance: ₹8,50,000 • Projected ending balance: ${formatInr(running)}</span>
            </div>
            <div style="display:flex; gap:12px; font-size:11px;">
              <span style="color:var(--cinema-emerald);">● Receivables (+₹6.3L)</span>
              <span style="color:var(--cinema-crimson);">● Vendor / Tax Dues (-₹3.2L)</span>
              <span style="color:var(--cinema-orange);">● Salary Day (-₹5.9L)</span>
            </div>
          </div>

          <div style="display:grid; grid-template-columns: repeat(7, 1fr); gap:8px;">
            ${gridHtml}
          </div>
        </div>
      `;
    }

    // -------------------------------------------------------------------------
    // 9. F&F SETTLEMENT SCREEN
    // -------------------------------------------------------------------------
    function renderFfSettlement(pane) {
      if (!pane) pane = document.getElementById('pane-ff-settlement');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">📑</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">FULL &amp; FINAL (F&amp;F) SETTLEMENT ENGINE</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Calculate exit dues: privilege leave encashment, notice pay shortfall/recovery, and statutory gratuity.</p>
        </div>

        <div class="card card-glow-orange" style="margin-bottom:24px;">
          <div class="grid-2" style="gap:20px; margin-bottom:20px;">
            <div>
              <label class="form-label">Employee Name &amp; Designation</label>
              <input type="text" id="ff-emp-name" class="form-control" value="Rohan Gupta (Tech Lead)" oninput="updateFfCalculations()">
            </div>
            <div>
              <label class="form-label">Monthly Gross Pay (₹)</label>
              <input type="number" id="ff-gross-input" class="form-control font-mono" value="75000" step="5000" oninput="updateFfCalculations()">
            </div>
            <div>
              <label class="form-label">Monthly Basic Salary (₹)</label>
              <input type="number" id="ff-basic-input" class="form-control font-mono" value="30000" step="2000" oninput="updateFfCalculations()">
            </div>
            <div>
              <label class="form-label">Total Tenure Completed (Years)</label>
              <input type="number" id="ff-tenure-input" class="form-control font-mono" value="5.5" min="0" step="0.5" oninput="updateFfCalculations()">
              <span style="font-size:11px; color:var(--cinema-muted);">Gratuity eligible after 5.0 continuous years of service.</span>
            </div>
            <div>
              <label class="form-label">Unused Privilege Leave Balance (Days)</label>
              <input type="number" id="ff-leave-input" class="form-control font-mono" value="18" min="0" max="180" oninput="updateFfCalculations()">
            </div>
            <div>
              <label class="form-label">Notice Period Shortfall / Buyout Days</label>
              <input type="number" id="ff-notice-input" class="form-control font-mono" value="0" min="0" max="90" oninput="updateFfCalculations()">
            </div>
          </div>

          <!-- Settlement Summary Cards -->
          <div class="grid-4" style="text-align:center; gap:12px; margin-bottom:20px;">
            <div style="background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--cinema-muted);">LEAVE ENCASHMENT</span>
              <div class="font-mono money-val" style="font-size:20px; color:var(--cinema-teal); font-weight:700; margin:4px 0;" id="ff-res-leave">₹0</div>
              <span style="font-size:10px; color:var(--cinema-muted);">(Basic/30) × Days</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--cinema-muted);">STATUTORY GRATUITY</span>
              <div class="font-mono money-val" style="font-size:20px; color:var(--cinema-gold); font-weight:700; margin:4px 0;" id="ff-res-gratuity">₹0</div>
              <span style="font-size:10px; color:var(--cinema-muted);" id="ff-grat-note">Eligible (5+ yrs)</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
              <span style="font-size:11px; color:var(--cinema-muted);">PRO-RATA DAYS SALARY</span>
              <div class="font-mono money-val" style="font-size:20px; color:var(--cinema-cream); font-weight:700; margin:4px 0;" id="ff-res-salary">₹0</div>
              <span style="font-size:10px; color:var(--cinema-muted);">Current month days</span>
            </div>
            <div style="background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-film);">
              <span style="font-size:11px; color:var(--cinema-muted); font-weight:700;">TOTAL NET F&amp;F DISBURSEMENT</span>
              <div class="font-mono money-val" style="font-size:24px; color:var(--cinema-orange); font-weight:700; margin:4px 0;" id="ff-res-total">₹0</div>
              <span style="font-size:10px; color:var(--cinema-emerald);">Clearance Release</span>
            </div>
          </div>
        </div>
      `;
      updateFfCalculations();
    }

    function updateFfCalculations() {
      try {
        const gross = Math.max(0, parseFloat(document.getElementById('ff-gross-input')?.value) || 0);
        const basic = Math.max(0, parseFloat(document.getElementById('ff-basic-input')?.value) || 0);
        const tenure = Math.max(0, parseFloat(document.getElementById('ff-tenure-input')?.value) || 0);
        const leaveDays = Math.max(0, parseFloat(document.getElementById('ff-leave-input')?.value) || 0);
        const noticeDays = Math.max(0, parseFloat(document.getElementById('ff-notice-input')?.value) || 0);

        // Leave encashment = (basic / 30) * leaveDays
        const leaveEncashment = Math.round((basic / 30) * leaveDays);

        // Gratuity = (15 * basic * tenureYears) / 26 (if tenure >= 5 years)
        let gratuity = 0;
        const isEligible = tenure >= 5.0;
        if (isEligible) {
          gratuity = Math.round((15 * basic * Math.round(tenure)) / 26);
        }

        // Notice recovery or pay = (gross / 30) * noticeDays
        const noticeAmount = Math.round((gross / 30) * noticeDays);

        // Pro-rata current month worked days (assume 20 days worked in final month)
        const proRataSalary = Math.round((gross / 30) * 20);

        const totalSettlement = Math.max(0, proRataSalary + leaveEncashment + gratuity - noticeAmount);

        document.getElementById('ff-res-leave').textContent = formatInr(leaveEncashment);
        document.getElementById('ff-res-gratuity').textContent = formatInr(gratuity);
        document.getElementById('ff-grat-note').textContent = isEligible ? `${Math.round(tenure)} yrs service` : 'Not eligible (<5 yrs)';
        document.getElementById('ff-res-salary').textContent = formatInr(proRataSalary);
        document.getElementById('ff-res-total').textContent = formatInr(totalSettlement);
      } catch (err) {
        console.error('[FfSettlement] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 10. ONBOARD CHECK SCREEN
    // -------------------------------------------------------------------------
    function renderOnboardCheck(pane) {
      if (!pane) pane = document.getElementById('pane-onboarding-check');
      if (!pane) return;

      const savedState = safeStorageGet('paypilot_onboarding_checks', [0, 1, 2, 3]);

      const steps = [
        { id: 0, title: 'PAN Card Verification', desc: 'Valid PAN linked with Aadhaar on Income Tax portal.' },
        { id: 1, title: 'Aadhaar & Address Verification', desc: 'Identity proof uploaded & matched.' },
        { id: 2, title: 'Bank Account & Cancelled Cheque', desc: 'IFSC verified for electronic salary NEFT.' },
        { id: 3, title: 'UAN (Universal Account Number)', desc: 'Mapped in EPFO portal for PF passbook credit.' },
        { id: 4, title: 'Form 11 (EPFO Declaration)', desc: 'Previous employment & pension scheme declaration.' },
        { id: 5, title: 'ESIC / Group Medical Insurance', desc: 'Family members nominated for healthcare cover.' },
        { id: 6, title: 'Signed Appointment & CTC Letter', desc: 'Executed contract acknowledging compensation structure.' },
        { id: 7, title: 'Tax Regime Choice Recorded', desc: 'Opted for New Regime or Old Regime with declaration.' }
      ];

      let listHtml = '';
      steps.forEach(s => {
        const checked = savedState.includes(s.id) ? 'checked' : '';
        listHtml += `
          <label style="display:flex; align-items:flex-start; gap:12px; cursor:pointer; background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
            <input type="checkbox" class="onboard-step-check" data-step-id="${s.id}" ${checked} style="width:20px; height:20px; margin-top:2px; accent-color:var(--cinema-teal);" onchange="updateOnboardProgress()">
            <div style="flex:1;">
              <strong style="color:var(--cinema-cream); font-size:15px;">${escapeHtml(s.title)}</strong>
              <p style="font-size:12px; color:var(--cinema-muted); margin-top:2px;">${escapeHtml(s.desc)}</p>
            </div>
          </label>
        `;
      });

      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">✅</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">ONBOARDING COMPLIANCE AUDIT</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Verify mandatory statutory documents and banking setup before adding worker to live payroll run.</p>
        </div>

        <div class="card card-glow-teal" style="margin-bottom:24px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-wrap:wrap; gap:12px;">
            <div>
              <span style="font-size:12px; color:var(--cinema-muted);">COMPLIANCE PROGRESS:</span>
              <h3 style="color:var(--cinema-cream); margin-top:2px;" id="onboard-progress-text">0 of 8 Steps Complete</h3>
            </div>
            <div id="onboard-status-badge" class="badge badge-gold" style="font-size:14px; padding:8px 16px;">
              IN PROGRESS
            </div>
          </div>

          <div style="background:var(--bg-card-subtle); height:12px; border-radius:6px; overflow:hidden; border:1px solid var(--border-subtle); margin-bottom:20px;">
            <div id="onboard-progress-bar" style="background:linear-gradient(90deg, var(--cinema-teal), var(--cinema-emerald)); height:100%; width:0%; transition:width 0.3s ease;"></div>
          </div>

          <div style="display:flex; flex-direction:column; gap:12px;">
            ${listHtml}
          </div>
        </div>
      `;
      updateOnboardProgress();
    }

    function updateOnboardProgress() {
      try {
        const checkboxes = document.querySelectorAll('.onboard-step-check');
        const checkedList = [];
        checkboxes.forEach(cb => {
          if (cb.checked) checkedList.push(parseInt(cb.dataset.stepId, 10));
        });

        safeStorageSet('paypilot_onboarding_checks', checkedList);

        const total = checkboxes.length || 8;
        const count = checkedList.length;
        const pct = Math.round((count / total) * 100);

        const textEl = document.getElementById('onboard-progress-text');
        if (textEl) textEl.textContent = `${count} of ${total} Steps Complete (${pct}%)`;

        const barEl = document.getElementById('onboard-progress-bar');
        if (barEl) barEl.style.width = pct + '%';

        const badgeEl = document.getElementById('onboard-status-badge');
        if (badgeEl) {
          if (count === total) {
            badgeEl.className = 'badge badge-teal';
            badgeEl.style.background = 'var(--cinema-emerald)';
            badgeEl.style.color = '#000';
            badgeEl.textContent = '🟢 READY TO PAY';
          } else {
            badgeEl.className = 'badge badge-gold';
            badgeEl.style.background = '';
            badgeEl.style.color = '';
            badgeEl.textContent = `${total - count} PENDING ITEMS`;
          }
        }
      } catch (err) {
        console.error('[OnboardingCheck] Progress update error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 11. HEALTH SCORE SCREEN
    // -------------------------------------------------------------------------
    function renderHealthScore(pane) {
      if (!pane) pane = document.getElementById('pane-health-score');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">🩺</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">FINANCIAL HEALTH SCORE // VITAL SIGNS</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Instant 0 to 100 index rating savings buffer, emergency liquidity, and debt ratio.</p>
        </div>

        <div class="card card-glow-teal" style="margin-bottom:24px;">
          <div class="grid-2" style="gap:24px; align-items:center;">
            <!-- Dial gauge -->
            <div style="text-align:center; padding:16px;">
              <div style="position:relative; width:160px; height:160px; margin:0 auto;">
                <svg viewBox="0 0 36 36" style="width:100%; height:100%; transform: rotate(-90deg);">
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="3.5" />
                  <path id="health-dial-arc" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="var(--cinema-teal)" stroke-dasharray="82, 100" stroke-width="3.5" stroke-linecap="round" />
                </svg>
                <div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); text-align:center;">
                  <span class="font-mono" style="font-size:42px; font-weight:800; color:var(--cinema-teal);" id="health-dial-score">82</span>
                  <div style="font-size:11px; color:var(--cinema-muted); font-weight:600;">HEALTH INDEX</div>
                </div>
              </div>
              <div style="margin-top:12px;">
                <span class="badge badge-teal" id="health-grade-badge">EXCELLENT FINANCIAL RESILIENCE</span>
              </div>
            </div>

            <!-- Inputs -->
            <div>
              <div style="margin-bottom:12px;">
                <label class="form-label">Monthly Net In-Hand Income (₹)</label>
                <input type="number" id="health-income" class="form-control font-mono" value="120000" step="5000" oninput="updateHealthCalculations()">
              </div>
              <div style="margin-bottom:12px;">
                <label class="form-label">Monthly Fixed Living Costs (Rent, Food, Bills) (₹)</label>
                <input type="number" id="health-expenses" class="form-control font-mono" value="55000" step="5000" oninput="updateHealthCalculations()">
              </div>
              <div style="margin-bottom:12px;">
                <label class="form-label">Liquid Bank Emergency Fund (₹)</label>
                <input type="number" id="health-emergency" class="form-control font-mono" value="400000" step="25000" oninput="updateHealthCalculations()">
              </div>
              <div>
                <label class="form-label">Monthly Debt / EMI Payments (₹)</label>
                <input type="number" id="health-emi" class="form-control font-mono" value="12000" step="2000" oninput="updateHealthCalculations()">
              </div>
            </div>
          </div>
        </div>

        <!-- 3 Actionable Tips -->
        <div class="card">
          <h3 style="color:var(--cinema-cream); margin-bottom:14px;">3 ACTIONABLE RECOMMENDATIONS FOR YOU</h3>
          <div style="display:flex; flex-direction:column; gap:12px;" id="health-tips-container">
            <div style="background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border-left:4px solid var(--cinema-teal);">
              <strong style="color:var(--cinema-teal); font-size:14px;">1. Emergency Cash Runway:</strong>
              <p style="color:var(--cinema-cream); font-size:13px; margin:4px 0 0 0;" id="health-tip-1">Your liquid reserves cover 7.2 months of living expenses. That is above the 6-month safety threshold.</p>
            </div>
            <div style="background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border-left:4px solid var(--cinema-gold);">
              <strong style="color:var(--cinema-gold); font-size:14px;">2. Debt-To-Income Ratio:</strong>
              <p style="color:var(--cinema-cream); font-size:13px; margin:4px 0 0 0;" id="health-tip-2">Your debt EMI stands at 10% of take-home income. Keep it strictly below 30% to preserve borrowing capacity.</p>
            </div>
            <div style="background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border-left:4px solid var(--cinema-orange);">
              <strong style="color:var(--cinema-orange); font-size:14px;">3. Savings Surplus Deployment:</strong>
              <p style="color:var(--cinema-cream); font-size:13px; margin:4px 0 0 0;" id="health-tip-3">You have ₹53,000 unallocated surplus each month. Channel ₹30,000 into automated index mutual fund SIPs on salary day.</p>
            </div>
          </div>
        </div>
      `;
      updateHealthCalculations();
    }

    function updateHealthCalculations() {
      try {
        const income = Math.max(1000, parseFloat(document.getElementById('health-income')?.value) || 120000);
        const expenses = Math.max(0, parseFloat(document.getElementById('health-expenses')?.value) || 55000);
        const emergency = Math.max(0, parseFloat(document.getElementById('health-emergency')?.value) || 400000);
        const emi = Math.max(0, parseFloat(document.getElementById('health-emi')?.value) || 0);

        const runwayMonths = expenses > 0 ? (emergency / expenses).toFixed(1) : 12;
        const emiRatio = ((emi / income) * 100).toFixed(0);
        const savingsSurplus = Math.max(0, income - expenses - emi);

        // Scoring: 0-100
        let score = 50;
        // Runway points: >=6m = +25, 3-6m = +15, <3m = -10
        if (runwayMonths >= 6) score += 25;
        else if (runwayMonths >= 3) score += 15;
        else score -= 15;

        // Debt ratio: <=15% = +20, <=30% = +10, >30% = -15
        if (emiRatio <= 15) score += 20;
        else if (emiRatio <= 30) score += 10;
        else score -= 15;

        // Savings surplus: >30% = +10
        if (savingsSurplus / income >= 0.3) score += 10;

        score = Math.max(10, Math.min(100, Math.round(score)));

        document.getElementById('health-dial-score').textContent = score;
        const arc = document.getElementById('health-dial-arc');
        if (arc) arc.setAttribute('stroke-dasharray', `${score}, 100`);

        const badge = document.getElementById('health-grade-badge');
        if (badge) {
          if (score >= 80) {
            badge.className = 'badge badge-teal';
            badge.textContent = 'EXCELLENT FINANCIAL RESILIENCE';
          } else if (score >= 60) {
            badge.className = 'badge badge-gold';
            badge.textContent = 'GOOD • ROOM FOR SAVINGS OPTIMIZATION';
          } else {
            badge.className = 'badge badge-crimson';
            badge.textContent = 'CAUTION • REINFORCE EMERGENCY BUFFER';
          }
        }

        const tip1 = document.getElementById('health-tip-1');
        if (tip1) tip1.textContent = `Your emergency reserves cover ${runwayMonths} months of living costs (${formatInr(emergency)}). Aim for a minimum 6 months (${formatInr(expenses * 6)}).`;

        const tip2 = document.getElementById('health-tip-2');
        if (tip2) tip2.textContent = `Debt EMI commitments are ${emiRatio}% of monthly income. Maintaining this below 25% prevents cash flow strain.`;

        const tip3 = document.getElementById('health-tip-3');
        if (tip3) tip3.textContent = `You have ${formatInr(savingsSurplus)} monthly surplus. Automate investing 50% into SIP mutual funds on payday.`;
      } catch (err) {
        console.error('[HealthScore] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 12. 3-MONTH FORECAST SCREEN
    // -------------------------------------------------------------------------
    function renderForecast3m(pane) {
      if (!pane) pane = document.getElementById('pane-forecast-3m');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">🔮</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">3-MONTH PAYROLL FORECAST &amp; HIRING SIMULATOR</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Simulate future payroll runway and run what-if scenarios when onboarding additional personnel.</p>
        </div>

        <div class="card card-glow-orange" style="margin-bottom:24px;">
          <div class="grid-2" style="gap:20px; align-items:flex-end; margin-bottom:20px;">
            <div>
              <label class="form-label">Current Monthly Payroll Outlay (₹)</label>
              <input type="number" id="fc-base-payroll" class="form-control font-mono" value="590000" step="25000" oninput="updateForecastCalculations()">
            </div>
            <div>
              <label style="display:flex; align-items:center; gap:10px; cursor:pointer;">
                <input type="checkbox" id="fc-hire-toggle" checked style="width:20px; height:20px; accent-color:var(--cinema-orange);" onchange="updateForecastCalculations()">
                <strong style="color:var(--cinema-cream); font-size:15px;">Simulate New Team Hire What-If</strong>
              </label>
            </div>
          </div>

          <div id="fc-hire-controls" class="grid-2" style="gap:20px; margin-bottom:20px; background:var(--bg-card-subtle); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
            <div>
              <label class="form-label">Proposed New Hire Monthly CTC (₹)</label>
              <input type="number" id="fc-hire-salary" class="form-control font-mono" value="125000" step="10000" oninput="updateForecastCalculations()">
              <span style="font-size:11px; color:var(--cinema-gold);">Annual CTC: ₹15.0 Lakhs</span>
            </div>
            <div>
              <label class="form-label">Start Month</label>
              <select id="fc-hire-start" class="form-control" onchange="updateForecastCalculations()">
                <option value="1">Month 1 (November 2026)</option>
                <option value="2">Month 2 (December 2026)</option>
                <option value="3">Month 3 (January 2027)</option>
              </select>
            </div>
          </div>

          <!-- Comparative 3-Month Bar Chart -->
          <div style="margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
              <span style="font-size:12px; color:var(--cinema-muted); font-weight:600;">3-MONTH DISBURSEMENT PROJECTION</span>
              <span style="font-size:12px; color:var(--cinema-orange);" id="fc-cumulative-label">Total Outlay: ₹0</span>
            </div>

            <div style="display:flex; flex-direction:column; gap:16px;">
              <!-- Month 1 -->
              <div>
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                  <span style="color:var(--cinema-cream); font-weight:600;">Month 1 (November 2026)</span>
                  <strong class="font-mono" style="color:var(--cinema-teal);" id="fc-m1-val">₹0</strong>
                </div>
                <div style="background:var(--bg-card-subtle); height:16px; border-radius:4px; overflow:hidden;">
                  <div id="fc-m1-bar" style="background:var(--cinema-teal); height:100%; width:70%; transition:width 0.3s ease;"></div>
                </div>
              </div>

              <!-- Month 2 -->
              <div>
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                  <span style="color:var(--cinema-cream); font-weight:600;">Month 2 (December 2026)</span>
                  <strong class="font-mono" style="color:var(--cinema-gold);" id="fc-m2-val">₹0</strong>
                </div>
                <div style="background:var(--bg-card-subtle); height:16px; border-radius:4px; overflow:hidden;">
                  <div id="fc-m2-bar" style="background:var(--cinema-gold); height:100%; width:70%; transition:width 0.3s ease;"></div>
                </div>
              </div>

              <!-- Month 3 -->
              <div>
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                  <span style="color:var(--cinema-cream); font-weight:600;">Month 3 (January 2027)</span>
                  <strong class="font-mono" style="color:var(--cinema-orange);" id="fc-m3-val">₹0</strong>
                </div>
                <div style="background:var(--bg-card-subtle); height:16px; border-radius:4px; overflow:hidden;">
                  <div id="fc-m3-bar" style="background:var(--cinema-orange); height:100%; width:70%; transition:width 0.3s ease;"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
      updateForecastCalculations();
    }

    function updateForecastCalculations() {
      try {
        const base = Math.max(0, parseFloat(document.getElementById('fc-base-payroll')?.value) || 590000);
        const hireOn = document.getElementById('fc-hire-toggle')?.checked;
        const hireCost = hireOn ? Math.max(0, parseFloat(document.getElementById('fc-hire-salary')?.value) || 0) : 0;
        const startMonth = parseInt(document.getElementById('fc-hire-start')?.value || '1', 10);

        const m1 = base + (startMonth <= 1 ? hireCost : 0);
        const m2 = base + (startMonth <= 2 ? hireCost : 0);
        const m3 = base + (startMonth <= 3 ? hireCost : 0);

        const total = m1 + m2 + m3;
        const maxVal = Math.max(m1, m2, m3, 1000000);

        document.getElementById('fc-m1-val').textContent = formatInr(m1);
        document.getElementById('fc-m2-val').textContent = formatInr(m2);
        document.getElementById('fc-m3-val').textContent = formatInr(m3);

        const bar1 = document.getElementById('fc-m1-bar');
        const bar2 = document.getElementById('fc-m2-bar');
        const bar3 = document.getElementById('fc-m3-bar');

        if (bar1) bar1.style.width = `${Math.min(100, Math.round((m1 / maxVal) * 100))}%`;
        if (bar2) bar2.style.width = `${Math.min(100, Math.round((m2 / maxVal) * 100))}%`;
        if (bar3) bar3.style.width = `${Math.min(100, Math.round((m3 / maxVal) * 100))}%`;

        document.getElementById('fc-cumulative-label').textContent = `Total 3-Month Commitment: ${formatInr(total)}`;
      } catch (err) {
        console.error('[Forecast3m] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // 13. SLIP TIMELINE SCREEN
    // -------------------------------------------------------------------------
    function renderSlipTimeline(pane) {
      if (!pane) pane = document.getElementById('pane-payslip-timeline');
      if (!pane) return;

      const runs = [
        { id: '2026-10', title: 'October 2026', status: 'Draft', gross: 590000, tds: 42000, net: 524000, count: 8, emp: 'EMP-101' },
        { id: '2026-09', title: 'September 2026', status: 'Paid', gross: 620000, tds: 45000, net: 549000, count: 8, emp: 'EMP-105', note: 'Includes ₹30k Festival Bonus to Kabir Singh' },
        { id: '2026-08', title: 'August 2026', status: 'Paid', gross: 590000, tds: 42000, net: 524000, count: 8, emp: 'EMP-101' },
        { id: '2026-07', title: 'July 2026', status: 'Paid', gross: 590000, tds: 42000, net: 524000, count: 8, emp: 'EMP-102' },
        { id: '2026-06', title: 'June 2026', status: 'Paid', gross: 590000, tds: 42000, net: 524000, count: 8, emp: 'EMP-103' },
        { id: '2026-05', title: 'May 2026', status: 'Paid', gross: 590000, tds: 42000, net: 524000, count: 8, emp: 'EMP-101' }
      ];

      let runsHtml = '';
      runs.forEach(r => {
        runsHtml += `
          <div class="card card-glow-orange" style="margin-bottom:14px; cursor:pointer; display:flex; justify-content:space-between; align-items:center; gap:16px; flex-wrap:wrap;" onclick="openPayslipModal('${r.emp}')">
            <div>
              <div style="display:flex; align-items:center; gap:10px;">
                <h3 style="color:var(--cinema-cream); margin:0;">${escapeHtml(r.title)}</h3>
                <span class="badge ${r.status === 'Paid' ? 'badge-teal' : 'badge-gold'}">${r.status.toUpperCase()}</span>
              </div>
              <p style="font-size:12px; color:var(--cinema-muted); margin:4px 0 0 0;">
                Disbursed to ${r.count} personnel • Gross ${formatInr(r.gross)} • TDS ${formatInr(r.tds)} ${r.note ? ' • ' + r.note : ''}
              </p>
            </div>
            <div style="text-align:right;">
              <span style="font-size:11px; color:var(--cinema-muted);">NET PAYOUT</span>
              <div class="font-mono money-val" style="font-size:22px; color:var(--cinema-teal); font-weight:700;">${formatInr(r.net)}</div>
              <button class="btn btn-sm btn-subtle" style="margin-top:4px;">Open Sample Payslip ➔</button>
            </div>
          </div>
        `;
      });

      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">🎞️</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">PAYSLIP DISBURSEMENT TIMELINE</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Historical salary runs archive. Tap any month to open detailed individual salary slips.</p>
        </div>

        <div>
          ${runsHtml}
        </div>
      `;
    }

    // -------------------------------------------------------------------------
    // 14. SALARY BUDDY SCREEN (50/30/20 BUDGETING)
    // -------------------------------------------------------------------------
    function renderSalaryBuddy(pane) {
      if (!pane) pane = document.getElementById('pane-salary-buddy');
      if (!pane) return;
      pane.innerHTML = `
        <div style="margin-bottom: 24px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:24px;">🎯</span>
            <h2 style="font-family:var(--font-headline); letter-spacing:0.5px;">SALARY BUDDY // 50/30/20 BUDGETING ENGINE</h2>
          </div>
          <p style="color: var(--cinema-muted); font-size:14px;">Allocate monthly take-home into clear living, lifestyle, and savings buckets.</p>
        </div>

        <div class="card card-glow-teal" style="margin-bottom:24px;">
          <div class="grid-2" style="gap:20px; align-items:flex-end; margin-bottom:20px;">
            <div>
              <label class="form-label">Monthly In-Hand Take-Home Salary (₹)</label>
              <input type="number" id="buddy-inhand-input" class="form-control font-mono" value="85000" min="5000" step="5000" style="font-size:20px; color:var(--cinema-teal);" oninput="updateBuddyCalculations()">
            </div>
            <div>
              <label class="form-label">Budget Split Rule</label>
              <div style="display:flex; gap:12px;">
                <div style="flex:1;">
                  <span style="font-size:11px; color:var(--cinema-teal);">Needs: <span id="buddy-needs-pct-label">50%</span></span>
                  <input type="range" id="buddy-needs-range" min="30" max="70" step="5" value="50" style="width:100%; accent-color:var(--cinema-teal);" oninput="updateBuddyPct()">
                </div>
                <div style="flex:1;">
                  <span style="font-size:11px; color:var(--cinema-gold);">Wants: <span id="buddy-wants-pct-label">30%</span></span>
                  <input type="range" id="buddy-wants-range" min="10" max="50" step="5" value="30" style="width:100%; accent-color:var(--cinema-gold);" oninput="updateBuddyPct()">
                </div>
                <div style="flex:1;">
                  <span style="font-size:11px; color:var(--cinema-orange);">Savings: <span id="buddy-savings-pct-label">20%</span></span>
                  <input type="range" id="buddy-savings-range" min="10" max="50" step="5" value="20" style="width:100%; accent-color:var(--cinema-orange);" oninput="updateBuddyPct()">
                </div>
              </div>
            </div>
          </div>

          <div class="grid-3" style="text-align:center; gap:16px;">
            <div class="card card-glow-teal" style="background:var(--bg-card-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;" id="buddy-needs-header">50% ESSENTIAL NEEDS</span>
              <div class="font-mono money-val" style="font-size:24px; color:var(--cinema-teal); font-weight:700; margin:6px 0;" id="buddy-needs-val">₹42,500</div>
              <p style="font-size:11px; color:var(--cinema-muted); margin:0;">Rent, groceries, utilities, school fees, EMIs.</p>
            </div>
            <div class="card card-glow-gold" style="background:var(--bg-card-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;" id="buddy-wants-header">30% LIFESTYLE WANTS</span>
              <div class="font-mono money-val" style="font-size:24px; color:var(--cinema-gold); font-weight:700; margin:6px 0;" id="buddy-wants-val">₹25,500</div>
              <p style="font-size:11px; color:var(--cinema-muted); margin:0;">Dining out, trips, gadgets, shopping, movies.</p>
            </div>
            <div class="card card-glow-orange" style="background:var(--bg-card-subtle);">
              <span style="font-size: 11px; color: var(--cinema-muted); font-weight:600;" id="buddy-savings-header">20% FUTURE SAVINGS</span>
              <div class="font-mono money-val" style="font-size:24px; color:var(--cinema-orange); font-weight:700; margin:6px 0;" id="buddy-savings-val">₹17,000</div>
              <p style="font-size:11px; color:var(--cinema-muted); margin:0;">Mutual fund SIPs, PPF, emergency fund, gold.</p>
            </div>
          </div>
        </div>

        <!-- Savings Goal Planner -->
        <div class="card">
          <h3 style="color:var(--cinema-cream); margin-bottom:14px;">SAVINGS GOAL SIMULATOR</h3>
          <div class="grid-3" style="gap:16px; align-items:flex-end;">
            <div>
              <label class="form-label">Goal Target Description</label>
              <input type="text" id="buddy-goal-name" class="form-control" value="New Laptop / Emergency Fund" oninput="updateBuddyCalculations()">
            </div>
            <div>
              <label class="form-label">Target Amount (₹)</label>
              <input type="number" id="buddy-goal-amount" class="form-control font-mono" value="100000" step="10000" oninput="updateBuddyCalculations()">
            </div>
            <div style="background:var(--bg-card-subtle); padding:14px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle); text-align:center;">
              <span style="font-size:11px; color:var(--cinema-muted);">ESTIMATED TIMELINE</span>
              <div class="font-mono" style="font-size:18px; color:var(--cinema-emerald); font-weight:700; margin:4px 0;" id="buddy-goal-months">6 Months</div>
              <span style="font-size:11px; color:var(--cinema-muted);" id="buddy-goal-date">Target Reached</span>
            </div>
          </div>
        </div>
      `;
      updateBuddyCalculations();
    }

    function updateBuddyPct() {
      const needs = parseInt(document.getElementById('buddy-needs-range')?.value || '50', 10);
      const wants = parseInt(document.getElementById('buddy-wants-range')?.value || '30', 10);
      const savings = parseInt(document.getElementById('buddy-savings-range')?.value || '20', 10);

      document.getElementById('buddy-needs-pct-label').textContent = needs + '%';
      document.getElementById('buddy-wants-pct-label').textContent = wants + '%';
      document.getElementById('buddy-savings-pct-label').textContent = savings + '%';

      document.getElementById('buddy-needs-header').textContent = `${needs}% ESSENTIAL NEEDS`;
      document.getElementById('buddy-wants-header').textContent = `${wants}% LIFESTYLE WANTS`;
      document.getElementById('buddy-savings-header').textContent = `${savings}% FUTURE SAVINGS`;

      updateBuddyCalculations();
    }

    function updateBuddyCalculations() {
      try {
        const inhand = Math.max(0, parseFloat(document.getElementById('buddy-inhand-input')?.value) || 0);
        const needsPct = parseInt(document.getElementById('buddy-needs-range')?.value || '50', 10);
        const wantsPct = parseInt(document.getElementById('buddy-wants-range')?.value || '30', 10);
        const savingsPct = parseInt(document.getElementById('buddy-savings-range')?.value || '20', 10);

        const totalPct = needsPct + wantsPct + savingsPct || 100;
        const needsVal = Math.round(inhand * (needsPct / totalPct));
        const wantsVal = Math.round(inhand * (wantsPct / totalPct));
        const savingsVal = Math.round(inhand * (savingsPct / totalPct));

        document.getElementById('buddy-needs-val').textContent = formatInr(needsVal);
        document.getElementById('buddy-wants-val').textContent = formatInr(wantsVal);
        document.getElementById('buddy-savings-val').textContent = formatInr(savingsVal);

        // Goal simulation
        const goalAmt = Math.max(0, parseFloat(document.getElementById('buddy-goal-amount')?.value) || 0);
        if (savingsVal > 0 && goalAmt > 0) {
          const months = Math.ceil(goalAmt / savingsVal);
          const targetDate = new Date();
          targetDate.setMonth(targetDate.getMonth() + months);
          const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

          document.getElementById('buddy-goal-months').textContent = `${months} Month${months === 1 ? '' : 's'}`;
          document.getElementById('buddy-goal-date').textContent = `Target by ${monthNames[targetDate.getMonth()]} ${targetDate.getFullYear()}`;
        }
      } catch (err) {
        console.error('[SalaryBuddy] Calculation error:', err);
      }
    }

    // -------------------------------------------------------------------------
    // DEFAULT WRAPPERS FOR CORE SCREENS
    // -------------------------------------------------------------------------
    function renderDashboard(pane) {
      if (typeof updateLandingTaxDemo === 'function') {
        const slider = document.getElementById('landing-ctc-slider');
        if (slider) updateLandingTaxDemo(slider.value);
      }
    }

    function renderCaBuddy(pane) {
      if (typeof openCaBuddy === 'function') openCaBuddy();
    }

    function renderSecurityAudit(pane) {
      if (typeof loadSecurityAuditReport === 'function') loadSecurityAuditReport();
    }

    function renderShopMode(pane) {
      if (typeof renderShopTables === 'function') renderShopTables();
    }

    function renderEmployees(pane) {
      if (typeof refreshEmployeesTable === 'function') refreshEmployeesTable();
    }

    function renderPayroll(pane) {
      if (typeof refreshPayrollTable === 'function') refreshPayrollTable();
    }

    function renderTaxCalc(pane) {
      if (typeof calculatePaneTax === 'function') calculatePaneTax();
    }

    function renderSalaryJourney(pane) {}
    function renderTaxDetective(pane) {}
    function renderCoinVault(pane) {}
    function renderQrScanner(pane) {}
    function renderLifeEvents(pane) {}
    function renderAssistant(pane) {}
    function renderAuditTrail(pane) {
      if (typeof loadSecurityAuditReport === 'function') loadSecurityAuditReport();
    }
    function renderSettings(pane) {}

    // Friendly fallback for unknown screens
    function showScreenNotFound(screenId) {
      document.querySelectorAll('.view-pane').forEach(el => el.classList.remove('active'));
      const mainContent = document.getElementById('main-content');
      if (!mainContent) return;

      let fallbackPane = document.getElementById('pane-screen-not-found');
      if (!fallbackPane) {
        fallbackPane = document.createElement('div');
        fallbackPane.id = 'pane-screen-not-found';
        fallbackPane.className = 'view-pane';
        mainContent.appendChild(fallbackPane);
      }
      fallbackPane.classList.add('active');
      fallbackPane.innerHTML = `
        <div class="card card-glow-orange" style="margin: 40px auto; max-width: 600px; text-align: center; padding: 40px 24px; border: 1px solid var(--border-film);">
          <div style="font-size: 54px; margin-bottom: 16px;">🚧</div>
          <h2 style="color: var(--cinema-orange); margin-bottom: 8px; font-family: var(--font-headline); letter-spacing: 0.5px;">This screen is not built yet</h2>
          <p style="color: var(--cinema-muted); font-size: 14px; margin-bottom: 24px;">
            The requested view <strong>"${escapeHtml(screenId)}"</strong> is registered in the architecture roadmap and will be active shortly.
          </p>
          <button class="btn btn-orange" onclick="showScreen('dashboard')">Back to Dashboard ➔</button>
        </div>
      `;
    }

    // -------------------------------------------------------------------------
    // MASTER SCREENS REGISTRY & ROUTER IMPLEMENTATION
    // -------------------------------------------------------------------------
    const screens = {
      // Canonical IDs matching sidebar navigation
      'dashboard': renderDashboard,
      'ca-buddy': renderCaBuddy,
      'security-audit': renderSecurityAudit,
      'shop-mode': renderShopMode,
      'employees': renderEmployees,
      'payroll': renderPayroll,
      'tax-calc': renderTaxCalc,
      'salary-journey': renderSalaryJourney,
      'tax-detective': renderTaxDetective,
      'coin-vault': renderCoinVault,
      'qr-scanner': renderQrScanner,
      'salary-buddy': renderSalaryBuddy,
      'what-if-raise': renderRaise,
      'goal-solver': renderGoal,
      'offer-compare': renderOfferCompare,
      'payslip-timeline': renderSlipTimeline,
      'tax-checklist': renderTaxChecklist,
      'hra-calc': renderHraCalc,
      'overtime-calc': renderOvertimeCalc,
      'festival-bonus': renderFestivalBonus,
      'cashflow-cal': renderCashCalendar,
      'ff-settlement': renderFfSettlement,
      'onboarding-check': renderOnboardCheck,
      'health-score': renderHealthScore,
      'forecast-3m': renderForecast3m,
      'life-events': renderLifeEvents,
      'assistant': renderAssistant,
      'audit-trail': renderAuditTrail,
      'settings': renderSettings,

      // Short aliases as requested in specification
      'raise': renderRaise,
      'goal': renderGoal,
      'offer': renderOfferCompare,
      'timeline': renderSlipTimeline,
      'checklist': renderTaxChecklist,
      'hra': renderHraCalc,
      'overtime': renderOvertimeCalc,
      'bonus': renderFestivalBonus,
      'cash': renderCashCalendar,
      'calendar': renderCashCalendar,
      'settlement': renderFfSettlement,
      'onboard': renderOnboardCheck,
      'health': renderHealthScore,
      'forecast': renderForecast3m,
      'buddy': renderSalaryBuddy
    };

    function showScreen(id) {
      try {
        const screenId = String(id || 'dashboard').trim();

        // 1. Highlight active menu item
        document.querySelectorAll('#sidebar-dock .nav-item').forEach(el => {
          const ds = el.dataset.screen || '';
          const oc = el.getAttribute('onclick') || '';
          const isActive = ds === screenId || oc.includes(`'${screenId}'`) || oc.includes(`"${screenId}"`);
          el.classList.toggle('active', isActive);
        });

        // 2. Validate screen exists in registry
        const renderFn = screens[screenId];
        if (!renderFn) {
          console.warn(`[Router] Screen not found: "${screenId}"`);
          showScreenNotFound(screenId);
          window.scrollTo({ top: 0, behavior: 'smooth' });
          return;
        }

        // 3. Clear/Hide view-panes
        document.querySelectorAll('.view-pane').forEach(el => el.classList.remove('active'));

        // 4. Ensure target pane exists
        const paneId = 'pane-' + screenId;
        let pane = document.getElementById(paneId);
        const mainContent = document.getElementById('main-content');
        if (!pane && mainContent) {
          pane = document.createElement('div');
          pane.id = paneId;
          pane.className = 'view-pane';
          mainContent.appendChild(pane);
        }

        if (pane) {
          pane.classList.add('active');
          try {
            renderFn(pane);
          } catch (renderError) {
            console.error(`[Router] Render error in screen "${screenId}":`, renderError);
            pane.innerHTML = `
              <div class="card card-glow-crimson" style="margin:20px 0; border:1px solid var(--cinema-crimson); padding:24px;">
                <h3 style="color:var(--cinema-crimson); margin-bottom:8px;">⚠️ Screen Rendering Error</h3>
                <p style="color:var(--cinema-muted); font-size:14px;">Error rendering <strong>${escapeHtml(screenId)}</strong>: ${escapeHtml(renderError.message || String(renderError))}</p>
              </div>
            `;
          }
        }

        // 5. Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch (routerErr) {
        console.error('[Router] Fatal router error:', routerErr);
      }
    }

    // Alias legacy switchTab to unified showScreen
    function switchTab(id) {
      showScreen(id);
    }

    // Event delegation on sidebar dock
    document.addEventListener('DOMContentLoaded', () => {
      const dock = document.getElementById('sidebar-dock');
      if (dock) {
        dock.addEventListener('click', (e) => {
          const item = e.target.closest('.nav-item');
          if (item) {
            const screenId = item.dataset.screen || (item.getAttribute('onclick') || '').match(/['"]([^'"]+)['"]/)?.[1];
            if (screenId) {
              e.preventDefault();
              showScreen(screenId);
            }
          }
        });
      }
    });
"""

# Inject router_js before the closing </script> in index.html
# Find the main script tag
last_script_end = html.rfind('</script>')
if last_script_end != -1:
    html = html[:last_script_end] + router_js + '\n' + html[last_script_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html written successfully!")
